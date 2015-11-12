#!/usr/bin/python3
# -*- coding: utf-8 -*-
# TOMUSS: The Online Multi User Simple Spreadsheet
# Copyright (C) 2015 Thierry EXCOFFIER, Universite Claude Bernard
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

def product_regtest():
    columns_set([Column(), Column(), Column(),
                 Column({"average_columns":[0, 1, 2]}),
               ])
    for cells, value in [
            [[  2,  2,  2], 8],
            [[  2,  2,abi], 0],
[[  2,  2,abj], nan],
[[  2,  2,ppn], nan],
            [[  2,  2,tnr], 0],
            [[  2,abi,abi], 0],
[[  2,abi,abj], nan],
[[  2,abi,ppn], nan],
            [[  2,abi,tnr], 0],
[[  2,abj,abj], nan],
[[  2,abj,ppn], nan],
[[  2,abj,tnr], nan],
[[  2,ppn,ppn], nan],
[[  2,ppn,tnr], nan],
            [[  2,tnr,tnr], 0],
            [[abi,abi,abi], abi],
[[abi,abi,abj], nan],
[[abi,abi,ppn], nan],
            [[abi,abi,tnr], abi],
[[abi,abj,abj], nan],
[[abi,abj,ppn], nan],
[[abi,abj,tnr], nan],
[[abi,ppn,ppn], nan],
[[abi,ppn,tnr], nan],
            [[abi,tnr,tnr], abi],
            [[abj,abj,abj], abj],
[[abj,abj,ppn], nan],
[[abj,abj,tnr], nan],
[[abj,ppn,ppn], nan],
[[abj,ppn,tnr], nan],
[[abj,tnr,tnr], nan],
            [[ppn,ppn,ppn], ppn],
[[ppn,ppn,tnr], nan],
[[ppn,tnr,tnr], nan],
            [[tnr,tnr,tnr], abi],
    ]:
        line = [Cell(cells[0]), Cell(cells[1]), Cell(cells[2]), CE(value)]
        check_result(line, 3, compute_product)
        
    print('Product regtest are fine')

product_regtest()
