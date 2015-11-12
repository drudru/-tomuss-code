#!/usr/bin/python3
# -*- coding: utf-8 -*-
# TOMUSS: The Online Multi User Simple Spreadsheet
# Copyright (C) 2014 Thierry EXCOFFIER, Universite Claude Bernard
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Contact: Thierry.EXCOFFIER@univ-lyon1.fr

"""
"""

def compute_max_real(data_col, line):
    column = columns[data_col]
    the_max = -1e10
    nr_abi = 0
    for data_column in column.average_columns:
        val = line[data_column].value
        col =  columns[data_column]
        if str(val) == '':
            val = col.empty_is
        if str(val) == '':
            return nan
        value = to_float_or_nan(val)
        if isNaN(value):
            if val in (abi, tnr):
                nr_abi += 1
                value = col.min
            elif val in (abj, ppn):
                continue
            else:
                return nan
        else:
            value = (value - col.min) / col.max
        if value > the_max:
            the_max = value

    if the_max > -1e10:
        if nr_abi == len(column.average_columns):
            return abi
        else:
            return the_max * (column.max - column.min) + column.min
    return nan
