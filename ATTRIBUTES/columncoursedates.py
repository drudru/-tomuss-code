#!/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2011 Thierry EXCOFFIER, Universite Claude Bernard
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

from column import ColumnAttr
import time

class ColumnCourseDates(ColumnAttr):
    name = 'course_dates'
    def check(self, dates):
        if dates == '':
            return
        dates = dates.split(' ')
        for date in dates:
            date = date.strip('MA')
            mktime = time.mktime(time.strptime(date, '%Y%m%d'))

    display_table = 1
    formatter = 'course_dates_formatter'
    check_and_set = 'set_course_dates'
    tip = """<b>Dates des enseignements</b>.<br>
    Les dates sont indiquées sous la forme JJ/MM/AAAA<br>
    suivi éventuellement de M ou A pour Matin ou Après-midi.<br>
    Les ABINJ concernant ces dates sont soulignés.
    """
    css = """
#menutop DIV.tabs #t_column_course_dates { width: 74% }

"""
