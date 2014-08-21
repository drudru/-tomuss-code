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

var default_title = "Séance" ;

function update_filters(unused_column)
{
  filters = [] ; // GLOBAL
  for(var data_col in columns)
    {
      var column = columns[data_col] ;
      if ( column.filter === '' )
	continue ;
      filters.push([column.real_filter, data_col, column]) ;
    }
  line_offset = 0 ;

  return true ;
}


var alert_merged = false ;

function alert_append_start()
{
  alert_merged = '' ;
}

function alert_append_stop()
{
  if ( alert_merged )
    alert(alert_merged) ;
  alert_merged = false ;
}

function alert_append(x)
{
  if ( alert_merged === false )
    alert(x) ;
  else
    alert_merged += '\n' + x ;
}

/******************************************************************************
When an header change, update cells
******************************************************************************/

function update_column_recursive(column, line)
{
  var type = column.real_type ;

  if ( column.update_done )
    return ;
  column.update_done = true ;

  if ( ! column.is_computed() )
    return ;

  for(var c in column.average_columns)
    {
      update_column_recursive(columns[column.average_columns[c]], line) ;
      column.need_update |= columns[column.average_columns[c]].need_update ;
    }
  
  if ( column.need_update )
    {
      if ( line === undefined )
	{
	  for(var line_id in lines)
	    if ( ! line_empty(lines[line_id]) )
	      compute_cell_safe(column.data_col, lines[line_id],
				type.cell_compute) ;
	}
      else
	{
	  compute_cell_safe(column.data_col, line, type.cell_compute) ;
	}
    }

  return ;
}

function update_columns(line)
{
  var need_update = false ;
  var data_col ;

  for(data_col in columns)
    columns[data_col].update_done = false ;

  for(data_col in columns)
    update_column_recursive(columns[data_col], line) ;

  for(data_col in columns)
    {
      need_update |= columns[data_col].need_update ;
      columns[data_col].need_update = false ;
    }
  return need_update ;
}

// Give focus to a newly created focus (redondant but necessary)
function my_focus(event)
{
  event = the_event(event) ;
  if ( event.target )
    {
      event.target.focus() ;
      if ( event.target.select !== undefined )
	event.target.select() ;
      event.target.onmouseup = function() {} ;
    }
}

/******************************************************************************
Column actions
******************************************************************************/

function column_title_to_data_col(title)
{
  for(var data_col in columns)
    if ( columns[data_col].title == title )
      return data_col ;
}

function column_used_in_average(name)
{
  for(var column in columns)
    {
      column = columns[column] ;
      if ( ! column_modifiable_attr('columns', column) )
	continue ; // Not used
      for(var use in column.average_from)
	if ( column.average_from[use] == name )
	  return column.title ;
    }
  return false ;
}

/******************************************************************************
Column Types
******************************************************************************/

function index_to_type(i)
{
  // alert('index_to_type ' + i + ' ' + types[i].title);
  return types[i].title ;
}

var types = [] ;

function test_nothing(value, column)
{
  return value ;
}

function test_float(value, column)
{
  return Number(value) ;
}

function unmodifiable(value, column)
{
  // It was "return '' ;" before the 2010-09-13
  // It was modified in order to make the 'import_columns' function work.
  return value ;
}

