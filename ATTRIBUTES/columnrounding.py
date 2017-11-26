#!/bin/env python3
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2012-2017 Thierry EXCOFFIER, Universite Claude Bernard
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

class ColumnRounding(ColumnAttr):
    default_value = ''
    name = 'rounding'
    display_table = 1
    check_and_set = 'set_rounding'
    always_visible = 1
    priority = 1 # Must be computed AFTER 'comment' attribute (historical)
    formatter = '''function(column, value)
     {
      var e = document.getElementById('t_column_rounding') ;
      if ( e )
        e.style.background = (column.type == 'Moy' && value > rounding_avg)
                             ? '#F88' : '' ;
      return value ;
     }'''

    def check(self, value):
        if value == '':
            return
        try:
            float(value)
        except ValueError:
            return '_("ALERT_rounding")'

    css = """
#menutop DIV.tabs INPUT#t_column_rounding { width: 23% ; }
#t_column_rounding.empty {
  background-image: url('rounding.png');
}

"""
