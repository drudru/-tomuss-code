// -*- coding: utf-8 -*-
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

function the_greentext_filter(c, column)
{
  return c.value > column.color_greentext ;
}

function set_greentext(value, column)
{
  if ( value === undefined )
    value = '' ;
  if ( value === '' )
    {
      column.color_greentext_filter = returns_false ;
    }
  else if ( value === 'NaN' )
    {
      column.color_greentext_filter = the_greentext_filter ;
      var stats = compute_histogram(column.data_col) ;
      column.color_greentext = stats.average() + stats.standard_deviation()/2 ;
    }
  else if ( isNaN(value) )
    {
      column.color_greentext_filter = compile_filter_generic(value) ;
    }
  else
    {
      value = Number(value) ;
      column.color_greentext_filter = the_greentext_filter ;
      column.color_greentext = value ;
    }
  column_update_option('greentext', value) ;

  return value ;
}
