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

from . import note

class Moy(note.Note):
    human_priority = -8
    cell_compute = 'compute_average'
    cell_is_modifiable = 0
    type_type = 'computed'
    attributes_visible = ('minmax', 'columns', 'weight', 'best', 'worst',
                          'rounding', 'abj_is', 'abi_is')
    type_change = """function(column)
                    {column_attr_set(column, 'rounding', rounding_avg);}"""
    def cell_indicator(self, column, value, cell, lines):
        return '', None
