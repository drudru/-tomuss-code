#!/bin/env python3
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2017 Thierry EXCOFFIER, Universite Claude Bernard
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

class ColumnTestIf(ColumnAttr):
    default_value = ''
    display_table = 1
    name = 'test_if'
    check_and_set = '''
function(value, column)
{
  column.need_update = true ;
  column.if_filter = compile_filter_generic(value, column, true) ;
  column.test_if_error = column.if_filter.errors ;
  return value ;
}'''
    css = """
    #menutop #t_column_test_if { width: 4em ; }
    #menutop DIV.tabs #t_column_test_if { width: 40% ; }
    """

