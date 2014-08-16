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

columns = []

class Column:
    def __init__(self,
                 average_columns = (),
                 real_weight = 1,
                 real_weight_add = True,
                 min = 0,
                 max = 20,
                 mean_of = 0,
                 best_of = 0,
                 round_by = 0,
                 empty_is = '',
                 ):
        # self.__dict__ is not translated into javascript
        # ** is not translated into javascript
        self.average_columns = average_columns
        self.real_weight = real_weight
        self.real_weight_add = real_weight_add
        self.min = min
        self.max = max
        self.mean_of = mean_of
        self.best_of = best_of
        self.round_by = round_by
        self.empty_is = empty_is

class Cell:
    def __init__(self, x, expected=0):
        self.value = x
        self.expected = expected
    def set_value(self, x):
        self.value = x
        return self
    def __repr__(self):
        return repr(self.value)

def strip0(txt):
    txt = str(txt)
    if txt in ('0', '0.', '0.0'):
        return '0'
    if len(txt) > 14:
        txt = txt[:-1] # Last digit is garbage
    while txt and txt[-1] in '0.':
        txt = txt[:-1]
    return txt

def C(expected):
    return Cell(-1, expected)
    
