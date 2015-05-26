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

/****************************************************************************/

function Places(text)
{
  this.text = text ;
  this.intervals = [] ; // first and last value are included
  this.parse(text) ;
  if ( this.intervals.length )
    this.length = this.intervals[this.intervals.length-1][1].toString().length;
  this.nr_places = 0 ;
  for(var i in this.intervals)
    this.nr_places += this.intervals[i][1] - this.intervals[i][0] + 1 ;
  this.init() ;
}

Places.prototype.init = function(text) {
  this.interval_number = 0 ;
  this.last_number = this.intervals[0] ? this.intervals[0][0] - 1 : 0 ;
} ;

Places.prototype.next = function(padding) {
  var from_to = this.intervals[this.interval_number] ;
  if ( ! from_to )
    return ;
  if ( this.last_number === from_to[1] )
    {
      this.interval_number++ ;
      if ( this.intervals[this.interval_number] )
	this.last_number = this.intervals[this.interval_number][0] ;
      else
	return ;
    }
  else
    this.last_number++ ;

  n = this.last_number.toString() ;

  if ( padding !== '' )
  {
    while ( n.length < this.length )
      n = padding + n ;
  }
  return n ;
} ;

Places.prototype.parse = function(text) {
  var from, to ;

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
	  if ( text[i] === '' )
	    continue ;
	  from = Number(text[i]) ;
	  if ( from < 0 )
	    {
	      from = -from ;
	      for(var j in this.intervals)
		{
		  if ( this.intervals[j][0] > from ) // before interval
		    continue ;
		  if ( this.intervals[j][1] < from ) // after interval
		    continue ;
		  if ( this.intervals[j][0] == from )
		    this.intervals[j][0]++ ; // 1-10 -1
		  else if ( this.intervals[j][1] == from )
		    this.intervals[j][1]-- ; // 1-10 -10
		  else if ( this.intervals[j][1] > i ) // in interval
		  {
		    this.intervals.splice(Number(j)+1, 0,
					  [from+1, this.intervals[j][1]]) ;
		    this.intervals[j][1] = from - 1 ;
		  }
		  break ;
		}
	      continue ;
	    }
	  to = from ;
	}
      
      if ( isNaN(from) || isNaN(to) )
	continue ;
      if ( from > to )
	continue ;
      for(var j=0; j < this.intervals.length; j++)
	if ( this.intervals[j][1] > from )
	  break ;
      this.intervals.splice(j, 0, [from, to]) ;
    }
} ;
if ( new Places("31-35 11-15 21-25 -21 -25 -23 -11 -35  9 19 29 39"
	       ).intervals.toString()
     != "9,9,12,15,19,19,22,22,24,24,29,29,31,34,39,39" )
  alert("BUG") ;

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
  this.places.init() ;       // Goto before the first place
} ;

