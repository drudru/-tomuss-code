/*
    TOMUSS: The Online Multi User Simple Spreadsheet
    Copyright (C) 2008-2011 Thierry EXCOFFIER, Universite Claude Bernard

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

function compute_column_stat(column)
{
  var data_col = column.data_col ;
  var max = -1e40 ;
  var v, sum, sum2, nr ;

  sum = 0 ;
  sum2 = 0 ;
  nr = 0 ;
  for(var lin in lines)
    {
      v = lines[lin][data_col].value ;
      if ( v === '' )
	v = column.empty_is ;
      if ( v > max )
	max = v ;
      v = a_float(v) ;
      if ( isNaN(v) )
	continue ;
      nr++ ;
      sum += v ;
      sum2 += v*v ;
    }
  v = 1 ;
  while ( v < max )
    {
      v *= 2 ;         // 2
      if ( v >= max )
	break ;
      v *= 2 ;         // 4
      if ( v >= max )
	break ;
      v = Math.round((v/4) * 5) ;  // 5
      if ( v >= max )
	break ;
      v *= 2 ;         // 10
    }
  
  column.computed_max = v ;
  if ( nr )
    {
      column.computed_avg = sum / nr ;
      column.computed_var = Math.pow(sum2 / nr - sum*sum/(nr*nr), 0.5) ;
    }
  else
    {
      column.computed_avg = 0 ;
      column.computed_var = 0 ;
    }
}


function test_note(value, column)
{
  var v = value.toUpperCase() ;
  var vv = test_prst(v, column) ;
  if ( vv !== '' && vv !== pre )
    return vv ;
  if ( v === 'N' || v == 'PP' || v === ppn )
    return ppn ;
  if ( v === '' )
    return v ;
  v = a_float(v) ;
  if ( column.round_by )
    {
      v = Math.round(v / column.round_by) * column.round_by ;
    }
  if ( isNaN(v) || v < column.min || v > column.max )
    {
      alert_append(value
		   + " n'est pas une note valide car non dans l'intervalle "
		   + column.minmax + "\n" +
		   "Ni I(" + abi + "), J(" + abj + "), N(" + ppn
		   + ": ne peut pas noter)") ;
      return ;
    }

  return v ;
}

function note_format(c, column)
{
    if ( c.toFixed && ( !column.round_by || column.round_by < 1 ) )
	  return tofixed(c) ;
    return c ;
}

