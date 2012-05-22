// -*- coding: utf-8 -*-
/*
  TOMUSS: The Online Multi User Simple Spreadsheet
  Copyright (C) 2011-2012 Thierry EXCOFFIER, Universite Claude Bernard

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

function fill_column()
{
  var m = '' ;

  if ( table_attr.autosave )
    m = '<div id="stop_the_auto_save">' + _("MSG_fill_warning_left")
	+ ' <a href="#" onclick="select_tab(\'table\', \'Action\');table_autosave_toggle();document.getElementById(\'stop_the_auto_save\').style.display=\'none\';">'
	+ _("MSG_fill_warning_middle") + '</a> ' +_("MSG_fill_warning_right")
	+ '</div>' ;

  create_popup('fill_column_div',
	       _("TITLE_fill_before")
	       + the_current_cell.column.title + _("TITLE_fill_after"),
	       m + _("MSG_fill") + '<br>&nbsp;<br>'
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
				  +'<br>'
				  +'<TEXTAREA id="column_fill_abab"></TEXTAREA>'
				 ],
				 ["AA... BB... CC...",
				  _('MSG_fill_multiple')
				  +' <tt>A A... B B... C C...</tt><br>'
				  +_('MSG_fill_equal')
				  +'<br>'
				  +'<TEXTAREA id="column_fill_aabb"></TEXTAREA>'
				  ],

			     ])
	       + '<BUTTON OnClick="fill_column_do_fill();">'
	       + _('B_fill') + '</BUTTON>',
	       '', false
	       ) ;
  select_tab("tablefill", _("TAB_fill_one")) ;
  popup_text_area().rows = 4 ;
}

function fill_column_do_fill()
{
    alert_append_start() ;

    var choice = selected_tab('tablefill') ;
    if ( choice === _('TAB_fill_clear') )
	fill_column_do_abab(['']) ;
    else if ( choice === _('TAB_fill_one') )
	fill_column_do_abab(parse_lines(
	    document.getElementById('column_fill_input').value)) ;
    else if ( choice === "AA... BB... CC..." )
	fill_column_do_aabb(parse_lines(
	    document.getElementById('column_fill_aabb').value)) ;
    else if ( choice === "ABC ABC ABC..." )
	fill_column_do_abab(parse_lines(
	    document.getElementById('column_fill_abab').value)) ;
    else
	alert_real(choice);
   
    alert_append_stop() ;
    the_current_cell.column.need_update = true ;
    update_columns() ;
    popup_close() ;
    table_fill() ;
}

function fill_column_do_aabb(values)
{
  var i, j, value ;

  for(j in filtered_lines)
    {
      i = Math.floor((values.length * j) / filtered_lines.length) ;
      if ( i >= values.length )
	i = values.length ;
      value = values[i] ;
      cell_set_value_real(filtered_lines[j].line_id, the_current_cell.data_col,
			  value) ;
    }
}

function fill_column_do_abab(values)
{
  var i, j, value ;

  for(j in filtered_lines)
    {
      i = j % values.length ;
      value = values[i] ;
      cell_set_value_real(filtered_lines[j].line_id, the_current_cell.data_col,
			  value) ;
    }
}
