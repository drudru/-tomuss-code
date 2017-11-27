// -*- coding: utf-8 -*-
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

function set_test_note(v, column, xattr)
{
  column.min = 0 ;
  column.max = 20 ;
  
  if ( v === '' )   // Should never be here except for old tables
    v = '[0;20]' ;
  
  value = v.replace(/;/g, ' ').replace(/\[/g, ' ').replace(/]/g, ' ').replace(/^ */, '').replace(/ *$/,'').split(/  */) ;

if ( value.length != 2 )
  {
    alert_append(_("ALERT_columnminmax_syntax")
		 + column.title + '(' + column.type + ')"'
		) ;
    return column.minmax ;
  }

if ( a_float(value[0]) >= a_float(value[value.length-1]) )
  {
    alert_append(_("ALERT_columnminmax_order") + column.title) ;
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

if ( xattr === false
     && column.type == 'Nmbr'
     && column.max < column.average_columns.length
     && column.rounding == 1
      )
      {
      column_attr_set(column, 'rounding', rounding_default) ;
      the_current_cell.update_headers() ;
      the_current_cell.do_update_column_headers = true ;
      }
column.need_update = true ;

return value ;
}
