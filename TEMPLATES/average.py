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

import data
import re

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
    nr = 0
    for title in column.depends_on():
        col = table.columns.from_title(title)
        value = line[col.data_col].value
        nr += 1
        if value == 'ABINJ':
            abinj += 1
            values.append((0, col.weight))
        elif value == 'ABJUS':
            abjus += 1
        elif value == 'PPNOT':
            ppnot += 1
        else:
            v_min, v_max = min_max(col.minmax)
            try:
                values.append(((float(value)-v_min)/(v_max-v_min), col.weight))
            except ValueError:
                return 'NaN'

    if abinj == nr:
        return 'ABINJ'
    if abjus == nr:
        return 'ABJUS'

    values.sort()
    worst, best = best_worst_of(column.comment)

    if best + worst > len(values):
        return 'NaN'

    if best:
        values = values[worst:-best]
    else:
        values = values[worst:]

    if len(values) == 0:
        return 'PPNOT'

    s = 0
    w = 0
    bonus = 0
    for value, weight in values:
        float_weight = float(weight)
        if weight[0] in '+-':
            bonus += value * float_weight
        else:
            s += value * float_weight
            w += float_weight

    if w == 0:
        return 'NaN'
            
    v_min, v_max = min_max(column.minmax)
    return v_min + (s / w) * (v_max - v_min) + bonus



possible = (5, 'ABINJ', 'ABJUS', 'PPNOT')

def values_next(i):
    if i == 0:
        yield []
        return
    for j in possible:
        for k in values_next(i-1):
            k.append(j)
            yield k

def create(table):
    p = table.new_page('' ,data.rw_user, '', '')

    attrs = (
        {'title': 'A', 'type': 'Note', 'minmax': '[0;10]'},
        {'title': 'B', 'type': 'Note', 'minmax': '[0;20]', "weight": 2},
        {'title': 'C', 'type': 'Note', 'minmax': '[0;20]', "weight": 3},
        {'title': 'Moy', 'type': 'Moy', 'columns': 'A B C'},
        {'title': 'Moy_OK', 'type': 'Text'},
        {'title': 'Moy-min', 'type': 'Moy', 'columns': 'A B C',
         'comment': ']1,0['},
        {'title': 'Moy-min_OK', 'type': 'Text'},
        {'title': 'Moy-max', 'type': 'Moy', 'columns': 'A B C',
         'comment': ']0,1['},
        {'title': 'Moy-max_OK', 'type': 'Text'},
        {'title': 'Moy-minmax', 'type': 'Moy', 'columns': 'A B C',
         'comment': ']1,1['},
        {'title': 'Moy-minmax_OK', 'type': 'Text'},
        {'title': 'MoyMoy', 'type': 'Moy',
         'columns': 'Moy Moy-min Moy-max Moy-minmax'},
        {'title': 'MoyMoy_OK', 'type': 'Text'},
        )

    for i, column in enumerate(attrs):
        for attr, value in column.items():
            table.column_attr(p, str(i), attr, str(value))

    table.table_attr(p, 'default_sort_column', [0,1])
    table.table_attr(p, 'default_nr_columns', 13)

    for i, values in enumerate(values_next(3)):
        i = str(i)
        table.cell_change(p, '0', i, values[0])
        table.cell_change(p, '1', i, values[1])
        table.cell_change(p, '2', i, values[2])
        for c in (4, 6, 8, 10, 12):
            v = compute_one(table, table.lines[i], table.columns[c-1])
            v = str(v)
            table.cell_change(p, str(c), i, v)
            table.lines[i][c-1] = table.lines[i][c-1].set_value(v)
    
