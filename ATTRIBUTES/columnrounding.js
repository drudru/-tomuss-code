// -*- coding: utf-8 -*-
/*
    TOMUSS: The Online Multi User Simple Spreadsheet
    Copyright (C) 2012-2014 Thierry EXCOFFIER, Universite Claude Bernard

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

function set_rounding(value, column)
{
  if ( table_attr.rounding <= 1 )
    column.do_rounding = function(v) { return v.toFixed ? tofixed(v) : v ; } ;
  else
    column.do_rounding = function(v) { return v.toFixed ? v.toFixed(2) : v ;} ;
  
  if ( column.historical_comment )
    return '' ;
  if ( isNaN(value) )
  {
    return '' ;
  }
  
  column.need_update = true ;
  if ( value === '' )
  {
    column.round_by = undefined ;
    return '' ;
  }
  value = Number(value) ;
  if ( value < 0 )
    value = -value ;
  if ( value < 0.001 )
    value = 0.001 ;
  column.round_by = value ;

  var digit = Math.max(0, -Math.floor(Math.log(value)/Math.log(10))) ;

  if ( table_attr.rounding <= 1 )
    // 'floor' because 9.999 must be displayed as 9.99 an not 10
    column.do_rounding = function(v) {
      return v.toFixed ? (Math.floor(v/value+0.0000001)*value).toFixed(digit)
	: v ; } ;
  else
    column.do_rounding = function(v) {
      return v.toFixed ? (Math.round(v/value)*value).toFixed(digit) : v ; } ;
    
  return value ;
}

