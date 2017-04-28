// -*- coding: utf-8; mode: Java; c-basic-offset: 2; tab-width: 8; -*-
/*
    TOMUSS: The Online Multi User Simple Spreadsheet
    Copyright (C) 2008-2015 Thierry EXCOFFIER, Universite Claude Bernard

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

    Contact: Thierry.EXCOFFIER@univ-lyon1.fr
*/

// Constants
var vertical_scrollbar_width = 17 ;
var horizontal_scrollbar_height = 10 ;
var nr_headers = 2 ;
var bs = '<td>' ;
var maximum_url_length = 3000 ;
var is_a_teacher = false ;
var periodic_work_period = 100 ; // In millisecs
// Work value
var element_focused ;           // If undefined: it is the current_cell
var line_offset ;		// The page being displayed
var column_offset ;
var filters ;			// The filters to apply to the lines
var nr_new_lines ;		// Number of created lines
var nr_new_columns ;		// Number of created columns
var nr_not_empty_lines ;        // Number of non empty lines
var nr_not_fully_empty_lines ;  // Number of non empty lines
var nr_filtered_not_empty_lines ;        // Number of non empty lines
var nr_filtered_not_fully_empty_lines ;  // Number of non empty lines
var sort_columns ;		// Define the sort columns
var table ;			// The table displayed on the screen
var tr_title ;			// The header TR element for 'title'
var tr_filter ;
var i_am_the_teacher ;
var i_am_root ;
var teachers ;
var display_tips ;
var columns_filter ;
var full_filter ;
var line_filter ;
var tr_classname ;		// Column containing the className of the line
var popup_on_red_line ;
var do_not_read_option ;	// Option disabled for virtual tables
var the_current_cell ;
var today ;
var debug_window ;
var mouse_over_old_td ; // To not recompute the tip on each mousemove.
var filtered_lines ;
var table_fill_do_not_focus ;
var table_fill_force_current_cell_update ;
var table_fill_hook ;
var next_page_col ;
var next_page_line ;
var highlight_list ;
var connection_state ;
var auto_save_running ;
var pending_requests, pending_requests_first ;
var scrollbar_right ;
var ask_login_list ;
var first_day ;
var last_day ;
var current_window_width ;
var current_window_height ;
var table_info = [] ; // see middle.js
var last_user_interaction = 0 ; // setted with millisec()
var zebra_step ;
var is_a_virtual_ue ;

// HTML elements
var divtable ;
var author ;
var modification_date ;
var server_log ;
var the_body ;
var nr_filtered_lines ;
var the_comment ;
var linefilter ;
var horizontal_scrollbar ;
var vertical_scrollbar ;
var t_student_picture ;
var t_student_firstname ;
var t_student_surname ;
var t_student_id ;
var t_value ;
var t_history ;
var t_editor ;
var t_date ;
var t_author ;
var t_menutop ;

// Redefined if needed
var root ;
var my_identity ;
var days, days_full, months, months_full, ampms, ampms_full ;
var contains_pm ;
var css_themes = ["", "G", "A", "P", "D", "R", "BW"] ; // In style.css


function lib_init()
{
  divtable             = document.getElementById('divtable'             );
  author               = document.getElementById('author'               );
  modification_date    = document.getElementById('date'                 );
  server_log           = document.getElementById('log'                  );
  the_body             = document.getElementById('body'                 );
  if ( the_body )
    the_body.style.overflowX = 'hidden' ;
  nr_filtered_lines    = document.getElementById('nr_filtered_lines'    );
  the_comment          = document.getElementById('comment'              );
  linefilter           = document.getElementById('linefilter'           );
  horizontal_scrollbar = document.getElementById('horizontal_scrollbar' );
  vertical_scrollbar   = document.getElementById('vertical_scrollbar'   );
  t_student_picture    = document.getElementById('t_student_picture'    );
  t_student_firstname  = document.getElementById('t_student_firstname'  );
  t_student_surname    = document.getElementById('t_student_surname'    );
  t_student_id         = document.getElementById('t_student_id'         );
  t_value              = document.getElementById('t_value'              );
  t_history            = document.getElementById('t_history'            );
  t_editor             = document.getElementById('t_editor'             );
  t_date               = document.getElementById('t_date'               );
  t_author             = document.getElementById('t_author'             );
  t_menutop            = document.getElementById('menutop'              );

  if ( root === undefined )
    root = [] ;
  if ( my_identity === undefined )
    my_identity = 'identity undefined' ;
  try
    {
      is_a_virtual_ue = ue === 'VIRTUALUE' || ue === '' || page_id <= 0 ;
    }
  catch(e)
    {
      is_a_virtual_ue = true ;
    }
  line_offset       = 0    ;// The page being displayed
  column_offset     = 0    ;
  filters           = []   ;// The filters to apply to the lines
  nr_new_lines      = 0    ;// Number of created lines
  nr_new_columns    = 0    ;// Number of created columns
  sort_columns      = []   ;// Define the sort columns
  i_am_the_teacher  = false;
  teachers          = []   ;
  display_tips      = true ;
  highlight_list = [] ;
  columns_filter = compile_filter_generic('') ;
  prst_is_input = true ;
  popup_on_red_line = true ;
  do_not_read_option = false ; // Option disabled for virtual tables
  the_current_cell = new Current() ;
  connection_state = new Connection() ;
  auto_save_running = false ;
  pending_requests = [] ;
  pending_requests_first = 0 ;
  i_am_root |= myindex(root, my_identity) != -1 ;

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

  days = eval(_("MSG_days")) ;
  days_full = eval(_("MSG_days_full")) ;
  months = eval(_("MSG_months")) ;
  months_full = eval(_("MSG_months_full")) ;
  ampms = eval(_("MSG_ampms")) ;
  ampms_full = eval(_("MSG_ampms_full")) ;
  contains_pm = new RegExp('.*(' + ampms[1] + '|' + ampms[1].toLowerCase() + ').*') ;
}


function _d(txt)
{
}

function charsize()
{
  return document.getElementById("charsize").offsetWidth ;
}

function char_per_line()
{
  return window_width() / charsize() ;
}

function compute_nr_cols()
{
  table_attr.nr_columns = Math.floor(char_per_line() / 8.5) ;
  if ( table_attr.nr_columns <= 0 )
    // Needed for 'statistics_per_group' virtual table
    table_attr.nr_columns = 1 ;
}

var header_height ;

function compute_header_height()
{
  if ( table )
    {
      document.body.style.overflow = 'hidden';
      header_height = findPosY(table.childNodes[0].childNodes[0]) ;
      var old = table_attr.nr_lines ;
      compute_nr_lines() ;
      if ( old !== table_attr.nr_lines )
	{
	  table_init() ;
	  table_fill(true,true,true) ;
	}
    }
}

function compute_nr_lines()
{
  if ( ! header_height )
    {
      table_attr.nr_lines = zebra_step + 1 ;
      compute_nr_lines.do_compute_nr_lines = true ;
      periodic_work_add(compute_header_height) ;
      return ;
    }
  if ( ! compute_nr_lines.do_compute_nr_lines)
    return ; // Value set by the preference.
  if ( the_current_cell.input )
    {
      // Number of displayed lines on the screen
      var line_height ;
      try {
	line_height = (table.childNodes[nr_headers+zebra_step].offsetTop
		       - table.childNodes[nr_headers].offsetTop) /zebra_step;
	} catch(e)
	{
	  // The table is too small
	  line_height = (table.childNodes[nr_headers+1].offsetTop
			- table.childNodes[nr_headers].offsetTop)  ;
	} ;
      table_attr.nr_lines = (window_height() - header_height
			     - horizontal_scrollbar.offsetHeight
			     /* XXX Magic number for Chrome/Opera */
			     - 15 // horizontal_scrollbar.offsetHeight ???
			     ) / line_height ;
      table_attr.nr_lines = Math.floor(table_attr.nr_lines) - nr_headers ;
      compute_nr_lines.do_compute_nr_lines = false ;
    }

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
    {
      event = the_event(event) ;
      if ( event === undefined )
	return ;
      td = event.target ;
    }
  if ( td.tagName == 'INPUT' || td.tagName == 'SELECT' || td.tagName == 'IMG'
       || td.tagName == 'A' || td.tagName == 'BUTTON' )
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
    o = decodeURI(o) ;
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

function filter_keyup(event, force)
{
  var e = the_event(event) ;
  if ( force || e.keyCode > 40 || e.keyCode == 8 || e.keyCode == 32 )
    header_change_on_update(e, e.target, '') ;
  GUI.add("column_filter", event);
}

function empty_header(event)
{
  event = the_event(event) ;
  var input = event.target ;

  input.className = input.className.replace(/empty/g,'') ;
  input.onmouseover = mouse_over ;
  input.onkeyup = filter_keyup ;
  input.onblur = filter_unfocus ;
}

function header_focus(t, event)
{
  t = t.parentNode ;
  show_the_tip(t) ;
  the_current_cell.change() ;
  the_current_cell.jump(the_current_cell.lin, col_from_td(t), true) ;
  element_focused = t ;
  empty_header(event) ;
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

function sort_column_update_option()
{
  var s = '' ;
  for(var c in sort_columns)
    if ( sort_columns[c].dir > 0 )
      s += sort_columns[c].data_col + '=' ;
    else
      s += (-sort_columns[c].data_col - 1) + '=' ;
  change_option('sort', s) ;
}


/* The title is clicked */
function sort_column(event, data_col, force)
{
  if ( !force && periodic_work_in_queue(table_fill_do) )
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
	  sort_column_update_option() ;
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
  sort_column_update_option() ;
}

function sort_column_by(data_col, what)
{
  columns[data_col].sort_by = what ;
  hide_the_tip_real(true) ;
  sort_column(undefined, data_col, true) ;
}

function sort_column_menu(event)
{
  var what = ['LABEL_sort_value', 'LABEL_sort_date', 'LABEL_sort_author',
	      'LABEL_sort_comment'] ;
  var data_col=data_col_from_td(the_event(event).target.parentNode.parentNode);
  var column = columns[data_col]
  if ( column.is_computed() )
    what.push('LABEL_sort_%ABJ') ;
  var s = [] ;
  for(i in what)
    {
      i = what[i] ;
      var v = '<li><a style="color:#00F" onmousedown="sort_column_by('
	+ data_col + ",'" + i + '\')">' + _(i) + '</a>' ;
      if ( column.sort_by == i )
	v = '<b>' + v + '</b>' ;
      s.push(v) ;
    }
  show_the_tip(event.target,
	       "<!--INSTANTDISPLAY-->" + _('LABEL_sort_by')
	       + '<ul style="padding-left:1.5em">'
	       + s.join('') + '</ul>') ;
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
      var tip_plus = document.createElement('div') ;
      tip_plus.id = 'tip_plus' ;
      tip_plus.innerHTML = '?' ;
      tip_plus.style.display = "none" ;
      tip_plus.onmousedown = function(event) { thetable.onmousedown(event);} ;
      document.getElementsByTagName('BODY')[0].appendChild(tip_plus) ;
    }
  tip.style.zIndex = 30 ; // Under tableforms

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
  set_element_relative_position(td, tip) ;
}

function header_title_click(t)
{
  if ( data_col_from_td(t.parentNode) === the_current_cell.data_col )
    return ;
  last_user_interaction = millisec() ;
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
  var s, column, h ;
  h = Math.floor(window_height() - header_height) ;
  if ( isNaN(h) )
    h = window_height() ;
  s = '<div style="overflow:auto;max-height:' + h + 'px">'
    + '<table class="colored" style="max-width:'
    + Math.floor(window_width()*0.75) + 'px">'
    + '<tr><th>' + _('TH_column')
    + '</th><th>' + _('TH_value')
    + '</th><th>' + _('TH_rank')
    + '</th><th>' + _('TH_comment')
    + '</th></tr>' ;
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
	    cell.value_fixed().replace(/\n/g,'<br>') + '</td><td>' +
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
  x += '</div>' ;

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
var instant_tip_display ;

function show_the_tip(td, tip_content, what)
{
  if ( body_on_mouse_up_doing )
    return ;

  var bottom = false ;
  var data_col, line_id, column, type, s ;

  if ( td.tagName == 'SPAN' && td.parentNode.tagName == 'TD' )
    td = td.parentNode ; // For the green square on modified cells
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
	  // Tips for the big table columns header: 'title' and 'filter'
	  bottom = true ;
	  while ( td.tagName != 'TH' )
	    {
	      td = td.parentNode ;
	      if ( ! td )
		return ;
	    }
	  s = _(type['tip_' + td.parentNode.className.split(' ')[0]]) ;
	  if ( column.filter_error && td.parentNode.className == 'filter' )
	    {
	      s += '<div class="attribute_error">' + column.filter_error
		+ "</div>" ;
	    }
	  what = td.parentNode.className.split(' ')[0] ;
	  remove_highlight() ;
	  if ( preferences.debug_table )
	    {
	      for(var i in filters)
		s += "<hr>" + filters[i][0] ;
	    }
	}
      else
	{
	  var line = lines[line_id] ;
	  if ( line === undefined )
	    return ;
	  var cell = line[data_col] ;
	  if ( cell.modifiable(line, column) && type.tip_cell )
	    s = '<span class="title">' + _(type.tip_cell) + '</span><br>' ;
	  else
	    s = '' ;
	  if ( data_col === 0 )
	    s += (1+myindex(filtered_lines, line)) + '<br>' ;
	  if ( cell.value )
	    s += '<b>' + html(cell.value).replace(/\n/g,"<br>") + '</b><br>' ;
	  s += cell.get_author() + ' ' + date(cell.date) + '<br>' ;
	  if ( preferences.debug_table )
	    s += 'line_id=' + line_id + ', col_id=' + column.the_id ;
	  // highlight line
	  remove_highlight() ;
	  the_current_line = td.parentNode ;
	  td.parentNode.className += ' highlight_current' ;
	  what = 'cell' ;
	}
      if ( s === '' )
	{
	  tip.style.display = 'none' ;
	  return ;
	}
    }
  else
    {
      var more ;
      switch(td.id)
	{
	case 'linefilter'    : more = line_filter    ; break ;
	case 'columns_filter': more = columns_filter ; break ;
	case 'full_filter'   : more = full_filter    ; break ;
	}
      if ( more && more.errors )
	more = '<div class="attribute_error">' + more.errors + '</div>' ;
      else
	more = "" ;
      s = tip_content + more ;
    }

  if ( ! display_tips )
    return ;

  // Prepare the full tip window (not yet displayed)
  tip.innerHTML = s ;
  tip.display_number++ ;
  var a = tip.display_number ;
  // Hide the tip if the mouse go inside
  tip.onmousemove = function() { hide_the_tip(a); } ;
  tip.tip_target = td ;

  if ( instant_tip_display || s.indexOf("<!--INSTANTDISPLAY-->") != -1 )
    {
      set_tip_position(td, bottom) ;
      tip.style.display = "block" ;
      tip.className = "tip_fade_in" ;
      return ;
    }

  // Display the '?'
  var tip_plus = document.getElementById('tip_plus') ;
  tip.style.display = 'none' ;
  tip_plus.style.display = 'block' ;
  var td2 = tip_top(td) ;
  var pos = findPos(td) ;

  var x = pos[0] - tip_plus.offsetWidth + 1 ;
  if ( x > 10 )
    {
      tip_plus.style.left = x + 'px' ;
      tip_plus.style.top = pos[1] + 'px' ;
    }
  else
    {
      tip_plus.style.left = '0px' ;
      tip_plus.style.top = pos[1]  + 'px' ;
    }

  tip_plus.onmouseover = function() { tip.do_not_hide = true ;
				      if ( tip_content !== undefined )
					tip.tip_target = td ;
				      set_tip_position(td, bottom) ;
				      tip.style.display = "block" ;
				      GUI.add('tip', '', what) ;
  }
  tip_plus.onmouseout = function() {tip.do_not_hide = false ;
				    tip_plus.style.display = "none" ;
				    hide_the_tip_real() ;
				    GUI.add('tip', '', '') ;
  }
  
  return tip ;
}

