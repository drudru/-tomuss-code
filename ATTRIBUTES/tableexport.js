// -*- coding: utf-8 -*-
/*
    TOMUSS: The Online Multi User Simple Spreadsheet
    Copyright (C) 2011-2013 Thierry EXCOFFIER, Universite Claude Bernard

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

function table_export()
{
  // Compute columns list to exports
  var cols = [] ;
  var cls = column_list_all() ;
  for(var column in cls)
    {
      column = columns[cls[column]] ;
      if ( column.is_empty )
	continue ;
      if ( column.author == '*' ) // ro_user
	continue ;
      cols.push(column) ;
    }
  // Compute attributes having at least one value != default
  var attrs = [] ;
  for(var c in column_attributes)
  {
    if ( column_attributes[c].computed || c == 'position' )
      continue ;
    for(var column in cols)
    {
      column = cols[column] ;
      if ( column[c] != column_attributes[c].default_value )
      {
	attrs.push(column_attributes[c]) ;
	break ;
      }
    }
  }

  var s = _("MSG_tableexport") + '<pre>\n' ;

  s += '<table border><tr>' ;
  for(var c in attrs)
    s += bs + '<small>' + attrs[c].name ;

  for(var column in cols)
    {
      column = cols[column] ;
      s += '<tr>' ;
      for(var c in attrs)
	  s += bs + attrs[c].formatter(column, column[attrs[c].name]) ;
      s += '\n</tr>' ;
    }
  s += '\n</table>\n' ;
  new_window(s, 'text/html') ;
}
