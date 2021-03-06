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

"""Management of the justification for missing courses."""

import os
import time
import html
import glob
import re
from . import utilities
from . import configuration
from . import inscrits
from . import document
from . import teacher

js = utilities.js

def a_date(date):
    """Check if the date (DD/MM/YYYY/[MA]) seems fine"""
    if date[-1] not in "MA":
        raise ValueError("Bad date:" + date)
    int_list = [int(v) for v in date[:-1].split('/')]
    if len(int_list) != 3:
        raise ValueError("Bad date:" + date)
    if (int_list[0] >= 1 and int_list[0] <= 31 and
        int_list[1] >= 1 and int_list[1] <= 12 and
        int_list[2] > 2000):
        return '%d/%d/%d%s' % (int_list[0], int_list[1], int_list[2], date[-1])
    raise ValueError("Bad date:" + date)

class Abj(object):
    """ABJ for a given student

    Functions: add, rem, add_da, rem_da
    are stored in the key file of the student (per university year).
    The parameters are yet validated.

    The same functions beginning with 'store_' do the check and the storage.
    """

    def __init__(self, year, semester, login):
        self.first_day, self.last_day = utilities.semester_span(year, semester)
        year, semester = utilities.university_year_semester(year, semester)
        self.login = utilities.the_login(login)
        self.filename = os.path.join(self.login, 'abj_%d' % year)
        self.abjs = []
        self.da = []
        f = utilities.manage_key('LOGINS', self.filename)
        if f:
            locales = self.get_locales()
            for line in f.strip().split('\n'):
                eval(line.strip(), {}, locales)

    def get_locales(self):
        return {'add'   : self.add,
                'add_da': self.add_da,
                'rem'   : self.rem,
                'rem2'  : self.rem2,
                'rem_da': self.rem_da,
                }

    def store(self, data):
        utilities.manage_key('LOGINS',self.filename, content=data, append=True)
        eval(data, {}, self.get_locales())

    def add(self, from_date, to_date, author, dummy_date, comment):
        self.abjs.append((from_date, to_date, author, comment))
    def store_add(self, from_date, to_date, user_name, date, comment):
        from_date = a_date(from_date)
        to_date = a_date(to_date)
        for abj in self.abjs:
            if (from_date, to_date) == abj[:2]:
                print('Do no add twice the same ABJ for', self.login)
                print(from_date, to_date, user_name, date, comment)
                for i in self.abjs:
                    print('\t', i)
                return
        if not date:
            date = time.strftime('%Y%m%d%H%M%S')
        self.store('add(%s,%s,%s,%s,%s)\n' % (
                repr(from_date), repr(to_date), repr(user_name),
                repr(date), repr(comment)))
        
    def add_da(self, ue_code, date, author, dummy_fdate, comment):
        self.da.append((ue_code, date, author, comment))
    def store_add_da(self, ue_code, date, user_name, fdate, comment):
        for i in self.da:
            if i[0] == ue_code and i[1] == date:
                return
        if not fdate:
            fdate = time.strftime('%Y%m%d%H%M%S')
        self.store('add_da(%s,%s,%s,%s,%s)\n' % (
            repr(ue_code), repr(date), repr(user_name),
            repr(fdate), repr(comment)))

    def rem(self, from_date, to_date, dummy_username, dummy_date):
        """BUGGED: Do not use. It is here to allow reading <2010 files"""
        self.abjs = [abj
                     for abj in self.abjs
                     if abj[0] != from_date and abj[1] != to_date]
    def store_rem(self, from_date, to_date, user_name, date=''):
        """BUGGED: Do not use. It is here to allow reading <2010 files"""
        from_date = a_date(from_date)
        to_date = a_date(to_date)
        if not date:
            date = time.strftime('%Y%m%d%H%M%S')
        self.store('rem(%s,%s,%s,%s)\n' % (
                repr(from_date), repr(to_date), repr(user_name), repr(date)))

    def rem2(self, from_date, to_date, dummy_username, dummy_date):
        self.abjs = [abj
                     for abj in self.abjs
                     if abj[0] != from_date or abj[1] != to_date]
    def store_rem2(self, from_date, to_date, user_name, date=''):
        from_date = a_date(from_date)
        to_date = a_date(to_date)
        if not date:
            date = time.strftime('%Y%m%d%H%M%S')
        self.store('rem2(%s,%s,%s,%s)\n' % (
                repr(from_date), repr(to_date), repr(user_name), repr(date)))
        
    def rem_da(self, ue_code, dummy_username, dummy_date):
        self.da = [da for da in self.da if da[0] != ue_code]
    def store_rem_da(self, ue_code, user_name, date):
        if not date:
            date = time.strftime('%Y%m%d%H%M%S')
        self.store('rem_da(%s,%s,%s)\n' % (
                repr(ue_code), repr(user_name), repr(date)))

    def js(self, full=True, current=False):
        """All the student ABJ data as a JavaScript fragment"""
        abj_list = []
        if current:
            list_in = self.current_abjs()
        else:
            list_in = self.abjs
        for from_date, to_date, author, comment in list_in:
            if full:
                abj_list.append('[%s,%s,%s,%s]' % (repr(from_date),
                                                   repr(to_date),
                                                   repr(author), js(comment)))
            else:
                abj_list.append('[%s,%s,%s]' % (repr(from_date),
                                                repr(to_date),
                                                js(comment)))
        return '[' + ','.join(abj_list) + ']'

    def js_da(self, current=False):
        """All the student DA data as a JavaScript fragment"""
        da_list = []
        if current:
            list_in = self.current_das()
        else:
            list_in = self.da
        for ue_code, date, author, comment in list_in:
            da_list.append('[%s,%s,%s,%s]' % (repr(ue_code), repr(date),
                                              repr(author), js(comment)))
        return '[' + ','.join(da_list) + ']'

    def ues_without_da(self):
        """List of the UE_CODE registered by the student, but without DA"""
        ues = inscrits.L_fast.ues_of_a_student_short(self.login)
        if len(self.da) == 0:
            return ues
        da = list(zip(*self.da))[0]
        return [ue_code for ue_code in ues if ue_code not in da]

    def current_abjs(self):
        for abj in self.abjs:
            abj_begin = utilities.date_to_time(abj[0].rstrip('AM'), 0)
            abj_end = utilities.date_to_time(abj[1].rstrip('AM'), 8000000000)
            if max(self.first_day, abj_begin) <= min(self.last_day, abj_end):
                yield abj

    def current_das(self):
        for da in self.da:
            date = configuration.date_to_time(da[1])
            if self.first_day < date < self.last_day:
                yield da

