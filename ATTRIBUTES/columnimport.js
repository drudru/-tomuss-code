// -*- coding: utf-8 -*-
/*
  TOMUSS: The Online Multi User Simple Spreadsheet
  Copyright (C) 2011-2013 Thierry EXCOFFIER, Universite Claude Bernard

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

function import_column()
{
  var m = '' ;

  if ( nr_not_empty_lines !== 0 )
    m = "<small>" + _("MSG_columnimport_empty") + "</small>" ;
  else
      m = '<small><a href="javascript:full_import()">'
	+ _("MSG_columnimport_link") + '</a></small>' ;

  var t = caution_message() ;
  if ( the_current_cell.data_col === 0 )
      t += _("MSG_columnimport_before")
	+ '<BUTTON OnClick="import_column_do();">'
	+ _("MSG_columnimport_button")+ '</BUTTON>'
	+ '/<BUTTON OnClick="import_column_do(true);">'
	+ _("MSG_columnimport_button_comments") + '</BUTTON> '
	+ _("MSG_columnimport_after") ;
  else
      t += _("MSG_columnimport_before2")
	+ '<BUTTON OnClick="import_column_do();">'
	+ _("MSG_columnimport_button2") + '</BUTTON>'
	+ '/<BUTTON OnClick="import_column_do(true);">'
	+ _("MSG_columnimport_button_comments") + '</BUTTON> '
	+ _("MSG_columnimport_after2") ;
  
  create_popup('import_div',
	       _("MSG_columnimport_title") + the_current_cell.column.title,
	       t, m) ;
}

function import_column_do(comments)
{
  var multiline = popup_value() ;
  var column = popup_column() ;
  var data_col = column.data_col ;

  if ( column_empty(data_col) && column.the_local_id !== undefined )
    {
      create_column(column) ;
    }

  var line_id ;
  var replace = '' ;
  var todo = [] ;
  var i ;
  var problems = '' ;

  if ( data_col === 0 && !comments )
    {
      // Import in ID column
      for(i in multiline)
	{
	  if ( multiline[i] === '' )
	    continue ;
	  var m = multiline[i].split(/[\t ]+/) ;
	  if ( m.length != 1 )
	    {
	      problems += _("MSG_columnimport_add") + m[0]
		+ _("MSG_columnimport_instead_of") + multiline[i] + '\n' ;
	      continue ;
	    }
	  m[0] = login_to_id(m[0]) ;
	  if ( login_to_line_id(m[0]) !== undefined )
	    {
	      problems += _("MSG_columnimport_yet") + m[0] + "\n";
	      continue ;
	    }
	  replace += _("MSG_columnimport_add2") + ' ' + m[0] + ' ' ;
	  todo.push([-1, 0, m[0]]) ;
	}
      if ( problems !== '' )
	{
	  element_focused = undefined ;
	  if ( ! confirm(problems + '\n' + _("MSG_columnimport_confirm")) )
	      return ;
	}
    }
  else
    {
      /* Test 'copy' content */
      var val ;
      var twin = [] ;
      for(i in multiline)
	{
	  if ( multiline[i] === '' )
	    continue ;
	  var login = multiline[i].replace(/[\t ].*/, '') ;
	  var value = multiline[i].replace(RegExp(login + '[\t ]*'), '') ;
	  if ( value.replace )
	    value = value.replace(/⏎/g, '\n') ;
	  line_id = login_to_line_id(login_to_id(login)) ;
	  if ( line_id === undefined )
	    {
	      replace += login + _("MSG_columnimport_not_found") + value+'\n';
	      continue ;
	    }
	  if ( comments )
	    val = lines[line_id][data_col].comment ;
	  else
	    val = lines[line_id][data_col].value ;
	  if ( val !== '' && value !== '' && a_float(val) == a_float(value) )
	    continue ; // Import same float value
	  if ( val === value )
	    continue ; // Import same string value
	  if ( val !== '' )
	    replace += lines[line_id][0].value+' : '+ val +' ==> '+value+'\n';
	  if ( twin[line_id] !== undefined )
	    {
	      replace += login + _("MSG_columnimport_multiple") + '\n' ;
	      continue ;
	    }
	  twin[line_id] = value ;
	  todo.push([line_id, data_col, value]) ;
	}
    }

  if ( replace !== '' )
    {
      element_focused = undefined ;
      if ( ! confirm(_("MSG_columnimport_confirm") + "\n" + replace) )
	return ;
    }
  alert_append_start() ;
  for(i in todo)
    {
      i = todo[i] ;
      if ( i[0] == -1 )
	i[0] = add_a_new_line() ;
      i[2] = decode_lf_tab(i[2]) ;
      if ( comments )
	comment_change(i[0], i[1], i[2]) ;
      else
	cell_set_value_real(i[0], i[1], i[2]) ;
    }
  alert_append_stop() ;

  popup_close() ;
  column.need_update = true ;
  update_columns() ;
  table_fill() ;
}

function full_import()
{
  var import_lines = popup_value() ;
  var line, nr_cols, new_lines, new_lines_id ;
  new_lines = [] ;
  for(var a in import_lines)
    {
      line = parseLineCSV(import_lines[a]) ;
      if ( nr_cols === undefined )
	nr_cols = line.length ;
      else
	if ( line.length > nr_cols )
	  {
	    alert(_("MSG_columnimport_max_first") + '\n' + line) ;
	    return ;
	  }
	else
	  {
	    while( line.length != nr_cols )
	      line.push('') ;
	  }
      new_lines.push(line) ;
    }
  if ( ! confirm(_("MSG_columnimport_confirm") + "\n"
		 + new_lines.length + _("MSG_columnimport_lines")
		 + nr_cols + _("MSG_columnimport_columns")
		 + (new_lines.length*nr_cols)/10+ _("MSG_columnimport_seconds")
		) )
    return ;

  alert_append_start() ;
  for(var data_col=0; data_col < nr_cols; data_col++)
    {
      if ( columns[data_col] === undefined )
	add_empty_column() ;
      if ( columns[data_col].the_local_id !== undefined ) // Just created
	{
	  column_attr_set(columns[data_col], 'type', 'Text') ;
	  // column_attr_set(columns[data_col], 'title', 'csv_' + data_col) ;
	  create_column(columns[data_col]) ;
	}
    }
  var cls = column_list(0, columns.length) ;
  for(line in new_lines)
    {
      add_a_new_line(line.toString()) ;
      // From right to left in order to not have a race between
      // the firstname and surname stored from the CSV and the sames
      // extracted from database.
      // If the race is lost, the user try to write a system computed data
      // and an error is displayed (one for each race lost)
      for(var data_col=nr_cols-1 ; data_col >= 0 ; data_col-- )
	cell_set_value_real(line, cls[data_col].data_col,
			    decode_lf_tab(new_lines[line][data_col])) ;
    }
  alert_append_stop() ;

  the_current_cell.jump(nr_headers,0,false,0,0) ;
  popup_close() ;
  table_init() ;
  table_fill(false, true) ;
}
