#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2008-2011 Thierry EXCOFFIER, Universite Claude Bernard
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

import plugin
import configuration
import inscrits
import referent
import utilities
import os
import tablestat
import abj
import document
import authentication
import cgi
import time
import teacher
import collections

header = utilities.StaticFile(os.path.join('FILES', 'suivi.html'))
header2 = utilities.StaticFile(os.path.join('FILES', 'suivi2.html'))
charte = utilities.StaticFile(os.path.join('FILES', 'charte.html'))


def tomuss_links(login, ticket, server, is_a_student=False):
    t = []
    try:
        year = 2000 + int(login[1:3])
    except ValueError:
        year = 0
    for url, port, tyear, tsemester, thost \
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
    return '<table class="tomuss_links colored"><tr><th><script>hidden(\'<span>Semestres</span>\',"Voir les notes dans TOMUSS pour un autre semestre");</script></tr><tr><td>' + ''.join(t) + '</tr></table>'

def member_of_list(login):
    x = '<script>hidden("Membre de...","<table class=\\"memberof\\">'
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

    s = ['<div class="student"><img class="photo" src="',
         configuration.picture(inscrits.login_to_student_id(login),
                               ticket=ticket),
         '">',
         tomuss_links(login, ticket, server, is_a_student) +
         abj.html_abjs(server.year, server.semester, login, read_only=True)
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
        s.append(u'Référent pédagogique : <script>hidden(\'<a href="mailto:' + mail_ref + '">' +
                 ref + u"</a>','Envoyez un message à l\\'enseignant référent pédagogique');</script><br>")
    else:
        if referent.need_a_referent(login):
            s.append(u"<script>hidden(\'Référent pédagogique : Aucun\','Seuls les étudiants inscrits pour la première fois à l\\'université ont un référent pédagogique.');</script><br>")
        else:
            s.append(u"<script>hidden(\'Référent pédagogique : Aucun\','Vous n\\'êtes pas dans la licence STS, vous n\\'avez donc pas d\\'enseignant référent');</script><br>")

    ################################################# TEACHERS MAILS

    if not is_a_student:
        teachers = collections.defaultdict(list)
        for t in the_ues(year, semester, login):
            if tuple(t.get_items(login)):
                for teacher_login in t.masters:
                    teachers[teacher_login].append(t.ue)
        if ref:
            teachers[ref].append(u'Référent')

        if teachers:
            s[-1] = s[-1].replace('<br>','')
            s.append(', <script>hidden(\'<a href="mailto:?to='
                     + ','.join([str(inscrits.L_fast.mail(k))
                                 + ' <' + ','.join(v) + '>'
                                 for k, v in teachers.items()])
                     + '&subject=' + (login + ' ' + firstname + ' ' + surname
                                      ).replace("'","\\'")
                     + u'">Mails responsables</a>\',"Liste les adresses mails du réferent ainsi que des<br>enseignants responsables des UE suivies par l\'étudiant.")</script><br>')

    ################################################# LOOK


    s.append('Regarder : ')
    
    # BILAN
    
    if not expand:
        s.append(u"""<script>hidden('<a href="%s" target="_blank">Bilan APOGÉE</a>','Affiche le récapitulatif des notes présentes dans APOGÉE<br>pour l\\'ensemble de la licence');""" %
                 (configuration.bilan_des_notes + login) + '</script>, ')

    if is_a_referent:
        s.append(u"""<script>hidden('<a href="%s/=%s/bilan/%s" target="_blank">Bilan TOMUSS</a>','Affiche le récapitulatif des notes présentes dans TOMUSS et APOGÉE.<br>Ceci permet de voir le nombre d\\'inscriptions à une UE.');""" %
                 (configuration.server_url, ticket.ticket, login) + '</script>, ')
    # CONTRACT

    if not is_a_student:
        if referent.need_a_charte(login):
            if utilities.manage_key('LOGINS',
                                    utilities.charte_server(login,server)):
                s.append(u'Contrat signé, ')
            else:
                s.append(u'<span style="background:red">Contrat non signé</span>, ')

        s.append(u'<script>hidden(\'<a href="%s/=%s/%s/%s/ %s" target="_blank">Vue étudiant</a>\',"Afficher ce que voit réellement l\'étudiant dans son navigateur");</script>, ' % (
            utilities.StaticFile._url_, ticket.ticket,
            year, semester, login))
    else:
        if referent.need_a_charte(login):
            s.append(u'<script>hidden(\'<a href="%s/charte.html" target="_blank">Contrat</a>\',"Le contrat pédagogique que vous avez signé.");</script>, ' %
                     utilities.StaticFile._url_)

    # MORE

    s.append(configuration.more_on_suivi(login))
    s.append('<br>')

    if not is_a_student:
        x, member_of = member_of_list(login)
        s.append(x)

    ################################################# FOR REFERENT

    if ref and ref == ticket.user_name and not is_a_student:
        tyear = utilities.university_year(year, semester)
        while True:
            table = document.table(tyear, 'Referents',
                                   utilities.login_to_module(ref), ro=True,
                                   create=False)
            if table is None:
                break
            first = True
            for line in table.get_lines(login):
                for i, col in enumerate(table.columns):
                    if i >= 3 and line[i].value:
                        if first:
                            s.append(u'<div class="blocnote">Vous êtes le seul à voir ces informations car vous êtes le référent pédagogique de l\'étudiant en %d-%d&nbsp;:<br>' % (tyear, tyear+1))
                            first = False
                        s.append(u'%s&nbsp;:&nbsp;<b>%s</b>,'
                                 % ( unicode(col.title, 'utf8'),
                                     unicode(cgi.escape(str(line[i].value)), 'utf8') ))
            if first == False:
                   s.append('</div>')
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
        s.append(u'<script>hidden(\'<a href="%s">Flux RSS : <img src="/feed.png" style="border:0px"></a>\',"Suivez ce lien pour recevoir les changements comme des actualités.<br>Dans votre navigateur, site web, lecteur de mail, portail étudiant...")</script>' % rss)
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
                    s.append(u"<h2 class=\"title\">Vous êtes inscrit à " + t
                             + ' ' + title + u"</h2><p>TOMUSS n'a pas été utilisé par un enseignant pour saisir des informations dans cette UE")
                else:
                    s.append(u"<p class=\"title\">Étudiant inscrit à "
                             + t + ' ' + title + u"</p>")

    if ss:
        ss.sort()
    s += ss

    if expand:
        xx = u"""<iframe style="width:100%%;height:120em" src="%s&ticket=%s"></iframe>""" % (configuration.bilan_des_notes + login, server.ticket.ticket)
    else:
        xx = ''

    table = document.table(utilities.university_year(), 'Dossiers', 'tt',
                           ro=True)
    tt = abj.tierstemps(login, aall=True, table_tt=table)
    if tt:
        tt = '<h2>Informations concernant le tiers temps :</h2><pre>' + cgi.escape(tt) + '</pre>'

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
        
    server.the_file.write((str(header2).replace("_USERNAME_",
                                          server.ticket.user_name)
                          .replace("_ADMIN_", configuration.maintainer) +
                          '<p id="x" style="background:yellow"><b>Chargement en cours, veuillez patienter s\'il vous plait. Cela ira encore plus lentement si vous réactualisez la page.</b></p>').replace('\n',''))
    server.the_file.flush()
    server.the_file.write(
        "<script>document.getElementById('x').style.display='none';</script>" +
        student_statistics(login, server,True).replace('\n','').encode('utf8'))


plugin.Plugin('student', '/{*}', function=student, teacher=False,
              launch_thread=True,
              password_ok = None)

def accept(server):
    """The student signs the contract"""
    utilities.manage_key('LOGINS',
                         utilities.charte(server.ticket.user_name),
                         content="Accept")
    student(server)
    

plugin.Plugin('accept', '/accept', function=accept, teacher=False,
              launch_thread=True,
              password_ok = None)


def home(server, nothing_behind=True):
    """Display the home page for 'suivi', it asks the student id."""
    the_header = str(header).replace("_TICKET_", server.ticket.ticket) \
                 .replace("_MESSAGE_", '') \
                 .replace("_SEMESTER_", server.semester) \
                 .replace("_USERNAME_", server.ticket.user_name) \
                 .replace("_YEAR_", str(server.year))

    server.the_file.write(the_header)

    if nothing_behind:
        server.the_file.write(student_statistics(server.ticket.user_name, server, is_a_student=True).encode('utf8'))

plugin.Plugin('home', '/', teacher=True, function = home)

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

    s = []
    firstname, surname, mail = inscrits.L_fast.firstname_and_surname_and_mail(login)
    s.append('%s <a href="mailto:%s">%s %s</a></h1>' % (
        login, mail, firstname.title(), surname))
    s.append(tomuss_links(login, ticket, server))
    s.append(member_of_list(login)[0])
    s = (' '.join(s) + '<br>').encode('utf8')

    if len(tables) == 0:
        return s

    return (
        s + "<p>Il a modifié %d notes dans %d UE" % (
        sum([v.nr for v in tables.values()]),
        len(tables)) +
        '\n'.join(['<TABLE class="colored"><tr><th>Lien vers l\'UE</th><th>Nombre<br>de notes</th><th>Première<br>modification le</th><th>Dernière<br>modification le</th></tr>'] +
                  [ str(t) for t in tables.values()] +
                  ['</TABLE>']))


def display_list(server, name):
    if name == '':
        return
    name = utilities.safe(name)
    t = list(inscrits.L_slow.firstname_or_surname_to_logins(name.replace('_',' ')))
    t.sort(key = lambda x: x[1] + x[2])
    if t:
        for lo, surname, name in t:
            s = '<a href="/=%s/%s/%s/%s">%s %s</a> (%s)<br>\n' % (
                server.ticket.ticket,
                server.year,
                server.semester,
                lo,
                surname,
                name,
                lo)
            server.the_file.write(s.encode('utf-8'))
    else:
        server.the_file.write('Nom et prénom inconnus.')


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

    if server.the_path[0].startswith('-'):
        display_list(server, server.the_path[0][1:].replace('+',' '))
    else:
        logins = server.the_path[0].replace('+',',').strip(',').split(',')
        logins = [inscrits.safe(lo).lower() for lo in logins]
        server.the_file.write(
            '<title>' +
            ', '.join([inscrits.L_fast.firstname_and_surname(login)[0].title() +
                       ' ' + inscrits.L_fast.firstname_and_surname(login)[1]
                      for login in logins]).encode('utf8') +
            '</title>'
                              ) ;
        for login in logins:
            display_login(server, login, expand)

    server.the_file.write('&nbsp;<br>'*10 +
                          '<p class="copyright">TOMUSS ' +
                          configuration.version + '</p>'
                          )

plugin.Plugin('infos', '/{*}', teacher=True, password_ok = None,
              function = page_suivi,
              launch_thread=True,
              )

def escape(t):
    return unicode(t,'utf8').replace('>', u'\ufe65').replace('<', u'\ufe64').replace('&','&amp;').encode('utf-8')


def rss_date(date=None):
    if date is None:
        date = time.localtime(time.time())
    elif isinstance(date, str):
        date = time.strptime(date, '%Y%m%d%H%M%S')
    return time.strftime('%a, %d %b %Y %H:%M:%S CEST', date)

def page_rss(server):
    """RSS for the student."""
    login = utilities.manage_key('RSSLOGINS', server.the_path[0], separation=2)
    if login is False:
        server.the_file.write('''<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
<language>fr</language> 
<title>TOMUSS</title>
<description>Dernières modifications dans TOMUSS</description>
<lastBuildDate>%s</lastBuildDate>
<link></link>
<item><title>Vous n\'avez pas le droit de regarder ce flux RSS</title>
<description>Pour des raisons de sécurité, il faut que vous réabonniez.</description>
<link>%s</link>
</item>
</channel>
</rss>
''' % ( time.asctime(), utilities.StaticFile._url_))
        return

    server.the_file.write('''<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
<language>fr</language>
<title>TOMUSS %s</title>
<description>Dernières modifications dans TOMUSS</description>
<lastBuildDate>%s</lastBuildDate>
<link>%s</link>''' % ( login, rss_date(), utilities.StaticFile._url_))

    s = []

    # Do not display change newer than ONE hour.
    if configuration.regtest:
        limit = '9999' # The regtests want to see all
    else:
        limit = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time() - 3600))
    
    for t in the_ues(server.year, server.semester, login):
        for line_id, line in t.get_items(login):
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
            comment=cgi.escape('Commentaire sur la valeur : <b>') + escape(cell.comment) + cgi.escape('</b>,<br>')
        else:
            comment = ''
        if column.comment:
            column_comment = 'Commentaire sur la colonne «' + \
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
                cgi.escape('Valeur modifiée par <b>' + cell.author
                           + '</b>,<br>À ' + utilities.nice_date(cell.date)
                           + '<br>')
                ) +
            '<link>%s</link>' % utilities.StaticFile._url_ +
            '<author>%s</author>\n' % cell.author +
            '<pubDate>%s</pubDate>\n' % rss_date(document.date_time(date))+
            '<guid>%s %s</guid>\n' % (table.ue, date) +
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
<description>Dernières modifications dans TOMUSS</description>
<lastBuildDate>%s</lastBuildDate>
<link>%s</link>
''' % (server.the_path[0], rss_date(), link))

    t = document.table(server.year, server.semester, server.the_path[0],
                       ro=True, create=False)
    if t is None:
        return
    # Only the 10 most recents pages containing modifications
    for p in [i for i in t.pages[1:] if i.request > 0 and i.date][-10:]:
        date = p.date_time()

        d = 'Connexion à %s,<br>%d changements faits' % (
             utilities.nice_date(p.date),
             p.request,
             )
        h = int((time.time() - time.mktime(date))/3600 + 1)
        t1 = p.day().replace('/', '%2501')

        f = '/=full_filter=@%s%%2520%%2502%%3C%%3D%s%%2520%%2502%%3E%%3D%s' % (p.user_name, t1, t1)

        server.the_file.write(
            '<item>\n' +
            '<title>%d modifications par %s</title>\n' % (p.request, p.user_name) +
            '<description>%s</description>\n' % cgi.escape(d) +
            '<link>%s%s</link>\n' % (link, f) +
            '<pubDate>%s</pubDate>\n' % rss_date(date)+
            '<author>%s</author>\n' % p.user_name +
            '<guid>%d</guid>\n' % t.pages.index(p) +
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

                       
