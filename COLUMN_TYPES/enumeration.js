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

// Search the best approximation
function test_enumeration(value, column)
{
  if (value === '')
    return '' ;

  for(var v in column.possible_values)
    if ( column.possible_values[v] == value )
      return column.possible_values[v] ;

  for(var v in column.possible_values)
    if ( column.possible_values[v].substr(0,value.length) == value )
      return column.possible_values[v] ;

  for(var v in column.possible_values)
    if ( column.possible_values[v].substr(0,value.length).toUpperCase()
	 == value.toUpperCase() )
      return column.possible_values[v] ;

  return '' ;
}


function toggle_enumeration(value, column)
{
  return toggle_PA(test_enumeration, value, column.possible_values, column) ;
}

