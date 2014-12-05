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

def weighted_percent_regtest():
    columns_set([Column({"real_weight":3}), Column(),
                 Column({"average_columns":[0, 1], "computed":1}),
                 Column(), Column(),
                 Column({"average_columns":[3, 4], "computed":1, "real_weight":4}),
                 Column({"average_columns":[2, 5], "computed":1}),
                 Column({"test_filter":"=" + abj,"average_columns":[6],
                      "min":0, "max":100})
           ])
    for line in [
            [Cell(1),Cell(1),Cell(0),Cell(1),Cell(1),Cell(0),Cell(0),CE(0)],
            [Cell(1),Cell(1),Cell(0),Cell(1),Cell('A'),Cell(0),Cell(0),CE(0)],
            [Cell(1),Cell(1),Cell(0),Cell(1),Cell(abj),Cell(0),Cell(0),CE(40)],
            [Cell(1),Cell(1),Cell(0),Cell(abj),Cell(1),Cell(0),Cell(0),CE(40)],
            [Cell(1),Cell(1),Cell(0),Cell(abj),Cell(abj),Cell(0),Cell(0),CE(80)],
            [Cell(1),Cell(abj),Cell(0),Cell(1),Cell(1),Cell(0),Cell(0),CE(5)],
            [Cell(abj),Cell(1),Cell(0),Cell(1),Cell(1),Cell(0),Cell(0),CE(15)],
            [Cell(abj),Cell(abj),Cell(0),Cell(1),Cell(1),Cell(0),Cell(0),CE(20)],
            [Cell(abj),Cell(abj),Cell(0),Cell(abj),Cell(abj),Cell(0),Cell(0),CE(100)],
            [Cell(abj),Cell(abj),Cell(abj),Cell(abj),Cell(abj),Cell(abj),Cell(abj),CE(100)],
    ]:
        check_result(line, 7, compute_weighted_percent)
        
    print('Weight_percent regtest are fine')

weighted_percent_regtest()
