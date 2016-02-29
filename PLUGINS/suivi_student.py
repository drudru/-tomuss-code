#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2008-2014 Thierry EXCOFFIER, Universite Claude Bernard
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#    Contact: Thierry.EXCOFFIER@bat710.univ-lyon1.fr

"""
"""

import os
import time
import html
import collections
from .. import plugin
from .. import configuration
from .. import inscrits
from .. import referent
from .. import utilities
from .. import tablestat
from .. import abj
from .. import document
from .. import column
from .. import teacher
from .. import files
from .. import signature

files.add('PLUGINS', 'suivi_student.css')
files.add('PLUGINS', 'suivi_student.js')

def teacher_can_see_suivi(server, the_student):
    prefs = display_preferences_get(the_student)
    priv = bool(prefs.get('private_suivi', False))
    server.concerned_teachers = configuration.concerned_teachers(server,
                                                                 the_student)
    if server.concerned_teachers:
        return priv, True

    if priv:
        return priv, False

    return priv, configuration.visible_from_suivi(server, the_student)

def display_referent(server):
    ref = referent.referent(server.year, server.semester, server.suivi_login)
    if ref:
        return list(inscrits.L_fast.firstname_and_surname_and_mail(ref))+[0,ref]
    return [0, 0, 0, referent.need_a_referent(server.suivi_login), ref]

def display_copyright(server):
    return configuration.version

def display_mails(server):
    if server.is_a_student:
        return '' # Student can't see all teacher mail addresses
    teachers = collections.defaultdict(list)
    for t in tablestat.the_ues(server.year, server.semester,
                               server.suivi_login):
        if tuple(t.get_items(server.suivi_login)):
            for teacher_login in t.masters:
                teachers[teacher_login].append(t.ue)
    if not teachers:
        return '' # No teachers
    return [' '.join(v) + ' <' + (inscrits.L_fast.mail(k) or k) + '>'
            for k, v in teachers.items()
            ]

def display_names(server):
    return inscrits.L_fast.firstname_and_surname_and_mail(server.suivi_login)

def display_login(server):
    return server.suivi_login

def display_charte(server):
    if not referent.need_a_charte(server.suivi_login):
        return ''
    return utilities.charte_signed(server.suivi_login, server)

def display_signature(server):
    if not server.suivi_question.html_answered():
        return '' # No message/contract link

def display_logo(server):
    return configuration.logo

def display_semesters(server):
    t = {}
    for (url, dummy_port, year, semester, dummy_host
         ) in configuration.suivi.urls.values():
        if configuration.display_this_semester_to_the_student(
            year, semester, server.suivi_login):
            t['%d/%s' % (year, semester)] = url
    return t

def display_get_student(server):
    if server.ticket.is_a_referent:
        return True
    return ''

def display_set_referent(server):
    if configuration.is_member_of(server.ticket.user_name,
                                  ('grp:referent_masters',)):
        return True
    return ''

def display_referent_notepad(server):
    if not server.suivi_ref:
        return ''
    if server.suivi_ref != server.ticket.user_name:
        return ''
    if server.is_a_student:
        return '' # Student view
    
    tyear = utilities.university_year()
    s = []
    while True:
        table = document.table(tyear, 'Referents',
                               utilities.login_to_module(server.suivi_ref),
                               ro=True, create=False)
        if table is None:
            break
        s.append(table.referent_resume(table, server.suivi_login))
        tyear -= 1
    return '\n'.join(s)

def display_question(server):
    return getattr(server, 'suivi_question_html', '')

def display_message(server):
    if server.is_a_student:
        return configuration.suivi_student_message
    else:
        return ''

def display_abjs(server):
    return [
        (from_date, to_date, comment)
        for from_date, to_date, dummy_author, comment
        in server.suivi_abj.current_abjs()
        ]

def display_da(server):
    return [
        (from_date, to_date, comment)
        for from_date, to_date, dummy_author, comment
        in server.suivi_abj.current_das()
        ]

def display_rss(server):
    if server.is_a_student:
        if server.ticket.user_name == server.suivi_login:
            return utilities.manage_key('LOGINS', os.path.join(
                    server.suivi_login,'rsskey'))
        else:
            return "fake_RSS_key"
    return ''

