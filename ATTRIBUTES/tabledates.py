#!/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2008-2011 Thierry EXCOFFIER, Universite Claude Bernard
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#    Contact: Thierry.EXCOFFIER@bat710.univ-lyon1.fr

import time
from ..column import TableAttr
from .. import configuration

class TableDates(TableAttr):
    name = 'dates'
    default_value = [0,2000000000]
    formatter = 'date_formatter'
    def encode(self, value):
        if isinstance(value, str):
            dates = value.split(' ')
            first_day = configuration.date_to_time(dates[0])
            last_day = configuration.date_to_time(dates[1])
            return [first_day, last_day]
        else:
            return value

    def decode(self, value):
        return configuration.tuple_to_date(time.localtime(value[0])) + \
               configuration.tuple_to_date(time.localtime(value[1]))

    def check(self, value):
        value = self.encode(value)
        if value[0] > value[1]:
            return '_("ALERT_first_before_second")'
