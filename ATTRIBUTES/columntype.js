// -*- coding: utf-8 -*-
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

function set_type(value, column, xcolumn_attr)
{
  var checked = type_title_to_type(value) ;

  if ( column.real_type
       && column.real_type.cell_compute !== undefined
       && checked.cell_compute === undefined
       && the_current_cell.line[column.data_col]._save !== undefined
       )
	{
	  // Restore uncomputed values. XXX some may missing if never in client
	  for(var line in lines)
	    lines[line][column.data_col].restore() ;
	  table_fill(false, false, true) ;
	}
  if ( column.real_type
       && column.real_type.cell_compute === undefined
       && checked.cell_compute !== undefined )
    {
      /* Save values */
      for(var line in lines)
	lines[line][column.data_col].save() ;
    }
  column.real_type = checked ;
  column.need_update = true ;

  if ( xcolumn_attr === false && column.columns === '' )
    {
	// Only here on local user interaction
	var use = _('B_' + column.real_type.title).split("(")[1] ;
	if ( use == 'ID)' )
	    column_attr_set(column, 'columns', 'ID') ;
    }

  return value ;
}

function popup_type_choice(t)
{
  var type = t.title ;
  var e = hidden_txt('<a href="javascript:popup_type_choosed(\''
		     + type + '\')">'
		     + _('B_'+type).replace(/(\(.*\))/,
					    '<small><small>$1</small></small>')
		     + '</a>',
		     _('H_' + type)) ;
  if ( type === 'Note' || type === 'Prst' || type == 'Moy' )
    e = '<b>' + e + '</b>' ;
  return e ;
}

function popup_type_chooser(button)
{
  if ( ! column_change_allowed(the_current_cell.column) )
  {
    Alert("ERROR_value_not_modifiable") ;
    return ;
  }

  var cols = {} ;
  for(var i in types)
  {
    t = types[i] ;
    if ( ! cols[t.type_type] )
      cols[t.type_type] = [] ;
    cols[t.type_type].push(popup_type_choice(t)) ;
  }
  var t = '<table class="colored"><tr>' ;
  for(var i in cols)
    t += '<th>' + _('TH_type_type_' + i) ;
  t += '</tr><tr>' ;
  for(var i in cols)
  {
    // Use try/catch for an unknown IE error
    try {
      cols[i].sort(function(a,b) { return a.human_priority
				   - b.human_priority ; }) ;
    }
    catch(error)
    {
    }
    if ( t.type_type != 'data' && t.type_type != 'computed' )
      e = '<var style="background:#FCC">' + e + '</var>' ;

    t += '<td>' + cols[i].join('<br>') ;
  }
  t += '</table>' ;
  
  create_popup('type_chooser_div',
	       _('TITLE_columntype') + the_current_cell.column.title,
	       _('MSG_columntype') + '<br>',
	       t,
	       false) ;
}

function popup_type_choosed(type)
{
  var t = type_title_to_type(type) ;
  if ( t.type_type != 'data' && t.type_type != 'computed' )
    if ( ! confirm(_('ALERT_columntype')) )
      return ;
  
  var button = document.getElementById('t_column_type') ;
  var td = the_td(button) ;
  button.innerHTML = _('B_' + type) ;
  column_attr_set(the_current_cell.column, 'type', type, td, true) ;
  attr_update_user_interface(column_attributes['type'],
			     the_current_cell.column) ;
  popup_close() ;
}