/*
    TOMUSS: The Online Multi User Simple Spreadsheet
    Copyright (C) 2008-2013 Thierry EXCOFFIER, Universite Claude Bernard

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

function test_read_only(value, column)
{
  alert_append("Résultat de calcul non modifiable") ;
}


/******************************************************************************
Cell Compute funtions.
The parameters are the column to update and the line of data.
******************************************************************************/


/*
http://pundit:8888/=ST-1480582-nScgSw4u5ZPhIuoL3HC3/2008/Test/UE-INF9999L
*/

function compute_average(data_col, line)
{
  var column = columns[data_col] ;

  if ( column.average_columns.length === 0 )
    {
      line[data_col].set_value('') ;
      return;
    }

  var nr_abj = 0 ;
  var nr_abi = 0 ;
  var nr_ppn = 0 ;
  var value ;
  var from ;
  var values = [] ;
  for(var c in column.average_columns)
    {
      c = column.average_columns[c] ;
      value = line[c].value ;
      from = columns[c] ;
      if ( from.real_weight === 0 )
	continue ;
      if ( value === '' ) 
	       value = from.empty_is ;
      switch(value)
	{
        case '':  line[data_col].set_value(NaN) ; return ;
	case abj_short:
	case abj: nr_abj++ ; continue ;
	case ppn_short:
	case ppn: nr_ppn++ ; continue ;
	case pre_short:
	case pre: values.push([1, from]) ; break ;
	case tnr_short:
	case tnr:
	case abi_short:
	case abi: values.push([0, from]) ; nr_abi++ ; break ;
	default:  
	  value = a_float(value) ;
	  if ( isNaN(value) )
	    {
	      line[data_col].set_value(NaN) ;
	      return ;
	    }
	  if ( from.real_weight_add )
	    {
	      values.push([(value - from.min) / (from.max - from.min), from]);
	    }
	  else
	    {
	      values.push([value, from]) ;
	      if (column.mean_of || column.best_of )
		{
		  line[data_col].set_value('???') ;
		  return ;
		}
	    }
	  break ;
	}
    }
  if ( nr_abj == column.average_columns.length )
    {
      line[data_col].set_value(abj) ;
      return ;
    }
  if ( column.best_of )
    {
      if ( column.best_of > 0 )
	{
	  values.sort() ;
	  values.reverse() ;
	  if ( values.length < column.best_of )
	    {
	      line[data_col].set_value(NaN) ;
	      return ;
	    }
	  values = values.slice(0, column.best_of) ;
	}
      else
	{
	  values.sort() ;
	  if ( values.length < -column.best_of )
	    {
	      line[data_col].set_value(NaN) ;
	      return ;
	    }
	  values = values.slice(0, values.length + column.best_of) ;
	}
    }
  if ( column.mean_of )
    {
      var i = -column.mean_of ;
      values.sort() ;
      values.reverse() ;
      if( i>0 && nr_abi )
	{
	  var n = Math.min(i, nr_abi) ;
	  i -= n ;
	  if ( values.length < n )
	    {
	      line[data_col].set_value(NaN) ;
	      return ;	      
	    }
	  values = values.slice(0, values.length - n) ;
	}
      if ( i > 0 )
	{
	  if ( values.length < i )
	    {
	      line[data_col].set_value(NaN) ;
	      return ;
	    }
	  values = values.slice(0, values.length - i) ;
	}
      if ( false )
	{
	  var s = '' ;
	  for(var ii in values)
	    s += ' ' + values[ii][0] ;
	  line[data_col].set_comment(s) ;
	}
    }
 
  var weight = 0, w ;
  var sum = 0 ;
  var sum2 = 0 ;
  var nr_sum = 0 ;
  for(var c in values)
    {
      c = values[c] ;
      from = c[1] ;
      value = c[0] ;
      if ( from.real_weight_add )
	{
	  w = from.real_weight ;
	  sum += w * value ;
	  weight += w ;
	}
      else
	{
	  sum2 += from.real_weight * value ;
	  nr_sum++ ;
	}
    }

  if ( nr_abj == column.average_columns.length )
    value = abj ;
  else if ( nr_abi == column.average_columns.length )
    value = abi ;
  else if ( weight !== 0 )
    {
      if ( sum2 <= 0 && nr_abi == values.length - nr_sum )
      {
	value = abi ;
      }
      else
      {
	sum = column.min + sum * (column.max - column.min) / weight + sum2 ;
	value = Number(sum.toPrecision(6)) ;
      }
      if ( column.round_by )
	{
	  value = Math.round(value / column.round_by) * column.round_by ;
	}
    }
  else if ( nr_sum == column.average_columns.length )
    value = sum2 ;
  else
    value = ppn ;

  line[data_col].set_value(value) ;
}
