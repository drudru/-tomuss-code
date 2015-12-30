#!/bin/env python
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
#    Contact: Thierry.EXCOFFIER@univ-lyon1.fr

from ..column import ColumnAttr

class ColumnABJ_is(ColumnAttr):
    default_value = 0
    always_visible = 1
    display_table = 1
    name = 'abj_is'
    check_and_set = "function(value, column) { column.need_update = true ; return Number(value) ;}"

    def encode(self, value):
        try:
            return int(value)
        except ValueError:
            return 0
    def check(self, value):
        if value in (0, 1, 2, 3, '0', '1', '2', '3'):
            return ''
        return self.check_error(value)

    gui_display = "GUI_select"
    css = '#menutop DIV.tabs #t_column_abj_is { width: auto }'

