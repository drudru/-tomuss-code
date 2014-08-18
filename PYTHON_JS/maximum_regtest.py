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

columns = []

def maximum_regtest():
    global columns
    columns = [Column(), Column(), Column(),
               Column(average_columns = [0, 1, 2]),
               ]
    for cells, value in (
            ((abi, abi, abi), abi),
            ((abi, abi, abj), 0),
            ((abi, abi, ppn), 0),
            ((abi, abi, tnr), abi),
            ((abi, abj, abj), 0),
            ((abi, abj, ppn), 0),
            ((abi, abj, tnr), 0),
            ((abi, ppn, ppn), 0),
            ((abi, ppn, tnr), 0),
            ((abi, tnr, tnr), abi),
            ((abj, abj, abj), nan),
            ((abj, abj, ppn), nan),
            ((abj, abj, tnr), 0),
            ((abj, ppn, ppn), nan),
            ((abj, ppn, tnr), 0),
            ((abj, tnr, tnr), 0),
            ((ppn, ppn, ppn), nan),
            ((ppn, ppn, tnr), 0),
            ((ppn, tnr, tnr), 0),
            ((tnr, tnr, tnr), abi),
            ((  0, abi, abi), 0),
            ((  0, abi, abj), 0),
            ((  0, abi, ppn), 0),
            ((  0, abi, tnr), 0),
            ((  0, abj, abj), 0),
            ((  0, abj, ppn), 0),
            ((  0, abj, tnr), 0),
            ((  0, ppn, ppn), 0),
            ((  0, ppn, tnr), 0),
            ((  0, tnr, tnr), 0),
            ((  0,   0, abi), 0),
            ((  0,   0, abj), 0),
            ((  0,   0, ppn), 0),
            ((  0,   0, tnr), 0),
            ((  0,   0,   0), 0),
            ((  0,   0,  12), 12),
            ((  0,   0, nan), nan),
            ((  0,  12, abi), 12),
            ((  0,  12, abj), 12),
            ((  0,  12, ppn), 12),
            ((  0,  12, tnr), 12),
            ((  0,  12,  12), 12),
            ((  0,  12, nan), nan),
            ((  0, nan, abi), nan),
            ((  0, nan, abj), nan),
            ((  0, nan, ppn), nan),
            ((  0, nan, tnr), nan),
            ((  0, nan,   0), nan),
            ((  0, nan,  12), nan),
            ((  0, nan, nan), nan),
            (( 12, abi, abi), 12),
            (( 12, abi, abj), 12),
            (( 12, abi, ppn), 12),
            (( 12, abi, tnr), 12),
            (( 12, abj, abj), 12),
            (( 12, abj, ppn), 12),
            (( 12, abj, tnr), 12),
            (( 12, ppn, ppn), 12),
            (( 12, ppn, tnr), 12),
            (( 12, tnr, tnr), 12),
            (( 12,  12, abi), 12),
            (( 12,  12, abj), 12),
            (( 12,  12, ppn), 12),
            (( 12,  12, tnr), 12),
            (( 12,  12,  12), 12),
            (( 12,  12, nan), nan),
            (( 12, nan, abi), nan),
            (( 12, nan, abj), nan),
            (( 12, nan, ppn), nan),
            (( 12, nan, tnr), nan),
            (( 12, nan,   0), nan),
            (( 12, nan,  12), nan),
            (( 12, nan, nan), nan),
            ((nan, abi, abi), nan),
            ((nan, abi, abj), nan),
            ((nan, abi, ppn), nan),
            ((nan, abi, tnr), nan),
            ((nan, abj, abj), nan),
            ((nan, abj, ppn), nan),
            ((nan, abj, tnr), nan),
            ((nan, ppn, ppn), nan),
            ((nan, ppn, tnr), nan),
            ((nan, tnr, tnr), nan),
            ((nan,   0, abi), nan),
            ((nan,   0, abj), nan),
            ((nan,   0, ppn), nan),
            ((nan,   0, tnr), nan),
            ((nan,   0,   0), nan),
            ((nan,   0,  12), nan),
            ((nan,   0, nan), nan),
            ((nan,  12, abi), nan),
            ((nan,  12, abj), nan),
            ((nan,  12, ppn), nan),
            ((nan,  12, tnr), nan),
            ((nan,  12,  12), nan),
            ((nan,  12, nan), nan),
            ((nan, nan, abi), nan),
            ((nan, nan, abj), nan),
            ((nan, nan, ppn), nan),
            ((nan, nan, tnr), nan),
            ((nan, nan,   0), nan),
            ((nan, nan,  12), nan),
            ((nan, nan, nan), nan),
        ):
        line = [Cell(cells[0]), Cell(cells[1]), Cell(cells[2]), CE(value)]
        check_result(line, 3, compute_max_real)
        
    print 'Maximum regtest are fine'

maximum_regtest()
