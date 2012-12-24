#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2008-2012 Thierry EXCOFFIER, Universite Claude Bernard
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
If there is a ':' before the login name then the APOGEE link is
translated as an IFRAME to include all the information.
"""

import os
import time
import cgi
import collections
from .. import plugin
from .. import configuration
from .. import inscrits
from .. import referent
from .. import utilities
from .. import tablestat
from .. import abj
from .. import document
from .. import teacher
from .. import files

charte =utilities.StaticFile(os.path.join('PLUGINS','suivi_student_charte.html'))

files.add('PLUGINS', 'suivi_student.css')
files.add('PLUGINS', 'suivi_student.js')
files.add('PLUGINS', 'suivi_student_doc.html')
files.add('PLUGINS', 'suivi_student_charte.html').replace('suivi_student',
                                                          '<input', '<p')

def tomuss_links(login, ticket, server, is_a_student=False):
    t = []
    try:
        year = 2000 + int(login[1:3])
    except ValueError:
        year = 0
    for url, dummy_port, tyear, tsemester, dummy_thost \
            in configuration.suivi.url_with_ticket(ticket.ticket):
        if tyear == server.year and tsemester == server.semester:
            highlight = ' class="highlight"'
        else:
            highlight = ''
        if tyear < year:
            continue

        if is_a_student:
            icone = ''
        else:
            icone = '<img class="icone" src="%s/_%s">' % (url, login)

        t.append('<div%s><a href="%s/%s">%s %s %s</a></div>' % (
            highlight, url, login, icone, tsemester, tyear))
    t.sort(key=lambda x: x.split('href="')[1].replace('A','Z') )
    return '''<table class="tomuss_links colored">
<tr><th><script>hidden('<span>' + _("MSG_suivi_student_semesters")
                       + '</span>',
                       _("TIP_suivi_student_semesters"));</script></tr>
<tr><td>''' + ''.join(t) + '</tr></table>'

def member_of_list(login):
    x = '<script>hidden(_("MSG_suivi_student_memberof"),"<table class=\\"memberof\\">'
    member_of = list(inscrits.L_fast.member_of_list(login))
    member_of.sort()
    for i in member_of:
        x += '<tr><th>' + cgi.escape(unicode(i,configuration.ldap_encoding)).replace('"','\\"') \
                                 .replace(',DC=univ-lyon1,DC=fr','') \
                                 .replace(',','<td>') + '</tr>'
    x += '</table>");</script>'
    return x, member_of

last_full_read_time = 0


def the_ues(year, semester, login):
    global last_full_read_time
    if configuration.regtest or time.time() - last_full_read_time > 60:
        last_full_read_time = time.time()
        return tablestat.les_ues(year, semester, true_file=False)
    else:
        login = utilities.the_login(login)
        tables = []
        for ue in document.tables_of_student.get(login,[]):
            the_table = document.table(year, semester, ue, ro=True)
            if the_table.official_ue:
                tables.append(the_table)
        return tables

# To not have duplicate error messages
referent_missing = {}

def student_statistics(login, server, is_a_student=False, expand=False,
                       is_a_referent=False):
    utilities.warn('Start', what='table')
    ticket = server.ticket
    year = server.year
    semester = server.semester
    firstname, surname, mail = inscrits.L_fast.firstname_and_surname_and_mail(login)

    s = [
        "<script>document.getElementById('x').style.display='none';</script>",
        '<div class="student"><img class="photo" src="',
         configuration.picture(inscrits.login_to_student_id(login),
                               ticket=ticket),
         '">',
         tomuss_links(login, ticket, server, is_a_student) +
         abj.html_abjs(server.year, server.semester, login)
         ,
         '<h1>'
         ]
    s.append('%s <a href="mailto:%s">%s %s</a></h1>' % (
        login, mail, firstname.title(), surname))

        

    ################################################# REFERENT

    ref = referent.referent(year, semester, login)

    if ref:
        mail_ref = inscrits.L_fast.mail(ref)
        if mail_ref == None:
            mail_ref = 'mail_inconnu'
        s.append('<script>Write("MSG_suivi_referent_is") ; hidden(\'<a href="mailto:' + mail_ref + '">' +
                 ref + "</a>', _('MSG_suivi_student_send_to_referent'));</script><br>")
    else:
        s.append("<script>hidden(_('MSG_suivi_student_no_referent'),_(")
        if referent.need_a_referent(login):
            s.append("'TIP_suivi_student_no_referent_needed'")
        else:
            s.append("'TIP_suivi_student_no_referent'")
        s.append("));</script><br>")

    ################################################# TEACHERS MAILS

    if not is_a_student:
        teachers = collections.defaultdict(list)
        for t in the_ues(year, semester, login):
            if tuple(t.get_items(login)):
                for teacher_login in t.masters:
                    teachers[teacher_login].append(t.ue)
        if ref:
            teachers[ref].append(server.__("MSG_suivi_student_referent"))

        if teachers:
            s[-1] = s[-1].replace('<br>','')
            s.append(', <script>hidden(\'<a href="mailto:?to='
                     + ','.join(['+'.join(v) +
                                 ' <' + str(inscrits.L_fast.mail(k)) + '>'
                                 for k, v in teachers.items()])
                     + '&subject=' + (login + ' ' + firstname + ' ' + surname
                                      ).replace("'","\\'")
                     + '">\' + _("MSG_suivi_student_mail_all") + \'</a>\','
                     + '_("TIP_suivi_student_mail_all"));</script><br>')

    ################################################# LOOK


    s.append('Regarder : ')
    
    # BILAN
    
    if not expand:
        s.append("""<script>
