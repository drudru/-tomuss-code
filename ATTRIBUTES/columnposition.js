// -*- coding: utf-8; mode: Java; c-basic-offset: 2; tab-width: 8; -*-
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

function left_column(column)
{
  var cls = column_list(0, columns.length) ;

  var i = myindex(cls, column) ;

  if ( i == 1 )
    column.position = cls[0].position - 1 ;
  else if ( i !== 0 )
    column.position = (cls[i-1].position + cls[i-2].position) / 2 ;

  table_fill(false, true) ;
  column_attr_set(column, 'position', column.position,
		  document.getElementById("column_attr_position"), true) ;
}

function right_column(column)
{
  var cls = column_list(0, columns.length) ;

  var i = myindex(cls, column) ;

  if ( i == cls.length - 2 )
    column.position = cls[i+1].position + 1 ;
  else if ( i != cls.length - 1 )
    column.position = (cls[i+1].position + cls[i+2].position) / 2 ;

  table_fill(false, true) ;
  column_attr_set(column, 'position', column.position,
		  document.getElementById("column_attr_position"), true) ;
}

function do_move_column_right()
{
  if ( periodic_work_in_queue(table_fill_do) )
    return ; // XXX Hide a bug (moving column quickly lost it sometimes)

  var column = the_current_cell.column ;
  the_current_cell.cursor_right() ;
  right_column(column) ;
  setTimeout("the_current_cell.update()", 100);

  column_update_option('position') ;
}

function do_move_column_left()
{
  if ( periodic_work_in_queue(table_fill_do) )
    return ; // XXX Hide a bug (moving column quickly lost it sometimes)

  var column = the_current_cell.column ;
  the_current_cell.cursor_left() ;
  left_column(column) ;
  setTimeout("the_current_cell.update()", 100);

  column_update_option('position') ;
}


