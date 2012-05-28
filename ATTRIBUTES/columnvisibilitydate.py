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

from column import ColumnAttr
import time

class ColumnVisibilityDate(ColumnAttr):
    name = 'visibility_date'
    def check(self, date):
        if date == '':
            return
        mktime = time.mktime(time.strptime(date, '%Y%m%d'))
        if mktime > time.time() + 86400*31:
            return '''_("ALERT_date_in_future_1")+"%d"+
_("ALERT_date_in_future_2")
''' % int((time.mktime(time.strptime(date, '%Y%m%d')) - time.time())/86400)
        if mktime < time.time() - 86400*31:
            return '_("ALERT_date_in_past")'
    formatter = '''
function(column, value)
{
  if ( value === '' ) return '' ;
  return column.visibility_date.substr(6,2) + '/' +
	 column.visibility_date.substr(4,2) + '/' +
	 column.visibility_date.substr(0,4) ;
}'''
    check_and_set = 'set_visibility_date'
    css = """
#menutop #t_column_visibility_date {
  background-image: url('eye.png');
  background-position: right ;
  background-repeat: no-repeat ;
  width: 5.5em ;
}

#menutop DIV.tabs #t_column_visibility_date { width: 74% }

"""
