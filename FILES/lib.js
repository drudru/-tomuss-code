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

// Constants
var vertical_scrollbar_width = 17 ;
var horizontal_scrollbar_height = 10 ;
var nr_headers = 2 ;
var histo_image_height = 90 ;
var bs = '<td>' ;
var maximum_url_length = 3000 ;

var is_a_teacher = false ;


// Work value
var element_focused ;
var server_feedback ;
var line_offset ;		// The page being displayed
var column_offset ;
var filters ;			// The filters to apply to the lines
var nr_new_lines ;		// Number of created lines
var nr_new_columns ;		// Number of created columns
var sort_columns ;		// Define the sort columns
var table ;			// The table displayed on the screen
var tr_title ;			// The header TR element for 'title'
var tr_type ;
var tr_weight ;
var tr_filter ;
var tip_display_date ;
var tip_fixed ;
var i_am_the_teacher ;
var i_am_root ;
var teachers ;
var display_tips ;
var columns_filter ;
var columns_filter_value ;
var full_filter ;
var full_filter_value ;
var line_filter ;
var line_filter_value ;
var tr_classname ;		// Column containing the className of the line
var popup_on_red_line ;
var do_not_read_option ;	// Option disabled for virtual tables
var nr_cols ;			// Number of displayed columns on the screen
var nr_lines ;
var the_current_cell ;
var today ;
var debug_window ;
var delayed_list ;
var mouse_over_old_td ; // To not recompute the tip on each mousemove.
var do_update_vertical_scrollbar_cursor ;
var do_update_vertical_scrollbar_position ;
var do_update_vertical_scrollbar ;
var filtered_lines ;
var table_fill_queued = 0 ;
var table_fill_do_not_focus ;
var table_fill_display_headers ;
var table_fill_compute_filtered_lines ;
var table_fill_hook ;
var next_page_col ;
var next_page_line ;
var highlight_list ;
var request_id ;
var connection_state ;
var last_server_answer ;
var nr_saved ;
var auto_save_running ;
var pending_requests ;
var scrollbar_right ;
var ask_login_list ;
var first_day ;
var last_day ;
var current_window_width ;
var current_window_height ;

// HTML elements
var divtable ;
var author ;
var modification_date ;
var server_log ;
var the_body ;
var p_title_links ;
var nr_not_empty_lines ;
var nr_filtered_lines ;
var select_nr_lines ;
var select_nr_cols ;
var message ;
var the_comment ;
var linefilter ;
var sort_down ;
var sort_up ;
var horizontal_scrollbar ;
var vertical_scrollbar ;
var t_authenticate ;
var t_student_picture ;
var t_student_firstname ;
var t_student_surname ;
var t_student_id ;
var t_value ;
var t_history ;
var t_date ;
var t_author ;
var t_column_histogram ;
var t_column_average ;
var t_menutop ;

// Redefined if needed
var root = [] ;
var my_identity = 'identity undefined' ;

function lib_init()
{
  divtable             = document.getElementById('divtable'             );
  tip                  = document.getElementById('tip'                  );
  author               = document.getElementById('author'               );
  modification_date    = document.getElementById('date'                 );
  server_log           = document.getElementById('log'                  );
  the_body             = document.getElementById('body'                 );
  p_title_links        = document.getElementById('title_links'          );
  nr_not_empty_lines   = document.getElementById('nr_not_empty_lines'   );
  nr_filtered_lines    = document.getElementById('nr_filtered_lines'    );
  select_nr_lines      = document.getElementById('nr_lines'             );
  select_nr_cols       = document.getElementById('nr_cols'              );
  message              = document.getElementById('message'              );
  the_comment          = document.getElementById('comment'              );
  linefilter           = document.getElementById('linefilter'           );
  sort_down            = document.getElementById('t_sort_down'          );
  sort_up              = document.getElementById('t_sort_up'            );
  horizontal_scrollbar = document.getElementById('horizontal_scrollbar' );
  vertical_scrollbar   = document.getElementById('vertical_scrollbar'   );
  t_authenticate       = document.getElementById('authenticate'         );
  t_student_picture    = document.getElementById('t_student_picture'    );
  t_student_firstname  = document.getElementById('t_student_firstname'  );
  t_student_surname    = document.getElementById('t_student_surname'    );
  t_student_id         = document.getElementById('t_student_id'         );
  t_value              = document.getElementById('t_value'              );
  t_history            = document.getElementById('t_history'            );
  t_date               = document.getElementById('t_date'               );
  t_author             = document.getElementById('t_author'             );
  t_column_histogram   = document.getElementById('t_column_histogram'   );
  t_column_average     = document.getElementById('t_column_average'     );
  t_menutop            = document.getElementById('menutop'              );
  server_feedback      = document.getElementById('server_feedback'      );

  /*
  if ( t_column_test )
    {
      t_column_test.style.display = 'none' ;
      t_column_red.style.display = 'none' ;
      t_column_green.style.display = 'none' ;
      t_column_columns.style.display = 'none' ;
      t_column_weight.style.display = 'none' ;
      t_column_visibility_date.style.display = '' ;
    }
  */

  line_offset       = 0    ;// The page being displayed
  column_offset     = 0    ;
  filters           = []   ;// The filters to apply to the lines
  nr_new_lines      = 0    ;// Number of created lines
  nr_new_columns    = 0    ;// Number of created columns
  sort_columns      = []   ;// Define the sort columns
  tip_display_date  = 0    ;
  tip_fixed         = 0    ;
  i_am_the_teacher  = false;
  teachers          = []   ;
  display_tips      = true ;
  delayed_list = [] ;
  highlight_list = [] ;
  columns_filter = compile_filter_generic('') ;
  columns_filter_value = '' ;
  full_filter_value = '' ;
  line_filter_value = '' ;
  prst_is_input = true ;
  popup_on_red_line = true ;
  do_not_read_option = false ; // Option disabled for virtual tables
  the_current_cell = new Current() ;
  request_id = 0 ;
  connection_state = 'ok' ;
  last_server_answer = millisec() ;
  nr_saved = 0 ;
  auto_save_running = false ;
  pending_requests = [] ;
  i_am_root = myindex(root, my_identity) != -1 ;

  compute_nr_cols() ;
  compute_nr_lines() ;
  current_window_height = window_height() ;
  current_window_width = window_width() ;

  today = new Date() ;
  today = today.getFullYear() + two_digits(today.getMonth() + 1) +
    two_digits(today.getDate()) ;

  if ( tip )
    tip.display_number = 1 ;

  _today = new Date() ;
  _today.setHours(0,0,0,0) ;

  if ( isNaN(first_day) )
    first_day = 0 ;
  if ( isNaN(last_day) )
    last_day = 86400000 * 365 * 1000 ; // parse_date('31/12/2100').getTime() ;
}


function _d(txt)
{
}

function compute_nr_cols()
{
  nr_cols = Math.floor(16 * (window_width() / 1280)) ;
  if ( nr_cols <= 0 )
    nr_cols = 1 ; // Needed for 'statistics_per_group' virtual table
}

var header_height ;

function compute_nr_lines()
{
  if ( the_current_cell.input && header_height === undefined )
    {
      header_height = findPosY(the_current_cell.input) ;
    }

  if ( the_current_cell.input )
    {
      // Number of displayed lines on the screen
      nr_lines = (window_height() - header_height)
	/ (3 + the_current_cell.input.offsetHeight) ;
      nr_lines = Math.floor(nr_lines) - 3 ;
    }

  // nr_lines = Math.floor( (window_height() - 350) / 22) ;
  if ( nr_lines < 3 )
    nr_lines = 3 ;
}

/*
 * Standard Variable name used in all the code :
 * data_lin : index of the line in 'lines'
 * lin      : index of the line in 'table'
 * data_col : index of the column in 'lines[data_lin]'
 * col      : index of the column in 'table[lin]'
 * column   : is columns[data_col]
 * line     : is lines[data_lin]
 * tr       : is 'table[lin]'
 * td       : is 'table[lin][col]' attributes : data_lin, data_col, lin, col
 * type     : a type of column
 * type_i   : type index
 * type_txt : textual type
 */




function data_col_from_col_id(col)
{
  for(var i in columns)
    if ( columns[i].the_id == col )
      return Number(i) ;
}

function data_col_from_col_title(title)
{
  for(var i in columns)
    if ( columns[i].title == title )
      return Number(i) ;
}

function data_lin_from_lin_id(lin)
{
  var data_lin = myindex(lines_id, lin) ;
  if ( data_lin != -1 )
    return data_lin ;
  return ;

  for(var i in lines_id)
    if ( lines_id[i] == lin )
      return Number(i) ;
}

function lin_from_data_lin(data_lin)
{
  var lin ;

  lin = myindex(filtered_lines, lines[data_lin]) - line_offset ;
  /* Commented 5/2/2010
  for(var i in filtered_lines)
    if ( filtered_lines[i]['number'] == data_lin )
      {
	lin = i - line_offset ;
	break ;
      }
  */
  if ( lin < 0  || lin >= nr_lines )
    return ;
  return lin ;
}

function td_from_data_lin_data_col(data_lin, data_col)
{
  var col, lin ;

  /*
  var cls = column_list() ;
  for(var i in cls)
    if ( cls[i].data_col == data_col )
      {
	col = i - column_offset ;
	break ;
      }
  if ( col < 0 || col >= nr_cols )
    return ;
  */

  col = columns[data_col].col ;
  if ( col === undefined )
    return ;

  lin = lin_from_data_lin(data_lin) ;
  if ( lin === undefined )
    return ;

  return table.childNodes[lin + nr_headers].childNodes[col] ;
}

function col_from_td(td)
{
  return myindex(td.parentNode.childNodes, td) ;
}

function data_col_from_col(col)
{
  return column_list(column_offset, col + 1)[col].data_col;
}

function data_col_from_td(td)
{
  return data_col_from_col(col_from_td(td)) ;
}

function column_from_td(td)
{
  return columns[data_col_from_td(td)] ;
}

function lin_from_td(td)
{
  return myindex(td.parentNode.parentNode.childNodes, td.parentNode) ;
}

function data_lin_from_lin(lin)
{
  var line = line_offset + lin - nr_headers ;
  if ( line >= filtered_lines.length )
    return add_empty_lines() + line - filtered_lines.length ;
  if ( line < 0 )
    return ;
  return filtered_lines[line]['number'] ;
}

function data_lin_from_td(td)
{
  return data_lin_from_lin(lin_from_td(td)) ;
}

function the_td(event)
{
  event = the_event(event) ;
  var td = event.target ;
  if ( td.tagName == 'INPUT' || td.tagName == 'SELECT' || td.tagName == 'IMG' )
    return td.parentNode ;
  else
    {
      while ( td.tagName != 'TD' && td.tagName != 'TH' )
	td = td.parentNode ;

      return td ;
    }
}

function the_input(event)
{
  return the_event(event).target ;
}

function get_option(name, default_value, do_not_unescape)
{
  var o ;

  o = window.location.pathname.split('=' + name + '=') ;
  if ( o.length == 1 )
    return default_value ;
  o = o[1].split('/')[0] ;
  if ( ! do_not_unescape )
    o = unescape(o) ;
  return o ;
}

/******************************************************************************
Function are launched on header events
******************************************************************************/

function filter_keyup(event)
{
  var e = the_event(event) ;
  if ( e.keyCode > 40 || e.keyCode == 8 )
    header_change_on_update(e, e.target, '') ;
}

function empty_header(event)
{
  event = the_event(event) ;
  var input = event.target ;

  input.className = input.className.replace('empty','') ;
  input.onmouseover = mouse_over ;
  input.onkeyup = filter_keyup ;
  input.onblur = filter_unfocus ;
}

function filter_unfocus(event)
{
  element_focused = undefined ;
  event = the_event(event) ;
  var input = event.target ;
  if ( input.value === '' )
    {
      input.className += ' empty' ;
      input.onchange = function () { } ;
    }
}

/* The title is clicked */
function sort_column(event, data_col)
{
  if ( table_fill_queued )
    return ;

  if ( data_col === undefined )
    data_col = the_current_cell.data_col ;

  if ( column_empty(data_col) )
    return ;

  line_offset = 0 ;

  if ( sort_columns[0] !== undefined )
    {
      if ( data_col == sort_columns[0].data_col )
	{
	  sort_columns[0].dir = -sort_columns[0].dir ;
	  table_fill(true,true,true) ;
	  return ;
	}
    }

  var t = [columns[data_col]] ;
  t[0].dir = 1 ;

  for(var i in sort_columns)
    {
      if ( sort_columns[i] != t[0] )
	{
	  t.push(sort_columns[i]) ;
	}
      if ( t.length == 3 ) // Limit the number of sort columns
	break ;
    }

  sort_columns = t ;  
  table_fill(true, true,true) ;
}

function set_tip_position(td, bottom)
{
  if ( tip_fixed )
    {
      tip.style.left = 'auto' ;
      tip.style.right = '0px' ;
      if ( bottom )
	{
	  tip.style.bottom = '0px' ;
	  tip.style.top = 'auto' ;
	}
      else
	{
	  tip.style.top = '0px' ;
	  tip.style.bottom = 'auto' ;
	}
    }
  else
    set_element_relative_position(td, tip) ;
}

function header_focus(t)
{
  t = t.parentNode ;
  show_the_tip(t) ;
  the_current_cell.change() ;
  the_current_cell.jump(the_current_cell.lin, col_from_td(t), true) ;
  element_focused = t ;
}

function header_title_click(t)
{  
  if ( element_focused && element_focused.onblur )
    element_focused.onblur() ;
  t = t.parentNode ;
  show_the_tip(t) ;
  the_current_cell.change() ;
  the_current_cell.jump(the_current_cell.lin, col_from_td(t), true) ;
}

function compute_rank(data_lin, column)
{
  var data_col = column.data_col ;
  var the_value = a_float(lines[data_lin][data_col].value) ;

  if ( isNaN(the_value) )
    return '&nbsp;' ;

  var v, rank = 1, nr = 0 ;
  for (var lin in lines)
    {
      v = lines[lin][data_col].value ;
      if ( v !== '' )
	{
	  nr++ ;
	  if ( v > the_value )
	    rank++ ;
	}
    }
  return rank + '/' + nr ;
}

function line_resume(data_lin)
{
  var s, column ;
  s = '<table class="colored" style="max-width:' + Math.floor(window_width()*0.75) + 'px">' ;
  s += '<tr><th>Colonne</th><th>Valeur</th><th>Rang</th><th>Commentaire</th></tr>';
  for(var data_col in columns)
    {
      cell = lines[data_lin][data_col] ;
      if ( cell.value !== "" || cell.comment !== "" )
	{
	  column = columns[data_col] ;
	  
	  if ( column.real_type.cell_compute )
	    classe = 'ro' ;
	  else
	    classe = '' ;
	  s += '<tr class="' + classe + '"><td style="text-align:right">' +
	    html(columns[data_col].title) + '</td><td>' +
	    cell.value_fixed() + '</td><td>' +
	    compute_rank(data_lin, column) + '</td>' ;
	  if (cell.comment)
	    s += '<td>' + cell.comment_html() + '</td>' ;
	  else
	    s += '<td>&nbsp;</td>' ;
	  s += '</tr>\n' ;
	}
    }
  s += '</table>' ;
  var x = table_attr.portails[lines[data_lin][0].value] ;

  if ( x === undefined )
    x = '' ;
  else
    {
      var xx = '' ;
      for(var i in x)
	xx += x[i] + '<br>' ;
      x = '<small>' + xx.substr(0, xx.length-4) + '</small>' ;
    }

  return s + x + '\n' ; // + '\n' : explanation in update_tip_from_value
}

/* Display the tip (both for headers and data cells) */
function mouse_over(event)
{
  event = the_event(event) ;

  var td = the_td(event) ;


  if ( td == mouse_over_old_td )
    return ;
  mouse_over_old_td = td ;

  if ( ! display_tips )
    return ;

  show_the_tip(td) ;
}

var the_current_line ;

function show_the_tip(td, tip_content)
{
  var bottom = false ;
  var data_col = data_col_from_td(td) ;
  //   alert('td:' + td.tagName + ' col_from_td:' + col_from_td(td) + ' data_col:' + data_col) ;
  var data_lin = data_lin_from_td(td) ;
  var column = columns[data_col] ;
  if ( column === undefined )
    return ;

  var type = column.real_type ;

  if ( tip_content === undefined )
    {
      if ( data_lin === undefined )
	{
	  bottom = true ;
	  s = type['tip_' + td.parentNode.className.split(' ')[0]] ;
	  remove_highlight() ;
	}
      else
	{
	  var line = lines[data_lin] ;
	  var cell = line[data_col] ;
	  if ( cell.is_mine() && table_attr.modifiable )
	    s = '<span class="title">' + type.tip_cell + '</span><br>' ;
	  else
	    s = '' ;
	  // highlight line
	  remove_highlight() ;
	  the_current_line = td.parentNode ;
	  td.parentNode.className += ' highlight_current' ;
	}
      if ( s === '' )
	{
	  tip.style.display = 'none' ;
	  return ;
	}
    }
  else
    s = tip_content ;

  tip.innerHTML = s ;
  tip.style.display = "block" ;
  tip.display_number++ ;
  var a = tip.display_number ;
  // Hide the tip if the mouse go inside
  tip.onmousemove = function() { hide_the_tip(a); } ;

  set_tip_position(td, bottom) ;
}

// XXX should be renamed on_mouse_up
function on_mouse_down(event)
{
  // See 'move_scrollbar_begin', we must finish scrollbar dragging
  if ( the_body.onmouseup && the_body.onmouseup(event) )
    {
      return false ;
    }

  // alert ( the_event(event).button ) ;
  var td = the_td(event) ;
  column_from_td(td).real_type.onmousedown(event) ;
  // stop_event(event) ;

  return false;
}

function wheel(event)
{
  if ( the_body.offsetHeight > window_height() )
    return ;
  if ( popup_is_open() )
    return ;

  if ( the_event(event).wheelDelta < 0 )
    next_page(undefined, zebra_step) ;
  else
    previous_page(undefined, zebra_step) ;
}

// Helper functions

function column_parse_attr(attr, value, column, xcolumn_attr)
{
  return column_attributes[attr].check_and_set(value, column, xcolumn_attr) ;
}

function column_modifiable_attr(attr, column)
{
  if ( ! column_attributes[attr] )
    return false ;

  if ( column_attributes[attr].visible_for.length )
    return myindex(column_attributes[attr].visible_for, column.type) >= 0 ;
  else
    return true ;
}

/******************************************************************************
Table initialization. Only done once
******************************************************************************/

// 'set' each of the column attributes
function init_column(column)
{
  column.real_type = type_title_to_type(column.type) ;

  for(var attr in column_attributes)
    column_parse_attr(attr, 
		      column_attributes[attr].formatter(column, column[attr]),
		      column,
		      ! column_modifiable_attr(attr, column)
		      ) ;
}


// table innerHTML is not supported by anyone

var colgroup ;

function table_init()
{
  var thetable ;

  // Create the table
  // The first two childs are HOVER et TIP
  while( divtable.childNodes[2] )
    divtable.removeChild(divtable.childNodes[2]) ;
  thetable = document.createElement('table') ;
  thetable.className = "colored" ;
  if ( preferences.unmodifiable == 1 )
    thetable.className += " leaves" ;
  thetable.id = 'thetable' ;
  thetable.style.tableLayout = "fixed" ;

  if ( vertical_scrollbar )
    {
      var m, sb_width = vertical_scrollbar_width + 3 ;
      var table_width = (divtable.offsetWidth - sb_width).toFixed(0) ;
      var pos = findPos(divtable) ;
      vertical_scrollbar.style.top = pos[1] + vertical_scrollbar_width ;
      if ( scrollbar_right )
	m = "0px " + sb_width + "px 0em 1px";
      else
	m = "0px 0px 0px " + sb_width + 'px';
      thetable.style.margin = m ;
      thetable.style.width = table_width ;
      // Use timeout because of a firefox3 bug...
      setTimeout(function() {thetable.style.width = table_width ;}, 100) ;
    }

  divtable.appendChild(thetable) ;

  _d('table created\n') ;

  colgroup = document.createElement('COLGROUP') ;
  thetable.appendChild(colgroup) ;
  for(var i=0 ; i<nr_cols; i++)
    colgroup.appendChild(document.createElement('COL')) ;
  

  // Create the table
  table = document.createElement('tbody') ;
  table.id = 'table' ;
  thetable.appendChild(table) ;

  // Header lines

  var input_line = '<INPUT TYPE="TEXT" onfocus="header_focus(this)" onChange="header_change_on_update(event,this,\'\');" onblur="element_focused=undefined">' ;

  tr_title = document.createElement('tr') ;
  tr_title.className = 'column_title' ;
  var th = document.createElement('th') ;
  th.innerHTML = '<p onmousedown="header_title_click(this);sort_column(event) ;"></p>' ;
  for(var i = 0 ; i < nr_cols ; i++ )
    {
      var th2 = th.cloneNode(true) ;
      tr_title.appendChild(th2) ;
      th2.type = tr_title.className ;
    }
  table.appendChild(tr_title) ;

  th.innerHTML = input_line ;
  tr_filter = document.createElement('tr') ;
  tr_filter.className = 'filter' ;
  for(var i = 0 ; i < nr_cols ; i++ )
    {
      var th2 = th.cloneNode(true) ;
      th2.onclick = empty_header ;
      th2.childNodes[0].onchange = function(event) { } ;
      tr_filter.appendChild(th2) ;
      th2.type = tr_filter.className ;
    }
  table.appendChild(tr_filter) ;

  // Content lines
  var td = document.createElement('td') ;
  td.innerHTML = '&nbsp;' ;
  var tr = document.createElement('tr') ;
  for(var i = 0 ; i < nr_cols ; i++ )
    tr.appendChild(td.cloneNode(true)) ;

  for(var i = 0 ; i < nr_lines ; i++ )
    {
      var t = tr.cloneNode(true) ;
      if ( i % zebra_step === 0 )
	t.zebra = 'separator ' ;
      else
	t.zebra = '' ;
      table.appendChild(t) ;
    }

  _d('headers inited\n') ;

  for(var lin = 0 ; lin < nr_lines + nr_headers ; lin++ )
    {
      tr = table.childNodes[lin] ;

      for(var col = 0 ; col < nr_cols ; col++ )
	{
	  td = tr.childNodes[col] ;
	  if ( lin >= nr_headers )
	    td.onmouseup = on_mouse_down ;
	  td.onmousemove = mouse_over ;
	}
    }
}