function on_mouse_down(event)
{
  last_user_interaction = millisec() ;
  var td = the_td(event) ;
  column_from_td(td).real_type.onmousedown(event) ;
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
  if ( element_focused && element_focused.tagName == 'TEXTAREA' )
    return ;
  var e = the_event(event) ;
  if ( e.ctrlKey || e.altKey || e.metaKey || e.shiftKey )
    return ;
  if ( e.wheelDelta < 0 )
    next_page(undefined, zebra_step) ;
  else
    previous_page(undefined, zebra_step) ;

  stop_event(event) ;
}

// Helper functions

function column_parse_attr(attr, value, column, xcolumn_attr)
{
  // xcolumn_attr :
  //    undefined : initialisation in a new column with default values
  //    false     : user interaction
  //    0         : initialisation of the attributes in an existing column 
  //    true      : value received from another user
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
		      // XXX: 0, 1, false and true are all their meanings
		      column_modifiable_attr(attr, column) ? 0 : true
		      ) ;
}

var use_touch = true ;

function table_move(event)
{
  event = the_event(event) ;
  var d = (thetable.start_drag_y - event.y)
    / the_current_cell.input.offsetHeight ;
  line_offset = thetable.start_line_offset + Math.floor(d) ;
  if ( line_offset < 0 )
    line_offset = 0 ;
  
  d = (thetable.start_drag_x - event.x) / the_current_cell.input.offsetWidth;
  column_offset = thetable.start_column_offset + Math.floor(d) ;
  if ( column_offset + table_attr.nr_columns
       > columns.length - nr_new_columns )
    column_offset = columns.length - table_attr.nr_columns - nr_new_columns ;
  if ( column_offset < 0 )
    column_offset = 0 ;
  change_option('column_offset', column_offset ? column_offset : '') ;

  
  if ( thetable.last_column_offset != column_offset
       || thetable.last_line_offset != line_offset )
    table_fill(undefined, thetable.last_column_offset != column_offset,
	       false, true);
  
  thetable.last_column_offset = column_offset ;
  thetable.last_line_offset = line_offset ;
}

function start_table_drag(event)
{
  the_current_cell.change() ;
  event = the_event(event) ;
  if ( event.target.tagName != "TD" )
    return ;
  thetable.start_line_offset = line_offset ;
  thetable.start_column_offset = column_offset ;
  thetable.start_drag_y = event.y ;
  thetable.start_drag_x = event.x ;

  body_on_mouse_up_doing = "table_drag" ;
  set_body_onmouseup() ; // ??? Why not working in HTML TAG
  the_body.onmousemove = table_move ;
  stop_event(event) ;
}

function do_touchstart(event)
{
  do_touchstart.touch_device = true ;
  the_current_cell.change() ;
  event = the_event(event) ;
  thetable.start_line_offset = line_offset ;
  thetable.start_column_offset = column_offset ;
  thetable.start_drag_y = event.y ;
  thetable.start_drag_x = event.x ;
}

function do_touchmove(event)
{
  var e = the_event(event) ;
  if ( e.one_finger )
    {
      table_move(event) ;
      stop_event(event) ;
    }
}



// table innerHTML is not supported by anyone

var colgroup ;

function table_init()
{
  var thetable ;

  if ( table_init.running ) // FireFox multithreaded JS
    return ;
  table_init.running = true ;

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
      vertical_scrollbar.style.top = pos[1] + vertical_scrollbar_width + 'px' ;
      if ( scrollbar_right )
	m = "0px " + sb_width + "px 0em 1px";
      else
	m = "0px 0px 0px " + sb_width + 'px';
      thetable.style.margin = m ;
      thetable.style.width = table_width + 'px' ;
      // Use timeout because of a firefox3 bug...
      setTimeout(function() {thetable.style.width = table_width+'px' ;}, 100) ;
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
  thetable.onmousedown = start_table_drag ;
  if ( use_touch )
    try {
      table.addEventListener("touchstart", do_touchstart, false);
      table.addEventListener("touchmove", do_touchmove, false);
    } catch(e) {} ;

  // Header lines

  tr_title = document.createElement('tr') ;
  tr_title.className = 'column_title' ;
  var th = document.createElement('th') ;
  th.innerHTML = '<div onclick="header_title_click(this);">'
    + '<span>&nbsp;</span>'
    + '<div onclick="header_title_click(this.parentNode);sort_column();GUI.add(\'column_sort\',\'\',the_current_cell.column.title)" onmouseenter="sort_column_menu(event)"></div></div>' ;
  for(var i = 0 ; i < table_attr.nr_columns ; i++ )
    {
      var th2 = th.cloneNode(true) ;
      tr_title.appendChild(th2) ;
      th2.type = tr_title.className ;
    }
  table.appendChild(tr_title) ;

  th.innerHTML = '<INPUT TYPE="TEXT" onfocus="header_focus(this,event)" onblur="element_focused=undefined" oninput="filter_keyup(event, true)">' ;
  tr_filter = document.createElement('tr') ;
  tr_filter.className = 'filter' ;
  for(var i = 0 ; i < table_attr.nr_columns ; i++ )
    {
      var th2 = th.cloneNode(true) ;
      th2.onclick = empty_header ;
      th2.onpaste = header_paste ;
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
	    td.onmousedown = on_mouse_down ;
	  td.onmousemove = mouse_over ;
	}
    }
  table_init.running = false ;
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
      if ( column.real_type.cell_compute === undefined
	   && column.red.indexOf('[') == -1
	   && column.green.indexOf('[') == -1
	   && column.redtext.indexOf('[') == -1
	   && column.greentext.indexOf('[') == -1
	   )
	continue ;
      if ( data_col != data_col2 ) // To not erase green square
	update_cell(tr.childNodes[column.col], line[data_col2], column,
		    undefined, line);
    }
}

function update_cell_at(line_id, data_col)
{
  if ( table === undefined )
    return ;
  var lin = lin_from_line_id(line_id) ;
  if ( lin === undefined )
    return ;
  var col = columns[data_col].col ;
  if ( col === undefined )
    return ;
  var tr = table.childNodes[lin + nr_headers] ;
  update_cell(tr.childNodes[col], lines[line_id][data_col],
	      columns[data_col], undefined, lines[line_id]);
}

/******************************************************************************
Update the header of the table
******************************************************************************/

function set_columns_filter(h)
{
  var cf = document.getElementById('columns_filter') ;
  if ( h === '' )
    cf.className = 'empty' ;
  else
    cf.className = '' ;
  if ( cf.value != h )
    cf.value = h ;
  columns_filter = compile_filter_generic(h) ;
  try {
    columns_filter(undefined, C()) ;
  }
  catch(e) {
    columns_filter = compile_filter_generic('=') ;
    columns_filter.errors = "BUG" ;
  }
  if ( columns_filter.errors )
    cf.className = 'attribute_error' ;
}


function columns_filter_change(v)
{
  if ( columns_filter.filter == v.value )
    return ;

  set_columns_filter(v.value) ;

  column_offset = 0 ;
  table_fill(true, true,true) ;

  change_option('columns_filter', encode_uri_option(columns_filter.filter)) ;
  change_option('column_offset') ;
}

function column_list_full_filter_hide(column, data_col)
{
  if ( column.column_list_full_filter !== undefined )
    return column.column_list_full_filter ;

  column.column_list_full_filter = false ;
  if ( full_filter && !column.is_empty )
    {
      for(var lin in filtered_lines)
	{
	  if ( full_filter(filtered_lines[lin], filtered_lines[lin][data_col]) )
	    return false ;
	}
      column.column_list_full_filter = true ;
      return true ;
    }
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

      if ( (column.freezed == 'F' || column.filter_freeze)
	   && column.hidden != 1 )
	{
	  freezed.push(column) ;
	  continue ;
	}
      if ( column.hidden == 1 )
	continue ;
      var v = C(column.title, column.author, '20080101', column.comment) ;
      if ( ! columns_filter(undefined, v) && !column.is_empty )
	continue ;
      if ( column_list_full_filter_hide(column, data_col) )
	continue ;
      cl.push(column) ;
    }

  freezed.sort(function(a,b) {return a.position - b.position ;}) ;
  cl.sort(function(a,b) {return a.position - b.position ;}) ;

  if ( number_of_cols > freezed.length )
    return freezed.concat(cl.slice(col_offset,
				   col_offset + number_of_cols - freezed.length));
  return freezed ;
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
function set_body_onmouseup()
{
  GUI.add(body_on_mouse_up_doing, '', 'start') ;

  if ( the_body.onmouseupold === undefined )
    the_body.onmouseupold = the_body.onmouseup ;
  the_body.onmouseup = body_on_mouse_up ;

  /* // Does not work for Chrome to detect the cursor moving outside window
  the_body.onmouseout = function(event) {
    if ( event.target.tagName == 'TABLE' )
      {
	the_body.onmouseout = function() {} ;
      	body_on_mouse_up(event) ;
      }
  } ;
  */
  display_tips_saved = display_tips ;
  display_tips = false ;
}

function move_horizontal_scrollbar_begin(event)
{
  if ( element_focused && element_focused.onblur )
      element_focused.onblur() ;
  the_current_cell.focus() ; // Take focus to do the necessary 'blurs'
  var col = the_event(event).target.col ;
  page_horizontal(0, col) ;
  body_on_mouse_up_doing = "horizontal_scrollbar_drag" ;
  set_body_onmouseup() ; // ??? Why not working in HTML TAG
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

  left.style.height = horizontal_scrollbar_height + 2 + 'px' ;
  right.style.height = horizontal_scrollbar_height + 2 + 'px' ;

  left.style.left = dx - horizontal_scrollbar_height + 'px' ;
  right.style.left = dx + hwidth + 'px' ;

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
      a.style.left = a.xcoord + 'px' ;
      a.style.width = (hwidth * cls_all[col].width / width).toFixed(0) + 'px' ;
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
      
      vertical_scrollbar.childNodes[3].style.top = p1.toFixed(0) + 'px' ;
      height = p2 - p1 ;
      if ( height <= 2 )
	height = 2 ;
      vertical_scrollbar.childNodes[3].style.height = height.toFixed(0) + 'px';
      //debug(vertical_scrollbar.childNodes[3].style,undefined,undefined,true);
    }
}

function update_vertical_scrollbar_cursor()
{
    periodic_work_add(update_vertical_scrollbar_cursor_real) ;
}


