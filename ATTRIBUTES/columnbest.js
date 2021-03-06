// -*- coding: utf-8 -*-
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

function best_worst_value(value, column)
{
  if ( column.historical_comment )
    return '' ;
  
  column.need_update = true ;
  value = Number(value) ;
  if ( isNaN(value) )
    value = 0 ;
  if ( value < 0 )
    value = 0 ;
  else
    value = Math.floor(value) ;
  return value ;
}

function set_best(value, column)
{
  value = best_worst_value(value, column) ;
  if ( value !== '' )
    column.best_of = -value ;
  return value ;
}

function set_worst(value, column)
{
  value = best_worst_value(value, column) ;
  if ( value !== '' )
    column.mean_of = -value ;
  return value ;
}