Room.prototype.add_predefined = function(line_id, place)
{
  this.nr_used++ ;
  this.number_used[place] = true ;
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
    + '"><td>' + cb
    + '<td class="room_used">'
    + '<td class="room_used">'
    + '<td class="room_name">' + name
    + (this.comment ?
       '<div class="room_comment">'
       + (this.url ? '<a target="_blank" href="' + this.url + '">' : '')
       + html(this.comment)
       + (this.url ? '</a>' : '')
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
  return this.get_tr().childNodes[0].firstChild ;
} ;
Room.prototype.get_nr_used = function() {
  return this.get_tr().childNodes[1] ;
} ;
Room.prototype.get_nr_will_be_used = function() {
  return this.get_tr().childNodes[2] ;
} ;
Room.prototype.get_name = function(i) {
  return this.get_tr().childNodes[3].firstChild ;
} ;
Room.prototype.get_places = function(i) {
  return this.get_tr().childNodes[4].firstChild ;
} ;
Room.prototype.get_comment = function(i) {
  return this.get_tr().childNodes[3].childNodes[1] ;
} ;

Room.prototype.update_html = function()
{
  this.get_nr_used().innerHTML = this.nr_used ? this.nr_used : ' ' ;
  var total = this.nr_used + this.nr_will_be_used ;
  var overflow = total - this.places.nr_places ;
  this.get_nr_will_be_used().innerHTML = this.nr_will_be_used
    ? this.nr_will_be_used + (
      overflow > 0
	? '<span class="fill_warning">(' + overflow + ')</span>'
	: '')
  : ' ' ;
} ;


/****************************************************************************/

function Filler()
{
  this.toggles = {
    'modify': 0,
    'interleave': 0,
    'unfiltered': 1,
    'comment': 0,
    'pad0': 1
  } ;
  this.column = the_current_cell.column ;
  this.data_col = the_current_cell.column.data_col ;
  this.create_rooms() ;
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
	+ '<option' + (! this.toggles[key] ? ' selected': "")
	+ '>' + _("TIP_fill_no_" + key) + '</option>'
	+ '<option' + (this.toggles[key] ? ' selected': "")
	+ '>' + _("TIP_fill_" + key) + '</option>'
	+ '</select>' ;
    }
  s += '</div>' ;
  return s ;
} ;

//  if ( column.real_type.title != 'Text' )