/******************************************************************************
Update one line of the table
******************************************************************************/

function update_line(data_lin, data_col)
{
  var line = lines[data_lin] ;
  if ( line_empty(line) )
    return ;

  var column = columns[data_col] ;
  column.need_update = true ;
  update_columns(line) ;

  if ( table === undefined )
    return ;

  var lin = lin_from_data_lin(data_lin) ;
  if ( lin === undefined )
    return ;
  
  var tr = table.childNodes[lin + nr_headers] ;
  
  for(var data_col2 in columns)
    {
      column = columns[data_col2] ;
      if ( column.col === undefined )
	continue ;
      if ( column.real_type.cell_compute === undefined )
	continue ;
      if ( data_col != data_col2 ) // To not erase green square
	update_cell(tr.childNodes[column.col], line[data_col2], column);
    }
}

/******************************************************************************
Update the header of the table
******************************************************************************/

function set_columns_filter(h)
{
  var cf = document.getElementById('columns_filter') ;
  cf.className = '' ;
  cf.value = h ;
  columns_filter_value = h ;
  columns_filter = compile_filter_generic(h) ;
}


function columns_filter_change(v)
{
  if ( columns_filter_value == v.value )
    return ;

  if ( v.value === '' )
    {
      // XXX 2010-03-01
      v.className = 'empty' ;
    }
  else
    v.className = '' ;
  columns_filter = compile_filter_generic(v.value) ;

  column_offset = 0 ;
  table_fill(true, true,true) ;
  columns_filter_value = v.value ;
}

function column_list(col_offset, number_of_cols)
{
  if ( col_offset === undefined )
    col_offset = column_offset ;
  if ( number_of_cols === undefined )
    number_of_cols = nr_cols ;

  var freezed = [] ;
  var cl = [] ;
  for(var data_col in columns)
    {
      var column = columns[data_col] ;

      if ( column.freezed == 'F' && column.hidden != 1 )
	{
	  freezed.push(column) ;
	  continue ;
	}
      if ( column.hidden == 1 )
	continue ;
      var v = C(column.title, column.author, '20080101', column.comment) ;
      if ( ! columns_filter(v) && !column.is_empty )
	continue ;
      if ( full_filter  && !column.is_empty )
	{
	  var ok = false ;
	  for(var lin in filtered_lines)
	    {
	      if ( full_filter(filtered_lines[lin][data_col]) )
		{
		  ok = true ;
		  break ;
		}
	    }
	  if ( ! ok )
	    continue ;
	}
      cl.push(column) ;
    }

  freezed.sort(function(a,b) {return a.position - b.position ;}) ;
  cl.sort(function(a,b) {return a.position - b.position ;}) ;

  return freezed.concat(cl.slice(col_offset, col_offset + number_of_cols - freezed.length));
}

/* This function is used by CSV and print
   because there is no scroll and no empty columns
*/

function column_list_all()
{
  var cl = column_list(0,columns.length) ;
  var cl2 = [] ;
  for(var c in cl)
    {
      var data_col = cl[c].data_col ;
      if ( column_empty(data_col) )
	continue ;
      cl2.push(data_col) ;
    }
  return cl2 ;
}

function next_column_from_data_col(data_col)
{
  var cl = column_list_all();
  for(var c in cl)
    {
      if ( cl[c] == data_col )
	{
	  return cl[Number(c)+1] ;
	}
    }
}


function nr_freezed()
{
  var i ;
  i = 0 ;
  for(var data_col in columns)
    if ( columns[data_col].freezed == 'F' )
      i++ ;
  return i ;
}

function update_horizontal_scrollbar_cursor()
{
  var sorted = sort_columns[0].data_col ;
  //  var sorted = sort_columns[0].data_col ;
  for(var cc in horizontal_scrollbar.childNodes)
    {
      var c = horizontal_scrollbar.childNodes[cc] ;
      if ( c && c.className )
	{
	  var classe = c.className.replace(/ (cursor|sorted)/g,'') ;
	  if ( c.data_col == the_current_cell.data_col )
	    classe += ' cursor' ;
	  if ( sorted == c.data_col )
	    classe += ' sorted' ;

	  c.className = classe ;
	}
    }
}

// IE bug for BODY, must use document for this event
function set_body_onmouseup(f)
{
  if ( the_body.onmouseupold === undefined )
    the_body.onmouseupold = the_body.onmouseup ;
  the_body.onmouseup = f ;
}

function move_horizontal_scrollbar_begin(event)
{
  if ( element_focused && element_focused.onblur )
      element_focused.onblur() ;
  the_current_cell.focus() ; // Take focus to do the necessary 'blurs'
  var col = the_event(event).target.col ;
  page_horizontal(0, col) ;
  set_body_onmouseup(body_on_mouse_up) ; // ??? Why not working in HTML TAG
  body_on_mouse_up_doing = "horizontal_scrollbar_drag" ;
  the_body.onmousemove = function(event) {
    var x = the_event(event).x ;
    var b ;
    for(var a in horizontal_scrollbar.childNodes)
      {
	a = horizontal_scrollbar.childNodes[a] ;
	if ( a.style && x < a.xcoord )
	  {
	    if ( b )
	      page_horizontal(0, b.col) ;
	    else
	      page_horizontal(0, a.col) ;
	    break ;
	  }
	b = a ;
      }
  } ;
  stop_event(the_event(event)) ;
}

function move_horizontal_scrollbar_move(event)
{
  if ( body_on_mouse_up_doing == "horizontal_scrollbar_drag" )
    page_horizontal(0, the_event(event).target.col) ;
}


function update_horizontal_scrollbar(cls)
{
  if ( horizontal_scrollbar === undefined )
    return ;

  if ( cls === undefined )
    cls = column_list() ;

  var width = 0 ;
  var cls_all = column_list(0, columns.length) ;
  for(var col in cls_all)
    {
      if ( cls_all[col].is_empty )
	continue ;
      width += cls_all[col].width ;
    }
  var s = '' ;
  var pos = 0 ;
  var dx ;
  var hwidth ;
  if ( vertical_scrollbar )
    {
      if ( scrollbar_right )
	dx = horizontal_scrollbar_height ;
      else
	dx = vertical_scrollbar_width + 2 ;
      hwidth = window_width() - dx - horizontal_scrollbar_height - 2 ;
    }
  else
    {
      dx = horizontal_scrollbar_height ;
      hwidth = window_width() - 2*horizontal_scrollbar_height ;
    }
  var left = horizontal_scrollbar.parentNode.childNodes[0] ;
  var right = horizontal_scrollbar.parentNode.childNodes[2] ;

  left.style.height = horizontal_scrollbar_height + 2 ;
  right.style.height = horizontal_scrollbar_height + 2 ;

  left.style.left = dx - horizontal_scrollbar_height ;
  right.style.left = dx + hwidth ;

  var nr_col_freezed = nr_freezed() ;

  while( horizontal_scrollbar.firstChild )
    horizontal_scrollbar.removeChild(horizontal_scrollbar.firstChild) ;


  for(var col in cls_all)
    {
      if ( cls_all[col].is_empty )
	continue ;
      var a = document.createElement('a') ;
      a.className = 'column_invisible' ;
      for (var c in cls)
	if ( cls[c] == cls_all[col] )
	  {
	    a.className = 'column_visible' ;
	    break;
	  }
      a.xcoord = (dx + ((hwidth * pos) / width)).toFixed(0) ;
      a.style.left = a.xcoord ;
      a.style.width = (hwidth * cls_all[col].width / width).toFixed(0) ;
      a.innerHTML = cls_all[col].title ;
      a.data_col = cls_all[col].data_col ;
      a.col = col ;
      a.href = "javascript:page_horizontal(0," + col + ");" ;

      a.onmousedown = move_horizontal_scrollbar_begin ;

      horizontal_scrollbar.appendChild(a) ;
      pos += cls_all[col].width ;
    }
  update_horizontal_scrollbar_cursor();
}



function sb_height()
{
  return divtable.offsetHeight - 2*vertical_scrollbar_width ;
}

function sb_line_to_pixel(line)
{
  var height = filtered_lines.length ;
  if ( height === 0 )
    return vertical_scrollbar_width ;
  else
    return (sb_height() * line) / height + vertical_scrollbar_width ;
}

function sb_pixel_to_line(pixel, dont_cut)
{
  var line ;

  line = (filtered_lines.length*(pixel-vertical_scrollbar_width))/sb_height() ;
  line = Number(line.toFixed(0));
  if ( dont_cut === undefined )
    if ( line >= filtered_lines.length - nr_lines )
      line = filtered_lines.length - nr_lines + 1 ;
  if ( line < 0 )
    line = 0 ;
  return line ;
}

function update_vertical_scrollbar_cursor_real()
{
  var line = myindex(filtered_lines, the_current_cell.line) ;
  if ( line == -1 )
    {
      vertical_scrollbar.childNodes[3].style.height = 0 ;
    }
  else
    {
      var p1 = sb_line_to_pixel(line);
      var p2 = sb_line_to_pixel(line+1);
      
      vertical_scrollbar.childNodes[3].style.top = p1.toFixed(0) ;      
      height = p2 - p1 ;
      if ( height <= 2 )
	height = 2 ;
      vertical_scrollbar.childNodes[3].style.height = height.toFixed(0) ;
      //debug(vertical_scrollbar.childNodes[3].style,undefined,undefined,true);
    }
}

function update_vertical_scrollbar_cursor()
{
  do_update_vertical_scrollbar_cursor = true ;
}


function update_vertical_scrollbar_position_real()
{
  if ( vertical_scrollbar === undefined )
    return ;
  var p = vertical_scrollbar.childNodes[0] ;
  var height = filtered_lines.length ;
  if ( height === 0 )
    {
      p.style.top = sb_line_to_pixel(0) ;
      p.style.height = sb_height() ;
    }
  else
    {
      p.style.top = sb_line_to_pixel(line_offset) ;
      p.style.height = sb_line_to_pixel(line_offset + nr_lines)
	- sb_line_to_pixel(line_offset) ;
    }
  update_vertical_scrollbar_cursor_real() ;
}

function update_vertical_scrollbar_position()
{
  do_update_vertical_scrollbar_position = true ;
}

var body_on_mouse_up_doing ;

// Return true if the event should not be taken into account
function body_on_mouse_up(event)
{
  if ( body_on_mouse_up_doing )
    {
      the_body.onmouseup = the_body.onmouseupold ;
      the_body.onmousemove = function() { } ;
      body_on_mouse_up_doing = undefined ;
      stop_event(the_event(event)) ;
      return true ;
    }
}


function move_vertical_scrollbar_begin(event)
{
  set_body_onmouseup(body_on_mouse_up) ; // ??? Why not working in HTML TAG
  body_on_mouse_up_doing = "vertical_scrollbar_drag" ;
  the_body.onmousemove = move_scrollbar ;
  move_scrollbar(event) ;
  stop_event(the_event(event));
}

function move_scrollbar(event)
{
  event = the_event(event) ;
  var y ;
  y = event.y - vertical_scrollbar.offsetTop ;
  if ( y < vertical_scrollbar_width )
    return ;
  if ( y > divtable.offsetHeight - vertical_scrollbar_width )
    return ;
  line_offset = sb_pixel_to_line(y,true) - Math.floor(nr_lines/2) ;
  if ( line_offset < 0 )
    line_offset = 0 ;
  var new_y = sb_pixel_to_line(y,true) - line_offset + nr_headers ;
  if ( new_y >= nr_lines + nr_headers ) // Should never be true.
    new_y = nr_lines - 1 + nr_headers ;
  table_fill();
  table_fill_hook = function() { the_current_cell.jump(new_y,
						       the_current_cell.col,
						       true);
  } ;
  stop_event(event) ;
}

function update_vertical_scrollbar_real()
{
  if ( vertical_scrollbar === undefined )
    return ;

  vertical_scrollbar.onmousedown = move_vertical_scrollbar_begin ;
  vertical_scrollbar.style.height = divtable.offsetHeight ;
  vertical_scrollbar.style.width = vertical_scrollbar_width ;
  if ( scrollbar_right )
    vertical_scrollbar.style.right = 0 ;
  else
    vertical_scrollbar.style.left = 0 ;

  vertical_scrollbar.style.top = divtable.offsetTop ;

  if ( sort_columns.length === 0 )
    return ;

  var last = '' ;
  var data_col = sort_columns[0].data_col ;
  var v, vv, v_upper ;
  var height = filtered_lines.length ;
  var y, last_y = -100 ;
  s = '<span class="position">&nbsp;</span><img src="' + url + '/up.gif" onclick="javascript:previous_page();"><img src="/down.gif" onclick="javascript:next_page();"><span class="cursor"></span>' ;


  if ( preferences.v_scrollbar_nr )
    for(var i in filtered_lines)
      {
	v = filtered_lines[i][data_col].value.toString().substr(0,preferences.v_scrollbar_nr) ;
	v_upper = v.toUpperCase() ;
	if ( v_upper != last )
	  {
	    y = sb_line_to_pixel(i) ;
	    if ( y - last_y < 10 )
	      continue ;
	    if ( last.substr(0,1) != v_upper.substr(0,1))
	      vv = '<b class="letter">' + v.substr(0,1) + '</b>' + v.substr(1) ;
	    else
	      vv = '<b class="hide">' + v.substr(0,1) + '</b>' + v.substr(1) ;
	    last = v_upper ;
	    // Was (y-6) ???
	    s += '<span style="top:' + (y).toFixed(0) + 'px">' + vv + '</span>' ;
	    last_y = y ;
	  }
      }

  vertical_scrollbar.innerHTML = s + '' ;
  vertical_scrollbar.childNodes[1].style.width = vertical_scrollbar_width;
  vertical_scrollbar.childNodes[2].style.width = vertical_scrollbar_width;
  vertical_scrollbar.childNodes[2].style.top = divtable.offsetHeight - vertical_scrollbar_width ;

  vertical_scrollbar.childNodes[3].style.width = vertical_scrollbar_width;
  update_vertical_scrollbar_position_real() ;
}

function update_vertical_scrollbar()
{
  do_update_vertical_scrollbar = true ;
}

function table_header_fill()
{
  table_fill_display_headers |= true ;
}

function table_header_fill_real()
{
  var empty_column = add_empty_columns() ;
  var cls = column_list() ;
  var w ;

  table_fill_display_headers = false ;
  the_current_cell.update_column_headers() ;
  update_horizontal_scrollbar(cls) ;

  for(var data_col in columns)
    columns[data_col].col = undefined ;

  // This loop is not with the other in order to speed up display.
  // So the table is not displayed with all the possible columns width.
  var width = 0 ;
  for(var col = 0 ; col < nr_cols ; col++)
    {
      width += cls[col].width + 1 ;
    }

  //var x = '' ;
  for(var col = 0 ; col < nr_cols ; col++)
    {
      w = ((window_width()*cls[col].width)/width-8).toFixed(0) ;
      // tr_title.childNodes[col].style.width = width + 'px' ;
      if ( w <= 0 )
	w = 1 ;
      colgroup.childNodes[col].width = w ;
      //x += '   ' + w ;
    }
  //alert(x) ;

  var sort_indicator ;
  for(var col = 0 ; col < nr_cols ; col++)
    {
      var className ;
      var column = cls[col] ;
      if ( column.author != my_identity || ! table_attr.modifiable )
	className = 'ro' ;
      else
	className = '' ;

      var td_title = tr_title.childNodes[col] ;
      var td_filter = tr_filter.childNodes[col] ;

      /* Remove green squares */
      while(td_title.childNodes[1])
	td_title.removeChild(td_title.childNodes[1]);

      column.col = col ;

      // td_title.data_col = td_filter.data_col = column.data_col ;

      td_title.childNodes[0].innerHTML = html(column.title) ;
      td_filter.childNodes[0].value = column.filter ;
      if ( column.filter === '' )
	td_filter.childNodes[0].className = 'empty' ;
      else
	td_filter.childNodes[0].className = '' ;
      if ( column.freezed !== '' )
	td_filter.childNodes[0].className += ' freezed' ;
      
      td_title.className = className ;

      if ( sort_columns.length !== 0 )
	if ( column == sort_columns[0] )
	  {
	    td_title.className += ' sorted' ;
	    
	    if ( column.dir < 0 )
	      {
		sort_indicator = sort_down ;
		sort_up.style.display = 'none' ;
	      }
	    else
	      {
		sort_indicator = sort_up ;
		sort_down.style.display = 'none' ;
	      }
	    sort_indicator.style.left = findPosX(td_title) + td_title.offsetWidth - 12 ;
	    sort_indicator.style.top = findPosY(td_title) ;
	    sort_indicator.style.display = '' ;
	  }
    }
  if ( sort_indicator === undefined )
    {
      sort_up.style.display = 'none' ;
      sort_down.style.display = 'none' ;
    }
  // XXX If updated, the value being edited may be erased
  if ( ! the_current_cell.focused )
    the_current_cell.update(true) ;
}

/******************************************************************************
Filter and sort the lines of data
******************************************************************************/

function get_filtered_lines(empty_line)
{
  var not_empty_lines = lines.slice(0, empty_line) ;

  if ( filters.length === 0 )
    return not_empty_lines ;  

  var f = [] ;

  for(var line in not_empty_lines)
    {
      line = not_empty_lines[line] ;
      var ok = true ;
      for(var filter in filters)
	{
	  filter = filters[filter] ;
	  if ( ! filter[0](line[filter[1]], filter[2]) )
	    {
	      ok = false ;
	      break ;
	    }
	}
      if ( ! ok )
	continue ;

      f.push(line) ;
    } 
  return f ;
}

/*
 * Search in all the table
 */


function full_filter_change(value)
{
  if ( full_filter_value == value.value )
    return ;

  if ( value.value === '' )
    {
      // value.className = 'empty' ;
      full_filter = undefined ;
    }
  else
    {
      value.className = '' ;
      full_filter = compile_filter_generic(value.value) ;
    }
  column_offset = 0 ;
  line_offset = 0 ;
  table_fill(true, true,true) ; 
  full_filter_value = value.value ;
}


function line_filter_change(value)
{
  if ( line_filter_value == value.value )
    return ;

  if ( value.value === '' )
    {
      // value.className = 'empty' ;
      line_filter = undefined ;
    }
  else
    {
      value.className = '' ;
      line_filter = compile_filter_generic(value.value) ;
    }
  //  column_offset = 0 ;
  line_offset = 0 ;
  table_fill(true, true,true) ; 
  line_filter_value = value.value ;
  update_histogram(true) ;
}

function sort_lines23(a,b)
{
  var c, cc, va, vb ;

  for(var c in sort_columns)
    {
      c = sort_columns[c] ;
      cc = c.data_col ;
      va = a[cc].key() ;
      vb = b[cc].key() ;
      if ( va > vb )
	return c.dir ;
      if ( va < vb )
	return -c.dir ;
    }
  return 0 ;
}

function sort_lines3()
{
  filtered_lines.sort(sort_lines23) ;
}

/******************************************************************************
Update the content of the table
******************************************************************************/


