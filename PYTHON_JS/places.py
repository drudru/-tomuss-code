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

class Places:
    def __init__(self, text):
        self.text = text
        self.intervals = [] # first and last value are included
        self.parse(text)
        if len(self.intervals):
            # Maximum number of digit for place number.
            # It is used to do the padding.
            self.length = len(str(self.intervals[-1][1]))
        # Compute the number of places.
        self.nr_places = 0
        for start, end in self.intervals:
            self.nr_places += end - start + 1

    def iter_start(self):
        self.iter_current = [i[:] for i in self.intervals[:]]

    def iter_next(self, padding=""):
        """Do not use yield because it needs ECMA script 6"""
        if len(self.iter_current) == 0:
            return ""
        start, end = self.iter_current[0]
        if start == end:
            python_pop(self.iter_current, 0)
        else:
            self.iter_current[0][0] = start + 1
        start = str(start)
        if padding != '':
            while len(start) < self.length:
                start = padding + start
        return start

    def iter(self, padding=''):
        """Iterate over the place numbers.
        The place numbers are prefixed with the padding.
        """
        for start, end in self.intervals:
            for i in range(start, end+1):
                i = str(i)
                if padding != '':
                    yield i.rjust(self.length, padding)
                else:
                    yield i

    def parse(self, text):
        self.errors = []
        for word in text.split(' '):
            if word == '':
                continue
            start_end = word.split("-")
            if len(start_end) == 2 and len(start_end[0]) != 0:
                # Add an interval
                start = int(start_end[0])
                end = int(start_end[1])
            else:
                start = int(word)
                if start < 0:
                    # Remove a single place
                    start = -start
                    for i, interval in enumerate(self.intervals):
                        if interval[0] > start: # before interval
                            continue
                        if interval[1] < start: # after interval
                            continue
                        if interval[0] == start:
                            if interval[1] == start:
                                python_pop(self.intervals, i)
                                break
                            interval[0] += 1    # 1-10 -1
                        elif interval[1] == start:
                            interval[1] -= 1    # 1-10 -10
                        else: # in the interval: so split it
                            self.intervals.insert(i+1, [start+1, interval[1]])
                            self.intervals[i][1] = start - 1
                        break
                        # No error on removing a non existent place
                    continue
                end = start
      
            if start > end:
                self.errors.append("Minimum must be before maximum: "
                                   + str(start) + '-' + str(end))
                continue
            do_insertion = True
            i = 0
            for interval in self.intervals:
                if min(end, interval[1]) >= max(start, interval[0]):
                    self.errors.append("Overlapping ranges "
                                       + str(start) + '-' + str(end)
                                       + ' and '
                                       + str(interval[0])
                                       + '-' + str(interval[1]))
                    do_insertion = False
                if interval[0] > start:
                    break
                i += 1
            if do_insertion:
                self.intervals.insert(i, [start, end])
        return ""

