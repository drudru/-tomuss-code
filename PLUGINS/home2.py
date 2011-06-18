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

top = utilities.StaticFile(os.path.join('PLUGINS','home2.html'))

files.add('PLUGINS', 'home2.js')
files.add('PLUGINS', 'home2.css')

options = configuration.special_semesters
urls = configuration.suivi.urls.values()
# XXX HORRIBLE KLUDGE because Autumne is before Printemps
# sort the semesters by time
urls.sort(cmp=lambda x,y: cmp( (x[2], y[3]), (y[2], x[3]) ))
for url, port, year, semester, host in urls:
    if configuration.year_semester[1] == semester and configuration.year_semester[0] == year:
        selected = ' selected'
    else:
        selected = ''
    options += '<option%s>%s/%s</option>' % (selected, year, semester)
top.replace('home.py', '</select>', options + '</select>')

import files
files.files['middle.js'].replace('home',
                                 '__OPTIONS__',options.replace('selected',''))

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
    if (user_name in configuration.root) and server.options:
        user_name = server.options[0].strip('=')

    ufr = inscrits.L_fast.ufr_of_teacher(user_name)

    if inscrits.L_fast.password_ok(user_name):
        password_ok = ''
    else:
        password_ok = configuration.bad_password

    f.write(str(top).replace('_MESSAGE_', password_ok)
            .replace('_BASE_',
                     configuration.server_url+'/='+ticket.ticket+'/')
            .replace('_SUIVI_', configuration.suivi.all(ticket.ticket))
            .replace('_UFR_',
                     'UE-' + configuration.ufr_short.get(ufr,('',''))[0])
            .replace('_USERNAME2_',
                    utilities.login_to_module(user_name))
            .replace('_USERNAME_', user_name)
            .replace('_TICKET_', ticket.ticket)
            .replace('_MESSAGE2_', configuration.message)
            .replace('_ADMIN_', configuration.maintainer)
            .replace('_ROOT_', utilities.js(list(configuration.root)))
            )
    f.write('''<h2>Autres</h2>''')

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
        encodings = server.headers['Accept-Encoding']
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
