// -*- coding: utf-8 -*-
/*
  TOMUSS: The Online Multi User Simple Spreadsheet
  Copyright (C) 2011-2016 Thierry EXCOFFIER, Universite Claude Bernard

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

function caution_message(no_float)
{
  if ( table_attr.autosave )
    return '<div id="stop_the_auto_save" style="'
    + (no_float ? '' : 'float:right;')
    + '">'
    + _("MSG_fill_warning_left")
    + ' <a href="#" onclick="select_tab(\'table\', \''
    + _("TAB_column_action")
    + '\');table_autosave_toggle();document.getElementById(\'stop_the_auto_save\').style.display=\'none\';">'
    + _("MSG_fill_warning_middle") + '</a> ' +_("MSG_fill_warning_right")
    + '</div>' ;
  return '' ;
}

/****************************************************************************/

function Room(infos)
{
  this.id      = Room.id++ ;
  this.name    = infos[0] ;
  this.places  = new Places(infos[1] || '1-9999') ;
  this.url     = infos[2] || '' ;
  this.comment = infos[3] || '' ;
  this.predefined_places = !!infos[1] ;
  this.predefined_name = !!infos[0] ;
  this.clear() ;
}
Room.id = 0 ;

Room.prototype.clear = function()
{
  this.nr_used = 0 ;         // Number of places yet used
  this.number_used = {} ;    // Indexed by the place number
  this.nr_will_be_used = 0 ; // Will be used be the filling
  this.places.iter_start('') ;       // Goto before the first place
  this.nr_erased = 0 ;       // Number of value erase

} ;

function remove_leading_0_and_space(txt)
{
  for(;;)
    {
      var f = txt.substr(0,1) ;
      if ( f == '0' || f == ' ' )
	txt = txt.substr(1) ;
      else
	return txt ;
    }
}

Room.prototype.add_predefined = function(line_id, place)
{
  this.nr_used++ ;
  this.number_used[remove_leading_0_and_space(place)] = true ;
} ;

Room.prototype.get_key = function()
{
  return (this.enumeration ? '0' : '1')
  + (this.predefined_places ? '1' : '0')
  + this.name ;
} ;

function fill_column_past_event(event)
{
  event = the_event(event) ;
  var data = event.real_event.clipboardData.getData('text/plain').trim() ;
  if ( data.indexOf('\n') == -1 )
    return ;
  data = data.split(/[\r\n]+/) ;

  event.target.value = data[0] ;
  for(var i in data)
    {
      var value = data[Number(i)+1] ;
      if ( value === undefined )
	continue ;
      value = value.trim() ;
      if ( value === '' )
	continue ;
      Filler.filler.add_empty_input().get_name().value = value ;
    }
  Filler.filler.update_html() ;
  stop_event(event) ;
}

function fill_column_keypress(event)
{
  event = the_event(event) ;
  switch ( event.keyCode )
  {
  case 13:
  case 40:
    var room = Filler.filler.next_room(Filler.filler.get_room(event.target)) ;
    if ( room !== undefined )
      room.get_name().focus() ;
    break ;
  case 38:
    var room = Filler.filler.previous_room(
      Filler.filler.get_room(event.target)) ;
    if ( room !== undefined )
      room.get_name().focus() ;
    break ;
  }    
}

Room.prototype.new_size = function()
{
  return this.nr_used + this.nr_will_be_used - this.nr_erased ;
}

Room.prototype.filling = function()
{
  // +1 because 0/9 should be more filled than 0/999
  return (this.new_size() + 1) / this.places.nr_places ;
}

Room.prototype.yet_overflowed = function()
{
  return this.checked && this.nr_used >= this.places.nr_places ;
}

Room.prototype.get_place = function(pad0)
{
  this.nr_will_be_used++ ;
  // Search an unused place number
  var place ;
  do
  {
    place = this.places.iter_next([' ', '0', ''][pad0]);
    if ( place === undefined || place === null )
    {
      place = undefined ;
      break ;
    }
  }
  while( this.number_used[remove_leading_0_and_space(place)] ) ;
  if ( place )
    this.number_used[place] = true ;
  return place ;
}


