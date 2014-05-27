#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2009 Thierry EXCOFFIER, Universite Claude Bernard
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

import re
from .. import data
from .. import configuration

def best_worst_of(txt):
    values = re.sub(r".*]([0-9]*),([0-9]*)\[.*", r'][ \1 \2', txt).split(" ")
    if len(values) != 3 or values[0] != '][':
        return (0, 0)
    return (int(values[1]), int(values[2]))

def min_max(txt):
    return [float(v) for v in txt.strip('[]').split(';')]

def compute_one(table, line, column):
    abinj = 0
    abjus = 0
    ppnot = 0
    values = []
    bonus = 0
    for title in column.depends_on():
        col = table.columns.from_title(title)
        value = line[col.data_col].value
        if value == configuration.abi:
            abinj += 1
            values.append((0, float(col.weight)))
        elif value == configuration.abj:
            abjus += 1
        elif value == configuration.ppn:
            ppnot += 1
        else:
            v_min, v_max = min_max(col.minmax)
            try:
                if col.weight == '?':
                    # For a future functionnality?
                    weight = float(line[col.data_col].comment)
                else:
                    weight = float(col.weight)
                if col.weight[0] in "+-":
                    bonus += weight * float(value)
                else:
                    values.append(((float(value)-v_min)/(v_max-v_min), weight))
            except ValueError:
                return 'NaN', ''

    nr = abjus + ppnot + len(values)
    if abjus == nr:
        return configuration.abj, ''

    if values:
        full_weight = sum(zip(*values)[1])
    else:
        full_weight = 0
    if abinj == nr:
        return configuration.abi, full_weight

    values.sort()
    worst, best = best_worst_of(column.comment)

    if best + worst > len(values):
        return 'NaN', ''

    if best:
        values = values[worst:-best]
    else:
        values = values[worst:]

    if len(values) == 0:
        return configuration.ppn, full_weight

    s = 0
    w = 0
    for value, weight in values:
        s += value * weight
        w += weight

    if w == 0:
        return 'NaN', ''
            
    v_min, v_max = min_max(column.minmax)
    return v_min + (s / w) * (v_max - v_min) + bonus, full_weight



possible = (5, configuration.abi, configuration.abj, configuration.ppn)

def values_next(i):
    if i == 0:
        yield [0]
        yield [1]
        return
    for j in possible:
        for k in values_next(i-1):
            k.append(j)
            yield k

def create(table):
    p = table.get_rw_page()

    attrs = (
        {'title': 'A', 'type': 'Note', 'minmax': '[0;10]'},
        {'title': 'B', 'type': 'Note', 'minmax': '[0;20]', "weight": 2},
        {'title': 'C', 'type': 'Note', 'minmax': '[0;20]', "weight": 3},
        {'title': 'D', 'type': 'Note', 'minmax': '[0;20]', "weight": '+2'},
        {'title': 'Moy', 'type': 'Moy', 'columns': 'A B C D', 'weight': '1'},
        {'title': 'Moy_OK', 'type': 'Text'},
        {'title': 'Moy-min', 'type': 'Moy', 'columns': 'A B C',
         'comment': ']1,0[', 'weight': '1'},
        {'title': 'Moy-min_OK', 'type': 'Text'},
        {'title': 'Moy-max', 'type': 'Moy', 'columns': 'A B C',
         'comment': ']0,1[', 'weight': '1'},
        {'title': 'Moy-max_OK', 'type': 'Text'},
        {'title': 'Moy-minmax', 'type': 'Moy', 'columns': 'A B C',
         'comment': ']1,1[', 'weight': '1'},
        {'title': 'Moy-minmax_OK', 'type': 'Text'},
        {'title': 'MoyMoy', 'type': 'Moy',
         'columns': 'Moy Moy-min Moy-max Moy-minmax'},
        {'title': 'MoyMoy_OK', 'type': 'Text'},
        )

    for i, column in enumerate(attrs):
        for attr, value in column.items():
            table.column_attr(p, str(i), attr, str(value))

    table.table_attr(p, 'default_sort_column', [0,1])
    table.table_attr(p, 'default_nr_columns', 14)

    for i, values in enumerate(values_next(3)):
        i = str(i)
        table.cell_change(p, '0', i, values[1])
        table.cell_change(p, '1', i, values[2])
        table.cell_change(p, '2', i, values[3])
        table.cell_change(p, '3', i, values[0])
        for c in (5, 7, 9, 11, 13):
            v, w = compute_one(table, table.lines[i], table.columns[c-1])
            v = str(v)
            table.cell_change(p, str(c), i, v)
            table.comment_change(p, str(c), i, str(w))
            table.lines[i][c-1] = table.lines[i][c-1].set_value(v)
    
