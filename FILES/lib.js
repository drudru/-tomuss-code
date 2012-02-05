// -*- coding: utf-8; mode: Java; c-basic-offset: 2; tab-width: 8; -*-
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
var bs = '<td>' ;
var maximum_url_length = 3000 ;

var is_a_teacher = false ;

// Work value
var popup_blocker = false ;
var element_focused ;
var server_feedback ;
var line_offset ;		// The page being displayed
var column_offset ;
var filters ;			// The filters to apply to the lines
var nr_new_lines ;		// Number of created lines
var nr_new_columns ;		// Number of created columns
var nr_not_empty_lines ;        // Number of non empty lines
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
var the_current_cell ;
var today ;
var debug_window ;
var delayed_list ;
var mouse_over_old_td ; // To not recompute the tip on each mousemove.
var filtered_lines ;
var table_fill_do_not_focus ;
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
var nr_filtered_lines ;
var the_comment ;
var linefilter ;
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
var t_menutop ;

// Redefined if needed
var root ;
var my_identity ;

function lib_init()
{
  divtable             = document.getElementById('divtable'             );
  author               = document.getElementById('author'               );
  modification_date    = document.getElementById('date'                 );
  server_log           = document.getElementById('log'                  );
  the_body             = document.getElementById('body'                 );
  if ( the_body )
    the_body.style.overflowX = 'hidden' ;
  p_title_links        = document.getElementById('title_links'          );
  nr_filtered_lines    = document.getElementById('nr_filtered_lines'    );
  the_comment          = document.getElementById('comment'              );
  linefilter           = document.getElementById('linefilter'           );
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
  t_menutop            = document.getElementById('menutop'              );
  server_feedback      = document.getElementById('server_feedback'      );

  if ( root === undefined )
    root = [] ;
  if ( my_identity === undefined )
    my_identity = 'identity undefined' ;

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

  if ( divtable ) // In a table
    {
      compute_nr_cols() ;
      compute_nr_lines() ;
    }
  current_window_height = window_height() ;
  current_window_width = window_width() ;

  today = new Date() ;
  today = today.getFullYear() + two_digits(today.getMonth() + 1) +
    two_digits(today.getDate()) + '000000' ;

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
  table_attr.nr_columns = Math.floor(16 * (window_width() / 1280)) ;
  if ( table_attr.nr_columns <= 0 )
    // Needed for 'statistics_per_group' virtual table
    table_attr.nr_columns = 1 ;
}

var header_height ;

function compute_nr_lines()
{
  if ( ! header_height )
    {
      setTimeout("header_height = findPosY(the_current_cell.input); compute_nr_lines();table_init();table_fill(true,true,true)", 1000) ;
      table_attr.nr_lines = 1 ;
      return ;
    }
  if ( the_current_cell.input )
    {
      // Number of displayed lines on the screen
      table_attr.nr_lines = (window_height() - header_height
			     - 1.5*the_current_cell.input.offsetHeight)
        / (1+table.childNodes[nr_headers].firstChild.offsetHeight) ;
      table_attr.nr_lines = Math.floor(table_attr.nr_lines) ;
    }

  // table_attr.nr_lines = Math.floor( (window_height() - 350) / 22) ;
  if ( table_attr.nr_lines < 3 )
    table_attr.nr_lines = 3 ;
}

