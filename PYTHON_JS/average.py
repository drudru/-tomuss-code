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

if python_mode:
    rint = round
    isNaN = __import__("math").isnan
    ceil = __import__("math").ceil
else:
    rint = Math.round
    ceil = Math.ceil

def compute_average(data_col, line):
    column = columns[data_col]

    if len(column.average_columns) == 0:
        line[data_col] = line[data_col].set_value('')
        return

    nr_abj = 0
    nr_ppn = 0
    nr_add = 0
    nr_abi = 0
    values = []
    line[data_col] = line[data_col].set_value(nan)

    for data_column in column.average_columns:
        value = line[data_column].value
        origin = columns[data_column]
        if origin.real_weight == 0:
            continue
        if str(value) == '': # str is here to turn arround the JavaScript cast
            value = origin.empty_is
            if str(value) == '':
                return # Empty cell ==> NaN
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
        else:
            try:
                value = to_float(value)
            except:
                return
            if isNaN(value):
                return
            if origin.real_weight_add:
                values.append([
                        (value - origin.min) / (origin.max - origin.min),
                        data_column, ''])
            else:
                if column.mean_of or column.best_of:
                    line[data_col] = line[data_col].set_value('???')
                    return
                values.append([value, data_column, ''])

    values.sort() # XXX
    if column.best_of:
        if len(values) < abs(column.best_of):
            return
        if column.best_of > 0:
            # Keep the 'best_of' best grades (historical functionnality)
            values = values[-column.best_of:]
        else:
            # Remove the 'best_of' best grades
            values = values[:column.best_of]
    if column.mean_of:
        if len(values) < -column.mean_of:
            return
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

    # print "%s abi:%s abj:%s ppn:%s sum:%s weight:%s used:%s add:%s only_add:%s only_abj:%s" % (values, nr_abi, nr_abj, nr_ppn, nr_sum, weight, nr_used, nr_add, only_add, only_abj)
    if weight != 0:
        if nr_abi >= len(column.average_columns) - nr_sum:
            value = abi
        else:
            value = (column.min
                     + sumw * (column.max - column.min) / weight
                     + sum2)
            if column.round_by:
                value = rint(value / column.round_by) * column.round_by
            else:
                value = rint(value * 1000000) / 1000000
    elif nr_sum == len(column.average_columns):
        if nr_abi == nr_sum:
            value = abi
        else:
            value = sum2
    elif only_abj:
        value = abj
    elif nr_ppn + nr_abj == len(column.average_columns) - nr_add:
        value = ppn
    else:
        value = nan
    line[data_col] = line[data_col].set_value(value)


def get_most_recent_date(data_col, line, not_root=False):
    if not not_root:
        if not columns[data_col].is_computed():
            return line[data_col].date
    date = "0"
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
    old_value = line[data_col].value
    compute_function(data_col, line)
    if columns[data_col].cell_is_modifiable():
        return # For COW column type

    line[data_col].author = '*\003'+ line[data_col].author
    if isNaN(to_float_or_nan(line[data_col].value)):
        if get_most_recent_date(data_col, line, True) < line[data_col].date:
            line[data_col].value = old_value
            line[data_col].author = line[data_col].author.replace('*\003','')