Room.prototype.html = function()
{
  var cb = '<input type="checkbox" class="room_cb">' ;
  var name = '<input value="' + encode_value(this.name)
    + '" onpaste="fill_column_past_event(event)'
    + '" onkeypress="fill_column_keypress(event)'
    + '">' ;
  return '<tr class="room_line '
    + (this.predefined_places ? 'room_predefined' :
       (this.created_empty ? 'room_created_empty' :
	(this.enumeration ? 'room_enumeration' :
	 'room_yet_used'))
      )
    + (this.in_comment & !this.in_value ? ' only_comment' : '')
    + (!this.in_comment & this.in_value ? ' only_value' : '')
    + '" id="ROOM_' + this.id
    + '">'
    + '<td class="room_used">'
    + '<td class="room_used">'
    + '<td class="room_used">'
    + '<td class="room_cb">' + cb
    + '<td class="room_name">' + name
    + (this.comment ?
       '<div class="room_comment">'
       + (this.url !== '' ? '<a target="_blank" href="' + this.url + '">' : '')
       + html(this.comment)
       + (this.url !== '' ? '</a>' : '')
       + '</div>'
       : ''
       )
    + '<td class="room_places"><input value="'
    + encode_value(this.places.text) + '">'
    + '</tr>' ;
} ;

Room.prototype.get_tr = function() {
  return document.getElementById('ROOM_' + this.id) ;
} ;
Room.prototype.get_toggle = function() {
  return this.get_tr().childNodes[3].firstChild ;
} ;
Room.prototype.get_nr_used = function() {
  return this.get_tr().childNodes[0] ;
} ;
Room.prototype.get_nr_will_be_used = function() {
  return this.get_tr().childNodes[1] ;
} ;
Room.prototype.get_total = function() {
  return this.get_tr().childNodes[2] ;
} ;
Room.prototype.get_name = function(i) {
  return this.get_tr().childNodes[4].firstChild ;
} ;
Room.prototype.get_places = function(i) {
  return this.get_tr().childNodes[5].firstChild ;
} ;
Room.prototype.get_comment = function(i) {
  return this.get_tr().childNodes[4].childNodes[1] ;
} ;

Room.prototype.update_html = function()
{
  this.get_nr_used().innerHTML = this.nr_used
    ? (this.name === '' && this.checked
       ? '<span style="color:#888">' + this.nr_used + '</span>'
       : this.nr_used)
    : ' ' ;
  var n = this.nr_will_be_used - this.nr_erased ;
  if ( n > 0 )
    n = '+' + n ;
  else if ( n == 0 )
    n = ' ' ;

  this.get_nr_will_be_used().innerHTML = n ;
  var total = this.nr_used + this.nr_will_be_used - this.nr_erased ;
  var overflow = total - this.places.nr_places ;
  this.get_total().innerHTML = total
    ? '=' + total + (
      overflow > 0
	? '<span class="fill_warning">(' + overflow + ')</span>'
	: '')
  : ' ' ;
} ;


/****************************************************************************/

function Filler(last_filler)
{
  this.column = the_current_cell.column ;
  this.data_col = the_current_cell.column.data_col ;
  if ( last_filler )
  {
    this.toggles = last_filler.toggles ;
    this.rooms = last_filler.rooms ;
    this.index = last_filler.index ;
    this.example_row_defined = true ;
  }
  else
  {
    this.toggles = {
      'modify': 0,
      'interleave': 0,
      'unfiltered': 1,
      'comment': 0,
      'pad0': 1,
      'relative': 0
    } ;
    this.create_rooms() ;
  }
  this.id = setInterval(this.update_html.bind(this), 100) ;
}

Filler.prototype.get_room = function(element) {
  while(element.tagName != 'TR')
    element = element.parentNode ;
  var id = element.id.split("_")[1] ;
  for(var room in this.rooms)
    {
      room = this.rooms[room] ;
      if ( room.id == id )
	return room ;
    }
} ;

Filler.prototype.room_index = function(room) {
  for(var i = 0; i < this.index.length; i++)
    if ( this.rooms[this.index[i]] === room )
      break ;
  return i ;
} ;

