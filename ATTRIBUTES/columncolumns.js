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
      if ( column.type == 'Nmbr' )
	{
	  column.minmax = '[0;1]' ;
	  column.min = 0 ;
	  column.max = 1 ;
	}
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
	    if ( search_column_in_columns(columns[c], column.title) )
	    {
	      ok = undefined ;
	      break ;
	    }
	    ok = true ;
	    break ;
	  }
      if ( ! ok )
	{
	  if ( xcolumn_attr === true )
	    {
	      // Wait the good value
	      // Next time 'xcolumn_attr' will be '1' in place of 'true'
	      setTimeout(function() {
		set_columns(value, column, 1);
		attr_update_user_interface(column_attributes['columns'],
					   column) ;
	      }, 1000) ;
	      column.average_columns = [] ;
	      return value ;
	    }
	  else
	    {
	      if ( column_modifiable_attr('columns', column) )
		if ( ok === undefined )
		  alert_append(_("ALERT_columns_recursive")
			       + column.title
			       + _("ALERT_columns_unknown_used_by")
			       + column.average_from[i]
			       + _("ALERT_columns_unsaved")
			     ) ;
	      else
		  alert_append(_("ALERT_columns_unknown_title")
			       + column.average_from[i]
			       + _("ALERT_columns_unknown_used_by")
			       + column.title
			       + _("ALERT_columns_unsaved")
			     ) ;
	      column.average_columns = [] ;
	      return null ; // Do not save, but leaves user input unchanged
	    }
	}
    }
  column.average_columns = cols ;
  column.average_weight = weight ;
  column.need_update = true ;
  if ( xcolumn_attr === false
       && column.type == 'Nmbr'
       && column.max != column.average_columns.length)
      {
       column_attr_set(column, 'minmax',
                       '[0;' + column.average_columns.length + ']');
       the_current_cell.update_headers() ;
       the_current_cell.do_update_column_headers = true ;
      }

  return value ;
}
