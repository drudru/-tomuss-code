#!/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2010 Thierry EXCOFFIER, Universite Claude Bernard
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

from .. import plugin
from .. import inscrits
from .. import configuration
from .. import utilities

def send(server, values, what):
    server.the_file.write('the_full_login_list('
                          + utilities.js(server.the_path[0])
                          + ',[' + ','.join(values)
                          + '], %s);' % utilities.js(what))
    
def login_list_of(text, base):
    """Retrieve information about any person, not only teachers"""
    a = inscrits.L_slow.firstname_or_surname_to_logins(
        text,
        attributes=[configuration.attr_login,
                    configuration.attr_surname,
                    configuration.attr_firstname,
                    configuration.attr_mail,
                    ],
        base = base
        )

    r = []
    for login, surname, firstname, mail  in a:
        login = login.lower().encode('utf8')
        firstname = firstname.title().encode('utf8')
        surname = surname.upper().encode('utf8')
        mail = mail.encode('utf8')
        r.append('[' + utilities.js(login)
                 + ',' + utilities.js(firstname)
                 + ',' + utilities.js(surname)
                 + ',' + utilities.js(mail)
                 + ']')
    return r

def login_list(server):
    send(server,
         login_list_of(server.the_path[0], configuration.cn_students),
         'student')
    send(server,
         login_list_of(server.the_path[0], configuration.cn_teachers),
         'teacher')

plugin.Plugin('login_list', '/login_list/{*}',
              function=login_list,
              group='staff',
              mimetype = 'application/x-javascript',
              launch_thread=True, unsafe=False,
              priority = -10 # Before student_redirection
              )