Filler.prototype.next_room = function(room) {
  var i = this.room_index(room) ;
  while(i++ < this.index.length )
  {
    var next = this.rooms[this.index[i]] ;
    if ( this.visible(next) )
      return next ;
  }
} ;

Filler.prototype.previous_room = function(room) {
  var i = this.room_index(room) ;
  while(--i >= 0)
  {
    var next = this.rooms[this.index[i]] ;
    if ( this.visible(next) )
      return next ;
  }
} ;

Filler.prototype.menu = function() {
  s = '<div class="fill_menu">' ;
  for(var key in this.toggles)
    {
      s += '<select id="select.' + key + '" value="' + this.toggles[key] + '">'
	+ '<option' + (this.toggles[key] == 0 ? ' selected': "")
	+ '>' + _("TIP_fill_no_" + key) + '</option>'
	+ '<option' + (this.toggles[key] == 1 ? ' selected': "")
	+ '>' + _("TIP_fill_" + key) + '</option>'
	+ (key == 'pad0'
	   ? '<option' + (this.toggles[key] == 2 ? ' selected': "")
	   + '>' + _("TIP_fill_empty_" + key) + '</option>'
	   : ''
	   )
	+ '</select>' ;
    }
  s += '</div>' ;
  return s ;
} ;

function text_to_room_and_place(text)
{
  var m = text.match(/(.*[^0-9. ])( *[0-9]+)(.*)/) ;
  if ( m )
      return [m[1] + '%%' + m[3], m[2]] ;
  m = text.match(/^[0-9]+$/) ;
  if ( m )
    return ['%%', text] ;
  return [text, 'undefined'] ;
}

Filler.prototype.create_rooms = function() {
  var room ;
  this.rooms = {} ; // Indexed by room name
  var enumeration = this.column.real_type.cell_completions('', this.column) ;
  if ( this.column.type == 'Note' )
    enumeration = [abi, abj, ppn, tnr] ; // Do not want popup menu for grades
  if ( ! enumeration.toUpperCase ) // A table of possible values
    {
      for(var i in enumeration)
	{
	  {
	    i = enumeration[i] ;
	    this.rooms[i] = new Room([i]) ;
	    this.rooms[i].enumeration = true ;
	  }
	}
    }

  // Create predefined rooms
  if ( this.column.type != 'Note' && this.column.type != 'Prst' )
  {
    for(var i in rooms)
    {
      this.rooms[rooms[i][0]] = new Room(rooms[i]) ;
      if ( rooms[i][0].indexOf('%%') != -1 )
	this.example_row_defined = true ;
    }
    if ( rooms.length == 0 )
      this.rooms['none'] = new Room([_("MSG_no_rooms"), "", "", ""]) ;
  }
  else
    this.example_row_defined = true ;
      
  for(var lin_id in lines)
  {
    if ( lines[lin_id][0].value === '' )
      continue ;
    v = lines[lin_id][this.data_col] ;
    
    room = text_to_room_and_place(v.comment)[0] ;
    if ( this.rooms[room] === undefined )
      this.rooms[room] = new Room([room]) ;
    this.rooms[room].in_comment = true ;
    
    room = text_to_room_and_place(v.value.toString())[0] ;
    if ( this.rooms[room] === undefined )
      this.rooms[room] = new Room([room]) ;
    this.rooms[room].in_value = true ;
  }
  // The list of room in alphabetical order
  this.index = [] ;
  for(var i in this.rooms)
    this.index.push(i) ;
  var r = this.rooms ;
  this.index.sort(function(a,b)
		  {
		   a = r[a].get_key() ;
		   b = r[b].get_key() ;
		   if ( a > b )
		     return 1 ;
		   if ( a < b )
		     return -1 ;
		   return 0 ;
		 }) ;
} ;

