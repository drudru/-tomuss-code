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

    Contact: Thierry.EXCOFFIER@univ-lyon1.fr
*/

function table_copy_button(id, text, help, toggled, unsensitive)
{
  id = 'table_copy_' + id ;
  if ( toggled )
    toggled = ' toggled' ;
  else
    toggled = '' ;
  if ( unsensitive === undefined )
    return '&nbsp;<span id="' + id
      + '" class="button_toggle' + toggled
      + '" onclick="tablecopy_do(this)"> '
      + hidden_txt(text, help) + ' </span>&nbsp;' ;
  else
    {
      if ( unsensitive )
	unsensitive = ' disabled="disabled" ' ;
      else
	unsensitive = '' ;
    return hidden_txt('<input type="button" onclick="tablecopy_do(this)" '
		      + 'id="' + id + '" ' + unsensitive
		      + 'style="width:auto" '
		      + 'value="' + text + '">', help) ;
    }
}

function tablecopy_toggle(id, toggle)
{
  var e = document.getElementById('table_copy_' + id) ;
  var toggled = e.className.indexOf('toggled') != -1 ;
  if ( toggle )
    {
      if ( toggled )
	e.className = 'button_toggle' ;
      else
	e.className += ' toggled' ;
    }
  return toggled ;
}

function tablecopy_do(t)
{
  var id = t.id.replace('table_copy_', '') ;
  var option = 'columns' ;
  if ( tablecopy_toggle('H') )
    option = 'history' ;
  else if ( tablecopy_toggle('C') )
    option = 'content' ;

  var iframe = '<iframe width="100%" style="height:10em" src="'
    + url + '/=' + ticket + '/' ;
  if ( t.type == 'button' )
    switch(id)
      {
      case 'TS':
	create_popup('export_div', _("TITLE_tablecopy_export"),
		     _("MSG_tablecopy_export") +
		     '<h3><span class="gui_button" '
		     + 'onmouseup="popup_close();print_selection()">'
		     + _("B_tablecopy_export") + '</span></h3>'
		     , '', false) ;
	break ;
      case 'ST':
	create_popup('export_div', _("TITLE_tablecopy_import"),
		     "<p>" + _("MSG_tablecopy_import"), '', false) ;
	break ;
      case 'F':
	var next_ys = next_year_semester(year, semester) ;
	  create_popup('export_div', _("TITLE_tablecopy_to_future"),
		       _("MSG_tablecopy_feedback")
		     + iframe
		     + year + '/' + semester + '/' + ue + '/tablecopy/'
		     + next_ys[0] + '/' + next_ys[1] + '/' + option
		     + '">' + '</iframe>',
		     "", false) ;
	break ;
      case 'P':
	var previous_ys = previous_year_semester(year, semester) ;
	  create_popup('export_div', _("TITLE_tablecopy_from_past"),
		       _("MSG_tablecopy_feedback")
		     + iframe
		     + previous_ys[0] + '/' + previous_ys[1] + '/' + ue
		     + '/tablecopy/' + year + '/' + semester + '/' + option
		     + '">' + '</iframe>',
		     "", false) ;
	break ;
      case 'PY':
	  create_popup('export_div', _("TITLE_tablecopy_from_past_year"),
		       _("MSG_tablecopy_feedback")
		     + iframe
		     + (year-1) + '/' + semester + '/' + ue
		     + '/tablecopy/' + year + '/' + semester + '/' + option
		     + '">' + '</iframe>',
		     "", false) ;
	break ;
      case 'R':
	var newname = document.getElementById('newname').value ;
	if ( newname == ue )
	  Alert("ALERT_tablecopy_copy_same") ;
	else
	  create_popup('export_div', _("TITLE_tablecopy_copy"),
		       _("MSG_tablecopy_feedback")
		     + iframe
		     + year + '/' + semester + '/' + ue + '/tablecopy/'
		     + year + '/' + semester + '/' + option + '/' + newname
		     + '">' + '</iframe>',
		     "", false) ;
	break ;
      }
  else
    {
      tablecopy_toggle(id, true) ;

      if ( ! tablecopy_toggle('c') )
	{
	  tablecopy_toggle('c', true) ;
	  Alert("ALERT_tablecopy_columns") ;
	}
      if ( tablecopy_toggle('H') && ! tablecopy_toggle('C') )
	{
	  if ( id != 'H' )
	    Alert("ALERT_tablecopy_history_without_content") ;
	  tablecopy_toggle('C', true) ;
	}
    }
}



function table_copy()
{
  var future, past, ts, st, current, previous, next, rename ;

  var next_ys = next_year_semester(year, semester) ;
  var previous_ys = previous_year_semester(year, semester) ;

  current = year + '<br>' + semester + '<br>' + ue ;
  previous_year = '<b>' + (year-1) + '</b><br>' + semester + '<br>' + ue ;
  previous = previous_ys[0] + '<br><b>' + previous_ys[1] + '</b><br>' + ue ;
  next = next_ys[0] + '<br>' + next_ys[1] + '<br>' + ue ;

  future = table_copy_button('F', '&nbsp;→&nbsp;',
			     _("TITLE_tablecopy_to_future") + '<br>'
			     +  _("TIP_tablecopy_warning_from"), false, false) ;

  past_year = table_copy_button('PY', '&nbsp;→&nbsp;',
				_("TITLE_tablecopy_from_past_year") + '<br>'
				+ _("TIP_tablecopy_warning_to"),
				false, false) ;

  past = table_copy_button('P', '&nbsp;→&nbsp;',
			   _("TITLE_tablecopy_from_past") + '<br>'
			   + _("TIP_tablecopy_warning_to"),
			   false, false) ;

  rename = table_copy_button('R', '&darr;',
			   _("TITLE_tablecopy_copy") + '<br>'
			   + _("TIP_tablecopy_warning_from"),
			   false, false) ;

  st= table_copy_button('ST','&darr;',_("TITLE_tablecopy_import"),false,false);
  ts= table_copy_button('TS','&uarr;',_("TITLE_tablecopy_export"),false,false);

  create_popup('import_div', _("TITLE_tablecopy"),
	       _("MSG_tablecopy") + '<br>'
	       + table_copy_button('c', _("B_tablecopy_columns"), 
				   _("TIP_tablecopy_columns"), true)
	       + _("TIP_tablecopy_and")
	       + table_copy_button('C', _("B_tablecopy_content"), 
				   _("TIP_tablecopy_content"))
	       + _("TIP_tablecopy_and")
	       + table_copy_button('H', _("TIP_tablecopy_history"), 
				   _("TIP_tablecopy_history"))
	       + '<br>&nbsp;<br>'
	       + '<table class="table_copy_diagram"><tr><td colspan="2">'
	       + _("MSG_tablecopy_arrow")
	       + '<th>' + _("MSG_tablecopy_spreadsheet") + '<td><td></tr>'
	       + '<tr><td><td><td>' + st + '&nbsp;' + ts + '<td><td></tr>'
	       + '<tr><th>' + previous_year + '<td>' + past_year
	       + '<th rowspan="2"><b>' + current
	       + '<td rowspan="2">' +future+ '<th rowspan="2">' +next+ '</tr>'
	       + '<tr><th>' + previous + '<td>' + past
	       + '<tr><td><td><td>' + rename
	       + '<tr><td><td><th>'
	       + year + '<br>' + semester + '<br>'
	       + '<input id="newname" style="font-weight:bold" value="'
	       + ue + '">'
	       + '</table>'
	       , '', false) ;
}
