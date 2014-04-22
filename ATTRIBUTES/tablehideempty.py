#!/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2013 Thierry EXCOFFIER, Universite Claude Bernard
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

class HideEmpty(TableModifiable):
    name = 'hide_empty'
    default_value = 0
    gui_display = "GUI_select"
    need_authorization = 0
    formatter = '''function(value)
{
  if ( value == table_attr.hide_empty )
     return Number(value) ;

  if ( ! table_change_allowed() || ! table_attr.modifiable )
    {
      if ( value != 0 )
        change_option('hide_empty', '1') ;
      else
        change_option('hide_empty', '0') ;
    }

  update_filtered_lines() ;
  table_fill(true) ;
  return Number(value) ;
}'''
    
    def update(self, table, old_value, new_value, page):
        pass

    css = "#menutop #t_table_attr_hide_empty { width: 100% }"


