// -*- coding: utf-8 -*-
/*
    TOMUSS: The Online Multi User Simple Spreadsheet
    Copyright (C) 2008-2011 Thierry EXCOFFIER, Universite Claude Bernard

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

function set_type(value, column, xcolumn_attr)
{
  var checked = type_title_to_type(value) ;

  if ( column.real_type
       && column.real_type.cell_compute !== undefined
       && checked.cell_compute === undefined
       && the_current_cell.line[column.data_col]._save !== undefined
       )
	{
	  // Restore uncomputed values. XXX some may missing if never in client
	  for(var line in lines)
	    lines[line][column.data_col].restore() ;
	  table_fill(false, false, true) ;
	}
  if ( column.real_type
       && column.real_type.cell_compute === undefined
       && checked.cell_compute !== undefined )
    {
      /* Save values */
      for(var line in lines)
	lines[line][column.data_col].save() ;
    }
  column.real_type = checked ;
  column.need_update = true ;

  if ( xcolumn_attr === false && column.columns === '' )
    {
	// Only here on local user interaction
	var use = _('B_' + column.real_type.title).split("(")[1] ;
	if ( use == 'ID)' )
	    column_attr_set(column, 'columns', 'ID') ;
    }

  return value ;
}

