#!/bin/env python
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

from column import ColumnAttr

class ColumnLocked(ColumnAttr):
    name = 'locked'
    check_and_set = "function(value, column) { return Number(value) ;}"
    default_value = 0
    
    def encode(self, value):
        return int(value)
    def decode(self, value):
        return str(value)

    def check(self, value):
        try:
            int(value)
        except ValueError:
            return "Le nombre de répétitions doit être un nombre entier"
    def encode(self, value):
        try:
            return int(value)
        except ValueError:
            return 0
    def check(self, value):
        if value in (0, 1, '0', '1'):
            return ''
        return "Valeur invalide pour 'locked' :" + repr(value)

    gui_display = "GUI_select"
    css = '#menutop DIV.tabs #t_column_locked { width: auto }'
