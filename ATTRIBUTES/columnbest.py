#!/bin/env python3
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2012 Thierry EXCOFFIER, Universite Claude Bernard
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

from ..column import ColumnAttr

class ColumnBest(ColumnAttr):
    default_value = '0'
    name = 'best'
    display_table = 1
    check_and_set = 'set_best'
    always_visible = 1
    priority = 1 # Must be computed AFTER 'comment' attribute (historical)
    css = '#menutop DIV.tabs #t_column_best { width: 10% ; }'

    def check(self, value):
        try:
            int(value)
        except ValueError:
            return '_("ALERT_bad_weight")'
