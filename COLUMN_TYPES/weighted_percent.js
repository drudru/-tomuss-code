/*
    TOMUSS: The Online Multi User Simple Spreadsheet
    Copyright (C) 2012 Thierry EXCOFFIER, Universite Claude Bernard

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

function compute_weighted_percent_(data_col, line, filter)
{
  var column = columns[data_col] ;
  if ( column.real_type.cell_compute === undefined )
  {
    if ( filter(line[data_col]) )
      return 1. ;
    else
      return 0. ;
  }
  var sum = 0, sum_weight = 0, weight ;
  for(var col in column.average_columns)
  {
    col = column.average_columns[col] ;
    
    if ( ! columns[col].real_weight_add )
      continue ;

    weight = columns[col].real_weight ;
    sum += weight * compute_weighted_percent_(col, line, filter);
    sum_weight += weight ;
  }
  if ( sum_weight == 0 )
    return 0. ;
  return sum / sum_weight ;
}

function compute_weighted_percent(data_col, line)
{
  var column = columns[data_col] ;

  if ( column.average_columns.length !== 1 )
    {
      line[data_col].set_value('') ;
      return;
    }
  var v = column.min + (column.max - column.min) *
    compute_weighted_percent_(column.average_columns[0],
			      line, column.nmbr_filter) ;

  if ( column.round_by )
    v = Math.round(v / column.round_by) * column.round_by ;

  line[data_col].set_value(v) ;
}
