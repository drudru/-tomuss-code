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
    m = '<div style="text-align:right" id="stop_the_auto_save">' +
      'Cette opération ne sera pas annulable.<br>' +
      'Désactivez la <a href="#" onclick="select_tab(\'table\', \'Action\');table_autosave_toggle();document.getElementById(\'stop_the_auto_save\').style.display=\'none\';">'+
      'sauvegarde automatique</a> pour être tranquille,<br>' +
      ' vous la réactiverez après avoir vérifié le résultat.</div>';


  create_popup('fill_column_div',
	       'Remplir la colonne «'
	       + the_current_cell.column.title + '»',
	       'Indiquez une valeur par ligne dans la zone de saisie.<br>' +
	       'Les valeurs seront recopiées '+
	       'autant de fois que nécessaire pour remplir la colonne de' +
	       ' la table telle qu\'elle apparaît sur l\'écran.' +
	       m
	       ,
	       "Pour remplir la colonne, cliquez sur le bouton indiquant " +
	       "dans quel ordre seront insérées les valeurs. " +
	       "Si vous avez indiqué les valeurs A, B et C sur 3 lignes :<br>" +
	       '<BUTTON OnClick="fill_column_do_aabb();">AAAABBBBCCCC</BUTTON> ou '+
	       '<BUTTON OnClick="fill_column_do_abab();">ABCABCABCABC</BUTTON>.'
	       ) ;
}

function fill_column_do_aabb()
{
  var values = popup_value() ;
  var i, value ;

  alert_append_start() ;
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
  alert_append_stop() ;
  popup_close() ;
  the_current_cell.column.need_update = true ;
  update_columns() ;
  table_fill() ;
}

function fill_column_do_abab()
{
  var values = popup_value() ;
  var i, value ;

  alert_append_start() ;
  for(data_lin in filtered_lines)
    {
      i = data_lin % values.length ;
      value = values[i] ;
      cell_set_value_real(filtered_lines[data_lin].number,
			  the_current_cell.data_col,
			  value) ;
    }
  alert_append_stop() ;
  the_current_cell.column.need_update = true ;
  update_columns() ;
  popup_close() ;
  table_fill() ;
}
