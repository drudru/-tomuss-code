#!/usr/bin/env python3
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

import json
import cgi
from .. import plugin
from .. import document
from .. import ticket
from .. import files
from . import suivi_student

files.add("PLUGINS", "public.js")

def public(server, login=False):
    t = document.table(server.the_year, server.the_semester, server.the_ue,
                       create=False)
    if not t:
        return
    to_display = []
    for col in t.columns:
        if col.visibility == 3:
            to_display.append(col)
        elif col.visibility == 4 and login:
            to_display.append(col)
    if not to_display:
        return
    if not login:
        server.ticket = ticket.Anonymous()
    suivi_student.suivi_headers(server, is_student=True)
    title = "{}/{}/{} {}".format(server.the_year, server.the_semester,
                                 server.the_ue, t.table_title)
    title = cgi.escape(title)
    server.the_file.write('<title>' + title + '</title>'
                          + '<h1>' + title + '</h1>'
                          + '<p>' + cgi.escape(t.comment)
                          + '<p>')
    cols = []
    for col in to_display:
        col = col.js(hide=1, python=True)
        if True or not login:
            col.pop("modifiable", None) # Never modifiable on a public page
        cols.append(col)
    server.the_file.write('<div id="content"></div><script><!--\n'
                          + "var columns = "
                          + json.dumps(cols)
                          + ';\nvar lines = '
                          )
    d = {}
    for line_id, line in t.lines.items():
        d[line_id] = [line[col.data_col].json()[:4] # Hide history
                      for col in to_display]
    server.the_file.write(json.dumps(d))
    table_attr = {'ue': server.the_ue, 'year': server.the_year,
                  'semester': server.the_semester, "modifiable": int(login)
                  }
    server.the_file.write(";\nvar table_attr = "
                          + json.dumps(table_attr) + ";\n"
                          + str(files.files["public.js"])
                          + "\n--></script>")

plugin.Plugin('public', '/public/{Y}/{S}/{U}', function=public,
              launch_thread=True, authenticated=False
              )

plugin.Plugin('public_login', '/public_login/{Y}/{S}/{U}',
              function=lambda server: public(server, login=True),
              launch_thread=True, unsafe=False
              )
