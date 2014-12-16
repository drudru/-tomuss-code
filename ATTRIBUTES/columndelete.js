// -*- coding: utf-8 -*-
/*
  TOMUSS: The Online Multi User Simple Spreadsheet
  Copyright (C) 2011-2012 Thierry EXCOFFIER, Universite Claude Bernard

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

  Contact: Thierry.EXCOFFIER@bat710.univ-lyon1.fr
*/

function column_delete()
{
  var column = the_current_cell.column ;
  if ( column.author == '*' && column.data_col < 6 )
    {
      Alert("ALERT_columndelete_forbiden") ;
      return ;
    }
  if ( ! column_change_allowed(column) )
    {
	alert(_("ALERT_columndelete_not_master_before") + column.author +
	      _("ALERT_columndelete_not_master_after") + teachers) ;
      return ;
    }

  var empty = column_empty_of_user_cells(column.data_col) ;
  if ( column.real_type.cell_is_modifiable && ! empty )
    {
      Alert("ALERT_columndelete_not_empty") ;
      return ;
    }
  var c = column_used_in_average(column.title) ;
  if ( c )
    {
      Alert("ALERT_columndelete_used", c) ;
      return ;
    }
  if ( column.is_empty )
    {
      Alert("ALERT_columndelete_void") ;
      return ;
    }
  if ( ! empty )
    if (!confirm(_("ALERT_columndelete_confirm") + column.title))
      return ;

  // The column name can be used in disabled formulas
  // Remove the column name to avoid any future problem
  for(var data_col in columns)
  {
    for(var use in columns[data_col].average_from)
    {
      if ( columns[data_col].average_from[use] == column.title)
      {
  	column_attr_set(columns[data_col], 'columns',
			(' '+columns[data_col].columns+' ').replace(
			  ' '+column.title+' ', ' ').trim()
		       ) ;
      }
    }
  }
  append_image(undefined, 'column_delete/' + column.the_id) ;
  Xcolumn_delete(' ', column.the_id) ;
  the_current_cell.update_headers() ;
}
