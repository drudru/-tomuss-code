// -*- coding: utf-8 -*-
/*
    TOMUSS: The Online Multi User Simple Spreadsheet
    Copyright (C) 2017 Thierry EXCOFFIER, Universite Claude Bernard

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

var table_create_slot = ["TD", "TP", "", "", "", "", "", ""] ;

function table_create_columns(columns_list)
{
  for(var i in columns_list)
  {
    i = columns_list[i] ;
    var column = columns[add_empty_columns()] ;

    column_attr_set(column, 'title', i.title) ;
    column_attr_set(column, 'type', i.type, undefined, true) ;
    for(var k in i)
      if ( k != "title" && k != "type" )
	column_attr_set(column, k, i[k]) ;
  }
  update_columns() ;
  table_fill(true, true, true) ;
  popup_close() ;
}

function table_create_compute_columns()
{
  var nr = Number(document.getElementById('table_create_nr').value) ;
  var c = [] ;
  var used = {} ;
  var all = [] ;
  
  for(var n=1 ; n <= nr ; n++)
  {
    for(var i in table_create_slot)
    {
      var title = document.getElementById('table_create_'+i).value ;
      if ( title !== '' )
      {
	title = title.replace(/ /g, '_') + n ;
	all.push(title) ;
	if ( used[title] === undefined
	     && data_col_from_col_title(title) === undefined )
	{
	  c.push({title: title, type: "Prst"}) ;
	  used[title] = true ;
	}
      }
    }
  }
  if ( data_col_from_col_title("#" + abi) === undefined )
    c.splice(0, 0,
	     {title: "#" + abi, type: "Nmbr", test_filter: abi, rounding: 1,
	      columns: all.join(' ')}) ;
  return c ;
}

function table_create_columns_do()
{
  table_create_columns(table_create_compute_columns()) ;
}

function table_create_update()
{
  var c = table_create_compute_columns() ;
  var s = [] ;
  for(var i in c)
    s.push(c[i].title) ;
  document.getElementById('table_create_button').innerHTML =
    _("MSG_table_create_do") + html(s.join(', ')) ;
}

function table_create()
{
  var c = [] ;
  for(var i in table_create_slot)
    c.push('<input id="table_create_' + i
	   + '" style="width:4em" value="' + table_create_slot[i]  + '">') ;
  var t = caution_message()
      + '<div onkeyup="table_create_update()">'
      + _("MSG_table_create_slot") + "<br>"
      + c.join(' ') + '<br>'
      + _("MSG_table_create_number")
      + '<input id="table_create_nr" value="4" size="2" maxlength="2"><br>'
      + '<button id="table_create_button" onclick="table_create_columns_do()">'
      + '</button> '
      + '</div>'
  ;
  create_popup("popup_tc", _("MSG_table_create"), t, '', false) ;
  table_create_update() ;
}


