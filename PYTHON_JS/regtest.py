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
Utillities for the regression tests
"""

abi_short = abi = "ABI"
abj_short = abj = "ABJ"
tnr_short = tnr = "TNR"
ppn_short = ppn = "PPN"
pre_short = pre = "PRE"

class Table:
    def __init__(self):
        self.rounding = 0

class Column:
    def __init__(self, args={}):
        # self.__dict__ is not translated into javascript
        # ** is not translated into javascript
        if not args:
            args = {}
        self.average_columns = args.get("average_columns", [])
        self.real_weight     = args.get("real_weight", 1)
        self.real_weight_add = args.get("real_weight_add", True)
        self.min             = args.get("min", 0)
        self.max             = args.get("max", 20)
        self.mean_of         = args.get("mean_of", 0)
        self.best_of         = args.get("best_of", 0)
        self.round_by        = args.get("round_by", 0)
        self.empty_is        = args.get("empty_is", "")
        self.test_filter     = args.get("test_filter", "")
        self.comment         = args.get("comment", "")
        self.computed        = args.get("computed", 0)
        self.abj_is          = args.get("abj_is", 0)
        if len(columns) != 0:
            self.table = columns[0].table

    def nmbr_filter(self, cell):
        return Filter(self.test_filter, "","").evaluate(cell)
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
        print('='*77)
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