function text_to_room_and_place(text)
{
  var m = text.match(/(.*[^0-9.])([0-9]+)(.*)/) ;
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
  for(var i in rooms)
    {
      this.rooms[rooms[i][0]] = new Room(rooms[i]) ;
      if ( rooms[i][0].indexOf('%%') != -1 )
	this.example_row_defined = true ;
    }
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

Filler.prototype.rooms_get_usage = function() {
  var v ;
  for(var i in this.rooms)
    this.rooms[i].clear() ;
  for(var i in lines)
    lines[i].is_filtered = false ;
  for(var i in filtered_lines)
    filtered_lines[i].is_filtered = true ;
  var check = this.toggles.unfiltered ? lines : filtered_lines ;
  this.nr_to_dispatch = 0 ;
  for(var i in check)
  {
    if ( check[i][0].value === '' )
      continue ;
    if ( this.toggles.modify && check[i].is_filtered )
      {
	// All the filtered values are going to be erased
	this.nr_to_dispatch++ ;
	continue
      }
    v = check[i][this.data_col] ;
    if ( this.toggles.comment )
      v = v.comment ;
    else
      v = v.value.toString() ;
    if ( v === '' && check[i].is_filtered )
      this.nr_to_dispatch++ ;
    var room_and_place = text_to_room_and_place(v) ;
    var room = room_and_place[0] ;
    var place = room_and_place[1] ;
    this.rooms[room].add_predefined(check[i].line_id, place) ;
  }
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
  feedback.parentNode.parentNode.style.height =
    feedback.parentNode.style.height =
    feedback.style.height = 1.2 * this.nr_visible_lines() + 'em' ;
  var table = document.getElementById("fill_table") ;
  if ( this.toggles.comment )
    table.className = 'show_in_comment' ;
  else
    table.className = 'show_in_value' ;
  this.add_empty_input() ;
  this.rooms_get_usage() ;
  for(var i in this.rooms)
    this.rooms[i].update_html() ;
  var to_dispatch = this.nr_to_dispatch ;

  pulsing(document.getElementById('select.modify'), to_dispatch == 0) ;
  for(var room in this.rooms)
    pulsing(this.rooms[room].get_toggle().parentNode, false) ;
  var message = '<p><b>' + _("MSG_fill_room_message") + '</b>' ;
  if ( to_dispatch == 0 )
    {
      feedback.innerHTML = message
	+ '<div class="fill_important">' + _("MSG_fill_room_nothing")
	+ '</div>' ;
      return ;
    }

  var full_size = 0 ;
  this.nr_rooms_used = 0 ;
  for(var room in this.rooms)
    {
      room = this.rooms[room] ;
      if ( room.checked )
	{
	  full_size += room.places.nr_places ;
	  room.nr_will_be_used = 0 ;
	  if ( room.name !== '' )
	    to_dispatch += room.nr_used ;
	  this.nr_rooms_used++ ;
	}
      else
	room.nr_will_be_used = '' ;
    }
  this.dispatch = [] ;
  var fill_empty_value = 0 ;
  var fill_value = 0 ;
  var overflow = 0 ;

  for(var room in this.index)
    {
      var room = this.rooms[this.index[room]] ;
      if ( ! room.checked )
	continue ;
      var nr_used = (room.name === '' ? 0 : room.nr_used) ;
      room.nr_will_be_used = Math.max(0,
				      Math.round(to_dispatch
						 * room.places.nr_places
						 / full_size) - nr_used) ;
      if ( 0 )
	console.log('to_dispatch=' + to_dispatch
		    + ' nr_used=' + room.nr_used
		    + ' will_be_used=' + room.nr_will_be_used
		    + ' full_size=' + full_size) ;
      to_dispatch -= room.nr_will_be_used + nr_used ;
      full_size -= room.places.nr_places ;
      if ( room.name !== '' )
	 fill_value++ ;
      else
	fill_empty_value++ ;

      for(var j=0; j<room.nr_will_be_used; j++)
	{
	  // Search an unused place number
	  var place ;
	  do
	    {
	      place = room.places.next(this.toggles.pad0 ? '0' : ' ') ;
	      if ( place === undefined )
		break ;
	    }
	  while( room.number_used[place] ) ;
	  if ( place === undefined )
	    overflow++ ;
	  else
	    room.number_used[place] = true ;
	  this.dispatch.push([this.toggles.interleave
			      ? j * this.nr_rooms_used
			      : 0,
			      place === undefined
			      ? room.name.replace('%%', '???')
			      : room.name.replace('%%', place),
			      place]) ;
	}
      room.update_html() ;
    }
  if ( this.toggles.interleave )
    this.dispatch.sort(function (a, b) { return a[0] - b[0] ; }) ;
  if ( this.dispatch.length == 0 )
    {
      for(var room in this.rooms)
	pulsing(this.rooms[room].get_toggle().parentNode, true) ;

     feedback.innerHTML = message + '<div class="fill_important">'
	+ _("MSG_fill_room") + '</div>' ;
      return ;
    }

  var j = 0 ;
  for(var i in filtered_lines)
    {
      if ( filtered_lines[i][0].value === '' )
	continue ;
      var c = filtered_lines[i][this.data_col] ;
      var v = this.toggles.comment ? c.comment : c.value ;
      if ( this.toggles.modify )
	this.dispatch[j++].push(filtered_lines[i]) ;
      else
	if ( v === '' )
	  this.dispatch[j++].push(filtered_lines[i]) ;
    }
  if ( j != this.dispatch.length )
    {
      console.log(filtered_lines.length) ;
      console.log(this.dispatch) ;
      console.log(j) ;
      alert("BUG columnfill") ;
      return ;
    }
  
  var s = [] ;
  var unwritable = 0 ;
  alert_append_start() ;
  for(var i in this.dispatch)
    {
      var cell = this.dispatch[i][3][this.data_col] ;
      var old_val = this.toggles.comment ? cell.comment : cell.value ;
      var new_val = this.dispatch[i][1] ;
      if ( old_val == new_val )
	continue ;
      var classe ;
      if ( ! cell.modifiable(this.column) )
      {
	classe = "fill_error" ;
	unwritable++ ;
      }
      else if ( this.dispatch[i][2] === undefined )
	classe = "fill_warning" ;
      else
	classe = "" ;
      if ( ! this.toggles.comment )
	{
	  var v = this.column.real_type.cell_test(new_val, this.column) ;
	  if ( new_val != v )
	  {
	    if ( v !== undefined )
	    {
	      new_val = v ;
	      classe += " fill_replace" ;
	    }
	    else
	    {
	      classe += " fill_error" ;
	    }
	  }
	}
      s.push('<div class="' + classe + '">'
	     + html(old_val) + '<tt>→</tt>' + html(new_val) + '</div>') ;
    }
  s = '<p><b>' + _("MSG_fill_room_simulation") + '</b>' + ''.join(s) ;
  if ( this.dispatch.length === 0 )
    s = message + '<div class="fill_important">'
    + _("MSG_fill_room") + '</div>' ;
  else if ( s === '' )
    s = message + '<div class="fill_important">'
    + _("MSG_fill_no_change") + '</div>' ;
  if ( fill_empty_value && fill_value )
    {
      s = message + '<div class="fill_warning">'
	+ _("MSG_fill_empty_not_empty") + '</div>' + s ;
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
    s = message + '<div class="fill_warning">'
    + overflow + ' ' + _("MSG_fill_overflow") + '</div>' + s ;
  if ( unwritable )
    s = message + '<div class="fill_error">'
    + unwritable + ' '+ _("MSG_fill_unwritable") + '</div>' + s ;
  if ( alert_merged !== '' )
    {
      s = message + '<div class="fill_error">'
	+ _("MSG_fill_bad_format")+'</div>' + s ;
      alert_merged = '' ;
    }
    s += '<p><b>' + _("MSG_fill_room_go")
    + '</b><p><button onclick="Filler.filler.do_fill()">'
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
  for(var d in this.dispatch)
  {
    d = this.dispatch[d] ;
    var line = d[3] ;
    var cell = line[this.data_col] ;
    var old_val = this.toggles.comment ? cell.comment : cell.value ;
    var new_val = d[1] ;
    if ( old_val == new_val )
      continue ;
    if ( this.toggles.comment )
      comment_change(line.line_id, this.data_col, new_val) ;
    else
      cell_set_value_real(line.line_id, this.data_col, new_val) ;
  }
  alert_append_stop() ;
  this.column.need_update = true ;
  update_columns() ;
  table_fill() ;
} ;

/****************************************************************************/

function fill_column()
{
  // MSG_fill_remove_empty MSG_fill TAB_fill_clear MSG_fill_clear TAB_fill_one MSG_fill_one MSG_fill_multiple MSG_fill_numbers COL_TITLE_room_name MSG_fill_before B_fill B_fill_comments MSG_fill_after MSG_fill_room_text
  Filler.filler = new Filler() ;
  var id = '<!--INSTANTDISPLAY-->' ;
  create_popup('fill_column_div',
	       _("TITLE_fill_before")
	       + the_current_cell.column.title + _("TITLE_fill_after"),
	       caution_message()
	       + '<div id="fill_is_safe">' + _('MSG_fill_safe') + '</div>'
	       + '<table id="fill_table" onmousemove="if ( the_event(event).target.className != \'text\' ) hide_the_tip_real(true)">'
	       + '<tr>'
	       + '<th>' + hidden_txt(_('?'),
				     id + _("TIP_TITLE_fill_?"))
	       + '<th>' + hidden_txt(_("COL_TITLE_fill_used"),
				     id + _("TIP_TITLE_fill_used"))
	       + '<th>' + hidden_txt(_("COL_TITLE_fill_use"),
				     id + _("TIP_TITLE_fill_use"))
	       + '<th>' + hidden_txt(_("COL_TITLE_fill_name"),
				     id + _("TIP_TITLE_fill_name"))
	       + '<th>' + hidden_txt(_("COL_TITLE_fill_possible"),
				     id + _("TIP_TITLE_fill_possible"))
	       + '<td class="fill_result" rowspan="'
	       + Filler.filler.index.length
	       + '">'
               + '<div class="fill_column_right"><b>'
               + _('MSG_fill') + '</b>'
	       + Filler.filler.menu()
               + '<div id="fill_result"></div>'
	       + '</div></tr>'
	       + Filler.filler.init_rooms()
	       + '</table>',
	       '',
	       false
	       ) ;
}
