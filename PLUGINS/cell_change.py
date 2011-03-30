#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2008 Thierry EXCOFFIER, Universite Claude Bernard
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
import document

def cell(server):
    """Modify an unique cell in a table.
    For example, the boolean values can be changed by teacher
    in the 'suivi'"""
    # Cell change without page editing.
    table, page = document.table(server.the_year, server.the_semester,
                                 server.the_ue, None, server.ticket,
                                 do_not_unload=1)
    col = server.the_path[0]
    lin = server.the_path[1]
    value = server.the_path[2]
    table.lock()
    try:
        if lin not in table.lines or table.columns.from_id(col) == None:
            r = 'bad.png'
        else:
            try:
                r = table.cell_change(page, col, lin, value)
            except ValueError:
                r = 'bad.png'
    finally:
        table.do_not_unload -= 1 # Protected
        table.unlock()
    if r == 'bad.png':
        server.the_file.write('<body style="background:red">')
    elif r == 'ok.png':
        server.the_file.write('<body style="background:green">')
    else:
        server.the_file.write('<body style="background:#F0F">')


plugin.Plugin('cell', '/{Y}/{S}/{U}/cell/{*}', function=cell, teacher=True)