function update_filtered_lines()
{
  var empty_line = add_empty_lines() ;
  var d1 = millisec();
  filtered_lines = get_filtered_lines(empty_line) ;

  if ( full_filter !== undefined )
    {
      var cls = column_list_all() ;
      var f = [] ;
      for(var line in filtered_lines)
	{
	  line = filtered_lines[line] ;
	  for(var column in cls)
	    if ( full_filter( line[cls[column]] ) )
	      {
		f.push(line) ;
		break ;
	      }
	}
      filtered_lines = f ;
    }

  if ( line_filter !== undefined )
    {
      var cls = column_list_all() ;
      var f = [] ;
      for(var line in filtered_lines)
	{
	  line = filtered_lines[line] ;
	  for(var column in cls)
	    if ( line_filter( line[cls[column]] ) )
	      {
		f.push(line) ;
		break ;
	      }
	}
      filtered_lines = f ;
    }

  update_line_menu() ;

  var d2 = millisec() ;
  if ( sort_columns.length !== 0 )
    {
      if ( false )
	filtered_lines.sort(sort_lines) ;
      else
	sort_lines3() ;
    }
  var d3 = millisec() ;
  _d('Filter time: ' + (d2 - d1) + 'ms, Sort time: ' + (d3 - d2) + 'ms');

  if ( nr_filtered_lines
       && nr_filtered_lines.innerHTML != filtered_lines.length )
    {
      nr_filtered_lines.innerHTML = filtered_lines.length ;
      highlight_add(nr_filtered_lines) ;
    }

  update_vertical_scrollbar() ;
}

function line_fill(line, write, cls, empty_column)
{
  if ( cls === undefined )
    cls = column_list() ;
  if ( empty_column === undefined )
    empty_column = add_empty_columns() ;

  var the_line = filtered_lines[line] ;

  var tr = table.childNodes[write] ;
  if ( tr_classname !== undefined )
    {
      var abj = the_student_abjs[the_line[0].value] ;
      if ( ! abj || abj[2] === '' )
	tr.className = tr.zebra + the_line[tr_classname].value ;
      else
	tr.className = tr.zebra + the_line[tr_classname].value + ' tierstemps' ;
    }
  else
    tr.className = tr.zebra ;
  var data_col, td ;
  tr = tr.childNodes ;
  var data_line = the_line['number'] ;
  for(var col = 0 ; col < nr_cols ; col++)
    {
      data_col = cls[col].data_col ;
      td = tr[col] ;

      if ( data_col >= empty_column )
	{
	  td.className = 'empty' ;
	  td.childNodes[0].nodeValue = ' ' ;
	  while( td.childNodes[1] )
	    td.removeChild(td.childNodes[1]) ;
	}
      else
	update_cell(td, the_line[data_col], cls[col], abj) ;
    }
}

function tf(t) { message.innerHTML += t ; }
function tf(t) { }

function table_fill_try()
{
  var terminate ;

  if ( current_window_width != window_width() )
    {
      if ( table_attr.default_nr_columns == 0 )
	{
	  compute_nr_cols() ;
	}
      update_column_menu() ;
      update_histogram(true) ;
    }
  if ( current_window_height != window_height() )
    {
      if ( preferences.nr_lines == 0 )
	compute_nr_lines() ;
      update_line_menu() ;
    }
  if ( current_window_width != window_width()
       || current_window_height != window_height() )
    {
      table_init() ;
      table_fill(false, true, true) ;
      current_window_width = window_width() ;
      current_window_height = window_height() ;
    }

  if ( table_fill_compute_filtered_lines )
    {
      table_fill_compute_filtered_lines = false ;
      update_filtered_lines() ;
    }
  if ( table_fill_queued )
    {
      tf('(TF');
      table_fill_queued = 0 ;
      table_fill_real() ;
      terminate = true ;
      tf(')');
    }
  if ( terminate )
    {
      if ( table_fill_hook )
	{
	  tf('(TFH');
	  table_fill_hook() ;
	  table_fill_hook = undefined ;
	  tf(')');
	}
      tf('(CU');
      // XXX_HS Do not update while the cell is being edited
      if ( ! the_current_cell.focused )
	{
	  the_current_cell.update(table_fill_do_not_focus) ;
	  // Timeout because the cell must be repositionned after
	  // The table column resize in case of horizontal scroll with
	  // variable size columns.
	  setTimeout("the_current_cell.update("+table_fill_do_not_focus+");"
		     ,100) ;
	}
      tf(')');
    }

  if ( table_fill_display_headers )
    {
      tf('(THF');
      // update_vertical_scrollbar() ;
      table_header_fill_real() ;
      tf(')');
    }

  if ( the_current_cell.do_update_headers )
    {
      tf('(UH');
      the_current_cell.update_headers_real() ;
      tf(')');
    }

  if ( do_update_vertical_scrollbar )
    {
      tf('(VS');
      update_vertical_scrollbar_real() ;
      do_update_vertical_scrollbar = false ;
      do_update_vertical_scrollbar_position = false ;
      do_update_vertical_scrollbar_cursor = false ;
      tf(')');
    }
  else if ( do_update_vertical_scrollbar_position )
    {
      tf('(VSP');
      update_vertical_scrollbar_position_real() ;
      update_vertical_scrollbar_cursor_real() ;
      do_update_vertical_scrollbar_position = false ;
      do_update_vertical_scrollbar_cursor = false ;
      tf(')');
    }
  else if ( do_update_vertical_scrollbar_cursor )
    {
      tf('(VSC');
      update_vertical_scrollbar_cursor_real() ;
      do_update_vertical_scrollbar_cursor = false ;
      tf(')');
    }

  if ( the_current_cell.column.type == 'Login'
       && the_current_cell.initial_value != the_current_cell.input.value
       && the_current_cell.input.value.length > 1
       && the_current_cell.input.value != ask_login_list
       && the_current_cell.input.value.toString().search('[.]$') == -1
       )
    {
      ask_login_list = the_current_cell.input.value ;

      login_list(replaceDiacritics(ask_login_list), 
		 [['Chargement des «',ask_login_list,'» en cours']]) ;
      //append_image(undefined, 'login_list/'
      //	   + encode_uri(replaceDiacritics(ask_login_list))) ;
      var s = document.createElement('script') ;
      s.src = url + '/=' + ticket + '/login_list/'
	+ encode_uri(replaceDiacritics(ask_login_list)) ;
      the_body.appendChild(s) ;

    }
}


function login_list_hide()
{
  the_current_cell.blur_disabled = false ;
  hide_the_tip_real() ;
  display_tips = display_tips_saved ;
}

function login_list_select(t)
{
  var s = t.options[t.selectedIndex].innerHTML.split('&nbsp;')[0] ;
  the_current_cell.input.value = s ;
  login_list_hide() ;
  the_current_cell.change() ;
}

var display_tips_saved ;

function login_list(name, x)
{
  if ( name != replaceDiacritics(ask_login_list) )
    return ;
  if ( x.length == 0 )
    {
      login_list_hide() ;
      show_the_tip(the_current_cell.td, "Nom et prénom inconnus") ;
      return ;
    }
  hide_the_tip_real();  
  display_tips_saved = display_tips ;
  display_tips = false ;

  var nr = Math.floor(nr_lines / 2) ;
  if ( x.length < nr )
    nr = x.length ;
  if ( nr < 2 )
    nr = 2 ;

  var s = '<select class="login_list" size="' + nr + '" onmouseover="the_current_cell.blur_disabled = true;" onmouseout="the_current_cell.blur_disabled = false" onchange="login_list_select(this)">' ;

  var w = 0 ;
  for(var i in x)
    if ( x[i][0].length > w )
      w = x[i][0].length ;
  
  for(var i in x)
    {
      i = x[i] ;
      var cn = '' ;
      if ( i[3] )
	{
	  cn = i[3].replace(/OU=/g, '') ;
	  cn = cn.split(',') ;
	  cn = cn.slice(1, cn.length-2) ;
	  cn = '<i><small>' + cn.toString() + '</small></i>' ;
	}
      s += '<option>'
	+ left_justify(i[0],w).replace('&nbsp;',' ')
	+ '&nbsp;' + i[1] + ' ' + i[2] + ' ' + cn + '</option>' ;
    }
  s += '</select>' ;
  show_the_tip(the_current_cell.td, s) ;
  tip.onmousemove = function() { } ;

}

function table_fill(do_not_focus, display_headers, compute_filtered_lines)
{
  if ( table === undefined )
    return ;
  table_fill_queued = 1 ;
  table_fill_do_not_focus = do_not_focus ;
  table_fill_display_headers |= display_headers ;
  table_fill_compute_filtered_lines = compute_filtered_lines ;
}

function table_fill_real()
{
  var read = 0 ;
  var write = nr_headers ;
  var td ;
  var empty_line = add_empty_lines() ;
  var empty_column = add_empty_columns() ;
  var cls = column_list() ;

  var d1 = millisec() ;
  for(var line in filtered_lines)
    {
      if ( read < line_offset ) // XXX slow :-(
	{
	  read++ ;
	  continue ;
	}
      line_fill(line, write, cls, empty_column) ;
      write++ ;
      if ( write == nr_lines + nr_headers )
	break ;
    }
  // lines of tables after the end of the data, the empty lines
  while( write < nr_lines + nr_headers )
    {
      var tr = table.childNodes[write] ;
      tr.className = tr.zebra ;
      for(var col = 0 ; col < nr_cols ; col++)
	{
	  var data_col = cls[col].data_col ;
	  td = tr.childNodes[col] ;
	  td.childNodes[0].nodeValue = " " ; // Unsecable space
	  while( td.childNodes[1] )
	    td.removeChild(td.childNodes[1]) ;
	  if ( data_col >= columns.length )
	    td.className = 'empty' ;
	  else
	    td.className = 'rw empty' ;
	}    
      empty_line++ ;
      write++ ;
    }
  update_vertical_scrollbar_position() ;
  _d(', table_fill_real: ' + (millisec() - d1) + 'ms') ;
  if ( the_current_cell.focused )
      the_current_cell.update() ; // 2010-10-06
}

/******************************************************************************
Table utilities
******************************************************************************/

function line_empty(line)
{
  for(var i in columns)
    if ( line[i].is_not_empty() )
      return false ;
  return true ;
}

function column_empty(column)
{
  return !! columns[column].is_empty ;
}

function column_empty_of_cells(column)
{
  for(var i in lines)
    {
      if ( lines[i][column].is_not_empty() )
	return false ;
    }
  return true ;
}

function first_line_not_empty()
{
  for(var i = lines.length - 1 ; i >=0 ; i--)
    if ( ! line_empty( lines[i] ) )
      break ;
  return i ;
}

function first_column_not_empty()
{
  for(var i = columns.length - 1 ; i >=0 ; i--)
    if ( ! column_empty( i ) )
      break ;
  return i ;
}

function add_empty_line()
{
  var line = [] ;
  for(var c in columns)
    line[c] = C();
  line['number'] = lines.length ;
  lines[lines.length] = line ;
  lines_id[lines_id.length] = page_id + '_' + nr_new_lines ;
  nr_new_lines++ ;
}

function add_empty_column(keep_data)
{
  var data_col = columns.length ;
  
  if ( ! keep_data )
    for(var line in lines)
      lines[line][data_col] = C() ;

  var position = 0 ;
  for(var i in columns)
    if ( columns[i].position > position )
      position = columns[i].position ;

  var d ;
  if ( tr_classname !== undefined )
    d = 5 ;
  else
    d = -1 ;

  var column = {the_id:page_id + '_' + nr_new_columns,
		the_local_id:  nr_new_columns.toString(),
		data_col: columns.length,
		is_empty: keep_data === undefined,
		filter: ""
  } ;

  column.real_type = type_title_to_type(column_attributes['type'].default_value) ;
  var value ;
  for(var attr in column_attributes)
    {
      switch(attr)
	{
	case 'title':   value = default_title + (columns.length - d) ; break ;
	case 'position':value = position + 1 ; break ;
	case 'author':  value = my_identity ; break ;
	default:        value = column_attributes[attr].default_value ; break ;
	}
      column[attr] = column_parse_attr(attr, value, column) ;
    }
  columns[columns.length] = column ;
  nr_new_columns++ ;
}

function Col(attrs)
{
  for(var attr in column_attributes)
    {
      if ( attrs[attr] === undefined )
	attrs[attr] = column_attributes[attr].default_value ;
    }
  return attrs ;
}

// Create many empty lines in order to fill the screen
// Returns the first line empty
function add_empty_lines()
{
  var not_empty = first_line_not_empty() ;
  var nr_empty_lines = lines.length - not_empty - 1 ;

  for(var i = 0 ; i < nr_lines - nr_empty_lines ; i++)
    add_empty_line() ;

  if ( nr_not_empty_lines )
    nr_not_empty_lines.innerHTML = not_empty + 1 ;

  return not_empty + 1 ;
}

function add_empty_columns()
{
  var not_empty = first_column_not_empty() ;
  var nr_empty_columns = columns.length - not_empty - 1 ;

  /* There is a +5 because a user may hide empty columns.
     It will make 'column_list' function have problems
     because there is missing empty columns.
     So, we add some more.
  */
  for(var i = 0 ; i < nr_cols - nr_empty_columns + 5 ; i++)
    add_empty_column() ;

  return not_empty + 1 ;
}

/******************************************************************************
Cursor movement
******************************************************************************/

function next_page(next_cell, dy)
{
  the_current_cell.change() ;

  if ( filtered_lines !== undefined 
       && line_offset + nr_lines > filtered_lines.length )
    return true;

  if ( dy === undefined )
    dy = Number((nr_lines * preferences.page_step).toFixed(0)) ;


  if ( next_cell )
    {
      table_fill_hook = function() {
	cell_goto(table.childNodes[nr_headers+nr_lines-dy].childNodes[the_current_cell.col]) ;
      } ;
    }

  line_offset += dy ;
  
  table_fill() ;
  return true ;
}

function previous_page(previous_cell, dy)
{
  the_current_cell.change() ;
  if ( dy === undefined )
    dy = Number((nr_lines * preferences.page_step).toFixed(0)) ;
  if ( previous_cell )
    {
      table_fill_hook = function() {
	cell_goto(table.childNodes[nr_headers+dy-1].childNodes[the_current_cell.col]) ; } ;
    }
  line_offset -= dy ;
  if ( line_offset < 0 )
    line_offset = 0 ;
  table_fill() ;
  return true ;
}


function table_fill_hook_horizontal()
{
  var tr = table.childNodes[next_page_line] ;
  var col = next_page_col - column_offset ;
  if ( col < 0 )
    cell_goto(tr.childNodes[0]); 
  else if ( col < nr_cols )
    cell_goto(tr.childNodes[col]); 
  else
    cell_goto(tr.childNodes[nr_cols-1]); 
}

/*
 * If 'col' is defined : then it is the required column (centered)
 * Else 'direction' is a delta
 */
function page_horizontal(direction, col)
{
  var cls = column_list_all() ;

  the_current_cell.change() ;
  
  if ( col === undefined )
    {
      col = myindex(cls, the_current_cell.data_col) +
	( direction > 0 ? 1 : -1 )  ;
      if ( direction > 0 && col === 0 )
	{
	  alert("À quoi cela vous sert d'aller à droite, le tableau est vide !") ;
	  return ;
	}
      column_offset += direction ;
    }
  else
    {
      column_offset = col - Math.floor((nr_cols+nr_freezed())/2) ;
    }

  next_page_col = col ;
  next_page_line = the_current_cell.lin ;
 
  if ( column_offset + nr_cols > columns.length )
    column_offset = columns.length - nr_cols ;
  if ( column_offset < 0 )
    column_offset = 0 ;

  the_current_cell.focused = false ; // XXX Kludge for XXX_HS
  table_fill_hook = table_fill_hook_horizontal ;
  table_fill(false, true) ;
  table_fill_try() ;
}

function next_page_horizontal(delta)
{
  page_horizontal( Math.floor((nr_cols-nr_freezed()) / 2), delta) ;
}

function previous_page_horizontal(delta)
{
  page_horizontal( -Math.floor((nr_cols-nr_freezed()) / 2), delta) ;
}


/******************************************************************************
Cursor movement
******************************************************************************/

function cell_get_value_real(data_lin, data_col)
{
  return columns[data_col].real_type.formatte(lines[data_lin][data_col].value);
}

function update_cell(td, cell, column, abj)
{
  var v = cell.value ;
  var className = '' ;

  if ( cell.is_mine() && column.real_type.cell_is_modifiable )
    className += 'rw' ;
  else
    className += 'ro' ;

  if ( cell.comment !== '' )
    className += ' comment' ;
  if ( cell.date.indexOf(today) === 0 )
    className += ' today' ;
  if ( v.toFixed )
    {
      className += ' number' ;
      v = column.real_type.formatte(v) ;
    }
  if ( full_filter && full_filter(cell) )
    className += ' filtered' ;
  else if ( line_filter && line_filter(cell) )
    className += ' filtered' ;


  if ( column.color_red_filter(cell, column) )
    className += ' color_red' ;

  if ( column.color_green_filter(cell, column) )
    className += ' color_green' ;

  if ( v === abi && abj && abj[0].length )
    {
      var d = new Date(cell.date.substr(0,4),
		       cell.date.substr(4,2)-1,
		       cell.date.substr(6,2)) ;
      d = d.getTime() ;
      for(var a in abj[0])
	{
	  a = abj[0][a] ;
	  if ( ! abj_is_fine(a) )
	    continue ;
	  if ( parse_date(a[0]).getTime() < d
	       && d < parse_date(a[1]).getTime() + 86400000*7 )
	    {
	      className += ' is_an_abj' ;
	      break ;
	    }
	}
    }
  td.className = className ;
  if ( v === '' )
    td.childNodes[0].nodeValue = ' ' ; // If empty : zebra are not displayed
  else
    td.childNodes[0].nodeValue = v.toString() ;
  while( td.childNodes[1] )
    td.removeChild(td.childNodes[1]) ;

  return v ;
}

function column_change_allowed_text(column)
{
  if ( ! table_attr.modifiable )
    return "Cette table a été passée en lecture seulement par son responsable";
  if ( column.title === '' )
    return true ;
  if ( column.author == '*' )
    return "Cette colonne est définie par le système et ne peut être changée.";
  if ( column.author == my_identity )
    return true ;
  if ( i_am_the_teacher )
    return true ;
  return "Cette colonne a été définie par un autre enseignant et vous n'êtes pas le responsable de l'UE." ;
}

function column_change_allowed(column)
{
  return column_change_allowed_text(column) === true ;
}

function add_a_new_line(data_lin)
{
  if ( line_empty(lines[data_lin]) )
    {
      for(var i=add_empty_lines(); i <= data_lin; i++)
	filtered_lines.push(lines[i]) ;
      if ( nr_filtered_lines )
	nr_filtered_lines.innerHTML = filtered_lines.length ;
    }
}

function create_column(column)
{
  if ( column.is_empty && column.the_local_id !== undefined )
    {
      column.is_empty = false ;
      append_image(undefined, 'column_attr_title/' + page_id + '_' + column.the_local_id + '/' +
		   encode_uri(column.title)) ;
      column.the_local_id = undefined ;
      update_horizontal_scrollbar() ;
      return true ;
    }
}

function cell_set_value_real(data_lin, data_col, value, td)
{
  var cell = lines[data_lin][data_col] ;
  var column = columns[data_col] ;

  // toString is used because '' != '0' and '00' != '000'
  // === is not used because 5.1 == "5.1"
  if ( value.toString() == lines[data_lin][data_col].value.toString() )
    return ;

  if ( ! cell.modifiable() )
    return ;

  if ( column.is_empty && columns_filter_value !== '' )
    {
      alert("Désolé, il n'est pas possible de créer de nouvelles colonnes quand il y a un filtre de colonne.\n\nCette fonctionnalité est très complexe à programmer et peu utile,\nElle ne sera donc pas ajoutée.") ;
      return;
    }

  value = column.real_type.cell_test(value, column);
  if ( value === undefined )
    return ;

  create_column(columns[data_col]) ;
  add_a_new_line(data_lin) ;

  // Does history should be modified in set_value ?
  if ( ! cell.never_modified() )
    cell.history += cell.value + '(' + cell.author + '),' ;
  cell.set_value(value) ;
  cell.author = my_identity ;
  var d = new Date() ;
  cell.date = '' + d.getFullYear() +
    two_digits(d.getMonth()+1) +
    two_digits(d.getDate()) +
    two_digits(d.getHours()) +
    two_digits(d.getMinutes()) +
    two_digits(d.getSeconds()) ;

  var v ;
  if ( td !== undefined )
    v = update_cell(td, cell, column) ;

  /* Create cell */
  append_image(td, 'cell_change/' + column.the_id + '/' +
	       lines_id[data_lin] + "/" + encode_uri(cell.value)
	       );

  if ( value !== '' )
    column.is_empty = false ;

  update_histogram(true) ; // XXX

  return v ;

}

function cell_set_value(td, value, data_lin, data_col)
{
  if ( value === undefined )
    // Next/Prev page if there is not a cell selected (Prst)
    return cell_get_value_real(data_lin, data_col) ;

  var v = cell_set_value_real(data_lin, data_col, value, td) ;
  if ( v !== undefined )
    return v ;
  return cell_get_value_real(data_lin, data_col) ;
}