function update_vertical_scrollbar_position_real()
{
  if ( ! vertical_scrollbar )
    return ;
  var p = vertical_scrollbar.childNodes[0] ;
  var height = filtered_lines.length ;
  if ( height === 0 )
    {
      p.style.top = sb_line_to_pixel(0) + 'px' ;
      p.style.height = sb_height() + 'px' ;
    }
  else
    {
      p.style.top = sb_line_to_pixel(line_offset) + 'px' ;
      p.style.height = sb_line_to_pixel(line_offset + table_attr.nr_lines)
	- sb_line_to_pixel(line_offset) + 'px' ;
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
      GUI.add(body_on_mouse_up_doing, '', 'stop') ;
      var was_doing = body_on_mouse_up_doing ;
      the_body.onmouseup = the_body.onmouseupold ;
      the_body.onmousemove = function() { } ;

      body_on_mouse_up_doing = undefined ;
      if (display_tips_saved !== undefined )
	display_tips = display_tips_saved ;
      if ( was_doing == 'table_drag' )
	{
	  if ( thetable.start_line_offset == line_offset )
	    return false ; // jump of the cursor
	}
      stop_event(the_event(event)) ;
      return true ;
    }
}


function move_vertical_scrollbar_begin(event)
{
  the_current_cell.change() ;
  body_on_mouse_up_doing = "vertical_scrollbar_drag" ;
  set_body_onmouseup() ; // ??? Why not working in HTML TAG
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
  if ( ! vertical_scrollbar )
    return ;

  vertical_scrollbar.onmousedown = move_vertical_scrollbar_begin ;
  vertical_scrollbar.style.height = divtable.offsetHeight + 'px' ;
  vertical_scrollbar.style.width = vertical_scrollbar_width + 'px' ;
  if ( scrollbar_right )
    vertical_scrollbar.style.right = 0 ;
  else
    vertical_scrollbar.style.left = 0 ;

  vertical_scrollbar.style.top = divtable.offsetTop + 'px' ;

  if ( sort_columns.length === 0 )
    return ;

  var last = '' ;
  var data_col = sort_columns[0].data_col ;
  var v, vv, v_upper ;
  var height = filtered_lines.length ;
  var y, last_y = -100 ;
  s = '<span class="position">&nbsp;</span><img src="_FILES_/up.gif" onclick="javascript:previous_page();"><img src="_FILES_/down.gif" onclick="javascript:next_page();"><span class="cursor"></span>' ;


  if ( preferences.v_scrollbar_nr
       && columns[data_col].sort_by == 'LABEL_sort_value' )
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
  vertical_scrollbar.childNodes[1].style.width = vertical_scrollbar_width+"px";
  vertical_scrollbar.childNodes[2].style.width = vertical_scrollbar_width+"px";
  vertical_scrollbar.childNodes[2].style.top = divtable.offsetHeight - vertical_scrollbar_width + 'px' ;

  vertical_scrollbar.childNodes[3].style.width = vertical_scrollbar_width+'px';
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
  var cs = charsize() ;
  for(var col = 0 ; col < table_attr.nr_columns ; col++)
    {
      w = ((window_width()*cls[col].width)/width-8).toFixed(0) ;
      // tr_title.childNodes[col].style.width = width + 'px' ;
      if ( w <= cs )
	w = cs ;
      colgroup.childNodes[col].width = w ;
      colgroup.childNodes[col].className = 'col_id_' + cls[col].the_id ;
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
      if ( column.is_visible() )
	{
	  if ( column.modifiable == 2 )
	    className += ' modifiable_by_student' ;
	  else if ( column.visibility == 3 || column.visibility == 4 )
	    className += ' public_display' ;
	}
      else
	className += ' hidden_to_student' ;

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
      if ( column.filter_error )
	td_filter.childNodes[0].className += ' attribute_error' ;
      if ( column.freezed !== '' )
	td_filter.childNodes[0].className += ' freezed' ;
      
      td_title.className = className ;

      var icon = title.childNodes[1] ;
      icon.innerHTML = "&nbsp;▲" ;
      icon.className = "icon_hidden" ;
      for(var i=0; i<2; i++)
	{
	  if ( column != sort_columns[i] )
	    continue ;
	  var triangle ;
	  if ( i == 0 )
	    {
	      td_title.className += ' sorted' ;
	      triangle = ["▼", "", "▲"] ;
	    }
	  else
	    triangle = ["▽", "", "△"] ;
	  icon.innerHTML = '&nbsp;' + triangle[column.dir+1] ;
	  icon.className = "" ;
	  break ;
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

  if ( filters.length === 0 )
    {
      for(var line in lines)
	{
	  empty = line_empty(lines[line]) ;
	  if ( table_attr.hide_empty && empty )
	    continue ;	    
	  if ( empty !== true )
	    f.push(lines[line]) ;  // Not empty on screen AND history
	}
      return f ;
    }

  for(var line in lines)
    {
      line = lines[line] ;
      var ok = true ;
      for(var filter in filters)
	{
	  filter = filters[filter] ;
	  if ( ! filter[0](line, line[filter[1]], filter[2]) )
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
  if ( (full_filter ? full_filter.filter : "") == value.value )
    return ;

  for(var data_col in columns)
    columns[data_col].column_list_full_filter = undefined ;

  if ( value.value === '' )
    {
      // value.className = 'empty' ;
      full_filter = undefined ;
    }
  else
    {
      value.className = '' ;
      full_filter = compile_filter_generic(value.value) ;
      if ( full_filter.errors )
	value.className = "attribute_error" ;
      else
	value.className = value.className.replace("attribute_error", "") ;

    }
  column_offset = 0 ;
  line_offset = 0 ;
  table_fill(true, true,true) ; 

  change_option('full_filter', encode_uri_option(value.value))
  change_option('column_offset') ;
}


function change_option(option, value)
{
  if ( column_get_option_running )
    return ;
  if ( ! window.history.replaceState )
    return ;
  // Remove ticket
  var loc =  window.location.toString().split("?")[0] ;
  // Remove old option value
  loc = loc.replace(RegExp('/=' + option + '=[^/]*'), '') ;
  // Remove trailing /
  loc = loc.replace(RegExp('/+$'), '') ;
  if ( value )
    loc += '/=' + option + '=' + value ;
  // Replace state because Undo this way has yet to be done
  if ( table_attr.bookmark )
    window.history.replaceState('_a_', '_t_', loc) ;
}


var line_filter_change_value ;

function line_filter_change_real()
{
  var value = line_filter_change_value ;
  if ( ! value )
    return ;
  line_filter_change_value = undefined ;
  var old_value = line_filter ? line_filter.filter : "" ;
  
  if ( old_value == value.value )
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
      if ( line_filter.errors )
	value.className = "attribute_error" ;
      else
	value.className = value.className.replace("attribute_error", "") ;
    }
    
  //  column_offset = 0 ;
  line_offset = 0 ;
  table_fill(true, true,true) ; 
  update_histogram(true) ;

  change_option('line_filter', encode_uri_option(value.value)) ;
}

function line_filter_change(value)
{
  line_filter_change_value = value ;
  periodic_work_add(line_filter_change_real) ;
}

function sort_lines23(a,b)
{
  var c, cc, va, vb ;
  if ( a.empty && ! b.empty )
    return 1 ;
  if ( b.empty && ! a.empty )
    return -1 ;
  for(var c in sort_columns)
    {
      c = sort_columns[c] ;
      cc = c.data_col ;
      va = a[cc]._key ;
      vb = b[cc]._key ;
      if ( va > vb )
	return c.dir ;
      if ( va < vb )
	return -c.dir ;
    }
  return 0 ;
}

function sort_lines3()
{
  var v, cell ;
  for(var i in filtered_lines)
    {
      filtered_lines[i].empty = line_empty(filtered_lines[i]) ;
      for(var c in sort_columns)
	{
	  c = sort_columns[c] ;
	  cell = filtered_lines[i][c.data_col] ;
	  
	  switch(c.sort_by)
	    {
	    case undefined:
	    case 'LABEL_sort_value'  :
	      cell._key = undefined ;
	      v = cell.key(c.empty_is) ;
	      break ;
	    case 'LABEL_sort_author' :
	      v = cell.author.replace(".", "<br>") ;
	      break ;
	    case 'LABEL_sort_date'   :
	      v = cell.date.substr(0,4) + ' '
		+ cell.date.substr(4,2) + ' '
		+ cell.date.substr(6,2) + '<br>'
		+ cell.date.substr(8,2) + ':'
		+ cell.date.substr(10,2) + ':'
		+ cell.date.substr(12) ;
	      break ;
	    case 'LABEL_sort_comment':
	      v = html(cell.comment).replace('\n', '<br>') ;
	      break ;
	    case 'LABEL_sort_%ABJ':
	      var o = {nmbr_filter: function(line, x) { return x.value == abj || x.value == ppn ; }};
	      v = compute_weighted_percent_(c.data_col, filtered_lines[i], o);
	      v = Math.round(1000*v)/10. ;
	      break ;
	    }
	  cell._key = v ;
	}
    }

  filtered_lines.sort(sort_lines23) ;
}

/******************************************************************************
Update the content of the table
******************************************************************************/

var count_empty = {false: 1, 1: 0, true: 0} ;
var count_fully_empty = {false: 1, 1: 1, true: 0} ;

function update_nr_empty(empty_before, empty_after, filtered)
{
  var ne  = count_empty      [empty_after] - count_empty      [empty_before] ;
  var nfe = count_fully_empty[empty_after] - count_fully_empty[empty_before] ;
  nr_not_empty_lines += ne ;
  nr_not_fully_empty_lines += nfe ;

  if ( filtered )
    {
      nr_filtered_not_empty_lines += ne ;
      nr_filtered_not_fully_empty_lines += nfe ;
    }
  if ( ne || nfe )
    periodic_work_add(update_line_counts) ;
}

function update_line_counts()
{
  if ( nr_filtered_lines
       && Number(nr_filtered_lines.innerHTML) != nr_filtered_not_empty_lines )
    {
      var empty = nr_filtered_not_fully_empty_lines
	- nr_filtered_not_empty_lines ;
      nr_filtered_lines.innerHTML = nr_filtered_not_empty_lines
	+ (empty ? " (+" + empty + '∅)' : "") ;
      highlight_add(nr_filtered_lines) ;
    }
  if ( document.getElementById('nr_not_empty_lines') )
    document.getElementById('nr_not_empty_lines').innerHTML
      = nr_not_empty_lines ;
}

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
	    if ( full_filter(line, line[cls[column]] ) )
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
	    if ( line_filter(line, line[cls[column]] ) )
	      {
		f.push(line) ;
		break ;
	      }
	}
      filtered_lines = f ;
    }

  for(var line in lines)
    lines[line].is_filtered = false ;

  nr_filtered_not_empty_lines = 0 ;
  nr_filtered_not_fully_empty_lines = 0 ;
  for(var line in filtered_lines)
    {
      filtered_lines[line].is_filtered = true ;
      switch ( line_empty(filtered_lines[line]) )
	{
	case false: nr_filtered_not_empty_lines++ ;       // Fall thru
	case 1:     nr_filtered_not_fully_empty_lines++ ;
	}
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

  update_line_counts() ;
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
	  td.innerHTML = ' ' ;
	}
      else
	update_cell(td, the_line[data_col], cls[col], abj, the_line) ;
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
    // Do not update while the cell is being edited
    if ( ! the_current_cell.focused || table_fill_force_current_cell_update )
	{
	    the_current_cell.update(table_fill_do_not_focus) ;
	    // Timeout because the cell must be repositionned after
	    // The table column resize in case of horizontal scroll with
	    // variable size columns.
	    setTimeout("the_current_cell.update("+table_fill_do_not_focus+");",
		       periodic_work_period+1) ; // XXX *2 in place of +1 ???
	}
}

function manage_window_resize_event()
{
  if ( do_touchstart.touch_device )
    return true ;
  var width=window_width(), height=window_height() ;
		
  if ( current_window_width != width )
    {
      if ( table_attr.default_nr_columns == 0
	   && get_option('nr_cols', '0') == '0')
	{
	  compute_nr_cols() ;
	}
      update_column_menu() ;
      update_histogram(true) ;
    }
  if ( current_window_height != height )
    {
      if ( preferences.nr_lines == 0 )
	{
	  compute_nr_lines.do_compute_nr_lines = true ;
	  compute_nr_lines() ;
	}
      update_line_menu() ;
    }
  if ( current_window_width != width || current_window_height != height )
    {
      the_current_cell.input.blur() ;
      table_init() ;
      table_fill(false, true, true, true) ;
      current_window_width = width ;
      current_window_height = height ;
    }
  return true ;
}

var display_tips_saved ;

function login_list_ask()
{
  if ( the_current_cell.initial_value != the_current_cell.input.value
       && the_current_cell.input.value.length > 1
       && the_current_cell.input.value != ask_login_list
       && the_current_cell.input.value.toString().search('[.]$') == -1
       )
    {
      ask_login_list = the_current_cell.input.value ;
      login_list(replaceDiacritics(ask_login_list),
		 [['', '', _('loading_logins_before') + ask_login_list
		   + _('loading_logins_after')]]) ;
      var s = document.createElement('script') ;
      s.src = url + '/=' + ticket + '/login_list/'
	+ encode_uri(replaceDiacritics(ask_login_list)) ;
      the_body.appendChild(s) ;
    }
  return true ;
}

