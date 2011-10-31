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

from column import ColumnAttr

class ColumnTestFilter(ColumnAttr):
    default_value = '!ABINJ'
    display_table = 1
    name = 'test_filter'
    check_and_set = '''
function(value, column)
{
  column.need_update = true ;
  column.nmbr_filter = compile_filter_generic(value) ;
  return value ;
}'''
    tip = """<b>Filtre indiquant les cellules à compter</b><br>
    Exemples pour compter les cellules :<ul>
    <li> <b>ABI</b> : commençant par ABI.
    <li> <b>!=ABINJ</b> : valeur différente de ABINJ.
    <li> <b>=</b> compte les cellules vides.
    <li> <b>&lt;8</b> compte les nombres plus petits que 8.
    </ul>
    Pour plus d'information, regardez l'aide sur les filtres."""
    css = """
    #menutop #t_column_test_filter { width: 4em ; }
    #menutop DIV.tabs #t_column_test_filter { width: 65% ; }
    """