def display_tt(server):
    if (server.concerned_teachers
        or configuration.is_member_of(server.ticket.user_name,
                                      ('grp:see_tt_suivi',))
        ):
        table = document.table(utilities.university_year(), 'Dossiers', 'tt',
                               ro=True)
        return abj.tierstemps(server.suivi_login, table_tt=table) or ''
    else:
        return ''

def display_more_on_suivi(server):
    return configuration.more_on_suivi(server.suivi_login, server)

def display_member_of(server):
    member_of = list(inscrits.L_fast.member_of_list(server.suivi_login))
    member_of.sort()
    member_of = [
        i.replace(',DC=univ-lyon1,DC=fr','')
        for i in member_of
        ]
    etapes = []
    for etape in inscrits.L_fast.etapes_of_student(server.suivi_login):
        e = teacher.all_ues().get('etape-' + etape)
        if e:
            title = e.intitule()
        else:
            title = "???"
        etapes.append([etape, title])

    return member_of, etapes

def json(server, table, line, line_id):
    table_attrs = {}
    for attr in column.TableAttr.attrs.values():
        if attr.name == 'formation': # XXX
            continue
        if attr.computed:
            continue
        if attr.gui_display == 'GUI_a':
            continue
        value = getattr(table, attr.name, attr.get_default_value(table))
        if value == '' or value == 0 or value == () or value == []:
            continue
        table_attrs[attr.name] = value
    table_attrs['masters'] = [
        inscrits.L_fast.firstname_and_surname_and_mail(login)
        for login in table.masters]
    table_attrs['ue'] = table.ue
    table_attrs['year'] = table.year
    table_attrs['semester'] = table.semester
    table_attrs['columns'] = table.columns.js(
        hide = server.is_a_student and 1 or True,
        python = True)
    table_attrs['line_id'] = line_id
    table_attrs['line'] = line.json(for_student=server.is_a_student,
                                    columns = table.columns)
    table_attrs['stats'] = table.lines.line_stat(
        table, line, link=not server.is_a_student)
    table_attrs['rounding'] = table.rounding
    return table_attrs

def display_grades(server):
    ss = []
    s = []
    codes = {}
    for t in tablestat.the_ues(server.year, server.semester,
                               server.suivi_login):
        for line_id, line in t.get_items(server.suivi_login):
            ss.append(json(server, t, line, line_id))
            if ss[-1]:
                # A line has been displayed
                codes[t.ue_code] = True
    if (configuration.suivi_display_more_ue
        and (server.year, server.semester) == configuration.year_semester
        and (not server.is_a_student or configuration.suivi_check_student_lists(server.suivi_login))
        ):
        for t in inscrits.L_fast.ues_of_a_student_short(server.suivi_login):
            if '-' not in t:
                continue
            title = teacher.all_ues().get(t.split('-')[1])
            if title:
                title = title.intitule()
            else:
                title = ''
            if t not in codes:
                s.append((t, title))
    return [ss, s]

def display_students(server):
    students = referent.students_of_a_teacher(server.suivi_login)
    if not students:
        return ''

    return [[student] + inscrits.L_slow.get_student_info(student)
            for student in students
            ]

def display_tables(server):
    if server.is_a_student and not getattr(server, 'teacher_as_a_student',0):
        return ''
    tables = utilities.manage_key('LOGINS',
                                  os.path.join(server.suivi_login,
                                               'tables'))
    if not tables:
        return ''
    return [
        year_semester_ue + (n,)
        for year_semester_ue, n in eval(tables).items()
    ]

def display_preferences_get(login):
    prefs = utilities.manage_key('LOGINS', os.path.join(login, 'preferences'))
    if prefs:
        return eval(prefs)
    else:
        return {}

