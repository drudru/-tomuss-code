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

/* 'Nmbr' type is used in 'columncolumns.js' */

function compute_nmbr(data_col, line)
{
  var sum, tmp, cell ;
  var column = columns[data_col] ;

  if ( column.average_columns.length === 0 )
    {
      line[data_col].set_value(0) ;
      return;
    }

  sum = 0 ;
  for(var c in column.average_columns)
    {
      c = column.average_columns[c] ;
      cell = line[c] ;
      if ( cell.is_empty() )
	{
	  tmp = cell.value ;
	  cell.value = columns[c].empty_is ;
	  if ( column.nmbr_filter(cell) )
	    sum++ ;
	  cell.value = tmp ;
	}
      else
	{
	  if ( column.nmbr_filter(cell) )
	    sum++ ;
	}
    }
  line[data_col].set_value(sum) ;
}
