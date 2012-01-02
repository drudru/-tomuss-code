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

function import_column()
{
  var m = '' ;

  if ( nr_not_empty_lines !== 0 )
    m = "<small>L'importation de table complète fonctionne seulement si la table est vide.</small>" ;
  else
    m = '<small><a href="javascript:full_import()">Import d\'une table complète : copier le fichier CSV au dessus et cliquez ici.</a></small>' ;

  var t ;
  if ( the_current_cell.data_col === 0 )
    t = 'Pour transférer des numéros d\'étudiants dans TOMUSS&nbsp;:' +
      '<ul><li>Copiez dans votre tableur favori les numéros d\'étudiant.' +
      '  <li>Coller dans la zone de saisie (blanche) le résultat qui ressemble à&nbsp;:'+
      '	<pre><b>10188995\n'+
      '10356775\n'+
      '10356011</b></pre>'+
      '   <li> Puis cliquez sur <BUTTON OnClick="import_column_do();">importer les numéros d\'étudiants dans TOMUSS</BUTTON>.' +
      '</ul>' ;
  else
    t = 'Pour transférer des valeurs dans TOMUSS&nbsp;:' +
      '<ul><li>Copiez de votre tableur favori les colonnes numéro d\'étudiant' +
      ' et la valeur que vous désirez transférer.'+
      '  <li>Coller dans la grande zone de saisie (blanche) juste au dessous le résultat qui ressemble à&nbsp;:'+
      '	<pre><b>10188995 8\n'+
      '10356775 9.6\n'+
      '10356011 ABI</b></pre>'+
      '   <li> Puis cliquez sur <BUTTON OnClick="import_column_do();">importer les données dans TOMUSS</BUTTON>.' +
      '</ul>' ;

  create_popup('import_div',
	       "Importer dans la colonne «" + the_current_cell.column.title + '»',
	       t, m) ;
}

function import_column_do()
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

  if ( data_col === 0 )
    {
      // Import in ID column
      for(i in multiline)
	{
	  if ( multiline[i] === '' )
	    continue ;
	  var m = multiline[i].split(/[\t ]+/) ;
	  if ( m.length != 1 )
	    {
	      problems += "On ajoute «" + m[0] + '» au lieu de «'
		+ multiline[i] + '»\n' ;
	      continue ;
	    }
	  if ( login_to_line_id(m[0]) !== undefined )
	    {
	      problems += "«"+ m[0] +"» n'est pas ajouté car déja présent\n";
	      continue ;
	    }
	  replace += 'Ajoute ' + m[0] + ' ' ;
	  todo.push([-1, 0, m[0]]) ;
	}
      if ( problems !== '' )
	{
	  element_focused = undefined ;
	  if ( ! confirm(problems + '\nVoulez-vous importer ?') )
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
	  line_id = login_to_line_id(login_to_id(login)) ;
	  if ( line_id === undefined )
	    {
	      replace += login + " n'est pas dans la table, sa note (" +
		value + ") ne sera pas importée\n" ;
	      // problems += login + '\n' ;
	      continue ;
	    }

	  val = lines[line_id][data_col].value ;
	  if ( val !== '' && val != value )
	    replace += lines[line_id][0].value + ' : ' + val + ' ==> '
	      + value + '\n' ;
	  if ( twin[line_id] !== undefined )
	    {
	      replace += 'Vous donnez plusieurs notes à ' + login +
		' seule la première sera importée\n' ;
	      continue ;
	    }
	  twin[line_id] = value ;
	  todo.push([line_id, data_col, value]) ;
	}
      /*
      if ( problems !== '' )
	{
	  element_focused = undefined ;
	  alert("Les numéros d'étudiant suivants ne sont pas dans ce tableau. Aucun importation n'a été faite. Vous devez d'abord importer ces numéros d'étudiants dans la colonne numéro d'étudiant.\n"
		+ problems);
	  return ;
	}
      */
    }

  if ( replace !== '' )
    {
      element_focused = undefined ;
      if ( ! confirm("Vous êtes sur de vouloir faire les changements suivants ?\n" + replace) )
	return ;
    }
  alert_append_start() ;
  for(i in todo)
    {
      i = todo[i] ;
      if ( i[0] == -1 )
	i[0] = add_a_new_line() ;
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
  var cls = column_list_all() ;
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
	    alert('Nombre de colonnes variable... La première ligne doit être la plus longue.') ;
	    return ;
	  }
	else
	  {
	    while( line.length != nr_cols )
	      line.push('') ;
	  }
      new_lines.push(line) ;
    }
  if ( ! confirm("Confirmez l'importation de " + new_lines.length +
		 ' lignes et de ' + nr_cols + ' colonnes ?\n\nAucun retour en arrière ne sera possible.\nAucun autre import CSV ne sera possible.\n\nCette importation peut prendre ' + (new_lines.length*nr_cols)/10 + ' secondes') )
    return ;

  alert_append_start() ;
  for(var data_col=0; data_col < nr_cols; data_col++)
    {
      if ( columns[data_col] === undefined )
	add_empty_column() ;
      if ( columns[data_col].the_local_id !== undefined ) // Just created
	{
	  column_attr_set(columns[data_col], 'type', 'Text') ;
	  column_attr_set(columns[data_col], 'title', 'csv_' + data_col) ;
	  create_column(columns[data_col]) ;
	}
    }
  for(line in new_lines)
    {
      add_a_new_line(line.toString()) ;
      // From right to left in order to not have a race between
      // the firstname and surname stored from the CSV and the sames
      // extracted from database.
      // If the race is lost, the user try to write a system computed data
      // and an error is displayed (one for each race lost)
      for(var data_col=nr_cols-1 ; data_col >= 0 ; data_col-- )
	cell_set_value_real(line, data_col, new_lines[line][data_col]) ;
    }
  alert_append_stop() ;

  the_current_cell.jump(nr_headers,0,false,0,0) ;
  popup_close() ;
  table_init() ;
  table_fill(false, true) ;
}
