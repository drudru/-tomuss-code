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

def compute_weighted_percent_(data_col, line, root_col):
    column = columns[data_col]
    if not column.is_computed():
        if root_col.nmbr_filter(line[data_col]):
            return 1.
        else:
            return 0.
    sum = 0
    sum_weight = 0
    for dc in column.average_columns:
        col = columns[dc]
    
        if not col.real_weight_add:
            continue

        weight = col.real_weight
        sum += weight * compute_weighted_percent_(dc, line, root_col)
        sum_weight += weight

    if sum_weight == 0:
        return 0.
    return sum / sum_weight

def compute_weighted_percent(data_col, line):
    column = columns[data_col]

    if len(column.average_columns) != 1:
      return ''
    v = (column.min + (column.max - column.min) *
         compute_weighted_percent_(column.average_columns[0],
                                   line, column)
         )

    if column.round_by:
        v = rint(v / column.round_by) * column.round_by

    return v

