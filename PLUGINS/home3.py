#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2015 Thierry EXCOFFIER, Universite Claude Bernard
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
import ast
from .. import plugin
from .. import utilities
from .. import inscrits
from .. import configuration
from .. import referent
from .. import document
from .. import files
from .. import display

D = display.Display

files.add('PLUGINS', 'home3.css')
files.add('PLUGINS', 'home3.js')

@utilities.add_a_cache0
def HomeSemesters():
    return configuration.suivi.urls_sorted()

def HomePreferences(server):
    return document.get_preferences(server.ticket.user_name, True,
                                    the_ticket=server.ticket)

def HomeUENrAccess(server):
    fav = utilities.manage_key('LOGINS',
                               os.path.join(server.ticket.user_name, 'pages'))
    if fav:
        fav = eval(fav)
    else:
        fav = {}
    return fav

def HomeUEBookmarked(server):
    fav = utilities.manage_key('LOGINS',
                               os.path.join(server.ticket.user_name,
                                            'bookmarked'))
    if fav:
        fav = eval(fav)
    else:
        fav = []
    return fav
    
def HomeUEMasterOf(server):
    fav = utilities.manage_key('LOGINS',
                               os.path.join(server.ticket.user_name,
                                            'master_of'))
    if fav:
        fav = eval(fav)
    else:
        fav = []
    return fav

def get_student_info(logins):
    if not logins:
        return []
        
    fav = inscrits.L_fast.query_logins(logins,
                                       (configuration.attr_login,
                                        configuration.attr_firstname,
                                        configuration.attr_surname,
                                        configuration.attr_mail,
                                    ))
    for login in set(utilities.the_login(login)
                     for login in logins
                    ) - set(x[0] for x in fav):
        fav.append([login, "?", "?", "?"])
    tt = document.table(utilities.university_year(), 'Dossiers', 'tt')
    tt = tt.the_current_tt(tt)
    for f in fav:
        s = f[0] = inscrits.login_to_student_id(f[0])
        f.append(configuration.student_in_first_year(s) or False)
        f.append(s in tt   and   tt[s].current())
        f.append(configuration.student_class(s))
        f.append(referent.get(s))
    return fav

def HomeStudentFavorites(server):
    fav = utilities.manage_key('LOGINS',
                               os.path.join(server.ticket.user_name, 'favstu'))
    if fav:
        fav = ast.literal_eval(fav)
        return get_student_info(fav)
    return ()

def HomeStudentRefered(server):
    fav = referent.students_of_a_teacher(server.ticket.user_name)
    return get_student_info(fav)

def HomeActions(server):
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
    return links  
    
D('Home'           , []          ,0, js='Vertical')
D('HomeRight'      , 'Home'      ,0, js='Horizontal')
D('HomeTop'        , 'Home'      ,1, js='Horizontal')
D('HomeMessage'    , 'Home'      ,2, lambda x: configuration.message)
D('HomeColumns'    , 'Home'      ,3)

D('HomeTitle'      , 'HomeTop'   ,0)
D('HomeSemesters'  , 'HomeTop'   ,1, lambda x: HomeSemesters())
D('HomeProfiling'  , 'HomeTop'   ,2)

D('HomeIdentity'   , 'HomeRight' ,1, js='Vertical')
D('HomeFeed'       , 'HomeRight' ,2)
D('HomeHelp'       , 'HomeRight' ,3)
D('HomePreferences', 'HomeRight' ,4, HomePreferences)

D('HomePreferencesLanguages'       , 'HomePreferences',0)
D('HomePreferencesSize'            , 'HomePreferences',1)
D('HomePreferencesYearSemester'    , 'HomePreferences',3)
D('HomePreferences3ScrollBars'     , 'HomePreferences',4)
D('HomePreferencesDebug'           , 'HomePreferences',9)

D('HomeLogout'                     , 'HomeIdentity',0)
D('HomeLogin'                      , 'HomeIdentity',1)

D('HomeUE'                         , 'HomeColumns',0)
D('HomeStudents'                   , 'HomeColumns',1)
D('HomeActions'                    , 'HomeColumns',2, HomeActions)

D('HomeUEUnsaved'                  , 'HomeUE', 0)
D('HomeUENrAccess'                 , 'HomeUE', 1, HomeUENrAccess)
D('HomeUETeacher'                  , 'HomeUE', 2)
D('HomeUEAcceded'                  , 'HomeUE', 3)
D('HomeUEBookmarked'               , 'HomeUE', 4, HomeUEBookmarked)
D('HomeUEMasterOf'                 , 'HomeUE', 5, HomeUEMasterOf)

D('HomeUEMenu'                     , [], 0, js="Vertical")
D('HomeUEMenuActions'              , 'HomeUEMenu', 0, js="Horizontal")
D('HomeUEMenuColumns'              , 'HomeUEMenu', 1)

D('HomeUEOpenRO'                   , 'HomeUEMenuActions', 0)
D('HomeUEOpen'                     , 'HomeUEMenuActions', 1)
D('HomeUESignature'                , 'HomeUEMenuActions', 2)
D('HomeUEPrint'                    , 'HomeUEMenuActions', 3)
D('HomeUEUnsemestrialize'          , 'HomeUEMenuActions', 8)
D('HomeUEClose'                    , 'HomeUEMenuActions', 9)

D('HomeStudentStudents'            , 'HomeStudents', 0)
D('HomeStudentTeachers'            , 'HomeStudents', 1)
D('HomeStudentFavorites'           , 'HomeStudents', 2, HomeStudentFavorites)
D('HomeStudentRefered'             , 'HomeStudents', 3, HomeStudentRefered)

D('HomeStudentMenu'                , [], 0, js="Vertical")
D('HomeStudentMenu1'               , 'HomeStudentMenu', 1, js='Horizontal')
D('HomeStudentMenu2'               , 'HomeStudentMenu', 2, js='Horizontal')
D('HomeStudentMenu3'               , 'HomeStudentMenu', 3, js='Horizontal')

D('HomeStudentPicture'             , 'HomeStudentMenu1', 1)
D('HomeStudentMail'                , 'HomeStudentMenu1', 2)

D('HomeStudentBilan'               , 'HomeStudentMenu2', 1)
D('HomeStudentSuivi'               , 'HomeStudentMenu2', 2)
D('HomeStudentGet'                 , 'HomeStudentMenu2', 3)

def home_page(server):
    display.send_headers(server, "home3.css", "home3.js", "initialize_home3")
    server.the_file.write('''
<script id="uesjs"
        onload="setTimeout(display_update_real, 500)"
        onreadystatechange="display_update_real()"
        src="%s/all_ues.js"
    ></script>
    <script>var i_am_a_referent=%d;</script>
    ''' % (configuration.url_files, int(server.ticket.is_a_referent)))
    display.data_to_display(server, "Home")

plugin.Plugin('homepage3', '/{=}', function=home_page, group='staff',
              launch_thread=True, unsafe=False)
