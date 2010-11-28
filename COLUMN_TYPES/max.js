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

function compute_max_real(data_col, line)
{
  var column = columns[data_col] ;
  var the_max ;

  if ( column.average_columns.length === 0 )
    {
      line[data_col].set_value('') ;
      return;
    }

  the_max = -1 ;
  for(var c in column.average_columns)
    {
      c = column.average_columns[c] ;
      value = line[c].value ;
      from = columns[c] ;
      if ( value === '' ) 
	value = from.empty_is ;
      if ( value === '' )
	continue ;
      value = a_float(value) ;
      value = (value - from.min) / from.max ;
      if ( value > the_max )
	the_max = value ;
    }

  if ( the_max >= 0 )
    line[data_col].set_value(the_max * (column.max - column.min) + column.min);
  else
    {
      // No good number
      line[data_col].set_value('') ;
    }

}
