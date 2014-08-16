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

if python_mode:
    C = Cell

def nmbr_regtest():
    def check(line, col):
        compute_nmbr(col, line)
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
    line = [Cell(5, author="john"), Cell('foo', comment="C1"),
            Cell('', date="20140101121212"), CE(0)]
    for filter, result in (
            ('>3', 1),
            ('>1', 2),
            ('=', 0),
            ('>1 <5', 1),
            ('#', 1),
            ('#d', 0),
            ('#c', 1),
            ('=5 | #=C1 | ?=01/01/2014', 3),
            ):
        columns = [Column(), Column(), Column(empty_is=2),
                   Column(average_columns = [0, 1, 2],
                          test_filter=filter
                      ),
               ]
        line[3].expected = result
        check(line, 3)
        
    print 'Nmbr regtest are fine'

nmbr_regtest()