def display_preferences(server):
    if server.is_a_student:
        login = server.suivi_login
    else:
        login = server.ticket.user_name
    prefs = display_preferences_get(login)
    if not prefs:
        if server.is_a_student:
            prefs = {}
        else:
            prefs = {'highlight_grade': 1}

    for k in ('show_empty', 'color_value', 'highlight_grade', 'private_suivi',
              'hide_right_column', 'big_text', 'hide_picture',
              'no_teacher_color', 'big_box', 'recursive_formula',
              'green_prst', 'black_and_white'):
        if k not in prefs:
            prefs[k] = 0

    if login in configuration.root:
        if 'debug_suivi' not in prefs:
            prefs['debug_suivi'] = 0

    # XXX For old files from TOMUSS before 5.3.2
    priv = utilities.manage_key('LOGINS', os.path.join(login, 'private'))
    if priv and priv.startswith('1'):
        prefs['private_suivi'] = 1

    if not configuration.suivi_student_allow_private or not server.is_a_student:
        del prefs['private_suivi']

    return prefs

from .. import display
D = display.Display

# Standard suivi page

D('Top'         , []          ,0, js='Vertical')
D('Private'     , []          ,0, js='Vertical')# Minimal suivi page if private
D('Question'    , []          ,0, js='Vertical')# Minimal suivi page if ask

D('User'        ,['Top','Private','Question'],-3, js='Horizontal')
D('Preamble'    ,['Top','Private','Question'],-2)
D('Message'     ,'Top'        ,-1, js="Horizontal", data=display_message)
D('Messages'    ,'Top'        ,-0.5) # To one student only
D('Body'        ,'Top'        ,1, js='Horizontal')

D('BodyLeft'    , 'Body'      ,0, js='Vertical')
D('RightClip'   , 'Body'      ,1)

D('BodyRight'   , 'RightClip' ,0, js='Vertical')

D('TopLine'     ,['BodyLeft', 'Private','Question'],0, js="Horizontal")
D('Student'     ,['BodyLeft', 'Private','Question'],1, js='Horizontal')
D('ReferentNP'  , 'BodyLeft'  ,2, js='Horizontal',data=display_referent_notepad)
D('LastGrades'  , 'BodyLeft'  ,3)
D('Grades'      , 'BodyLeft'  ,4, data=display_grades)
D('Students'    , 'BodyLeft'  ,5, data=display_students)
D('Tables'      , 'BodyLeft'  ,6, data=display_tables)

D('Semesters'   , 'BodyRight' ,1, data=display_semesters)
D('LinksTable'  , 'BodyRight' ,2)
D('Abjs'        , 'BodyRight' ,3, data=display_abjs)
D('DA'          , 'BodyRight' ,4, data=display_da)
D('TT'          , 'BodyRight' ,5, data=display_tt)
D('MoreOnSuivi' , 'BodyRight' ,9, data=display_more_on_suivi)
D('Advertising' , 'BodyRight',99, data=lambda server: configuration.advertising)

D('Logo'        , 'User'      ,0, data=display_logo)
D('YearSemester', 'User'      ,1.9)
D('Reload'      , 'User'      ,2)
D('Profiling'   , 'User'      ,3)
D('IdentityR'   , 'User'      ,-1, js='Horizontal') # Yes : -1

D('Explanation' , 'IdentityR' ,0, data=display_copyright)
D('Preferences' , 'IdentityR' ,1, data=display_preferences)

D('IsPrivate'   , 'Private'   ,5, data=display_referent)
D('AskQuestion' , 'Question'  ,6, data=display_question)

D('Picture'     , 'TopLine'   ,0)
D('Login'       , 'TopLine'   ,1, js='Vertical', data=display_login)
D('Names'       , 'TopLine'   ,2, data=display_names)
D('GetStudent'  , 'TopLine'   ,3, data=display_get_student)

# Line 1 for students and 1&2 fr teachers :
D('Referent'    , 'LinksTable',0, data=display_referent)
D('SetReferent' , 'LinksTable',0.5, data=display_set_referent)
D('Mails'       , 'LinksTable',1, data=display_mails)
D('Official'    , 'LinksTable',2)
D('Bilan'       , 'LinksTable',3, data=display_get_student)
# Line 3 for teachers
D('StudentView' , 'LinksTable',4)
D('NewSignature', 'LinksTable',5)
# Line 4
D('Charte'      , 'LinksTable',6, display_charte)
D('Signature'   , 'LinksTable',7, display_signature)

D('RSS'         , 'LinksTable',8, data=display_rss)
D('MemberOf'    , 'LinksTable',10, data=display_member_of)