var element_focused_saved = false ;

function login_list_hide()
{
  get_tip_element().do_not_hide = false ;
  the_current_cell.blur_disabled = false ;
  hide_the_tip_real() ;
}

function login_list_select(event)
{
  event = the_event(event) ;
  var t = event.target ;
  if ( t.selectedIndex === undefined )
    return ;    
  if ( t.disable_onchange )
    {
      // To ne terminate on change done by a cursor key
      t.disable_onchange = false ;
      return ;
    }
  
  if ( t.options[t.selectedIndex] )
    {
      var s = t.options[t.selectedIndex].value ;
      if ( s !== '' )
	{
	  if ( element_focused_saved )
	    {
	      element_focused_saved.value = s ;
	      element_focused_saved.scrollLeft = 9999 ;
	    }
	  else
	    the_current_cell.input.value = s ;
	}
    }
  ask_login_list = s ;
  login_list_hide() ;
}

function login_list_select_keydown(event)
{
  var event = the_event(event) ;
  if ( event.keyCode == 13 )
    login_list_select(event.real_event);

  event.target.disable_onchange = true ;
  stop_event(event) ;
  return true;
}

function noblur(event)
{
}

function login_list(name, x, current_value)
{
  // x contains:
  //   [ ["id (value)", "firstname", "surname", "grp", "real_value"], ...]
  if ( name != replaceDiacritics(ask_login_list) )
    return ;

  if ( element_focused === get_tip_element().firstChild )
    {
      element_focused = element_focused_saved ;
    }
  
  if ( x.length == 0 )
      x = [['', '', _("ALERT_unknown_user")]] ;
  hide_the_tip_real();

  var nr = Math.floor(table_attr.nr_lines / 2) ;
  if ( x.length < nr )
    nr = x.length ;
  if ( nr < 2 )
    nr = 2 ;
  var s = '<select class="login_list" size="' + nr + '" onmouseover="the_current_cell.blur_disabled = true;" onmouseout="the_current_cell.blur_disabled = false"  onkeydown="login_list_select_keydown(event)" onclick="login_list_select(event)" onblur="login_list_hide()" style="width:100%">' ;

  var w = 0 ;
  for(var i in x)
    if ( x[i][0].length > w )
      w = x[i][0].length ;

  if ( current_value === undefined )
    current_value = x[0][0] ;

  var autoselect ;
  for(var ii in x)
    if ( x[ii][0].substr(0, current_value.length) == current_value )
      {
	autoselect = ii ;
	break ;
      }
  if ( autoselect === undefined )
    for(var ii in x)
      if ( x[ii][0].toLowerCase() == current_value.toLowerCase() )
	{
	  autoselect = ii ;
	  break ;
	}
  if ( autoselect === undefined )
    autoselect = 0 ;

  x.sort(function(a,b) {
      if ( a[0] < b[0] ) return -1 ;
      if ( a[0] > b[0] ) return 1 ;
      if ( a[1] < b[1] ) return -1 ;
      if ( a[1] > b[1] ) return 1 ;
      if ( a[2] < b[2] ) return -1 ;
      if ( a[2] > b[2] ) return 1 ;
      return 0 }) ;

  for(var ii in x)
    {
      var i = x[ii] ;
      var cn = '' ;
      if ( i[3] )
	{
	  cn = i[3].replace(/OU=/g, '') ;
	  cn = cn.split(',') ;
	  cn = cn.slice(1, cn.length-2) ;
	  cn = '<i><small>' + cn.toString() + '</small></i>' ;
	}
      s += '<option value="' + encode_value(i[4] ? i[4] : i[0]) + '"'
	+ (ii == autoselect ? ' selected' : '') + '>'
	+ left_justify(i[0],w).replace('&nbsp;',' ')
	+ '&nbsp;' + i[1] + ' ' + i[2] + ' ' + cn + '</option>' ;
    }
  s += '</select>' ;
  if ( display_tips_saved === undefined )
      display_tips_saved = display_tips ;
  display_tips = true ;
  instant_tip_display = true ;
  document.getElementById('tip_plus').style.display = 'none' ;

  if ( element_focused )
    {
      if ( element_focused.onblur != noblur )
	element_focused.saved_blur = element_focused.onblur ;
      element_focused.onblur = noblur ;
      show_the_tip(element_focused, s) ;
    }
  else
    show_the_tip(the_current_cell.input, s) ;
  instant_tip_display = false ;
  display_tips = false ;
  get_tip_element().onmousemove = function() { } ;
  element_focused_saved = element_focused ;
  element_focused = get_tip_element().firstChild ;
  element_focused.my_selected_index = autoselect ;
  get_tip_element().do_not_hide = true ;
  get_tip_element().style.zIndex = 40 ; // Above tableforms
  element_focused.onchange = login_list_select ; // Here for IE
}

function table_fill(do_not_focus, display_headers, compute_filtered_lines,
		    force_current_cell_update)
{
  if ( table === undefined )
    return ;
  if ( table_forms_element )
    display_headers = false ;
  table_fill_do_not_focus = do_not_focus ;
  table_fill_force_current_cell_update = force_current_cell_update ;
  if ( compute_filtered_lines )
      periodic_work_add(update_filtered_lines) ;
  periodic_work_add(table_fill_do) ;
  if ( display_headers )
    table_header_fill() ;
}

