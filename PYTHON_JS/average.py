#!/usr/bin/python3
# -*- coding: utf-8 -*-
# TOMUSS: The Online Multi User Simple Spreadsheet
# Copyright (C) 2014-2015 Thierry EXCOFFIER, Universite Claude Bernard
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
About rounding:

   0: Display down rounding (old behaviour)
      Average are rounded to the nearest if a rounding value is defined
      If no rounding is defined, average value is not rounded.
      On display, values are down rounded.

   1: Compute down rounding (new default recommended behaviour)
      All intermediate values are down rounded

   2: Perfect compute, rounding to the nearest
"""

def compute_average(data_col, line):
    column = columns[data_col]
    if len(column.average_columns) == 0:
        return ''
    if column.best_of or column.mean_of:
        weight = None
        for data_column in column.average_columns:
            origin = columns[data_column]
            if not origin.real_weight_add:
                return _('ERROR_addition_not_allowed')
            if weight is None:
                weight = origin.real_weight
                continue
            if weight != origin.real_weight:
                return _('ERROR_different_not_allowed')
    nr_abj = 0
    nr_ppn = 0
    nr_add = 0
    nr_abi = 0
    values = []
    for data_column in column.average_columns:
        origin = columns[data_column]
        if origin.real_weight == 0:
            continue
        value = line[data_column].get_value(origin)
        if str(value) == '': # str is here to turn arround the JavaScript cast
            return nan # Empty cell
        value = allowed_grades.get(value, [value])[0]
        if not origin.real_weight_add:
            nr_add += 1
        if value in (abj, abj_short):
            nr_abj += 1
        elif value in (ppn, ppn_short):
            nr_ppn += 1
        elif value in (pre, pre_short):
            values.append([1, data_column, ''])
        elif value in (tnr, tnr_short):
            nr_abi += 1
            values.append([0, data_column, abi])
        elif value in (abi, abi_short):
            nr_abi += 1
            values.append([0, data_column, abi])
        elif value == "DEF":
            return "DEF"
        else:
            try:
                value = to_float(value)
            except:
                return nan
            if isNaN(value):
                return nan

            if column.table.rounding == 1:
                if origin.round_by:
                    value = rint(value / origin.round_by,0) * origin.round_by
                else:
                    value = rint(value * 1000000,0) / 1000000

            if origin.real_weight_add:
                values.append([
                        (value - origin.min) / (origin.max - origin.min),
                        data_column, ''])
            else:
                if column.mean_of or column.best_of:
                    return '???'
                values.append([value, data_column, ''])

    if nr_abi and column.abi_is == 1:
        return "DEF"

    if column.abj_is and (nr_abj != 0 or nr_ppn != 0):
        # Replace the ABJ/PPN by the average
        weight = 0
        sumw = 0
        for c in values:
            origin = columns[c[1]]
            value = c[0]
            if origin.real_weight_add:
                w = origin.real_weight
                sumw += w * value
                weight += w
        if weight:
            note = sumw / weight
            for data_column in column.average_columns:
                if ((column.abj_is & 1)
                    and line[data_column].get_value(columns[data_column]) in (abj, abj_short)):
                    values.append([note, data_column, ''])
                    nr_abj = 0
                if ((column.abj_is & 2)
                    and line[data_column].get_value(columns[data_column]) in (ppn, ppn_short)):
                    values.append([note, data_column, ''])
                    nr_ppn = 0
        else:
            if nr_abj == len(column.average_columns):
                return abj
            if nr_ppn == len(column.average_columns):
                return ppn
    values.sort() # XXX
    if column.best_of:
        if len(values) < abs(column.best_of):
            return nan
        if column.best_of > 0:
            # Keep the 'best_of' best grades (historical functionnality)
            values = values[-column.best_of:]
        else:
            # Remove the 'best_of' best grades
            values = values[:column.best_of]
    if column.mean_of:
        if len(values) < -column.mean_of:
            return nan
        values = values[-column.mean_of:]
    weight = 0  # The full weight
    sumw = 0    # Normal weighted average
    sum2 = 0    # An addition to do once the average is computed
    nr_sum = 0
    for c in values:
        origin = columns[c[1]]
        value = c[0]
        if origin.real_weight_add:
            w = origin.real_weight
            sumw += w * value
            weight += w
        else:
            sum2 += origin.real_weight * value
            nr_sum += 1

    nr_used = len(column.average_columns) - abs(column.mean_of) - abs(column.best_of) - nr_add
    only_add = nr_add == len(column.average_columns)
    if nr_abj:
        if only_add:
            only_abj = nr_abj == nr_add
        else:
            only_abj = nr_abj == len(column.average_columns) - nr_add
    else:
        only_abj = False

    # print("%s abi:%s abj:%s ppn:%s sum:%s weight:%s used:%s add:%s only_add:%s only_abj:%s" % (values, nr_abi, nr_abj, nr_ppn, nr_sum, weight, nr_used, nr_add, only_add, only_abj))
    if weight != 0:
        if nr_abi >= len(column.average_columns) - nr_sum:
            return abi
        else:
            sumw += 1e-16 ; # Fix .499999999999999 numbers
            value = (column.min
                     + sumw * (column.max - column.min) / weight
                     + sum2)
            if column.table.rounding <= 1 and column.round_by:
                return rint(value / column.round_by,0) * column.round_by
            else:
                return rint(value * 1000000,0) / 1000000
    elif nr_sum == len(column.average_columns):
        if nr_abi == nr_sum:
            return abi
        else:
            return sum2
    elif only_abj:
        return abj
    elif nr_ppn + nr_abj == len(column.average_columns) - nr_add:
        return ppn
    else:
        return nan

def get_most_recent_date(data_col, line, not_root=False):
    if not not_root:
        if not columns[data_col].is_computed():
            return line[data_col].date
    date = ""
    for data_column in columns[data_col].average_columns:
        d = get_most_recent_date(data_column, line)
        if d > date:
            date = d
    return date

def compute_cell_safe(data_col, line, compute_function):
    """
    If the computed value is not a number and the cell was containing
    a newer value, then the old cell value is restored.
    """
    if line[data_col].comment == 'Fixed!':
        return # To override the computed value
    date = line[data_col].date
    v = compute_function(data_col, line)

    if columns[data_col].cell_is_modifiable():
        if v != line[data_col].value:
            line[data_col] = line[data_col].set_value(v)
            line[data_col].date = ''
            try:
                a = line[columns[data_col].average_columns[0]].author
                if a == '*':
                    a = '?' # COW on an average must be modifiable
            except:
                a = '?'
            line[data_col].author = a
        return # For COW column type
    if isNaN(to_float_or_nan(v)):
        if get_most_recent_date(data_col, line, True) >= line[data_col].date:
            line[data_col] = line[data_col].set_value(v)
            line[data_col].date = date
            line[data_col].author = '?'
    else:
        line[data_col] = line[data_col].set_value(v)
        line[data_col].date = date
        line[data_col].author = '*'
