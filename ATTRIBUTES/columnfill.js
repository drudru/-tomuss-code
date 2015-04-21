// -*- coding: utf-8 -*-
/*
  TOMUSS: The Online Multi User Simple Spreadsheet
  Copyright (C) 2011-2015 Thierry EXCOFFIER, Universite Claude Bernard

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

var place_separator ;

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

function room_numbers(text)
{
  var n = [], from, to ;
  text = text.split(/ +/) ;
  for(var i in text)
    {
      var range = text[i].split(/-+/) ;
      if ( range.length == 2 && range[0].length != 0 )
	{
	  from = Number(range[0]) ;
	  to = Number(range[1]) ;
	}
      else
	{
	  from = Number(text[i]) ;
	  if ( from < 0 )
	    {
	      var to_remove = myindex(n, -from) ;
	      if ( to_remove >= 0 )
		n.splice(to_remove, 1) ;
	      continue ;
	    }
	  to = from ;
	}
      if ( ! isNaN(from) && ! isNaN(to) )
	for(var j = from; j <= to ; j++)
	  n.push(j) ;
    }
  return n ;
}

function fill_analyse_rooms()
{
  if ( ! analyse_rooms.places_used || ! analyse_rooms.places_used[''] )
    return ; // nothing to dispatch
  var e = document.getElementById("analyse_rooms") ;
  var full_size = 0 ;
  var to_dispatch = analyse_rooms.places_used[''][4] ;
  for(var i=1; i<e.childNodes.length; i++)
    {
      var infos = analyse_rooms.places_used[analyse_rooms.index[i-1]] ;
      var label = e.childNodes[i].firstChild.firstChild ;
      var input = label.childNodes[0] ;
      if ( input.checked )
	{
	  infos[5] = room_numbers(infos[1]).length ;
	  full_size += infos[5] ;
	  to_dispatch += infos[4] ;
	}
      else
	infos[5] = 0 ;
    }
  fill_analyse_rooms.dispatch = [] ;
  for(var i=1; i<e.childNodes.length; i++)
    {
      var infos = analyse_rooms.places_used[analyse_rooms.index[i-1]] ;
      var label = e.childNodes[i].firstChild.firstChild ;
      var input = label.childNodes[0] ;
      var text = label.childNodes[2] ;
      var take ;
      if ( infos[5] )
	{
	  if ( 0 )
	    console.log('to_dispatch=' + to_dispatch
			+ ' size=' + infos[5]
			+ ' full_size=' + full_size
			+ ' yet_used=' + infos[4]) ;
	  take = Math.max(0,
			  Math.round(to_dispatch * infos[5] / full_size
				    ) - infos[4]) ;
	  to_dispatch -= take + infos[4] ;
	  }
      else
	take = 0 ;
      full_size -= infos[5] ;
      var numbers = room_numbers(infos[1]) ;
      var place, n ;
      for(var j=0; j<take; j++)
	{
	  // Search an unused place number
	  do
	    {
	      place = infos[0] + place_separator + numbers.shift() ;
	    }
	  while( analyse_rooms.number_used[place] ) ;
	  fill_analyse_rooms.dispatch.push(place.replace(
	    place_separator + 'undefined', '')) ;
	}

      var s = [] ;
      if ( infos[4] !== 0 )
	s.push(infos[4]) ;
      if ( take !== 0 )
	s.push(take) ;
      if ( s.length === 0 )
	s.push('') ;
      var max = room_numbers(infos[1]).length ;
      s = s.join('+') + '/' + max ;
      var inside =  infos[4] + take ;
      if ( inside > max )
	s = hidden_txt('<span style="color:#F00">' + s + '</span>',
		       '+' + (inside - max) + ' !') ;
      text.innerHTML = s ;
    }
}

function analyse_rooms(column)
{
  if ( column.real_type.title != 'Text' )
    return _("MSG_fill_room_text") ;
  place_separator = _("MSG_fill_room_place_separator") ;
  var v ;
  analyse_rooms.places_used = {} ;
  analyse_rooms.number_used = {} ;
  for(var i in rooms)
    {
      analyse_rooms.places_used[rooms[i][0]] = rooms[i] ;
      rooms[i][4] = 0 ; // Yet used places
    }
  for(var i in filtered_lines)
    {
      v = filtered_lines[i][column.data_col].value ;
      var room = v.split(place_separator)[0] ;
      if ( analyse_rooms.places_used[room] === undefined )
	analyse_rooms.places_used[room] = [room, '1-9999', '', '', 0] ;
      analyse_rooms.places_used[room][4]++ ;
      analyse_rooms.number_used[v] = true ;
    }
  analyse_rooms.index = [] ;
  for(var i in analyse_rooms.places_used)
    if ( i !== '' )
      analyse_rooms.index.push(i) ;
  analyse_rooms.index.sort() ;
  
  var s = [analyse_rooms.places_used[''] === undefined
	   ? _('MSG_fill_room_nothing')
	   : _('MSG_fill_room')
	   + '<br><label><input type="checkbox" style="width:auto" id="room_places"> '
	   + _('MSG_fill_room_place') + '</label>',
	   ,
	   '<table class="colored"><tbody id="analyse_rooms">',
	   '<tr>',
	   '<th>', _('COL_TITLE_room_use'),
	   '<th>', _('COL_TITLE_room_name'),
	   '<th>', _('COL_TITLE_room_places'),
	   '<th>', _('COL_TITLE_room_comment'),
	   '</tr>'
	  ] ;
  for(var i in analyse_rooms.index)
    {
      i = analyse_rooms.index[i] ;
      i = analyse_rooms.places_used[i] ;
      s.push('<tr><td style="white-space:pre"><label><input style="width:auto;" type="checkbox" onchange="fill_analyse_rooms()"> <span></span></label><td>')
      if ( i[2] !== '' )
	s.push('<a target="_blank" href="' + i[2] + '">'
	       + html(i[0]) + '</a>') ;
      else
	s.push(html(i[0])) ;
      s.push("<td>") ;
      s.push(html(i[1])) ;
      s.push('<td>') ;
      s.push(html(i[3])) ;
      s.push('</tr>') ;
    }
  s.push("</tbody></table>") ;
  if ( len(rooms) == 0 )
    s.push('<div class="color_red">' + _('MSG_no_rooms') + "</div>") ;

  return s.join('') ;
}

function fill_column()
{
  if ( columns[0].filter === '' )
  {
    for(var i in filtered_lines)
    {
      if ( filtered_lines[i][0].is_empty() )
      {
	the_current_cell.jump(nr_headers, the_current_cell.col, true) ;
	filter_change_column('!=', columns[0]) ;
	// The previous function modify the current column filter :-(
	// So restore it.
	filter_change_column(the_current_cell.column.filter,
			     the_current_cell.column) ;
	table_fill(true, true, true) ;
	Alert('MSG_fill_remove_empty') ;
	break ;
      }
    }
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
				  +'<div class="fillbottom"><TEXTAREA id="column_fill_abab"></TEXTAREA></div>'
				 ],
				 ["AA... BB... CC...",
				  _('MSG_fill_multiple')
				  +' <tt>A A... B B... C C...</tt><br>'
				  +_('MSG_fill_equal')
				  +'<div class="fillbottom"><TEXTAREA id="column_fill_aabb"></TEXTAREA></div>'
				  ],
				 ["42 43 44 45...",
				  _('MSG_fill_numbers')
				  +'<br>'
				  +'<INPUT id="column_fill_numbers">'
				  ],
				 [_("COL_TITLE_room_name"),
				  analyse_rooms(the_current_cell.column)
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
  fill_analyse_rooms() ;
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
      var x = t.match(/([0-9]+)([^0-9]*)$/) ;
      var before = t.substr(0, t.length - x[0].length) ;
      var after = x[2] ;
      var start = Number(x[1]) ;
      var v = [], s ;
      for(var i = start; i < start + filtered_lines.length; i++)
      {
	s = i.toString() ;
	while( s.length < x[1].length )
	  s = '0' + s ;
	v.push([1, 1, before + s + after]) ;
      }
      fill_column_do_abab(v, comments) ;
    }
    else if ( choice === _('COL_TITLE_room_name') )
      {
	var v = [] ;
	var add_place = document.getElementById("room_places").checked ;
	for(var i = 0; i < filtered_lines.length; i++)
	  {
	    var val = filtered_lines[i][popup_column().data_col].value ;
	    if ( val === '' )
	      {
		val = fill_analyse_rooms.dispatch.shift() ;
		if ( ! add_place )
		  val = val.split(place_separator)[0] ;
	      }
	    v.push([1, 1, val]) ;
	  }
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