class Abjs(object):
    """ABJ for a set of students"""

    def __init__(self, year, semester):
        self.year, self.semester = utilities.university_year_semester(
            year, semester)

        # This code is here to translate old data format to the new one.
        
        if configuration.read_only:
            return
        filename = os.path.join(configuration.db, 'Y'+str(year), 'S'+semester)
        utilities.mkpath_safe(filename)
        filename = os.path.join(filename, 'abjs.py')
        if not os.path.exists(filename):
            return
        utilities.warn('Start translation from old file format')

        locales = {'add'   : self.add   ,
                   'add_da': self.add_da,
                   'rem'   : self.rem   ,
                   'rem2'  : self.rem   ,
                   'rem_da': self.rem_da,
                   }
        f = open(filename, "r", encoding = "utf-8")
        for line in f:
            if '(' not in line:
                continue
            eval(line, {}, locales)
        f.close()

        utilities.unlink_safe(filename)
        utilities.warn('Done translation from old file format')

    def add(self, login, from_date, to_date, user_name='', date='',comment=''):
        Abj(self.year, self.semester, login).store_add(
            from_date, to_date, user_name, date, comment)
    def add_da(self, login, ue_code, date=None, user_name='', fdate='',
               comment=''):
        Abj(self.year, self.semester, login).store_add_da(
                ue_code, date, user_name, fdate, comment)
    def rem(self, login, from_date, to_date, user_name='', date=''):
        """BUGGED: Do not use. It is here to allow reading <2010 files"""
        Abj(self.year, self.semester, login).store_rem(
            from_date, to_date, user_name, date)
    def rem2(self, login, from_date, to_date, user_name='', date=''):
        Abj(self.year, self.semester, login).store_rem2(
            from_date, to_date, user_name, date)
    def rem_da(self, login, ue_code, user_name='', date=''):
        Abj(self.year, self.semester, login).store_rem_da(
            ue_code, user_name, date)

    def students(self, progress_bar=None):
        i = 0
        dirs = tuple(glob.glob(os.path.join(configuration.db, 'LOGINS','*')))
        for key in dirs:
            if progress_bar:
                i += 1
                progress_bar.update(i, len(dirs))
            for filename in glob.glob(os.path.join(key, '*',
                                                   'abj_%s' % self.year)):
                yield filename.split(os.path.sep)[-2]

