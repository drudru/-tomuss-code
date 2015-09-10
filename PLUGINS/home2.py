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

import os
from .. import plugin
from .. import utilities
from .. import inscrits
from .. import configuration
from .. import referent
from .. import document
from .. import files

files.add('PLUGINS', 'home2.js')
files.add('PLUGINS', 'home2.css')

def semester_list():
    options = configuration.special_semesters
    for (dummy_url, dummy_port, year, semester, dummy_host
         ) in configuration.suivi.urls_sorted():
        if (configuration.year_semester[1] == semester
            and configuration.year_semester[0] == year):
            selected = ' selected'
        else:
            selected = ''
        options += '<option%s>%s/%s</option>' % (selected, year, semester)
    return options

files.files['middle.js'].replace('home',
                                 '__OPTIONS__',
                                 semester_list().replace('selected',''))

def home_page(server):
    """Display TOMUSS home page, it extracts some links from the
    plugin list. The page content depends on user role."""
    f = server.the_file
    ticket = server.ticket
    user_name = ticket.user_name

    if inscrits.L_fast.password_ok(user_name):
        password_ok = ''
    else:
        password_ok = configuration.bad_password()

    favorites = utilities.manage_key('LOGINS',
                                     os.path.join(user_name, 'pages'))
    if favorites is False:
        favorites = {}
    else:
        favorites = eval(favorites)

    prefs_table = document.get_preferences(user_name, True, the_ticket=ticket)

    master_of = utilities.manage_key('LOGINS',
                                     os.path.join(user_name, 'master_of'))
    if master_of is False:
        master_of = []
    else:
        master_of = eval(master_of)

    bookmarked = utilities.manage_key('LOGINS',
                                      os.path.join(user_name, 'bookmarked'))
    if bookmarked:
        master_of += eval(bookmarked)

    refered = []
    tt = document.table(utilities.university_year(), 'Dossiers', 'tt')
    tt = tt.the_current_tt(tt)

    for login in referent.students_of_a_teacher(user_name):
        a,b,c = inscrits.L_fast.firstname_and_surname_and_mail(login)
        pe = int(configuration.student_in_first_year(login) or False)
        refered.append(('[' + utilities.js(login) + ','
                        + utilities.js(a) + ','
                        + utilities.js(b) + ','
                        + utilities.js(c) + ','
                        + utilities.js(pe) + ','
                        + utilities.js(int(login in tt
                                           and tt[login].current())) + ','
                        + utilities.js(configuration.student_class(login))
                        + ']').encode('utf-8'))

    favstu = utilities.manage_key('LOGINS',
                             os.path.join(user_name, 'favstu')
                             )
    if favstu is False:
        favstu = ''
    else:
        favstu = eval(favstu)
        favstu_infos = inscrits.L_fast.query_logins(
            favstu,
            (configuration.attr_login,
             configuration.attr_firstname,
             configuration.attr_surname,
             configuration.attr_mail,
         ))
        for login in set(favstu) - set(x[0] for x in favstu_infos):
            favstu_infos.append((login, "?", "?", "?"))
        favstu = ','.join(['[%s,%s,%s,%s]' %
                          (utilities.js(inscrits.login_to_student_id(x[0].lower().encode('utf8'))),
                           utilities.js(x[1].encode('utf-8')),
                           utilities.js(x[2].encode('utf-8')),
                           utilities.js(x[3].encode('utf-8')))
                           for x in favstu_infos])

    links = []
    for link, the_plugin in plugin.get_links(server):
        url, target = link.get_url_and_target(the_plugin)
        if the_plugin:
            p = the_plugin.name
        else:
            p = ''
        links.append(
            (link.where,
             link.priority,
             link.html_class,
             link.text or '',
             url, target,
             link.help,
             p,
             '/'.join((the_plugin and the_plugin.module or link.module)
                      .split('/')[-2:])))

    f.write(
        str(document.the_head)
        + document.translations_init(prefs_table['language'])
        +'''
<script src="%s/home2.js" onload="this.onloadDone=true;"></script>
<link rel="stylesheet" href="%s/home2.css" type="text/css">
<link href="%s/news.xml" rel="alternate" title="TOMUSS : News" type="application/rss+xml">
</HEAD>
<body>
<noscript><h1 style="font-size:400%%;background-color:red; color:white">'''
        % (configuration.url_files,
           configuration.url_files,
           configuration.url_files,
           )
        + server._('MSG_need_javascript') + '</h1></noscript><script>'
        + 'var tomuss_version="%s";\n' % configuration.version
        + 'var base="%s/=%s/";\n'      % (configuration.server_url,
                                          ticket.ticket)
        + 'var username2="%s";\n'      % utilities.login_to_module(user_name)
        + 'var username="%s";\n'       % user_name
        + 'var suivi=%s;\n'            % configuration.suivi.all(ticket.ticket)
        + 'var ticket="%s";\n'         % ticket.ticket
        + 'var root=%s;\n'             % utilities.js(list(configuration.root))
        + 'var my_identity = username ;\n'
        + 'var information_message=%s;\n'  % utilities.js(configuration.message)
        + 'var bad_password_message=%s;\n' % utilities.js(password_ok)
        + 'var url="%s";\n'                % utilities.StaticFile._url_
        + 'var admin="%s";\n'              % configuration.maintainer
        + 'var semester_list=%s;\n'        % utilities.js(semester_list())
        + 'var preferences='               + repr(prefs_table) + ';\n'
        + 'var ues_favorites='             + utilities.js(favorites) + ';\n'
        + 'var i_am_a_referent=%d;\n'      % int(ticket.is_a_referent)
        + 'var master_of=['
        + ','.join([utilities.js(list(m)) for m in master_of])
        + '];\n'
        + 'var referent_of=[' + ','.join(refered) + '];\n'
        + 'var favstu=[' + favstu + '];\n'
        + 'var links=['
        + ',\n'.join('['+','.join(utilities.js(j) for j in i) + ']'
                     for i in links)
        + '];\n'
        + configuration.home_page_js_hook(server)
        + utilities.wait_scripts()
        + 'function initialize_home()\n'
        + '{ if ( ! wait_scripts("initialize_home()") ) return ;\n'
        + 'generate_home_page() ;\n'
        + "}\n"
        + 'initialize_home();\n'
        + '</script>\n'
        + '<script id="uesjs" onload="update_ues2(\'\')" onreadystatechange="if ( document.getElementById(\'uesjs\').readyState === \'complete\') update_ues2(\'\')" src="'
        + configuration.url_files + '/all_ues.js"></script>'
        )

plugin.Plugin('homepage2', '/{=}', function=home_page, group='staff',
              launch_thread=True, unsafe=False)
