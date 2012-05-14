// -*- coding: utf-8 -*-
/*
    TOMUSS: The Online Multi User Simple Spreadsheet
    Copyright (C) 2008-2012 Thierry EXCOFFIER, Universite Claude Bernard

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

var free_print_headers ;
var textual_table = '' ;

function printable_display_page(lines, title, page_break)
{

  var v, i, cell, line_id, tt = [], nr_lines ;
  var sorted = [] ;
  for(var c in columns)
    sorted.push(c) ;
  sorted.sort(function(a,b)
	      { return columns[a].position - columns[b].position ; }) ;

  for(var i=0;;i++)
    {
      var input = document.getElementById('free' + i) ;
      if ( ! input )
	break ;
      if ( input.value )
	sorted.push([input.value, i]) ;
    }

  var s = [] ;
  var html_class = 'printable_table', th_class ;

  if ( uniform == _("B_print_yes") )
    html_class += ' tdnowrap' ;

  if ( page_break )
    th_class = ' style="page-break-before:always;"' ;
  else
    th_class = '' ;

  s.push('<h2' + th_class + '>' + year + ' ' + semester + ' ' + ue
	 + ': ' + table_title + ' ' + title + '</h2>') ;

  nr_lines = 0 ;
  tt = [] ;
  for(var line_id in lines)
    {
      cell = lines[line_id][columns.length] ;
      if ( cell )
	tt.push(lines[line_id][0].value + ' '
		+ lines[line_id][1].value + ' '
		+ lines[line_id][2].value + '<ul>'
		+ cell + '</ul>') ;
      nr_lines++ ;
    }

  if ( do_emargement_header )
    {
      if ( tt.length )
	  v = ' ' + _("MSG_print_nr_tt_before") + ' <b>' + tt.length + ' '
	      + _("MSG_print_nr_tt_after") + '</b>' ;
      else
	  v = _("B_print_no_tt") ;
      s.push(
	     '<table width="100%" style="white-space: pre ;">'
	     + '<tr style="vertical-align:top;"><td>'
	     + '<p>' + _("MSG_print_date")
	     + "<p>" + _("MSG_print_supervisors")
	     + "<p>" + _("MSG_print_room")
	     + "<p>" + _("MSG_print_nr_students")
	     + "<b>" + nr_lines + "</b>" + v
	     + "</td>"
	     + '<td><p>' + _("MSG_print_nr_present")
	     + "<p>" + _("MSG_print_nr_signature")
	     + "<p>" + _("MSG_print_nr_paper")
	     + "</td></tr></table>"
	     ) ;
    }
  if ( tierstemps != _("B_print_only") )
    {
      var t = [], txt_line ;
      s.push('<table id="table_to_print" class="' + html_class + '"><thead>') ;
      for(var header in headers_to_display)
	{
	  if ( ! headers_to_display[header] )
	    continue ;
	  s.push('<tr><td class="hidden_on_paper smaller" onclick="button_toggle(' 
		 + 'headers_to_display,\'' + header
		 + '\',document.getElementById(\'headers_to_display_'
		 + header + '\'));'
		 + 'do_printable_display=true;">'
		 + header
		 + '</td>') ;
	  txt_line = [] ;
	  for(var c in sorted)
	    {
	      c = sorted[c] ;
	      if ( isNaN(c) )
		{
		  if ( header == 'title' )
		    {
		      s.push('<th onclick="do_printable_display=true;'
			     + 'document.getElementById(\'free'
			     + c[1] + '\').value = \'\'">'
			     + html(c[0])
			     + '</th>') ;
		      txt_line.push(c[0]) ;
		    }
		  else
		    {
		      txt_line.push('') ;
		      s.push('<th>&nbsp;</th>') ;
		    }
		  continue ;
		}
	      if ( ! columns_to_display[c] )
		continue ;

	      v = columns[c][header] ;
	      txt_line.push(v) ;
	      if ( v.length > 30 )
		th_class = ' smaller' ;
	      else if ( v.length > 10 )
		th_class = ' smaller' ;
	      else
		th_class = '' ;

	      if ( ! column_modifiable_attr(header, columns[c]) )
		v = '' ;

	      if ( v === '' )
		v = '&nbsp;' ;

	      s.push('<th onclick="button_toggle(columns_to_display,'
		     + c + ',document.getElementById(\'columns_to_display\').getElementsByTagName(\'SPAN\')['
		     + columns[c].ordered_index + ']);do_printable_display=true" class="'
		     + th_class + '">'
		     + v + '</th>') ;
	    }
	  s.push('</tr>') ;
	  t.push( txt_line.join('\t') ) ;
	}
      s.push('<thead>') ;
      i = 1 ;
      for(var line_id in lines)
	{
	  line = lines[line_id] ;
	  if ( tr_classname === undefined )
	    html_class = '' ;
	  else
	    html_class = line[tr_classname].value ;
	  if ( nr_lines == i || i % preferences.zebra_step === 0 )
	    html_class += ' separatorvertical' ;
	  s.push('<tr class="' + html_class + '"><td class="hidden_on_paper" onclick="delete lines[\'' + line_id + '\'];do_printable_display=true;">'
		 + i + '</td>') ;
	  i++ ;
	  txt_line = [] ;
	  for(var c in sorted)
	    {
	      c = sorted[c] ;
	      if ( isNaN(c) )
		{
		  txt_line.push('') ;
		  s.push('<td>&nbsp;</td>') ;
		  continue ;
		}
	      if ( ! columns_to_display[c] )
		continue ;
	      cell = line[c] ;
	      html_class = '' ;
	      if ( cell.value.toFixed )
		{
		  html_class += ' number' ;
		  v = tofixed(cell.value) ;
		  if ( separator == _("B_print_comma") )
		    v = v.replace('.', ',') ;
		}
	      else
		v = cell.value_html() ;
	      txt_line.push(v.replace(/\t/g, ' ')) ;
	      if ( v === '' )
		v = '&nbsp;' ;
	      if ( columns[c].green_filter(cell, columns[c]) )
		html_class += ' color_green' ;
	      if ( columns[c].red_filter(cell, columns[c]) )
		html_class += ' color_red' ;
	    
	      s.push('<td class="' + html_class + '">' + v + '</td>') ;
	    }
	  t.push( txt_line.join('\t') ) ;
	  s.push('</tr>') ;
	}
      s.push('</table>') ;
      textual_table = t.join('\n') ;
    }
  if ( tierstemps != _("B_print_no") && tt.length )
      s.push('<h2 style="page-break-before:always;">' + _("MSG_print_tt_title")
	     + '</h2>' + tt.join('\n'));

  return s.join('\n') ;
}

function printable_display()
{
  if ( ! do_printable_display )
    return ;
  do_printable_display = false ;

  var groups = compute_groups_values(grouped_by) ;
  var x, selected_lines, i, title ;

  if ( do_emargement_header ) 
    for(var i in lines)
      if ( ! display_on_signature_table(lines[i]) )
	delete lines[i] ;

  if ( groups.length == 1 )
    x = printable_display_page(lines, '', false) ;
  else
    {
      var t = [] ;
      for(var group in groups)
	{
	  group = groups[group] ;

	  i = 0 ;
	  title = [] ;
	  for(var g in grouped_by)
	    {
	      if ( grouped_by[g] )
		title.push(columns[g].title + '=' + group.split('\001')[i++]) ;
	    }
	  title = html(' ' + title.join(', ')) ;
	  selected_lines = {} ;
	  for(var j in lines)
	    if ( compute_groups_key(grouped_by, lines[j]) == group )
	      selected_lines[j] = lines[j] ;
	  t.push(printable_display_page(selected_lines,
					title,
					t.length != 0)) ;
	}
      x = t.join('\n');
    }

  document.getElementById('content').innerHTML = x ;
}

function display_button(data_col, title, selected, table_name, tip, not_escape,
			html_class)
{
  if ( selected )
    selected = 'toggled' ;
  else
    selected = '' ;
  if ( ! html_class )
    html_class = '' ;
  if ( ! not_escape )
    title = html(title) ;
  if ( tip )
    title = hidden_txt(title, tip) ;
  return '<span class="button_toggle ' + selected + ' ' + html_class
    + '" onclick="button_toggle(' + table_name + ','
    + data_col + ',this);do_printable_display=true;"'
    + ' id="' + table_name + '_'
    + data_col.replace(/\'/g,'')+ '">'
    + title + '</span>' + '<script>'
    + table_name + '[' + data_col + '] =' + !!selected + '</script>' ;
}

function first_line_of_tip(attr)
{
  var tip_name = 'TIP_column_attr_' + attr ;
  var tip = _(tip_name) ;
  if ( tip == tip_name )
      tip = _(tip_name + '__') ; // Generic comment the the attribute
  else
      tip = tip.split('</b>')[0].substr(3) ;
  return tip ;
}

function print_add_free_column()
{
    var i = free_print_headers.length - 1 ;
    var o = document.getElementById('free' + i) ;
    var e = document.createElement("INPUT") ;
    o.parentNode.insertBefore(e, o.nextSibling) ;
    e.id = 'free' + (i+1) ;
    e.style.width = "5em" ;
    e.onkeyup = function() { do_printable_display=true; } ;
    e.value = "--" + i + "--" ;
    free_print_headers.push(e.value) ;
    do_printable_display = true ;
}

function do_emargement()
{
  for(var i in free_print_headers)
    document.getElementById('free' + i).value = free_print_headers[i] ;

  for(var data_col in columns_to_display)
    {
      if ( (data_col < 3) !=  columns_to_display[data_col] )
	button_toggle(columns_to_display, data_col,
		      document.getElementById('columns_to_display_' + data_col)
		      );
    }
  for(var header in headers_to_display)
    {
      if ( (header == 'title') !=  headers_to_display[header] )
	button_toggle(headers_to_display, header,
		      document.getElementById('headers_to_display_' + header)
		      );
    }
  do_printable_display = true ;
  do_emargement_header = true ;
}

function do_page_per_group()
{
  for(var data_col in grouped_by)
    {
      if ( (data_col == 3 || data_col == 4) !=  grouped_by[data_col] )
	button_toggle(grouped_by, data_col,
		      document.getElementById('grouped_by_' + data_col)
		      );
    }
  do_printable_display = true ;
}

function print_choice_line(p, title, title_tip, choices, the_id)
{
  if ( the_id )
    the_id = ' id="' + the_id + '"' ;
  else
    the_id = '' ;
  p.push('<tr><td class="nowrap">' + hidden_txt(title, title_tip)
	 + '</td><td class="toggles"' + the_id + '>'
	 + choices + '</td></tr>') ;
}

function popup_export_window(event)
{
    create_popup('textual_table', _("MSG_print_popup_title"),
		 _("MSG_print_popup_content"),
	       '') ;
  popup_set_value(textual_table) ;
}


function print_selection(object, emargement, replace)
{
  free_print_headers = [_("MSG_print_present"), _("MSG_print_given")] ;
  var p = [ printable_introduction() ] ;
  p.push('<script>') ;
  p.push('var do_printable_display = true ;') ;
  p.push('var columns_to_display = {};') ;
  p.push('var headers_to_display = {};') ;
  p.push('var grouped_by = {};') ;
  p.push('var do_emargement_header = 0;') ;
  p.push('var tr_classname = "' + tr_classname + '";') ;
  p.push('var popup_on_red_line = ' + popup_on_red_line + ';') ;
  p.push('var ue = ' + js(ue) + ';') ;
  var t = [] ;
  for(var i in free_print_headers)
      t.push(js(free_print_headers[i])) ;
  p.push('var free_print_headers = [' + t.join(',') + '];') ;  
	 
  p.push('var table_title = ' + js(table_attr["table_title"]) + ';') ;
  p.push('var display_tips = true ;') ;
  p.push('var columns = ' + columns_in_javascript() + ';') ;
  p.push('var tr_classname = ' + tr_classname + ';') ;
  p.push('var lines ;') ;
  p.push('function initialize() {') ;
  p.push('if ( ! wait_scripts("initialize()") ) return ;') ;
  p.push('lines = ' + lines_in_javascript() + ';') ;
  if ( emargement )
    p.push('do_emargement();') ;
  p.push('setInterval("printable_display()", 200);') ;
  p.push('}') ;
  p.push('</script>') ;
  p.push('<p class="hidden_on_paper"><a href="javascript:do_emargement()">'
	 + _("MSG_print_do_attendance_sheet") + '</a>');
  p.push('<p class="hidden_on_paper"><a href="javascript:do_page_per_group()">'
	 + _("MSG_print_do_one_sheet_per_group") + '</a>');
  p.push('<p class="hidden_on_paper"><A href="javascript:popup_export_window()">'
	 + _("MSG_print_do_spreadsheet_export") + '</a>');
  p.push('<p class="hidden_on_paper">' + _("MSG_print_hide_title")) ;
  p.push('<table class="hidden_on_paper print_options">') ;
  print_choice_line(p, _("MSG_print_display_tt"),
		    _("TIP_print_display_tt"),
		    radio_buttons('tierstemps',
				  [_("B_print_yes"),
				   _("B_print_no"),
				   _("B_print_only")],
				  _("B_print_no"))
		    ) ;
  print_choice_line(p, _("MSG_print_display_separator"),
		    _("TIP_print_display_separator"),
		    radio_buttons('separator',
				  [_("B_print_comma"),
				   _("B_print_dot")],
				  _("B_print_comma"))) ;
  print_choice_line(p, _("MSG_print_display_line"),
		    _("TIP_print_display_line"),
		    radio_buttons('uniform',[_("B_print_yes"),
					     _("B_print_no")],
				  _("B_print_yes")));

  var t = [], cols = column_list_all() ;
  for(var data_col in cols)
    {
      data_col = cols[data_col].toString() ;
      if ( ! columns[data_col].is_empty )
	t.push(display_button(data_col, columns[data_col].title,
			      ! columns[data_col].hidden,
			      'columns_to_display',
			      html(columns[data_col].comment)));
    }
  print_choice_line(p, _("MSG_print_display_columns"),
		    _("TIP_print_display_columns"),
		    t.join(' '),
		    'columns_to_display') ;

  t = [] ;
  for(var data_col in cols)
    {
      data_col = cols[data_col].toString() ;
      if ( ! columns[data_col].is_empty )
	t.push(display_button(data_col, columns[data_col].title,
			      false,
			      'grouped_by',
			      html(columns[data_col].comment)));
    }
  print_choice_line(p, _("MSG_print_display_paging"),
		    _("TIP_print_display_paging"),
		    t.join(' '),
		    'grouped_by') ;

  t = [] ;
  t.push(hidden_txt('<a onclick="print_add_free_column()">+</a>',
		    _("TIP_print_add_column"))) ;
  for(var i in free_print_headers)
      t.push(hidden_txt('<input id="free' + i + '" style="width:15em" onkeypress="do_printable_display=true;">', _("TIP_print_column_name"))) ;
  print_choice_line(p, _("MSG_print_display_add_columns"),
		    _("TIP_print_display_add_columns"),
		    '<small>' + t.join(' '),
		    'columns_to_display') ;

		    
  var attrs = ['title','type','red','green','weight','minmax','empty_is','comment','columns','enumeration','test_filter','visibility_date'] ;
  
  t = [] ;
  for(var attr in attrs)
    {
      attr = attrs[attr] ;
      t.push(display_button("'" + attr + "'", _('B_print_attr_' + attr),
			    attr == 'title', 'headers_to_display',
			    first_line_of_tip(attr))) ;
    }
  print_choice_line(p, _("MSG_print_display_headers"),
		    _("TIP_print_display_headers"),
		    t.join(' '),
		    'headers_to_display') ;

  p.push('</table>') ;
  p.push('<div style="clear:both" id="content"></div>') ;
  p.push('</div>') ;
  p.push('<script>') ;
  p.push('setTimeout(initialize, 100) ;') ; // Timeout for IE
  p.push('</script>') ;

  var w = window_open('', replace) ;
  w.document.open('text/html') ;
  w.document.write(html_begin_head(true) + p.join('\n')) ;
  w.document.close() ;
  return w ;
}
