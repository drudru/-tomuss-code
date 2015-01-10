#!/usr/bin/env python
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

from .. import plugins
from .. import configuration

def update_column(table):
    for t in plugins.types_ordered():
        if table.columns.from_id(t.name) is None:
            table.column_attr(table.pages[1], t.name, 'title', t.name)
            table.column_attr(table.pages[1], t.name, 'type', t.name)
            table.column_attr(table.pages[1], t.name, 'columns', '')
    table.table_attr(table.pages[0], 'default_nr_columns', len(plugins.types))
    for i, v in enumerate(('1','a','31/1/1998','é',
                           '&~!@#$%^&*()_+|-=][{}":;,.<>')):
        i = str(i)
        if i in table.lines:
            continue
        for t in plugins.types_ordered():
            table.cell_change(table.pages[1], t.name, i,
                              v, '')
        
def create(table):
    if table.year != 0 or table.semester != 'Test':
        raise ValueError('Not allowed')
    p = table.get_ro_page()
    table.table_attr(p, 'masters', list(configuration.root))
    table.get_rw_page()
    update_column(table)

def check(table):
    table.lock()
    update_column(table)
    table.unlock()
