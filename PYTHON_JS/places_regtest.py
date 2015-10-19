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

def places_regtest():
    for text, expected, error in [
            ["", [], []],
            ["5", [5], []],
            ["5 7", [5,7], []],
            ["5 7 -5", [7], []],
            ["5 7 -7", [5], []],
            ["5 7 -5 -7", [], []],
            ["5 -6 7", [5,7], []],
            ["7 5", [5,7], []],
            ["5-7", [5,6,7], []],
            ["5-7 -5", [6,7], []],
            ["5-7 -7", [5,6], []],
            ["5-7 -6", [5,7], []],
            ["5-7 -6 -5", [7], []],
            ["5-7 -6 -7", [5], []],
            ["5-7 -4 -8", [5,6,7], []],
            ["5-7 4 8", [4,5,6,7,8], []],
            ["5-7 2-4 8-9", [2,3,4,5,6,7,8,9], []],
            ["5-7 2-4 8-9 -3 -6 -8", [2,4,5,7,9], []],
            ["4 4", [4],
             ['Overlapping ranges 4-4 and 4-4']],
            ["1-4 2-3 5", [1, 2, 3, 4, 5],
             ['Overlapping ranges 2-3 and 1-4']],
            ["7-5 9", [9],
             ['Minimum must be before maximum: 7-5']],
    ]:
        p = Places(text)
        if p.nr_places != len(expected):
            print("Unexpected number of places")
            fail0
        if '\n'.join(p.errors) != '\n'.join(error):
            print("Input: " + text + "\nExpected: "
                  + str(error) + "\nComputed: " + str(p.errors) + "\n")
            fail1
        result = []
        p.iter_start()
        while True:
            i = p.iter_next()
            if i is None:
                break
            result.append(int(i))

        if python_mode:
            assert result == [int(i) for i in p.iter()]

        if str(result) != str(expected):
            print("Input: " + text + "\nExpected: "
                  + str(expected) + "\nComputed: " + str(result) + "\n")
            fail2
places_regtest()
print('Places regtest are fine')
