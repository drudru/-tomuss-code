/*
    TOMUSS: The Online Multi User Simple Spreadsheet
    Copyright (C) 2008,2010 Thierry EXCOFFIER, Universite Claude Bernard

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

function compute_cow(data_col, line)
{
  var column = columns[data_col] ;

  if ( column.average_columns.length != 1 )
    return ;
  if ( line[data_col].author !== '' )
    return ;

  c = column.average_columns[0] ;

  var value = line[c].value ;

  if ( value === '' )
    value = columns[c].empty_is ;

  line[data_col].set_value(value) ;
}

function get_original_cow_column()
{
  var column = the_current_cell.column ;
  while(column.type == 'COW')
    {
      column = columns[column.average_columns[0]] ;
      if ( column === undefined )
	return ;
    }
  return column ;
}


function toggle_cow(value)
{
  var column = get_original_cow_column() ;
  if ( column )
    return column.real_type.ondoubleclick(value) ;
  else
    return value ;
}

function test_cow(value, column)
{
  var column = get_original_cow_column() ;
  if ( column )
    return column.real_type.cell_test(value, column) ;
  else
    return value ;
}
