#!/bin/env python3
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

from ..column import TableAttr

class TableRounding(TableAttr):
    name = 'rounding'
    display_table = 1
    default_value = 0 # Compatible with old TOMUSS version
    gui_display = "GUI_select"
    formatter = """
function(value)
{
    var e = document.getElementById('t_table_attr_rounding') ;
    if ( e )
       if ( value == 2 )
            e.style.background = '#F88' ;
       else
            e.style.background = '' ;
    for(var data_col in columns)
    {
        var column = columns[data_col] ;
        column.need_update = true ;
        column_attributes.rounding.check_and_set(column.rounding, column) ;
    }
    return value ;
}"""
    css = """
#menutop #t_table_attr_rounding { width: 50% }
#menutop #t_table_attr_rounding OPTION { background: #DDD }
"""

    def encode(self, value):
        return int(value)
    def check(self, value):
        try:
            value = int(value)
        except ValueError:
            return self.check_error(value)
        if 0 <= value <= 2:
            return
        return self.check_error(value)
