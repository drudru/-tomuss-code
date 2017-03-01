#!/usr/bin/python3
# -*- coding: utf-8 -*-
# TOMUSS: The Online Multi User Simple Spreadsheet
# Copyright (C) 2015 Thierry EXCOFFIER, Universite Claude Bernard
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

def compute_product(data_col, line):
    column = columns[data_col]
    if len(column.average_columns) == 0:
        return ''

    nr_abj = 0
    nr_ppn = 0
    nr_abi = 0
    product = 1
    for data_column in column.average_columns:
        origin = columns[data_column]
        if str(origin.real_weight) != "1":
            return _('ERROR_all_weight_equals_to_1')
        value = line[data_column].get_value(origin)
        if str(value) == '': # str() to turn around JS cast
            return nan # Empty cell
        if value in (abj, abj_short):
            nr_abj += 1
        elif value in (ppn, ppn_short):
            nr_ppn += 1
        elif value in (pre, pre_short):
            continue
        elif value in (tnr, tnr_short, abi, abi_short):
            nr_abi += 1
            product = 0
        else:
            product *= to_float_or_nan(value)
    if nr_abj == 0 and nr_abi != len(column.average_columns) and nr_ppn == 0:
        return product
    if nr_abi == len(column.average_columns):
        return abi
    if nr_abj == len(column.average_columns):
        return abj
    if nr_ppn == len(column.average_columns):
        return ppn
    return nan