Filler.prototype.add_empty_input = function() {
  var table = document.getElementById("fill_table") ;
  var i = 0 ;
  if ( this.example_row_defined )
  {
    var cell, room ;
    for(i in this.index)
    {
      room = this.rooms[this.index[i]] ;
      cell = room.get_name() ;
      if ( ! room.created_empty )
	break ;
      if ( cell.value === '' )
	return ; // Yet an empty input
    }
  }
  if ( value === undefined )
    value = '' ;
  var room = new Room(['']) ;
  room.created_empty = true ;
  this.rooms[' empty' + i] = room ;
  this.index.splice(i, 0, ' empty' + i) ;

  var d = document.createElement('TBODY') ;
  d.innerHTML = room.html() ;
  d = d.firstChild ;
  i = Number(i) ;
  if ( table.rows[i+1] )
    table.firstChild.insertBefore(d, table.rows[i+1]) ;
  else
    table.firstChild.appendChild(d) ;
  if ( i == 0 )
    room.get_name().focus() ; // Focus on first empty input
  if ( ! this.example_row_defined ) 
    {
      this.example_row_defined = true ;
      room.get_toggle().checked = true ;
      room.get_name().value = "Darwin (%%)" ;
      room.get_name().focus() ;
      room.get_name().select() ;
      return this.add_empty_input() ;
    }
  return room ;
} ;

Filler.prototype.count_line = function(line) {
  if ( line[0].value === '' ) // No ID
    return ;
  var v = line[this.data_col] ;
  if ( this.toggles.comment )
    v = v.comment ;
  else
    v = v.value.toString() ;
  var room_and_place = text_to_room_and_place(v) ;
  var room = room_and_place[0] ;
  var place = room_and_place[1] ;
  if ( (this.toggles.modify || v === '') && line.is_filtered )
  {
    this.to_dispatch.push(line) ;
    if ( this.toggles.modify )
      this.rooms[room].nr_erased++ ;
  }
  if ( v !== '' )
    this.not_empty++ ;
  this.rooms[room].add_predefined(line.line_id, place) ;
}

Filler.prototype.rooms_get_usage = function() {
  for(var i in this.rooms)
    this.rooms[i].clear() ;
  this.to_dispatch = [] ;
  this.not_empty = 0 ;
  for(var i in lines)
    lines[i].is_filtered = false ;
  for(var i in filtered_lines)
    {
      filtered_lines[i].is_filtered = true ;
      this.count_line(filtered_lines[i]) ;
    }
  if ( this.toggles.unfiltered )
    for(var i in lines)
      if ( ! lines[i].is_filtered )
	this.count_line(lines[i]) ;
} ;

Filler.prototype.init_rooms = function() {
  var s = [] ;

  for(var i in this.index)
    {
      s.push(this.rooms[this.index[i]].html()) ;
      s.push('</tr>') ;
    }
  return s.join('') ;
} ;

function pulsing(element, state)
{
  element.className = element.className.replace(" pulsing", "")
      + (state ? " pulsing" : "") ;
}

Filler.prototype.use_a_number = function()
{
  for(var i in this.rooms)
    if ( this.rooms[i].checked && this.rooms[i].name.indexOf("%%") != -1 )
      return true ;
} ;

Filler.prototype.state_change = function()
{
  var s = '' ;
  for(var i in this.toggles)
    {
      var e = document.getElementById('select.' + i) ;
      if ( e )
	this.toggles[i] = e.selectedIndex ;
      s += i + ':' + this.toggles[i] + " " ;
    }
  for(var i in this.rooms)
    {
      this.rooms[i].checked = this.rooms[i].get_toggle().checked ;
      if ( this.rooms[i].get_places().value !== undefined )
	this.rooms[i].places = new Places(this.rooms[i].get_places().value) ;
      if ( this.rooms[i].name != this.rooms[i].get_name().value )
	{
	  this.rooms[i].name = this.rooms[i].get_name().value ;
	  this.rooms[i].checked = true ;
	  this.rooms[i].get_toggle().checked = true ;
	}
      s += i
	+ ':' + this.rooms[i].checked
	+ ':' + this.rooms[i].name
	+ ':' + this.rooms[i].places.text
	+ "\n"
      ;
    }
  if ( s == this.old_state )
    return false ;
  this.old_state = s ;
  return true ;
} ;

