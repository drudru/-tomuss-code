#!/bin/env python3
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2017 Thierry EXCOFFIER, Universite Claude Bernard
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
#    Contact: Thierry.EXCOFFIER@univ-lyon1.fr

import os
import re
import html
from .. import plugin
from .. import files
from .. import document
from .. import utilities
from .. import configuration

f = files.add('PLUGINS', 'create_table.js')
files.files['lib.js'].append('create_table.py', f)

def create_table(server):
    """Return the column definition of the table"""
    year, semester, code, title, private, visible = server.the_path
    year = utilities.safe(year)
    semester = utilities.safe(semester)
    code = utilities.safe(code)
    cleanup = " \n\r,;"
    private = private.strip(cleanup)
    server.the_file.write('<h2>' + year + "/" + semester + "/" + code
                          + " : " + html.escape(title) + '</h2>')
    if private:
        private = re.split("[" + cleanup + "]+", private)
        for login in tuple(private):
            if not configuration.is_member_of(login, 'staff'):
                server.the_file.write(server._("ALERT_bad_login") + login
                                      + '<br>')
                private.remove(login)

    if os.path.exists(document.table_filename(year, semester, code)):
        message =  server._("MSG_create_table_not_done")
    else:
        message = server._("MSG_create_table_done")
        t, p = document.table(year, semester, code, ticket=server.ticket)
        try:
            t.lock()
            if not t.masters:
                t.table_attr(p, 'masters', [server.ticket.user_name])
            if not t.table_title:
                t.table_attr(p, 'table_title', title)
            t.table_attr(p, 'official_ue', int(visible))
            if private:
                t.table_attr(p, 'teachers', private)
        finally:
            t.unlock()
    
    server.the_file.write(
        '<p>' + message
        + '<a href="' + configuration.server_url + '/=' + server.ticket.ticket
        + '/' + year + "/" + semester + "/" + code + '" target="_blank">'
        + configuration.server_url + '/' + year + "/" + semester + "/" + code
        + '</a>')
    

plugin.Plugin('create_table', '/create_table/{*}',
              function=create_table, group='staff',
              link=plugin.Link(html_class="verysafe",
                               where="root_rw",
                               url="javascript:create_table()"
                               ),
              )