hidden('<a href="%s" target="_blank">'
       + _("MSG_suivi_student_official_bilan") + '</a>'
       , _("TIP_suivi_student_official_bilan"));""" %
                 (configuration.bilan_des_notes + login) + '</script>, ')

    if is_a_referent:
        s.append("""<script>
hidden('<a href="%s/=%s/bilan/%s" target="_blank">'
       + _("MSG_suivi_student_TOMUSS_bilan") + '</a>'
       , _("TIP_suivi_student_TOMUSS_bilan"));""" %
                 (configuration.server_url, ticket.ticket, login) + '</script>, ')
    # CONTRACT

    if not is_a_student:
        if referent.need_a_charte(login):
            if utilities.manage_key('LOGINS',
                                    utilities.charte_server(login,server)):
                s.append('<script>Write("MSG_suivi_student_contract_checked");</script>')
            else:
                s.append('''<span style="background:red">'
<script>Write("MSG_suivi_student_contract_unchecked");</script></span>''')
            s.append(', ')
        s.append('''<script>
hidden('<a href="%s/=%s/%s/%s/ %s" target="_blank">'
       + _("MSG_suivi_student_view") + '</a>',
       _("TIP_suivi_student_view"));
</script>, ''' % (
            utilities.StaticFile._url_, ticket.ticket,
            year, semester, login))
    else:
        if referent.need_a_charte(login):
            s.append('''<script>
hidden('<a href="%s/suivi_student_charte.html" target="_blank">'
       + _("MSG_suivi_student_contract_view") + '</a>',
       _("TIP_suivi_student_contract_view"));</script>, ''' %
                     utilities.StaticFile._url_)

    # MORE

    s.append(configuration.more_on_suivi(login, server))
    s.append('<br>')

    if not is_a_student:
        s.append(member_of_list(login)[0])

    ################################################# FOR REFERENT

    if ref and ref == ticket.user_name and not is_a_student:
        tyear = utilities.university_year(year, semester)
        while True:
            table = document.table(tyear, 'Referents',
                                   utilities.login_to_module(ref), ro=True,
                                   create=False)
            if table is None:
                break
            s.append(table.referent_resume(table, login))
            # table.unload() # XXX Memory leak
            tyear -= 1

    ################################################# FOR STUDENT


    if is_a_student:
        key = utilities.manage_key('LOGINS', os.path.join(login,'rsskey'))
        if key is False:
            import random
            random.seed()
            key = random.randint(0, 1000000000000000000)
            random.seed(id(s))
            key += random.randint(0, 1000000000000000000)
            key = "%x" % key
            utilities.manage_key('LOGINS', os.path.join(login, 'rsskey'),
                                 content=key)
            utilities.manage_key('RSSLOGINS', key, content=login, separation=2)

        if ticket.user_name != login:
            key = ''

        rss = '%s/rss/%s' % (utilities.StaticFile._url_, key)
        s.append('''<script>
hidden('<a href="%s">' + _("MSG_suivi_student_RSS") +
       '<img src="%s/feed.png" style="border:0px"></a>\',
       _("TIP_suivi_student_RSS"));</script>''' % (rss, utilities.StaticFile._url_))
        s.append('<link href="%s" rel="alternate" title="TOMUSS" type="application/rss+xml">' % rss)
 
    
    s.append('<p>')

    ss = []
    codes = {}
    for t in the_ues(year, semester, login):
        for line_id, line in t.get_items(login):
            ss.append(unicode(t.lines.line_html(
                t, line, line_id, ticket.ticket,
                link=not is_a_student
                ),'utf8'))
            if ss[-1]:
                # A line has been displayed
                codes[t.ue_code] = True
    if (configuration.suivi_display_more_ue
        and (year, semester) == configuration.year_semester
        and (not is_a_student or configuration.suivi_check_student_lists(login))
        ):
        for t in inscrits.L_fast.ues_of_a_student_short(login):
            # import cgi
            # ss.append(cgi.escape(repr(t)))
            if '-' not in t:
                continue
            title = teacher.all_ues().get(t.split('-')[1])
            if title:
                title = title.intitule()
            else:
                title = ''
            if t not in codes:
                if is_a_student:
                    s.append('''
<h2 class=\"title\"><script>
Write("MSG_suivi_student_not_in_TOMUSS_before")'
</script>''' + t + ' ' + title + '''</h2><p>
<script>Write("MSG_suivi_student_not_in_TOMUSS_after")</script>
''')
                else:
                    s.append('<p class="title"><script>'
                             + 'Write("MSG_suivi_student_registered")'
                             + '</script>' + t + ' ' + title + "</p>")

    if ss:
        ss.sort()
    s += ss

    if expand:
        xx = """<iframe style="width:100%%;height:120em" src="%s&ticket=%s"></iframe>""" % (configuration.bilan_des_notes + login, server.ticket.ticket)
    else:
        xx = ''

    table = document.table(utilities.university_year(), 'Dossiers', 'tt',
                           ro=True)
    tt = abj.tierstemps(login, aall=True, table_tt=table)
    if tt:
        tt = '<h2><script>Write("MSG_suivi_student_tt");</script></h2><pre>' + cgi.escape(tt) + '</pre>'

    s.append(xx)
    s.append(tt)
    s.append('</div>')

    return '\n'.join(s)

def student(server, login=''):
    """Display all the informations about a student."""
    if not login:
        login = server.ticket.user_name
        
    if referent.need_a_charte(server.ticket.user_name) \
           and utilities.manage_key('LOGINS',
                                    utilities.charte(server.ticket.user_name)
                                    ) == False:
        server.the_file.write(str(charte).replace("_TICKET_", server.ticket.ticket))
        return

    suivi_headers(server, is_student=True)
    server.the_file.write(
        student_statistics(login, server,True).replace('\n','').encode('utf8'))


plugin.Plugin('student', '/{*}', function=student, group='!staff',
              launch_thread=True,
              password_ok = None)

def accept(server):
    """The student signs the contract"""
    utilities.manage_key('LOGINS',
                         utilities.charte(server.ticket.user_name),
                         content="Accept")
    student(server)
    

plugin.Plugin('accept', '/accept', function=accept, group='!staff',
              launch_thread=True,
              password_ok = None)

def suivi_headers(server, is_student=True):
    server.ticket.set_language(server.headers.get('accept-language',''))
    server.the_file.write(str(document.the_head)
                          + document.translations_init(server.ticket.language)
                          )
    server.the_file.flush()
    server.the_file.write(
        '<link rel="stylesheet" href="%s/suivi_student.css" type="text/css">\n'
        % utilities.StaticFile._url_
        + '<script src="%s/suivi_student.js" onload="this.onloadDone=true;"></script>\n' % utilities.StaticFile._url_
        + '<noscript><h1>'+server._('MSG_need_javascript')+'</h1></noscript>\n'
        "<script>"
        + "var semester = %s;\n" % utilities.js(server.semester         )
        + "var year     = %s;\n" % utilities.js(server.year             )
        + "var ticket   = %s;\n" % utilities.js(server.ticket.ticket    )
        + "var username = %s;\n" % utilities.js(server.ticket.user_name )
        + "var admin    = %s;\n" % utilities.js(configuration.maintainer)
        + "var is_a_teacher = %s;\n" % int(not is_student)
        + "var root = %s ;\n" % utilities.js(list(configuration.root))
        + "var maintainer = %s;\n" % utilities.js(configuration.maintainer)
        + "var message = %s;\n" % utilities.js(
            configuration.suivi_student_message)
        + "</script>\n"
        + "</head>\n"
        + '<body class="%s">\n' % server.semester
        + '<div id="top"></div>'
        + '<div id="allow_inline_block" class="notes"></div>\n'
        + '<p id="x" style="background:yellow"></p>'
        + '<script>\n'
        + utilities.wait_scripts()
        + 'function initialize_suivi()'
        + '{ if ( ! wait_scripts("initialize_suivi()") ) return ;'
        + 'initialize_suivi_real() ; }'
        + 'initialize_suivi();\n'
        + '</script>\n'        
        )

def home(server, nothing_behind=True):
    """Display the home page for 'suivi', it asks the student id."""
    suivi_headers(server, is_student=nothing_behind)

    if nothing_behind:
        server.the_file.write(student_statistics(server.ticket.user_name, server, is_a_student=True).encode('utf8'))

plugin.Plugin('home', '/', group='staff', function = home)

def teacher_statistics(login, server):
    ticket = server.ticket
    tables = {}
    for t in tablestat.les_ues(server.year, server.semester, true_file=True):
        for line in t.lines.values():
            if t not in tables:
                for v in line:
                    if v.author == login:
                        url = '<a href="%s/=' % configuration.server_url + \
                              ticket.ticket + '/' + \
                              str(t.year) + '/' + str(t.semester) + '/' + \
                              t.ue + '/=full_filter=@' + login + '" target="_blank">' + \
                              t.location() + '</a>'
                        tables[t] = tablestat.TableStat(url)
                        break
    for t in tables:
        for line in t.lines.values():
            for v in line:
                if v.author == login:
                    tables[t].update(v)

    s = ["<script>document.getElementById('x').style.display='none';</script>"]

    firstname, surname, mail = inscrits.L_fast.firstname_and_surname_and_mail(login)
    s.append('%s <a href="mailto:%s">%s %s</a></h1>' % (
        login, mail, firstname.title(), surname))
    s.append(tomuss_links(login, ticket, server))
    s.append(member_of_list(login)[0])
    s = (' '.join(s) + '<br>').encode('utf8')

    if tables:
        s += ("<p>" + server._("MSG_suivi_student_ue_changes") % (
                sum([v.nr for v in tables.values()]),
                len(tables)) +
              '\n'.join(['''
<TABLE class="colored"><tr>
<th><script>Write("TH_suivi_student_ue");</script></th>
<th><script>Write("TH_suivi_student_nr_grades");</script></th>
<th><script>Write("TH_suivi_student_first_change");</script></th>
<th><script>Write("TH_suivi_student_last_change");</script></th></tr>
'''] +
                        [ str(t) for t in tables.values()] +
                        ['</TABLE>']))

    students = referent.students_of_a_teacher(login)
    if students:
        s += '<p><script>Write("MSG_suivi_student_contact_for");</script>'
        s += '<table class="colored">'
        for student in students:
            infos = inscrits.L_slow.get_student_info(student)
            infos = [unicode(i) for i in infos]
            s += ('<tr><th>' + student + '<td>' + '<td>'.join(infos) + '</tr>'
                  ).encode('utf-8')
        s += '</table>'
    return s

def display_login(server, login, expand=False):
    if login == '':
        return

    # login = login.lower().replace('_', ' ')
    if login[1].isdigit():
        # Student
        try:
            login = utilities.the_login(login)
            server.the_file.write(
                student_statistics(login, server,
                                   is_a_student=False,
                                   is_a_referent=server.ticket.is_a_referent,
                                   expand=expand)
                .encode('utf8'))
        except ValueError:
            raise
    else:
        server.the_file.write(teacher_statistics(login, server))
    server.the_file.flush()
    

def page_suivi(server):
    """Display the informations about all the students indicated."""
    if len(server.the_path) == 0:
        server.the_path = [''] # XXX Not nice

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
                  for login in logins]).encode('utf8') +
        '</title>'
                          )
    for login in logins:
        display_login(server, login, expand)

    server.the_file.write('&nbsp;<br>'*10 +
                          '<p class="copyright">TOMUSS ' +
                          configuration.version + '</p>'
                          )

plugin.Plugin('infos', '/{*}', group='staff', password_ok = None,
              function = page_suivi,
              launch_thread=True,
              )

def escape(t):
    return unicode(t,'utf-8').replace('>', u'\ufe65').replace('<', u'\ufe64').replace('&','&amp;').encode('utf-8')

def rss_author(x):
    try:
        fn, sn = inscrits.L_fast.firstname_and_surname(x)
        fn = fn.encode('utf8')
        sn = sn.encode('utf8')
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
    login = utilities.manage_key('RSSLOGINS', server.the_path[0], separation=2)
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
    
    for t in the_ues(server.year, server.semester, login):
        for line in t.get_lines(login):
            for cell,column in zip(line[6:], t.columns[6:]):
                if cell.date > limit:
                    continue
                if cell.value == '':
                    continue
                if not column.visible():
                    continue # Hidden column
                if column.type.cell_compute == 'undefined':
                    s.append((cell.date, cell, t, column))
    s.sort()
    for date, cell, table, column in s[-10:]:
        if cell.comment:
            comment= cgi.escape(utilities._("MSG_suivi_student_RSS_value_comment")
                                + '<b>') + escape(cell.comment) + cgi.escape('</b>,<br>')
        else:
            comment = ''
        if column.comment:
            column_comment = utilities._("MSG_suivi_student_RSS_column_comment"
                                      ) + '«' + \
                             escape(column.title) + cgi.escape('» : <b>') + escape(
                column.comment) + cgi.escape('</b>,<br>')
        else:
            column_comment = ''
        if column.type.name == 'Note':
            note_range = column.type.value_range(*column.min_max())
        else:
            note_range = ''
        table_title = escape(table.table_title)
        if table.comment:
            table_title += ' (<b>' + escape(table.comment) + '</b>)'
        table_title = cgi.escape(table_title + ',<br>')
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
                cgi.escape(utilities._("MSG_suivi_student_RSS_value_modified")
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
              mimetype = 'application/rss+xml',
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
    for p in [i for i in t.pages[1:] if i.request > 0 and i.date][-10:]:
        date = p.date_time()

        d = utilities._("MSG_suivi_student_RSS_table") % (
             utilities.nice_date(p.date),
             p.request,
             )
        t1 = p.day().replace('/', '$2F')
        # %3C %3E to not broke XML syntax
        # $20 $3F to not be tampered
        f = '/=full_filter=@%s$20$3F%%3C_E%s$20$3F%%3E_E%s' % (
            p.user_name, t1, t1)
        server.the_file.write(
            '<item>\n' +
            '<title>%d modifications par %s</title>\n' % (p.request, p.user_name) +
            '<description>%s</description>\n' % cgi.escape(d) +
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
              mimetype = 'application/rss+xml',
              )
