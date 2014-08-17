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

def diff_date_regtest():
    def check(line, col):
        compute_diff_date(col, line)
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
    columns = [Column(), Column(), Column(average_columns = [0, 1])]
    for values in (
            ('5/1/2014', '6/1/2014', 1),
            ('6/1/2014', '5/1/2014', -1),
            ('6/1', '6/2', 31),
            ('1', '2', 1),
            ('1j', '2j', -1),
            ('', '', 0),
            ):
        line = [Cell(values[0]), Cell(values[1]), CE(values[2])]
        check(line, 2)
        
    print 'Diff_date regtest are fine'

diff_date_regtest()
