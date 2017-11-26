// -*- coding: utf-8 -*-
/*
    TOMUSS: The Online Multi User Simple Spreadsheet
    Copyright (C) 2012-2017 Thierry EXCOFFIER, Universite Claude Bernard

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

function set_rounding(value, column, xattr)
{
  if ( column.historical_comment )
    return '' ;
  column.need_update = true ;
  if ( value === '' || isNaN(value) )
    value = rounding_default ;
  else
  {
    value = a_float(value) ;
    if ( value < 0 )
      value = -value ;
    if ( value < rounding_min )
      value = rounding_min ;
  }
  if ( xattr === false && value > rounding_avg && column.type == "Moy" )
     alert(_("ALERT_avg_rounding") + ' ' + rounding_avg) ;

  column.round_by = value ;

  var digit = Math.max(0, -Math.floor(Math.log(value)/Math.log(10))) ;

  column.do_rounding = function(v) {
    return v.toFixed ? do_round(v, value, column.table.rounding,
                                column.old_function).toFixed(digit) : v ; } ;

  return value ;
}