# Template of an UE

D('UE'          , []          ,0)

D('UEHeader'    , 'UE'        ,0, js='Horizontal')
D('UEComment'   , 'UE'        ,1)
D('UEGrades'    , 'UE'        ,2)

D('UEToggle'    , 'UEHeader'  ,-1)
D('UETitle'     , 'UEHeader'  ,0)
D('UEMasters'   , 'UEHeader'  ,1)

# Template of a Cell

D('Cell'        , []          ,0, js='Vertical')
D('CellTop'     , 'Cell'      ,0, js='Vertical')
D('CellBox'     , 'Cell'      ,1)
D('CellBottom'  , 'Cell'      ,2, js='Vertical')

D('CellAuthorLine', 'CellBottom',0, js='Horizontal')
D('CellColumn'  , 'CellBottom',2)
D('CellComment' , 'CellBottom',1)

D('CellAuthor' , 'CellAuthorLine',0)
D('CellMTime'  , 'CellAuthorLine',1)

D('CellTitle'   , 'CellBox'   ,0)
D('CellValue'   , 'CellBox'   ,1)

D('CellTypeLine', 'CellTop'   ,0, js='Vertical')
D('CellDate'    , 'CellTop'   ,1)
D('CellStatLine', 'CellTop'   ,2, js='Horizontal')

D('CellRank'    , 'CellStatLine',0)
D('CellAvg'     , 'CellStatLine',1)

D('CellType'    , 'CellTypeLine'      ,0)
D('CellFormula' , 'CellTypeLine'      ,1)

def student_statistics(login, server, is_a_student=False, expand=False,
                       is_a_referent=False):
    utilities.warn('Start', what='table')
    server.is_a_student = is_a_student
    server.suivi_login = login
    server.suivi_question = signature.get_state(login)
    server.suivi_ref = referent.referent(server.year, server.semester, login)
    server.suivi_abj = abj.Abj(server.year,server.semester, server.suivi_login)
    server.suivi_private_life, visible = teacher_can_see_suivi(server, login)

    if not visible:
        return display.data_to_display(server, 'Private')

    if is_a_student:
        server.suivi_question_html = server.suivi_question.html()
        if server.suivi_question_html:
            return display.data_to_display(server, 'Question')

    return display.data_to_display(server, 'Top')

def page_tail(server):
    # Not in JS in case of multiple students on the same page
    server.the_file.write('<br class="noprint">'*10) # for popups

def student(server, login=''):
    """Display all the informations about a student."""
    if not login:
        login = server.ticket.user_name
        
    suivi_headers(server, is_student=True)
    student_statistics(login, server, True)
    page_tail(server)

plugin.Plugin('student', '/{*}', function=student, group='!staff',
              launch_thread=True, unsafe=False,
              password_ok = None)

def accept(server):
    """The student signs the contract"""
    suivi_headers(server, is_student=True)
    server.the_file.write('<img src="%s/=%s/store_accept">' % (
                          configuration.server_url, server.ticket.ticket)
                          )
    student_statistics(server.ticket.user_name, server, True)
    page_tail(server)

plugin.Plugin('accept', '/accept', function=accept, group='!staff',
              launch_thread=True,
              password_ok = None)

def suivi_headers(server, is_student=True):
    display.send_headers(
        server, "suivi_student.css", "suivi_student.js",
        "initialize_suivi_real",
        'var table_attr = {} ;'
        + "var semester = %s;\n" % utilities.js(server.semester         )
        + "var year     = %s;\n" % utilities.js(server.year             )
        + "var is_a_teacher = %s;\n" % int(not is_student)
        + 'var max_visibility_date = %d;\n' % configuration.max_visibility_date
        + 'var upload_max = %s;\n' % utilities.js(configuration.upload_max)
        + 'column_get_option_running = true ;\n'
    )

def home(server, nothing_behind=True):
    """Display the home page for 'suivi', it asks the student id."""
    suivi_headers(server, is_student=nothing_behind)
    server.teacher_as_a_student = True

    if nothing_behind:
        student_statistics(server.ticket.user_name, server, is_a_student=True)
        page_tail(server)

