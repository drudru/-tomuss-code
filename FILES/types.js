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

function freeze_column(column)
{
  if ( column === undefined )
    column = the_current_cell.column ;
  if ( column.freezed == 'F' )
    column.freezed = '' ;
  else
    column.freezed = 'F' ;
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
  if ( ! column_empty_of_cells(column.data_col) )
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

  append_image(undefined, 'column_delete/' + column.the_id) ;
  Xcolumn_delete(' ', column.the_id) ;
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

function export_column()
{
  create_popup('export_div',
	       "Exporte la colonne «" + the_current_cell.column.title + '»',
	       'Pour transférer de TOMUSS vers APOGÉE&nbsp;:' +
	       "<ul><li>Collez dans la grande zone de saisie (blanche) les numéros d'étudiants venant d'APOGÉE" +
	       '<li>Cochez <input type="checkbox" id="abjvalue"> pour transformer les ABJ et les PPN en 0.'+
	       '<li>Cliquez sur <BUTTON OnClick="export_column_value();">récupérer les notes</BUTTON>' +
	       '<li>Copiez les notes de la zone de saisie vers APOGÉE (en utilisant Excel en Français).</ul>' +
	       'Sinon vous pouvez <BUTTON OnClick="export_column_id_value();">exporter les numéros d\'étudiants et les valeurs</BUTTON> de cette colonne vers la zone de saisie pour les copier dans votre tableur favori.',
	       '') ;
}

function abj_ppn_value()
{
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

function export_column_value()
{
  var multiline = popup_value() ;
  var column = popup_column() ;
  var data_col = column.data_col ;
  var error = false ;
  var v = '' ;
  var exported = [] ;

  abj_ppn_value() ;

  for(var i in multiline)
    {
      if ( multiline[i] === '' )
	{
	  element_focused = undefined ;
	  alert("Il y a une ligne sans numéro d'étudiant") ;
	  return ;
	}
      data_lin = login_to_line(login_to_id(multiline[i].replace(/ */g,''))) ;
      if ( data_lin === undefined )
	{
	  v += '???\n' ;
	  if ( error === false )
	    {
	      error = true ;
	    }
	  continue ;
	}

      v += lines[data_lin][data_col].value_export() + '\n' ;

      exported[lines[data_lin][0].value] = true ;
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

/******************************************************************************
Column Types
******************************************************************************/

function index_to_type(i)
{
  // alert('index_to_type ' + i + ' ' + types[i].title);
  return types[i].title ;
}

var types = [] ;



/*
 * Set the column title and change formula if necessary.
 * Returns the new title.
 */

function set_title(value, column, xcolumn_attr)
{
  value = value.replace(/ /g, '_') ;

  for(var data_col in columns)
    if ( data_col != column.data_col
	 && column.data_col // For display_suivi()
	 && !xcolumn_attr
	 && columns[data_col].title == value )
      {
	return column_attributes.title.check_and_set(value + '_bis', column,
                                                     xcolumn_attr) ;
      }

  // XXX does not replace multiple occurrence because
  // Regex can not be used easely with special characters
  // that may appear in titles.

  if ( ! xcolumn_attr && column.title !== '' )
    {
      var job_to_do = [] ;

      for(var data_col in columns)
	{
	  var formula_column = columns[data_col] ;
	  var w = (' ' + formula_column.columns + ' ')
	    .replace(' ' + column.title + ' ',
		     ' ' + value + ' ') ;
	  w = w.substr(1, w.length-2) ; // Remove appended space
	  
	  if ( w == formula_column.columns )
	    continue ;
	  if ( ! column_change_allowed(formula_column) )
	    {
	      alert_append("Cette colonne est utilisée dans une formule qui ne peut être mise à jour car vous n'avez pas le droit.\nLe changement de ce titre est donc interdit.\nSeul le responsable de la table peut faire ce changement.") ;
	      return column.title ;
	    }
	  job_to_do.push([formula_column, 'columns', w]) ;
	}
      // Title change is possible
      for(var i in job_to_do)
	column_attr_set(job_to_do[i][0], job_to_do[i][1], job_to_do[i][2]) ;
    }
  column.title = value ;
  return column.title ;
}

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

function set_test_note(v, column)
{
  column.min = 0 ;
  column.max = 20 ;

  if ( v === '' )   // Should never be here except for old tables
    v = '[0;20]' ;
  
  value = v.replace(/;/g, ' ').replace(/\[/g, ' ').replace(/]/g, ' ').replace(/^ */, '').replace(/ *$/,'').split(/  */) ;

if ( value.length != 2 )
  {
    alert_append('Pour la colonne "' + column.title + '(' + column.type + ')".\nVous devez indiquer la note minimum et maximum\nsous la forme : [0;20]') ;
    return column.minmax ;
  }

if ( Number(value[0]) > Number(value[value.length-1]) )
    {
      alert_append('La note minimum doit être plus petite que la note maximum') ;
      return column.minmax ;
    }

column.need_update = true ;
column.min = a_float(value[0]) ;
if ( isNaN(column.min) )
  column.min = 0 ;

column.max = a_float(value[1]) ;
if ( isNaN(column.max) )
  {
    compute_column_stat(column) ;
    column.max = column.computed_max ;
  }
value = '[' + column.min + ';' + column.max + ']' ;

column.need_update = true ;

return value ;
}

/******************************************************************************
Check the 'weight' of a column.
******************************************************************************/

function set_weight(value, column)
{
  value = value.replace(',', '.') ;
  var v = a_float(value) ;

  column.real_weight_add = true ; // Pondered average

  if ( value === '?' && column.type == 'Moy' ) // XXX Only Moy ?
    {
      value = v = '?' ;
    }
  else if ( isNaN(v) )
    {
      v = 0 ;
      value = '0' ;
    }
  else if ( value === '' )
    {
      v = 1 ;
      value = '1' ;
    }
  else
    {
      if ( value.substr(0,1) == '+' || value.substr(0,1) == '-' )
	column.real_weight_add = false ;
    }

  column.real_weight = v ;
  column.need_update = true ;

  return value ;
}

function set_comment(value, column)
{
  var round_by = value.replace(/.*arrondi[es]* *[aà] *([0-9.,]*).*/i,'$1') ; 
  if ( round_by === '' )
    column.round_by = undefined ;
  else
    column.round_by = a_float(round_by) ;

  var best_of = value.replace(/.*oyenne *des *([0-9]*) *meilleur.*/i,'$1') ; 
  if ( best_of === '' )
    {
      if ( value.search('la meilleure note') == -1 )
	column.best_of = undefined ;
      else
	column.best_of = 1 ;
    }
  else
    column.best_of = a_float(best_of) ;

  var best_of = value.replace(/.*]([0-9]*),([0-9]*)\[.*/,'][ $1 $2').split(/ /) ;

  if ( best_of.length == 3 && best_of[0] == '][' )
    {
      column.best_of = - a_float(best_of[2]) ;
      if ( isNaN(column.best_of) )
	column.best_of = undefined ;

      column.mean_of = - a_float(best_of[1]) ;
      if ( isNaN(column.mean_of) )
	column.mean_of = undefined ;
    }
  else
    column.mean_of = undefined ;

  column.need_update = true ;

  return value ;
}

function set_columns(value, column, xcolumn_attr)
{
  var cols = [] ;
  var weight = 0 ;
  var ok ;

  value = value.replace(/ *$/,'').replace(/^ */,'') ;

  if ( value === '' )
    {
      column.average_from = [] ;
      column.average_columns = [] ;
      column.need_update = true ;
      return value ;
    }


  column.average_from = value.split(/ +/) ;

  for(var i=0; i<column.average_from.length; i++)
    {
      ok = false ;
      for(var c in columns)
	if ( columns[c].title == column.average_from[i] )
	  {
	    cols.push(c) ;
	    weight += columns[c].real_weight ;
	    ok = true ;
	    break ;
	  }
      if ( ! ok )
	{
	  if ( xcolumn_attr )
	    // Wait the good value
	    setTimeout(function() {set_columns(value, column, xcolumn_attr)},
		       1000) ;
	  else
	    {
	      alert_append("Je ne connais pas le titre de colonne '"
			   + column.average_from[i]
			   + "' qui est utilisé dans la moyenne de la colonne "
			   + column.title + "\n"
			   + "LA LISTE DES COLONNES N'A PAS ÉTÉ SAUVEGARDÉE"
			   ) ;
	      return null ; // Do not save, but leaves user input unchanged
	    }
	}
    }
  column.average_columns = cols ;
  column.average_weight = weight ;
  column.need_update = true ;
  if ( column.type == 'Nmbr' )
    column.max = column.average_columns.length ;

  return value ;
}

function set_visibility_date(value, column, interactive_modification)
{
  if ( value === '')
    return value ;
  v = get_date(value) ;
  if ( v == false )
    {
      alert_append("La date que vous donnez n'est pas valide : " + value) ;
      return column.visibility_date ;
    }
  if ( (v.getTime() - millisec())/(86400*1000) > 31 )
    {
      alert_append("La date de visibilité doit être dans moins d'un mois") ;
      return column.visibility_date ;
    }
  if ( interactive_modification && v.getTime() - millisec() < 0 )
    {
      alert_append("La date de visibilité ne doit pas être dans le passé") ;
      return column.visibility_date ;
    }
  v = ''+v.getFullYear()+two_digits(v.getMonth()+1)+two_digits(v.getDate()) ;
  return v ;
}

function returns_false() { return false ; } ;

function the_green_filter(c, column)
{
  return c.value > column.color_green ;
}

function set_green(value, column)
{
  if ( value === undefined )
    value = '' ;
  if ( value === '' )
    {
      column.color_green_filter = returns_false ;
    }
  else if ( value === 'NaN' )
    {
      column.color_green_filter = the_green_filter ;
      var stats = compute_histogram(column.data_col) ;
      column.color_green = stats.average() + stats.standard_deviation() ;
    }
  else if ( isNaN(value) )
    {
      column.color_green_filter = compile_filter_generic(value) ;
    }
  else
    {
      value = Number(value) ;
      column.color_green_filter = the_green_filter ;
      column.color_green = value ;
    }

  return value ;
}

function the_red_filter(c, column)
{
  return c.value < column.color_red ;
}

function set_red(value, column)
{
  if ( value === undefined )
    value = '' ;
  if ( value === '' )
    {
      column.color_red_filter = returns_false ;
    }
  else if ( value === 'NaN' )
    {
      column.color_red_filter = the_red_filter ;
      var stats = compute_histogram(column.data_col) ;
      column.color_red = stats.average() - stats.standard_deviation() ;
    }
  else if ( isNaN(value) )
    {
      column.color_red_filter = compile_filter_generic(value) ;
    }
  else
    {
      value = Number(value) ;
      column.color_red_filter = the_red_filter ;
      column.color_red = value ;
    }

  return value ;
}

function set_type(value, column)
{
  var checked = type_title_to_type(value) ;

  if ( column.real_type
       && column.real_type.cell_compute !== undefined
       && checked.cell_compute === undefined
       && lines[0][column.data_col]._save !== undefined
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

  return value ;
}

function set_test_enumeration(value, column)
{
  value = value.replace(/  */g, ' ') ;
  column.possible_values = value.split(' ') ;
  return value ;
}
