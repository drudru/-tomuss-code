// -*- coding: utf-8 -*-
/*
    TOMUSS: The Online Multi User Simple Spreadsheet
    Copyright (C) 2008-2014 Thierry EXCOFFIER, Universite Claude Bernard

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


/* Check of the 'type' cell in the header. */

function type_title_to_type(title)
{
  for(var v in types)
    if ( types[v].title == title )
      return types[v] ;
  // alert_append('bug type_title_to_type : ' + title);
}

function compile_filter_generic(value, column, error_if_hidden)
{
  var typ ;
  if ( column )
    column_type = column.type.name ;
  else
    column_type = 'Text' ;
  var g = new Filter(value, my_identity, column_type) ;
  if ( error_if_hidden )
    {
      var used = g.other_data_col() ;
      for(var i in used)
      {
	if ( ! columns[used[i]].is_visible() )
	{
	  g.errors[html('«' + columns[used[i]].title) + '» '
		   + _("MSG_depends_on_invisible")] = true ;
	}
      }
    }
  return g.compiled_js() ;
}

function set_filter_generic(value, column)
{
  column.real_filter = compile_filter_generic(value, column) ;
  column.filter_error = column.real_filter.errors ;
  column_update_option('filter', value) ;
  return value ;
}

function cell_select(event)
{
  event = the_event(event) ;
  stop_event(event) ;
  the_current_cell.change() ;
  _d('cell select');
  cell_goto(the_td(event), false) ;
}

function text_format(c)
{
  return c ;
}

function student_input(column)
{
  return '_cell(this,\'' + url + '/=' + ticket + '/' + year + '/' + semester
    + '/' + DisplayGrades.ue.ue + '/cell/' + column.the_id
    + '/' + DisplayGrades.ue.line_id + "','" + column.type
    + "','" + column.minmax + '\');' ;
}

function text_format_suivi()
{
  if ( cell_modifiable_on_suivi() )
    return '<input class="hidden" onkeypress="if ( the_event(event).keyCode == 13 ) '
    + student_input(DisplayGrades.column)
    + '" value="' + encode_value(DisplayGrades.value.toString())
    + '"></input> <small style="font-size:80%">' + _("MSG_enter") + '</small>';

  var v = html(DisplayGrades.value.toString()).replace(/\n/g,'<br>') ;
  // To avoid non breaking long strings, replace _ by spaces
  if ( v.indexOf(' ') == -1 && v.replace(/[^_]/g, '').length > 5 )
    v = v.replace(/_/g, ' ') ;
  return v ;
}

function ___NAME__()
{
  types.push({title: '__NAME__',
		 tip_column_title: __TIP_COLUMN_TITLE__,
		 tip_filter: __TIP_FILTER__,
		 tip_cell: __TIP_CELL__,
		 cell_test: __CELL_TEST__,
		 cell_completions: __CELL_COMPLETIONS__,
		 cell_compute: __CELL_COMPUTE__,   
		 cell_is_modifiable: __CELL_IS_MODIFIABLE__,   
		 onmousedown: __ONMOUSEDOWN__,
		 formatte: __FORMATTE__,
		 formatte_suivi: __FORMATTE_SUIVI__,
                 should_be_a_float: __SHOULD_BE_A_FLOAT__,
	         type_type: __TYPE_TYPE__,
	         type_change: __TYPE_CHANGE__,
	         human_priority: __HUMAN_PRIORITY__
		 }) ;
  types[types.length-1].index = types.length - 1 ;
  return types[types.length-1] ;
}

