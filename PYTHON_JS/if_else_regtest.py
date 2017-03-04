#!/usr/bin/python3
# -*- coding: utf-8 -*-
# TOMUSS: The Online Multi User Simple Spreadsheet
# Copyright (C) 2017 Thierry EXCOFFIER, Universite Claude Bernard
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

def if_else_regtest():
    line = [Cell(5, "john"), Cell(6, 'doe'), Cell(7), Cell(8), CE(0), CE(0)]
    for filter, result1, result2 in [
            ['[A]=5', 7, 7],
            ['[A]=6', 8, 4],
            ['[A]<[B]', 7, 7],
            ['[A]>[B]', 8, 4],
            ['>3', 7, 7],
            ['<10', 7, 7],
            ['<3', 8, 4],
            ]:
        columns_set([Column({"title": "A"}),
                     Column({"title": "B"}),
                     Column(),
                     Column(),
                     Column({"average_columns":[2, 3],
                             'test_if':filter}),
                     Column({"average_columns":[2],
                             'test_if':filter}),
               ])
        line[4].value = 9
        line[4].expected = result1
        check_result(line, 4, compute_if_else)
        line[5].value = 4
        line[5].expected = result2
        check_result(line, 5, compute_if_else)
        
    print('if_else regtest are fine')

if_else_regtest()
