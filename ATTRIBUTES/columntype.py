#!/bin/env python3
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2008-2012 Thierry EXCOFFIER, Universite Claude Bernard
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
from .. import plugins

class ColumnType(ColumnAttr):
    name = 'type'
    priority = -1 # because 'real_type' must be computed before
    update_headers = 1
    display_table = 1
    default_value = 'Note'
    check_and_set = 'set_type'
    gui_display = 'GUI_type'
    action = 'popup_type_chooser'
    def encode(self, value):
        return plugins.types[value]
    def decode(self, value):
        return value.name
    css = """
DIV.tabs #t_column_type { min-width: 10em; font-weight: bold }
.type_chooser_div { border: 3px solid black }
.type_chooser_div TABLE TR { vertical-align:top }
.type_chooser_div TABLE TD { white-space: nowrap;}
.type_chooser_div TABLE TH { font-weight: bold }
DIV.type_chooser_div.import_export TABLE { width: 10% }
DIV.type_chooser_div.import_export TABLE TD { padding: 4px }
DIV.type_chooser_div.import_export TABLE { margin-left: auto; margin-right: auto }
"""
