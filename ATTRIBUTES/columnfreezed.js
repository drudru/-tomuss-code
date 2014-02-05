// -*- coding: utf-8 -*-
/*
    TOMUSS: The Online Multi User Simple Spreadsheet
    Copyright (C) 2011 Thierry EXCOFFIER, Universite Claude Bernard

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

function freeze_column(the_id)
{
  var column = the_current_cell.column ;
  if ( column.freezed == 'F' )
    column.freezed = '' ;
  else
    column.freezed = 'F' ;
  table_fill(false, true) ;
  the_current_cell.do_update_column_headers = true ;

  var p = '' ;
  for(var c in columns)
    if ( columns[c].freezed == 'F' )
      p += columns[c].the_id + ':F=' ;
  change_option('freezeds', p) ;
}

