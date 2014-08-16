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
"""

if False and python_mode:
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
           Column(average_columns = [11,12,13]),
]            

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
def infos():
    return ('[' + ','.join("'" + str(x) + "'" for x in i)
            + (',"%s"' % strip0(line[3].value))
            + (',"%s"' % strip0(line[4].value))
            + (',"%s"' % strip0(line[5].value))
            + (',"%s"' % strip0(line[6].value))
            + (',"%s"' % strip0(line[8].value))
            + (',"%s"' % strip0(line[10].value))
            + (',"%s"' % strip0(line[14].value))
            + (',"%s"' % strip0(line[15].value))
            + ']')

for i in values:
    line = [Cell(i[0]), Cell(i[1]), Cell(i[2]), C(0), C(0), C(0), C(0),
            Cell(1), C(0), Cell(-1), C(0),
            Cell(i[0]), Cell(i[1]), Cell(i[2]), C(0), C(0)]
    compute_average(3, line)
    compute_average(4, line)
    compute_average(5, line)
    compute_average(6, line)
    compute_average(8, line)
    compute_average(10, line)
    compute_average(14, line)
    compute_max_real(15, line)
    s.append(infos())
    compute_average_old(3, line)
    compute_average_old(4, line)
    compute_average_old(5, line)
    compute_average_old(6, line)
    compute_average_old(8, line)
    compute_average_old(10, line)
    compute_average_old(14, line)
    compute_max_real_old(15, line)
    t.append(infos())
print 'new_values = [', ',\n'.join(s), '];'
print 'old_values = [', ',\n'.join(t), '];'