/*REDEFINE
  If LDAP students login and real students ID are not equals
  then a translation must be done.
  This function translate the login to a student number.
*/
function login_to_id(login)
{
  return login ;
}

/*REDEFINE
  If LDAP students login and real students ID are not equals
  then a translation must be done.
  This function translate the student number to a login
*/
function the_login(login)
{
  return login ;
}

function abj_is_fine(abj)
{
  if ( parse_date(abj[0]).getTime() > last_day )
    return 0 ;
  if ( parse_date(abj[1]).getTime() < first_day )
    return false ;
  return true ;
}

function student_abjs(login)
{
  var abjs_da = the_student_abjs[login] ;
  
  if ( abjs_da === undefined )
    return '' ;

  var abjs = [] ;
  var s = '' ;

  for(var i in abjs_da[0])
    {
      i = abjs_da[0][i] ;
      if ( abj_is_fine(i) )
	abjs.push(i) ;
    }

  if ( abjs.length )
    {
      s += '<TABLE class="display_abjs colored">' ;
      s += '<TR><TH COLSPAN="4">Liste des ABJs</TH></TR>' ;
      s += '<TR><TH>Début</TH><TH>Fin</TH><TH>Durée</TH><TH></TH></TR>' ;
      for(var abj in abjs)
        {
	  s += '<TR>' ;
          var d = (0.5 + (parse_date(abjs[abj][1]).getTime()
			  - parse_date(abjs[abj][0]).getTime())/(1000*86400)) ;
	  if ( d == 0.5 )
	    s += '<TD COLSPAN="2">' + nice_date(abjs[abj][0]) ;
	  else if ( abjs[abj][0].replace(/[AM]/,'')
		    == abjs[abj][1].replace(/[AM]/,'') )
	    s += '<TD COLSPAN="2">' + nice_date(abjs[abj][0]).replace(/ [^ ]*$/,'');
	  else      
	    s += '<TR><TD>' + nice_date(abjs[abj][0]) +
	      '</TD><TD>' + nice_date(abjs[abj][1]) ;
	  
	  s += '</TD><TD>' + d.toFixed(1) +
	    '</TD><TD>' + html(abjs[abj][2]) +
	    '</TD></TR>' ;
        }
      s += '</TABLE>' ;
    }

  var das = abjs_da[1] ;
  if ( das.length )
    {
      for(var da in das)
        {
          if ( das[da][0] == ue )
	    {
	      s += '<p class="da">Dispense d\'assiduité pour l\'UE (à partir du ' + das[da][1] + ') <em>' + das[da][2] + '</em></p>' ;
	      break ;
	    }
        }
    }
  if ( abjs_da[2] )
    s += '<p class="tierstemps"><b>Actuellement avec un tiers temps</b> :<br>' + abjs_da[2].replace(/\n/g, '<br>') ;

  return s ;
}

function set_element_relative_position(anchor, element)
{
  var pos = findPos(anchor) ;
  var table_pos = findPos(table) ;

  tip_display_date = millisec() ;

  if ( pos[1] + element.offsetHeight > window_height() + scrollTop())
    {
      element.style.top = window_height() + scrollTop() - element.offsetHeight;
      if ( pos[0] + anchor.offsetWidth + element.offsetWidth
	   > table_pos[0] + table.offsetWidth )
	element.style.left = pos[0] - element.offsetWidth ;
      else
	element.style.left = pos[0] + anchor.offsetWidth ;
      return ;
    }     

  element.style.top = pos[1] + anchor.offsetHeight ;

  if ( pos[0] + element.offsetWidth > table_pos[0] + table.offsetWidth)
    element.style.left = table_pos[0] + table.offsetWidth - element.offsetWidth ;
  else
    element.style.left = pos[0] ;

  element.style.right = 'auto' ;
  element.style.bottom = 'auto' ;

}

function highlight_effect()
{
  var t = [] ;
  for(var o in highlight_list)
    {
      o = highlight_list[o] ;
      o.className = o.className
	.replace(/ *highlight4/, '')
	.replace(/ *highlight3/, ' highlight4')
	.replace(/ *highlight2/, ' highlight3')
	.replace(/ *highlight1/, ' highlight2')
	;
      if ( o.className.search('highlight') != -1 )
	t.push(o) ;
    }
  highlight_list = t ;
}

function highlight_add(element)
{
  // The spaces broke the filter input with empty message ??? XXX WHY
  // element.className += (element.className + ' highlight1')
  //  .replace('empty','').replace(/^ */,'').replace(/ *$/,'') ;
  // With this code, highlight of 'freezed' links does not happen.

  element.className = 'highlight1' ;
  if ( myindex(highlight_list, element) == -1 )
    highlight_list.push(element) ;
}


// In firefox a VAR object disapear from DOM tree !
function update_tip_from_value(o, value)
{
  if ( !o )
    return ;

  var e = tip_top(o).childNodes[0].lastChild ;
  e.className = 'more' ;

  if ( value.substr(value.length-1) != '\n' ) // Tip with HTML inside
    e.innerHTML = html(value) ;
  else
    e.innerHTML = value ;
}


function update_value_and_tip(o, value)
{
  value = html(value.toString()) ;
  var v = value + '&nbsp;' ;
  if ( o.innerHTML != v )
    {
      highlight_add(o) ;
      o.innerHTML = v ;
      update_tip_from_value(o, value) ;
    }
}

function update_input(element, value, empty)
{
  if ( ! element )
    return ;
  if ( element_focused == element )
    return ; // Do not update value if the input has the focus

  if ( empty )
    {
      element.className = ' empty' ;
      element.value = '' ;
    }
  else
    {
      value = value.toString() ;
      if ( element.value != value )
	{
	  element.value = value ;
	  highlight_add(element) ;
	}
    }
  element.theoldvalue = element.value ;
  update_tip_from_value(element, element.value) ;
}

function cell_goto(td, do_not_focus)
{
  var lin = lin_from_td(td) ;
  var col = col_from_td(td) ;
  var data_col = data_col_from_col(col) ;
  var data_lin = data_lin_from_lin(lin) ;
  var column = columns[data_col] ;

  if ( do_not_focus !== true && element_focused )
    {
      element_focused.blur();// To save values being edited before cell change.
      if ( element_focused && element_focused.onblur )
	element_focused.onblur() ; // Buggy Browser
    }

  if ( the_current_cell.td != td && do_not_focus !== true )
    the_current_cell.input.selectionEnd = 0 ; // For Opera

  the_current_cell.jump(lin, col, do_not_focus, data_lin, data_col) ;
}

/* Communication to the server */

function server_answered(t)
{
  last_server_answer = millisec() ;

  if ( connection_state != 'ok' )
    {
      _d('An image was received : state=' + connection_state + '\n');
      the_body.className = 'tomuss' ;
      t_authenticate.style.display = 'none' ;
      server_feedback.answered = true ;
      connection_state = 'ok' ;
    }

  if ( t === undefined )
    return ;

  if ( t.request.saved )
    return ;
  saved(t.request.request_id) ;

  //  auto_save_errors() ;
}

function revalidate_ticket()
{
  _d('A server feedback was received\n');
  server_feedback.answered = true ;

  if ( connection_state == 'no_connection' )
    {
      connection_state = 'no_save' ;
    }
}


function Request(content)
{
  this.content = content ;
  this.request_id = request_id++ ;
  this.time = millisec() ;
  this.firsttime = this.time ;
  this.requested = false ;
}

function request_url()
{
  var a ;
  a = url + "/=" + ticket + '/' + year + '/' + semester + '/' + ue + '/' +
    page_id + '/' + this.request_id ;
  if ( this.time != this.firsttime )
    a += '.' + millisec() ;
  return a + '/' + this.content ;
}

function request_send()
{
  var url = this.url() ;
  if ( this.image_pending === undefined )
    {
      // The feedback square under the table
      if ( this.image )
	this.image_pending = this.image.cloneNode(true) ;
      else
	this.image_pending = url_base().childNodes[0] ;
      this.image_pending.alt = "Changement pas encore sauvegardé" ;
      server_log.appendChild( this.image_pending) ;
      this.image_pending.request = this ;
    }
  this.image_pending.src = url ;
  // After because image_pending must be created before receiving 'saved'
  if ( this.image )
    {
      // The inline feedback square
      this.image.src = url ;
    }
  this.time = millisec() ;
  this.requested = true ;
}


Request.prototype.url = request_url ;
Request.prototype.send = request_send ;

function click_to_revalidate_ticket()
{
  var m =  '<a onclick="javascript: t_authenticate.style.display = \'none\' ; window_open(\'' + cas_url + '/login?service='
    + encode_uri('http://' + document.location.host +
		 '/allow/' + ticket + '/' + millisec()).replace(/%01/g, '%2F')
    + '\')">CLIQUEZ ICI<br>POUR VOUS AUTHENTIFIER À NOUVEAU<br>votre session a expiré ou<br>votre machine a changé de réseau.</a>' ; 
  t_authenticate.style.display = 'block' ;
  t_authenticate.innerHTML = m ;
  connection_state = 'auth' ;
}

// Restart image loading if the connection was not successul

function auto_save_errors()
{
  var nr_unsaved = 0 ;
  var errors = 0 ;
  var i ;
  // Problem if the server is slow to answer
  // In millisecond
  var max_answer_time = 10000 ;

  if ( last_server_answer != 0
       && (millisec() - last_server_answer) > 5000+1000*check_down_connections_interval)
      reconnect() ;

  if ( auto_save_running || ! table_attr.autosave )
    return ;

  auto_save_running = true ;

  _d('(autosave[' + connection_state + ', server_feedback(answered=' +
     server_feedback.answered + ',time=' + server_feedback.time +
     '),last_server_answer=' + last_server_answer + ']' );

  var d = millisec() ;
  nr_saved = 0 ;

  for(var i in  pending_requests)
    {
      i =  pending_requests[i] ;
      if ( i.saved )
	continue ;
      nr_unsaved++ ;
      // Some browsers don't like many connections
      if ( nr_unsaved > 10 + nr_saved )
	break ;
      // Retry to load the image each N seconds and the first time
      if ( d > i.time + max_answer_time || ! i.requested )
	{
	  if ( i.requested )
	    errors++ ; // Because it is requested again
	  i.send() ;
	}
    }

  // Remove the item 10 by 10 (it's slow one by one)
  for(var i=10; i>=0; i--)
    if (  pending_requests[i] === undefined || !  pending_requests[i].saved )
      break ;
  if ( i == -1 )
    pending_requests.splice(0,10) ;

  if ( connection_state == 'ok' && errors
       && d > last_server_answer + max_answer_time ) // TO BE THREAD SAFE
    {
      _d('\nSTATE=no_save ==> ');
      connection_state = 'no_save' ;

      server_feedback.answered = false ;
      server_feedback.time = d ;
      server_feedback.innerHTML = '<img src="_URL_/status/' + d +
	'" width="8" height="8" onload="revalidate_ticket();">' ;
      _d(server_feedback.innerHTML + '\n');      
    }

  if ( connection_state == 'no_connection'
       && d - server_feedback.time > 2*max_answer_time)
    {
      server_feedback.innerHTML = '<img src="_URL_/status/' + d +
	'" width="8" height="8" onload="revalidate_ticket();">' ;
      server_feedback.time = d ;
    }

  // See PLUGINS/newpage.py before modifying
  if ( connection_state == 'no_save'
       && d - server_feedback.time > max_answer_time )
    {
      if ( server_feedback.answered )
	click_to_revalidate_ticket() ;
      else
	{
	  _d('STATE=NO_CONNECTION');
	  alert("Cela fait 5 secondes que l'on n'arrive pas à sauvegarder votre travail sur le serveur.\nIl sera sauvegardé quand la connexion internet sera rétablie.\n\nVous perdrez votre travail si vous fermez la page web ou la rechargez...\n\nIl est préférable d'attendre que TOUS les carrés oranges deviennent verts\navant de continuer à travailler") ;
	  if (  last_server_answer < d )
	    {
	      // Nothing was received while alert was displayed
	      the_body.className = 'tomuss autosavefailed' ;
	      connection_state = 'no_connection' ;
	    }
	}
    }

  _d('autosave)\n');
  auto_save_running = false ;
}

// Remove green images
// The function is called :
//    * On feedback image load
//    * On pending image load
//    * When the server answer by the normal connection (page_answer).
function saved(r)
{
  nr_saved++ ;
  for(var i in pending_requests)
    {
      if ( pending_requests[i].request_id == r )
	{
	  if ( pending_requests[i].saved )
	    return ;
	  pending_requests[i].saved = true ;
	  server_log.removeChild(pending_requests[i].image_pending) ;
	  return ;
	}
    }
}

function connected()
{
  last_server_answer = millisec() ;
}

function url_base()
{
  var invisible ;
  if ( table_attr.autosave )
    {
      invisible = '' ;
    }
  else
    {
      invisible = ' style="display:none"' ;
    }

  var a = '<img onLoad="server_answered(this);" class="server"'+invisible+'>';
  var s = document.createElement('span');
  s.innerHTML = a ;
  return s ;
}

function append_image(td, text, force)
{
  if ( ! table_attr.modifiable && ! force )
    return ;

  var request = new Request(text) ;
  pending_requests.push(request) ;

  if ( td )
    {
      if ( td.childNodes[0] !== undefined
	   && td.childNodes[0].style !== undefined )
	if ( td.childNodes[0].id === '' )
	  td.childNodes[0].style.width = td.childNodes[0].offsetWidth - 7 ;
	else
	  td.childNodes[0].style.width = td.childNodes[0].offsetWidth - 0 ;

      s = url_base() ;
      request.image = s.childNodes[0] ;
      request.image.request = request ;
      td.appendChild(s) ;
    }
}

function login_to_line(login)
{
  for(var data_lin in lines)
    {
      if (login_to_id(lines[data_lin][0].value) == login)
	return Number(data_lin) ;
    }
}


/* Communication from the server */

function Xcell_change(col, lin, value, date, identity, history)
{
  var data_col = data_col_from_col_id(col) ;
  var data_lin = data_lin_from_lin_id(lin) ;

  if ( data_lin === undefined )
    {
      // Create empty lines
      data_lin = add_empty_lines() ;
      lines_id[data_lin] = lin ;

      /* Update screen : dangerous, but necessary in order to take into
       account the fact that empty lines may be no more empty...
      */
      filtered_lines.push(lines[data_lin]) ;
      lin = filtered_lines.length - line_offset ;
      if ( lin > 0 && lin < nr_lines - nr_headers )
	{
	  line_fill(filtered_lines.length-1, lin + nr_headers) ;
	}
    }
  var cell = lines[data_lin][data_col] ;

  cell.set_value(value) ;
  cell.author = identity ;
  cell.date = date ;
  cell.history = history ;

  var td = td_from_data_lin_data_col(data_lin, data_col) ;

  if ( td !== undefined )
    {
      update_cell(td, cell, columns[data_col]) ;
      if ( td == the_current_cell.td )
	{
	  the_current_cell.update_cell_headers() ;
	  the_current_cell.jump(the_current_cell.lin,
				the_current_cell.col) ;
	}
    }
  update_line(data_lin, data_col) ;
}

function Xcomment_change(identity, col, lin, value)
{
  var data_col = data_col_from_col_id(col) ;
  var data_lin = data_lin_from_lin_id(lin) ;
  if ( data_lin === undefined )
    {
      data_lin = add_empty_lines() ;
      lines_id[data_lin] = lin ;
      /* Update screen : dangerous, but necessary */
      filtered_lines.push(lines[data_lin]) ;
    }
  var cell = lines[data_lin][data_col] ;

  cell.set_comment(value) ;

  var td = td_from_data_lin_data_col(data_lin, data_col) ;
  if ( td !== undefined )
    {
      update_cell(td, cell, columns[data_col]) ;
      if ( cell === the_current_cell.cell )
	the_current_cell.update_cell_headers() ;
    }
}

function Xcolumn_delete(page, col)
{
  var data_col = data_col_from_col_id(col) ;

  for(data_lin in lines)
    {
      lines[data_lin].splice(data_col ,1) ;
    }
  columns.splice(data_col ,1) ;
  for(data_col in columns)
    columns[data_col].data_col = Number(data_col) ;
  the_current_cell.update() ;

  if ( page != ' ')
    alert("Désolé pour le dérangement, mais je dois tout réafficher car quelqu'un a détruit une colonne") ;
  table_fill(true, true,true) ;  
}

function Xcolumn_attr(attr, col, value)
{
  var data_col = data_col_from_col_id(col) ;
  var column ;
  if ( data_col === undefined )
    {
      data_col = add_empty_columns() ;
      column = columns[data_col] ;
      column.the_id = col ;
      column.local_id = undefined ;
      column.is_empty = false ;
      table_fill() ;
    }
  else
    column = columns[data_col] ;
  column[attr] = column_parse_attr(attr, value, column, true) ;
  attr_update_user_interface(attr, column, true) ;
}

function Xtable_attr(attr, value)
{
  table_attr[attr] = table_attributes[attr].formatter(value) ;
  the_current_cell.update_table_headers();
}

function update_table_size()
{
  // In order to force Gecko to update table size
  var tr = table.childNodes[nr_lines + nr_headers - 1] ;

  table.removeChild(tr);
  table.appendChild(tr) ;
}

function stop_event(event)
{
  if ( event.real_event )
    event = event.real_event ;
  if ( event.stopPropagation )
    event.stopPropagation(true) ;
  if ( event.preventDefault )
    event.preventDefault(true) ;
  else
    {
      event.returnValue = false;
      event.keyCode = 0;
    }

  event.cancelBubble = true ;
}


function toggle_display_tips()
{
  display_tips = ! display_tips ;
  if ( ! display_tips )
    hide_the_tip_real() ;
}

function do_move_column_right()
{
  var x ;
  if (the_current_cell.col == nr_cols - 1 )
    x = the_current_cell.data_col - 1 ;
  var col = the_current_cell.col ;
  var column = the_current_cell.column ;
  the_current_cell.cursor_right() ;
  right_column(column) ;
  if ( col == nr_cols - 1 )
    next_page_horizontal_data_col = x ;
}

function do_move_column_left()
{
  var col = the_current_cell.col ;
  var column = the_current_cell.column ;
  the_current_cell.cursor_left() ;
  left_column(column) ;
  if ( col === 0 )
    next_page_horizontal_data_col = 0 ;
}


// Set comment

function comment_change(data_lin, data_col, comment, td)
{
  create_column(columns[data_col]) ;
  add_a_new_line(data_lin) ;

  lines[data_lin][data_col].set_comment(comment);
  var col_id = columns[data_col].the_id ;
  var lin_id = lines_id[data_lin] ;
  append_image(td, 'comment_change/' + col_id + '/' +
	       lin_id + '/' + encode_uri(comment)) ;
}

function comment_on_change()
{
  var input = the_comment ;

  if ( the_comment === undefined )
    return ;

  if ( lines[the_current_cell.data_lin][the_current_cell.data_col].comment == input.value )
    return ;

  if ( ! cell.modifiable() )
    {
      alert("Vous n'avez pas l'autorisation de modifier ce commentaire");
      return ;
    }
  
  the_current_cell.td.className += ' comment' ;
  comment_change(the_current_cell.data_lin, the_current_cell.data_col,
		 input.value, the_current_cell.td) ;
}

/* CSV */

function csv_cell_coma(x)
{
  if ( x.replace === undefined )
    return x + ',' ; // Number
  else
    return '"' + x.replace('"', '""') + '",' ;
}

function csv_cell_dot_coma(x)
{
  if ( x.replace === undefined )
    return x.toString().replace('.',',') + ';' ; // Number
  else
    return '"' + x.replace('"', '""') + '";' ;
}

function csv(csv_cell)
{
  var cols = columns.slice(0, add_empty_columns()) ;

  var s = '' ;
  for(var data_col in cols)
    s += csv_cell(columns[data_col].title) ;
  s += '\r\n' ;
  for(var data_col in cols)
    s += csv_cell(columns[data_col].type) ;
  s += '\r\n' ;
  for(var data_col in cols)
    s += csv_cell(columns[data_col].test_filter) ;
  s += '\r\n' ;
  for(var data_col in cols)
    s += csv_cell(columns[data_col].minmax) ;
  s += '\r\n' ;
  for(var data_col in cols)
    s += csv_cell(columns[data_col].weight) ;
  s += '\r\n' ;


  for(var data_line in filtered_lines)
    {
      var line = filtered_lines[data_line] ;
      for(var data_col in cols)
	{
	  s += csv_cell(line[data_col].value) ;
	}
      s += '\r\n' ;
    }

  my_csv(s) ;
}

function the_filters()
{
  var s = "" ;

  for(var data_col in columns)
    {
      column = columns[data_col] ;
      if ( column.filter !== '' )
	s += '<span class="hidden_on_paper">Filtre sur la colonne <B>' + column.title + '</B> : ' +
	  column.filter + '<BR></span>\n' ;
    }
  return s ;
}