plugin.Plugin('home', '/', group='staff', function = home, unsafe=False)


def page_suivi(server):
    """Display the informations about all the students indicated."""
    if (len(server.the_path) == 0
        or server.the_path[0] == ''
        or server.the_path[0] == server.ticket.user_name):
        server.teacher_as_a_student = True
        student(server)
        return

    server.the_path[0] = server.the_path[0].replace('?X=', '').replace('?=','')

    if server.the_path[0].startswith(' '):
        # If student id starts by space the teacher want
        # to see exactly the same thing than the student
        student(server, server.the_path[0][1:])
        return

    if server.the_path[0].startswith(':'):
        # Expand more information in resume.
        server.the_path[0] = server.the_path[0][1:]
        expand = True
    else:
        expand = False

    home(server, nothing_behind=False)

    logins = server.the_path[0].replace('+',',').strip(',').split(',')
    logins = [inscrits.safe(lo).lower() for lo in logins]
    server.the_file.write(
        '<title>' +
        ', '.join([inscrits.L_fast.firstname_and_surname(login)[0].title() +
                   ' ' + inscrits.L_fast.firstname_and_surname(login)[1]
                  for login in logins]) +
        '</title>'
                          )
    done = False
    for login in logins:
        try:
            if done:
                server.the_file.write("<script>start_display()</script>")
            login = utilities.the_login(login)
            student_statistics(login, server, is_a_student=False,expand=expand)
            done = True
        except ValueError:
            raise
        server.the_file.flush()
    page_tail(server)

plugin.Plugin('infos', '/{*}', group='staff', password_ok = None,
              function = page_suivi, unsafe=False,
              launch_thread=True,
              )

def escape(t):
    # > and < must really be not interpretable at any level of escape
    return t.replace('>', '﹥').replace('<', '﹤').replace('&','&amp;')

def rss_author(x):
    try:
        fn, sn = inscrits.L_fast.firstname_and_surname(x)
        return inscrits.L_fast.mail(x) + ' (%s %s)' % (fn.title(), sn.upper())
    except:
        return x

def rss_date(date=None):
    if date is None:
        date = time.localtime(time.time())
    elif isinstance(date, str):
        date = time.strptime(date, '%Y%m%d%H%M%S')
    return time.strftime('%a, %d %b %Y %H:%M:%S +0000', date)

