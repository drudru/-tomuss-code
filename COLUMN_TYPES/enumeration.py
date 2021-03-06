#!/bin/env python3
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2011-2013 Thierry EXCOFFIER, Universite Claude Bernard
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

from . import text
import collections

class Enumeration(text.Text):
    tip_cell = "TIP_cell_Enumeration"
    cell_test = 'test_enumeration'
    cell_completions = 'completions_enumeration'
    ondoubleclick = 'toggle_enumeration'
    attributes_visible = ('enumeration', 'weight', 'repetition', 'url_import',
                          "groupcolumn")
    formatte_suivi = "enumeration_format_suivi"

    def stat(self, column, value, cell, lines):
        v = column.enumeration.split(' ')
        if column.repetition:
            nb = collections.defaultdict(int)
            data_col = column.data_col
            if column.repetition > 0:
                verify_lines = list(column.table.lines.values())
            else:
                verify_lines = lines
            for line in verify_lines:
                nb[line[data_col].value] += 1
            nb[value] -= 1
            v = [(x, abs(column.repetition) - nb[x])
                 for x in v
                 if nb[x] < abs(column.repetition)
                 ]
        v.insert(0, '')
        return {'enumeration': v}

