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

function test_prst(value, column)
{
  var v = value.toUpperCase() ;
  if ( v === abi_char || v === abi_short || v === abi )
    return abi ;
  if ( v === abj_char || v === abj_short || v === abj )
    return abj ;
  if ( v === pre_char || v === pre_short || v === pre )
    return pre ;
  return '' ;
}

function prst_completions(value, column)
{
  column.possible_values = [pre, abi, abj, ''] ;
  return completions_enumeration(value, column) ;
}

function toggle_PA(test, v, values, column)
{
  v = test(v, column) ;
  
  /* Cycle through values */
  var i = myindex(values, v) ;
  if ( i == -1 )
    i = values.length - 1 ;
  i = (i+1) % values.length ;

  return values[i] ;
}

function toggle_prst(value)
{
  return toggle_PA(test_prst, value, [pre, abi, abj]) ;
}

function prst_format_suivi()
{
  return enumeration_suivi(['', pre, abi, abj]) ;
}
