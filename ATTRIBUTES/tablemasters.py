#!/bin/env python3
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

import re
from .. import utilities
from .. import configuration
from . import tabletabletitle

class TableMasters(tabletabletitle.TableTableTitle):
    name = 'masters'
    priority = -1 # Must compute 'i_am_the_teacher' before other attributes
    update_headers = 1
    # Side effect to update 'i_am_the_teacher' global variable
    formatter = '''
function(value)
{
if ( value instanceof Array )
  {
   teachers = value ;
   value = value.join(' ') ;
  }
else
  {
   teachers = value.split(/ +/) ;
  }
if ( teachers.length )
    i_am_the_teacher = myindex(teachers, my_identity) != -1 ;
else
    i_am_the_teacher = false ;
return value ;
}'''
    css = """
#menutop #t_table_attr_masters { font-size: 60% ; }
#menutop #t_table_attr_masters.empty {
  background-image: url('teacher.png');
}
#menutop DIV.tabs #t_table_attr_masters { font-size: 100% ; }
"""

    def encode(self, value):
        if isinstance(value, str):
            value = value.strip()
            if value == '':
                return []
            return re.split(' +', value.strip().lower())
        else:
            return value
    def check(self, value):
        value = self.encode(value)
        if hasattr(configuration, 'is_member_of'):
            for login in value:
                if not configuration.is_member_of(login, 'staff'):
                    return '_("ALERT_bad_login") + ' + utilities.js(login)
    def update(self, table, old_value, new_value, page):
        for login in new_value:
            if login not in old_value:
                table.master_of_update('+', login)
        for login in old_value:
            if login not in new_value:
                table.master_of_update('-', login)

    def default_value(self, table):
        ue = self.get_ue(table)
        if ue:
            return list(ue.responsables_login())
        return []
