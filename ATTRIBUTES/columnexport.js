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

function export_column()
{
  create_popup('export_div',
	       "Exporte la colonne «" + the_current_cell.column.title + '»',
	       'Pour transférer de TOMUSS vers APOGÉE&nbsp;:' +
	       "<ul><li>Collez dans la grande zone de saisie (blanche) les numéros d'étudiants venant d'APOGÉE" +
	       '<li>Cochez <input type="checkbox" id="abjvalue"> pour transformer les ABJ et les PPN en 0.'+
	       '<li>Cliquez sur <BUTTON OnClick="export_column_value();">récupérer les notes</BUTTON>' +
	       '<li>Copiez les notes de la zone de saisie vers APOGÉE (en utilisant Excel en Français).</ul>' +
	       'Sinon vous pouvez <BUTTON OnClick="export_column_id_value();">exporter les numéros d\'étudiants et les valeurs</BUTTON> ou <BUTTON OnClick="export_column_uniques_values();">les valeurs <b>uniques</b></BUTTON> de cette colonne vers la zone de saisie pour les copier dans votre tableur favori.',
	       '') ;
}

function export_column_uniques_values()
{
  var data_col = popup_column().data_col, student_id ;
  var v = {} ;

  abj_ppn_value() ;

  for(var lin in filtered_lines)
    {
      lin = filtered_lines[lin] ;
      if ( lin[0].value )
	v[lin[data_col].value] = true ;
    }

  var text = [] ;
  for(var i in v)
    text.push(i) ;
  text.sort() ;

  popup_set_value(text.join('\n')) ;
}

function export_column_id_value()
{
  var data_col = popup_column().data_col, student_id ;
  var v = '' ;

  abj_ppn_value() ;

  for(var lin in filtered_lines)
    {
      lin = filtered_lines[lin] ;
      student_id = login_to_id(lin[0].value) ;
      if ( student_id === '' )
	continue ;
      if ( data_col )
	v += student_id  + '\t' + lin[data_col].value_export() + '\n' ;
      else
	v += student_id + '\n' ;
    }
  popup_set_value(v) ;
}

var abjvalue, ppnvalue ;

function abj_ppn_value()
{
  Cell.prototype.value_export = cell_value_export ;
  abjvalue = document.getElementById('abjvalue').checked ;
  if ( abjvalue )
    {
      abjvalue = '0' ;
      ppnvalue = '0' ;
    }
  else
    {
      abjvalue = 'ABJ' ;
      ppnvalue = 'PPN' ;
    }
}

function cell_value_export()
{
  var xx = a_float(this.value) ;
  if ( isNaN(xx) )
    {
      xx = this.value.toString() ;
      switch(xx)
	{
	case 'NaN': return '' ;
	case abi: return 'ABI' ;
	case abj: return abjvalue ;
	case ppn: return ppnvalue ;
	default: return xx ;
	}
    }
  else
    {
      if ( xx < 0 )
	xx = 0 ;
      return tofixedapogee(xx) ;
    }
}

function export_column_value()
{
  var multiline = popup_value() ;
  var column = popup_column() ;
  var data_col = column.data_col ;
  var error = false ;
  var v = '' ;
  var exported = [] ;
  var line_id ;

  abj_ppn_value() ;

  for(var i in multiline)
    {
      if ( multiline[i] === '' )
	{
	  element_focused = undefined ;
	  alert("Il y a une ligne sans numéro d'étudiant") ;
	  return ;
	}
      line_id = login_to_line_id(login_to_id(multiline[i].replace(/ */g,''))) ;
      if ( line_id === undefined )
	{
	  v += '???\n' ;
	  if ( error === false )
	    {
	      error = true ;
	    }
	  continue ;
	}

      v += lines[line_id][data_col].value_export() + '\n' ;

      exported[lines[line_id][0].value] = true ;
    }
  popup_set_value(v) ;

  var m = '' ;
  if ( error )
    m = "Au moins un numéro d'étudiant n'a pas été trouvé.\nLa valeur a été mise à ???.\n\n" ;

  for(var line in filtered_lines)
    if ( exported[filtered_lines[line][0].value] != true )
      if ( filtered_lines[line][data_col].value !== '' )
	m += filtered_lines[line][0].value + ':'
	  + filtered_lines[line][data_col].value + '\n' ;

  if ( m !== '' )
    alert("Les étudiants suivants n'ont pas eu leur notes exportées :\n" + m) ;
}