Filler.prototype.visible = function(room) {
  if ( ! room.in_comment && ! room.in_value )
    return true ;
  if ( this.toggles.comment )
  {
    if ( room.in_comment )
      return true ;
  }
  else
  {
    if ( room.in_value )
      return true ;
  }
} ;

Filler.prototype.highlight_option = function(option, bool) {
    document.getElementById("select." + option).style.opacity = bool ? 1 : 0.4;
} ;


Filler.prototype.nr_visible_lines = function() {
  var nr = 0 ;
  for(var room in this.rooms)
    if(this.visible(this.rooms[room]))
      nr++ ;
  return nr ;
} ;

Filler.prototype.update_html = function() {
  var feedback = document.getElementById('fill_result') ;
  if ( ! feedback )
    {
      clearInterval(this.id) ;
      return ;
    }
  if ( ! this.state_change() )
    return ;
  feedback.parentNode.parentNode.setAttribute('rowspan', this.index.length+1) ;
  var table = document.getElementById("fill_table") ;
  if ( this.toggles.comment )
    table.className = 'show_in_comment' ;
  else
    table.className = 'show_in_value' ;
  this.add_empty_input() ;
  this.rooms_get_usage() ; // Compute to_dispatch, not_empty

  pulsing(document.getElementById('select.modify'),
	  this.to_dispatch.length == 0) ;
  for(var room in this.rooms)
    pulsing(this.rooms[room].get_toggle().parentNode, false) ;
  
  var messages = [] ;

  if ( this.to_dispatch.length == 0 )
    messages.push('<div class="fill_important">' + _("MSG_fill_room_nothing")
		  + '</div>') ;

  this.rooms_to_use = [] ;
  for(var room in this.rooms)
    {
      room = this.rooms[room] ;
      if ( room.checked )
	{
	  room.nr_will_be_used = 0 ;
	  this.rooms_to_use.push(room) ;
	}
      else
	room.nr_will_be_used = '' ;
    }
  function priority_r(r) { return r.new_size() ; }
  function priority_f(r) { return r.filling() ; }
  priority = this.toggles.relative ? priority_f : priority_r ;

  this.rooms_to_use.sort(function(a,b) {return priority(a) - priority(b) ;});
  this.highlight_option("interleave", this.rooms_to_use.length >= 2) ;
  this.highlight_option("relative", this.rooms_to_use.length >= 2) ;
  this.highlight_option("unfiltered", filters.length != 0
			|| full_filter || line_filter) ;
  this.highlight_option("pad0", this.use_a_number()) ;

  var fill_value = 0 ;
  var fill_empty_value = 0 ;
  var overflow = 0 ;
  var room, place ;
  this.todo = [] ;
  if ( this.rooms_to_use.length )
    for(var i in this.to_dispatch)
    {
      room = this.rooms_to_use[0]
      if ( room.name !== '' )
	fill_value++ ;
      else
	fill_empty_value++ ;

      place = room.get_place(this.toggles.pad0) ;
      if ( place === undefined )
	overflow++ ;
      this.todo.push([room, place, i]) ;
      // Sort the rooms by filling
      for(var j = 1 ; j < this.rooms_to_use.length ; j++)
	{
	  if ( priority(this.rooms_to_use[j-1])
	     < priority(this.rooms_to_use[j]) )
	    break ;
	  var tmp = this.rooms_to_use[j-1] ;
	  this.rooms_to_use[j-1] = this.rooms_to_use[j] ;
	  this.rooms_to_use[j] = tmp ;
	}
    }
  for(var i in this.rooms)
    this.rooms[i].update_html() ;
  if ( this.to_dispatch.length != 0 && this.todo.length == 0 )
    {
      for(var room in this.rooms)
	pulsing(this.rooms[room].get_toggle().parentNode, true) ;

      messages.push('<div class="fill_important">' + _("MSG_fill_room")
		    + '</div>') ;
    }
  for(var room in this.rooms)
    {
      if ( this.rooms[room].yet_overflowed() )
	messages.push('<div class="fill_warning">'
		      + '«' + html(this.rooms[room].name) + '» '
		      + _("MSG_fill_room_overflow")
		      + '</div>') ;
    }
  if ( ! this.toggles.interleave )
    this.todo.sort(function (a, b) {
      return a[0].name > b[0].name ? 1
	: (a[0].name < b[0].name ? -1 : a[2] - b[2]) ;
    })
  if ( this.to_dispatch.length != this.todo.length
       && this.todo.length != 0 )
    alert("BUG column fill") ;
  var s = [] ;
  var unwritable = 0, problems = 0, replacements = 0, changes = 0 ;
  alert_append_start() ;
  this.todo_real = [] ;
  for(var i in this.todo)
    {
      var room = this.todo[i][0] ;
      var place = this.todo[i][1] ;
      var line = this.to_dispatch[i] ;
      var cell = line[this.data_col] ;
      var old_val = this.toggles.comment ? cell.comment : cell.value ;
      var new_val = place
	? room.name.replace('%%', place)
	: room.name.replace('%%', '???') ;
      var tip = '' ;
      if ( old_val == new_val )
	continue ;
      this.todo_real.push([new_val, line]) ;
      var classe ;
      if ( ! cell.modifiable(line, this.column) )
      {
	classe = "fill_error" ;
	tip = _("ERROR_value_not_modifiable") ;
	unwritable++ ;
      }
      else if ( place === undefined )
	{
	  classe = "fill_warning" ;
	  tip = _("MSG_fill_overflow") ;
	}
      else
	classe = "" ;
      if ( ! this.toggles.comment )
	{
	  var v = this.column.real_type.cell_test(new_val, this.column) ;
	  if ( new_val != v )
	  {
	    if ( v !== undefined )
	    {
	      tip = html(new_val) + '→' + html(v) ;
	      new_val = v ;
	      classe += " fill_replace" ;
	      replacements++ ;
	    }
	    else
	    {
	      classe += " fill_error" ;
	      problems++ ;
	      tip = alert_merged ;
	      alert_merged = '' ;
	    }
	  }
	}
      if ( tip )
	tip = '<!--INSTANTDISPLAY-->' + tip ;
      if ( old_val != new_val )
	changes++ ;
      s.push('<tr><td class="old_value">'
	     + (tip !== '' ? hidden_txt(html(old_val), tip) : html(old_val))
	     + '<td class="' + classe + '">'
	     + (tip !== '' ? hidden_txt('→', tip) : '→')
	     + '<td class="new_value">'
	     + (tip !== '' ? hidden_txt(html(new_val), tip) : html(new_val))
	     + '</tr>') ;
    }
  s = '<h3>' + _("MSG_fill_room_simulation")
    + '</h3><table class="simulation">'
    + (s.length == 0
       ? '<tr><td colspan="2">' + _("MSG_fill_no_change") + '</tr>'
       : '<tr><td class="old_value">' + _("MSG_fill_room_old_value")
       + '<td>'
       + '<td class="new_value">' + _("MSG_fill_room_new_value") + '</tr>'
       + ''.join(s)
      )
    + '</table>' ;
  
  if ( s === '' )
    messages.push('<div class="fill_important">'
		  + _("MSG_fill_no_change") + '</div>') ;
  if ( fill_empty_value && fill_value )
    {
      messages.push('<div class="fill_warning">'
		    + _("MSG_fill_empty_not_empty") + '</div>') ;
      for(var room in this.rooms)
	{
	  if ( this.rooms[room].name === ''
	       && this.rooms[room].checked
	       && fill_empty_value == 1
	     )
	      pulsing(this.rooms[room].get_toggle().parentNode, true) ;
	  else if ( this.rooms[room].name !== ''
		    && fill_value == 1
		    && this.rooms[room].checked )
	    pulsing(this.rooms[room].get_toggle().parentNode, true) ;
	}
    }
  if ( overflow )
    messages.push('<div class="fill_warning">' + overflow + ' '
		  + _("MSG_fill_overflow") + '</div>') ;
  if ( unwritable )
    messages.push('<div class="fill_error">' + unwritable + ' '
		  + _("MSG_fill_unwritable") + '</div>') ;
  if ( problems )
      messages.push('<div class="fill_error">' + _("MSG_fill_bad_format")
		    + '</div>') ;
  if ( replacements )
      messages.push('<div class="fill_replace">' + replacements
		    + _("MSG_fill_replace") + '</div>') ;
  if ( changes )
      messages.push('<div class="fill_room_messages">' + changes + ' '
		    + _("MSG_modifiable_cells") + '</div>') ;
  if ( this.not_empty && ! this.toggles.modify )
      messages.push('<div class="fill_room_messages">' + this.not_empty + ' '
		    + _("MSG_unchanged_cells") + '</div>') ;
  this.highlight_option("modify", this.not_empty > 0) ;
  s = '<h3>' + _("MSG_fill_room_message")
    + '</h3><div class="fill_room_messages">'
    + (messages.length == 0 // Never true
       ? _("MSG_fill_room_message_none")
       : messages.join('')
      )
    + '</div>' + s + '<h3>' + _("MSG_fill_room_go")
    + '</h3>'
    + caution_message(true)
    + '<button onclick="Filler.filler.do_fill()">'
    + ( this.toggles.comment
	? _("MSG_fill_the_comments")
	: _("MSG_fill_the_values")
      ) + '</button>' ;
  feedback.innerHTML = s ;
  alert_append_stop() ;
} ;

