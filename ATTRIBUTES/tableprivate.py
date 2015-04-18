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

from .tablemodifiable import TableModifiable

class TablePrivate(TableModifiable):
    formatter = r'''
function(value)
{
  if ( (table_attr.masters.length == 0 || ! i_am_the_teacher) && value == 1
       && myindex(table_attr.managers, my_identity) == -1
       && ! i_am_root )
    {
      Alert("ALERT_colmunprivate") ;
      return ;
    }
  return value ;
}'''

    name = 'private'
    default_value = 0
    gui_display = "GUI_select"

    def update(self, table, old_value, new_value, page):
        pass
