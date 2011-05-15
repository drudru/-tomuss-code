/*
    TOMUSS: The Online Multi User Simple Spreadsheet
    Copyright (C) 2008,2009 Thierry EXCOFFIER, Universite Claude Bernard

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

var abi = "ABINJ" ;
var abj = "ABJUS" ;
var ppn = "PPNOT" ;
var pre = "PRST" ;
var default_title = "Séance" ;
var yes = 'OUI' ;
var no = 'NON' ;


function update_filters(unused_column)
{
  filters = [] ; // GLOBAL
  for(var data_col in columns)
    {
      var column = columns[data_col] ;
      if ( column.filter === '' )
	continue ;
      filters.push([column.real_filter, data_col, column]) ;
    }
  line_offset = 0 ;

  return true ;
}


var alert_merged = false ;

function alert_append_start()
{
  alert_merged = '' ;
}

function alert_append_stop()
{
  if ( alert_merged )
    alert(alert_merged) ;
  alert_merged = false ;
}

function alert_append(x)
{
  if ( alert_merged === false )
    alert(x) ;
  else
    alert_merged += '\n' + x ;
}
 





/******************************************************************************
When an header change, update cells
******************************************************************************/

function update_column_recursive(column, line)
{
  var type = column.real_type ;

  if ( column.update_done )
    return ;
  column.update_done = true ;

  if ( type.cell_compute === undefined )
    return ;

  for(var c in column.average_columns)
    {
      update_column_recursive(columns[column.average_columns[c]], line) ;
      column.need_update |= columns[column.average_columns[c]].need_update ;
    }
  
  if ( column.need_update )
    {
      if ( line === undefined )
	{
	  for(var data_lin in lines)
	    if ( ! line_empty(lines[data_lin]) )
	      type.cell_compute(column.data_col, lines[data_lin]) ;
	}
      else
	{
	  type.cell_compute(column.data_col, line) ;
	}
    }

  return ;
}

function update_columns(line)
{
  var need_update = false ;
  var data_col ;

  for(data_col in columns)
    columns[data_col].update_done = false ;

  for(data_col in columns)
    update_column_recursive(columns[data_col], line) ;

  for(data_col in columns)
    {
      need_update |= columns[data_col].need_update ;
      columns[data_col].need_update = false ;
    }
  return need_update ;
}

// Give focus to a newly created focus (redondant but necessary)
function my_focus(event)
{
  event = the_event(event) ;
  if ( event.target )
    {
      event.target.focus() ;
      if ( event.target.select !== undefined )
	event.target.select() ;
      event.target.onmouseup = function() {} ;
    }
}

/******************************************************************************
Column actions
******************************************************************************/

function hide_column()
{
  var column = the_current_cell.column ;
  column.hidden = 1 ;
  table_fill(false, true) ;
}

function bigger_column()
{
  var column = the_current_cell.column ;
  column.width += 1 ;
  table_header_fill() ;
  setTimeout('update_table_size()', 200) ;
}

function smaller_column()
{
  var column = the_current_cell.column ;
  if ( column.width > 1 )
    {
      column.width -= 1 ;
      table_header_fill() ;
      setTimeout('update_table_size()', 200) ;
    }
}

function left_column(column)
{
  if ( table_fill_queued )
    return ; // XXX Hide a bug (moving column quickly lost it sometimes)

  var cls = column_list(0, columns.length) ;

  var i = myindex(cls, column) ;

  if ( i == 1 )
    column.position = cls[0].position - 1 ;
  else if ( i !== 0 )
    column.position = (cls[i-1].position + cls[i-2].position) / 2 ;

  table_fill(false, true) ;
}

function right_column(column)
{
  if ( table_fill_queued )
    return ; // XXX Hide a bug (moving column quickly lost it sometimes)

  var cls = column_list(0, columns.length) ;

  var i = myindex(cls, column) ;

  if ( i == cls.length - 2 )
    column.position = cls[i+1].position + 1 ;
  else if ( i != cls.length - 1 )
    column.position = (cls[i+1].position + cls[i+2].position) / 2 ;

  table_fill(false, true) ;
}

function column_title_to_data_col(title)
{
  for(var data_col in columns)
    if ( columns[data_col].title == title )
      return data_col ;
}

function column_used_in_average(name)
{
  for(var column in columns)
    {
      column = columns[column] ;
      for(var use in column.average_from)
	if ( column.average_from[use] == name )
	  return column.title ;
    }
  return false ;
}

function column_delete()
{
  var column = the_current_cell.column ;
  var empty = column_empty_of_cells(column.data_col) ;
  if ( column.real_type.cell_is_modifiable && ! empty )
    {
      alert('On peut seulement détruire des colonnes vides.\n\nVous devez donc d\'abord vider la colonne en cliquant sur "Remp."') ;
      return ;
    }
  if ( column.author == '*' && column.data_col < 6 )
    {
      alert("Il est interdit d'enlever cette colonne") ;
      return ;
    }
  if ( ! column_change_allowed(column) )
    {
      alert("La colonne n'a pas été créée par vous mais par " + column.author +
	    " et vous n'êtes pas responsable de l'UE : " + teachers) ;
      return ;
    }
  var c = column_used_in_average(column.title) ;
  if ( c )
    {
      alert("Cette colonne est utilisée par la colonne «" + c + '»') ;
      return ;
    }
  if ( column.the_local_id !== undefined )
    {
      alert("Cette colonne n'existe pas encore.\nPour afficher moins de colonnes sur l'écran, changez le nombre de colonnes à afficher dans le menu en haut de la case «Tableau».") ;
      return ;
    }
  if ( ! empty )
    if (!confirm("Voulez-vous vraiment détruire la colonne : " + column.title))
      return ;

  append_image(undefined, 'column_delete/' + column.the_id) ;
  Xcolumn_delete(' ', column.the_id) ;
  the_current_cell.update_headers() ;
}

function save_position_column(column, td)
{
  column_attr_set(column, 'position', column.position, td) ;
}

function save_width_column(column, td)
{
  column_attr_set(column, 'width', column.width, td) ;
}

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


/******************************************************************************
Column Types
******************************************************************************/

function index_to_type(i)
{
  // alert('index_to_type ' + i + ' ' + types[i].title);
  return types[i].title ;
}

var types = [] ;

function test_nothing(value, column)
{
  return value ;
}

function test_float(value, column)
{
  return Number(value) ;
}

function unmodifiable(value, column)
{
  // It was "return '' ;" before the 2010-09-13
  // It was modified in order to make the 'import_columns' function work.
  return value ;
}

