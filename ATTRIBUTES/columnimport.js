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
  if ( semester != 'Printemps' && semester != 'Automne' )
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
  var empty_line = add_empty_lines() ;
  var column = popup_column() ;
  var data_col = column.data_col ;

  if ( column_empty(data_col) && column.the_local_id !== undefined )
    {
      create_column(column) ;
    }

  var data_lin ;
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
	      problems += "Indiquez seulement le numéro d'étudiant : "
		+ multiline[i] + '\n' ;
	      continue ;
	    }
	  if ( login_to_line(m[0]) !== undefined )
	    {
	      problems += "L'étudiant est déja dans la table : " + m[0] + '\n';
	      continue ;
	    }
	  replace += 'Ajoute ' + m[0] + ' ' ;
	  todo.push([-1, 0, m[0]]) ;
	}
      if ( problems !== '' )
	{
	  element_focused = undefined ;
	  alert(problems) ;
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
	  data_lin = login_to_line(login_to_id(login)) ;
	  if ( data_lin === undefined )
	    {
	      replace += login + " n'est pas dans la table, sa note (" +
		value + ") ne sera pas importée\n" ;
	      // problems += login + '\n' ;
	      continue ;
	    }

	  val = lines[data_lin][data_col].value ;
	  if ( val !== '' && val != value )
	    replace += lines[data_lin][0].value + ' : ' + val + ' ==> '
	      + value + '\n' ;
	  if ( twin[data_lin] !== undefined )
	    {
	      replace += 'Vous donnez plusieurs notes à ' + login +
		' seule la première sera importée\n' ;
	      continue ;
	    }
	  twin[data_lin] = value ;
	  todo.push([data_lin, data_col, value]) ;
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
	i[0] = add_empty_lines() ;
      cell_set_value_real(i[0], i[1], i[2]) ;
    }
  alert_append_stop() ;

  popup_close() ;
  column.need_update = true ;
  update_columns() ;
  table_fill() ;
}
