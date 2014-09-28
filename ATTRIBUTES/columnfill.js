// -*- coding: utf-8 -*-
/*
  TOMUSS: The Online Multi User Simple Spreadsheet
  Copyright (C) 2011-2014 Thierry EXCOFFIER, Universite Claude Bernard

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

function caution_message()
{
  if ( table_attr.autosave )
    return '<div id="stop_the_auto_save">' + _("MSG_fill_warning_left")
	+ ' <a href="#" onclick="select_tab(\'table\', \''
	+ _("TAB_column_action")
	+ '\');table_autosave_toggle();document.getElementById(\'stop_the_auto_save\').style.display=\'none\';">'
	+ _("MSG_fill_warning_middle") + '</a> ' +_("MSG_fill_warning_right")
	+ '</div>' ;
  return '' ;
}

function fill_column()
{
  if ( tr_filter.childNodes[0].firstChild.value === ''
     || tr_filter.childNodes[0].firstChild.value === '!=')
      for(var i in filtered_lines)
	  if ( filtered_lines[i][0].is_empty() )
              {
		  var filter0 = tr_filter.childNodes[0].firstChild ;
		  Alert('MSG_fill_remove_empty');
		  the_current_cell.jump(nr_headers, the_current_cell.col,true);
		  filter0.value = '!=' ;
		  filter0.className = filter0.className.replace('empty','') ;
		  filter_change_column(filter0.value, columns[0]) ;
		  periodic_work_remove(update_filtered_lines) ,
		  update_filtered_lines() ;
		  break ;
	      }

  create_popup('fill_column_div',
	       _("TITLE_fill_before")
	       + the_current_cell.column.title + _("TITLE_fill_after"),
	       caution_message()
	       + fill_column_problems(the_current_cell.data_col)
	       + _("MSG_fill") + '<br>&nbsp;<br>'
	       + create_tabs('tablefill',
			     [
				 [_('TAB_fill_clear'),
				  _('MSG_fill_clear')
				 ],
				 [_('TAB_fill_one'),
				  _('MSG_fill_one') + '<br>'
				  + '<INPUT id="column_fill_input"><br>'
				 ],
				 ["ABC ABC ABC...",
				  _('MSG_fill_multiple')
				  +' <tt>A B C A B C A B C...</tt>'
				  +'<br>'
				  +'<TEXTAREA id="column_fill_abab"></TEXTAREA>'
				 ],
				 ["AA... BB... CC...",
				  _('MSG_fill_multiple')
				  +' <tt>A A... B B... C C...</tt><br>'
				  +_('MSG_fill_equal')
				  +'<br>'
				  +'<TEXTAREA id="column_fill_aabb"></TEXTAREA>'
				  ],
				 ["42 43 44 45...",
				  _('MSG_fill_numbers')
				  +'<br>'
				  +'<INPUT id="column_fill_numbers">'
				  ]

			     ])
	       +  _('MSG_fill_before')
	       + ' <BUTTON OnClick="fill_column_do_fill();">'
	       + _('B_fill') + '</BUTTON>/'
	       + '<BUTTON OnClick="fill_column_do_fill(true);">'
	       + _('B_fill_comments') + '</BUTTON> '
	       +  _('MSG_fill_after')
	       ,
	       '', false
	       ) ;
  select_tab("tablefill", _("TAB_fill_one")) ;
  popup_text_area().rows = 4 ;
}

function fill_column_problems(data_col)
{
  var errors = 0, ok = 0 ;
  for(var i in filtered_lines)
    {
      if ( filtered_lines[i][data_col].modifiable(columns[data_col]) )
	ok++ ;
      else
	errors++ ;
    }
  var msg = '<p>' + ok + ' ' + _('MSG_modifiable_cells') + '</p>' ;
  if ( errors )
    msg += '<p><span  class="color_red">' + errors
    + ' ' + _('MSG_unmodifiable_cells') + '</span></p>' ;

  return msg ;
}

function fill_column_parse(t)
{
  var t = parse_lines(t) ;
  var max ;
  for(var i in t)
  {
    max = t[i].replace(/.*{{{(.*)}}}.*/, "$1") ;
    if ( max == t[i] || isNaN(max) )
      max = 999999999 ;
    else
      max = Number(max) ;
    
    // Current number, maximum number, value
    t[i] = [0, max, t[i].split('{{{')[0].replace(/[ \t]*$/,''), i] ;
  }
  // The dispatch is slow, but the algorithm is simple.
  var to_dispatch = filtered_lines.length ;
  var not_full = t.slice(0, t.length) ;
  function sort_values(a, b)
  {
    if ( a[0] != b[0] )
      return a[0] - b[0] ;
    if (  b[1] != a[1] )
      return b[1] - a[1] ;
    return a[3] - b[3] ; // do not change user order
  }
  while( to_dispatch )
  {
    not_full.sort(sort_values) ;
    if ( not_full[0][0] >= not_full[0][1] )
    {
      not_full.shift() ;
      if ( not_full.length == 0 )
	Alert('ALERT_column_fill_max') ;
      continue ;
    }
    not_full[0][0]++ ;
    to_dispatch-- ;
  }
  return t ;
}

