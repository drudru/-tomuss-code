/*
    TOMUSS: The Online Multi User Simple Spreadsheet
    Copyright (C) 2013 Thierry EXCOFFIER, Universite Claude Bernard

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

function compute_diff_date(data_col, line)
{
  var column = columns[data_col] ;

  if ( column.average_columns.length !== 2 )
    {
      line[data_col].set_value('') ;
      return;
    }

  var div = Number(column.comment.split('/')[1]) ;
  if ( isNaN(div) )
    div = 1 ;  

  var values = [] ;
  for(var c in column.average_columns)
    {
      c = column.average_columns[c] ;
      value = line[c].value ;
      from = columns[c] ;
      if ( value === '' ) 
	value = from.empty_is ;
      values.push(get_date(value)) ;
    }
  try {
    line[data_col].set_value(
      (values[1].getTime() - values[0].getTime())/(div*1000*86400)) ;
  }
  catch(e) { line[data_col].set_value('') ; }
}