Filler.prototype.do_fill = function()
{
  popup_close() ;
  alert_append_start() ;
  for(var d in this.todo_real)
  {
    var new_val = this.todo_real[d][0] ;
    var line = this.todo_real[d][1] ;
    if ( this.toggles.comment )
      comment_change(line.line_id, this.data_col, new_val) ;
    else
      cell_set_value_real(line.line_id, this.data_col, new_val) ;
  }
  alert_append_stop() ;
  this.column.need_update = true ;
  update_columns() ;
  table_fill() ;
  Filler.last_state = this ; // Only on successful filling
} ;

/****************************************************************************/

function fill_column(redo)
{
  Filler.filler = new Filler(redo == 'redo' ? Filler.last_state : undefined) ;
  var id = '<!--INSTANTDISPLAY-->' ;
  create_popup('fill_column_div',
	       _("TITLE_fill_before")
	       + the_current_cell.column.title + _("TITLE_fill_after")
	       + ' (' + _('B_' + the_current_cell.column.real_type.title) + ')'
	       ,
	       '<div id="fill_is_safe">' + _('MSG_fill_safe') + '</div>'
	       + '<table id="fill_table" onmousemove="if ( the_event(event).target.className != \'text\' ) hide_the_tip_real(true)">'
	       + '<tr>'
	       + '<th>' + hidden_txt(_("COL_TITLE_fill_used"),
				     id + _("TIP_TITLE_fill_used"))
	       + '<th>' + hidden_txt(_("COL_TITLE_fill_use"),
				     id + _("TIP_TITLE_fill_use"))
	       + '<th>' + hidden_txt(_("COL_TITLE_fill_total"),
				     id + _("TIP_TITLE_fill_total"))
	       + '<th>' + hidden_txt(_('?'),
				     id + _("TIP_TITLE_fill_?"))
	       + '<th class="nowrap">' + hidden_txt(_("COL_TITLE_fill_name"),
				     id + _("TIP_TITLE_fill_name"))
	       + '<th>' + hidden_txt(_("COL_TITLE_fill_possible"),
				     id + _("TIP_TITLE_fill_possible"))
	       + '<td class="fill_result" rowspan="'
	       + Filler.filler.index.length
	       + '">'
               + '<div class="fill_column_right">'
	       + '<h3 style="clear: both; margin-top: 0px">'
	       + _('MSG_fill') + '</h3>'
	       + Filler.filler.menu()
               + '<div id="fill_result"></div>'
	       + '</div></tr>'
	       + Filler.filler.init_rooms()
	       + '</table>',
	       '',
	       false
	       ) ;
  if ( redo && Filler.last_state )
    {
      for(var room in Filler.filler.rooms)
	{
	  room = Filler.filler.rooms[room] ;
	  room.get_toggle().checked = room.checked ;
	}
    }
  Filler.filler.update_html() ;
}
