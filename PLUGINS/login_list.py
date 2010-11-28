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

import plugin
import inscrits
import configuration
import utilities

def login_list(server):
    """Retrieve information about any person, not only teachers"""
    a = inscrits.firstname_or_surname_to_logins(
        server.the_path[0],
        attributes=[configuration.attr_login,
                    configuration.attr_surname,
                    configuration.attr_firstname,
                    configuration.attr_mail,
                    ]
        )

    if a:
        s = []
        for login, surname, firstname, mail  in a:
            login = login.lower().encode('utf8')
            firstname = firstname.title().encode('utf8')
            surname = surname.upper().encode('utf8')
            mail = mail.encode('utf8')
            s.append('[' + utilities.js(login)
                     + ',' + utilities.js(firstname)
                     + ',' + utilities.js(surname)
                     + ',' + utilities.js(mail)
                     + ']')
    else:
        s = []
    s = 'full_login_list(' + utilities.js(server.the_path[0]) + ',[' \
        + ',\n'.join(s) + ']);'
    server.the_file.write(s)
    server.the_file.close()

plugin.Plugin('login_list', '/login_list/{*}',
              function=login_list,
              teacher=True,
              mimetype = 'application/x-javascript',
              launch_thread=True,
              )
