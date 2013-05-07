#!/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2008-2011 Thierry EXCOFFIER, Universite Claude Bernard
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

class ColumnTitle(ColumnAttr):
    name = 'title'
    update_table_headers = 1
    # System tables may contains spaces
    # def check(self, value):
    #    if ' ' in value:
    #        return 'Espace interdit dans les titres de colonnes'
    empty = 'function(column, value) { return value.substr(0,default_title.length) == default_title && !isNaN(value.substr(default_title.length))  ; }'
    check_and_set = 'set_title'
    css = '''
#t_column_title.empty {
  background-image: url("title.png");
  background-repeat: no-repeat;
  background-position: 2px 2px;
}
#t_column_title { font-weight: bold ; }
'''
