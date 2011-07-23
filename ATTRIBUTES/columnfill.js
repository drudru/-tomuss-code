// -*- coding: utf-8 -*-
/*
  TOMUSS: The Online Multi User Simple Spreadsheet
  Copyright (C) 2011 Thierry EXCOFFIER, Universite Claude Bernard

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
    m = '<div id="stop_the_auto_save">' +
      'Ces opérations ne sont pas annulable.<br>' +
      'Désactivez la <a href="#" onclick="select_tab(\'table\', \'Action\');table_autosave_toggle();document.getElementById(\'stop_the_auto_save\').style.display=\'none\';">'+
      'sauvegarde automatique</a> pour être tranquille,<br>' +
      ' vous la réactiverez après avoir vérifié le résultat.</div>';


  create_popup('fill_column_div',
	       'Remplir la colonne «'
	       + the_current_cell.column.title + '»',m +
	       '<b>Seules les lignes filtrées seront modifiées.</b><br>' +
	       'Vous pouvez <BUTTON OnClick="fill_column_do_empty();">' +
	       'effacer les valeurs</BUTTON><br>' +
	       'Sinon, indiquez une valeur par ligne dans la zone de saisie, '+
	       'ces valeurs rempliront la colonne quand vous cliquerez sur ' +
	       '<BUTTON OnClick="fill_column_do_fill();">remplir</BUTTON>'
	       ,
	       'Si vous avez saisi plus d\'une valeur (A, B, C sur 3 lignes ' +
	       'par exemple), le remplissage sera équilibré entre les ' +
	       'valeurs et vous pouvez choisir l\'ordre de remplissage&nbsp;:'+
	       '<select id="aaabbbccc">' +
	       '<option>A A A A... B B B B... C C C C...</option>' +
	       '<option>A B C A B C A B C A B C...</option>' +
	       '</select>'
	       ) ;
  popup_text_area().rows = 4 ;
}

function fill_column_do_empty()
{
  popup_set_value('') ;
  fill_column_do_fill() ;
}

function fill_column_do_fill()
{
  var values = popup_value() ;

  alert_append_start() ;

  if ( document.getElementById('aaabbbccc').selectedIndex == 0 )
    fill_column_do_aabb(values) ;
  else
    fill_column_do_abab(values) ;

  alert_append_stop() ;
  the_current_cell.column.need_update = true ;
  update_columns() ;
  popup_close() ;
  table_fill() ;
}

function fill_column_do_aabb(values)
{
  var i, value ;

  for(data_lin in filtered_lines)
    {
      i = Math.floor((values.length * data_lin) / filtered_lines.length) ;
      if ( i >= values.length )
	i = values.length ;
      value = values[i] ;
      cell_set_value_real(filtered_lines[data_lin].number,
			  the_current_cell.data_col,
			  value) ;
    }
}

function fill_column_do_abab(values)
{
  var i, value ;

  for(data_lin in filtered_lines)
    {
      i = data_lin % values.length ;
      value = values[i] ;
      cell_set_value_real(filtered_lines[data_lin].number,
			  the_current_cell.data_col,
			  value) ;
    }
}
