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
import sys
import utilities

def cell_change(server):
    col = server.the_path[0]
    lin = server.the_path[1]
    value = server.the_path[2]
    table = document.table(server.the_year, server.the_semester,
                           server.the_ue, create=False)
    column = table.columns.from_id(col)
    if lin not in table.lines or column is None:
        return 'bad.png'
    # Test if the column is modifiable in the 'suivi'
    if not column.is_modifiable(server.ticket.is_a_teacher):
        return 'bad.png'
    # The student can only modify its line
    if (not server.ticket.is_a_teacher
        and table.the_keys()[server.ticket.user_name][0] != lin):
        return 'bad.png'

    table, page = document.table(server.the_year, server.the_semester,
                                 server.the_ue, None, server.ticket,
                                 do_not_unload=1)
    try:
        table.lock()
        try:
                try:
                    return table.cell_change(page, col, lin, value)
                except ValueError:
                    return 'bad.png'
        finally:
            table.unlock()
    finally:
        table.do_not_unload_add(-1)

def cell(server):
    """Modify an unique cell in a table. It is used by the 'suivi' page"""

    r = cell_change(server)

    if r == 'bad.png':
        server.the_file.write(
            '<body style="background:red"><script>alert(%s)</script>' %
            utilities.js(server._("ERROR_value_not_modifiable")))
    elif r == 'ok.png':
        server.the_file.write('<body style="background:green">')
    else:
        server.the_file.write(
            '<body style="background:#F0F"><script>alert(%s)</script>' %
            utilities.js(server._("TIP_violet_square")))


plugin.Plugin('cell', '/{Y}/{S}/{U}/cell/{*}', function=cell,
              priority = -10 # Before student_redirection
              )
