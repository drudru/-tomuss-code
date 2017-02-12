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

def average_regtest():
    for infos in [
            [[(20*(5/6.), 6), (20*(9.75/14.), 14), (ppn,1), (ppn,1)],15.,0.5],
            [[(11.5, 0.5), (0, 0.5), (0, 1), (1, 1)], 2.5, 0.5],
            [[(9, 15), (16.5, 15), (13, 15), (12.5, 15), (11.5, 20), (5, 20)],
              10.9, 0.1],
            [[(16, 6), (12, 6), (9.5, 3), (10, 3), (12, 3), (11, 3), (7, 8),
              (4, 8)], 9.588, 0.001],
            [[(16.5, 1.25), ("", 1.25)], nan, 0.01],
            [[("", 1.25), (16.5, 1.25)], nan, 0.01],
            ]:
        value_and_weights, result, rounding = infos
        columns_set([Column({'real_weight':value_weight[1]})
                   for value_weight in value_and_weights
                   ])
        columns.append(Column({'average_columns':range(len(value_and_weights)),
                               'round_by': rounding}))
        line = [Cell(value_weight[0])
                for value_weight in value_and_weights
            ]
        line.append(CE(result))
        columns[0].table.rounding = 0
        check_result(line, len(value_and_weights), compute_average)
        columns[0].table.rounding = 1
        if infos[-2] == 15:
            line[-1] = CE(14.5)
        check_result(line, len(value_and_weights), compute_average)
    columns_set([Column(), Column(), Column(),
                 Column({"average_columns":[0, 1, 2]}),
               Column({"average_columns":[0, 1, 2], "best_of":-1}),
               Column({"average_columns":[0, 1, 2], "mean_of":-1}),
               Column({"real_weight":3, "min":-40, "max":-20}),
               Column({"average_columns":[5, 6]}),
               Column({"real_weight_add":False, "real_weight":-0.1}),
               Column({"average_columns":[5, 8]}),
               ])
    g = Cell(-30)
    C = CE
    for line in [
[Cell(1  ),Cell(2  ),Cell(6  ),C(3  ),C(1.5),C(4  ),g,C(8.5  ),g,C(7  )],
[Cell(1  ),Cell(2  ),Cell(abi),C(1  ),C(0.5),C(1.5),g,C(7.875),g,C(4.5)],
[Cell(abi),Cell(abi),Cell(abi),C(abi),C(abi),C(abi),g,C(7.5  ),g,C(abi)],
[Cell(1  ),Cell(2  ),Cell(abj),C(1.5),C(1  ),C(2  ),g,C(8    ),g,C(5  )],
[Cell(1  ),Cell(abj),Cell(abj),C(1  ),C(nan),C(nan),g,C(nan  ),g,C(nan)],
[Cell(abj),Cell(abj),Cell(abj),C(abj),C(nan),C(nan),g,C(nan  ),g,C(nan)],
[Cell(abi),Cell(abj),Cell(abj),C(0  ),C(nan),C(nan),g,C(nan  ),g,C(nan)],
[Cell(tnr),Cell(abj),Cell(ppn),C(0  ),C(nan),C(nan),g,C(nan  ),g,C(nan)],
[Cell(0  ),Cell(0  ),Cell(0  ),C(0  ),C(0  ),C(0  ),g,C(7.5  ),g,C(3  )],
[Cell(pre),Cell(pre),Cell(pre),C(20 ),C(20 ),C(20 ),g,C(12.5 ),g,C(23 )],
[Cell(1  ),Cell(1  ),Cell("" ),C(nan),C(nan),C(nan),g,C(nan  ),g,C(nan)],
# ABI + 0 = ABI
[Cell(abi),Cell(abi),Cell(abi),C(abi),C(abi),C(abi),g,C(7.5  ),Cell(0),C(abi)],
# allowed_grades
[Cell("DIS"),Cell(1),Cell(3)  ,C(2  ),C(1  ),C(3  ),g,C(8.25 ),g,C(6)],
]:
        check_result(line, 3, compute_average)
        check_result(line, 4, compute_average)
        check_result(line, 5, compute_average)
        check_result(line, 7, compute_average)
        check_result(line, 9, compute_average)

    for value, expect in [
            [1.22, [2, 1, 1.2, 1.2]],
            [1.27, [2, 1, 1.2, 1.3]],
            [1.31, [2, 1, 1.4, 1.3]],
            [-.24, [0, 0, -0.2, -0.2]],
            [-.69, [0,-1, -0.6, -0.7]],
        ]:
        for i in range(len(expect)):
            round_by = [2, 1, 0.2, 0.1][i]
            exp = expect[i]
            columns_set([Column(),
                         Column({'average_columns':[0], 'round_by':round_by})
                       ])
            check_result([Cell(value), C(exp)], 1, compute_average)

    columns_set([Column({"real_weight_add":False, "empty_is":abi}),
                 Column({"real_weight_add":False}),
                 Column({'average_columns':[0,1]})])
    for v1, v2, expect in [
        [1  , 1  , 2  ],
        [abi, 1  , 1  ],
        [abi, abi, abi],
        [abi, 0  , 0  ],
        ['' , abi, abi],
        [abj, 1  , nan],
        [ppn, 1  , nan],
        [abj, 0  , nan],
        [abj, abj, abj],
        [abi, tnr, abi],
        [1  , abi, 1  ],
        ]:
        check_result([Cell(v1), Cell(v2), C(expect)], 2, compute_average)

    columns_set([Column(), Column(), Column(),
                 Column( {"average_columns":[0,1,2]}),
               Column( {"average_columns":[0,1,2], "best_of":-1}),
               Column( {"average_columns":[0,1,2], "mean_of":-1}),
               Column( {"average_columns":[0,1,2], "best_of":-1, "mean_of":-1}),
               Column( {"real_weight":1, "real_weight_add":False}),
               Column( {"average_columns":[0,1,2,7]}),
               Column( {"real_weight":1, "real_weight_add":False}),
               Column( {"average_columns":[0,1,2,9]}),
               Column( {"real_weight_add":False}),
               Column( {"real_weight_add":False}),
               Column( {"real_weight_add":False}),
               Column( {"average_columns":[11,12,13]}),
               ])
        
    for cells, value, v_best, v_mean, v_best_mean, v_p1, v_m1, v_sum in [
[[abi, abi, abi], abi, abi, abi, abi, abi, abi, abi],
[[abi, abi, abj],   0,   0,   0, nan,   1,  -1, nan],
[[abi, abi, ppn],   0,   0,   0, nan,   1,  -1, nan],
[[abi, abi, tnr], abi, abi, abi, abi, abi, abi, abi],
[[abi, abj, abj],   0, nan, nan, nan,   1,  -1, nan],
[[abi, abj, ppn],   0, nan, nan, nan,   1,  -1, nan],
[[abi, abj, tnr],   0,   0,   0, nan,   1,  -1, nan],
[[abi, ppn, ppn],   0, nan, nan, nan,   1,  -1, nan],
[[abi, ppn, tnr],   0,   0,   0, nan,   1,  -1, nan],
[[abi, tnr, tnr], abi, abi, abi, abi, abi, abi, abi],
[[abj, abj, abj], abj, nan, nan, nan, abj, abj, abj],
[[abj, abj, ppn], ppn, nan, nan, nan, ppn, ppn, nan],
[[abj, abj, tnr],   0, nan, nan, nan,   1,  -1, nan],
[[abj, ppn, ppn], ppn, nan, nan, nan, ppn, ppn, nan],
[[abj, ppn, tnr],   0, nan, nan, nan,   1,  -1, nan],
[[abj, tnr, tnr],   0,   0,   0, nan,   1,  -1, nan],
[[ppn, ppn, ppn], ppn, nan, nan, nan, ppn, ppn, nan],
[[ppn, ppn, tnr],   0, nan, nan, nan,   1,  -1, nan],
[[ppn, tnr, tnr],   0,   0,   0, nan,   1,  -1, nan],
[[tnr, tnr, tnr], abi, abi, abi, abi, abi, abi, abi],
[[  0, abi, abi],   0,   0,   0,   0,   1,  -1,   0],
[[  0, abi, abj],   0,   0,   0, nan,   1,  -1, nan],
[[  0, abi, ppn],   0,   0,   0, nan,   1,  -1, nan],
[[  0, abi, tnr],   0,   0,   0,   0,   1,  -1,   0],
[[  0, abj, abj],   0, nan, nan, nan,   1,  -1, nan],
[[  0, abj, ppn],   0, nan, nan, nan,   1,  -1, nan],
[[  0, abj, tnr],   0,   0,   0, nan,   1,  -1, nan],
[[  0, ppn, ppn],   0, nan, nan, nan,   1,  -1, nan],
[[  0, ppn, tnr],   0,   0,   0, nan,   1,  -1, nan],
[[  0, tnr, tnr],   0,   0,   0,   0,   1,  -1,   0],
[[  0,   0, abi],   0,   0,   0,   0,   1,  -1,   0],
[[  0,   0, abj],   0,   0,   0, nan,   1,  -1, nan],
[[  0,   0, ppn],   0,   0,   0, nan,   1,  -1, nan],
[[  0,   0, tnr],   0,   0,   0,   0,   1,  -1,   0],
[[  0,   0,   0],   0,   0,   0,   0,   1,  -1,   0],
[[  0,   0,  12],   4,   0,   6,   0,   5,   3,  12],
[[  0,   0, nan], nan, nan, nan, nan, nan, nan, nan],
[[  0,  12, abi],   4,   0,   6,   0,   5,   3,  12],
[[  0,  12, abj],   6,   0,  12, nan,   7,   5, nan],
[[  0,  12, ppn],   6,   0,  12, nan,   7,   5, nan],
[[  0,  12, tnr],   4,   0,   6,   0,   5,   3,  12],
[[  0,  12,  12],   8,   6,  12,  12,   9,   7,  24],
[[  0,  12, nan], nan, nan, nan, nan, nan, nan, nan],
[[  0, nan, abi], nan, nan, nan, nan, nan, nan, nan],
[[  0, nan, abj], nan, nan, nan, nan, nan, nan, nan],
[[  0, nan, ppn], nan, nan, nan, nan, nan, nan, nan],
[[  0, nan, tnr], nan, nan, nan, nan, nan, nan, nan],
[[  0, nan,   0], nan, nan, nan, nan, nan, nan, nan],
[[  0, nan,  12], nan, nan, nan, nan, nan, nan, nan],
[[  0, nan, nan], nan, nan, nan, nan, nan, nan, nan],
[[ 12, abi, abi],   4,   0,   6,   0,   5,   3,  12],
[[ 12, abi, abj],   6,   0,  12, nan,   7,   5, nan],
[[ 12, abi, ppn],   6,   0,  12, nan,   7,   5, nan],
[[ 12, abi, tnr],   4,   0,   6,   0,   5,   3,  12],
[[ 12, abj, abj],  12, nan, nan, nan,  13,  11, nan],
[[ 12, abj, ppn],  12, nan, nan, nan,  13,  11, nan],
[[ 12, abj, tnr],   6,   0,  12, nan,   7,   5, nan],
[[ 12, ppn, ppn],  12, nan, nan, nan,  13,  11, nan],
[[ 12, ppn, tnr],   6,   0,  12, nan,   7,   5, nan],
[[ 12, tnr, tnr],   4,   0,   6,   0,   5,   3,  12],
[[ 12,  12, abi],   8,   6,  12,  12,   9,   7,  24],
[[ 12,  12, abj],  12,  12,  12, nan,  13,  11, nan],
[[ 12,  12, ppn],  12,  12,  12, nan,  13,  11, nan],
[[ 12,  12, tnr],   8,   6,  12,  12,   9,   7,  24],
[[ 12,  12,  12],  12,  12,  12,  12,  13,  11,  36],
[[ 12,  12, nan], nan, nan, nan, nan, nan, nan, nan],
[[ 12, nan, abi], nan, nan, nan, nan, nan, nan, nan],
[[ 12, nan, abj], nan, nan, nan, nan, nan, nan, nan],
[[ 12, nan, ppn], nan, nan, nan, nan, nan, nan, nan],
[[ 12, nan, tnr], nan, nan, nan, nan, nan, nan, nan],
[[ 12, nan,   0], nan, nan, nan, nan, nan, nan, nan],
[[ 12, nan,  12], nan, nan, nan, nan, nan, nan, nan],
[[ 12, nan, nan], nan, nan, nan, nan, nan, nan, nan],
[[nan, abi, abi], nan, nan, nan, nan, nan, nan, nan],
[[nan, abi, abj], nan, nan, nan, nan, nan, nan, nan],
[[nan, abi, ppn], nan, nan, nan, nan, nan, nan, nan],
[[nan, abi, tnr], nan, nan, nan, nan, nan, nan, nan],
[[nan, abj, abj], nan, nan, nan, nan, nan, nan, nan],
[[nan, abj, ppn], nan, nan, nan, nan, nan, nan, nan],
[[nan, abj, tnr], nan, nan, nan, nan, nan, nan, nan],
[[nan, ppn, ppn], nan, nan, nan, nan, nan, nan, nan],
[[nan, ppn, tnr], nan, nan, nan, nan, nan, nan, nan],
[[nan, tnr, tnr], nan, nan, nan, nan, nan, nan, nan],
[[nan,   0, abi], nan, nan, nan, nan, nan, nan, nan],
[[nan,   0, abj], nan, nan, nan, nan, nan, nan, nan],
[[nan,   0, ppn], nan, nan, nan, nan, nan, nan, nan],
[[nan,   0, tnr], nan, nan, nan, nan, nan, nan, nan],
[[nan,   0,   0], nan, nan, nan, nan, nan, nan, nan],
[[nan,   0,  12], nan, nan, nan, nan, nan, nan, nan],
[[nan,   0, nan], nan, nan, nan, nan, nan, nan, nan],
[[nan,  12, abi], nan, nan, nan, nan, nan, nan, nan],
[[nan,  12, abj], nan, nan, nan, nan, nan, nan, nan],
[[nan,  12, ppn], nan, nan, nan, nan, nan, nan, nan],
[[nan,  12, tnr], nan, nan, nan, nan, nan, nan, nan],
[[nan,  12,  12], nan, nan, nan, nan, nan, nan, nan],
[[nan,  12, nan], nan, nan, nan, nan, nan, nan, nan],
[[nan, nan, abi], nan, nan, nan, nan, nan, nan, nan],
[[nan, nan, abj], nan, nan, nan, nan, nan, nan, nan],
[[nan, nan, ppn], nan, nan, nan, nan, nan, nan, nan],
[[nan, nan, tnr], nan, nan, nan, nan, nan, nan, nan],
[[nan, nan,   0], nan, nan, nan, nan, nan, nan, nan],
[[nan, nan,  12], nan, nan, nan, nan, nan, nan, nan],
[[nan, nan, nan], nan, nan, nan, nan, nan, nan, nan],
        ]:
        line = [Cell(cells[0]), Cell(cells[1]), Cell(cells[2]),
                C(value), C(v_best), C(v_mean), C(v_best_mean),
                Cell(1), C(v_p1), Cell(-1), C(v_m1),
                Cell(cells[0]), Cell(cells[1]), Cell(cells[2]), C(v_sum) ]
        check_result(line, 3, compute_average)
        check_result(line, 4, compute_average)
        check_result(line, 5, compute_average)
        check_result(line, 6, compute_average)
        check_result(line, 8, compute_average)
        check_result(line, 10, compute_average)

    def combinations(values):
        if len(values) == 1:
            return [[values[0]]]
        result = []
        for i in range(len(values)):
            tous_sauf_i = values[:i]
            for j in values[i+1:]:
                tous_sauf_i.append(j)
            for v in combinations(tous_sauf_i):
                v.append(values[i])
                result.append(v)
        return result
    columns_set([Column(), Column(), Column(), Column(), Column(), Column(),
               Column({"average_columns":[0, 1, 2, 3, 4 ,5],
                       "mean_of":-3}),
               ])
    for i in combinations([3, abi, abj, tnr, ppn, 2]):
        check_result([Cell(i[0]), Cell(i[1]), Cell(i[2]), Cell(i[3]),
                      Cell(i[4]), Cell(i[5]), C(3)], 6, compute_average)

    columns_set([Column(), Column(), Column(),
                 Column({"average_columns":[0, 1, 2],
                         "abj_is": 1}),
                 Column({"average_columns":[0, 1, 2],
                         "mean_of":-1, "abj_is": 1}),
                 Column({"average_columns":[0, 1, 2],
                         "best_of":-1, "abj_is": 1}),
                 Column({"average_columns":[0, 1, 2],
                         "mean_of":-1, "best_of":-1, "abj_is": 1}),
                 Column({"average_columns":[0, 1, 2],
                         "mean_of":-1, "best_of":-1, "abj_is": 2}),
             ])
    for line in [
            [Cell(1  ),Cell(1  ),Cell(1  ),C(1  ),C(1  ),C(1  ),C(1  ),C(1  )],
            [Cell(3  ),Cell(3  ),Cell(9  ),C(5  ),C(6  ),C(3  ),C(3  ),C(3  )],
            [Cell(2  ),Cell(6  ),Cell(abj),C(4  ),C(5  ),C(3  ),C(4  ),C(nan)],
            [Cell(2  ),Cell(abj),Cell(abj),C(2  ),C(2  ),C(2  ),C(2  ),C(nan)],
            [Cell(abj),Cell(abj),Cell(abj),C(abj),C(abj),C(abj),C(abj),C(abj)],
            [Cell(abi),Cell(abj),Cell(abj),C(0  ),C(0  ),C(0  ),C(0  ),C(nan)],
            [Cell(2  ),Cell(6  ),Cell(ppn),C(4  ),C(6  ),C(2  ),C(nan),C(4  )],
            [Cell(abj),Cell(6  ),Cell(ppn),C(6  ),C(6  ),C(6  ),C(nan),C(nan)],
            [Cell(ppn),Cell(ppn),Cell(ppn),C(ppn),C(ppn),C(ppn),C(ppn),C(ppn)],
            [Cell(abj),Cell(ppn),Cell(ppn),C(ppn),C(nan),C(nan),C(nan),C(nan)],
            [Cell(abi),Cell(ppn),Cell(ppn),C(0  ),C(nan),C(nan),C(nan),C(0  )],
    ]:
        check_result(line, 3, compute_average)
        check_result(line, 4, compute_average)
        check_result(line, 5, compute_average)
        check_result(line, 6, compute_average)
        check_result(line, 7, compute_average)
# Not allowed to use mean_of or best_of with additions
#     columns_set([Column(), Column(), Column(),
#                  Column({"real_weight_add":False, "real_weight":1}),
#                  Column({"average_columns":[0, 1, 2, 3],
#                          "mean_of":-1, "abj_is": 1}),
#              ])
#     for line in [
#             [Cell(2  ),Cell(6  ),Cell(abj), Cell(1), C(6  )],
#             [Cell(2  ),Cell(abj),Cell(abj), Cell(1), C(3  )],
#             [Cell(abj),Cell(abj),Cell(abj), Cell(1), C(ppn)],
#             [Cell(abi),Cell(abj),Cell(abj), Cell(1), C(1  )],
#     ]:
#         check_result(line, 4, compute_average)

    print('Average regtest are fine')

average_regtest()