def add_abjs(year, semester, ticket, student, from_date, to_date, comment):
    """Helper function"""
    Abjs(year, semester).add(student, from_date, to_date, ticket.user_name,
                             comment=comment)

def rem_abjs(year, semester, ticket, student, from_date, to_date):
    """Helper function"""
    Abjs(year, semester).rem(student, from_date, to_date,
                             ticket.user_name)

def add_abjs_da(year, semester, ticket, student, ue_code, date, comment):
    """Helper function"""
    Abjs(year, semester).add_da(student, ue_code, date, ticket.user_name,
                                comment=comment)

def rem_abjs_da(year, semester, ticket, student, ue_code):
    """Helper function"""
    Abjs(year, semester).rem_da(student, ue_code, ticket.user_name)

def html_abjs(year, semester, student, full=False):
    """Get all the ABJS/DA informations has HTML
    It is required to include suivi_student.js
    """
    s = ''
    a = Abj(year, semester, student)
    a_abj = a.js(full=full)
    if len(a_abj) > 2:
        s += ('node.data = ' + a.js(full=full, current=True)
              + '; document.write(DisplayAbjs(node)) ;')
    a_da = a.js_da()
    if len(a_da) > 2:
        s += ('node.data = ' + a.js_da(current=True)
              + '; document.write(DisplayDA(node)) ;')
    if s:
        return '<script>node = {} ;' + s + '</script>'
    return ''

def a_student(browser, year, semester, ticket, student):
    """Send student abj with the data to_date the navigator."""
    student = inscrits.login_to_student_id(student)
    html = """
<link rel="stylesheet" href="%s/style.css" type="text/css">
<body class="themeG">
<div id="student_display"><IMG src="%s"></div>
""" % (configuration.url_files, configuration.picture(student, ticket))

    html += "<A HREF=\"%s/%s\">%s</A>, <small>%s</small><SCRIPT>" % (
        configuration.suivi.url(year,semester,ticket.ticket),
        student.replace("'","\\'"),
        ' '.join(inscrits.L_fast.firstname_and_surname(student)).replace("'","\\'"),
        ', '.join(inscrits.L_fast.portail(student)).replace("'","\\'")
        )
    abj = Abj(year, semester, student)
    html += "document.write(window.parent.display_abjs(%s));" % abj.js()
    html += "document.write(window.parent.display_da(%s));" % abj.js_da()
    ue_list = abj.ues_without_da()
    ue_list.sort()
    html += "window.parent.ues_without_da(%s);" % js(ue_list) + '</SCRIPT>'
    browser.write(html)

def tierstemps(student_id, table_tt=None, only_current=True):
    """Returns a strings containing all tiers-temps informations about
    the student from the TT table given."""
    student_id = inscrits.login_to_student_id(student_id)
    if table_tt == None:
        # Get TT for current year
        table_tt = get_table_tt(*configuration.year_semester)
    tt = table_tt.the_current_tt(table_tt).get(student_id, None)
    if tt and (not only_current or tt.current()):
        return tt.text()
    return ''

def title(name, sort_fct):
    """Columns title with the link to sort the HTML table"""
    return (name +
            ' <span class="x">(<a href="javascript:sort(' +
            sort_fct +
            ')">Trier</a>)</span>')