def page_rss(server):
    """RSS for the student."""
    if len(server.the_path) != 1:
        login = False
    else:
        login = utilities.manage_key('RSSLOGINS', server.the_path[0],
                                     separation=2)
    if login is False:
        server.the_file.write('''<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
<language>fr</language> 
<title>TOMUSS</title>
<description>%s</description>
<lastBuildDate>%s</lastBuildDate>
<link></link>
<item><title>%s</title>
<description>%s</description>
<link>%s</link>
</item>
</channel>
</rss>
''' % ( utilities._("MSG_suivi_student_RSS_title"),
        time.asctime(),
        utilities._("MSG_suivi_student_RSS_forbiden_title"),
        utilities._("MSG_suivi_student_RSS_forbiden_description"),
        utilities.StaticFile._url_))
        return

    server.the_file.write('''<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
<language>fr</language>
<title>TOMUSS %s</title>
<description>%s</description>
<lastBuildDate>%s</lastBuildDate>
<link>%s</link>''' % ( login,
                       utilities._("MSG_suivi_student_RSS_title"),
                       rss_date(), utilities.StaticFile._url_))

    s = []

    # Do not display change newer than ONE hour.
    if configuration.regtest:
        limit = '9999' # The regtests want to see all
    else:
        limit = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time() - 3600))
    
    i = 0
    for t in tablestat.the_ues(server.year, server.semester, login):
        for line in t.get_lines(login):
            for cell, column in zip(line[6:], t.columns[6:]):
                if cell.date > limit:
                    continue
                if cell.value == '':
                    continue
                if not column.visible(hide=1):
                    continue # Hidden column
                if not column.is_computed():
                    s.append((max(cell.date,
                                  getattr(column, 'visibility_date__mtime',''),
                                  getattr(column, 'visibility__mtime', ''),
                                  column.visibility_date + '000000'
                              ), i,
                              cell, t, column))
                    i += 1 # All first items must be different
    s.sort()
    for date, i, cell, table, column in s[-10:]:
        if cell.comment:
            comment= html.escape(utilities._("MSG_suivi_student_RSS_value_comment")
                                + '<b>') + escape(cell.comment) + html.escape('</b>,<br>')
        else:
            comment = ''
        if column.comment:
            column_comment = utilities._("MSG_suivi_student_RSS_column_comment"
                                      ) + '«' + \
                             escape(column.title) + html.escape('» : <b>') + escape(
                column.comment) + html.escape('</b>,<br>')
        else:
            column_comment = ''
        if column.type.name == 'Note':
            note_range = column.type.value_range(*column.min_max())
        else:
            note_range = ''
        table_title = escape(table.table_title)
        if table.comment:
            table_title += ' (<b>' + escape(table.comment) + '</b>)'
        table_title = html.escape(table_title + ',<br>')
        server.the_file.write(
            '<item>\n' +
            '<title>%s : %s : %s%s</title>\n' % (table.ue,
                                           escape(column.title),
                                           escape(str(cell.value)),
                                           note_range) +
            '<description>%s%s%s%s</description>\n' % (
                table_title,
                column_comment,
                comment,
                html.escape(utilities._("MSG_suivi_student_RSS_value_modified")
                           + '<b>' + cell.author
                           + '</b>,<br>' + utilities.nice_date(cell.date)
                           + '<br>')
                ) +
            '<link>%s</link>' % utilities.StaticFile._url_ +
            '<author>%s</author>\n' % rss_author(cell.author) +
            '<pubDate>%s</pubDate>\n' % rss_date(document.date_time(date))+
            '<guid isPermaLink="false">%s %s</guid>\n' % (table.ue,
                                                          column.the_id) +
            '</item>\n')

    server.the_file.write('''    
    </channel>
</rss>
''')
    

plugin.Plugin('rss', '/rss/{*}', authenticated=False, password_ok = None,
              function = page_rss,
              launch_thread=False,
              mimetype = 'application/rss+xml; charset=utf-8',
              )

def page_rss2(server):
    """RSS for the table."""
    link = '%s/%s/%s/%s' % (configuration.server_url,
                           server.year,
                           server.semester,
                           server.the_path[0]
                           )
    server.the_file.write('''<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
<title>TOMUSS : %s</title>
<description>%s</description>
<lastBuildDate>%s</lastBuildDate>
<link>%s</link>
''' % (server.the_path[0], utilities._("MSG_suivi_student_RSS_value_modified"),
       rss_date(), link))

    t = document.table(server.year, server.semester, server.the_path[0],
                       ro=True, create=False)
    if t is None:
        return
    # Only the 10 most recents pages containing modifications
    for p in [i for i in t.pages[1:] if i.nr_cell_change > 0 and i.date][-10:]:
        date = p.date_time()

        d = utilities._("MSG_suivi_student_RSS_table") % (
             utilities.nice_date(p.date),
             p.nr_cell_change,
             )
        t1 = p.day().replace('/', '$2F')
        # %3C %3E to not broke XML syntax
        # $20 $3F to not be tampered
        f = '/=full_filter=@%s$20$3F%%3C_E%s$20$3F%%3E_E%s' % (
            p.user_name, t1, t1)
        server.the_file.write(
            '<item>\n' +
            '<title>' +
            utilities._("MSG_suivi_student_RSS_table_nr_change") % (
                p.nr_cell_change,
                p.user_name) +
            '</title>' +
            '<description>%s</description>\n' % html.escape(d) +
            '<link>%s%s</link>\n' % (link, f) +
            '<pubDate>%s</pubDate>\n' % rss_date(date)+
            '<author>%s</author>\n' % rss_author(p.user_name) +
            '<guid isPermaLink="false">%d</guid>\n' % t.pages.index(p) +
            '</item>\n'
            )

    server.the_file.write('''    
    </channel>
</rss>
''')

plugin.Plugin('rss2', '/rss2/{*}', authenticated=False, password_ok = None,
              function = page_rss2,
              launch_thread=False,
              mimetype = 'application/rss+xml; charset=utf-8',
              )
