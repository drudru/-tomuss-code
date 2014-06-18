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

var column_get_option_running ; // true on table loading

// The value is the value that will be saved in the current column attribute
// because it is not yet fully stored.
function column_update_option(attr, value)
{
  if ( column_get_option_running )
    return ;
  if ( the_current_cell === undefined )
    return ; // Not in the table editor
  var column, attr_value, save, p = '' ;
  for(var data_col in columns)
    {
      column = columns[data_col] ;
      if ( value === undefined || data_col != the_current_cell.data_col )
	attr_value = column[attr] ;
      else
	attr_value = value ; // Not yet saved

      if ( column_attributes[attr] === undefined )
	{
	  // For column filters
	  save = attr_value !== '' ;
	}
      else
	{
	  save = (! column_change_allowed(column)
		  && attr_value != column_attributes[attr].default_value
		  ) ;
	}
      if ( save )
	p += column.the_id + ':' + encode_uri_option(attr_value) + '=' ;
    }
  change_option(attr + 's', p) ;
}

function column_get_option(attr, hook, alternate_option_name)
{
  if ( hook === undefined )
    hook = function(value, column) { return value ; } ;
  
  var h = get_option(attr + 's', '') ;
  if ( h === '' )
    h = get_option(alternate_option_name + 's', '') ; // Compatibility
  h = h.split('=') ;
  for(var i in h)
  {
      var j = h[i].split(':') ;
      if ( j.length != 2 )
	break ;
      var data_col = data_col_from_col_id(j[0]) ;
      if ( data_col === undefined )
	if ( columns[Number(j[0])] )
	  data_col = Number(j[0]) ;  // For compatibility with old bookmarks
      if ( data_col !== undefined )
	columns[data_col][attr] = hook(decode_uri_option(j[1]),
				       columns[data_col]) ;
    }
}

function table_bookmark(value)
{
  change_option('foobar', '') ;
  return Number(value) ;
}

function __d(txt)
{
  debug_window.document.write(txt) ;
}

// Called from runlog in lib.js

function get_all_options()
{
  var h ;
  if ( window.location.pathname.search('=debug=') != -1 )
    {
      _d = __d ;
      debug_window = window_open('debug') ;
      debug_window.document.open('text/plain') ;
    }

  _d('start get_all_options\n') ;

  if ( window.location.pathname.search('=user=') != -1 )
    {
      root = [] ;
      i_am_root = false ;
    }

  if ( window.location.pathname.search('=tipfixed=') != -1 )
    tip_fixed = 1 ;

  if ( window.location.pathname.search('=display_tips=') != -1 )
    display_tips = false ;

  table_attr.nr_lines = Number(get_option('nr_lines', table_attr.nr_lines)) ;
  table_attr.nr_columns=Number(get_option('nr_cols', table_attr.nr_columns));
  table_attr.hide_empty=Number(get_option('hide_empty',table_attr.hide_empty));
  column_offset = Number(get_option('column_offset', column_offset)) ;
  
  h = get_option('hidden', '').split('=') ;
  for(var i in h)
    if ( columns[h[i]] )
      columns[h[i]].hidden = 1 ;

  h = get_option('sort', '') ;
  if ( h !== '' )
    {
      h = h.split('=') ;
      sort_columns = [] ;
      for(var i in h)
	{
	  var x = Number(h[i]) ;
	  if ( x >= 0 )
	    {
	      sort_columns.push(columns[x]) ;
	      columns[x].dir = 1 ;
	    }
	  else
	    {
	      sort_columns.push(columns[-x-1]) ;
	      columns[-x-1].dir = -1 ;
	    }
	}
    }
  
  h = get_option('columns_filter', '', true) ;
  if ( h !== '' )
    set_columns_filter(decode_uri_option(h)) ;

  h = get_option('line_filter', '', true) ;
  if ( h !== '' )
    {
      h = decode_uri_option(h) ;
      var cf = document.getElementById('linefilter') ;
      cf.className = '' ;
      cf.value = h ;
      line_filter_value = h ;
      line_filter = compile_filter_generic(h) ;
    }

  h = get_option('full_filter', '', true) ;
  if ( h !== '' )
    {
      h = decode_uri_option(h) ;
      var ff = document.getElementById('fullfilter') ;
      ff.className = '' ;
      ff.value = h ;
      full_filter_value = h ;
      full_filter = compile_filter_generic(h) ;
    }

  column_get_option('red') ;
  column_get_option('green') ;
  column_get_option('redtext') ;
  column_get_option('greentext') ;
  column_get_option('position') ;
  column_get_option('freezed',undefined,
		    'frozen' // old option name
		   ) ;
  column_get_option('filter',
		    function(value, column)
		    {
		      init_column(column) ;
		      return set_filter_generic(value, column) ;
		    }) ;

  update_filters() ;

  _d('end get_all_options\n') ;
}
