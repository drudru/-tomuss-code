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

function table_bookmark()
{
  var p ;

  var s = url + '/=' + ticket + '/' + year + '/' + semester + '/' + ue +
    '/=nr_cols=' + table_attr.nr_columns +
    '/=nr_lines=' + table_attr.nr_lines
    ;
 
  p = '' ;
  for(var c in columns)
    if ( columns[c].hidden && columns[c].freezed != 'C' )
      p += c + '=' ;
  if ( p !== '' )
    s += '/=hidden=' + p ;

  p = '' ;
  for(var c in columns)
    if ( columns[c].filter )
      p += c + ':' + encode_uri_option(columns[c].filter) + '=' ;
  if ( p !== '' )
    s += '/=filters=' + p ;

  p = '' ;
  for(var c in columns)
    if ( columns[c].freezed == 'F' )
      p += c + '=' ;
  if ( p !== '' )
    s += '/=frozen=' + p ;

  s += '/=sort=' ;
  for(var c in sort_columns)
    if ( sort_columns[c].dir > 0 )
      s += sort_columns[c].data_col + '=' ;
    else
      s += (-sort_columns[c].data_col - 1) + '=' ;

  p = '' ;
  for(var data_col in columns)
    if (!columns[data_col].is_empty && columns[data_col].position != data_col )
      p += columns[data_col].the_id + ':' + columns[data_col].position + '=' ;
  if ( p !== '' )
    s += '/=positions=' + p ;

  if ( tip_fixed )
    s += '/=tipfixed=' ;
  if ( ! display_tips)
    s += '/=display_tips=' ;
  if ( columns_filter_value !== '' )
    s += '/=columns_filter=' + encode_uri_option(columns_filter_value) ;
  if ( line_filter_value !== '' )
    s += '/=line_filter=' + encode_uri_option(line_filter_value) ;
  if ( full_filter_value !== '' )
    s += '/=full_filter=' + encode_uri_option(full_filter_value) ;
  if ( column_offset !== 0 )
    s += '/=column_offset=' + column_offset ;

  window.location = s ;
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
      debug_window = window_open() ;
      debug_window.document.open('text/plain') ;
    }

  _d('start get_all_options\n') ;

  if ( window.location.pathname.search('=tipfixed=') != -1 )
    tip_fixed = 1 ;

  if ( window.location.pathname.search('=display_tips=') != -1 )
    display_tips = false ;

  table_attr.nr_lines = Number(get_option('nr_lines', table_attr.nr_lines)) ;
  table_attr.nr_columns = Number(get_option('nr_cols', table_attr.nr_columns));
  column_offset = Number(get_option('column_offset', column_offset)) ;
  h = get_option('hidden', '').split('=') ;
  for(var i in h)
    if ( columns[h[i]] )
      columns[h[i]].hidden = 1 ;

  h = get_option('frozen', '').split('=') ;
  for(var i in h)
    if ( columns[h[i]] && ! columns[h[i]].freezed )
      columns[h[i]].freezed = 'F' ;

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

  h = get_option('positions', '').split('=') ;
  for(var i in h)
    {
      var j = h[i].split(':') ;
      var data_col = data_col_from_col_id(j[0]) ;
      if ( data_col )
	columns[data_col].position = Number(j[1]) ;
    }

  h = get_option('filters', '', true).split('=') ;
  for(var i in h)
    {
      var j = h[i].split(':') ;
      var column = columns[decode_uri_option(j[0])] ;
      if ( column )
	{
	  init_column(column) ;
	  column.filter = set_filter_generic(decode_uri_option(j[1]), column) ;
	}
    }
  update_filters() ;

  _d('end get_all_options\n') ;
}