def alpha_html(server, year, semester, ue_name_endswith="",
               ue_name_startswith="", author=None, match=None):
    """Returns ABJ/DA information for all the students in HTML format"""
    _ = utilities._
    write = server.the_file.write
    write('''<html>
<head>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
</head>
<body>
<div id="x"></div>
''')
    progress_bar = utilities.ProgressBar(
        server, message = '<h1>' + server._("MSG_suivi_student_wait")+'</h1>')
    write('<table style="table-layout: fixed" border><tbody id="t">')
    line = '<tr>'  +  '<td>%s</td>' * 8  +  '</tr>\n'
    write(line % (
        _("COL_TITLE_0_1"),
        title(_("COL_TITLE_0_2"), 'cmp_name'),
        title(_("COL_TITLE_0_0"),  'cmp_id'),
        _("TH_what"),
        title(_("B_Date"), 'cmp_ue'),
        title(_("TH_end_or_ue"), 'cmp_ue2'),
        title(_("TH_comment"), 'cmp_comment'),
        title(_("TH_abj_author"), 'cmp_comment'),
        ))
    if match is None:
        match = "^" + ue_name_endswith + ".*" + ue_name_startswith + "$"
    match_compiled = re.compile(match)
    students = tuple(Abjs(year, semester).students(progress_bar))
    nb = 0
    for login in students:
        nb += 1
        progress_bar.update(nb, len(students))
        if match != "^.*$":
            for ue_code in inscrits.L_batch.ues_of_a_student_short(login):
                if match_compiled.match(ue_code):
                    break
            else:
                continue

        def w(a, b, c, d, e):
            fn, sn = inscrits.L_slow.firstname_and_surname(login)
            write( line % (fn, sn, login, a, b, c ,d, e))
        student = Abj(year, semester, login)
        for from_date, to_date, author2, comment in student.abjs:
            if author is None or author == author2:
                w('ABJ', from_date, to_date, html.escape(comment), author2)
        for ue_code, date, author2, comment in student.da:
            if author is None or author == author2:
                w('DAS', date, ue_code, html.escape(comment), author2)
    write('</tbody></table>'
          + '<script>abj_messages = [%s,%s,%s,%s] ; </script>' % (
              utilities.js(utilities._("MSG_abj_choose_action")),
              utilities.js(utilities._("MSG_abj_hide_abj")),
              utilities.js(utilities._("MSG_abj_hide_da")),
              utilities.js(utilities._("MSG_abj_display_all")))
    )
    progress_bar.hide()
    write(utilities.read_file(os.path.join('FILES', 'abj_recap.html')))

def underline(txt, char='='):
    """Returns the text preceded with a line of '=' of same length"""
    return '\n' + char * len(txt) + '\n' + txt + '\n' + char * len(txt) + '\n'

def nice_date(date):
    """Returns a DD/MM/YYYY/[AM] nicely formatted"""
    return date.replace('M',' ' + configuration.ampms_full[0]
                        ).replace('A', ' ' + configuration.ampms_full[1])

def get_table_tt(year, semester):
    """Returns the current database for TT"""
    return document.table(utilities.university_year(year, semester),
                          'Dossiers', 'tt')

def feedback(browser, letter, nr_letters):
    """This function displays a feedback in the browser while
    loading students informations"""
    if browser:
        nr_letters += 1
        if nr_letters % 80 == 0:
            letter += '\n'
        browser.write(letter)
        browser.flush()
        return nr_letters

#REDEFINE
# When a student has an ABJ it may be outside of UE schedule.
# The function returns the ABJs without ABJ outside of UE planning.
def prune_abjs(abj_list, group, sequence, ue_code):
    """Trim unecessary ABJS"""
    return abj_list

def do_prune(abj_list, first_day, last_day, group, sequence, ue_code):
    """Trim unecessary ABJS using first and last day of the course."""
    abjs_pruned = []
    messages = []
    for abjj in abj_list:
        if utilities.date_to_time(abjj[0][:-1], 0) >= last_day:
            continue
        if utilities.date_to_time(abjj[1][:-1], 8000000000) < first_day:
            continue
        if abjj[3].startswith('{{{MESSAGE}}}'):
            messages.append(abjj)
            continue
        abjs_pruned.append(abjj)

    return prune_abjs(abjs_pruned, group, sequence, ue_code) + messages

