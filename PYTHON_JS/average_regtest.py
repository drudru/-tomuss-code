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

abi_short = abi = "ABI"
abj_short = abj = "ABJ"
tnr_short = tnr = "TNR"
ppn_short = ppn = "PPN"
pre_short = pre = "PRE"

create_js_data = False

columns = []

def average_regtest():
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

    def C(expected):
        return Cell(-1, expected)
    
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
    if create_js_data and python_mode:
        # Generate values to include in this program
        v = (12, 0, abi, abj, ppn, tnr, nan)
        itertools = __import__("itertools")
        t = [str(i) + ','
             for i in set(tuple(sorted(i))
                          for i in itertools.product(v, v, v)
                          )
             ]
        print 'values = ['
        print '\n'.join(sorted(t))
        print ']'
    if create_js_data:
        values = [
('ABI', 'ABI', 'ABI'),
('ABI', 'ABI', 'ABJ'),
('ABI', 'ABI', 'PPN'),
('ABI', 'ABI', 'TNR'),
('ABI', 'ABJ', 'ABJ'),
('ABI', 'ABJ', 'PPN'),
('ABI', 'ABJ', 'TNR'),
('ABI', 'PPN', 'PPN'),
('ABI', 'PPN', 'TNR'),
('ABI', 'TNR', 'TNR'),
('ABJ', 'ABJ', 'ABJ'),
('ABJ', 'ABJ', 'PPN'),
('ABJ', 'ABJ', 'TNR'),
('ABJ', 'PPN', 'PPN'),
('ABJ', 'PPN', 'TNR'),
('ABJ', 'TNR', 'TNR'),
('PPN', 'PPN', 'PPN'),
('PPN', 'PPN', 'TNR'),
('PPN', 'TNR', 'TNR'),
('TNR', 'TNR', 'TNR'),
(0, 'ABI', 'ABI'),
(0, 'ABI', 'ABJ'),
(0, 'ABI', 'PPN'),
(0, 'ABI', 'TNR'),
(0, 'ABJ', 'ABJ'),
(0, 'ABJ', 'PPN'),
(0, 'ABJ', 'TNR'),
(0, 'PPN', 'PPN'),
(0, 'PPN', 'TNR'),
(0, 'TNR', 'TNR'),
(0, 0, 'ABI'),
(0, 0, 'ABJ'),
(0, 0, 'PPN'),
(0, 0, 'TNR'),
(0, 0, 0),
(0, 0, 12),
(0, 0, nan),
(0, 12, 'ABI'),
(0, 12, 'ABJ'),
(0, 12, 'PPN'),
(0, 12, 'TNR'),
(0, 12, 12),
(0, 12, nan),
(0, nan, 'ABI'),
(0, nan, 'ABJ'),
(0, nan, 'PPN'),
(0, nan, 'TNR'),
(0, nan, 0),
(0, nan, 12),
(0, nan, nan),
(12, 'ABI', 'ABI'),
(12, 'ABI', 'ABJ'),
(12, 'ABI', 'PPN'),
(12, 'ABI', 'TNR'),
(12, 'ABJ', 'ABJ'),
(12, 'ABJ', 'PPN'),
(12, 'ABJ', 'TNR'),
(12, 'PPN', 'PPN'),
(12, 'PPN', 'TNR'),
(12, 'TNR', 'TNR'),
(12, 12, 'ABI'),
(12, 12, 'ABJ'),
(12, 12, 'PPN'),
(12, 12, 'TNR'),
(12, 12, 12),
(12, 12, nan),
(12, nan, 'ABI'),
(12, nan, 'ABJ'),
(12, nan, 'PPN'),
(12, nan, 'TNR'),
(12, nan, 0),
(12, nan, 12),
(12, nan, nan),
(nan, 'ABI', 'ABI'),
(nan, 'ABI', 'ABJ'),
(nan, 'ABI', 'PPN'),
(nan, 'ABI', 'TNR'),
(nan, 'ABJ', 'ABJ'),
(nan, 'ABJ', 'PPN'),
(nan, 'ABJ', 'TNR'),
(nan, 'PPN', 'PPN'),
(nan, 'PPN', 'TNR'),
(nan, 'TNR', 'TNR'),
(nan, 0, 'ABI'),
(nan, 0, 'ABJ'),
(nan, 0, 'PPN'),
(nan, 0, 'TNR'),
(nan, 0, 0),
(nan, 0, 12),
(nan, 0, nan),
(nan, 12, 'ABI'),
(nan, 12, 'ABJ'),
(nan, 12, 'PPN'),
(nan, 12, 'TNR'),
(nan, 12, 12),
(nan, 12, nan),
(nan, nan, 'ABI'),
(nan, nan, 'ABJ'),
(nan, nan, 'PPN'),
(nan, nan, 'TNR'),
(nan, nan, 0),
(nan, nan, 12),
(nan, nan, nan),
]
        s = []
        t = []
        for i in values:
            line = [Cell(i[0]), Cell(i[1]), Cell(i[2]), C(0), C(0), C(0), C(0),
                    Cell(1), C(0), Cell(-1), C(0),
                    Cell(i[0]), Cell(i[1]), Cell(i[2]), C(0)]
            if python_mode:
                compute_average(3, line)
                compute_average(4, line)
                compute_average(5, line)
                compute_average(6, line)
                compute_average(8, line)
                compute_average(10, line)
                compute_average(14, line)
                s.append('((' + ', '.join(('%3s' % x).lower() for x in i) + '), '
                         + ('%3s' % strip0(line[3].value)).lower() + ', '
                         + ('%3s' % strip0(line[4].value)).lower() + ', '
                         + ('%3s' % strip0(line[5].value)).lower() + ', '
                         + ('%3s' % strip0(line[6].value)).lower() + ', '
                         + ('%3s' % strip0(line[8].value)).lower() + ', '
                         + ('%3s' % strip0(line[10].value)).lower() + ','
                         + ('%3s' % strip0(line[14].value)).lower() + '),'
                         )
            else:
                compute_average_old(3, line)
                compute_average_old(4, line)
                compute_average_old(5, line)
                compute_average_old(6, line)
                compute_average_old(8, line)
                compute_average_old(10, line)
                compute_average_old(14, line)
            t.append('[' + ','.join("'" + str(x) + "'" for x in i)
                     + (',"%s"' % strip0(line[3].value))
                     + (',"%s"' % strip0(line[4].value))
                     + (',"%s"' % strip0(line[5].value))
                     + (',"%s"' % strip0(line[6].value))
                     + (',"%s"' % strip0(line[8].value))
                     + (',"%s"' % strip0(line[10].value))
                     + (',"%s"' % strip0(line[14].value))
                     + ']'
                     )
        print '\n'.join(s)
        if python_mode:
            print 'new_values',
        else:
            print 'old_values',
        print '= [\n' + ',\n'.join(t) + '\n] ;'
            
        
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
