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
Utilities for the regression tests
"""

abi_short = abi = "ABI"
abj_short = abj = "ABJ"
tnr_short = tnr = "TNR"
ppn_short = ppn = "PPN"
pre_short = pre = "PRE"
def or_keyword():
    return "or"
allowed_grades = {'DIS': [ppn, ""]}

class Table:
    def __init__(self):
        self.rounding = 0

def get(args, x, v):
    if x in args:
        return args[x]
    else:
        return v

class Column:
    def __init__(self, args={}):
        # self.__dict__ is not translated into javascript
        # ** is not translated into javascript
        if not args:
            args = {}
        self.average_columns = get(args, "average_columns", [])
        self.real_weight     = get(args, "real_weight", 1)
        self.real_weight_add = get(args, "real_weight_add", True)
        self.min             = get(args, "min", 0)
        self.max             = get(args, "max", 20)
        self.mean_of         = get(args, "mean_of", 0)
        self.best_of         = get(args, "best_of", 0)
        self.round_by        = get(args, "round_by", 0)
        self.empty_is        = get(args, "empty_is", "")
        self.test_filter     = get(args, "test_filter", "")
        self.test_if         = get(args, "test_if", "")
        self.comment         = get(args, "comment", "")
        self.computed        = get(args, "computed", 0)
        self.abj_is          = get(args, "abj_is", 0)
        self.abi_is          = get(args, "abi_is", 0)
        self.title           = get(args, "title", "")
        if len(columns) != 0:
            self.table = columns[0].table

    def nmbr_filter(self, line, cell):
        return Filter(self.test_filter, "", "").evaluate(line, cell)
    def if_filter(self, line, cell):
        return Filter(self.test_if, "", "").evaluate(line, cell)
    def is_computed(self):
        return self.computed

class Cell:
    def __init__(self, x, author="", date="", comment="", history="",
                 expected=0):
        self.value = x
        self.expected = expected
        self.author = author
        self.comment = comment
        self.history = history
        self.date = date
    def set_value(self, x):
        self.value = x
        return self
    def get_value(self, col):
        if str(self.value) == '':
            return col.empty_is
        return self.value
    def __repr__(self):
        return repr(self.value)

if python_mode:
    C = Cell
    os.environ['TZ'] = 'GMT-2'
    time.tzset()

def strip0(txt):
    txt = str(txt)
    if txt in ('0', '0.', '0.0'):
        return '0'
    if len(txt) > 14:
        txt = txt[:-1] # Last digit is garbage
    while txt and txt[-1] in '0.':
        txt = txt[:-1]
    return txt

def CE(expected):
    return Cell(-1, "", "", "", "", expected)

def check_result(line, col, fct):
    line[col] = line[col].set_value(fct(col, line))
    if strip0(line[col].value) != strip0(line[col].expected):
        try:
            if abs(float(line[col].value) - float(line[col].expected)
                   ) < 1e-5:
                return
        except ValueError:
            pass
        print('============================')
        print("Column:", col)
        print(line)
        print('Expected:', line[col].expected)
        print('Computed:', line[col].value)
        regression_test_failed


columns = []

def columns_set(cols):
    while len(columns):
        columns.pop()
    t = Table()
    for c in cols:
        columns.append(c)
        c.table = t
