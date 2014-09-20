// -*- coding: utf-8 -*-
/*
  TOMUSS: The Online Multi User Simple Spreadsheet
  Copyright (C) 2011, 2013 Thierry EXCOFFIER, Universite Claude Bernard

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

var columnexport_options ;
var abjvalue, ppnvalue, tnrvalue ;

function cell_value_export(column)
{
  var xx = a_float(this.value) ;
  if ( column.type == 'Text' || isNaN(xx) )
    {
      xx = this.value.toString() ;
      switch(xx)
	{
	case 'NaN': return '' ;
	case abi: return abi_short ;
	case abj: return abjvalue ;
	case ppn: return ppnvalue ;
	case tnr: return tnrvalue ;
	default: return xx.replace(/\n/g, '⏎') ;
	}
    }
  else
    {
      if ( xx < column.min )
	xx = column.min ;
      else if ( xx > column.max )
	xx = column.max ;
      return local_number(column.do_rounding(xx)) ;
    }
}

function abj_ppn_value()
{
  Cell.prototype.value_export = cell_value_export ;
  
  if ( columnexport_options.abjvalue )
    {
      abjvalue = '0' ;
      ppnvalue = '0' ;
      tnrvalue = '0' ;
    }
  else
    {
      abjvalue = abj_short ;
      ppnvalue = ppn_short ;
      tnrvalue = tnr_short ;
    }
}

function get_filtered_logins()
{
  var v = {} ;
  for(var lin in filtered_lines)
    {
      lin = filtered_lines[lin] ;
      if ( lin[0].value )
	v[lin[0].value] = true ;
    }
  return v ;
}

function export_column()
{
  if ( the_current_cell.data_col == 0 )
    columnexport_options = {"students": true} ;
  else
    columnexport_options = {"values": true} ;
  create_popup('export_div',
	       _("TITLE_columnexport_before") + the_current_cell.column.title
	       + _("TITLE_columnexport_after"),
	       _("MSG_columnexport_before")
	       + '<a href="javascript:columnexport_filtered()">'
	       + hidden_txt(_("MSG_columnexport_filtered"),
			    _("TIP_columnexport_filtered")) + '</a>'
	       + _("MSG_columnexport_middle")
	       + toggle_button(_("B_columnexport_abjvalue"),
			       'columnexport_options', 'abjvalue',
			       _("TIP_columnexport_abjvalue")
			      )
	       + ', '
	       + toggle_button(_("B_columnexport_unique"),
			       'columnexport_options', 'unique',
			       _("TIP_columnexport_unique"))
	       + _("MSG_columnexport_after")
	       + '<table class="colored columnexport">'
	       + '<colgroup><col width="10*"><col width="12*"><col width="30*"></colgroup>'
	       + '<tr><th>' + _("MSG_columnexport_students") + '<br>'
	       + '<a href="javascript:columnexport_filtered()">'
	       + hidden_txt(_("MSG_columnexport_filtered"),
			    _("TIP_columnexport_filtered")) + '</a>'
	       + '<th>'
	       + toggle_button(_("B_columnexport_students"),
			       'columnexport_options', 'students',
			       _("TIP_columnexport_students"))
	       + ' '
	       + toggle_button(_("B_columnexport_values"),
			       'columnexport_options', 'values',
			       _("TIP_columnexport_values"))
	       + ' '
	       + toggle_button(_("B_columnexport_comments"),
			       'columnexport_options', 'comments',
			       _("TIP_columnexport_comments"))
	       + '<th>' + _("MSG_columnexport_errors") + '</tr>'
	       + '<tr class="content"><td><textarea rows="10" style="width:100%" onscroll="columnexport_scroll(event,0);" onchange="do_printable_display = true ;" onkeyup="do_printable_display = true" onpaste="do_printable_display = true ;"></textarea>'
	       + '<td><textarea id="columnexport_output" wrap="off" onscroll="columnexport_scroll(event,1);"></textarea>'
	       + '<td><div id="columnexport_errors"></div>'
	       + '</tr></table>', '', false
	       ) ;
  do_printable_display = false ;
  periodic_work_add(do_columnexport) ;
  if ( popup_column().data_col == 0 )
    columnexport_filtered() ;
}

function columnexport_filtered()
{
  var s = [] ;
  for(var i in get_filtered_logins())
    s.push(i) ;
  popup_text_area().value = s.join('\n') ;
  do_printable_display = true ;
}

function columnexport_scroll(event, dir)
{
  if ( columnexport_options.unique )
    return ;
  event = the_event(event) ;
  if ( dir != 0 )
    popup_text_area().scrollTop = event.target.scrollTop ;
  else
    document.getElementById("columnexport_output").scrollTop = event.target.scrollTop ;
}

function do_columnexport()
{
  if ( ! popup_is_open() )
    return ; // Stop periodic work
  if ( ! do_printable_display )
    return true ;
  do_printable_display = false ;

  abj_ppn_value() ;
  var column = popup_column() ;
  var data_col = column.data_col ;
  var multiline = popup_value() ;
  var exported = {} ;
  var uniques = {} ;
  var error1 = '', error2 = '' ;
  var v = [], line, cell, login ;

  for(var i in multiline)
    {
      if ( multiline[i] === '' )
	{
	  v.push('') ;
	  error1 = _("ALERT_columnexport_no_id") + '<hr>' ;
	  continue ;
	}
      cell = [] ;
      login = login_to_id(multiline[i].replace(/^ */,'').replace(/ *$/,'')) ;
      line_id = login_to_line_id(login) ;
      if ( line_id === undefined )
	{
	  if ( columnexport_options.students && !columnexport_options.unique )
	    cell.push(login) ;
	  if ( columnexport_options.values )
	    cell.push('???') ;
	  if ( columnexport_options.comments )
	    cell.push('???') ;	  
	  v.push(cell.join('\t')) ;
	  error2 = _("ALERT_columnexport_unfound") + '<hr>' ;
	  continue ;
	}
      line = lines[line_id] ;
      if ( columnexport_options.students && !columnexport_options.unique )
	cell.push(encode_lf_tab(line[0].value.toString())) ;
      if ( columnexport_options.values )
	cell.push(line[data_col].value_export(column)) ;
      if ( columnexport_options.comments )
	cell.push(encode_lf_tab(line[data_col].comment)) ;
      v.push(cell.join('\t')) ;

      exported[line[0].value] = true ;
      if ( uniques[cell] === undefined )
	uniques[cell] = [line[0].value] ;
      else
	uniques[cell].push(line[0].value) ;
    }

  if ( columnexport_options.unique )
  {
    v = [] ;
    var t = [] ;
    for(var i in uniques)
      t.push(i) ;
    t.sort() ;
    for(var i in t)
    {
      i = t[i] ;
      if ( columnexport_options.students )
	v.push(i + '\t' + uniques[i].join(' ')) ;
      else
	v.push(i) ;
    }
  }
  var co = document.getElementById('columnexport_output') ;
  co.value = v.join('\n') ;
  co.scrollTop = popup_text_area().scrollTop ;
  
  var m = '' ;

  for(var line in filtered_lines)
    if ( exported[filtered_lines[line][0].value] != true )
      if ( filtered_lines[line][data_col].value !== '' )
	m += filtered_lines[line][0].value + ':'
	  + filtered_lines[line][data_col].value + '\n' ;

  if ( m !== '' )
      m = _("ALERT_columnexport_unexported") + '\n' + m ;

  document.getElementById('columnexport_errors').innerHTML =
    error1 + error2 + html(m).replace(/\n/g, "<br>")  ;
  return true ;
}
