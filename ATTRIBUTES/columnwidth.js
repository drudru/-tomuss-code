// -*- coding: utf-8 -*-
/*
  TOMUSS: The Online Multi User Simple Spreadsheet
  Copyright (C) 2011-2013 Thierry EXCOFFIER, Universite Claude Bernard

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

function bigger_column()
{
  var column = the_current_cell.column ;
  column.width += 1 ;
  table_header_fill() ;
  setTimeout('update_table_size()', 200) ;
  column_attr_set(column, 'width', column.width
		  , document.getElementById("column_attr_width"), true) ;
  column_update_option('width', column.width) ;
}

function smaller_column()
{
  var column = the_current_cell.column ;
  if ( column.width > 1 )
    {
      column.width -= 1 ;
      table_header_fill() ;
      setTimeout('update_table_size()', 200) ;
      column_attr_set(column, 'width', column.width,
		      document.getElementById("column_attr_width"), true) ;
      column_update_option('width', column.width) ;
    }
}

