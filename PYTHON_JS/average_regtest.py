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

def average_regtest():

    def check(line, col):
        compute_average(col, line)
        if strip0(line[col].value) != strip0(line[col].expected):
            try:
                if abs(float(line[col].value) - float(line[col].expected)
                       ) < 1e-5:
                    return
            except ValueError:
                pass
            print '='*77
            print "Column:", col
            print line
            print 'Expected:', line[col].expected
            print 'Computed:', line[col].value
            regression_test_failed

    global columns
    columns = [Column(), Column(), Column(),
               Column(average_columns = [0, 1, 2]),
               Column(average_columns = [0, 1, 2], best_of=-1),
               Column(average_columns = [0, 1, 2], mean_of=-1),
               Column(real_weight = 3, min=-40, max=-20),
               Column(average_columns = [5, 6]),
               Column(real_weight_add = False, real_weight = -0.1),
               Column(average_columns = [5, 8]),
               ]
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
# ABI + 0 = ABI
[Cell(abi),Cell(abi),Cell(abi),C(abi),C(abi),C(abi),g,C(7.5  ),Cell(0),C(abi)],
]:
        check(line, 3)
        check(line, 4)
        check(line, 5)
        check(line, 7)
        check(line, 9)

    for value, expect in (
        (1.22, (2, 1, 1.2, 1.2)),
        (1.27, (2, 1, 1.2, 1.3)),
        (1.31, (2, 1, 1.4, 1.3)),
        (-.24, (0, 0, -0.2, -0.2)),
        (-.69, (0,-1, -0.6, -0.7)),
        ):
        for i in range(len(expect)):
            round_by = (2, 1, 0.2, 0.1)[i]
            exp = expect[i]
            columns = [Column(),
                       Column(average_columns = [0], round_by = round_by)
                       ]
            check([Cell(value), C(exp)], 1)
    
    columns = [Column(real_weight_add = False, empty_is=abi),
               Column(real_weight_add = False),
               Column(average_columns = [0,1])]
    for v1, v2, expect in (
        (1  , 1  , 2  ),
        (abi, 1  , 1  ),
        (abi, abi, abi),
        (abi, 0  , 0  ),
        ('' , abi, abi),
        (abj, 1  , nan),
        (ppn, 1  , nan),
        (abj, 0  , nan),
        (abj, abj, abj),
        (abi, tnr, abi),
        (1  , abi, 1  ),
        ):
        check([Cell(v1), Cell(v2), C(expect)], 2)

    columns = [Column(), Column(), Column(),
               Column(average_columns = [0,1,2]),
               Column(average_columns = [0,1,2], best_of=-1),
               Column(average_columns = [0,1,2], mean_of=-1),
               Column(average_columns = [0,1,2], best_of=-1, mean_of=-1),
               Column(real_weight=1, real_weight_add=False),
               Column(average_columns = [0,1,2,7]),
               Column(real_weight=1, real_weight_add=False),
               Column(average_columns = [0,1,2,9]),
               Column(real_weight_add=False),
               Column(real_weight_add=False),
               Column(real_weight_add=False),
               Column(average_columns = [11,12,13]),
               ]            
        
    for cells, value, v_best, v_mean, v_best_mean, v_p1, v_m1, v_sum in (
((abi, abi, abi), abi, abi, abi, abi, abi, abi, abi),
((abi, abi, abj),   0,   0,   0, nan,   1,  -1, nan),
((abi, abi, ppn),   0,   0,   0, nan,   1,  -1, nan),
((abi, abi, tnr), abi, abi, abi, abi, abi, abi, abi),
((abi, abj, abj),   0, nan, nan, nan,   1,  -1, nan),
((abi, abj, ppn),   0, nan, nan, nan,   1,  -1, nan),
((abi, abj, tnr),   0,   0,   0, nan,   1,  -1, nan),
((abi, ppn, ppn),   0, nan, nan, nan,   1,  -1, nan),
((abi, ppn, tnr),   0,   0,   0, nan,   1,  -1, nan),
((abi, tnr, tnr), abi, abi, abi, abi, abi, abi, abi),
((abj, abj, abj), abj, nan, nan, nan, abj, abj, abj),
((abj, abj, ppn), ppn, nan, nan, nan, ppn, ppn, nan),
((abj, abj, tnr),   0, nan, nan, nan,   1,  -1, nan),
((abj, ppn, ppn), ppn, nan, nan, nan, ppn, ppn, nan),
((abj, ppn, tnr),   0, nan, nan, nan,   1,  -1, nan),
((abj, tnr, tnr),   0,   0,   0, nan,   1,  -1, nan),
((ppn, ppn, ppn), ppn, nan, nan, nan, ppn, ppn, nan),
((ppn, ppn, tnr),   0, nan, nan, nan,   1,  -1, nan),
((ppn, tnr, tnr),   0,   0,   0, nan,   1,  -1, nan),
((tnr, tnr, tnr), abi, abi, abi, abi, abi, abi, abi),
((  0, abi, abi),   0,   0,   0,   0,   1,  -1,   0),
((  0, abi, abj),   0,   0,   0, nan,   1,  -1, nan),
((  0, abi, ppn),   0,   0,   0, nan,   1,  -1, nan),
((  0, abi, tnr),   0,   0,   0,   0,   1,  -1,   0),
((  0, abj, abj),   0, nan, nan, nan,   1,  -1, nan),
((  0, abj, ppn),   0, nan, nan, nan,   1,  -1, nan),
((  0, abj, tnr),   0,   0,   0, nan,   1,  -1, nan),
((  0, ppn, ppn),   0, nan, nan, nan,   1,  -1, nan),
((  0, ppn, tnr),   0,   0,   0, nan,   1,  -1, nan),
((  0, tnr, tnr),   0,   0,   0,   0,   1,  -1,   0),
((  0,   0, abi),   0,   0,   0,   0,   1,  -1,   0),
((  0,   0, abj),   0,   0,   0, nan,   1,  -1, nan),
((  0,   0, ppn),   0,   0,   0, nan,   1,  -1, nan),
((  0,   0, tnr),   0,   0,   0,   0,   1,  -1,   0),
((  0,   0,   0),   0,   0,   0,   0,   1,  -1,   0),
((  0,   0,  12),   4,   0,   6,   0,   5,   3,  12),
((  0,   0, nan), nan, nan, nan, nan, nan, nan, nan),
((  0,  12, abi),   4,   0,   6,   0,   5,   3,  12),
((  0,  12, abj),   6,   0,  12, nan,   7,   5, nan),
((  0,  12, ppn),   6,   0,  12, nan,   7,   5, nan),
((  0,  12, tnr),   4,   0,   6,   0,   5,   3,  12),
((  0,  12,  12),   8,   6,  12,  12,   9,   7,  24),
((  0,  12, nan), nan, nan, nan, nan, nan, nan, nan),
((  0, nan, abi), nan, nan, nan, nan, nan, nan, nan),
((  0, nan, abj), nan, nan, nan, nan, nan, nan, nan),
((  0, nan, ppn), nan, nan, nan, nan, nan, nan, nan),
((  0, nan, tnr), nan, nan, nan, nan, nan, nan, nan),
((  0, nan,   0), nan, nan, nan, nan, nan, nan, nan),
((  0, nan,  12), nan, nan, nan, nan, nan, nan, nan),
((  0, nan, nan), nan, nan, nan, nan, nan, nan, nan),
(( 12, abi, abi),   4,   0,   6,   0,   5,   3,  12),
(( 12, abi, abj),   6,   0,  12, nan,   7,   5, nan),
(( 12, abi, ppn),   6,   0,  12, nan,   7,   5, nan),
(( 12, abi, tnr),   4,   0,   6,   0,   5,   3,  12),
(( 12, abj, abj),  12, nan, nan, nan,  13,  11, nan),
(( 12, abj, ppn),  12, nan, nan, nan,  13,  11, nan),
(( 12, abj, tnr),   6,   0,  12, nan,   7,   5, nan),
(( 12, ppn, ppn),  12, nan, nan, nan,  13,  11, nan),
(( 12, ppn, tnr),   6,   0,  12, nan,   7,   5, nan),
(( 12, tnr, tnr),   4,   0,   6,   0,   5,   3,  12),
(( 12,  12, abi),   8,   6,  12,  12,   9,   7,  24),
(( 12,  12, abj),  12,  12,  12, nan,  13,  11, nan),
(( 12,  12, ppn),  12,  12,  12, nan,  13,  11, nan),
(( 12,  12, tnr),   8,   6,  12,  12,   9,   7,  24),
(( 12,  12,  12),  12,  12,  12,  12,  13,  11,  36),
(( 12,  12, nan), nan, nan, nan, nan, nan, nan, nan),
(( 12, nan, abi), nan, nan, nan, nan, nan, nan, nan),
(( 12, nan, abj), nan, nan, nan, nan, nan, nan, nan),
(( 12, nan, ppn), nan, nan, nan, nan, nan, nan, nan),
(( 12, nan, tnr), nan, nan, nan, nan, nan, nan, nan),
(( 12, nan,   0), nan, nan, nan, nan, nan, nan, nan),
(( 12, nan,  12), nan, nan, nan, nan, nan, nan, nan),
(( 12, nan, nan), nan, nan, nan, nan, nan, nan, nan),
((nan, abi, abi), nan, nan, nan, nan, nan, nan, nan),
((nan, abi, abj), nan, nan, nan, nan, nan, nan, nan),
((nan, abi, ppn), nan, nan, nan, nan, nan, nan, nan),
((nan, abi, tnr), nan, nan, nan, nan, nan, nan, nan),
((nan, abj, abj), nan, nan, nan, nan, nan, nan, nan),
((nan, abj, ppn), nan, nan, nan, nan, nan, nan, nan),
((nan, abj, tnr), nan, nan, nan, nan, nan, nan, nan),
((nan, ppn, ppn), nan, nan, nan, nan, nan, nan, nan),
((nan, ppn, tnr), nan, nan, nan, nan, nan, nan, nan),
((nan, tnr, tnr), nan, nan, nan, nan, nan, nan, nan),
((nan,   0, abi), nan, nan, nan, nan, nan, nan, nan),
((nan,   0, abj), nan, nan, nan, nan, nan, nan, nan),
((nan,   0, ppn), nan, nan, nan, nan, nan, nan, nan),
((nan,   0, tnr), nan, nan, nan, nan, nan, nan, nan),
((nan,   0,   0), nan, nan, nan, nan, nan, nan, nan),
((nan,   0,  12), nan, nan, nan, nan, nan, nan, nan),
((nan,   0, nan), nan, nan, nan, nan, nan, nan, nan),
((nan,  12, abi), nan, nan, nan, nan, nan, nan, nan),
((nan,  12, abj), nan, nan, nan, nan, nan, nan, nan),
((nan,  12, ppn), nan, nan, nan, nan, nan, nan, nan),
((nan,  12, tnr), nan, nan, nan, nan, nan, nan, nan),
((nan,  12,  12), nan, nan, nan, nan, nan, nan, nan),
((nan,  12, nan), nan, nan, nan, nan, nan, nan, nan),
((nan, nan, abi), nan, nan, nan, nan, nan, nan, nan),
((nan, nan, abj), nan, nan, nan, nan, nan, nan, nan),
((nan, nan, ppn), nan, nan, nan, nan, nan, nan, nan),
((nan, nan, tnr), nan, nan, nan, nan, nan, nan, nan),
((nan, nan,   0), nan, nan, nan, nan, nan, nan, nan),
((nan, nan,  12), nan, nan, nan, nan, nan, nan, nan),
((nan, nan, nan), nan, nan, nan, nan, nan, nan, nan),
        ):
        line = [Cell(cells[0]), Cell(cells[1]), Cell(cells[2]),
                C(value), C(v_best), C(v_mean), C(v_best_mean),
                Cell(1), C(v_p1), Cell(-1), C(v_m1),
                Cell(cells[0]), Cell(cells[1]), Cell(cells[2]), C(v_sum) ]
        check(line, 3)
        check(line, 4)
        check(line, 5)
        check(line, 6)
        check(line, 8)
        check(line, 10)

    def combinations(values):
        if len(values) == 1:
            return [[values[0]]]
        result = []
        for i in range(len(values)):
            for v in combinations(values[:i] + values[i+1:]):
                v.append(values[i])
                result.append(v)
        return result
    columns = [Column(), Column(), Column(), Column(), Column(), Column(),
               Column(average_columns = [0, 1, 2, 3, 4 ,5],
                      mean_of=-3),
               ]
    for i in combinations((3, abi, abj, tnr, ppn, 2)):
        check_result([Cell(i[0]), Cell(i[1]), Cell(i[2]), Cell(i[3]),
                      Cell(i[4]), Cell(i[5]), C(3)], 6, compute_average)

    print 'Average regtest are fine'

average_regtest()