function fill_column_do_fill(comments)
{
    alert_append_start() ;

    var choice = selected_tab('tablefill') ;
    if ( choice === _('TAB_fill_clear') )
      fill_column_do_aabb([[999999999, 999999999, '']], comments) ;
    else if ( choice === _('TAB_fill_one') )
	fill_column_do_abab(fill_column_parse(
	    document.getElementById('column_fill_input').value), comments) ;
    else if ( choice === "AA... BB... CC..." )
	fill_column_do_aabb(fill_column_parse(
	  document.getElementById('column_fill_aabb').value), comments, true) ;
    else if ( choice === "ABC ABC ABC..." )
	fill_column_do_abab(fill_column_parse(
	    document.getElementById('column_fill_abab').value), comments) ;
    else if ( choice === "42 43 44 45..." )
    {
	var t = document.getElementById('column_fill_numbers').value ;
	var left = t.replace(/[0-9]+.*/, '') ;
	var right = t.replace(/^[^0-9]*[0-9]+/, '') ;
	var start = Number(t.replace(/^[^0-9]*([0-9]+).*$/, '$1')) ;
	var v = [] ;
	for(var i = start; i < start + filtered_lines.length; i++)
	  v.push([1, 1, left + i + right]) ;
	fill_column_do_abab(v, comments) ;
    }
    else
	alert_real(choice);
   
    alert_append_stop() ;
    the_current_cell.column.need_update = true ;
    update_columns() ;
    popup_close() ;
    table_fill() ;
}

function fill_column_do_aabb(values, comments, display_report)
{
  var j, value, last_sorted_value, current_sorted_value ;
  var sorted = sort_columns[0].data_col ;
  var message = values[0][2] + ': ' + filtered_lines[0][sorted].value ;

  for(j in filtered_lines)
    {
      current_sorted_value = filtered_lines[j][sorted].value ;
      while( values[0][0] == 0 )
      {
	values.shift() ; // remove full value
	message += '→' + last_sorted_value + '\n'
	  + values[0][2] + ': ' + current_sorted_value ;
      }
      last_sorted_value = current_sorted_value ;
      value = values[0] ;
      value[0]-- ;
      
      if ( comments )
	comment_change(filtered_lines[j].line_id, popup_column().data_col,
		       value[2]) ;
      else
	cell_set_value_real(filtered_lines[j].line_id,
			    popup_column().data_col, value[2]) ;

    }
  message += '→' + last_sorted_value + '\n' ;
  if ( display_report )
    alert(message) ;
}

function fill_column_do_abab(values, comments)
{
  var i, j, value ;

  i = 0 ;
  for(j in filtered_lines)
    {
      while( values[i%values.length][0] == 0 )
	i++ ;
      value = values[i%values.length] ;
      value[0]-- ;
      
      if ( comments )
	comment_change(filtered_lines[j].line_id, popup_column().data_col,
		       value[2]) ;
      else
	cell_set_value_real(filtered_lines[j].line_id,
			    popup_column().data_col, value[2]) ;
      i++ ;
    }
}
