// -*- coding: utf-8 -*-
/*
    TOMUSS: The Online Multi User Simple Spreadsheet
    Copyright (C) 2008-2011 Thierry EXCOFFIER, Universite Claude Bernard

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

function printable_display_page(lines, title, page_break)
{

  var v, i, cell, line_id, tt = [], nr_lines ;
  var sorted = [] ;
  for(var c in columns)
    sorted.push(c) ;
  sorted.sort(function(a,b)
	      { return columns[a].position - columns[b].position ; }) ;

  for(var i=0;;i++)
    {
      var input = document.getElementById('free' + i) ;
      if ( ! input )
	break ;
      if ( input.value )
	sorted.push(input.value) ;
    }

  var s = [] ;
  var html_class = 'printable_table', th_class ;

  if ( uniform == 'oui' )
    html_class += ' tdnowrap' ;

  if ( page_break )
    th_class = ' style="page-break-before:always;"' ;
  else
    th_class = '' ;

  s.push('<h2' + th_class + '>' + year + ' ' + semester + ' ' + ue
	 + title + '</h2>') ;

  nr_lines = 0 ;
  tt = [] ;
  for(var line_id in lines)
    {
      cell = lines[line_id][columns.length] ;
      if ( cell )
	tt.push(lines[line_id][0].value + ' '
		+ lines[line_id][1].value + ' '
		+ lines[line_id][2].value + '<ul>'
		+ cell + '</ul>') ;
      nr_lines++ ;
    }

  if ( do_emargement_header )
    {
      if ( tt.length )
	v = ' dont <b>' + tt.length + ' tiers-temps</b>' ;
      else
	v = '' ;
      s.push(
	     '<table width="100%" style="white-space: pre ;">'
	     + '<tr style="vertical-align:top;"><td>'
	     + '<p>Date/Heure/Durée de l\'examen :'
	     + "<p>Surveillants :"
	     + "<p>Salle : " + 'salle'
	     + "<p>Nombre d'étudiants sur cette liste : <b>" + nr_lines + "</b>" + v
	     + "</td>"
	     + '<td><p>Nombre de présents :'
	     + "<p>Nombre de signatures :"
	     + "<p>Nombre de copies :"
	     + "</td></tr></table>"
	     ) ;
    }

  if ( tierstemps != 'seulement' )
    {
      s.push('<table class="' + html_class + '"><thead>') ;
      for(var header in headers_to_display)
	{
	  if ( ! headers_to_display[header] )
	    continue ;
	  s.push('<tr><td class="hidden_on_paper smaller" onclick="button_toggle(' 
		 + 'headers_to_display,\'' + header
		 + '\',document.getElementById(\'headers_to_display_'
		 + header + '\'));'
		 + 'do_printable_display=true;">'
		 + hidden_txt(header, first_line_of_tip(header)
			      + "<br>Cliquer pour cacher cette ligne") + '</td>') ;
	  for(var c in sorted)
	    {

	      c = sorted[c] ;
	      if ( isNaN(c) )
		{
		  if ( header == 'title' )
		    s.push('<th>' + html(c) + '</th>') ;
		  else
		    s.push('<th>&nbsp;</th>') ;
		  continue ;
		}
	      if ( ! columns_to_display[c] )
		continue ;

	      v = columns[c][header] ;
	      if ( v.length > 30 )
		th_class = ' smaller' ;
	      else if ( v.length > 10 )
		th_class = ' smaller' ;
	      else
		th_class = '' ;

	      if ( ! column_modifiable_attr(header, columns[c]) )
		v = '' ;

	      if ( v === '' )
		v = '&nbsp;' ;


	      s.push('<th onclick="button_toggle(columns_to_display,'
		     + c + ',document.getElementById(\'columns_to_display\').getElementsByTagName(\'SPAN\')['
		     + c + ']);do_printable_display=true" class="'
		     + th_class + '">'
		     + hidden_txt(v, "Cache cette colonne") + '</th>') ;
	    }
	  s.push('</tr>') ;
	}
      s.push('<thead>') ;
      i = 1 ;
      for(var line_id in lines)
	{
	  line = lines[line_id] ;
	  if ( nr_lines == i || i % preferences.zebra_step === 0 )
	    html_class = ' class="separatorvertical"' ;
	  else
	    html_class = '' ;
	  s.push('<tr' + html_class + '><td class="hidden_on_paper" onclick="delete lines[\'' + line_id + '\'];do_printable_display=true;">'
		 + hidden_txt(i, "Cache cette ligne") + '</td>') ;
	  i++ ;

	  for(var c in sorted)
	    {
	      c = sorted[c] ;
	      if ( isNaN(c) )
		{
		  s.push('<td>&nbsp;</td>') ;
		  continue ;
		}
	      if ( ! columns_to_display[c] )
		continue ;
	      cell = line[c] ;
	      html_class = '' ;
	      if ( cell.value.toFixed )
		{
		  html_class += ' number' ;
		  v = tofixed(cell.value) ;
		  if ( separator == 'la virgule' )
		    v = v.replace('.', ',') ;
		}
	      else
		v = cell.value_html() ;
	      if ( v === '' )
		v = '&nbsp;' ;
	      if ( columns[c].green_filter(cell, columns[c]) )
		html_class += ' color_green' ;
	      if ( columns[c].red_filter(cell, columns[c]) )
		html_class += ' color_red' ;
	    
	      s.push('<td class="' + html_class + '">' + v + '</td>') ;
	    }
	  s.push('</tr>') ;
	}
      s.push('</table>') ;
    }
  if ( tierstemps != 'non' && tt.length )
    s.push('<h2 style="page-break-before:always;">Tiers-temps</h2>' + tt.join('\n'));

  return s.join('\n') ;
}

function printable_display()
{
  if ( ! do_printable_display )
    return ;
  do_printable_display = false ;

  var groups = compute_groups_values(grouped_by) ;
  var x, selected_lines, i, title ;

  if ( do_emargement_header ) 
    for(var data_lin in lines)
      if ( ! display_on_signature_table(lines[data_lin]) )
	delete lines[data_lin] ;

  if ( groups.length == 1 )
    x = printable_display_page(lines, '', false) ;
  else
    {
      var t = [] ;
      for(var group in groups)
	{
	  group = groups[group] ;

	  i = 0 ;
	  title = [] ;
	  for(var g in grouped_by)
	    {
	      if ( grouped_by[g] )
		title.push(columns[g].title + '=' + group.split('\001')[i++]) ;
	    }
	  title = html(' ' + title.join(', ')) ;
	  selected_lines = {} ;
	  for(var data_lin in lines)
	    if ( compute_groups_key(grouped_by, lines[data_lin]) == group )
	      selected_lines[data_lin] = lines[data_lin] ;
	  t.push(printable_display_page(selected_lines,
					title,
					t.length != 0)) ;
	}
      x = t.join('\n');
    }

  document.getElementById('content').innerHTML = x ;
}

function display_button(data_col, title, selected, table_name, tip)
{
  if ( selected )
    selected = 'toggled' ;
  else
    selected = '' ;
  if ( ! tip )
    tip = '' ;
  return hidden_txt('<span class="button_toggle ' + selected
		    + '" onclick="button_toggle(' + table_name + ','
		    + data_col + ',this);do_printable_display=true;"'
		    + ' id="' + table_name + '_'
		    + data_col.replace(/\'/g,'')+ '">'
		    + html(title) + '</span>', tip) + '<script>'
    + table_name + '[' + data_col + '] =' + !!selected + '</script>' ;
}

function first_line_of_tip(attr)
{
  var tip = column_attributes[attr].tip ;
  if ( tip[''] ) // For 'columns' attribute
    tip = tip[''] ;
  if ( tip.split )
    tip = tip.split('</b>')[0].substr(3) ;
  return tip ;
}

function do_emargement()
{
  document.getElementById('free0').value = 'Présent' ;
  document.getElementById('free1').value = 'Signature copie rendue' ;
  for(var data_col in columns_to_display)
    {
      if ( (data_col < 3) !=  columns_to_display[data_col] )
	button_toggle(columns_to_display, data_col,
		      document.getElementById('columns_to_display_' + data_col)
		      );
    }
  for(var header in headers_to_display)
    {
      if ( (header == 'title') !=  headers_to_display[header] )
	button_toggle(headers_to_display, header,
		      document.getElementById('headers_to_display_' + header)
		      );
    }
  do_printable_display = true ;
  do_emargement_header = true ;
}

function do_page_per_group()
{
  for(var data_col in grouped_by)
    {
      if ( (data_col == 3 || data_col == 4) !=  grouped_by[data_col] )
	button_toggle(grouped_by, data_col,
		      document.getElementById('grouped_by_' + data_col)
		      );
    }
  do_printable_display = true ;
}

function print_choice_line(p, title, title_tip, choices, the_id)
{
  if ( the_id )
    the_id = ' id="' + the_id + '"' ;
  else
    the_id = '' ;
  p.push('<tr><td class="nowrap">' + hidden_txt(title, title_tip)
	 + '</td><td class="toggles"' + the_id + '>'
	 + choices + '</td></tr>') ;
}


function print_selection(object, emargement)
{
  var p = [ printable_introduction() ] ;
  p.push('<script>') ;
  p.push('var do_printable_display = true ;') ;
  p.push('var columns_to_display = {};') ;
  p.push('var headers_to_display = {};') ;
  p.push('var grouped_by = {};') ;
  p.push('var do_emargement_header = ' + emargement + ';') ;
  p.push('var tr_classname = "' + tr_classname + '";') ;
  p.push('var popup_on_red_line = ' + popup_on_red_line + ';') ;
  p.push('var ue = ' + js(ue) + ';') ;
  p.push('var display_tips = true ;') ;
  p.push('var columns = ' + columns_in_javascript() + ';') ;
  p.push('var lines ;') ;
  p.push('function initialize() {') ;
  p.push('if ( ! wait_scripts("initialize()") ) return ;') ;
  p.push('lines = ' + lines_in_javascript() + ';') ;
  p.push('setInterval("printable_display()", 200);') ;
  p.push('}') ;
  p.push('</script>') ;
  p.push('<p class="hidden_on_paper"><a href="javascript:do_emargement()">Je veux une feuille d\'émargement !</a>');
  p.push('<p class="hidden_on_paper"><a href="javascript:do_page_per_group()">Je veux une feuille par groupe !</a>');
  p.push('<p class="hidden_on_paper">Exporter dans un tableur : faites un copier/coller de toute la page dans votre tableur (Ctrl-A Ctrl-C Ctrl-V)');
  p.push('<table class="hidden_on_paper">') ;
  print_choice_line(p, 'Affiche tiers-temps',
		    'Si oui alors le détail sur les tiers-temps<br>'
		    + 'est indiqué sur une feuille à part.',
		    radio_buttons('tierstemps',['oui', 'non', 'seulement'], 'non')
		    ) ;
  print_choice_line(p, 'Séparateur décimal',
		    'Indiquez le séparateur décimal du tableur<br>'
		    + ' dans lequel vous voulez copier le tableau',
		    radio_buttons('separator',['la virgule', 'le point'],
				  'la virgule')) ;
  print_choice_line(p, 'Lignes uniformes',
		    'Si les lignes sont toutes de même hauteur<br>'
		    + ' alors le texte dans chaque cellule est<br>'
		    + ' obligatoirement sur une seule ligne.',
		    radio_buttons('uniform',['oui', 'non'], 'oui'));

  var t = [] ;
  for(var data_col in columns)
      if ( ! columns[data_col].is_empty )
	t.push(display_button(data_col, columns[data_col].title,
			      ! columns[data_col].hidden,
			      'columns_to_display',
			      html(columns[data_col].comment)));
  print_choice_line(p, 'Colonnes à afficher',
		    'Choisissez les colonnes à afficher.',
		    t.join(' '),
		    'columns_to_display') ;

  t = [] ;
  for(var data_col in columns)
    if ( ! columns[data_col].is_empty )
      t.push(display_button(data_col, columns[data_col].title,
			    false,
			    'grouped_by',
			    html(columns[data_col].comment)));
  print_choice_line(p, 'Paginer par',
		    'Critère indiquant quand il faut changer de page lors de l\'impression.<br>On peut utiliser ceci pour faire une feuille d\'émargement par salle de TP ou enseignant.',
		    t.join(' '),
		    'grouped_by') ;

  t = [] ;
  for(var i=0; i<2; i++)
    t.push('<input id="free' + i + '" style="width:15em" onkeypress="do_printable_display=true;">') ;
  print_choice_line(p, 'Colonnes à ajouter',
		    'Ceci vous permet d\'ajouter des colonnes vides<br>avec le titre de votre choix.',
		    '<small>' + t.join(' '),
		    'columns_to_display') ;

		    
  var attrs = [
	       ['title', 'Titre'],
	       ['type', 'Type'],
	       ['red', 'Rouge'],
	       ['green', 'Vert'],
	       ['weight', 'Poids'],
	       ['minmax', '[0;20]'],
	       ['empty_is', 'ø'],
	       ['comment', 'Commentaire'],
	       ['columns', 'Colonnes utilisées'],
	       ['enumeration', 'Énumération'],
	       ['test_filter', 'Fitre comptage'],
	       ['visibility_date', 'Date de visibilité']
	       ] ;
  t = [] ;
  for(var attr in attrs)
    {
      attr = attrs[attr] ;
      t.push(display_button("'"+attr[0]+"'", attr[1],
			    attr[0] == 'title', 'headers_to_display',
			    first_line_of_tip(attr[0]))) ;
    }
  print_choice_line(p, 'Entêtes à afficher',
		    'Les informations que vous désirez afficher concernant les colonnes',
		    t.join(' '),
		    'headers_to_display') ;

  p.push('</table>') ;
  p.push('<div style="clear:both" id="content"></div>') ;
  p.push('<script>') ;
  p.push('initialize() ;') ;
  p.push('</script>') ;

  var w = window_open() ;
  w.document.open('text/html') ;
  w.document.write(html_begin_head(true) + p.join('\n')) ;
  w.document.close() ;
  return w ;
}
