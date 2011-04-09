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

css = '''

TABLE.top2 { empty-cells: show; width:100%; table-layout: fixed ; }

TABLE.top2 TR TD { 
  vertical-align: top ;
}

TABLE.top2 INPUT { background-color: #DDD ; }
TABLE.top2 INPUT.search_field  {
  background-color: white ;
  border: 1px solid black ;
  width: 100% ;
}
TABLE.top2 U { background-color: yellow; text-decoration: none }
TABLE.top2 H2 { text-align: center; margin: 0 }

TABLE.uelist, TABLE.student_list, DIV#the_students TABLE { 
  width: 100% ;
  table-layout: fixed ;
  border-spacing: 0px;
  border: 1px solid #0B0;
}


TABLE.with_margin { margin-top: 0.6em ; }

TABLE.uelist TH, TABLE.student_list TH, DIV#the_students TABLE TH { 
  border-bottom: 1px solid #0B0;
  min-height: 1em ; /* Only for IE !!! */
  
}

TABLE.searchresult { 
  margin-top: 0em ;
}

TABLE.student_list TR.ue_list_more TD, TABLE.uelist TR.ue_list_more TD { 
  white-space: normal ;
}

TABLE.uelist TR TD, TABLE.student_list TR TD {
  white-space: nowrap ;
  overflow: hidden;
  margin: 0px ;
  padding: 0px ;
  color: blue;
}

COL.student_id { width: 5em; }
COL.student_icon { width: 35px; }
COL.code { width: 7.6em ; }
COL.responsable { width: 10em ; }

TABLE.uelist INPUT { width: 5em ;  }

TABLE.uelist TR.search TD { padding: 0.4em ; color: black; }

TABLE.uelist DIV.help { display: none ; font-style: italic; font-size: small }
TABLE.uelist TR.ue_list_more DIV.help { display: block }

IMG.safety { border:0 ;width: 0.7em ; vertical-align: middle  }



TABLE.student_list TR.hover TD, TABLE.uelist TR.hover TD, TABLE.uelist TR.ue_list_more TD, TABLE.student_list TR.ue_list_more TD { 
  background-color: #CCF ;
}

TABLE.uelist TR.unsaved_data TD { color: #F00; }

TABLE.uelist TR.with_students TD.title { font-weight: bold ; }

TABLE.uelist TR TH { height: 0.5em ; margin: 0; padding: 0 }

IMG.tt { height: 1em ; float:right; }

TABLE.uelist TD.title, TABLE TD.student_id { 
border-right: 1px solid #0B0 ;
border-left: 1px solid #0B0 ;
}


DIV.ue_list_more, SPAN.ue_list_more_help {
  border: 2px outset #AAA ;
  border: 2px outset #4F4 ;
  background-color: #CCC ;
}

DIV.ue_list_more { 
  position:absolute;
}

DIV.ue_list_more DIV.title:hover { 
  background-color: #0F0 ;
/*  padding-bottom: 2px ; Flickering hover bug in firefox */
}

DIV.ue_list_more DIV.more DIV.no_menu { display: none; }
DIV.ue_list_more:hover DIV.more DIV.no_menu { display: block; }
DIV.ue_list_more DIV.more DIV.no_menu:hover { display: none; }

DIV.ue_list_more DIV.title { 
  background-color: #8F8 ;
  text-align: left;
  font-weight: bold ;
/*  font-size: 70%; */
}

DIV.ue_list_more DIV.more { 
  background-color: white ;
}

DIV.ue_list_more DIV.more A:hover { 
  text-decoration: underline ;
}


#feedback .frame { 
  position: absolute ;
  left: 25% ;
  top: 25% ;
  width: 20em ;
  height: 10em ;
  border: 2px outset #AAA ;
 }

#feedback .frame DIV { 
  width: 100% ;
  background-color: #CCC ;
  color: black ;
}

#feedback .frame DIV:hover { 
  background-color: #EEE ;
}

#feedback .frame IFRAME { 
  background-color: white ;
  width: 100% ;
  height: 100% ;
}

'''

top = utilities.StaticFile(os.path.join('FILES','top2.html'))

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

    ufr = inscrits.L_fast.ufr_of_teacher(ticket.user_name)

    if inscrits.L_fast.password_ok(ticket.user_name):
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
                    utilities.login_to_module(ticket.user_name))
            .replace('_USERNAME_', ticket.user_name)
            .replace('_TICKET_', ticket.ticket)
            .replace('_MESSAGE2_', configuration.message)
            .replace('_ADMIN_', configuration.maintainer)
            .replace('_ROOT_', utilities.js(list(configuration.root)))
            )
    f.write('''<h2>Autres</h2>''')

    #####################################################################

    favorites = utilities.manage_key('LOGINS',
                                     os.path.join(ticket.user_name, 'pages'))
    if favorites is False:
        favorites = {}
    else:
        favorites = eval(favorites)
    prefs_table = document.get_preferences(ticket.user_name, True)

    f.write('<script>var preferences = ' + repr(prefs_table)
            + ' ;\nvar ues_favorites = ' + utilities.js(favorites)
            + ' ;\ni_am_a_referent = %d' % int(ticket.is_a_referent)
            + ';</script>\n')

    #####################################################################

    master_of = utilities.manage_key('LOGINS',
                                     os.path.join(ticket.user_name,
                                                  'master_of'))
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
    for login in referent.students_of_a_teacher(ticket.user_name):
        a,b,c = inscrits.L_fast.firstname_and_surname_and_mail(login)
        t.append(('[' + utilities.js(login) + ','
                 + utilities.js(a) + ','
                 + utilities.js(b) + ','
                 + utilities.js(c) + ']').encode('utf8'))
    f.write(','.join(t) + '];</script>')

    #####################################################################

    favstu = utilities.manage_key('LOGINS',
                             os.path.join(ticket.user_name, 'favstu')
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

    if ticket.user_name in configuration.root:
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
       and 'gzip' in encodings:
        f.write('<script src="' + configuration.server_url + '/all_ues.js.gz"></script>')
    else:
        f.write('<script src="' + configuration.server_url + '/all_ues.js"></script>')
    f.write('<script src="' + configuration.server_url + '/top_tail2.js"></script><p class="copyright">TOMUSS '
            + configuration.version + '</p>')


plugin.Plugin('homepage2', '/', function=home_page, teacher=True,
              launch_thread=True, css=css)
