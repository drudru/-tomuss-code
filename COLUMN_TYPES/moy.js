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

function test_read_only(value, column)
{
  alert_append("Résultat de calcul non modifiable") ;
}

function set_columns(value, column, xcolumn_attr)
{
  var cols = [] ;
  var weight = 0 ;
  var ok ;

  value = value.replace(/ *$/,'').replace(/^ */,'') ;

  if ( value === '' )
    {
      column.average_from = [] ;
      column.average_columns = [] ;
      column.need_update = true ;
      return value ;
    }


  column.average_from = value.split(/ +/) ;

  for(var i=0; i<column.average_from.length; i++)
    {
      ok = false ;
      for(var c in columns)
	if ( columns[c].title == column.average_from[i] )
	  {
	    cols.push(c) ;
	    weight += columns[c].real_weight ;
	    ok = true ;
	    break ;
	  }
      if ( ! ok )
	{
	  if ( xcolumn_attr )
	    // Wait the good value
	    setTimeout(function() {set_columns(value, column, xcolumn_attr)},
		       1000) ;
	  else
	    alert("Je ne connais pas le titre de colonne '"
		  + column.average_from[i]
		  + "' qui est utilisé dans la moyenne de la colonne "
		  + column.title) ;
	}
    }
  column.average_columns = cols ;
  column.average_weight = weight ;
  column.need_update = true ;
  if ( column.type == 'Nmbr' )
    column.max = column.average_columns.length ;

  return value ;
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
	case 'ABJ':
	case abj: nr_abj++ ; continue ;
	case 'PPN':
	case ppn: nr_ppn++ ; continue ;
	case 'PRE':
	case pre: values.push([1, from]) ; break ;
	case 'ABI':
	case abi: values.push([0, from]) ; nr_abi++ ; break ;
	default:  
	  value = a_float(value) ;
	  if ( isNaN(value) )
	    {
	      line[data_col].set_value(NaN) ;
	      return ;
	    }
	  if ( from.real_weight_add )
	    values.push([(value - from.min) / from.max, from,
			 line[c].weight]) ;
	  else
	    values.push([value, from]) ;
	  break ;
	}
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
	  nr_abi -= n ;
	  i -= n ;
	  if ( values.length < n )
	    {
	      line[data_col].set_value(NaN) ;
	      return ;	      
	    }
	  values = values.slice(0, values.length - n) ;
	}
      // i -= nr_ppn + nr_abj ; // Uncomment to see ABJ as a bad rank
      if ( i > 0 )
	{
	  if ( values.length < i )
	    {
	      line[data_col].set_value(NaN) ;
	      return ;
	    }
	  values = values.slice(0, values.length - i) ;
	}
      var s = '' ;
      for(var i in values)
	s += ' ' + values[i][0] ;
      line[data_col].set_comment(s) ;
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
	  if ( from.real_weight === '?' )
	    w = c[2] ;
	  else
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
      sum = column.min + sum * (column.max - column.min) / weight + sum2 ;
      value = Number(sum.toPrecision(6)) ;
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
  line[data_col].set_weight(weight) ;
}