function print_cell(x, i, prepend, data_col)
{
  var html_class = 'col' + data_col ;

  if ( i % zebra_step === 0 )
    html_class += ' separatorvertical' ;

  if ( prepend === undefined )
    prepend = '' ;

  if ( x.toFixed )
    {
      if ( data_col )
	{
	  if ( x < columns[data_col].color_red )
	    html_class += ' color_red' ;
	  if ( x > columns[data_col].color_green )
	    html_class += ' color_green' ;
	}
      x = tofixedlocal(x) ;
      html_class += ' number' ;
    }

  x = html(x) ;
  if ( x === '' )
    x = '&nbsp;' ;

  return '<TD CLASS="' + html_class + '">' + prepend + x + '</TD>' ;
}

function assert_name_sort()
{
  if ( tr_classname === undefined )
	return ; // Pas des étudiants
  if ( sort_columns[0].data_col != 2 )
	alert("La liste n'est pas dans l'ordre alpabétique des noms.") ;
}

function hide_class(c, add)
{
  var s = document.getElementById('computed_style') ;
  if ( s !== undefined )
    {
      var x = '.' + c + '{ display: none ; }' ;
      if ( add )
	s.textContent += x ;
      else
	s.textContent = x ;
    }
}

function show_class(c)
{
  var s = document.getElementById('computed_style') ;
  if ( s !== undefined )
      s.textContent = s.textContent.replace('.' + c + '{ display: none ; }',
					    '') ;
}

function display_on_signature_table(line)
{
  if ( line[0].value == '' && line[1].value == '' )
    return false ; // Empty line

  if ( tr_classname === undefined )
    return true ; // Not concept of registered student

  if ( line[tr_classname].value != 'non' )
    return true ; // The student is registered in the UE

  if ( popup_on_red_line )
    return false ; // Do not display unregistered student.

  return true ;
}

function signature_table(line_list, tt, pb, more)
{
  var i = 0 ;
  var salle ;

  for(var data_line in line_list)
    if ( display_on_signature_table(line_list[data_line]) )
	 i++ ;

  if ( more && more.substr(0,5) == 'Salle' )
    {
      salle = more.replace(/[^ ]* /,'') ;
      more = '' ;
    }
  else
    salle = '' ;

  var a = html_begin_head(false, pb, more) ;
  if ( salle && ! pb )
    a += '<small class="hidden_on_paper">Si la colonne qui est à droite de la colonne contenant le nom de la salle indique la place de l\'étudiant dans la salle, alors vous pouvez <a href="javascript:show_class(\'zz\')">faire apparaître la place de l\'étudiant sur la feuille démargement</a>.</small>' ;

  a += '<table width="100%" style="white-space: pre ;">' ;
  a += '<tr style="vertical-align:top;"><td width="75%">' ;
  a += '<p>Date/Heure/Durée de l\'examen :' ;
  a += "<p>Surveillants :" ;
  a += "<p>Salle : " + salle ;
  a += "<p>Nombre d'étudiants sur cette liste : <b>" + i + "</b>" ;
  a += "</td>" ;
  a += '<td><p>Nombre de présents :' ;
  a += "<p>Nombre de signatures :" ;
  a += "<p>Nombre de copies :" ;
  a += "</td></tr></table><p>" ;
  a += "<script>hide_class('zz');</script>" ;
  a += '<TABLE class="printer colored signature" style="white-space: pre">' ;
  a += '<THEAD><TR><TH>ID<TH>Nom<TH>Prénom' +
    '<TH class="zz">Place<p class="hidden_on_paper"><small><a href="javascript:hide_class(\'zz\',true)">Cacher cette colonne</a></small></p></TH>' +
    '<TH class="yy">Est présent<p class="hidden_on_paper"><small><a href="javascript:hide_class(\'yy\',true)">Cacher cette colonne</a></small></p></TH>' +
    '<TH class="xx">Signature copie rendue<p class="hidden_on_paper"><small><a href="javascript:hide_class(\'xx\',true)">Cacher cette colonne</a></small></p></TH></TR></THEAD>';

  var x ;
  i = 0 ;
  var col = next_column_from_data_col(the_current_cell.data_col) ;
  if ( col === undefined )
    col = 3 ;

  for(var data_line in line_list)
    {  
      var line = line_list[data_line] ;
      if ( ! display_on_signature_table(line) )
	continue ;
    
      i++ ;
      if ( i % zebra_step == 1 )
	s = '<TR CLASS="separator">' ;
      else
	s = '<TR>' ;

      s += print_cell(login_to_id(line[0].value), 1) ;
      s += print_cell(line[2].value, 1) ;
      s += print_cell(line[1].value, 1) ;
      s += '<TD class="zz">' + html(line[col].value) + '</TD>' ;
      s += '<TD class="yy">&nbsp;</TD><TD class="xx">&nbsp;</TD></TR>' ;
      a += s

      x = the_student_abjs[line[0].value] ;
      if ( x && x[2] )
	tt.push(line[1].value + ' ' + line[2].value + '<ul><li>'
		+ x[2].substr(0,x[2].length-1).replace(/\n/g,'<li>')
		+ '</ul>') ;
    }
  a += '</table>' ;
  return a ;
}

function signatures_page()
{
  assert_name_sort() ;
  var w = window_open() ;
  var tt = [] ;
  w.document.write( signature_table(filtered_lines, tt) ) ;
  
  if ( tt.length )
    w.document.write('<h2 style="page-break-before:always">Dispositions particulières</h2>' + tt);
  w.document.close() ;
  return w ;
}

function signatures_page_grp_seq()
{
  assert_name_sort() ;

  var g = grp_and_seq() ;
  var s = '' ;
  var t ;
  var w = window_open() ;
  var tt = [] ;
  var pb = '' ; // No page break for the first one

  for(var gs in g)
    {
      gs = g[gs] ;
      var grp = gs.split('\001')[1] ;
      var seq = gs.split('\001')[0] ;

      t = [] ;
      for(var data_lin in filtered_lines)
	{
	  line = filtered_lines[data_lin] ;
	  if ( line[0].value != '' && line[3].value == grp && line[4].value == seq)
	    t.push(line) ;
	}
      w.document.write(signature_table(t, tt, pb,
				       'séq. ' + seq + ", grp. " + grp) ) ;
      pb = ' style="page-break-before:always;clear:left"' ;
    }
  
  if ( tt.length )
    w.document.write('<h2 style="page-break-before:always">Dispositions particulières</h2>' + tt);
  w.document.close() ;
  return w ;
}

function signatures_page_per_column()
{
  assert_name_sort() ;

  var g = values_in_a_column(the_current_cell.column) ;
  var s = '' ;
  var t ;
  var w = window_open() ;
  var tt = [] ;
  var pb = '' ; // No page break for the first one

  for(var gs in g)
    {
      gs = g[gs] ;

      t = [] ;
      for(var data_lin in filtered_lines)
	{
	  line = filtered_lines[data_lin] ;
	  if ( line[0].value != ''
	       && line[the_current_cell.data_col].value == gs)
	    t.push(line) ;
	}
      w.document.write(signature_table(t, tt, pb, 'Salle ' + gs) ) ;
      pb = ' style="page-break-before:always;clear:left"' ;
    }
  
  if ( tt.length )
    w.document.write('<h2 style="page-break-before:always">Dispositions particulières</h2>' + tt);
  w.document.close() ;
  return w ;
}

function print_page(w)
{
  var hide_link = '<TD class="hidden_on_paper"><a href="#" onclick="this.parentNode.parentNode.style.display=\'none\';return false"><small>Cacher</small></a>' ;
  assert_name_sort() ;
  var cols = column_list_all() ;

  if ( w === undefined )
    w = window_open() ;
  
  var s = html_begin_head() ;
  s += '<div class="hidden_on_paper">' +
    '<p>Pour importer ces données dans votre tableur favori, ' +
    'il suffit de copier la page (Ctrl-A Ctrl-C) ' +
    'et de la coller (Ctrl-V) dans votre tableur. ' +
    'Attention, le copier/collé copie les colonnes cachées. ' +
    'En cas de problème avec les nombres : ' +
    '<a href="javascript:replace_coma_by_dot()">remplacer les \',\' ' +
    'par des \'.\'</a></p>' +
    '<p><b>N\'utilisez pas cette méthode pour importer ' +
    'des notes dans APOGÉE</b> utilisez l\'export de colonne ' +
    '(Exp.) dans le cadre «Colonne»</p></div>' ;
  if ( table_attr.comment )
    s += '<p>Petit message : <b>' + html(table_attr.comment) + '</b></p>' ;
  s += '<TABLE class="printer colored">' ;
  s += '<THEAD><TR  class="hidden_on_paper"><TD>&nbsp;\n' ;
  var minmax, test_filter ;
  for(var col in cols)
    s += print_cell('', col,
		    '<a href="javascript:hide_class(\'col' + cols[col] + '\',true)"><small>Cacher</small></a>', cols[col]
		    ) ;
  s += '</TR><TR CLASS="title">\n' + hide_link ;
  for(var col in cols)
    s += print_cell(columns[cols[col]].title, col, '', cols[col]) ;
  s += '</TR>\n<TR CLASS="type">\n' + hide_link ;
  for(var col in cols)
    s += print_cell(columns[cols[col]].type, col, '', cols[col]) ;
  s += '</TR>\n<TR CLASS="test">\n' + hide_link ;
  for(var col in cols)
    {
      if ( column_modifiable_attr('minmax', columns[cols[col]]) )
	minmax = columns[cols[col]].minmax ;
      else
	minmax = '' ;
      if ( column_modifiable_attr('set_test_filter', columns[cols[col]]) )
	test_filter = columns[cols[col]].test_filter ;
      else
	test_filter = '' ;
      s += print_cell(minmax + ' ' + test_filter, col, '', cols[col]) ;
    }
  s += '</TR>\n<TR CLASS="visibility_date">\n' + hide_link ;
  for(var col in cols)
    s += print_cell(columns[cols[col]].visibility_date, col, '', cols[col]) ;
  s += '</TR>\n<TR CLASS="weight">\n' + hide_link ;
  for(var col in cols)
    {
      if ( columns[cols[col]].real_type.set_weight != unmodifiable )
	s += print_cell(columns[cols[col]].weight, col,
			'Poids:', cols[col]) ;
      /* '<img src="' + url + '/weight.png">', cols[col]) ; */
      else
	s += print_cell('', col, '', cols[col]) ;
    }
  for(var col in cols)
    if ( columns[cols[col]].empty_is )
      {
	s += '</TR>\n<TR CLASS="empty_is">\n' + hide_link ;
	for(var col in cols)
	  if ( columns[cols[col]].empty_is )
	    s += print_cell(columns[cols[col]].empty_is, col, '&#8709;=',
			    cols[col]);
	  else
	    s += print_cell('', col, '', cols[col]) ;
	break ;
      }

  s += '</TR>\n<TR CLASS="comment">\n' + hide_link ;
  for(var col in cols)
    s += print_cell(columns[cols[col]].comment, col, '', cols[col]) ;

  s += '</TR></THEAD><TBODY><TR CLASS="separator">' ;
  w.document.write(s) ;
  
  var i = 0 ;
  for(var data_line in filtered_lines)
    {      
      var line = filtered_lines[data_line] ;
      s = hide_link ;
      for(var col in cols)
	{
	  if ( col === 0 )
	    s += print_cell(login_to_id(line[cols[col]].value), col,'',cols[col]);
	  else
	    s += print_cell(line[cols[col]].value, col, '', cols[col]) ;
	}
      s += '</TR>\n' ;
      i++ ;
      if ( i % zebra_step === 0 )
	s += '<TR CLASS="separator">' ;
      else
	s += '<TR>' ;
      w.document.write(s) ;
    }
  w.document.write('</TR></TBODY></TABLE>') ;
  w.document.close() ;
  return w ;
}

function a_picture(line)
{
  var url = '<A HREF="' + suivi + '/' + line[0].value + '">' ;
  var firstname ;
  if ( line[1].value.length >= 2 )
    firstname = line[1].value.substr(0,1)+ line[1].value.substr(1).toLowerCase() ;
  else
    firstname = line[1].value ;
    
  return '<DIV CLASS="trombinoscope">' + url +
    '<IMG SRC="' + student_picture_url(line[0].value) + '"><BR>' +
    firstname + '<br>' +
    line[2].value + '</A></DIV>' ;
}

function students_pictures()
{
  var s = '' ;

  for(var data_lin in filtered_lines)
    {
      line = filtered_lines[data_lin] ;
      if ( line[0].value !== '' )
	s += a_picture(line) ;
    }
  
  var w = window_open() ;
  w.document.open('text/html') ;
  w.document.write(html_begin_head() + s) ;
  w.document.close() ;
  return w ;
}

function goto_resume()
{
  window_open('/=' + ticket + '/' + year + '/' + semester + '/' + ue + '/resume');
}


function grp_and_seq()
{
  var g = {} ;
  for(var data_lin in filtered_lines)
    {
      line = filtered_lines[data_lin] ;
      if ( line[0].value !== '' )
	g[line[4].value + '\001' + line[3].value] = true ;
    }
  tabl = [] ;
  for(var gg in g)
    tabl.push(gg) ;
  tabl.sort() ;
  return tabl ;
}

function values_in_a_column(column)
{
  var g = {} ;
  var data_col = column.data_col ;
  for(var data_lin in filtered_lines)
    {
      g[filtered_lines[data_lin][data_col].value] = true ;
    }
  var t = [] ;
  for(var i in g)
    t.push(i) ;
  return t
}

function students_pictures_per_grp_seq()
{
  var g = grp_and_seq() ;
  var s = '' ;

  for(var gs in g)
    {
      gs = g[gs] ;
      var grp = gs.split('\001')[1] ;
      var seq = gs.split('\001')[0] ;
      s += '<h2 style="page-break-before:always;clear:left">' + year + ' ' + semester +
	' ' + ue +  ' séq. ' + seq + ", grp. " + grp + "</h2>" ;
      s += '<div>' ;
      for(var data_lin in filtered_lines)
	{
	  line = filtered_lines[data_lin] ;
	  if ( line[0].value != '' && line[3].value == grp && line[4].value == seq)
	    s += a_picture(line) ;
	}
      s += '</div>' ;
    }
  var w = window_open() ;
  w.document.open('text/html') ;
  w.document.write(html_begin_head() + s) ;
  w.document.close() ;
  return w ;
}



function histo_image(nr, maxmax)
{
  return '<img HEIGHT="' +
    (nr*histo_image_height)/maxmax + '" src="' + url + '/bug.png"><br>' + nr ;
}

// pb = page break
function html_begin_head(hide_title, pb, more)
{
  var s = '' ;

  if ( ! pb )
    s = '<html><head>\n' +
      '<link rel="stylesheet" href="'+url + '/style.css" type="text/css">\n' +
      '<link rel="stylesheet" href="'+url + '/hidden.css" type="text/css">\n' +
      '<script src="' + url + '/utilities.js"></script>\n' +
      '<script src="' + url + '/middle.js"></script>\n' +
      '<script src="' + url + '/lib.js"></script>\n' +
      '<script src="' + url + '/types.js"></script>\n' +
      '<script src="' + url + '/abj.js"></script>\n' +
      '<style id="computed_style"></style>\n' +
      '<title>' + ue + ' ' + year + ' ' + semester + '</title>' +
      '</head>' ;

  if ( ! pb )
    pb = '' ;
  if ( ! more )
    more = '' ;
  else
    more = '<br>' + more ;

  if ( ! hide_title )
    {
      s += '<body>' ;
      s += '<h1 ' +pb + '>' + year + ' ' + semester + ' '
	+ ue + '<br>' +	html(table_attr.table_title) + more + '</h1>\n' + the_filters() ;
    }

  return s ;
}



function compute_histogram(data_col)
{
  var stats = new Stats(columns[data_col].min, columns[data_col].max,
			columns[data_col].empty_is) ;
  for(var line in filtered_lines)
    if ( filtered_lines[line][0].value || filtered_lines[line][1].value )
      stats.add(filtered_lines[line][data_col].value) ;
  return stats ;
}

function statistics()
{
  var w = window_open() ;
  w.document.open('text/html') ;

  w.document.write(html_begin_head()) ;
  w.document.write('Statistiques des colonnes de type note') ;

  w.document.write('<TABLE class="stat colored"><TR><TH>Colonne</TH>' +
		   '<TH>Nb<br>Notes' +
		   '</TH><TH>Statistiques</TH>' +
		   '<TH>Histogramme</TH></TR>') ;
  var cls = column_list_all() ;
  for(var data_col in cls)
    {
      data_col = cls[data_col] ;
      column = columns[data_col] ;
      if ( ! column.real_type.should_be_a_float)
	continue ;
      w.document.write('<TR><TH>' + column.title + '</TH>') ;

      var stats = compute_histogram(data_col) ;

      w.document.write('<TD>' + stats.nr  +  '</TD><TD>') ;
      /* XXX
      if ( nr != 0 )
	w.document.write(stats.html_resume()) ;
      */

      var maxmax = stats.maxmax() ;

      var h = '<TD><TABLE class="histogram colored"><tbody><tr>' ;
      h += '<TD COLSPAN="2">' + histo_image(stats.nr_abi, maxmax) + '</TD>' ;
      h += '<TD COLSPAN="2">' + histo_image(stats.nr_abj, maxmax) + '</TD>' ;
      h += '<TD COLSPAN="2">' + histo_image(stats.nr_ppn, maxmax) + '</TD>' ;
      h += '<TD COLSPAN="2">' + histo_image(stats.nr_nan, maxmax) + '</TD>' ;
      h += '<TD></TD>' ;
      for(i=0; i<20; i++)
	h += '<TD COLSPAN="2">' +
	  histo_image(stats.histogram[i], maxmax) + '</TD>' ;
      h += '<TD></TD></TR><TR>' ;
      h += '<TD COLSPAN="2">' + abi + '</TD>' ;
      h += '<TD COLSPAN="2">' + abj + '</TD>' ;
      h += '<TD COLSPAN="2">' + ppn + '</TD>' ;
      h += '<TD COLSPAN="2">???</TD>' ;
      for(i=0; i<21; i++)
	{
	  var v = i / 20 * (column.max-column.min) + column.min ;
	  if ( v > 100 )
	    v = v.toFixed(0) ;
	  else
	    v = v.toFixed(1).toString().replace('.0','') ;

	  h += '<TD COLSPAN="2">' + v + '</TD>' ;
	}
      h += '</TR><TR>' ;
      for(i=0; i<50; i++)
	h += '<td width="20px"></td>' ;
      h += '</TR></TBODY></TABLE>' ;
      
      w.document.write(h + '</TD></TR>') ;
      
    }
  w.document.write('</TABLE>') ;	  

 
  var maxmax = 1 ;
  var cols = [] ;
  for(var data_col in cls)
      {
	data_col = cls[data_col] ;
	column = columns[data_col] ;

	if ( column.type != 'Prst' && column.type != 'Bool' )
	  continue ;
	var nr_pre = 0 ;
	var nr_abi = 0 ;
	var nr_abj = 0 ;
	var nr_ppn = 0 ;
	var nr_nan = 0 ;
	var nr_yes = 0 ;
	var nr_no = 0 ;
	var nr = 0 ;
	var i ;
	for(var line in filtered_lines)
	  {
	    nr++ ;
	    switch(filtered_lines[line][data_col].value)
	      {
	      case pre : nr_pre++ ; break ;
	      case yes : nr_yes++ ; break ;
	      case no  : nr_no++  ; break ;
	      case abi : nr_abi++ ; break ;
	      case abj : nr_abj++ ; break ;
	      case ppn : nr_ppn++ ; break ;
	      default: nr_nan++ ;
	      }
	  }
	if ( nr_pre > maxmax ) maxmax = nr_pre ;
	if ( nr_abi > maxmax ) maxmax = nr_abi ;
	if ( nr_abj > maxmax ) maxmax = nr_abj ;
	if ( nr_ppn > maxmax ) maxmax = nr_ppn ;
	if ( nr_yes > maxmax ) maxmax = nr_yes ;
	if ( nr_no  > maxmax ) maxmax = nr_no  ;
	if ( nr_nan > maxmax ) maxmax = nr_nan ;

	cols.push([column, nr_pre, nr_abi,  nr_abj, nr_ppn , nr_yes, nr_no, nr_nan]) ;
      }

  var h = "<p>Statistiques sur les présences et booléens." ; 
  h += '<TABLE class="colored alignbottom"><tbody>' ;
  h += '<tr><th width="1%">Titre</th>' ;
  for(var c in cols)
    h += '<th width="10%">' + cols[c][0].title + '</th>' ;
  h += '</tr><th>PRST</th>' ;
  for(var c in cols)
    h += '<td>' + histo_image(cols[c][1], maxmax) + '</td>' ;
  h += '</tr><th>ABINJ</th>' ;
  for(var c in cols)
    h += '<td>' + histo_image(cols[c][2], maxmax) + '</td>' ;
  h += '</tr><th>ABJUS</th>' ;
  for(var c in cols)
    h += '<td>' + histo_image(cols[c][3], maxmax) + '</td>' ;
  h += '</tr><th>PPNOT</th>' ;
  for(var c in cols)
    h += '<td>' + histo_image(cols[c][4], maxmax) + '</td>' ;
  h += '</tr><th>OUI</th>' ;
  for(var c in cols)
    h += '<td>' + histo_image(cols[c][5], maxmax) + '</td>' ;
  h += '</tr><th>NON</th>' ;
  for(var c in cols)
    h += '<td>' + histo_image(cols[c][6], maxmax) + '</td>' ;
  h += '</tr><th>???</th>' ;
  for(var c in cols)
    h += '<td>' + histo_image(cols[c][7], maxmax) + '</td>' ;
  h += '</tr></tbody></table>' ;

  if ( cols.length !== 0 )
    w.document.write(h) ;
 
  w.document.close() ;
  return w ;
}