def ue_mails_and_comments(ue_code):
    """Returns the mails of the master of the UE and a comment
    about the origin of the mail address"""
    mails = []
    text = []
    the_ue = teacher.all_ues().get(ue_code[3:], None)
    if the_ue:
        for teacher_login in the_ue.responsables_login():
            fn, sn, mail = inscrits.L_slow.firstname_and_surname_and_mail(
                teacher_login)
            text.append("   * " + fn.title() + ' ' + sn.upper() + ' : ')
            if mail == None:
                text.append(utilities._("MSG_abj_unknown_mail"))
            else:
                mails.append(mail.lower())
                text.append(mail)
            text.append('\n')

    # Add other mails
            
    other_mails = []
    for an_other_mail in teacher.other_mails(ue_code[3:]):
        an_other_mail = an_other_mail.lower()
        if an_other_mail not in mails:
            other_mails.append(an_other_mail)

    if other_mails:
        text.append("   " + utilities._("MSG_other_mail") +
                 ', '.join(other_mails) + '\n')
        mails += other_mails

    # Add other mails from SPIRAL

    if the_ue:
        other_mails = []
        for an_other_mail in the_ue.mails():
            an_other_mail = an_other_mail.lower()
            if an_other_mail not in mails:
                other_mails.append(an_other_mail)

        if other_mails:
            text.append("   " + utilities._("MSG_other_mail2") +
                     ', '.join(other_mails) + '\n')
            mails += other_mails

    if len(mails) == 0:
        text.append(utilities._("MSG_no_master") + '\n')

    return mails, text

def ue_resume(ue_code, year, semester, browser=None):
    """Returns all the ABJ/DA/TT informations about the all the UE students"""
    nr_letters = 0

    table_tt = get_table_tt(year, semester)
    #
    # The UE title
    #
    the_ue = teacher.all_ues().get(ue_code[3:], None)

    if browser:
        text = []
        browser.write(utilities._("MSG_suivi_student_wait") + '\n')
    else:
        text = [utilities._("MSG_abj_mail_header") % configuration.server_url
                + '\n\n']

    if not the_ue:
        text.append(underline(ue_code + utilities._("MSG_abj_no_title")))
    else:
        text.append(underline(ue_code + ' : ' + the_ue.intitule()))

    text.append('\n' + utilities._("MSG_abj_link") + '\n\n')
    text.append('    %s/%s/%s/%s/resume\n' % (
        configuration.server_url, year, semester, ue_code))
    #
    # The UE managers
    #
    text.append(underline(utilities._("MSG_abj_master"), char='-'))
    mails, infos = ue_mails_and_comments(ue_code)
    text += infos

    the_students = []
    first_day = 0
    last_day = 8000000000

    if len(the_students) == 0:
        # Fast process but may be incomplete
        table_ue = document.table(year, semester, ue_code, create=False)
        if table_ue:
            the_students = [(line[0].value, line[3].value, line[4].value)
                            for line in table_ue.lines.values()
                            if line[0].value]
            first_day = table_ue.dates[0]
            last_day = table_ue.dates[1] + 86400 # End of last day
            table_ue.unload()
    if first_day == 0:
        first_day, last_day = utilities.semester_span(year, semester)
    utilities.warn('first_day=%s %s' % (first_day, last_day))
    #
    # The ABJ
    #
    first = True
    infos = []
    for student_login, group, sequence in the_students:
        student_id = inscrits.login_to_student_id(student_login)
        student = Abj(year, semester, student_id)
        
        abjs_pruned = do_prune(student.abjs, first_day, last_day,
                               group, sequence, ue_code) 

        if len(abjs_pruned) == 0:
            continue
        nr_letters = feedback(browser, 'A', nr_letters)
        if first:
            first = False
            text.append(underline(utilities._("TH_ABJ_list"), char='-'))
        fs = inscrits.L_slow.firstname_and_surname(student.login)
        the_abjs = ('   * ' + student.login + ' ' + fs[1].upper() + ' ' +
                    fs[0].title() + '\n')
        for abj in abjs_pruned:
            if abj[0] == abj[1]:
                an_abj = '      - ' + utilities._("MSG_abj_the") \
                    + ' ' + nice_date(abj[0])
            elif abj[0][:-1] == abj[1][:-1]:
                an_abj = '      - ' + utilities._("MSG_abj_the") \
                    + ' ' + abj[0][:-1]
            else:
                an_abj = "      - " + utilities._("MSG_abjtt_from_before") \
                    + " " + nice_date(abj[0]) + ' ' \
                    + utilities._("TH_until") + ' ' + nice_date(abj[1])
            if abj[3]:
                an_abj += ' (' + abj[3] + ')'
            
            the_abjs += an_abj + '\n'
        infos.append( (utilities.flat(fs[1]).lower(),
                    utilities.flat(fs[0]).lower(),
                    the_abjs) )
    if infos:
        infos.sort()
        text += list(zip(*infos))[2]
    #
    # The DA
    #
    first = True
    infos = []
    for student_login, group, sequence in the_students:
        student_id = inscrits.login_to_student_id(student_login)
        student = Abj(year, semester, student_id)
        dates = [d for d in student.current_das() if d[0] == ue_code]
        if dates:
            nr_letters = feedback(browser, 'D', nr_letters)
            if first:
                first = False
                text.append(underline(utilities._("MSG_abj_da_list"),
                                   char='-'))
            fs = inscrits.L_slow.firstname_and_surname(student_login)
            an_abj = ('   * ' + student_login + ' '
                      + fs[1].upper() + ' ' + fs[0].title()
                      + ' ' + utilities._("MSG_abj_tt_from") + dates[0][1])
            if dates[0][3]:
                an_abj += ' (' + dates[0][3] + ')'
            an_abj += '\n'
            
            infos.append((utilities.flat(fs[1]).lower(),
                          utilities.flat(fs[0]).lower(),
                          an_abj))
    if infos:
        infos.sort()
        text += list(zip(*infos))[2]
    #
    # The TT
    #
    first = True
    tt_logins = list(table_tt.logins())
    infos = []

    for student_login, group, sequence in the_students:
        infos_tt = tierstemps(student_login, table_tt = table_tt)
        if not infos_tt:
            continue
        nr_letters = feedback(browser, 'T', nr_letters)
        if first:
            first = False
            text.append(underline(utilities._("MSG_abj_tt_list"),
                               char='-'))
        fs = inscrits.L_slow.firstname_and_surname(student_login)
        a_tt = ('   * ' + student_login + ' ' + fs[1].upper() + ' '
                + fs[0].title() + '\n')
        for line in infos_tt.strip().split('\n'):
            a_tt += '      - ' + line + '\n'
        infos.append((utilities.flat(fs[1]).lower(),
                      utilities.flat(fs[0]).lower(),
                      a_tt))

    if infos:
        infos.sort()
        text += list(zip(*infos))[2]

    return text, mails

