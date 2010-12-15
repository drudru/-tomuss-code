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

function compute_column_stat(column)
{
  var data_col = column.data_col ;
  var max = lines[0][data_col].value ;
  var v, sum, nr ;

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

function set_test_note(v, column)
{
  column.min = 0 ;
  column.max = 20 ;

  if ( v === '' )   // Should never be here except for old tables
    v = '[0;20]' ;
  
  value = v.replace(/;/g, ' ').replace(/\[/g, ' ').replace(/]/g, ' ').replace(/^ */, '').replace(/ *$/,'').split(/  */) ;

if ( value.length != 2 )
  {
    alert_append('Pour la colonne "' + column.title + '(' + column.type + ')".\nVous devez indiquer la note minimum et maximum\nsous la forme : [0;20]') ;
    return column.minmax ;
  }

if ( Number(value[0]) > Number(value[value.length-1]) )
    {
      alert_append('La note minimum doit être plus petite que la note maximum') ;
      return column.minmax ;
    }

column.need_update = true ;
column.min = a_float(value[0]) ;
if ( isNaN(column.min) )
  column.min = 0 ;

column.max = a_float(value[1]) ;
if ( isNaN(column.max) )
  {
    compute_column_stat(column) ;
    column.max = column.computed_max ;
  }
value = '[' + column.min + ';' + column.max + ']' ;

column.need_update = true ;

return value ;
}

/******************************************************************************
Check the 'weight' of a column.
******************************************************************************/

function set_weight(value, column)
{
  var v = a_float(value) ;

  column.real_weight_add = true ; // Pondered average

  if ( value === '?' && column.type == 'Moy' ) // XXX Only Moy ?
    {
      value = v = '?' ;
    }
  else if ( isNaN(v) )
    {
      v = 0 ;
      value = '0' ;
    }
  else if ( value === '' )
    {
      v = 1 ;
      value = '1' ;
    }
  else
    {
      if ( value.substr(0,1) == '+' || value.substr(0,1) == '-' )
	column.real_weight_add = false ;
    }

  column.real_weight = v ;
  column.need_update = true ;

  return value ;
}


function test_note(value, column)
{
  var v = value.toUpperCase() ;
  var vv = test_prst(v, column) ;
  if ( vv !== '' && vv !== pre )
    return vv ;
  if ( v === 'N' || v === ppn )
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

function note_format(c)
{
  if ( c.toFixed )
    return tofixed(c) ;
  else
    return c ;
}