function notes_columns()
{
  var cols = [] ;

  var cls = column_list_all() ;

  for(var data_col in cls)
    {
      data_col = cls[data_col] ;
      if ( columns[data_col].real_type.should_be_a_float
	   && ! columns[data_col].is_empty )
	{
	  var a = {min: 1000000, max: -1000000, sum: 0, nr: 0,
		   nr_nan:0, nr_pre:0, nr_abi:0, nr_abj: 0, nr_ppn: 0,
		   sum2: 0} ;
	  a.data_col = Number(data_col) ;
	  cols.push(a) ;
	}
    }
  return cols ;
}

function virtual_table_common_begin()
{
  var p = '{' ;
  for(var i in preferences)
    p += i + ':"' + preferences[i] + '",' ;
  p = p.substr(0,p.length-1) + '};' ;

  var a = '{' ;
  for(var i in table_attr)
    a += i + ':"' + table_attributes[i].formatter(table_attr[i]) + '",' ;
  a = a.substr(0,a.length-1) + '}' ;

  return html_begin_head(true) +
    head_html() +
    '<script>\n' +
    'page_id = "" ;\n' +
    'check_down_connections_interval = 0 ;\n' +
    'url = "' + url.split('/=')[0] + '";\n' +
    'my_identity = "' + my_identity + '" ;\n' +
    'year = "' + year + '" ;\n' +
    'semester = "' + semester + '" ;\n' +
    'ticket = "' + ticket + '" ;\n' +
    'ue = "VIRTUALUE" ;\n' +
    'root = [];\n' +
    'suivi = "' + suivi + '";\n' +
    'version = "' + version + '" ;\n' +
    'preferences = ' + p + ';\n' +
    'columns = [] ;\n' +
    'lines = [] ;\n' +
    'lines_id = [] ;\n' +
    'adeweb = {};\n' + // XXX should not be here (LOCAL/spiral.py)
    'table_attr = ' + a + ';\n' +
    '</script>\n' +
    new_interface() ;
}

// Function to enhance and coordinate with tail.html
function virtual_table_common_end()
{
  return tail_html() ;
}

function XX(x) { return x * 900 + 40 ; }
function YY(y) { return 660 - y * 1300 ; }
function svgText(x, y, text, node_class)
{
  if ( node_class )
    node_class = ' class="' + node_class + '"' ;
  else
    node_class = '' ;
  return '<text x="' + XX(x) + '" y="' + YY(y) + '"' + node_class + '>'
    + text + '</text>' ;
}
function svgTextVertical(x, y, text, node_class)
{
  if ( node_class )
    node_class = ' class="' + node_class + '"' ;
  else
    node_class = '' ;
  return '<g transform="translate(' + XX(x) + ',' + YY(y) + ') rotate(-90)">'
    + '<text' + node_class + '>' + text + '</text></g>' ;
}
function svgLine(x1, y1, x2, y2)
{
  return '<line x1="' + XX(x1) + '" y1="' + YY(y1) +
    '" x2="' + XX(x2) + '" y2="' + YY(y2) + '"/>' ;
}
function svgTranslate(x, y, what, node_class)
{
  if ( node_class )
    node_class = ' class="' + node_class + '"' ;
  else
    node_class = '' ;
  return '<g transform="translate(' + XX(x) + ',' + YY(y) + ')"' +
    node_class + ' onmouseover="svgMouseOver(this)">' + what + '</g>' ;
}
function svgGrid(label_x, label_y, label, x_tics, y_tics)
{
  var grid, i, ii, width ;

  if ( x_tics === undefined )
    x_tics = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20] ;

  width = 1/20. * (x_tics.length-1) ;

  grid = svgText(0, -0.015,  label_x, 'label') +
    svgTextVertical(-0.025, 0, label_y, 'label') +
    svgText(0, -0.025, label, 'label') ;
    
  for(var i=0; i < x_tics.length; i++)
    {
      ii = i/20. ;
      grid += svgLine(ii,0, ii, 1) ;
      grid += svgText(ii, -0.007, html(x_tics[i]), 'tic') ;
    }
  for(var i=0; i <= 20; i++)
    {
      ii = i/40. ;
      grid += svgLine(0,ii, width,ii) ;
      if ( y_tics )
	grid += svgText(-0.01, ii, y_tics[i], 'tic') ;
      else
	grid += svgText(-0.01, ii, i/2, 'tic') ;
    }
  return grid ;
}


/*
 * Compute the statistics per groups and columns
 */

function compute_statistics_per_group()
{
  var grps = {} ;

  for(var data_line in filtered_lines)
    {
      line = filtered_lines[data_line] ;
      var grp = line[3].value + line[4].value ;
      if ( grps[grp] === undefined )
	grps[grp] = {nr: 0, cols: notes_columns()} ;
      grps[grp].nr++ ;
      for(var col in grps[grp].cols)
	{
	  col = grps[grp].cols[col] ;
	  var v = line[col.data_col].value ;
	  if ( col.notes === undefined )
	    col.notes = [] ;
	  if ( v === '' )
	    v = columns[col.data_col].empty_is ;

	  if ( v === '' )
	    col.notes.push('_') ;
	  else
	    col.notes.push(v) ;
	  if ( v === '' ) { col.nr_nan++ ; continue ; }
	  if ( v == pre ) { col.nr_pre++ ; continue ; }
	  if ( v == abi ) { col.nr_abi++ ; continue ; }
	  if ( v == abj ) { col.nr_abj++ ; continue ; }
	  if ( v == ppn ) { col.nr_ppn++ ; continue ; }
	  v = a_float(v) ;
	  if ( isNaN(v) ) { col.nr_nan++ ; continue ; }
	  if ( v < col.min ) col.min = v ;
	  if ( v > col.max ) col.max = v ;
	  col.sum += v ;
	  col.sum2 += v*v ;
	  col.nr++ ;
	}
    }
  for(var grp in grps)
    {
      for(var col in grps[grp].cols)
	{
	  col = grps[grp].cols[col] ;
	  if ( col.nr && col.min != 1000000 )
	    {
	      var column = columns[col.data_col] ;
	      col.avg_real = col.sum/col.nr ;
	      col.avg = (col.avg_real-column.min) / (column.max-column.min) ;
	      col.vari_real = Math.pow(col.sum2/col.nr
				 - col.sum*col.sum/col.nr/col.nr
				 , 0.5) ;
	      col.vari = col.vari_real/(column.max-column.min) ;
	    }
	  else
	    {
	      col.avg = '' ;
	      col.vari = '' ;
	    }
	}
    }
  return grps ;
}

function statistics_per_group()
{
  var avg, vari, col, x, nr, date, auth ;
  var grps = compute_statistics_per_group() ;
  var s ;

  s = 'lines = [] ;' ;
  for(var grp in grps)
    {
      s += 'lines.push([C("' + grp + '"),C(' + grps[grp].nr + ')' ;
      
      for(var col in grps[grp].cols)
	{
	  col = grps[grp].cols[col] ;

	  x = '' ;
	  nr = Math.ceil((col.notes.length+1)/3) ;
	  for(var i in col.notes)
	    {
	      if ( i % nr == (nr-1) )
		x += '\\n' ;
	      else
		x += ' ' ;
	      x += col.notes[i] ;
	    }
	  x += '\\n\\n' ;
	  if ( col.nr_ppn )
	    x += col.nr_ppn + ' PPN, ' ;
	  if ( col.nr_abi )
	    x += col.nr_abi + ' ABI, ' ;
	  if ( col.nr_abj )
	    x += col.nr_abj + ' ABJ, ' ;
	  if ( col.nr_pre )
	    x += col.nr_pre + ' PRE, ' ;
	  if ( col.nr_nan )
	    x += col.nr_nan + ' Vides' ;
	  if ( col.avg !== '' )
	    avg = tofixed(col.avg_real) ;
	  else
	    avg = '""' ;
	  if ( col.vari !== '' )
	    vari = tofixed(col.vari_real) ;
	  else
	    vari = '' ;
	  auth = '' ;
	  date = '' ;
	  if ( col.nr < grps[grp].nr * 0.75 )
	    {
	      date = today ;
	      if ( col.nr > grps[grp].nr * 0.5 )
		auth = '*' ;
	    }

	  s += ',C(' + avg + ',"' + auth + '","' + date + '","' + col.nr +' notes, min=' + col.min +
	    ', max=' + col.max + ', écart-type=' + vari +
	    '","' + x.replace(/\042/g, '\\"') + '")\n' ; // \042 = "
	}
      s += ']) ;' ;
    }

  s = virtual_table_common_begin() + virtual_table_common_end() + '<script>' +
    'function delayed_init() {\n' +
    s +
    'do_not_read_option = true ;' +
    'lib_init() ;' +
    'for(var i=0; i<2; i++) add_empty_column(true);' +
    'columns[0].title = "Groupe" ;' +
    'columns[0].freezed = "F" ;' +
    'columns[0].type = "Text" ;' +
    'columns[0].minmax = "[0;100]" ;' +
    'columns[0].green = "0" ;' +
    'columns[0].red = "100" ;' +
    'columns[1].title = "#étudiants" ;' +
    'columns[1].minmax = "[0;NaN]" ;' +
    'columns[1].freezed = "F" ;' ;

  var t, column, col ;
  for(var c in grps[grp].cols)
    {
      col = grps[grp].cols[c] ;
      column = columns[col.data_col] ;
      t = column.title ;
      s += 'add_empty_column(true);\n' +
	'column = columns[' + (Number(c)+2) +'] ;\n' +
	'column.title = "' + t + ' Moyenne";\n' +
	'column.minmax = "[' + column.min + ';' + column.max + ']";' +
	'column.green = "NaN" ;\n' +
	'column.red = "NaN" ;\n' ;
    }

  // The delayed function call is only here for IE
  // It is absolutely useles.
  s += 'lines_id=[];for(var i in lines) { lines_id["x"+i] = lines[i] ; };\n' +
    'table_attr.default_nr_columns = ' + (Number(c)+3)  + ' ;\n' +
    '// set_columns_filter("~Moyenne") ;\n' +
    'table_attr.comment = "Gras : gris<75% des notes, noir<50% des notes" ;\n' +
    'table_attr.table_title = "Statistiques par groupe" ;\n' +
    'runlog(columns, lines) ;\n' +
    '}\n' +
    'setTimeout("delayed_init()",100) ;\n' +
    '</script>'
    ;

  var svg = '', rgb, rgb2, i=0, r, grid ;

  grid = svgGrid("Moyennes des notes des groupes",
		 "Écart-type des notes des groupes",
		 "Rectangle : La taille : taille du groupe, couleur interne : groupe, bord noir : colonne identique") ;
   
  var nr_grps = dict_size(grps) ;
  for(var grp in grps)
    {
      rgb = hls2rgb(i/nr_grps, 0.7, 1) ;
      i++ ;
      for(var c in grps[grp].cols)
	{
	  col = grps[grp].cols[c] ;
	  column = columns[col.data_col] ;
	  if ( col.nr > 1 )
	    {
	      r = col.nr/2 ;
	      svg += svgTranslate(col.avg, col.vari,
				  '<rect x="' + (-r) + '" y="' + (-r)
				  + '" width="' + 2*r +
				  '" height="' + 2*r + '" style="fill:' + rgb +
				  '"/>' +
				  '<text y="-2">' + html(grp) + '</text>' +
				  '<text y="8">' +
				  html(columns[col.data_col].title) +
				  '</text>') ;
	    }
	}
    }
	  

  svg = 'data:image/svg+xml;utf-8,' +
    base64('<?xml version="1.0" encoding="UTF-8" standalone="no"?>' +
	   '<svg xmlns="http://www.w3.org/2000/svg">' +
	   '<style>' +
	   'svg { background: white; }' +
	   'text.tic { font-size: 10px ; text-anchor: middle}' +
	   'g.node g.show text { opacity:1; font-weight: bold; font-size:12px}' +
	   'g.node g.showcol rect { stroke-opacity:1}' +
	   'g.node text { font-size: 12px; text-anchor: middle; opacity:0}' +
	   'text.label { font-size: 12px ; text-anchor: start}' +
	   'rect { fill-opacity: 0.7; stroke-opacity: 0 ;stroke-width:3 ; stroke: #666; }' +
	   'line { stroke-width: 1px; stroke-opacity:1;stroke:#888}' +
	   '@media print { g.node text { opacity:1 } }' +
	   '</style>' +
	   '<script>' +
	   'function svgMouseOver(t)' +
	   '{' +
	   'var grp = t.childNodes[1].textContent ;' +
	   'var col = t.childNodes[2].textContent ;' +
	   'var top = t.parentNode.childNodes ;' +
	   'var cls ;' +
	   'for(var i in top)' +
	   '   {' +
	   '   i = top[i] ;' +
	   '   if ( i.childNodes === undefined ) continue ;' +
	   '   if ( grp === i.childNodes[1].textContent )' +
	   '         cls = "show" ;' +
	   '   else' +
	   '         cls = "" ;' +
	   '   if ( col == i.childNodes[2].textContent )' +
	   '        cls += " showcol" ;' +
	   '   i.setAttribute("class",cls) ;' +
	   '   }' +
	   '}' +
	   '</script>' +
	   '<g transform="translate(0,0)">' +
	   grid + '<g class="node">' + svg + '</g>' +
	   '</g></svg>') ;

  s +='<object type="image/svg+xml" height="700" width="100%" data="' + svg + '"></object>';

  return new_window(s, 'text/html') ;

}