to_send_ok = [] # (Recipent, Title, message) list

def list_mail(browser, year, semester, only_licence=True):
    """Compute and display for all the UE the 'ue_resume'.
    Store the result in order to send all the mails after human check"""
    to_send = []
    sender = configuration.abj_sender
    browser.write(utilities._("MSG_abj_sender") + sender)
    browser.write('<pre>')

    ues = {}
    for login in Abjs(year, semester).students():
        student = Abj(year, semester, login)
        for a_da in student.da:
            ues[a_da[0]] = True
        if student.abjs:
            for ue_code in inscrits.L_batch.ues_of_a_student_short(student.login):
                ues[ue_code] = True

    table_tt = get_table_tt(year, semester)
    tt_logins = list(table_tt.logins())
    for student_login in tt_logins:
        for ue_code in inscrits.L_batch.ues_of_a_student_short(student_login):
            ues[ue_code] = True
    if only_licence:
        ues = [ue_code for ue_code in ues if ue_code[-1] == 'L']
    for ue_code in ues:
        lines, mails = ue_resume(ue_code, year, semester)
        browser.write(''.join(lines))
        if mails:
            to_send.append( (mails,
                             'ABJ + DA + TT pour l\'UE ' + ue_code,
                             ''.join(lines)) )
    global to_send_ok
    to_send_ok = to_send
    browser.write('</pre>' + utilities._("MSG_abj_send") % len(to_send))

to_send_ok_example = [
    (['exco@bat710.univ-lyon1.fr', 'thierry.excoffier@bat710.univ-lyon1.fr'],
     'UE_CODE x',
     'blabla'),
    (['exco@liris.univ-lyon1.fr', 'excé@www710.univ-lyon1.fr'],
     'UE_CODE y',
     'blaBLA'),
    (['exco@bat710.univ-lyon1.fr', 'thierry.excoffier@bat710.univ-lyon1.fr'],
     'UE_CODE z',
     'blabla'),
    ]

def send_mail(browser):
    """Send all the mails generated by 'list_mail'"""
    for recipients, mail_title, text in to_send_ok:
        try:
            utilities.send_mail_in_background(recipients,
                                              mail_title,
                                              text,
                                              configuration.abj_sender)
            browser.write("<p>" + repr(recipients)
                          + utilities._("MSG_abj_sent"))
        except UnicodeEncodeError:
            browser.write("<pre>BUG dans abj.send_mail</pre>")
