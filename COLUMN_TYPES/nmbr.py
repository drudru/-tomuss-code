#!/bin/env python3
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2008,2010 Thierry EXCOFFIER, Universite Claude Bernard
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

from . import moy
from . import text

class Nmbr(moy.Moy):
    human_priority = -5
    cell_compute = 'compute_nmbr'
    attributes_visible = ('test_filter', 'columns', 'weight', 'minmax', 'rounding')
    type_change = """
function(column)
{
 column_attr_set(column, 'minmax', '[0;' +
                 Math.max(1, column.average_columns.length) + '] ');
 column_attr_set(column, 'rounding', 1) ;
}"""