function table_graph()
{
  var s, i, column, v ;

  s = '' ;
  i = 0 ;
  var cols = notes_columns() ;
  for(var line in filtered_lines)
    {
      line = filtered_lines[line] ;
      rgb = hls2rgb(i/filtered_lines.length, 0.5, 1) ;
      i++ ;
      s += '<path d="M ' ;
      for(var c in cols)
	{
	  column = columns[cols[c].data_col] ;
	  v = line[cols[c].data_col].value ;
	  if ( isNaN(v) )
	       continue ;
	  s += XX(c/20.).toFixed(1) + ' ' +
	    YY((v - column.min)/(column.max-column.min)/2).toFixed(1) + ' L ' ;
	}
      s = s.replace(/ L $/,'') + '" style="stroke:' + rgb + '"/>\n' ;
    }
  var cc = [] ;
  for(var c in cols)
    cc[c] = columns[cols[c].data_col].title ;
  grid = svgGrid("Colonnes du tableau",
		 "Valeur des cellules (normalisées entre 0 et 20)",
		 "",
		 cc,
		 [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
		 ) ;

  svg = '<object type="image/svg+xml;utf-8" height="700" data="data:image/svg+xml;utf-8,' +
    base64('<?xml version="1.0" encoding="UTF-8" standalone="no"?>' +
	   '<svg xmlns="http://www.w3.org/2000/svg">' +
	   '<style>' +
	   'svg { background: white; }' +
	   'text.tic { font-size: 10px ; text-anchor: middle}' +
	   'text.label { font-size: 12px ; text-anchor: start}' +
	   'line { stroke-width: 1px; stroke-opacity:1;stroke:#888}' +
	   'path { fill: none;stroke-width: 1px; stroke-opacity:1}' +
	   '@media print { }' +
	   '</style>' +
	   '<script>' +
	   '</script>' +
	   '<g transform="translate(0,0)">' +
	   grid + '<g class="node">' + s + '</g>' +
	   '</g></svg>') + '"></object>' ;

  return new_window(svg, 'text/html') ;
}


function statistics_authors()
{
  var s, v, cell, author, column ;

  var t = [] ;
  for(var data_col in columns)
    {
      column = columns[data_col] ;
      if ( column.author == '*' || column.author === '' )
	continue ;
      /*
	if ( column.type != 'Note' && column.type != 'Prst')
	continue ;
      */
      for(var line in filtered_lines)
	{
	  line = filtered_lines[line] ;
	  cell = line[data_col] ;
	  author = cell.author ;
	  if ( author == '*' || author === '' || cell.value === '' )
	    continue ;
	  if ( t[author] === undefined )
	    t[author] = {nr:0, nr_numbers:0, sum:0, sum2: 0} ;
	  s = t[author] ;
	  s.nr++ ;
	  v = a_float(cell.value) ;
	  if ( ! isNaN(v) )
	    {
	      v = (v - column.min) / (column.max - column.min) ;
	      s.nr_numbers++ ;
	      s.sum += v ;
	      s.sum2 += v*v ;
	    }
	}
    }

  var c = 'lines = [];' ;
  var i, max_nr=0, max_nr_numbers=0, max_stddev=0 ;
  var average, stddev ;
  i = 0 ;
  for(var author_name in t)
    {
      author = t[author_name] ;
      c += 'lines.push([' ;
      c += 'C("' + author_name + '"),' ;

      c += 'C(' + author.nr + '),' ;
      if ( author.nr > max_nr )
	max_nr = author.nr ;

      c += 'C(' + author.nr_numbers + '),' ;
      if ( author.nr_numbers > max_nr_numbers )
	max_nr_numbers = author.nr_numbers ;

      average = 20 * author.sum / author.nr_numbers ;
      c += 'C(' + tofixed(average) + '),' ;

      stddev = 20 * Math.pow(author.sum2 / author.nr_numbers -
			author.sum*author.sum/author.nr_numbers
			/author.nr_numbers, 0.5) ;

      c += 'C(' + tofixed(stddev) + ')]);\n' ;  
      if ( stddev > max_stddev )
	max_stddev = stddev ;
    }
  // c = c.substr(0,c.length-1) ;
  c += 'lines_id = [] ; for(var i in lines) { lines_id["x"+i] = lines[i] ; };\n' ;


  // The delayed function call is only here for IE
  // It is absolutely useles.
  v = virtual_table_common_begin() + virtual_table_common_end() +
    '<script>' +
    'function delayed_init() {\n' +
    'do_not_read_option = true ;' +
    'lib_init() ;' +
    'for(var i=0; i<5; i++) add_empty_column(true);\n' +
    'columns[0].title = "Enseignant";\n' +
    'columns[1].title = "#Cellules";\n' +
    'columns[1].type = "Note";\n' +
    'columns[1].minmax = "[0;' + Number(max_nr.toFixed(0)) + ']";\n' +
    'columns[2].title = "#Notes";\n' +
    'columns[2].type = "Note";\n' +
    'columns[2].minmax = "[0;' +Number(max_nr_numbers.toFixed(0)) + ']";' +
    'columns[3].title = "Moyenne";\n' +
    'columns[3].type = "Note";\n' +
    'columns[3].minmax = "[0;20]";' +
    'columns[4].title = "Écart_Type";\n' +
    'columns[4].type = "Note";\n' +
    'columns[4].minmax = "[0;' +Number(max_stddev.toFixed(0)) + ']";' +
    c +
    'table_attr.table_title = "Statistiques enseignants" ;' +
    'table_attr.default_nr_columns = 5 ;\n' +
    'runlog(columns, lines) ;' +
    '}\n' +
    'setTimeout("delayed_init()", 100) ;\n' +
    '</script>\n'

  return new_window(v, 'text/html') ;
}

// XXX yet done somewhere else
function student_search(id)
{
  for(var data_lin in lines)
    if ( lines[data_lin][0].value == id )
      return Number(data_lin) ;

  id = login_to_id(id) ;
  for(var data_lin in lines)
    if ( lines[data_lin][0].value == id )
      return Number(data_lin) ;
}


function full_import()
{
  var cls = column_list_all() ;

  if ( filtered_lines.length !== 0 )
    {
      alert("Il est interdit d'importer dans une table non vide") ;
      return ;
    }

  var import_lines = popup_value() ;
  var line, nr_cols, new_lines, new_lines_id ;
  new_lines = [] ;
  for(var a in import_lines)
    {
      var line = parseLineCSV(import_lines[a]) ;
      if ( nr_cols === undefined )
	nr_cols = line.length ;
      else
	if ( line.length > nr_cols )
	  {
	    alert('Nombre de colonnes variable... La première ligne doit être la plus longue.') ;
	    return ;
	  }
	else
	  {
	    while( line.length != nr_cols )
	      line.push('') ;
	  }
      new_lines.push(line) ;
    }
  if ( ! confirm("Confirmez l'importation de " + new_lines.length +
		 ' lignes et de ' + nr_cols + ' colonnes ?\n\nAucun retour en arrière ne sera possible.\nAucun autre import CSV ne sera possible.\n\nCet importation peut prendre ' + (new_lines.length*nr_cols)/10 + ' secondes') )
    return ;


  for(var data_col=0; data_col < nr_cols; data_col++)
    {
      if ( columns[data_col] === undefined )
	add_empty_column() ;
      column_attr_set(columns[data_col], 'type', 'Text')
      column_attr_set(columns[data_col], 'title', 'csv_' + data_col)
      create_column(columns[data_col]) ;
    }

  for(var data_line in new_lines)
    for(var data_col=0 ; data_col < nr_cols ; data_col++ )
      cell_set_value_real(data_line, data_col,
			  new_lines[data_line][data_col]) ;

  the_current_cell.jump(nr_headers,0,false,0,0) ;
  

  // mettre a jours colonnes, envoyer au serveur

  popup_close() ;
  table_init() ;
  table_fill(false, true) ;
}

function remove_highlight()
{
  if ( the_current_line )
    {
      var name = the_current_line.className.replace('highlight_current', ' ') ;
      // The spaces broke the filter input : WHY XXX !!!
      name = name.replace(/^ */,'').replace(/ *$/,'') ;
      the_current_line.className = name ;
      the_current_line = undefined ;
    }
}

function hide_the_tip_real()
{
  tip.onmousemove = function() {} ;
  tip.style.display = "none" ;
  remove_highlight() ;
}

function hide_the_tip(real)
{
  if (  tip.style.display == "none" )
    return ;

  if ( real == tip.display_number ) // To not receive event from old tips
    {
      hide_the_tip_real() ;
      return ;
    }
}

function tip_bottom_right()
{
  tip_fixed = 1 - tip_fixed ;
}

function add_a_master(t)
{
  append_image(undefined, 'add_a_master/' + t.value.toLowerCase()) ;
  t.value = '' ; // Was WAIT A MOMENT
}

function update_popup_on_red_line()
{
  var e = document.getElementById('popup_on_red_line') ;

  if ( e )
    if ( popup_on_red_line )
      e.lastChild.className='' ;
    else
      e.lastChild.className='stroked';
}

function change_popup_on_red_line()
{
  popup_on_red_line = ! popup_on_red_line ;
  update_popup_on_red_line() ;
}

function students_mails(missing)
{
  var s = '' ;

  for(var data_lin in filtered_lines)
    {
      line = filtered_lines[data_lin] ;
      if ( line[0].value !== '' )
	{
	  if ( table_attr.mails[line[0].value]
	       && table_attr.mails[line[0].value].indexOf('@') != -1)
	    s += table_attr.mails[line[0].value] + ',' ;
	  else
	    if ( missing )
	      missing.push(line[0].value) ;
	}
      
    }
  return s ;
}
function authors_mails(missing)
{
  var cls = column_list_all() ;
  var cols = [] ;
  for (column in cls)
    cols.push(cls[column]) ;

  var a = {} ;
  for(var data_lin in filtered_lines)
    {
      line = filtered_lines[data_lin] ;
      for (data_col in cols)
	{
	  cell = line[cols[data_col]] ;
	  if ( cell.author !== '' && cell.author != '*' && cell.value !== '' )
	    {
	      a[cell.author] = cell.author ;
	    }
	}      
    }
  var s = '' ;
  for(var i in a)
    {
      if ( a[i] == i )
	if ( table_attr.mails[i] && table_attr.mails[i].indexOf('@') != -1 )
	  s += table_attr.mails[i] + ',' ;
	else
	  if ( missing )
	      missing.push(i) ;
    }
  return s ;
}

var mail_separator = '\n' ;

function mail_div_box(mails)
{
  return '<textarea readonly="1" class="mails" onclick="this.select()">'
    + mails.replace(/,/g, mail_separator) + '</textarea>' ;
}


function mail_window()
{
  var missing = [] ;
  var the_student_mails = students_mails(missing) ;
  var nr_student_mails = the_student_mails.split(',').length - 1 ;

  if ( the_student_mails.search('@') == -1 )
    {
      alert("Désolé, votre navigateur n'a pas encore reçu les adresses mails.\nRéessayez dans quelques secondes.") ;
      return ;
    }

  var link_students = nr_student_mails + ' Étudiants' ;
  if ( mailto_url_usable(the_student_mails) )
    link_students = hidden_txt('<a href="javascript: window.location=\'mailto:?bcc=' +
			       the_student_mails + '\'">' + link_students + ' (Lien rapide)</a>',
			       'Suivez le lien pour directement lancer ' +
			       'votre logiciel de messagerie.') ;

  var the_author_mails = authors_mails(missing) ;
  var nr_author_mails = the_author_mails.split(',').length - 1 ;
  var link_authors = nr_author_mails + ' Enseignants' ;
  if ( mailto_url_usable(the_author_mails) )
    link_authors = hidden_txt('<a href="javascript: window.location=\'mailto:?bcc=' +
			       the_author_mails + '\'">' + link_authors + ' (Lien rapide)</a>',
			       'Suivez le lien pour directement lancer ' +
			       'votre logiciel de messagerie.') ;

  var missing_text ;
  if ( missing.length )
    {
	missing_text = '<p class="unknown_mails">' + missing.length
	  + ' adresses mail inconnues' ;
       if ( missing.length > 20 )
	 missing_text += '.' ;
       else
	 missing_text += ' : ' + missing ;
       missing_text += '</p>' ;
    }
  else
    missing_text = '' ;

  create_popup('mails_div',
	       'Gestion des mails',
	       '<ul>' +
	       '<li> <b>Cliquez sur une adresse</b> pour toutes les sélectionner.' +
	       '<li> Puis faites <b>Ctrl-C</b> pour les copier' +
	       '<li> Puis faites <b>Ctrl-V</b> dans la liste des destinataires en <b>Copie Carbone Invisible (CCI ou BCC)</b> si vous ne voulez pas que les étudiants connaissent les autres destinataires.' +
	       '</ul>' +
	       'En cas de problème, utilisez le <a href="javascript:mail_separator=\';\';mail_window()">point-virgule</a> ou la <a href="javascript:mail_separator=\',\';mail_window()">virgule</a>  comme séparateur.' +
	       '<table class="colored"><tr>' +
	       '<th>' + link_students +
	       '<th>' + link_authors +
	       '</tr><tr><td>' +
	       mail_div_box(the_student_mails) +
	       '</td><td>' +
	       mail_div_box(the_author_mails) +
	       '</td></tr></table>' + missing_text
	       ,
	       'TOMUSS peut faire du <a href="javascript:personal_mailing()">publi-postage</a> en envoyant les mails pour vous.<br>Ceci permet d\'envoyer des informations personnalisées aux étudiants en fonction du contenu de la table.') ;

}

function update_mail(login, mail)
{
  table_attr.mails[login] = mail ;
}

function update_portail(login, portail)
{
  table_attr.portails[login] = portail ;
}

function change_size(dx, dy)
{
  nr_cols += dx ;
  nr_lines += dy ;
  table_init() ;
  table_fill(false, true) ;
}

function ljust(txt, len)
{
  // spaces are used as padding 
  // tabulation are used as separator 
  txt = txt.toString() ;
  if ( txt.length < len ) // Pad
    txt = (txt + '                                                         ').substr(0,len) ;
  else
    // To avoid the black strip of tabulation
    txt = txt + '        '.substr(0,7-(txt.length%8)) ;
  return txt + bs ;
}

function personal_mailing()
{
   create_popup('personal_mailing_div',
		'Envoyer un mail personnalisé aux étudiants filtrés',
		'<p style="background-color:#F00;color:#FFF">N\'ENVOYEZ PAS DE NOTES PAR MAIL AUX ÉTUDIANTS.</p>Les titres de colonne entre crochets sont remplacés par la valeur de la case correspondant à l\'étudiant pour cette colonne. Vous pouvez utiliser toutes les colonnes existantes.<p>&nbsp;<br>Sujet du message : <input id="personal_mailing" style="width:100%" value="' + ue + ' ' + table_attr.table_title + ' : Info pour [Prénom] [Nom]"><br>Votre message&nbsp;:',
	       'Pour envoyer, cliquez sur : <BUTTON OnClick="personal_mailing_do();">Envoyer les ' + filtered_lines.length + ' messages</BUTTON>.') ;
   popup_set_value('Bonjour [Prénom] [Nom].\n\nVotre groupe est [Grp] et votre séquence [Seq]\n\nAu revoir.') ;
}

function personal_mailing_parse_line(text, column_used, column_data_col)
{
  var t = text.split('[') ;
  var col_name, data_col ;
  for(var i in t)
    {
      if ( i == 0 )
	continue ;
      col_name = t[i].split(']')[0] ;
      if ( column_used[col_name] !== undefined )
	continue ;
      data_col = column_title_to_data_col(col_name) ;
      if ( data_col == undefined )
	{
	  alert("La colonne «" + col_name + "» n'existe pas.");
	  return ;
	}
      column_used[col_name] = personal_mailing_do.nr_items++ ;
      column_data_col[data_col] = true ;
    }
  for(var i in column_used)
    {
      text = text.replace('[' + i + ']', '[' + column_used[i] + ']') ;
    }

  return text ;
}

function personal_mailing_do()
{
  var mailing_mail = popup_value() ;
  var subject = document.getElementById('personal_mailing').value ;
  var column_used = {}, column_data_col = {} ;
  var t, col_name, nr, message, line, data_col ;
  var url_content, feedback_content ;
  var nr_frame ;

  nr = 0 ;
  message = '' ;
  personal_mailing_do.nr_items = 0 ;
  for(var line in mailing_mail)
    {
      t = personal_mailing_parse_line(mailing_mail[line],
				      column_used, column_data_col) ;
      if ( t === undefined )
	return ;
      message += t + '\n' ;
    }
  subject = personal_mailing_parse_line(subject, column_used, column_data_col);
  if ( subject === undefined )
    return ;
  subject = encode_uri(subject) ;
  url_content = '' ;
  feedback_content = '' ;
  nr_frame = 0 ;
  for(var i in filtered_lines)
    {
      if ( url_content === '' )
	{
	  nr_frame++ ;
	  url_content = '<iframe src="_URL_/=' + ticket + '/send_mail/'
	    + subject + '/' + encode_uri(message) ;
	}

      line = filtered_lines[i] ;
      url_content += '/' + encode_uri(line[0].value) ;
      for(data_col in column_data_col)
	url_content += '/' + encode_uri(line[data_col].value) ;

      if ( url_content.length > maximum_url_length
	   || i == filtered_lines.length-1 )
	{
	  feedback_content += url_content
	    + '" style="width:100%; height:2em;"></iframe>' ;
	  url_content = '' ;
	}
    }
  
  server_feedback.innerHTML = feedback_content ;
  
  popup_close() ;

  if ( nr_frame > 4 )
    alert("Ne fermez pas cette page tant que vous n'avez pas vu le/les message(s) « Les messages ont été envoyés » au dessous du tableau") ;
}

function change_table_size(select)
{
  var i = select.childNodes[select.selectedIndex].innerHTML ;
  var i = Math.floor(i.split(' ')[0]) ; // Remove text after number
  if ( select.id == 'nr_cols' )
    {
      nr_cols = i ;
      column_offset = 0 ;
      if ( the_current_cell.col >= nr_cols )
	the_current_cell.col = nr_cols - 1 ;
    }
  else
    {
      nr_lines = i ;
      line_offset = 0 ;
    }
  table_init() ;
  table_fill(false, true) ;
  update_vertical_scrollbar();
  the_current_cell.update() ;
}


function nice_scale_from(min, v, max, bigger)
{
  var t = [] ;
  var i, j ;

  for(i=min; i <= bigger ; i = Math.ceil(1.3*i))
    t.push(i) ;
  if ( myindex(t,v) == -1 )
    t.push(v) ;
  if ( myindex(t,max) == -1 )
    t.push(max) ;
  for(i=1; i <= 10 ; i *= Math.ceil(1.3))
    {
      j = v + i ;
      if ( myindex(t,j) == -1 )
	t.push(j) ;
      j = v - i ;
      if ( j > min && myindex(t,j) == -1 )
	t.push(j) ;
    }
  t.sort(function(x,y) { return x - y ; }) ;
  t[ myindex(t,max) ] = max + ' (tout)' ;
  return t ;
}

function update_a_menu(min, current, all, max, select)
{
  if ( ! select )
    return ;

  var i ;
  var sel ;
  var t = nice_scale_from(min, current, all, max) ;

  for(var ii in t)
    {
      var created = false ;
      var option = select.childNodes[ii] ;
      if ( option === undefined )
	{
	  option = document.createElement('option') ;
	  created = true ;
	}
      i = t[ii] ;
      if ( i.toString().replace(' (tout)','') == current )
	sel = ii ;
      option.innerHTML = i ;
      if ( created )
	select.appendChild(option) ;
    }
  select.selectedIndex = sel ;
}

function update_line_menu()
{
  var nr ;

  if ( filtered_lines )
    nr = filtered_lines.length ;
  else
    nr = lines.length ;

  update_a_menu(2, nr_lines, nr, Math.max(nr*1.5, nr_lines*1.1),
		select_nr_lines) ;
}

function update_column_menu()
{
  update_a_menu(2, nr_cols, add_empty_columns() - (tr_classname !== undefined),
		columns.length, select_nr_cols) ;
}

function compute_abj_per_day(t)
{
  var tag = document.getElementById('div_abjs') ;
  var s, abjs, end ;
  var ttam = [], ttpm = []  ;
  var d = new Date() ;
  d.setTime(t) ;
  var t12 = t + 16*3600*1000 ;
  
  for(var login in the_abjs)
    {
      abjs = the_abjs[login] ;
      for(i in abjs)
	{
	  begin = parse_date(abjs[i][0]) ;
	  end = parse_date(abjs[i][1]) ;
	  if ( end < t )
	    continue ; // Before the day
	  if ( begin > t12 )
	    continue ; // After the day
	  s = '<!-- ' +  names[login]
	    + ' --><tr><td>' + login + '<th align="left">'
	    + names[login] +
	    '<td>' + abjs[i][0] + '<td>' + abjs[i][1] +
	    '<td>' + html(abjs[i][2]) + '</tr>' ;
	  if ( begin <= t )
	    ttam.push(s) ;
	  if ( end > t )
	    ttpm.push(s) ;
	}
    }
  ttam.sort() ;
  ttpm.sort() ;
  s = '<h2>ABJ du ' + days_long[d.getDay()] + ' ' + d.getDate() + ' ' +
    months[d.getMonth()] + ' ' + d.getFullYear() + ' :</h2>' ;
  s += 'Date de début et fin (incluses), M=Matin, A=Après-midi.' ;
  s += '<p>ABJ pour le matin :<table class="colored">' ;
  for(var i=0; i<ttam.length; i++)
    s += ttam[i] ;
  s += '</table>' ;
  s += '<p>ABJ pour l\'après-midi :<table class="colored">' ;
  for(var i=0; i<ttpm.length; i++)
    s += ttpm[i] ;
  s += '</table>' ;
  tag.innerHTML = s ;
}

function abj_per_day()
{
  var w = window_open() ;
  w.document.open('text/html') ;

  var p = html_begin_head(true) ;


  var title = 'ABJ pour ' + ue + ' ' + semester + ' ' + year ;

  p += '<script src="_URL_/abj.js"></script>' +
    '<title>' + title + '</title>' +
    '<body><h1>' + title + '</h1>\n' +
    '<p>Cliquez pour choisir votre jour :' +
    '<script>var the_abjs = {};\n' ;

  var s = '', t, end, names='' ;
  var days = [] ;
  for(var i in the_student_abjs)
    {
      s += "the_abjs['" + i + "'] = [" ;
      names += ',\"' + i + '\":\"' + lines[login_to_line(i)][2].value
	+ ' ' + lines[login_to_line(i)][1].value+ '\"';
      i = the_student_abjs[i] ;
      var t = '' ;
      for(var j in i[0])
	{
	  j = i[0][j] ;
	  t += ',["' + j[0] + '","' + j[1] + '","' + j[2] + '"]' ;
	  end = parse_date(j[1].replace(am,pm)).getTime() ;
	  for(var d=parse_date(j[0].replace(pm,am));
	      d.getTime() < end;
	      d.setTime(d.getTime() + 86400*1000)
	      )
	    {
	      if ( d.getHours() == 23 )
		d.setHours(24) ;
	      else if ( d.getHours() == 1 )
		d.setHours(0) ;
	      days[d.getFullYear()+'/'+d.getMonth()+'/'+d.getDate()] = d.getTime() ;
	    }
	      
	}
      s += (t+' ').substr(1) + '] ;\n' ;
    }
  p += s + '\n' +
    'var names = {' + (names+' ').substr(1) + '};</script>' +
    '<table class="colored">' ;

  var mm, first ;

  if ( semester == 'Automne' )
    var start = 7, stop = 13, yy = year ;
  else
    var start = 1, stop = 7, yy = year + 1 ;

  for(var m=start; m<stop; m++)
    {
      first = true ;
      mm = m % 12 ;
      if ( mm == 0 )
	  yy++ ;
      for(var d=1; d<32; d++)
	if ( days[yy + '/' + mm + '/' + d] )
	  {
	    if ( first )
	      {
		first = false ;
		p += '<tr><th>' + months[mm] ;
		for(var i=1;i<d;i++)
		  p += '<td>&nbsp;' ;
	      }
	    p += '<td><a onclick="javascript:compute_abj_per_day('
	      + days[yy + '/' + mm + '/' + d] + ');">' + d + '</a>' ;
	  }
      if ( ! first )
	{
	  p += '</tr>\n' ;
	}
    }
  p +=  '</table>\n' +
    '<div id="div_abjs"></div>' +
    '</html></body>' ;
  w.document.write(p) ;
  w.document.close() ;
}

var last_reconnect = 0 ;
var reconnect_giveup ;

function reconnect()
{
  if ( ue == 'VIRTUALUE' || ue == '' )
    return ;
  if ( check_down_connections_interval == 0 )
    return ;
  if ( millisec() - last_reconnect < 1000*check_down_connections_interval )
    return ;
  if ( millisec() - last_server_answer > 1000*(ticket_time_to_live-3600))
    {
      if ( ! reconnect_giveup )
	{
	  reconnect_giveup = true ;
	  alert('Votre page est trop ancienne, actualisez-la') ;
	}
      // XXX The ticket is too old, The reconnection will fail.
      return ;
    }
  var server_answer = document.getElementById('server_answer') ;
  if ( ! server_answer )
    return ;
  server_answer.src = url + "/=" + ticket + '/' + year
    + '/' + semester + '/' + ue + '/' + page_id ;
  last_reconnect = millisec() ;
}

function runlog(the_columns, the_lines)
{
  columns = the_columns ;
  lines = the_lines ;

  lib_init() ;

  if ( test_bool(preferences.display_tips) == no )
    display_tips = false ;
  if ( test_bool(preferences.tipfixed) == yes )
    tip_fixed = true ;
  scrollbar_right = test_bool(preferences.scrollbar_right) == yes ;
    
  if ( test_bool(preferences.invert_name) == yes
       && columns.length > 2
       && columns[2].title == 'Nom'
       )
    {
      columns[2].position = columns[1].position - 0.1 ;
    }
  if ( preferences.nr_lines > 0 && preferences.nr_lines < 1000 )
    nr_lines = preferences.nr_lines ;
  if ( Number(preferences.zebra_step) > 0 )
    zebra_step = Number(preferences.zebra_step) ;
  else
    zebra_step = 3 ;
  if ( preferences.nr_cols > 0 && preferences.nr_cols < 100 )
    nr_cols = preferences.nr_cols ;

  if ( table_attr.default_nr_columns )
    nr_cols = table_attr.default_nr_columns ;
  if ( test_bool(preferences.v_scrollbar) == no )
    vertical_scrollbar = undefined ;

  for(var data_lin in lines)
    {
      lines[data_lin]['number'] = Number(data_lin) ;
    }

  for(var data_col in columns)
    {
      columns[data_col].filter = '' ;
      columns[data_col].data_col = Number(data_col) ;
      if ( columns[data_col].freezed == 'C' )
	{
	  tr_classname = data_col ;
	}
    }
  if ( tr_classname === undefined )
    {
      default_title = 'Titre' ;
    }
  // Default : Name sort

  add_empty_columns() ;
  if ( table_attr.default_sort_column[0] != undefined )
    {
      // default_sort column is a list
      sort_columns = [] ;
      for(var i in table_attr.default_sort_column)
	{
	  sort_columns.push(columns[table_attr.default_sort_column[i]]) ;
	  sort_columns[i].dir = 1 ;
	}
    }
  else if ( columns.length > table_attr.default_sort_column )
    {
      if ( columns.length > 1 )
	{
	  sort_columns = [columns[table_attr.default_sort_column],columns[1]] ;
	  columns[1].dir = 1 ;
	}
      else
	sort_columns = [columns[table_attr.default_sort_column]] ;
      columns[table_attr.default_sort_column].dir = 1 ;
    }
  else
    {
      table_attr.default_sort_column = 0 ;
      sort_columns = [columns[0]] ;
    }

  if ( ! do_not_read_option )
    {
      try
	{
	  get_all_options() ; // Defined in by tablebookmark ATTRIBUTE
	}
      catch(err)
	{
	}
    }
  update_line_menu() ;
  update_column_menu() ;
  update_popup_on_red_line() ;

  update_filtered_lines(); // Before init_columns to compute RED/GREEN
  for(var data_col in columns)
    {
      init_column(columns[data_col]) ;
      columns[data_col].need_update = true ;
    }
  update_columns() ;

  if ( server_log )
    setInterval(auto_save_errors, 100) ;


  if ( preferences.interface == 'L' )
    {
      dispatch('init') ;
      return ;
    }

  /*
   * The normal interface (not linear)
   */

  table_init() ;
  table_fill(false, true, true) ;

  if ( ue == 'javascript_regtest_ue' )
    {
      javascript_regtest_ue() ;
    }

  // Try to load image not yet loaded.
  setInterval(highlight_effect, 500) ;
  setInterval(table_fill_try, 100) ;

  if (window.addEventListener)
    /** DOMMouseScroll is for mozilla. */
    window.addEventListener('DOMMouseScroll', wheel, false);
  /** IE/Opera. */
  window.onmousewheel = document.onmousewheel = wheel;

  if ( ue != 'VIRTUALUE' && ue != '' && page_id > 0 )
    document.write('<img width="1" height="1" src="' + url + "/=" + ticket
		   + '/' + year + '/' + semester + '/' + ue + '/' +
		   page_id + '/end_of_load">') ;

  if ( get_option('print-table', 'a') !== 'a' )
    {
      print_page() ;
      window.close() ;
      return ;
    }
  if ( get_option('signatures-page', 'a') !== 'a' )
    {
      signatures_page() ;
      window.close() ;
      return ;
    }

  // Firefox bug : the page refresh reload the old iframe, not the new one
  setTimeout(reconnect, 10) ;

  the_current_cell.update_table_headers() ;
  change_title(table_attr.table_title, table_attr.code) ;
}


// Regression tests (the link is on the home page for super user

function get_tr_classname()
{
  for(var data_col in columns)
    if ( columns[data_col].freezed == 'C' )
      return data_col ;
}

function display_suivi(cols) /* [value, class, comment] */
{
  var c = column_list_all() ;
  var comment, cell, visual_cell, infos ;
  var tr_classname = get_tr_classname() ;

  if ( tr_classname && line[tr_classname].value == 'non' )
    document.write('<div class="noninscrit">Étudiant non inscrit à l\'UE. Aucune note ne peut être saisie et cette UE ne pourra être validée.<br><br>') ;

  for(var data_col in c)
    c[data_col].data_col = data_col ;

  for(var data_col in c)
    {
      data_col = c[data_col] ;
      column = columns[data_col] ;
      visual_cell = cols[column.title] ;
      if ( visual_cell === undefined )
	continue ;
      comment = '<span class="column_title">' + column.title ;
      if (column.comment)
	comment += '<em> : ' + html(column.comment) + '</em>' ;
      comment += '</span>' ;
      cell = line[column.data_col] ;
      // For evaluated columns
      visual_cell[0] = visual_cell[0].replace('\001',cell.value_fixed())
	.replace('\002','/' + column.max);

      if ( cell.comment )
	{
	  comment += 'Commentaire : <b>' + html(cell.comment) + '</b><br>' ;
	  visual_cell[1] += ' commented' ;
	}
      if (cell.date)
	comment += 'Date modification : <b>' + date(cell.date) + '</b><br>';
      if (cell.author)
	comment += 'Par : <b>' + cell.author + '</b><br>' ;
      if (column.real_type.should_be_a_float)
	comment += 'Poids dans la moyenne pondérée : <b>' + column.weight + '</B><br>' ;
      if (comment)
	visual_cell[2] = comment + visual_cell[2] ;
      if ( visual_cell[0] === '' )
	visual_cell[1] += ' empty' ;
    }

  if ( document.getElementById("allow_inline_block").offsetWidth > 50 )
    for(var title in c)
      {
	title = columns[c[title]].title ;
	visual_cell = cols[title] ;
	if ( visual_cell === undefined )
	  continue ;

	if ( visual_cell[0] !== '' || is_a_teacher )
	  {
	    hidden(title+':<b>'+ visual_cell[0] + '</b>', 
		   visual_cell[2], visual_cell[1]);
	    document.write(', ') ;
	  }
      }
  else
    {
      function fusion(title, first)
      {
	var name, s, visual_cell, v ;
	var column = columns[data_col_from_col_title(title)] ;
	if ( column === undefined )
	  return '???' + title + '???' ;
	s = '' ;
	for(var depend in column.average_columns)
	  {
	    name = columns[column.average_columns[depend]].title
	    visual_cell = cols[name] ;
	    if ( visual_cell === undefined )
	      continue ;
	    visual_cell[3] = true; // Used
	    
	    if ( column.type == 'Nmbr' ) // No weight on Nmbr compute
	      s += fusion(name, depend==0).replace(/Poids[^B]*B><br>/, '') ;
	    else
	      s += fusion(name, depend==0) ;
	  }
	visual_cell = cols[title] ;
	//return '['+title+','+s+']' ;
	if ( first )
	  first = ' first_child' ;
	else
	  first = '' ;
	if ( s === '' )
	  v = '<div class="notes fine ' + visual_cell[1] + first + '">'
	    + hidden_txt('<i>' + title + '<br>' + visual_cell[0] + '</i>', visual_cell[2])
	    + '</div>' ;
	else
	  v = '<div class="notes' + first + '">'
	    + hidden_txt('<i>' + title + ': ' + visual_cell[0] + '</i><br>',
			 visual_cell[2], visual_cell[1])
	    + s + '</div>' ;
	return v ;
      }
      for(var title in cols)
	{
	  visual_cell = cols[title] ;
	  visual_cell[4] = fusion(title) ;
	}
      for(var data_col in c)
	{
	  data_col = c[data_col] ;
	  visual_cell = cols[columns[data_col].title] ;
	  if (visual_cell === undefined )
	    continue ;
	  if ( ! visual_cell[3] )
	    {
	      if ( visual_cell[0] !== '' || is_a_teacher )
		{
		  cell = visual_cell[4].replace(/Poids[^B]*B><br>/, '') ;
		  document.write(cell) ;
		}
	    }
	}
    }

  if ( tr_classname && line[tr_classname].value == 'non' )
    document.write('</div>');
}

function javascript_regtest_ue()
{
  function set(i, v)
  {
    i.style.display = '' ;
    if ( i.focus )
      {
	if ( i.onfocus )
	  {
	    window.event = new Object() ;
	    window.event.target = i ;
	    i.onfocus(window.event) ;
	  }
	else
	  i.focus() ;
      }
    switch( i.tagName )
      {
      case 'SELECT':
	//	i.value = v ; // 8/12/2009

	for(var j in i.childNodes)
	  {
	    if ( i.childNodes[j].value == v )
	      {
		i.selectedIndex = j ;
		i.childNodes[j].selected = true ;
		window.event = new Object() ;
		window.event.target = i ;
		i.onchange(window.event) ;
		break ;
	      }
	  }
	if ( i.blur )
	  i.blur() ;
	break ;
      case 'INPUT':
	i.value = v ;
	if ( i.onblur )
	  {
	    window.event = new Object() ;
	    window.event.target = i ;
	    i.onblur(window.event) ;
	  }
	else
	  i.blur() ;
	break ;
      case 'TD':
	i.childNodes[0].value = v ;
	window.event = new Object() ;
	window.event.target = i ;
	i.childNodes[0].onchange(window.event) ;
	if ( i.blur )
	  i.blur() ;
	break ;
      default:
	alert('BUG') ;
      }
    highlight_list = [] ;
  } ;
  function expected(messages)
  {
    if ( alert_messages != messages )
      {
	alert_real('Alerts expected:' + messages +
		   '\n\nGot: ' + alert_messages);
	correct_this_problem_please ;
      }
  alert_messages = '' ;
  } ;
  function fill_col(content, check, messages)
  {
    // message.innerHTML += '[' + the_current_cell.column.title + '(' + the_current_cell.column.type + ')]';
    for(var i in content)
      {
	// message.innerHTML += '{' + content[i] + '}' ;
	set(the_current_cell.input, content[i]) ;
	the_current_cell.change() ;
	var v = the_current_cell.td.innerHTML ;
	v = v.split('<')[0] ;
	if ( v == '&nbsp;' || v == ' ' ) // WARNING : unsecable space (Opera)
	  v = '' ;
	if ( check && v != check[i] )
	  {
	    alert_real('Result: "' + v
		       + '" Expected result: "' + check[i] + '"') ;
	    asdasdasd;
	  }
	  
	the_current_cell.cursor_down() ; 
      }
    for(var i in content)
      the_current_cell.cursor_up() ; 
    the_current_cell.cursor_right() ; 
    expected(messages) ;
  } ;

  var start_test = millisec() ;

  var col_types=['Note','Moy' ,'Nmbr','Bool','Date'] ;
  var col_types2=['Note','Moyenne' ,'Nombre de','Booléen','Date'] ;

  var inputs=['0'   ,'1'   ,'2,2' ,'p'  ,'i','j','o'  ,'n','4/3/2008'  ,'3/4/8'     ,'12/12/99', '0.95', '0.9966'] ;
  var notes =['0.00','1.00','2.20',''   ,abi,abj,''   ,ppn,''          ,''          ,'', '0.95', '0.99'] ;
  var moys  =['0.00','1.00','2.20','NaN',abi,abj,'NaN',ppn,'NaN'       ,'NaN'       ,'NaN', '0.95', '0.99'] ;
  var expore=['0,000','1,000','2,200', '','ABI','ABJ','','PPN',''         ,''          ,'', '0,950', '0,993'] ;
  var nmbr  =['0'   ,'0'   ,'5'   ,'0'  ,'1','4','0'  ,'0','0'         ,'0'         ,'0', '0', '0'] ;
  var boole =[no    ,yes   ,''    ,''   ,'' ,'' ,yes  ,no ,''          ,''          ,'', '', ''] ;
  var today = new Date() ;
  var date  =[''    ,
	      '01/'+two_digits(today.getMonth()+1)+'/' + today.getFullYear(),
	      ''    ,''   ,'' ,'' ,''   ,'' ,'04/03/2008','03/04/2008',
	      '12/12/1999', '', ''] ;

  lines = [] ;
  columns = [] ;
  lines_id = {} ;
  add_empty_columns() ;
  table_attr.default_sort_column = 0 ;
  sort_columns = [columns[0]] ;
  update_filtered_lines();
  the_current_cell.jump(nr_headers,0) ;
  nr_cols = 12 ;


  alert_real = alert ;
  var alert_messages = '' ;

  if ( navigator.appName != 'Microsoft Internet Explorer' )
    alert = function(x) { alert_messages += escape(x) + '<hr>' ; } ;

  table_init() ;
  update_columns() ;
  table_fill(false, true,true) ; table_fill_try() ;

  table_autosave_toggle() ;

  var t_column_title       = document.getElementById('t_column_title'      );
  var t_column_test_filter = document.getElementById('t_column_test_filter');
  var t_column_columns     = document.getElementById('t_column_columns'    );
  var t_column_type        = document.getElementById('t_column_type'       );

  set(t_column_title, 'Saisie') ;
  set(t_column_type, 'Texte libre') ;
  the_current_cell.cursor_right() ;
  expected('');

  for(var col_type2 in col_types)
    {
      var col_type = col_types[col_type2] ;
      set(t_column_title, col_type) ;
      /*
      if ( columns[col_type2].title != col_type )
	{
	  alert_real('Browser Bug: Title') ;
	  return ;
	}
      */
      set(t_column_type, col_types2[col_type2]) ;
      /*
      if ( columns[col_type2].type != col_types2[col_type2] )
	{
	  alert_real('Browser Bug: Type') ;
	  return ;
	}
      */
      if ( col_type == 'Moy' )
	{
	  set(t_column_columns, 'Note AttendueNote') ;
	  /*
	  if ( columns[col_type2].average_from != ['Note','AttendueNote'] )
	    {
	      alert_real('Browser Bug: average columns') ;
	      return ;
	    }
	  */
	}
      if ( col_type == 'Nmbr' )
	{
	  set(t_column_columns, 'Saisie Note AttendueNote Moy AttendueMoy') ;
	  set(t_column_test_filter, '>1 ou =i ou ~u') ;
	}

      the_current_cell.cursor_right() ;
      set(t_column_title, 'Attendue' + col_type) ;
      set(t_column_type, 'Texte libre') ;
      the_current_cell.cursor_right() ;
    }
  message.innerHTML += 'a';
  expected('');
  for(var col_type in col_types)
    {
      the_current_cell.cursor_left() ;
      the_current_cell.cursor_left() ;
    }
  the_current_cell.cursor_left() ;

  fill_col(inputs, undefined, '');
  fill_col(inputs, notes, 'p%20n%27est%20pas%20une%20note%20valide%20car%20non%20dans%20l%27intervalle%20%5B0%3B20%5D%0ANi%20I%28ABINJ%29%2C%20J%28ABJUS%29%2C%20N%28PPNOT%3A%20ne%20peut%20pas%20noter%29<hr>o%20n%27est%20pas%20une%20note%20valide%20car%20non%20dans%20l%27intervalle%20%5B0%3B20%5D%0ANi%20I%28ABINJ%29%2C%20J%28ABJUS%29%2C%20N%28PPNOT%3A%20ne%20peut%20pas%20noter%29<hr>4/3/2008%20n%27est%20pas%20une%20note%20valide%20car%20non%20dans%20l%27intervalle%20%5B0%3B20%5D%0ANi%20I%28ABINJ%29%2C%20J%28ABJUS%29%2C%20N%28PPNOT%3A%20ne%20peut%20pas%20noter%29<hr>3/4/8%20n%27est%20pas%20une%20note%20valide%20car%20non%20dans%20l%27intervalle%20%5B0%3B20%5D%0ANi%20I%28ABINJ%29%2C%20J%28ABJUS%29%2C%20N%28PPNOT%3A%20ne%20peut%20pas%20noter%29<hr>12/12/99%20n%27est%20pas%20une%20note%20valide%20car%20non%20dans%20l%27intervalle%20%5B0%3B20%5D%0ANi%20I%28ABINJ%29%2C%20J%28ABJUS%29%2C%20N%28PPNOT%3A%20ne%20peut%20pas%20noter%29<hr>');
  fill_col(notes, undefined, '');
  var non_modifiable = 'R%E9sultat%20de%20calcul%20non%20modifiable<hr>R%E9sultat%20de%20calcul%20non%20modifiable<hr>R%E9sultat%20de%20calcul%20non%20modifiable<hr>R%E9sultat%20de%20calcul%20non%20modifiable<hr>R%E9sultat%20de%20calcul%20non%20modifiable<hr>R%E9sultat%20de%20calcul%20non%20modifiable<hr>R%E9sultat%20de%20calcul%20non%20modifiable<hr>R%E9sultat%20de%20calcul%20non%20modifiable<hr>R%E9sultat%20de%20calcul%20non%20modifiable<hr>R%E9sultat%20de%20calcul%20non%20modifiable<hr>R%E9sultat%20de%20calcul%20non%20modifiable<hr>R%E9sultat%20de%20calcul%20non%20modifiable<hr>' ;
  fill_col(nmbr, moys, non_modifiable);
  fill_col(moys, undefined, '');
  fill_col(inputs, nmbr, non_modifiable);
  fill_col(nmbr, undefined, '');
  fill_col(inputs, boole, '');
  fill_col(boole, undefined, '');
  fill_col(inputs, date, 'Cette%20date%20n%27existe%20pas%20%3A%200<hr>Cette%20date%20n%27existe%20pas%20%3A%202%2C2<hr>Cette%20date%20n%27existe%20pas%20%3A%20p<hr>Cette%20date%20n%27existe%20pas%20%3A%20i<hr>Cette%20date%20n%27existe%20pas%20%3A%20j<hr>Cette%20date%20n%27existe%20pas%20%3A%20o<hr>Cette%20date%20n%27existe%20pas%20%3A%20n<hr>Cette%20date%20n%27existe%20pas%20%3A%200.95<hr>Cette%20date%20n%27existe%20pas%20%3A%200.9966<hr>');
  fill_col(date, undefined, '');

  the_current_cell.cursor_left() ;
  do_move_column_left() ;
  table_fill(false, true) ; table_fill_try() ;
  bigger_column() ;
  bigger_column() ;
  bigger_column() ;
  do_move_column_left() ;
  table_fill(false, true) ; table_fill_try() ;
  smaller_column() ;
  smaller_column() ;
  smaller_column() ;
  message.innerHTML += 'n';

  cell_goto(table.childNodes[nr_headers].childNodes[3]) ;
  export_column() ; // Moyenne
  export_column_id_value();
  v = popup_value() ;
  for(var i in inputs)
    if ( v[i] != inputs[i] + '\t' + expore[i] )
      alert_real('Export BUG:' + v[i] + ' != ' + inputs[i] + '\t' + expore[i]);
  popup_close() ;
  message.innerHTML += 'o';
  expected('');

  cell_goto(table.childNodes[nr_headers].childNodes[11]) ;
  set(t_column_type, 'Texte libre') ;
  import_column() ;
  popup_set_value('p PP\ni II\nj JJ') ;
  import_column_do() ;
  message.innerHTML += 'p';
  expected('');
  freeze_column() ;
  table_fill(false, true) ; table_fill_try() ;

  cell_goto(table.childNodes[nr_headers+3].childNodes[0], true) ;
  if ( the_current_cell.td.innerHTML != 'PP' )
    alert_real('Import problem: ' + the_current_cell.td.innerHTML) ;

  message.innerHTML += 'q';
  column_delete() ;
  if ( the_current_cell.column.title != default_title + '12' )
    alert_real('Non empty column destroyed') ;

  expected('On%20peut%20seulement%20d%E9truire%20des%20colonnes%20vides.%0A%0AVous%20devez%20donc%20d%27abord%20vider%20la%20colonne%20en%20cliquant%20sur%20%22Remp.%22<hr>');

  if ( the_current_cell.column.the_local_id !== undefined )
    alert_real('Bug local_id') ;

  message.innerHTML += 'r';
  set(the_current_cell.input, '') ;
  the_current_cell.cursor_down() ;
  set(the_current_cell.input, '') ;
  the_current_cell.cursor_down() ;
  set(the_current_cell.input, '') ;
  the_current_cell.cursor_down() ;

  expected('') ;

  column_delete() ;
  if ( the_current_cell.column.title == default_title + '12' )
    alert_real('Empty column not destroyed: ' + the_current_cell.column.title);

  expected('') ;

  // Stat, impression, mails, filter, double click

  var w ;

  message.innerHTML += 's';
  
  w = print_page()                    ; w.close() ; message.innerHTML += '1';
  w = signatures_page()               ; w.close() ; message.innerHTML += '2';
  // w = goto_resume()                ; w.close() ; message.innerHTML += '3';
  w = students_pictures()             ; w.close() ; message.innerHTML += '4';
  w = students_pictures_per_grp_seq() ; w.close() ; message.innerHTML += '5';
  w = statistics()                    ; w.close() ; message.innerHTML += '6';
  w = statistics_per_group()          ; w.close() ; message.innerHTML += '7';
  w = statistics_authors()            ; w.close() ; message.innerHTML += '8';
  w = my_mailto(students_mails()+'@',true);w.close(); message.innerHTML += '9';
  w = my_mailto(authors_mails()+'@',true) ;w.close(); message.innerHTML += 'A';

  if ( alert_messages )
    {
      alert_real('Unexpected alert message :' + alert_messages.replace(/<hr>/,'\n')) ;
      alert_messages = '' ;
    }

  var end_test = millisec() ;
  alert_real('Test duration:' + (end_test - start_test)/1000 + 'seconds') ;
}

/*REDEFINE
*/
function do_change_abjs(m)
{
  the_student_abjs = m ;
}

var the_student_abjs = {} ;
function change_abjs(m)
{
  do_change_abjs(m) ;
}

// XXX COPY/PASTE in the end of new_page.py
window.Xcell_change    = Xcell_change ;
window.Xcomment_change = Xcomment_change ;
window.Xcolumn_delete  = Xcolumn_delete ;
window.Xcolumn_attr    = Xcolumn_attr ;
window.Xtable_attr     = Xtable_attr ;
window.change_abjs     = change_abjs ;
window.saved           = saved ;
window.connected       = connected ;
window.update_mail     = update_mail ;
window.update_portail  = update_portail ;
window.login_list      = login_list ;
window.click_to_revalidate_ticket = click_to_revalidate_ticket ;
window.server_answered = server_answered ;