/*
 * Standard Variable name used in all the code :
 * line_id  : index of the line in 'lines'
 * lin      : index of the line in 'table'
 * data_col : index of the column in 'lines[line_id]'
 * col      : index of the column in 'table[lin]'
 * column   : is columns[data_col]
 * line     : is lines[line_id]
 * tr       : is 'table[lin]'
 * td       : is 'table[lin][col]' attributes : line_id, data_col, lin, col
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

// Index in 'filtered_lines'
function lin_from_line_id(line_id)
{
  var lin ;

  lin = myindex(filtered_lines, lines[line_id]) - line_offset ;
  if ( lin < 0  || lin >= table_attr.nr_lines )
    return ;
  return lin ;
}

function td_from_line_id_data_col(line_id, data_col)
{
  var col, lin ;

  col = columns[data_col].col ;
  if ( col === undefined )
    return ;

  lin = lin_from_line_id(line_id) ;
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

function line_id_from_lin(lin)
{
  var line = line_offset + lin - nr_headers ;
  if ( line >= filtered_lines.length )
    return ;
  if ( line < 0 )
    return ;
  return filtered_lines[line].line_id ;
}

function line_id_from_td(td)
{
  return line_id_from_lin(lin_from_td(td)) ;
}

// The parameter can be an event or an HTML element
function the_td(event)
{
  var td ;
  if ( event && event.tagName )
    td = event ;
  else
    td = the_event(event).target ;
  if ( td.tagName == 'INPUT' || td.tagName == 'SELECT' || td.tagName == 'IMG'
       || td.tagName == 'A' )
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

function previous_year_semester(year, semester)
{
  var i = myindex(semesters, semester) ;
  if ( i == -1 )
    return [year - 1, semester] ;
  i = ( i + semesters.length - 1 ) % semesters.length ;
  if (i != semesters.length - 1)
    return [year, semesters[i]] ;
  else
    return [year - 1, semesters[i]] ;
}

function next_year_semester(year, semester)
{
  year = Number(year) ;
  var i = myindex(semesters, semester) ;
  if ( i == -1 )
    return [year + 1, semester] ;
  i = ( i + 1 ) % semesters.length ;
  if (i != 0)
    return [year, semesters[i]] ;
  else
    return [year + 1, semesters[i]] ;
}

function next_year_semester_number(year, semester)
{
  year = Number(year) ;
  semester += 1 ;
  if ( semester == semesters.length )
    {
      semester = 0 ;
      year += 1 ;
    }
  return [year, semester] ;
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
  if ( periodic_work_in_queue(table_fill_do) )
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

function get_tip_element()
{
  var tip = document.getElementById('tip') ;

  if ( ! tip )
    {
      tip = document.createElement('div') ;
      tip.display_number = 1 ;
      tip.id = 'tip' ;
      document.getElementsByTagName('BODY')[0].appendChild(tip) ;
    }
  return tip ;
}

function set_tip_position(td, bottom)
{
  var tip = get_tip_element() ;
  tip.target = undefined ;
  if ( table_forms_element && line_id_from_td(td) )
    {
      set_element_relative_position(td, tip) ;
      tip.style.left = '0px' ;
      return ;
    }
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

function compute_rank(line_id, column)
{
  var data_col = column.data_col ;
  var the_value = a_float(lines[line_id][data_col].value) ;

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

function line_resume(line_id)
{
  var s, column ;
  s = '<table class="colored" style="max-width:' + Math.floor(window_width()*0.75) + 'px">' ;
  s += '<tr><th>Colonne</th><th>Valeur</th><th>Rang</th><th>Commentaire</th></tr>';
  for(var data_col in columns)
    {
      cell = lines[line_id][data_col] ;
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
	    compute_rank(line_id, column) + '</td>' ;
	  if (cell.comment)
	    s += '<td>' + cell.comment_html() + '</td>' ;
	  else
	    s += '<td>&nbsp;</td>' ;
	  s += '</tr>\n' ;
	}
    }
  s += '</table>' ;
  var x = table_attr.portails[lines[line_id][0].value] ;

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

  show_the_tip(td) ;
}

var the_current_line ;

function show_the_tip(td, tip_content)
{
  var bottom = false ;
  var data_col, line_id, column, type, s ;

  try {
    data_col = data_col_from_td(td) ;
    line_id = line_id_from_td(td) ;
    column = columns[data_col] ;
    type = column.real_type ;
  }
  catch(e) { // Not in a 'table' page
  }

  var tip = get_tip_element() ;

  if ( tip_content === undefined )
    {
      if ( line_id === undefined )
	{
	  bottom = true ;
	  while ( td.tagName != 'TH' )
	    {
	      td = td.parentNode ;
	      if ( ! td )
		return ;
	    }
	  s = type['tip_' + td.parentNode.className.split(' ')[0]] ;
	  remove_highlight() ;
	}
      else
	{
	  var line = lines[line_id] ;
	  if ( line === undefined )
	    return ;
	  var cell = line[data_col] ;
	  if ( cell.is_mine() && table_attr.modifiable
	       && column.real_type.cell_is_modifiable)
	    s = '<span class="title">' + type.tip_cell + '</span><br>' ;
	  else
	    s = '' ;
	  if ( i_am_root )
	    s += 'line_id=' + line_id + ', col_id=' + column.the_id ;
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

  if ( ! display_tips )
    return ;

  tip.innerHTML = s ;
  tip.style.display = "block" ;
  tip.display_number++ ;
  var a = tip.display_number ;
  // Hide the tip if the mouse go inside
  tip.onmousemove = function() { hide_the_tip(a); } ;

  set_tip_position(td, bottom) ;
  return tip ;
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
  if ( table_forms_element )
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
  // The first child is HOVER
  while( divtable.childNodes[1] )
    divtable.removeChild(divtable.childNodes[1]) ;
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
  for(var i=0 ; i<table_attr.nr_columns; i++)
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
  th.innerHTML = '<div onmousedown="header_title_click(this);sort_column(event) ;"><span></span><img src="' + url + '/sort_down.png" width="12"><img src="' + url + '/sort_down2.png" width="12"></div>' ;
  for(var i = 0 ; i < table_attr.nr_columns ; i++ )
    {
      var th2 = th.cloneNode(true) ;
      tr_title.appendChild(th2) ;
      th2.type = tr_title.className ;
    }
  table.appendChild(tr_title) ;

  th.innerHTML = input_line ;
  tr_filter = document.createElement('tr') ;
  tr_filter.className = 'filter' ;
  for(var i = 0 ; i < table_attr.nr_columns ; i++ )
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
  for(var i = 0 ; i < table_attr.nr_columns ; i++ )
    tr.appendChild(td.cloneNode(true)) ;

  for(var i = 0 ; i < table_attr.nr_lines ; i++ )
    {
      var t = tr.cloneNode(true) ;
      if ( i % zebra_step === 0 )
	t.zebra = 'separator ' ;
      else
	t.zebra = '' ;
      table.appendChild(t) ;
    }

  _d('headers inited\n') ;

  for(var lin = 0 ; lin < table_attr.nr_lines + nr_headers ; lin++ )
    {
      tr = table.childNodes[lin] ;

      for(var col = 0 ; col < table_attr.nr_columns ; col++ )
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

function update_line(line_id, data_col)
{
  var line = lines[line_id] ;
  if ( line_empty(line) )
    return ;

  var column = columns[data_col] ;
  column.need_update = true ;
  update_columns(line) ;

  if ( table === undefined )
    return ;

  var lin = lin_from_line_id(line_id) ;
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
    number_of_cols = table_attr.nr_columns ;

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
    if ( line >= filtered_lines.length - table_attr.nr_lines )
      line = filtered_lines.length - table_attr.nr_lines + 1 ;
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
    periodic_work_add(update_vertical_scrollbar_cursor_real) ;
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
      p.style.height = sb_line_to_pixel(line_offset + table_attr.nr_lines)
	- sb_line_to_pixel(line_offset) ;
    }
  update_vertical_scrollbar_cursor_real() ;
}

function update_vertical_scrollbar_position()
{
    periodic_work_add(update_vertical_scrollbar_position_real) ;
    periodic_work_add(update_vertical_scrollbar_cursor_real) ;
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
  line_offset = sb_pixel_to_line(y,true) - Math.floor(table_attr.nr_lines/2) ;
  if ( line_offset < 0 )
    line_offset = 0 ;
  var new_y = sb_pixel_to_line(y,true) - line_offset + nr_headers ;
  if ( new_y >= table_attr.nr_lines + nr_headers ) // Should never be true.
    new_y = table_attr.nr_lines - 1 + nr_headers ;
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
  s = '<span class="position">&nbsp;</span><img src="' + url + '/up.gif" onclick="javascript:previous_page();"><img src="' + url + '/down.gif" onclick="javascript:next_page();"><span class="cursor"></span>' ;


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
    periodic_work_add(update_vertical_scrollbar_real) ;
    periodic_work_remove(update_vertical_scrollbar_cursor_real) ;
    periodic_work_remove(update_vertical_scrollbar_position_real) ;
}

function table_header_fill()
{
    periodic_work_add(table_header_fill_real) ;
}

function table_header_fill_real()
{
  var empty_column = add_empty_columns() ;
  var cls = column_list() ;
  var w ;

  the_current_cell.update_column_headers() ;
  update_horizontal_scrollbar(cls) ;

  for(var data_col in columns)
    columns[data_col].col = undefined ;

  // This loop is not with the other in order to speed up display.
  // So the table is not displayed with all the possible columns width.
  var width = 0 ;
  for(var col = 0 ; col < table_attr.nr_columns ; col++)
    {
      width += cls[col].width + 1 ;
    }

  //var x = '' ;
  for(var col = 0 ; col < table_attr.nr_columns ; col++)
    {
      w = ((window_width()*cls[col].width)/width-8).toFixed(0) ;
      // tr_title.childNodes[col].style.width = width + 'px' ;
      if ( w <= 0 )
	w = 1 ;
      colgroup.childNodes[col].width = w ;
      //x += '   ' + w ;
    }
  //alert(x) ;

  for(var col = 0 ; col < table_attr.nr_columns ; col++)
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
      var title = td_title.childNodes[0] ;

      // td_title.data_col = td_filter.data_col = column.data_col ;

      title.firstChild.innerHTML = html(column.title) ;
      td_filter.childNodes[0].value = column.filter ;
      if ( column.filter === '' )
	td_filter.childNodes[0].className = 'empty' ;
      else
	td_filter.childNodes[0].className = '' ;
      if ( column.freezed !== '' )
	td_filter.childNodes[0].className += ' freezed' ;
      
      td_title.className = className ;

      for(var i=0; i<2; i++)
	{
	  var img = title.childNodes[i+1] ;
	  if ( column != sort_columns[i] )
	    img.style.display = 'none' ;
	  else
	    {
	      if ( i == 0 )
		td_title.className += ' sorted' ;
	      if ( column.dir < 0 )
		img.src = img.src.replace('sort_up', 'sort_down');
	      else
		img.src = img.src.replace('sort_down', 'sort_up');
	      img.style.display = '' ;
	    }
	}
    }
  // XXX If updated, the value being edited may be erased
  if ( ! the_current_cell.focused )
    the_current_cell.update(true) ;
}

/******************************************************************************
Filter and sort the lines of data
******************************************************************************/
function get_filtered_lines()
{
  var f = [], empty ;

  nr_not_empty_lines = 0 ;
  if ( filters.length === 0 )
    {
      for(var line in lines)
	{
	  empty = line_empty(lines[line]) ;
	  if ( ! empty )           // Not empty on screen
	    nr_not_empty_lines++ ;
	  if ( empty !== true )
	    f.push(lines[line]) ;  // Not empty on screen AND history
	}
      return f ;
    }

  for(var line in lines)
    {
      line = lines[line] ;
      empty = line_empty(line) ;
      if ( ! empty )
	nr_not_empty_lines++ ;
      if ( empty ) // empty on screen
	continue ;
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
  var d1 = millisec();
  filtered_lines = get_filtered_lines() ;

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
  if ( document.getElementById('nr_not_empty_lines') )
    document.getElementById('nr_not_empty_lines').innerHTML
      = nr_not_empty_lines ;

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
  for(var col = 0 ; col < table_attr.nr_columns ; col++)
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

function table_fill_do()
{
    table_fill_real() ;
    
    if ( table_fill_hook )
	{
	    table_fill_hook() ;
	    table_fill_hook = undefined ;
	}
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
}

function manage_window_resize_event()
{
  var width=window_width(), height=window_height() ;
		
  if ( current_window_width != width )
    {
      if ( table_attr.default_nr_columns == 0 )
				{
					compute_nr_cols() ;
				}
      update_column_menu() ;
      update_histogram(true) ;
    }
  if ( current_window_height != height )
    {
      if ( preferences.nr_lines == 0 )
				compute_nr_lines() ;
      update_line_menu() ;
    }
  if ( current_window_width != width || current_window_height != height )
    {
      the_current_cell.input.blur() ;
      table_init() ;
      table_fill(false, true, true) ;
      current_window_width = width ;
      current_window_height = height ;
    }
  return true ;
}

function login_list_ask()
{
	if ( the_current_cell.column.type != 'Login' )
		return ;
  if ( the_current_cell.initial_value != the_current_cell.input.value
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
	return true ;
}

function login_list_hide()
{
  the_current_cell.blur_disabled = false ;
  hide_the_tip_real() ;
}

function login_list_select(t)
{
  var s = t.options[t.selectedIndex].innerHTML.split('&nbsp;')[0] ;
  the_current_cell.input.value = s ;
  login_list_hide() ;
  the_current_cell.change() ;
}

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

  var nr = Math.floor(table_attr.nr_lines / 2) ;
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
  var display_tips_saved = display_tips ;
  display_tips = true ;
  show_the_tip(the_current_cell.td, s) ;
  display_tips = display_tips_saved ;
  get_tip_element().onmousemove = function() { } ;

}

function table_fill(do_not_focus, display_headers, compute_filtered_lines)
{
  if ( table === undefined )
    return ;
  if ( table_forms_element )
    display_headers = false ;
  table_fill_do_not_focus = do_not_focus ;
  if ( compute_filtered_lines )
      periodic_work_add(update_filtered_lines) ;
  periodic_work_add(table_fill_do) ;
  if ( display_headers )
    table_header_fill() ;
}

function table_fill_real()
{
  var read = 0 ;
  var write = nr_headers ;
  var td ;
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
      if ( write == table_attr.nr_lines + nr_headers )
	break ;
    }
  // lines of tables after the end of the data, the empty lines
  while( write < table_attr.nr_lines + nr_headers )
    {
      var tr = table.childNodes[write] ;
      tr.className = tr.zebra ;
      for(var col = 0 ; col < table_attr.nr_columns ; col++)
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
  for(var i in columns)
    if ( line[i].history )
      return 1 ;
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

function first_column_not_empty()
{
  for(var i = columns.length - 1 ; i >=0 ; i--)
    if ( ! column_empty( i ) )
      break ;
  return i ;
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

function add_empty_columns()
{
  var not_empty = first_column_not_empty() ;
  var nr_empty_columns = columns.length - not_empty - 1 ;

  /* There is a +5 because a user may hide empty columns.
     It will make 'column_list' function have problems
     because there is missing empty columns.
     So, we add some more.
  */
  for(var i = 0 ; i < table_attr.nr_columns - nr_empty_columns + 5 ; i++)
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
       && line_offset + table_attr.nr_lines > filtered_lines.length )
    return true;

  if ( dy === undefined )
    dy = Number((table_attr.nr_lines * preferences.page_step).toFixed(0)) ;


  if ( next_cell )
    {
      table_fill_hook = function() {
	cell_goto(table.childNodes[nr_headers+table_attr.nr_lines-dy].childNodes[the_current_cell.col]) ;
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
    dy = Number((table_attr.nr_lines * preferences.page_step).toFixed(0)) ;
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
    cell_goto(tr.childNodes[0], true);
  else if ( col < table_attr.nr_columns )
    cell_goto(tr.childNodes[col], true);
  else
    cell_goto(tr.childNodes[table_attr.nr_columns-1], true);
}

/*
 * If 'col' is defined : then it is the required column (centered)
 * Else 'direction' is a delta
 */
function page_horizontal(direction, col, do_not_focus)
{
  var cls = column_list_all() ;

  if ( ! do_not_focus )
    the_current_cell.change() ;

  if ( col === undefined )
    {
      col = myindex(cls, the_current_cell.data_col) +
	( direction > 0 ? 1 : -1 )  ;
      if ( direction > 0 && col === 0 )
	{
	  // alert("À quoi cela vous sert d'aller à droite, le tableau est vide !") ;
	  return ;
	}
      column_offset += direction ;
    }
  else
    {
      column_offset = col - Math.floor((table_attr.nr_columns+nr_freezed())/2);
    }

  next_page_col = col ;
  next_page_line = the_current_cell.lin ;
 
  if ( column_offset + table_attr.nr_columns > columns.length )
    column_offset = columns.length - table_attr.nr_columns ;
  if ( column_offset < 0 )
    column_offset = 0 ;

  the_current_cell.focused = false ; // XXX Kludge for XXX_HS
  table_fill_hook = table_fill_hook_horizontal ;
  table_fill(do_not_focus, true) ;


  periodic_work_do() ;
}

function next_page_horizontal(delta)
{
  page_horizontal( Math.floor((table_attr.nr_columns-nr_freezed()) / 2),delta);
}

function previous_page_horizontal(delta)
{
  page_horizontal(-Math.floor((table_attr.nr_columns-nr_freezed())/ 2),delta) ;
}


/******************************************************************************
Cursor movement
******************************************************************************/

function cell_get_value_real(line_id, data_col)
{
  return columns[data_col].real_type.formatte(lines[line_id][data_col].value,
					      columns[data_col]);
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
  if ( cell.date >= today )
    className += ' today' ;
  if ( v === '' && column.empty_is )
    {
      className += ' default' ;
      v = column.empty_is ;
    }
  if ( v.toFixed )
    {
      className += ' number' ;
      v = column.real_type.formatte(v, column) ;
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
      if ( column.parsed_course_dates )
	{
	  var t, first, last, stop = false ;
	  for(var a in abj[0])
	    {
	      a = abj[0][a] ;
	      first = parse_date(a[0]).getTime() ;
	      last = parse_date(a[1]).getTime() ;
	      for(var date in column.parsed_course_dates)
		{
		  t = column.parsed_course_dates[date] ;
		  if ( t >= first && t <= last )
		    {
		      className = className.substr(2).replace(' default','')
		      className += ' is_not_an_abi' ;
		      stop = true ;
		      break ;
		    }
		}
	      if ( stop )
		break ;
	    }
	}
      else
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
	      if ( parse_date(a[0]).getTime() <= d
		   && d < parse_date(a[1]).getTime() + 86400000*7 )
		{
		  className += ' is_an_abj' ;
		  break ;
		}
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

// Indicate that 'line_id' will be filled
function add_a_new_line(line_id)
{
  if ( line_id === undefined )
    {
      line_id = page_id + '_' + nr_new_lines ;
      nr_new_lines++ ;
    }

  if ( lines[line_id] )
    return ;

  // Create a new line

  var line = [] ;
  for(var c in columns)
    line[c] = C();
  line.line_id = line_id ;
  lines[line_id] = line ;
  filtered_lines.push(line) ;

  /* Update screen table with the new id */
  var lin = filtered_lines.length - 1 - line_offset ;
  if ( lin >= 0 && lin < table_attr.nr_lines )
    {
      line_fill(filtered_lines.length-1, lin + nr_headers) ;
    }
  return line_id ;
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

function cell_set_value_real(line_id, data_col, value, td)
{
  var cell = lines[line_id][data_col] ;
  var column = columns[data_col] ;

  // toString is used because '' != '0' and '00' != '000'
  // === is not used because 5.1 == "5.1"
  if ( value.toString() == lines[line_id][data_col].value.toString() )
    return ;

  if ( ! cell.modifiable(column) )
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
  add_a_new_line(line_id) ;

  // Does history should be modified in set_value ?
  if ( ! cell.never_modified() )
    cell.history += cell.value + '\n('+ cell.date + ' ' + cell.author + '),·' ;
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
	       line_id + "/" + encode_uri(cell.value)
	       );

  if ( value !== '' )
    column.is_empty = false ;

  update_histogram(true) ; // XXX

  return v ;

}

function cell_set_value(td, value, line_id, data_col)
{
  if ( value === undefined )
    // Next/Prev page if there is not a cell selected (Prst)
    return cell_get_value_real(line_id, data_col) ;

  var v = cell_set_value_real(line_id, data_col, value, td) ;
  if ( v !== undefined )
    return v ;
  return cell_get_value_real(line_id, data_col) ;
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
  while ( anchor.offsetHeight === undefined ) // Firefox bug on SVG histogram
    anchor = anchor.parentNode ;

  var pos = findPos(anchor) ;

  tip_display_date = millisec() ;

  if ( element.tagName != 'TD' )
    {
      element.style.top = pos[1] + anchor.offsetHeight ;
      element.style.bottom = 'auto' ;
      if ( pos[0] + element.offsetWidth < window_width() + scrollLeft() )
	{
	  element.style.left = pos[0] ;
	  element.style.right = 'auto' ;
	}
      else
	{
	  element.style.left = 'auto' ;
	  element.style.right = 0 ;
	}
      return ;
    }

  if ( pos[1] > scrollTop() + window_height()/2)
    {
      element.style.bottom = window_height() - pos[1] ;
      element.style.top = 'auto' ;
    } 
  else
    {
      element.style.top = pos[1] + anchor.offsetHeight ;
      element.style.bottom = 'auto' ;
    }

  if ( element.offsetWidth < pos[0] - scrollLeft() )
    {
      element.style.right = window_width() - pos[0] ;
      element.style.left = 'auto' ;
    }
  else if ( pos[0] + anchor.offsetWidth + element.offsetWidth
	    < window_width() + scrollLeft() )
    {
      element.style.left = pos[0] + anchor.offsetWidth ;
      element.style.right = 'auto' ;
    }
  else
    {
      element.style.left = scrollLeft() ;
      element.style.right = 'auto' ;
    }
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
  if ( highlight_list.length )
    return true ;
}

function highlight_add(element)
{
  // The spaces broke the filter input with empty message ??? XXX WHY
  // element.className += (element.className + ' highlight1')
  //  .replace('empty','').replace(/^ */,'').replace(/ *$/,'') ;
  // With this code, highlight of 'freezed' link does not happen.

  element.className = 'highlight1' ;
  if ( myindex(highlight_list, element) == -1 )
    {
      highlight_list.push(element) ;
      periodic_work_add(highlight_effect) ;
    }
}


// In firefox a VAR object disapear from DOM tree !
function update_tip_from_value(o, value)
{
  if ( !o )
    return ;
  var e = tip_top(o).childNodes[0].lastChild ;

  // XXX
  // with IE there is a problem because 'e' can be a 'text' element
  // It is impossible : so where is the bug ?
  // It is raised on 'column_columns' tip attribute
  if ( e.className === undefined )
    return ;

  e.className = 'more' ;

  if ( value.substr(value.length-1) != '\n' ) // Tip with HTML inside
    e.innerHTML = html(value) ;
  else
    e.innerHTML = value ;
}

function update_value_and_tip(o, value)
{
  if ( !o )
    {
      alert(value) ;
      return ;
    }
  if ( o.tagName == 'SELECT' )
    return ;

  value = html(value.toString()) ;
  var v = value + '&nbsp;' ;
  if ( o.innerHTML != v )
    {
      highlight_add(o) ;
      if ( o.tagName != 'INPUT' )
	{
	  o.innerHTML = v ;
	  update_tip_from_value(o, value) ;
	}
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
  // update_tip_from_value(element, element.value) ;
}

function cell_goto(td, do_not_focus)
{
  var lin = lin_from_td(td) ;
  var col = col_from_td(td) ;
  var data_col = data_col_from_col(col) ;
  var line_id = line_id_from_lin(lin) ;
  var column = columns[data_col] ;

  if ( do_not_focus !== true && element_focused )
    {
      element_focused.blur();// To save values being edited before cell change.
      if ( element_focused && element_focused.onblur )
	element_focused.onblur() ; // Buggy Browser
    }

  if ( the_current_cell.td != td && do_not_focus !== true )
    the_current_cell.input.selectionEnd = 0 ; // For Opera

  the_current_cell.jump(lin, col, do_not_focus, line_id, data_col) ;
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
      server_feedback.innerHTML = '' ; // Hide green image
    }

  if ( t === undefined )
    return ;

  if ( t.request.saved )
    return ;
  saved(t.request.request_id) ;
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

function store_unsaved()
{
  if ( ! table_attr.autosave )
    return ;
  auto_save_errors() ; // Cleanup pending_requests list
  if ( pending_requests.length == 0 )
    return ;
  if ( ! localStorage )
    {
      alert("Désolé, la fenêtre a été fermée sans tout sauvegarder") ;
      return ;
    }
  var s = [] ;
  for(var i in pending_requests)
    {
      i = pending_requests[i] ;
      s.push(i.content) ;
    }
  localStorage['/' + year + '/' + semester + '/' + ue] = s.join('\n') ;
  index = localStorage['index'] ;
  if ( ! index )
    index = '' ;
  index += '\n' + '/' + year + '/' + semester + '/' + ue ;
  localStorage['index'] = index ;
}

var do_reload_when_all_saved = false ;

function restore_unsaved()
{
  if ( ! localStorage )
    return ;
  var t = localStorage['/' + year + '/' + semester + '/' + ue] ;
  if ( ! t )
    return ;
  var t_splited = t.split('\n') ;
  var message = '', line ;
  for(var i in t_splited)
    {
      line = t_splited[i].split('/') ;
      if ( line[0] == 'cell_change' )
	{
	  var data_col = data_col_from_col_id(line[1]) ;
	  var line_id = line[2] ;
	  if ( data_col !== undefined && lines[line_id] !== undefined )
	    {
	      message += lines[line_id][0].value + ' ' +
		lines[line_id][1].value + ' ' + lines[line_id][2].value 
		+ ', ' + columns[data_col].title + ' = ' + line[3] + '\n' ;
	      continue ;
	    }
	}
      message += t_splited[i] + '\n' ;
    }

  if ( confirm("Voulez-vous restaurer les actions suivantes :\n" + message) )
    {
      for(var i in t_splited)
	pending_requests.push(new Request(t_splited[i])) ;
      periodic_work_add(auto_save_errors) ;
      create_popup('restoring_data',
		   'Sauvegarde en cours, veuillez patienter',
		   '', '', message) ;
    }
  else
    t = '' ;
  localStorage['/' + year + '/' + semester + '/' + ue] = '' ;
  index = localStorage['index'] ;
  localStorage['index'] = index.replace(RegExp('\n/'+year+'/'+semester+'/'+ue,
					       'g'), '') ;
  if ( t )
    do_reload_when_all_saved = true ;
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
    + encode_uri('_URL_/allow/'+ticket+'/'+millisec()).replace(/%01/g, '%2F')
    + '\')">CLIQUEZ ICI<br>POUR VOUS AUTHENTIFIER À NOUVEAU<br>votre session a expiré ou<br>votre machine a changé de réseau.</a>' ; 
  t_authenticate.style.display = 'block' ;
  t_authenticate.innerHTML = m ;
  connection_state = 'auth' ;
}

/*
 ****************************************************************************
 * Management of periodic work.
 * Once added, the function is called every 0.1 seconds until it returns false
 * 'add' can be called from a periodic function, in this case the function
 * may be called more than one in a period.
 * When a function is added to the list, it goes to the end,
 * so it is processed after the others.
 ****************************************************************************
 */

var periodic_work_functions = [] ;
var periodic_work_id ;

function periodic_work_add_once(table, item) // Do not use this
{
    var i = myindex(table, item) ;
    if ( i == -1 )
	table.push(item) ;
    else
	{
	    table.splice(i, 1) ;
	    table.push(item) ;
	}
}

function periodic_work_in_queue(f) // The function is the the queue
{
    return myindex(periodic_work_functions, f) != -1 ;
}

function periodic_work_add(f)
{
    periodic_work_add_once(periodic_work_functions, f) ;
    if ( periodic_work_id === undefined )
	periodic_work_id = setInterval(periodic_work_do, 100) ;    
}

function periodic_work_remove(f)
{
    var i = myindex(periodic_work_functions, f) ;
    if ( i != -1 )
	periodic_work_functions.splice(i, 1) ;
}

function periodic_work_do()
{
  var f, to_do ;
  var to_continue = [] ;
  while(periodic_work_functions.length)
    {
      to_do = periodic_work_functions ;
      periodic_work_functions = [] ;
      for(f in to_do)
	{
	  f = to_do[f] ;
	  if ( f() )
	    periodic_work_add_once(to_continue, f) ;
	}
    }
  periodic_work_functions = to_continue ;
  if ( to_continue.length == 0 )
    {
      clearInterval(periodic_work_id) ;
      periodic_work_id = undefined ;
    }
  //  p_title_links.innerHTML = periodic_work_functions.length ;
}


// **********************************************************
// Restart image loading if the connection was not successul
// **********************************************************

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
    return true ;

  auto_save_running = true ;

  _d('(autosave[' + connection_state + ', server_feedback(answered=' +
     server_feedback.answered + ',time=' + server_feedback.time +
     '),last_server_answer=' + last_server_answer + ']' );

  var d = millisec() ;
  nr_saved = 0 ;

  for(var i in pending_requests)
    {
      i = pending_requests[i] ;
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

  var saving = document.getElementById('saving') ;
  if ( saving )
    {
      if ( nr_unsaved > 10 )
	document.getElementById('saving').style.display = 'block' ;
      if ( nr_unsaved == 0 )
	document.getElementById('saving').style.display = 'none' ;
    }

  if ( do_reload_when_all_saved && nr_unsaved == 0 )
    {
      window.location = window.location ;
      do_reload_when_all_saved = false ;
    }

  // Remove the item 10 by 10 (it's slow one by one)
  for(var i=10; i>=0; i--)
    if (  pending_requests[i] && ! pending_requests[i].saved )
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

  if ( pending_requests.length != 0 )
      return true ; // Continue
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
  periodic_work_add(auto_save_errors) ;

  if ( td )
    {
      var child = td.childNodes[0] ;
      if ( child !== undefined && child.style !== undefined
	   && child.tagName != 'SPAN')
	{
	  var width ;
	  if ( child.id === '' )
	    width = child.offsetWidth - 7 ;
	  else
	    width = child.offsetWidth - 0 ;
	  if ( width > 0 )
	    child.style.width = width ;
	}

      s = url_base() ;
      request.image = s.childNodes[0] ;
      request.image.request = request ;
      td.appendChild(s) ;
    }
}

function login_to_line_id(login)
{
  for(var line_id in lines)
    if (login_to_id(lines[line_id][0].value) == login)
      return line_id ;
}


/* Communication from the server */
function Xcell_change(col, line_id, value, date, identity, history)
{
  var data_col = data_col_from_col_id(col) ;
  add_a_new_line(line_id) ;

  var cell = lines[line_id][data_col] ;

  cell.set_value(value) ;
  cell.author = identity ;
  cell.date = date ;
  cell.history = history ;

  var td = td_from_line_id_data_col(line_id, data_col) ;

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
  update_line(line_id, data_col) ;
}

function Xcomment_change(identity, col, line_id, value)
{
  var data_col = data_col_from_col_id(col) ;
  add_a_new_line(line_id) ;
  var cell = lines[line_id][data_col] ;

  cell.set_comment(value) ;

  var td = td_from_line_id_data_col(line_id, data_col) ;
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

  for(line_id in lines)
    lines[line_id].splice(data_col ,1) ;
  columns.splice(data_col ,1) ;
  for(data_col in columns)
    columns[data_col].data_col = Number(data_col) ;
  the_current_cell.update() ;

  if ( page != ' ')
    alert("Désolé pour le dérangement, mais je dois tout réafficher car quelqu'un a détruit une colonne") ;
  the_current_cell.do_update_column_headers = true ;
  the_current_cell.update_headers() ;
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
  attr_update_user_interface(column_attributes[attr], column, true) ;
}

function Xtable_attr(attr, value)
{
  table_attr[attr] = table_attributes[attr].formatter(value) ;
  the_current_cell.update_table_headers();
}

function update_table_size()
{
  // In order to force Gecko to update table size
  var tr = table.childNodes[table_attr.nr_lines + nr_headers - 1] ;

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
      try { event.keyCode = 0; } catch(e) { } ;
    }

  event.cancelBubble = true ;
}


function toggle_display_tips()
{
  display_tips = ! display_tips ;
  if ( ! display_tips )
    hide_the_tip_real() ;
}

// Set comment

function comment_change(line_id, data_col, comment, td)
{
  create_column(columns[data_col]) ;
  add_a_new_line(line_id) ;

  lines[line_id][data_col].set_comment(comment);
  var col_id = columns[data_col].the_id ;
  append_image(td, 'comment_change/' + col_id + '/' +
	       line_id + '/' + encode_uri(comment)) ;
}

function comment_on_change()
{
  var input = the_comment ;

  if ( the_comment === undefined )
    return ;

  if ( lines[the_current_cell.line_id][the_current_cell.data_col].comment == input.value )
    return ;

  if ( ! cell.modifiable(the_current_cell.column) )
    {
      alert("Vous n'avez pas l'autorisation de modifier ce commentaire");
      return ;
    }
  
  the_current_cell.td.className += ' comment' ;
  comment_change(the_current_cell.line_id, the_current_cell.data_col,
		 input.value, the_current_cell.td) ;
}

/* CSV */

function csv_cell_coma(x)
{
  if ( x.replace === undefined )
    return x + ',' ; // Number
  else
    return '"' + x.replace(/"/g, '""') + '",' ;
}

function csv_cell_dot_coma(x)
{
  if ( x.replace === undefined )
    return x.toString().replace('.',',') + ';' ; // Number
  else
    return '"' + x.replace(/"/g, '""') + '";' ;
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


  for(var i in filtered_lines)
    {
      var line = filtered_lines[i] ;
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
  var column ;

  for(var data_col in columns)
    {
      column = columns[data_col] ;
      if ( column.filter !== '' )
	s += 'Filtre sur la colonne <B>'
	  + column.title + '</B> : <b>' + html(column.filter)
	  + '</b><BR>\n' ;
    }
  return s ;
}

function printable_introduction()
{
  var name_sort = '' ;

  if ( tr_classname !== undefined )
    if ( sort_columns[0].data_col != 2 )
      name_sort = '<span style="background:#F00;color:white">La liste n\'est pas dans l\'ordre alpabétique des noms.</span>' ;

  return '<p class="hidden_on_paper printable_introduction">'
    + "Ce qui est sur fond jaune n'est pas imprimé.<br>"
    + "Les lignes sont triées par «<b>" + sort_columns[0].title
    + '</b>» puis «<b>' + sort_columns[1].title + '</b>»<br>'
    + the_filters() + name_sort ;
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

function lines_in_javascript()
{
  var s = [], t, x, i ;
  for(i in filtered_lines)
    {
      line = filtered_lines[i] ;
      if ( display_on_signature_table(line) )
	{
	  t = [] ;
	  for(var data_col in columns)
	    t.push(line[data_col].get_data()) ;

	  x = the_student_abjs[line[0].value] ;
	  if ( x && x[2] )
	    t.push(js('<li>' +x[2].substr(0,x[2].length-1).replace(/\n/g,'<li>'))) ;

	  s.push('[' + t.join(',') + ']') ;
	}
    }
  return '[\n' + s.join(',\n') + ']' ;
}

function columns_in_javascript()
{
  var s = [], p, column, all_cls ;
  all_cls = column_list_all() ;
  for(var i in all_cls)
    columns[all_cls[i]].ordered_index = i ;

  for(var data_col in columns)
    {
      column = columns[data_col] ;
      p = [] ;

      for(var attr in column_attributes)
	p.push('"' + attr + '":' + js(column[attr])) ;

      p.push("green_filter:" + column.color_green_filter) ;
      p.push("red_filter:" + column.color_red_filter) ;
      if ( isNaN(column.red) || column.red === '' )
	p.push("color_red:" + js(column.red)) ;
      else
	p.push("color_red:" + column.red) ;
      if ( isNaN(column.green) || column.green=== ''  )
	p.push("color_green:" + js(column.green)) ;
      else
	p.push("color_green:" + column.green) ;
      p.push("min:" + column.min) ;
      p.push("max:" + column.max) ;
      p.push("ordered_index:" + column.ordered_index) ;
      s.push('{' + p.join(',\n') + '}') ;
    }
  return '[\n' + s.join(',\n') + ']' ;
}

function button_toggle(dictionnary, data_col, tag)
{
  if ( dictionnary[data_col] )
    {
      delete dictionnary[data_col] ;
      tag.className = tag.className.replace(/ toggled/g, '') ;
    }
  else
    {
      tag.className += ' toggled' ;
      dictionnary[data_col] = true ;
    }
}

function radio_buttons(variable, values, selected)
{
  var value, the_class, tip, v ;
  var s = ['<script>' + variable + ' = "' + selected + '";</script>'] ;

  s.push('<var>') ;
  for(var i in values)
    {
      value = values[i] ;

      if ( value.sort )
	{
	  tip = value[1] ;
	  value = value[0] ;
	}
      else
	tip = '' ;

      
      if ( value == selected )
	the_class = 'toggled' ;
      else
	the_class = '' ;
      v = '<span class="button_toggle ' + the_class
	+ '" onclick="' + variable + "='" + value
	+ "'; radio_clean(this);this.className += ' toggled' ;"
	+ 'do_printable_display=true;">' +
	(tip ? hidden_txt(value,tip) : value) + '</span>' ;
      s.push(v) ;
    }
  s.push('</var>') ;
  return s.join('\n') ;
}

function radio_clean(t)
{
  for(t = t.parentNode.firstChild; t; t = t.nextSibling)
    if ( t.tagName == 'SPAN' )
      t.className = t.className.replace(/ toggled/,'') ;
}

function compute_groups_key(grouped_by, line)
{
  var s = [] ;
  for(var data_col in grouped_by)
    if ( grouped_by[data_col] )
      s.push(line[data_col].value) ;
  return s.join('\001') ;
}

function compute_groups_values(grouped_by)
{
  var g = {}, s ;
  for(var line_id in lines)
    g[compute_groups_key(grouped_by, lines[line_id])] = true ;
  tabl = [] ;
  for(var gg in g)
    tabl.push(gg) ;
  tabl.sort() ;
  return tabl ;
}

function goto_resume()
{
  window_open(url + '/=' + ticket + '/' + year + '/' + semester + '/' + ue + '/resume');
}

// pb = page break
function html_begin_head(hide_title, pb, more)
{
  var s = '' ;

  var p = '{' ;
  for(var i in preferences)
    p += i + ':"' + preferences[i] + '",' ;
  p = p.substr(0,p.length-1) + '};' ;

  var a = '{' ;
  for(var i in table_attr)
    a += i + ':' + js(table_attributes[i].formatter(table_attr[i])) + ',' ;
  a = a.substr(0,a.length-1) + '}' ;

  if ( ! pb )
    s = '<html><head>\n' +
      '<link rel="stylesheet" href="'+url + '/style.css" type="text/css">\n' +
      '<script src="' + url + '/utilities.js" onload="this.onloadDone=true;"></script>\n' +
      '<script src="' + url + '/middle.js" onload="this.onloadDone=true;"></script>\n' +
      '<script src="' + url + '/lib.js" onload="this.onloadDone=true;"></script>\n' +
      '<script src="' + url + '/types.js" onload="this.onloadDone=true;"></script>\n' +
      '<script src="' + url + '/abj.js" onload="this.onloadDone=true;"></script>\n' +
      '<style id="computed_style"></style>\n' +
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
      'lines = {} ;\n' +
      'adeweb = {};\n' + // XXX should not be here (LOCAL/spiral.py)
      'table_attr = ' + a + ';\n' +
      wait_scripts + // The function definition
      '</script>\n' +
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
  return html_begin_head(true) +
    head_html() +
    new_interface() ;
}

// Function to enhance and coordinate with tail.html
function virtual_table_common_end()
{
  return tail_html() ;
}

// XXX yet done somewhere else
function student_search(id)
{
  for(var line_id in lines)
    if ( lines[line_id][0].value == id )
      return line_id ;

  id = login_to_id(id) ;
  for(var line_id in lines)
    if ( lines[line_id][0].value == id )
      return line_id ;
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
  var tip = get_tip_element() ;
  tip.onmousemove = function() {} ;
  tip.style.display = "none" ;
  tip.tip_target = undefined ;
  // remove_highlight() ;
}

function hide_the_tip(real)
{
  var tip = get_tip_element() ;
  if ( tip.style.display == "none" )
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
  table_attr.nr_columns += dx ;
  table_attr.nr_lines += dy ;
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


function change_table_size(select)
{
  var i = select.childNodes[select.selectedIndex].innerHTML ;
  i = Math.floor(i.split(' ')[0]) ; // Remove text after number
  if ( select.id == 't_table_attr_nr_columns' )
    {
      table_attr.nr_columns = i ;
      column_offset = 0 ;
      if ( the_current_cell.col >= table_attr.nr_columns )
	the_current_cell.col = table_attr.nr_columns - 1 ;
    }
  else
    {
      table_attr.nr_lines = i ;
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

  var i, i_striped ;
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
      i_striped = i.toString().replace(' (tout)','') ;
      if ( i_striped == current )
	sel = ii ;
      option.innerHTML = i ;
      option.value = i_striped ;
      if ( created )
	select.appendChild(option) ;
    }
  select.selectedIndex = sel ;
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
  var server_answer = document.getElementById('server_answer') ;
  if ( ! server_answer )
    return ;
  if ( connection_state == 'auth' )
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
    table_attr.nr_lines = preferences.nr_lines ;
  if ( Number(preferences.zebra_step) > 0 )
    zebra_step = Number(preferences.zebra_step) ;
  else
    zebra_step = 3 ;
  if ( preferences.nr_cols > 0 && preferences.nr_cols < 100 )
    table_attr.nr_columns = preferences.nr_cols ;

  if ( table_attr.default_nr_columns )
    table_attr.nr_columns = table_attr.default_nr_columns ;
  if ( test_bool(preferences.v_scrollbar) == no )
    vertical_scrollbar = undefined ;

  for(var line_id in lines)
    {
      lines[line_id].line_id = line_id ;
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

  // This function is used when we want to replace the current window
  // content by the popup content.
  // It is NEEDED because some browser open popup UNDER the current window
  function replace_window_content(w)
  {
    for(var i in the_body.childNodes)
      if ( the_body.childNodes[i].style )
	the_body.childNodes[i].style.display = 'none' ;
    
    if (w)
      setTimeout(function() { if ( popup_blocker ) { alert(allow_popup_message);popup_blocker=false;}} , 10000) ;
  }

  if ( get_option('print-table', 'a') !== 'a' )
    {
      replace_window_content(print_selection(undefined, undefined, '_self'));
      return ;
    }
  if ( get_option('signatures-page', 'a') !== 'a' )
    {
      replace_window_content(print_selection(undefined, 1, '_self')) ;
      return ;
    }
  if ( get_option('facebook', 'a') !== 'a' )
    {
      replace_window_content(tablefacebook('_self')) ;
      return ;
    }
  if ( table_forms_element || get_option('tableforms', 'a') !== 'a' )
    {
      setTimeout(table_forms, 1500) ;
    }


  if ( preferences.interface == 'L' )
    {
      dispatch('init') ;
      return ;
    }

  /*
   * The normal interface (not linear)
   */

  table_init() ;
  table_fill(true, true, true) ;

  if ( ue == 'javascript_regtest_ue' )
    {
      javascript_regtest_ue() ;
    }

  if (window.addEventListener)
    /** DOMMouseScroll is for mozilla. */
    window.addEventListener('DOMMouseScroll', wheel, false);
  /** IE/Opera. */
  window.onmousewheel = document.onmousewheel = wheel;

  if ( window.attachEvent )
    {
      // IE does not launch resize event if the window is loading
      periodic_work_add(manage_window_resize_event) ;
    }
  else
    window.onresize = manage_window_resize_event ;

  
	
  if ( ue != 'VIRTUALUE' && ue != '' && page_id > 0 )
    document.write('<img width="1" height="1" src="' + url + "/=" + ticket
		   + '/' + year + '/' + semester + '/' + ue + '/' +
		   page_id + '/end_of_load" style="position:absolute;left:0;top:0">') ;


  // Firefox bug : the page refresh reload the old iframe, not the new one
  setTimeout(reconnect, 10) ;

  the_current_cell.jump(nr_headers, 0, true) ;
  the_current_cell.update_table_headers() ;
  change_title(table_attr.table_title, table_attr.code) ;

  restore_unsaved() ;
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
	{
	  if ( column.weight.substr(0,1) == '+'
	       || column.weight.substr(0,1) == '-' )
	    comment += 'Poids du bonus/malus : ' ;
	  else
	    comment += 'Poids dans la moyenne pondérée : ' ;
	  comment += '<b>' + column.weight + '</B><br>' ;
	}
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
	    hidden(title.replace(/_/g,' ')+':<b>'+ visual_cell[0] + '</b>', 
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
	if ( column_modifiable_attr('columns', column) )
	  {
	    for(var depend in column.average_columns)
	      {
		name = columns[column.average_columns[depend]].title
		  visual_cell = cols[name] ;
		if ( visual_cell === undefined )
		  continue ;
		visual_cell[3] = true; // Used
		s += fusion(name, depend==0) ;
	      }
	  }
	visual_cell = cols[title] ;
	//return '['+title+','+s+']' ;
	if ( first )
	  first = ' first_child' ;
	else
	  first = '' ;
	if ( s === '' )
	  v = '<div class="notes fine ' + visual_cell[1] + first + '">'
	    + hidden_txt('<i>' + title.replace(/_/g,' ') + '<br>'
			 + visual_cell[0] + '</i>', visual_cell[2])
	    + '</div>' ;
	else
	  v = '<div class="notes' + first + '">'
	    + hidden_txt('<i>' + title.replace(/_/g,' ')
			 + ': ' + visual_cell[0] + '</i><br>',
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
  function table_fill_try()
  {
    
  }
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
	set_select_by_value(i, v) ;
	window.event = new Object() ;
	window.event.target = i ;
	i.onchange(window.event) ;
	break ;
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
    for(var i in content)
      {
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

  lines = {} ;
  columns = [] ;
  add_empty_columns() ;
  table_attr.default_sort_column = 0 ;
  sort_columns = [columns[0],columns[1]] ;
  update_filtered_lines();
  the_current_cell.jump(nr_headers,0) ;
  table_attr.nr_columns = 12 ;
  table_attr.nr_lines = 14 ;

  alert_real = alert ;
  var alert_messages = '' ;

  if ( navigator.appName != 'Microsoft Internet Explorer' )
    alert = function(x) { alert_messages += escape(x) + '<hr>' ; } ;

  table_init() ;
  update_columns() ;
  table_fill(false, true,true) ; periodic_work_do() ;

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
  table_fill(false, true) ; periodic_work_do() ;
  bigger_column() ;
  bigger_column() ;
  bigger_column() ;
  do_move_column_left() ;
  table_fill(false, true) ; periodic_work_do() ;
  smaller_column() ;
  smaller_column() ;
  smaller_column() ;

  cell_goto(table.childNodes[nr_headers].childNodes[3]) ;
  periodic_work_do() ;
  export_column() ; // Moyenne
  export_column_id_value();
  v = popup_value() ;
  for(var i in inputs)
    if ( v[i] != inputs[i] + '\t' + expore[i] )
      alert_real('Export BUG: line=(' + v[i] + ') != expected=(' + inputs[i] + '\t' + expore[i] + ')');
  popup_close() ;
  expected('');

  cell_goto(table.childNodes[nr_headers].childNodes[11]) ;
  set(t_column_type, 'Texte libre') ;
  import_column() ;
  popup_set_value('p PP\ni II\nj JJ') ;
  import_column_do() ;
  expected('');
  freeze_column() ;
  table_fill(false, true) ; periodic_work_do() ;

  cell_goto(table.childNodes[nr_headers+3].childNodes[0], true) ;
  if ( the_current_cell.td.innerHTML != 'PP' )
    alert_real('Import problem: ' + the_current_cell.td.innerHTML) ;

  column_delete() ;
  if ( the_current_cell.column.title != default_title + '12' )
    alert_real('Non empty column destroyed') ;

  expected('On%20peut%20seulement%20d%E9truire%20des%20colonnes%20vides.%0A%0AVous%20devez%20donc%20d%27abord%20vider%20la%20colonne%20en%20cliquant%20sur%20%22Remp.%22<hr>');

  if ( the_current_cell.column.the_local_id !== undefined )
    alert_real('Bug local_id') ;

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

  w = print_selection(undefined,1)    ; w.close() ;
  // w = goto_resume()                ; w.close() ;
  w = display_statistics()            ; w.close() ;
  w = my_mailto(students_mails()+'@',true);w.close();
  w = my_mailto(authors_mails()+'@',true) ;w.close();

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

function the_full_login_list(login, results, add)
{
  if ( ! document.getElementById('students_list') )
    {
      // We are in a table, not the home page
      login_list(login, results) ;
    }
  else
    full_login_list(login, results, add) ; // Defined in home2.js
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