function table_fill_real()
{
  var write = nr_headers ;
  var td ;
  var empty_column = add_empty_columns() ;
  var cls = column_list() ;
  var d1 = millisec() ;
  for(var line=line_offset; line<filtered_lines.length; line++)
    {
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
	  td.innerHTML = " " ; // Unsecable space
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

// true : empty and no history, 1 : empty and an history
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

function column_empty_of_user_cells(column)
{
  var c ;
  for(var i in lines)
    {
      c = lines[i][column] ;
      if ( c.is_not_empty() && c.author !== "*" && c.author !== "" )
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

  var column = Col({the_id:page_id + '_' + nr_new_columns,
		    the_local_id:  nr_new_columns.toString(),
		    data_col: columns.length,
		    is_empty: keep_data === undefined,
		    filter: ""
    }) ;

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

/*****************************************************************************/

function Column(attrs)
{
  for(var attr in attrs)
    this[attr] = attrs[attr] ;
  for(var attr in column_attributes)
    if ( this[attr] === undefined )
      this[attr] = column_attributes[attr].default_value ;
  this.sort_by = 'LABEL_sort_value' ;
  this.table = table_attr ;
}

function Col(attrs)
{
  return new Column(attrs) ;
}

Column.prototype.is_computed = function() {
  return this.real_type.cell_compute !== undefined ;
} ;

Column.prototype.cell_is_modifiable = function() {
  return this.real_type.cell_is_modifiable ;
} ;

Column.prototype.is_visible = function() {
  if ( this.visibility != 0 && this.visibility != 3 && this.visibility != 4 )
    return false ;
  if ( this.title.substr(0,1) == '.' )
    return false ;
  if ( this.visibility_date != '' )
    {
      if ( this.visibility_date > get_date().formate('%Y%m%d') )
	return false ;
    }
  return true ;
} ;

Column.prototype.all_cells_are_empty = function() {
  for(var lin in lines)
    if ( lines[lin][this.data_col].value !== '' )
      return false ;
  return true ;
} ;

Column.prototype.contain_mails = function(allow_multiple) {
  if ( this.all_cells_are_empty() )
    return false ;
  var mail = "[-'_.a-zA-Z0-9]*@[-'_.a-zA-Z0-9]*" ;
  var test = mail ;
  if ( allow_multiple )
    test += "( +" + mail + ")*" ;
  test = RegExp("^( *$|(mailto:)?" + test + ")$") ;
  for(var lin in lines)
    {
      var value = lines[lin][this.data_col].value ;
      if ( ! value.match )
	return false ; // An int
      if ( ! test.exec(value) )
	return false ;
    }
  return true ;
} ;

/*****************************************************************************/

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

function search_column_in_columns(column, title)
{
  if ( column.title == title )
    return column ;
  if ( ! column_modifiable_attr('columns', column) )
    return ;
  for(var i in column.average_columns)
    {
      var c = search_column_in_columns(columns[column.average_columns[i]],
				       title) ;
      if ( c )
	return c ;
    }
}


/******************************************************************************
Cursor movement
******************************************************************************/

function need_to_save_change()
{
  return ! element_focused || element_focused.id != 'linefilter' ;
}


function next_page(next_cell, dy)
{
  if ( need_to_save_change() )
    the_current_cell.change() ;

  if ( filtered_lines !== undefined 
       && line_offset + table_attr.nr_lines > nr_filtered_not_fully_empty_lines + 1 )
    return true;

  if ( dy === undefined )
    dy = Number((table_attr.nr_lines * preferences.page_step).toFixed(0)) ;

  if ( next_cell === true )
    {
      table_fill_hook = function() {
	cell_goto(table.childNodes[nr_headers+table_attr.nr_lines-dy-preferences.one_line_more].childNodes[the_current_cell.col]) ;
      } ;
    }

  line_offset += dy ;
  
  table_fill(true) ;
  return true ;
}

function previous_page(previous_cell, dy)
{
  if ( need_to_save_change() )
    the_current_cell.change() ;
  if ( dy === undefined )
    dy = Number((table_attr.nr_lines * preferences.page_step).toFixed(0)) ;
  if ( previous_cell === true )
    {
      table_fill_hook = function() {
	cell_goto(table.childNodes[nr_headers+dy-1+preferences.one_line_more].childNodes[the_current_cell.col]) ; } ;
    }
  line_offset -= dy ;
  if ( line_offset < 0 )
    line_offset = 0 ;
  table_fill(true) ;
  return true ;
}

function first_page()
{
  if ( need_to_save_change() )
    the_current_cell.change() ;
  line_offset = 0 ;
  the_current_cell.lin = nr_headers ;
  table_fill(false) ;
  return true ;
}

function last_page()
{
  if ( need_to_save_change() )
    the_current_cell.change() ;
  var nr_lines = Math.min(nr_filtered_not_fully_empty_lines, filtered_lines.length) ;
  line_offset = nr_lines - table_attr.nr_lines + 1 ;
  if ( line_offset < 0 )
    {
      line_offset = 0 ;
      the_current_cell.lin = nr_lines + nr_headers - 1 ;
    }
  else
    {
      the_current_cell.lin = table_attr.nr_lines - 1 ;
    }
  table_fill(false) ;
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
 * Autofreeze columns with a filter
 */
function autofreeze()
{
  if ( preferences.filter_freezed )
    {
      for(var data_col in columns)
	{
	  var column = columns[data_col] ;
	  if ( column.filter !== '' && column.filter !== undefined )
	      column.filter_freeze = true ;
	  else
	      column.filter_freeze = false ;
	}
    }
}
/*
 * If 'col' is defined : then it is the required column (centered)
 * Else 'direction' is a delta
 */
function page_horizontal(direction, col, do_not_focus)
{
  var cls = column_list_all() ;
  if ( column_offset + direction >= cls.length )
    return ;
  if ( ! do_not_focus )
    the_current_cell.change() ;

  autofreeze() ;
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

  table_fill_hook = table_fill_hook_horizontal ;
  table_fill(do_not_focus, true, false, true) ;

  periodic_work_do() ;

  change_option('column_offset', column_offset ? column_offset : '') ;

}

function next_page_horizontal(full_page)
{
  var n = table_attr.nr_columns - nr_freezed() ;
  page_horizontal( full_page ? n : Math.floor(n / 2)) ;
}

function previous_page_horizontal(full_page)
{
  var n = table_attr.nr_columns - nr_freezed() ;
  page_horizontal( full_page ? -n : -Math.floor(n / 2)) ;
}


/******************************************************************************
Cursor movement
******************************************************************************/

function cell_get_value_real(line_id, data_col)
{
  return columns[data_col].real_type.formatte(lines[line_id][data_col].value,
					      columns[data_col]);
}

function cell_class(column, line, cell)
{
  var className = '' ;

  if ( column.color_green_filter(line, cell) )
    className += ' color_green' ;
  if ( column.color_red_filter(line, cell) )
    className += ' color_red' ;  
  if ( column.color_greentext_filter(line, cell) )
    className += ' greentext' ;
  if ( column.color_redtext_filter(line, cell) )
    className += ' redtext' ;
  return className ;
}

function there_is_an_abj(cell, column, abj)
{
  if ( ! abj || abj[0].length == 0 )
    return ;
  if ( column.parsed_course_dates )
    {
      var t, first, last ;
      for(var a in abj[0])
	{
	  a = abj[0][a] ;
	  if ( ! abj_is_fine(a) )
	    continue ;
	  first = parse_date(a[0]).getTime() ;
	  last = parse_date(a[1]).getTime() ;
	  for(var date in column.parsed_course_dates)
	    {
	      t = column.parsed_course_dates[date] ;
	      if ( t >= first && t <= last )
		return 'is_not_an_abi' ;
	    }
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
	    return 'is_an_abj' ;
	}
    }
}


function update_cell(td, cell, column, abj_list, line)
{
  var v = cell.value ;
  var className = cell_class(column, line, cell) ;
  if ( className.indexOf('text') == -1 )
    if ( cell.is_mine() && column.real_type.cell_is_modifiable )
      className += ' rw' ;
    else
      className += ' ro' ;
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
  if ( full_filter && full_filter(line, cell) )
    className += ' filtered' ;
  else if ( line_filter && line_filter(line, cell) )
    className += ' filtered' ;

  // XXX : This does not work if there are no courses dates
  // because the ABJ modify the ABI date
  if ( v === abj && column.parsed_course_dates )
    {
      var c = there_is_an_abj(cell, column, abj_list) ;
      if ( ! c )
	className = className.replace(' default','') + ' is_not_an_abj' ;
    }
  if ( v === abi && column.parsed_course_dates)
    {
      var c = there_is_an_abj(cell, column, abj_list) ;
      if ( c )
	className = className.replace(' default','') + ' ' + c ;
    }
  td.className = className ;
  while( td.childNodes[1] )
    td.removeChild(td.childNodes[0]) ; // Remove feedback square

  if ( column.sort_by != 'LABEL_sort_value' && cell._key !== undefined )
    {
      var vv = document.createElement('SPAN') ;
      vv.className = "sorted_value" ;
      if ( cell.value.toFixed )
	{
	  vv.style.left = '0px' ;
	  vv.style.textAlign = 'left' ;
	}
      else
	{
	  vv.style.right = '0px' ;
	  vv.style.textAlign = 'right' ;
	}
      vv.innerHTML = cell._key ;
      td.insertBefore(vv, td.firstChild) ;
    }

  if ( v === '' )
    td.lastChild.nodeValue = ' ' ; // If empty : zebra are not displayed
  else
    td.lastChild.nodeValue = v.toString() ;

  return v ;
}

function column_change_allowed_text(column)
{
  if ( ! table_attr.modifiable )
    return _("ERROR_table_read_only") ;
  if ( column.title === '' )
    return true ;
  if ( column.author == '*' )
    return _("ERROR_column_system_defined") ;
  if ( column.author == my_identity )
    return true ;
  if ( column.author == '' )
    return true ;
  if ( i_am_the_teacher )
    return true ;
  if ( myindex(minors, column.author) != -1 )
    return true ;
  return _("ERROR_value_defined_by_another_user") ;
}

function column_change_allowed(column)
{
  return column_change_allowed_text(column) === true ;
}

// Indicate that 'line_id' will be filled
function add_a_new_line(line_id, hide_if_created)
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

  if ( hide_if_created && (filters.length !== 0 || full_filter || line_filter))
    return ;
  
  filtered_lines.push(line) ;
  line.is_filtered = true ;

  /* Update screen table with the new id */
  var lin = filtered_lines.length - 1 - line_offset ;
  if ( lin >= 0 && lin < table_attr.nr_lines )
    {
      line_fill(filtered_lines.length-1, lin + nr_headers) ;
    }
  update_vertical_scrollbar() ;
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

// self is not included in the returned lines
function lines_of_the_group(column, line_id)
{
  var g = [] ;
  if ( column.groupcolumn === '' )
    return g ;
  var col = data_col_from_col_title(column.groupcolumn) ;
  if ( ! col )
    return g ;
  var group = lines[line_id][col].value.toString() ;
  if ( group !== '' )
    for (var line_key in lines)
      {
	if ( line_key == line_id )
	  continue ; // Itself
	if ( lines[line_key][col].value.toString() === group )
	  g.push(lines[line_key]) ;
      }
  return g ;
}

function cell_set_value_real(line_id, data_col, value, td)
{
  var cell = lines[line_id][data_col] ;
  var column = columns[data_col] ;

  if ( ! modification_allowed_on_this_line(line_id, data_col, value) )
    {
      GUI.add("cell_change_error", undefined, "not_allowed") ;
      return ;
    }

  // toString is used because '' != '0' and '00' != '000'
  // === is not used because 5.1 == "5.1"
  if ( value.toString() == lines[line_id][data_col].value.toString() )
    return ;

  if ( ! cell.modifiable(lines[line_id], column) )
    return ;

  if ( column.is_empty && columns_filter.filter !== '' )
    {
      Alert("ERROR_column_creation") ;
      return;
    }
  if ( column.is_empty && column.data_col > 0
       && columns[column.data_col-1].is_empty )
      alert_append(_("ERROR_column_left_to_right")) ;

  var orig_value = value ;
  value = column.real_type.cell_test(value, column);
  if ( value === undefined )
    {
      if ( ! column.is_empty )
	return ;
      if ( ! confirm(_("ALERT_to_text")) )
	return ;
      column_attr_set(column, "type", "Text", undefined, true) ;
      the_current_cell.do_update_column_headers = true ;
      return cell_set_value_real(line_id, data_col, orig_value, td) ;
    }

  // Used as a group column
  for(var i in columns)
    if ( columns[i].groupcolumn == column.title && column.title !== '' )
      {
	var e = [], quoi ;
	var group = lines[line_id][column.data_col].value.toString() ;
	var value_group = lines[line_id][columns[i].data_col].value ;
	for (var line_key in lines)
	  {
	    if ( line_key == line_id )
	      continue ;
	    quoi = '' ;
	    if ( lines[line_key][columns[i].data_col].value !== ''
		 && group !== ''
		 && lines[line_key][column.data_col].value.toString()
		 == group )
	      quoi = '-' ;
	    if ( lines[line_key][columns[i].data_col].value !== ''
		 && lines[line_key][columns[i].data_col].value !== value_group
		 && value !== ''
		 && lines[line_key][column.data_col].value.toString()
		 == value.toString() )
	      quoi = '+' ;
	    if ( quoi )
	      e.push(_('MSG_columngroup' + quoi)
		     + ' ' + lines[line_key][0].value + ' '
		     + lines[line_key][1].value + ' '
		     + lines[line_key][2].value + ' '
		     + columns[i].title
		     + (quoi == '+' ?
			' : ' + lines[line_key][columns[i].data_col].value
			+ '≠' + value_group : '')
		     + '\n') ;
	  }
	if ( e.length )
	  {
	    e.sort() ;
	    alert_append(_("ALERT_columngroup_change") + '\n\n'
			 + lines[line_id][column.data_col].value
			 + '→'
			 + value + '\n\n'
			 + e.join(""));
	  }
      }

  create_column(columns[data_col]) ;
  add_a_new_line(line_id) ;
  var empty_before = line_empty(lines[line_id]) ;
  cell.set_value(value) ;
  update_nr_empty(empty_before, line_empty(lines[line_id]),
		  lines[line_id].is_filtered) ;

  var v ;
  if ( td !== undefined )
    v = update_cell(td, cell, column, undefined, lines[line_id]) ;

  /* Create cell */
  append_image(td, 'cell_change/' + column.the_id + '/' +
	       line_id + "/" + encode_uri(cell.value)
	       );

  if ( value !== '' )
    column.is_empty = false ;

  update_histogram(true) ; // XXX

  var g = lines_of_the_group(column, line_id) ;
  if ( g.length )
    {
      for (var line in g)
	{
	  line = g[line] ;
	  var cell = line[column.data_col] ;
	  cell.set_value(value) ;
	  td = td_from_line_id_data_col(line.line_id, column.data_col) ;
	  if ( td !== undefined )
	    update_cell(td, cell, column, undefined, line) ;
	}
    }  
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
      s += '<TR><TH COLSPAN="4">' + _("TH_ABJ_list") + '</TH></TR>' ;
      s += '<TR><TH>' + _('TH_begin')
	+ '</TH><TH>' + _('TH_end')
	+ '</TH><TH>' + _('TH_length') + '</TH><TH></TH></TR>' ;
      for(var abj in abjs)
        {
	  if ( abjs[abj][2].substr(0,13) == '{{{MESSAGE}}}' )
	    {
	      s += '<TD COLSPAN="4">' + nice_date(abjs[abj][0])
		+ ' <span style="background: #F00; color: #FFF">'
		+ html(abjs[abj][2].replace('{{{MESSAGE}}}', ''))
		+ '</span>'
		;
	      continue ;
	    }
	  s += '<TR>' ;
          var d = (0.5 + (parse_date(abjs[abj][1]).getTime()
			  - parse_date(abjs[abj][0]).getTime())/(1000*86400)) ;
	  var x = new RegExp('[' + ampms[0] + ampms[1] + ']') ;
	  if ( d == 0.5 )
	    s += '<TD COLSPAN="2">' + nice_date(abjs[abj][0]) ;
	  else if ( abjs[abj][0].replace(x,'')
		    == abjs[abj][1].replace(x,'') )
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
	      s += '<p class="da">' + _("MSG_DA") + ' ' + das[da][1] + ' <em>'
		+ html(das[da][2]).replace(/\n/g,'<br>') + '</em></p>' ;
	      break ;
	    }
        }
    }
  if ( abjs_da[2] )
    s += '<p class="tierstemps"><b>' + _('MSG_TT')
      + '</b> :<br>' + html(abjs_da[2]).replace(/\n/g, '<br>') ;

  return s ;
}

function set_element_relative_position(anchor, element)
{
  while ( anchor.offsetHeight === undefined  // Firefox bug on SVG histogram
	  || anchor.tagName == 'B'
	  )
    anchor = anchor.parentNode ;

  var pos = findPos(anchor) ;
  
  var element_width = Math.max(element.offsetWidth, 200) ;
  if ( pos[1] > scrollTop() + window_height()/2 )
    {
      element.style.bottom = window_height() - pos[1] + 'px' ;
      element.style.top = 'auto' ;
    } 
  else
    {
      element.style.top = pos[1] + anchor.offsetHeight + 'px' ;
      element.style.bottom = 'auto' ;
    }

  if ( pos[0] > scrollLeft() + window_width()/2 )
    {
      element.style.right = Math.max(window_width()-(pos[0]+anchor.offsetWidth),
				     0) + 'px' ;
      element.style.left = 'auto' ;
    }
  else
    {
      element.style.left = pos[0] + 'px' ;
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
	.replace(/ *highlight8/, '')
	.replace(/ *highlight7/, ' highlight8')
	.replace(/ *highlight6/, ' highlight7')
	.replace(/ *highlight5/, ' highlight6')
	.replace(/ *highlight4/, ' highlight5')
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
    e.innerHTML = html(value).replace(/\n/g, '<br>') ;
  else
    e.innerHTML = value ;

  var tip = get_tip_element() ;
  if ( tip && tip.tip_target === o )
    {
      show_the_tip(o, compute_tip(o)) ;
    }
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

  var v = html(value.toString()) + '&nbsp;' ;
  if ( o.innerHTML != v )
    {
      highlight_add(o) ;
      if ( o.tagName != 'INPUT' )
	{
	  o.innerHTML = v ;
	  update_tip_from_value(o, value.toString()) ;
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

function Connection()
{
  this.start_time = millisec() ;
  this.server_feedback = document.getElementById('server_feedback');
  this.server_answer   = document.getElementById('server_answer') ;
  this.t_authenticate  = document.getElementById('authenticate');
  this.connection_state= document.getElementById('connection_state') ;
  if ( ! this.server_feedback )
    return ; // Home page
  this.server_alive() ; // update last_server_answer because it is alive
  this.last_reconnect = millisec() ;
  this.last_server_check = millisec() ;
  this.server_start_time = 0 ;
  this.connection_open = false ; // false or undefined(checking)
  // Time before TOMUSS is fully started or take to answer under heavy load
  this.tomuss_boot_time = 5000 ;
}
Connection.prototype.time = function(v)
{
  return ((v - this.start_time)/1000).toFixed(1) ;
} ;

Connection.prototype.debug = function(txt)
{
  if ( false )
    console.log(
		[
   '====' + txt + '====',
   'now=' + this.time(millisec())
   + " need_connection:" + this.need_connection()
   + " is_server_alive()= " + this.is_server_alive(),
   ' server_start_time=' + this.time(this.server_start_time)
   + " connection_open= " + this.connection_open
   + " "
   + (pending_requests ? pending_requests_first + '/' + pending_requests.length
      : ''),
   "last_reconnect= " + this.time(this.last_reconnect)
   + " last_server_check= " + this.time(this.last_server_check),
   "last_server_answer= " + this.time(this.last_server_answer)
   + " time_check_interval= " + this.time_check_interval
   ].join("\n")) ;
} ;

Connection.prototype.server_alive = function(what)
{
  if ( this.server_start_time == 0 )
    this.server_start_time = millisec() ;
  this.last_server_answer = millisec() ;
  this.server_feedback.innerHTML = '' ;
  if ( what === undefined )
    what = "server_alive" ;
  this.debug(what) ;
} ;

Connection.prototype.is_server_alive = function()
{
  if ( this.connection_open )
    return true ;
  if ( millisec() - this.last_server_answer < 1000 )
    return true ;
} ;

Connection.prototype.check_if_server_is_alive = function()
{
  if ( millisec() - this.last_server_check < this.time_check_interval )
    return ;
  this.last_server_check = millisec() ;
  if ( ! this.server_feedback )
    return ;
  this.server_feedback.innerHTML = '<img src="' + url + '/status/' + millisec()
  + '" width="8" height="8" onload="connection_state.server_alive();">' ;
  this.debug("check_if_server_is_alive") ;
}

Connection.prototype.connection_alive = function(message)
{
  var before = this.connection_open ;
  this.connection_open = true ;
  this.revalidate_on_screen = false ;
  if ( this.connection_state )
    this.connection_state.innerHTML = _('MSG_connected') ;
  this.t_authenticate.style.display = 'none' ;
  this.time_check_interval = this.tomuss_boot_time ;
  this.server_alive(message) ;
  if ( before === false || before === undefined )
    {
      if ( pending_requests )
	{
	  auto_save_errors() ; // Ask now that the server restarted
	}
    }
} ;

Connection.prototype.increase_time_check_interval = function()
{
  this.time_check_interval = Math.min(this.time_check_interval * 1.1, 30000) ;
} ;

Connection.prototype.broken_connection = function()
{
  this.increase_time_check_interval() ;
  if ( ! this.connection_open )
    return ;
  if ( millisec() < this.last_server_answer + this.tomuss_boot_time )
    return ; // The server may take some time to answer
  if ( millisec() < this.last_reconnect + this.tomuss_boot_time )
    return ; // Just reconnected, so wait a little longer

  this.server_start_time = 0 ;
  this.connection_open = false ;
  this.connection_state.innerHTML = _('MSG_unconnected');
  this.check_if_server_is_alive() ;
  this.debug("broken_connection") ;
} ;

Connection.prototype.close_connection = function()
{
  if ( ! this.connection_open )
    return ;
  if ( pending_requests.length != pending_requests_first )
    return ; // do not close if data is being sent
  this.server_start_time = 0 ;
  this.connection_open = 0 ;
  if ( this.xmlhttp )
    {
      this.xmlhttp.abort() ;
      this.xmlhttp = undefined ;
    }
  this.connection_state.innerHTML += '...' ;
  this.debug("close_connection") ;
} ;

Connection.prototype.click_to_revalidate_ticket = function()
{
  if ( millisec() - this.server_start_time < this.tomuss_boot_time )
    return ;
  if ( ! this.is_server_alive() )
    {
      this.check_if_server_is_alive() ;
      return ;
    }
  if ( this.server_start_time === 0 )
    return ;
  var validate = url + '/allow/' + ticket + '/' + millisec() ;
  if ( authenticate_iframe )
    this.t_authenticate.src = validate ;
  else
    {
      this.t_authenticate.innerHTML =
	"<h2>" + _("MSG_session_expired") + "</h2>"
	+ _("MSG_session_reconnect")
	+ ' <a href="' + validate + '" target="_blank">'
	+ _("MSG_session_link") + '</a>' ;
      this.t_authenticate.style.width = "80%" ;
      this.t_authenticate.style.height = "80%" ;
      this.t_authenticate.style.top = "10%" ;
      this.t_authenticate.style.left = "10%" ;
      var c = this ;
      this.t_authenticate.onmouseup = function() {
	c.t_authenticate.style.width = c.t_authenticate.style.height = "auto" ;
	c.t_authenticate.style.top = c.t_authenticate.style.left = "0px" ;
	c.time_check_interval = 100 ;
	} ;
    }
  this.t_authenticate.style.display = 'block' ;
  this.connection_state.innerHTML= _('MSG_unconnected') ;
  this.revalidate_on_screen = true ;
  this.time_check_interval = this.tomuss_boot_time ;
  this.debug("click_to_revalidate_ticket") ;
} ;

function click_to_revalidate_ticket()
{
  connection_state.click_to_revalidate_ticket() ;
}

Connection.prototype.need_connection = function(force)
{
  if ( this.connection_open )
    return ;
  if ( ! this.server_answer )
    return ;
  if ( is_a_virtual_ue )
    return ;
  if ( check_down_connections_interval === 0 )
    return ;
  if ( !force && millisec() - this.last_reconnect < this.time_check_interval )
    return ;
  return true ;
} ;

Connection.prototype.reconnect_real = function()
{
  if ( ! this.server_answer || is_a_virtual_ue )
    return ;

  var connection = url + "/=" + ticket + '/' + year
    + '/' + semester + '/' + ue + '/' + page_id + '/' + pending_requests_first
    + '.' + page_index + '.' + table_creation_date ;

  if ( window.XMLHttpRequest )
    {
      if ( this.xmlhttp )
	this.xmlhttp.abort() ;
      this.xmlhttp = new XMLHttpRequest();
      this.xmlhttp.nb_read = 0 ;
      this.xmlhttp.js_buffer = '' ;
      // Remove things that are not JavaScript and 'var' definition
      // used in the IFRAME case
      this.xmlhttp.clean_js = new RegExp("^var ", "g") ;
      this.xmlhttp.open("GET", connection, true) ;
      this.xmlhttp.setRequestHeader("If-Modified-Since",
				    "Thu, 1 Jan 1970 00:00:00 GMT") ;
      this.xmlhttp.setRequestHeader("Cache-Control", "no-cache") ;

      // Must be defined last: resetted by .open()
      this.xmlhttp.onreadystatechange = function()
	{
	  if (this.readyState >= 3 && this.status == 200)
	    {
	      var t ;
	      t = this.responseText.substr(this.nb_read) ;
	      this.js_buffer += t ;
	      this.nb_read += t.length ;
	      // Evaluate only complete <script>....</script> sequence
	      t = this.js_buffer.split("</script>");
	      var to_eval = '' ;
	      for(var i in t)
		{
		  if ( i != t.length - 1 )
		    to_eval += t[i].split('<script>')[1] + ';' ;
		  else
		    this.js_buffer = t[i] ;
		}
	      eval(to_eval.replace(this.clean_js, '//')) ;
	      // If the buffer is really too big: create a new one
	      if ( this.nb_read > 100000000 )
		{
		  this.abort() ;
		  this.nb_read = 0 ;
		  this.open("GET", connection, true) ;
		  this.send() ;
		}
	    }
	} ;
      this.xmlhttp.send() ;
    }
  else
      this.server_answer.src = connection ;
}

Connection.prototype.reconnect = function(force)
{
  if ( ! this.need_connection(force) )
    return ;
  if ( ! this.is_server_alive() )
    {
      this.check_if_server_is_alive() ;
      return ;
    }
  if ( this.connection_open === undefined && !this.revalidate_on_screen )
    {
      this.click_to_revalidate_ticket() ;
      return ;
    }
  // Request without answer must have been lost, resent them without waiting
  for(var ii=pending_requests_first; ii < pending_requests.length; ii++)
    pending_requests[ii].requested = false ;

  this.reconnect_real() ;
  this.connection_open = undefined ;
  this.last_reconnect = millisec() ;
  this.debug("reconnect(" +  pending_requests_first + ')') ;
} ;

function server_answered(t)
{
  connection_state.connection_alive("server_answered(" + t + ')') ;

  if ( t === undefined )
    return ;

  if ( t.request.saved )
    return ;

  if ( t.complete !== undefined && ! t.complete )
    return ; // Error loading image
  if ( t.naturalWidth === 0 )
    return ; // Not an image

  saved(t.request.request_id) ;
}

// XXX Does not work if there is 2 browser page open in the table.
function store_unsaved()
{
  if ( ! table_attr.autosave )
    return ;
  auto_save_errors() ; // Cleanup pending_requests list
  if ( ! localStorage )
    {
      Alert("ERROR_save_to_localstorage_failed") ;
      return ;
    }
  var s = [] ;
  for(var i=pending_requests_first; i < pending_requests.length; i++)
    s.push(pending_requests[i].content) ;
  if ( s.length == 0 )
    return ;
  var key = '/' + year + '/' + semester + '/' + ue ;
  if ( localStorage[key] )
    localStorage[key] += '\n' + s.join('\n') ;
  else
    {
      localStorage[key] = s.join('\n') ;
      index = localStorage['index'] ;
      if ( ! index )
	index = '' ;
      index += '\n' + key ;
      localStorage['index'] = index ;
    }
}

var do_reload_when_all_saved = false ;

function restore_unsaved_forgot()
{
  localStorage['/' + year + '/' + semester + '/' + ue] = '' ;
  index = localStorage['index'] ;
  localStorage['index'] = index.replace(RegExp('\n/'+year+'/'+semester+'/'+ue,
					       'g'), '') ;
  popup_close() ;
}

function restore_unsaved_do_save()
{
  for(var i in restore_unsaved.t_splited)
    pending_requests.push(new Request(restore_unsaved.t_splited[i])) ;
  periodic_work_add(auto_save_errors) ;
  do_reload_when_all_saved = true ;
  if ( GUI )
    {
      GUI.add('restore_unsaved', '', 'save') ;
      GUI.save() ;
    }
  create_popup('import_div', _('MSG_currently_saving'), '', '', false) ;
}

function restore_unsaved()
{
  if ( GUI )
    GUI.add('restore_unsaved', '', 'localStorage=' + !!localStorage) ;
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
	  line[3] = decode_uri(line[3]) ;
	  if ( data_col !== undefined && lines[line_id] !== undefined )
	    {
	      if ( lines[line_id][data_col].value == line[3] )
		continue ; // Unchanged value
	      message += '<tr><td>' + html(lines[line_id][0].value)
		+ '<td>' + html(lines[line_id][1].value
				+ ' ' + lines[line_id][2].value) 
		+ '<td>' + html(columns[data_col].title)
		+ '<td>' + html(line[3]) + '</tr>' ;
	      continue ;
	    }
	}
      message += '<tr><td colspan="4">' + html(decodeURI(t_splited[i]))
	+ '</tr>' ;
    }
  if ( message == '' )
    {
      restore_unsaved_forgot() ;
      return ;
    }
  restore_unsaved.t_splited = t_splited ;
  create_popup('restoring_data', _('ASK_restore'),
	       '',
	       '<div style="height:10.5em;overflow:auto;">'
	       + '<table class="colored"><tr><th>'
	       + _('COL_TITLE_ID')
	       + '<th>' + _('COL_TITLE_firstname')
	       + ' ' +  _('COL_TITLE_surname')
	       + '<th>' + _('TH_column')
	       + '<th>' + _('TH_unsaved_value')
	       + '</tr>'
	       + message + '</table></div>'
	       + '<button onclick="restore_unsaved_forgot()">'
	       + _('B_unsaved_forgot') + '</button> '
	       + '<button onclick="restore_unsaved_do_save()">'
	       + _('B_unsaved_save') + '</button> '
	       + '<button onclick="popup_close()">'
	       + _('B_unsaved_cancel') + '</button>',
	       false) ;
}

function Request(content)
{
  this.content = content ;
  this.request_id = pending_requests.length ;
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
      this.image_pending.alt = _("MSG_not_yet_saved") ;
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

/*
 ****************************************************************************
 * Management of periodic work.
 * Once added, the function is called every 0.1 seconds until it returns false
 * 'add' can be called from a periodic function, in this case the function
 * may be called more than one in a period.
 * When a function is added to the list, it goes to the end,
 * so it is processed after the others.
 * The same function can not be added twice
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

function periodic_work_in_queue(f) // The function is in the queue
{
    return myindex(periodic_work_functions, f) != -1 ;
}

function periodic_work_add(f)
{
    periodic_work_add_once(periodic_work_functions, f) ;
    if ( periodic_work_id === undefined )
	periodic_work_id = setInterval(periodic_work_do,
				       periodic_work_period) ;
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
}

var max_socket_open = 5 ;

// **********************************************************
// Restart image loading if the connection was not successul
// **********************************************************

function auto_save_errors()
{
  var errors = 0 ;
  var i ;
  // Problem if the server is slow to answer
  // In millisecond
  var max_answer_time = 10000 ;

  if ( auto_save_running || ! table_attr.autosave )
    return true ;

  auto_save_running = true ;
  connection_state.reconnect() ;
  /* If sending image is not done, then alive connection is not detected
     So these lines must not be added :
  if ( connection_state.connection_open === false )
    return ;
  */
  var d = millisec() ;
  var nr_unsaved = 0 ;

  for(var ii=pending_requests_first; ii < pending_requests.length; ii++)
    {
      i = pending_requests[ii] ;
      if ( i.saved )
	{
	  if ( ii == pending_requests_first )
	    pending_requests_first++ ;
	  continue ;
	}
      nr_unsaved++ ;
      // Some browsers don't like many connections
      if ( nr_unsaved > max_socket_open )
	break ;
      // Retry to load the image each N seconds and the first time
      if ( d > i.time + connection_state.time_check_interval || ! i.requested )
	{
	  if ( i.requested )
	    errors++ ; // Because it is requested again
	  i.send() ;
	  connection_state.debug("send(" + ii + ",errors=" + errors + ')') ;
	}
    }
  var saving = document.getElementById('saving') ;
  if ( saving )
    {
      if ( nr_unsaved > max_socket_open )
	document.getElementById('saving').style.display = 'block' ;
      if ( nr_unsaved == 0 )
	document.getElementById('saving').style.display = 'none' ;
    }

  if ( do_reload_when_all_saved && nr_unsaved == 0 )
    {
      restore_unsaved_forgot() ;
      window.location = window.location ;
      do_reload_when_all_saved = false ;
    }

  if ( errors )
    connection_state.broken_connection() ;
  auto_save_running = false ;

  if ( pending_requests.length != pending_requests_first )
      return true ; // Continue
}

// Remove green images
// The function is called :
//    * On feedback image load
//    * On pending image load
//    * When the server answer by the normal connection (page_answer).
function saved(r)
{
  connection_state.connection_alive("saved(" + r + ')') ;
  if ( pending_requests[r].saved )
    return ;
  pending_requests[r].saved = true ;
  server_log.removeChild(pending_requests[r].image_pending) ;
}

function connected()
{
  connection_state.connection_alive("connected()") ;
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
  if ( is_a_virtual_ue )
    return ;
  if ( text.length > maximum_url_length )
    {
      Alert("ALERT_column_not_saved") ;
      return ;
    }
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
	    child.style.width = width + 'px' ;
	}

      s = url_base() ;
      request.image = s.childNodes[0] ;
      request.image.request = request ;
      td.insertBefore(s, td.lastChild) ;
    }
}

function login_to_line_id(login)
{
  if ( login_to_line_id.dict === undefined )
    {
      login_to_line_id.dict = {} ;
      for(var line_id in lines)
	login_to_line_id.dict[login_to_id(lines[line_id][0].value)] = line_id ;
    }
  return login_to_line_id.dict[login_to_id(login)] ;
}


/* Communication from the server */
function Xcell_change(col, line_id, value, date, identity, history)
{
  var data_col = data_col_from_col_id(col) ;
  add_a_new_line(line_id, true) ;

  var cell = lines[line_id][data_col] ;
  var empty_before = line_empty(lines[line_id]) ;

  cell.set_value_real(value) ;
  cell.author = identity ;
  cell.date = date ;
  cell.history = history ;
  update_nr_empty(empty_before, line_empty(lines[line_id]),
		  lines[line_id].is_filtered) ;

  var td = td_from_line_id_data_col(line_id, data_col) ;

  if ( td !== undefined )
    {
      update_cell(td, cell, columns[data_col], undefined, lines[line_id]) ;
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
      update_cell(td, cell, columns[data_col], undefined, lines[line_id]) ;
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
    Alert("MSG_refresh") ;
  the_current_cell.do_update_column_headers = true ;
  the_current_cell.update_headers() ;
  table_fill(true, true,true,true) ;
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
  change_option('display_tips', display_tips ? '' : 'n') ;
}

// Set comment

function comment_change(line_id, data_col, comment, td)
{
  create_column(columns[data_col]) ;
  add_a_new_line(line_id) ;

  var ok = lines[line_id][data_col].changeable(lines[line_id],
					       columns[data_col]) ;
  if ( ok !== true )
    {
      alert_append(ok) ;
      return ;
    }
    
  lines[line_id][data_col].set_comment(comment);
  var col_id = columns[data_col].the_id ;
  append_image(td, 'comment_change/' + col_id + '/' +
	       line_id + '/' + encode_uri(comment)) ;
  if ( td )
    update_cell(td, lines[line_id][data_col], columns[data_col], undefined,
		lines[line_id]) ;
}

function comment_on_change()
{
  var input = the_comment ;

  if ( the_comment === undefined )
    return ;

  if ( lines[the_current_cell.line_id][the_current_cell.data_col].comment == input.value )
    return ;

  if ( ! cell.modifiable(lines[the_current_cell.line_id],
			 the_current_cell.column) )
    {
      Alert("ERROR_value_not_modifiable") ;
      return ;
    }
  
  the_current_cell.td.className += ' comment' ;
  comment_change(the_current_cell.line_id, the_current_cell.data_col,
		 input.value, the_current_cell.td) ;
}

function the_filters()
{
  var s = "" ;
  var column ;

  for(var data_col in columns)
    {
      column = columns[data_col] ;
      if ( column.filter !== '' )
	s += _("MSG_filter_on") + ' <B>' + column.title + '</B> : <b>'
	  + html(column.filter) + '</b><BR>\n' ;
    }
  return s ;
}

function printable_introduction()
{
  var problems = [] ;

  if ( tr_classname !== undefined )
    if ( sort_columns[0].data_col != 2 )
      problems.push(_("WARN_not_name_sorted")) ;

  if ( tr_classname !== undefined  &&  popup_on_red_line )
    {
      var nb = 0 ;
      for(i in filtered_lines)
	{
	  line = filtered_lines[i] ;
	  if ( line[0].value == '' && line[1].value == '' )
	    continue ;
	  if ( line[tr_classname].value === 'non' )
	    nb++ ;
	}
      if ( nb )
	problems.push(nb + ' ' + _("WARN_students_not_registered")) ;
    }

  return '<p class="hidden_on_paper printable_introduction">'
    + _("MSG_not_printed") + "<br>" + _("MSG_sorted_by") + " «<b>"
    + sort_columns[0].title + '</b>» ' + _("MSG_sorted_by_more") + ' «<b>'
    + sort_columns[1].title + '</b>»<br>' + the_filters()
    + '<span style="background:#F00;color:white">'
    + problems.join('<br>') + '</span>' ;
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
	    if ( ! columns[data_col].is_empty )
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
      if ( column.is_empty )
	continue ;
      p = [] ;

      for(var attr in column_attributes)
	p.push('"' + attr + '":' + js(column[attr])) ;

      p.push("green_filter:" + column.color_green_filter) ;
      p.push("red_filter:" + column.color_red_filter) ;
      p.push("greentext_filter:" + column.color_greentext_filter) ;
      p.push("redtext_filter:" + column.color_redtext_filter) ;
      if ( isNaN(column.red) || column.red === '' )
	p.push("color_red:" + js(column.red)) ;
      else
	p.push("color_red:" + column.red) ;
      if ( isNaN(column.green) || column.green=== ''  )
	p.push("color_green:" + js(column.green)) ;
      else
	p.push("color_green:" + column.green) ;
      
      if ( isNaN(column.redtext) || column.redtext === '' )
	p.push("color_redtext:" + js(column.redtext)) ;
      else
	p.push("color_redtext:" + column.redtext) ;
      if ( isNaN(column.greentext) || column.greentext=== ''  )
	p.push("color_greentext:" + js(column.greentext)) ;
      else
	p.push("color_greentext:" + column.greentext) ;
      p.push("min:" + column.min) ;
      p.push("max:" + column.max) ;
      p.push("ordered_index:" + column.ordered_index) ;
      p.push("rounding:" + js(column.rounding)) ;
      s.push('Col({' + p.join(',\n') + '})') ;
    }
  return '[\n' + s.join(',\n') + ']' ;
}

function button_toggle(dictionnary, data_col, tag, event)
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
  do_printable_display = true ;
  if ( event )
    stop_event(the_event(event)) ;
}

function toggle_button(text, dictionnary, name, help)
{
  if ( help )
    text = hidden_txt(text, help) ;
  var toggled = eval(dictionnary + '.' + name) ? " toggled" : "" ;
  var a = '<span class="button_toggle' + toggled
    + '" id="' + dictionnary + '.' + name
    + '" onclick="button_toggle('
    + dictionnary + ",'" + name + "',this,event)\">"
    +  text + '</span>' ;
  return a ;
}

function radio_buttons(variable, values, selected, action)
{
  var value, the_class, tip, v ;
  var s = [] ;

  if ( variable.indexOf('.') == -1 )
    s.push('<script>' + variable + ' = "' + selected + '";</script>') ;

  if ( action === undefined )
    action = "do_printable_display=true" ;
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
	+ action + ';stop_event(the_event(event))">' +
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

function html_begin_head()
{
  var p = '{' ;
  for(var i in preferences)
    p += i + ':"' + preferences[i] + '",' ;
  p = p.substr(0,p.length-1) + '};' ;

  var a = '{' ;
  for(var i in table_attr)
    {
      var value = table_attr[i] ;
      if ( table_attributes[i] )
	value = table_attributes[i].formatter(value) ;
      a += i + ':' + JSON.stringify(value) + ',' ;
    }
  a = a.substr(0,a.length-1) + '}' ;

  var languages = '' ;
  var all = preferences['language'].split(',') ;
  for(var i in all)
    languages += '<script onload="this.onloadDone=true;" src="_FILES_/'
      + all[i] + '.js"></script>' ;
  
  return [
     '<html><head>',
     '<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />',
     '<meta charset="utf-8">',
     '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">',
     '<link rel="stylesheet" href="_FILES_/style.css" type="text/css">',
     '<script src="_FILES_/utilities.js" onload="this.onloadDone=true;" charset="UTF-8">',
     '</script>',
     '<script src="_FILES_/middle.js" onload="this.onloadDone=true;" charset="UTF-8">',
     '</script>',
     '<script src="_FILES_/lib.js" onload="this.onloadDone=true;" charset="UTF-8"></script>',
     '<script src="_FILES_/types.js" onload="this.onloadDone=true;" charset="UTF-8"></script>',
     '<script src="_FILES_/abj.js" onload="this.onloadDone=true;" charset="UTF-8"></script>',
     '<style id="computed_style"></style>',
     '<script>var translations = {} ; </script>',
     languages,
     table_headers,
     '<script>',
     'page_id = "" ;',
     'check_down_connections_interval = 0 ;',
     'url = "' + url.split('/=')[0] + '" ;',
     'my_identity = "' + my_identity + '" ;',
     'year = "' + year + '" ;',
     'semester = "' + semester + '" ;',
     'ticket = "' + ticket + '" ;',
     'upload_max = "' + upload_max + '" ;',
     'ampms = ' + JSON.stringify(ampms) + ' ;',
     'ampms_full = ' + JSON.stringify(ampms_full) + ' ;',
     'days = ' + JSON.stringify(days) + ' ;',
     'days_full = ' + JSON.stringify(days_full) + ' ;',
     'months = ' + JSON.stringify(months) + ' ;',
     'months_full = ' + JSON.stringify(months_full) + ' ;',
     'ue = "VIRTUALUE" ;',
     'real_ue = "' + ue + '" ;',
     'root = [];',
     'suivi = "' + suivi + '";',
     'version = "' + version + '" ;',
     'preferences = ' + p + ';',
     'columns = [] ;',
     'lines = {} ;',
     'adeweb = {} ;', // XXX should not be here (LOCAL/spiral.py)
     // "table_headers = " + JSON.stringify(table_headers) + ";",
     'table_attr = ' + a + ';',
     'all_the_semesters = ' + js(all_the_semesters) + ' ;',
     wait_scripts, // The function definition
     '</script>',
     '<title>' + ue + ' ' + year + ' ' + semester + '</title>',
     '</head>',
     '<body class="' + the_body.className + '">'
     ].join('\n') ;
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
  return html_begin_head() + head_html() + new_interface() ;
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

function hide_the_tip_real(force)
{
  var tip = get_tip_element() ;
  if ( !force && tip.innerHTML.indexOf('overflow:') != -1 )
    return ; // To let the user scroll
  if ( !force && tip.do_not_hide )
    return ;
  /* tip.do_not_hide take some time to be setted for tip_plus */
  var tip_display_number = tip.display_number ;
  var tip_plus = document.getElementById('tip_plus') ;
  setTimeout(function() {
      if ( ! tip.do_not_hide && tip.display_number === tip_display_number )
	tip_plus.style.display = "none" ;
    }, 100) ;

  if ( !force && tip.innerHTML.match(/INSTANTDISPLAY/) )
    return ;
  tip.onmousemove = function() {} ;
  tip.style.display = "none" ;
  tip.className = "tip_fade_out" ;
  tip.tip_target = undefined ;
  // remove_highlight() ;
  if ( display_tips_saved !== undefined )
    {
      display_tips = display_tips_saved ;
      display_tips_saved = undefined ;
    }

  if ( element_focused_saved != false )
    {
      element_focused = element_focused_saved ;
      if ( element_focused )
	{
	  if (element_focused.saved_blur != noblur)
	    element_focused.onblur = element_focused.saved_blur ;
	  element_focused.focus() ;
	}
      else
	the_current_cell.input.focus() ;
      element_focused_saved = false ;
    }
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
  table_fill(false, true, false, true) ;
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
      change_option('column_offset') ;
      if ( the_current_cell.col >= table_attr.nr_columns )
	the_current_cell.col = table_attr.nr_columns - 1 ;
    }
  else
    {
      table_attr.nr_lines = i ;
      line_offset = 0 ;
    }
  table_init() ;
  table_fill(false, true, false, true) ;
  update_vertical_scrollbar();
  setTimeout("the_current_cell.update()", 100);
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
  t[ myindex(t,max) ] = max + ' (' + _('MSG_all') + ')' ;
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
      i_striped = i.toString().replace(' (' + _('MSG_all') + ')','') ;
      if ( i_striped == current )
	sel = ii ;
      option.innerHTML = i ;
      option.value = i_striped ;
      if ( created )
	select.appendChild(option) ;
    }
  select.selectedIndex = sel ;
}

function set_body_theme(the_semester)
{
  var theme = preferences.theme === ''
    ? the_semester.substr(0,1) // A or P or T
    : preferences.theme ;
  theme = css_themes[Math.max(myindex(css_themes, theme), 1)] ;
  the_body.className = "theme" + theme ;
}

function initialise_columns()
{
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
      default_title = _("DEFAULT_title") ;
    }
  for(var data_col in columns)
    {
      init_column(columns[data_col]) ;
      columns[data_col].need_update = true ;
    }
  update_columns() ;
}

function runlog(the_columns, the_lines)
{
  column_get_option_running = true ;
  columns = the_columns ;
  lines = the_lines ;

  if ( Number(preferences.zebra_step) > 0 )
    zebra_step = Number(preferences.zebra_step) ;
  else
    zebra_step = 3 ;

  lib_init() ;

  if ( test_bool(preferences.display_tips) == no )
    display_tips = false ;
  scrollbar_right = test_bool(preferences.scrollbar_right) == yes ;
  if ( test_bool(preferences.invert_name) == yes
       && columns.length > 2 && columns[2].title == COL_TITLE_0_2)
    {
      columns[2].position = columns[1].position - 0.1 ;
    }
  if ( preferences.nr_lines > 0 && preferences.nr_lines < 1000 )
    table_attr.nr_lines = preferences.nr_lines ;
  if ( preferences.nr_cols > 0 && preferences.nr_cols < 100 )
    table_attr.nr_columns = preferences.nr_cols ;

  if ( table_attr.default_nr_columns )
    table_attr.nr_columns = table_attr.default_nr_columns ;
  if ( test_bool(preferences.v_scrollbar) == no )
    vertical_scrollbar = undefined ;

  nr_not_empty_lines = 0 ;
  nr_not_fully_empty_lines = 0 ;
  for(var line_id in lines)
    {
      lines[line_id].line_id = line_id ;
      switch ( line_empty(lines[line_id]) )
	{
	case false: nr_not_empty_lines++ ;       // Fall thru
	case 1:     nr_not_fully_empty_lines++ ;
	}
    }

  initialise_columns() ;
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
  update_filtered_lines() ;
  try { table_fill_hook = template_init ; } catch(e) { }

  set_body_theme(semester)

  if ( ! is_a_virtual_ue )
    document.write('<img width="1" height="1" src="' + url + "/=" + ticket
		   + '/' + year + '/' + semester + '/' + ue + '/' +
		   page_id + '/end_of_load" style="position:absolute;left:0;top:0">') ;

  // This function is used when we want to replace the current window
  // content by the popup content.
  // It is NEEDED because some browser open popup UNDER the current window
  function replace_window_content(new_one)
  {
    for(var i in the_body.childNodes)
      if ( the_body.childNodes[i].style )
	the_body.childNodes[i].style.display = 'none' ;
    the_body.onunload = '' ;
    the_body.onkeydown = '' ;
    new_one() ;
  }
  if ( get_option('print-table', 'a') !== 'a' )
    {
      replace_window_content(function()
			     { print_selection(undefined,undefined,'_self')});
      return ;
    }
  if ( get_option('signatures-page', 'a') !== 'a' )
    {
      replace_window_content(function()
			     { print_selection(undefined, 1, '_self')}) ;
      return ;
    }
  if ( get_option('facebook', 'a') !== 'a' )
    {
      replace_window_content(function()
			     { tablefacebook('_self',
					     get_option('facebook',
							undefined))}) ;
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
  autofreeze() ;
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

  // Firefox bug : the page refresh reload the old iframe, not the new one
  // setTimeout(reconnect, 10) ;

  the_current_cell.jump(nr_headers, 0, true) ;
  the_current_cell.update_table_headers() ;

  // The restore popup must not be erased by the table filling
  var old_table_fill_hook = table_fill_hook ;
  function ask_for_restore()
  {
    if ( old_table_fill_hook )
      old_table_fill_hook() ;
    restore_unsaved() ;
  }
  table_fill_hook = ask_for_restore ;

  document.getElementById("linefilter").focus() ;
  column_get_option_running = false ;

  if ( table_attr.code === '' && table_attr.modifiable !== 0
       && i_am_the_teacher && nr_not_empty_lines === 0
       && millisec() - get_date_tomuss(table_creation_date).getTime() < 86400000
       )
    send_invitation() ;
}


// Regression tests (the link is on the home page for super user

function get_tr_classname()
{
  for(var data_col in columns)
    if ( columns[data_col].freezed == 'C' )
      return data_col ;
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
      case 'BUTTON':
	i.innerHTML = v ;
	if ( _("B_Text") == v )
	  v = "Text" ;
	else
	  for(var j in col_types2)
	    if ( col_types2[j] == v )
	      v = col_types[j] ;
	popup_get_element().column = the_current_cell.column ;
	popup_type_choosed(v) ;
	break ;
      default:
	alert('BUG TN: ' + i.tagName) ;
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
	if ( check && (v != check[i] && v !== '') )
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

  var col_types=['Note', 'Moy', 'Nmbr', 'Bool', 'Date'] ;
  var col_types2 = [] ;
  for(var i in col_types)
    col_types2.push(_("B_" + col_types[i])) ;
  if ( preferences.language != "fr" )
    {
      alert("The user & server language must be french to run the regtests") ;
      return ;
    }
  languages = ["fr"] ;
  pre = _('pre') ;
  abi = _('abi') ;
  abj = _('abj') ;
  ppn = _('ppn') ;
  yes = _('yes') ;
  no = _('no') ;
  pre_char = _('pre_char') ;
  abi_char = _('abi_char') ;
  abj_char = _('abj_char') ;
  ppn_char = _('ppn_char') ;
  yes_char = _('yes_char') ;
  no_char = _('no_char') ;
  pre_short = _('pre_short') ;
  abi_short = _('abi_short') ;
  abj_short = _('abj_short') ;
  ppn_short = _('ppn_short') ;
  

  var inputs=['0'   ,'1'   ,'2,2' ,'p'   ,'i'   ,'j'   , 'o'  ,'n'   ,'4/3/2008','3/4/8','12/12/99','0.95', '0.9966'] ;
  var notes =['0.00','1.00','2.20',''    ,abi   ,abj   ,''    ,ppn   ,''        ,''     ,''    	   ,'0.95', '0.99'] ;
  var moys  =['0.00','1.00','2.20','NaN' ,abi   ,abj   ,'NaN' ,ppn   ,'NaN'     ,'NaN'  ,'NaN' 	   ,'0.95', '0.99'] ;
  var expore=['0,00','1,00','2,20','0,00','1,00','4,00','0,00','0,00', '0,00'   ,'0,00'	,'0,00'    ,'0,95', '0,99'] ;
  var nmbr  =['0'   ,'0'   ,'5'   ,'0'   ,'1'   ,'4'   ,'0'   ,'0'   ,'0'       ,'0'    ,'0'   	   , '0'  , '0'] ;
  var boole =[no    ,yes   ,''    ,''    ,''    ,''    ,yes   ,no    ,''        ,''     ,''    	   , ''   , ''] ;
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
  sort_lines3 = function() { } ;
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

  table_autosave_toggle('t_table_attr_autosave') ;

  var t_column_title       = document.getElementById('t_column_title'      );
  var t_column_test_filter = document.getElementById('t_column_test_filter');
  var t_column_columns     = document.getElementById('t_column_columns'    );
  var t_column_type        = document.getElementById('t_column_type'       );

  set(t_column_title, 'Saisie') ;
  set(t_column_type, 'Text') ;
  the_current_cell.cursor_right() ;
  expected('');

  for(var col_type2 in col_types)
    {
      var col_type = col_types[col_type2] ;
      set(t_column_title, col_type) ;
      set(t_column_type, col_types2[col_type2]) ;
      if ( col_type == 'Moy' )
	expected("Indiquez%20maintenant%20les%20titres%20des%20colonnes%20%E0%20moyenner%20en%20les%20s%E9parant%20par%20un%20espace.%0A%0ALes%20poids%20sont%20%E0%20indiquer%20dans%20l%27onglet%20%ABFormule%BB%20de%20chacune%20des%20colonnes%20que%20vous%20moyennez.%0A%0ALes%20poids%20peuvent%20%EAtre%20des%20nombres%20entiers%20ou%20%E0%20virgule.<hr>") ;
      else if ( col_type == 'Nmbr' )
	expected("Indiquez%20maintenant%20les%20titres%20des%20colonnes%20contenant%20les%20valeurs%20%E0%20compter%20en%20les%20s%E9parant%20par%20un%20espace.%0A%0ACe%20que%20vous%20voulez%20compter%20est%20indiqu%E9%20dans%20le%20filtre%20qui%20est%20%E0%20droite%20du%20type%20de%20la%20colonne.<hr>") ;
      the_current_cell.update_headers_real() ;
      if ( col_type == 'Moy' )
	{
	  set(t_column_columns, 'Note AttendueNote') ;
	}
      if ( col_type == 'Nmbr' )
	{
	  set(t_column_columns, 'Saisie Note AttendueNote Moy AttendueMoy') ;
	  set(t_column_test_filter, '>1 | =i | ~u') ;
	}

      the_current_cell.cursor_right() ;
      set(t_column_title, 'Attendue' + col_type) ;
      set(t_column_type, _('Text')) ;
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
  fill_col(inputs, notes, 'p%20n%27est%20pas%20une%20note%20valide%20car%20non%20dans%20l%27intervalle%20%5B0%3B20%5D%0AI%28ABINJ%29%2C%20J%28ABJUS%29%2C%20N%28PPNOT%29%2C%20T%28TNR%29<hr>o%20n%27est%20pas%20une%20note%20valide%20car%20non%20dans%20l%27intervalle%20%5B0%3B20%5D%0AI%28ABINJ%29%2C%20J%28ABJUS%29%2C%20N%28PPNOT%29%2C%20T%28TNR%29<hr>4/3/2008%20n%27est%20pas%20une%20note%20valide%20car%20non%20dans%20l%27intervalle%20%5B0%3B20%5D%0AI%28ABINJ%29%2C%20J%28ABJUS%29%2C%20N%28PPNOT%29%2C%20T%28TNR%29<hr>3/4/8%20n%27est%20pas%20une%20note%20valide%20car%20non%20dans%20l%27intervalle%20%5B0%3B20%5D%0AI%28ABINJ%29%2C%20J%28ABJUS%29%2C%20N%28PPNOT%29%2C%20T%28TNR%29<hr>12/12/99%20n%27est%20pas%20une%20note%20valide%20car%20non%20dans%20l%27intervalle%20%5B0%3B20%5D%0AI%28ABINJ%29%2C%20J%28ABJUS%29%2C%20N%28PPNOT%29%2C%20T%28TNR%29<hr>');
  fill_col(notes, undefined, '');
  var non_modifiable = 'R%E9sultat%20de%20calcul%20non%20modifiable<hr>R%E9sultat%20de%20calcul%20non%20modifiable<hr>R%E9sultat%20de%20calcul%20non%20modifiable<hr>R%E9sultat%20de%20calcul%20non%20modifiable<hr>R%E9sultat%20de%20calcul%20non%20modifiable<hr>R%E9sultat%20de%20calcul%20non%20modifiable<hr>R%E9sultat%20de%20calcul%20non%20modifiable<hr>R%E9sultat%20de%20calcul%20non%20modifiable<hr>R%E9sultat%20de%20calcul%20non%20modifiable<hr>R%E9sultat%20de%20calcul%20non%20modifiable<hr>R%E9sultat%20de%20calcul%20non%20modifiable<hr>R%E9sultat%20de%20calcul%20non%20modifiable<hr>' ;
  fill_col(nmbr, moys, '' /*non_modifiable*/ );
  fill_col(moys, undefined, '');
  fill_col(inputs, nmbr, '' /*non_modifiable*/ );
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
  columnexport_filtered() ;
  columnexport_options["students"] = true ;
  do_columnexport() ;
  v = document.getElementById('columnexport_output').value.split('\n') ;
  for(var i in inputs)
    if ( v[i] != inputs[i] + '\t' + expore[i] )
      alert_real('Export BUG: line=(' + v[i] + ') != expected=(' + inputs[i] + '\t' + expore[i] + ')');
  popup_close() ;
  expected('');

  cell_goto(table.childNodes[nr_headers].childNodes[11]) ;
  set(t_column_type, _('Text')) ;
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

  expected(escape(_("ALERT_columndelete_not_empty")) + '%0A<hr>');

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

function user_is_doing_nothing()
{
  if ( millisec() - last_user_interaction > 60000 ) // 60 seconds
    return true ;
  return false ;
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
  if ( user_is_doing_nothing() )
    table_fill(true) ;
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

function set_updating(bool)
{
  var u = document.getElementById('updating') ;
  if ( u )
    if ( bool )
      u.style.display = 'inline';
    else
      u.style.display = 'none';
}

window.onerror = function(message, url_error, lineNumber) {
  if ( lineNumber == 0 )
    return false ; // Error not in a TOMUSS script
  window.onerror = function() { return false ; } ; // Only first error
  var i = document.createElement('IMG') ;
  var now = new Date() ;
  var user ;
  try { user = window.username ; }
  catch(e) { user = window.my_identity ; }
    
  i.width = i.height = 1 ;
  i.src = url + '/log/javascript_errors/'
        + encode_uri('[' + js(now) + ',' + js(message) + ',' + js(url_error)
		     + ',' + js(lineNumber) + ',' + js(window.location)
		     + ',' + js(user)
		     + ',' + js(navigator.platform
				+ '/' + navigator.appName
				+ '/' + navigator.appVersion
				+ '/' + navigator.product
				)
		     + ',' + js(navigator.userAgent)
		     + ']') ;
  if ( ! window.server_log )
    server_log = document.getElementsByTagName('BODY')[0] ;
  server_log.appendChild(i) ;
  return false ;
} ;

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
window.set_updating    = set_updating ;
