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

import plugin
import utilities
import os
import inscrits
import configuration
import referent
import teacher
import time
import document
import files

files.add('PLUGINS', 'home2.js')
files.add('PLUGINS', 'home2.css')

def semester_list():
    options = configuration.special_semesters
    for url, port, year, semester, host in configuration.suivi.urls_sorted():
        if (configuration.year_semester[1] == semester
            and configuration.year_semester[0] == year):
            selected = ' selected'
        else:
            selected = ''
        options += '<option%s>%s/%s</option>' % (selected, year, semester)
    return options

    
import files
files.files['middle.js'].replace('home',
                                 '__OPTIONS__',
                                 semester_list().replace('selected',''))

def home_box(server, where, title, html_class='with_margin'):
    links = plugin.get_menu_for(where, server, True)
    if links:
        server.the_file.write(
            '<table class="uelist ' + html_class + '"><tr><th>'
            + title +'</th></tr>\n'
            + '\n'.join(['<tr onmouseover="ue_line_over(\'\',this)"><td>'
                         + s + '</td></tr>'
                         for s in links]) + '\n</table>\n')
        return 'with_margin'
    return html_class
        
def home_page(server):
    """Display TOMUSS home page, it extracts some links from the
    plugin list. The page content depends on user role."""
    f = server.the_file
    ticket = server.ticket
    user_name = ticket.user_name
    # Not working because the functions look the ticket
    # if (user_name in configuration.root) and server.options:
    #    user_name = server.options[0].strip('=')

    if inscrits.L_fast.password_ok(user_name):
        password_ok = ''
    else:
        password_ok = configuration.bad_password

    f.write(str(document.the_head))
    f.write('''
<script src="%s/home2.js" onload="this.onloadDone=true;"></script>
<link rel="stylesheet" href="%s/home2.css" type="text/css">
<link href="%s/news.xml" rel="alternate" title="TOMUSS : nouveautés" type="application/rss+xml">
</HEAD>
<noscript><h1 style="font-size:400%%;background-color:red; color:white">
    Cette application nécessite que JavaScript soit activé
</h1></noscript>

<script>
''' % (utilities.StaticFile._url_,
       utilities.StaticFile._url_,
       utilities.StaticFile._url_,
       )
            + 'var base="%s/=%s/";\n' % (configuration.server_url,
                                       ticket.ticket)
            + 'var username2="%s";\n' % utilities.login_to_module(user_name)
            + 'var username="%s";\n' % user_name
            + 'var suivi=%s;\n' % configuration.suivi.all(ticket.ticket)
            + 'var ticket="%s";\n' % ticket.ticket
            + 'var root=%s;\n' % utilities.js(list(configuration.root))
            + 'var my_identity = username ;\n'
            + 'var information_message=%s;\n'%utilities.js(configuration.message)
            + 'var bad_password_message=%s;\n' % utilities.js(password_ok)
            + 'var url="%s";\n' % utilities.StaticFile._url_
            + 'var admin="%s";\n' % configuration.maintainer
            + 'var semester_list=%s;\n' % utilities.js(semester_list())
            + 'generate_home_page() ;\n'
            + '</script>\n'           
            )

    #####################################################################

    favorites = utilities.manage_key('LOGINS',
                                     os.path.join(user_name, 'pages'))
    if favorites is False:
        favorites = {}
    else:
        favorites = eval(favorites)
    prefs_table = document.get_preferences(user_name, True)

    f.write('<script>var preferences = ' + repr(prefs_table)
            + ' ;\nvar ues_favorites = ' + utilities.js(favorites)
            + ' ;\ni_am_a_referent = %d' % int(ticket.is_a_referent)
            + ';</script>\n')

    #####################################################################

    master_of = utilities.manage_key('LOGINS',
                                     os.path.join(user_name, 'master_of'))
    if master_of is False:
        master_of = []
    else:
        master_of = eval(master_of)

    f.write('<script>var master_of = ['
            + ','.join([utilities.js(list(m)) for m in master_of])
            + '];</script>\n')

    #####################################################################

    f.write('<script>var referent_of = [')
    t = []
    for login in referent.students_of_a_teacher(user_name):
        a,b,c = inscrits.L_fast.firstname_and_surname_and_mail(login)
        t.append(('[' + utilities.js(login) + ','
                 + utilities.js(a) + ','
                 + utilities.js(b) + ','
                 + utilities.js(c) + ']').encode('utf8'))
    f.write(','.join(t) + '];</script>')

    #####################################################################

    favstu = utilities.manage_key('LOGINS',
                             os.path.join(user_name, 'favstu')
                             )
    if favstu is False:
        favstu = ''
    else:
        favstu = eval(favstu)
        favstu = inscrits.L_fast.query_logins(favstu,
                                              (configuration.attr_login,
                                               configuration.attr_firstname,
                                               configuration.attr_surname,
                                               configuration.attr_mail,
                                               ))
        favstu = ','.join(['[%s,%s,%s,%s]' %
                          (utilities.js(inscrits.login_to_student_id(x[0].lower().encode('utf8'))),
                           utilities.js(x[1].encode('utf8')),
                           utilities.js(x[2].encode('utf8')),
                           utilities.js(x[3].encode('utf8')))
                          for x in favstu])
            

    f.write('<script>var favstu = [' + favstu + '];</script>')

    #####################################################################

    hclass = ''
    for key, title in plugin.get_box_list():
        hclass=home_box(server, key, title ,html_class=hclass)

    if user_name in configuration.root:
        f.write("Les portails : " +
                ',\n'.join(['<a href="javascript:go(%s)">%s</a>' %(
            repr('portail-' + p),p)
                            for p in configuration.the_portails])
                )
    f.write('\n</td></tr></table>')
    # XXX Tester si accept gz dans les headers
    try:
        encodings = server.headers['accept-encoding']
    except KeyError:
        encodings = ''
    utilities.warn('Encodings: ' + encodings)
    if 'Safari' not in ticket.user_browser \
       and 'Konqueror' not in ticket.user_browser \
       and 'Python-urllib' not in ticket.user_browser \
       and 'gzip' in encodings:
        f.write('<script src="' + configuration.server_url + '/all_ues.js.gz"></script>')
    else:
        f.write('<script src="' + configuration.server_url + '/all_ues.js"></script>')
    f.write('<script src="' + configuration.server_url + '/top_tail2.js"></script><p class="copyright">TOMUSS '
            + configuration.version + '</p>')


plugin.Plugin('homepage2', '/{=}', function=home_page, teacher=True,
              launch_thread=True)
