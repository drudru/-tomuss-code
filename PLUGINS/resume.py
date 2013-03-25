#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2009-2011 Thierry EXCOFFIER, Universite Claude Bernard
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
from .. import document
from .. import column
from .. import plugins
from ..TEMPLATES import _ucbl_
from ..cell import CellValue, Line
from .. import configuration

class Stat(object):
    def __init__(self, login):
        self.login = login
        self.tables = {}

def resume(server):
    """Resume the number of cells used in the given tables"""
    logins = {}
    columns = [
        column.Column('c0', '', freezed='F', position=0,
                      title=server._('COL_TITLE_ID')),
        column.Column('c1', '', freezed='F', position=1,
                      title=server._('COL_TITLE_firstname')),
        column.Column('c2', '', freezed='F', position=2,
                      title=server._('COL_TITLE_surname')),
        ]
    i = 4
    for table in server.the_path:
        t = document.table(server.year, server.semester, table, None, None,
                           create=False, ro=True)
        if t == None:
            continue
        columns.append(
            column.Column('c%d' % i, '',
                          position=i,
                          title=table,
                          weight='+1',
                          type="Note",
                          test='[0;NaN]',
                          empty_is="0",
                          rounding='1',
                          comment=server._('COL_COMMENT_nb_cells_entered'),
                          ))
        i += 1
        for line in t.lines.values():
            login = line[0].value
            if login == '':
                continue
            if login not in logins:
                logins[login] = s = Stat(login)
                s.surname = line[1].value
                s.name = line[2].value
            logins[login].tables[table] = (
                len([cell for cell in line[6:]
                     if cell.value != ''
                     and cell.value != configuration.abi]),
                )
    columns.append(
        column.Column('c3', '', position=2,
                      title=server._('COL_TITLE_TOTAL'),
                      type="Moy",                      
                      weight='1',
                      rounding='1',
                      columns=' '.join([c.title for c in columns[3:]]),
                      minmax='[0;NaN]',
                      )
        )
    # XXX Really not nice.
    # Why the 'type' attribute does not work like the others ?
    columns[-1].type = plugins.types['Moy']

    lines = []
    for stat in logins.values():
        line = [CellValue(stat.login),
                CellValue(stat.surname),
                CellValue(stat.name)]
        for col in columns[3:]:
            line.append(CellValue(stat.tables.get(col.title,('',))[0]))
            
        # line.append(CellEmpty())
        lines.append(Line(line))

    document.virtual_table(server, columns, lines,
                           table_attrs={
            'default_sort_column': 2,
            }, js=_ucbl_.update_student_information)
    
plugin.Plugin('resume', '/resume/{*}',
              function=resume, group='staff',
              launch_thread = True)

