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

  if ( t.type == 'button' )
    switch(id)
      {
      case 'TS':
	create_popup('export_div',
		     "Exporter vers un tableur",
		     "Pour exporter les données du tableau actuel "
		     + "dans un tableur il faut passer "
		     + "par la page «Imprime» de TOMUSS qui vous permettra : "
		     + '<ul>'
		     + "<li> de choisir les colonnes à envoyer au tableur."
		     + "<li> de choisir le séparateur décimal."
		     + '</ul>'
		     + '<h3>Cliquez sur&nbsp;:&nbsp;<span class="gui_button" onmouseup="popup_close();print_selection()">Imprime</span></h3>'
		     ,
		     '', false) ;
	break ;
      case 'ST':
	create_popup('export_div',
		     "Recopier le contenu d'un tableur dans TOMUSS",
		     "<p>Si votre table TOMUSS n'est pas vide, "
		     + "il faut recopier le contenu du tableur colonne "
		     + "par colonne&nbsp;:"
		     + "<ul>"
		     + "<li> En sélectionnant la bonne colonne ;"
		     + "<li> en allant dans l'onglet «Colonne/Action» ;"
		     + "<li> puis en cliquant sur «Importer...»."
		     + "</ul>"
		     + "&nbsp;<br>"
		     + "<p>Si la table est vide, il est possible d'importer "
		     + "le tableau complet dans le format CSV. "
		     + "Pour cela faite comme si vous importiez une colonne, "
		     + "mais cliquez sur le lien en bas de fenêtre."
		     ,
		     '', false) ;
	break ;
      case 'F':
	var next_ys = next_year_semester(year, semester) ;
	create_popup('export_div',
		     'Copie de la table courante dans le futur.',
		     'Déroulement de la copie :'
		     + '<iframe width="100%" src="' + url + '/=' + ticket + '/'
		     + year + '/' + semester + '/' + ue + '/tablecopy/'
		     + next_ys[0] + '/' + next_ys[1] + '/' + option
		     + '">' + '</iframe>',
		     "", false) ;
	break ;
      case 'P':
	var previous_ys = previous_year_semester(year, semester) ;
	create_popup('export_div',
		     'Copie du passé dans la table courante.',
		     'Déroulement de la copie :'
		     + '<iframe width="100%" src="' + url + '/=' + ticket + '/'
		     + previous_ys[0] + '/' + previous_ys[1] + '/' + ue
		     + '/tablecopy/' + year + '/' + semester + '/' + option
		     + '">' + '</iframe>',
		     "", false) ;
	break ;
      case 'PY':
	create_popup('export_div',
		     'Copie de l"an passé dans la table courante.',
		     'Déroulement de la copie :'
		     + '<iframe width="100%" src="' + url + '/=' + ticket + '/'
		     + (year-1) + '/' + semester + '/' + ue
		     + '/tablecopy/' + year + '/' + semester + '/' + option
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
	  alert("Il est obligatoire de copier les définitions des colonnes") ;
	}
      if ( tablecopy_toggle('H') && ! tablecopy_toggle('C') )
	{
	  if ( id != 'H' )
	    alert("On ne peut pas copier l'historique sans le contenu") ;
	  tablecopy_toggle('C', true) ;
	}
    }
}



function table_copy()
{
  var future, past, ts, st, current, previous, next ;

  var next_ys = next_year_semester(year, semester) ;
  var previous_ys = previous_year_semester(year, semester) ;

  current = year + '<br>' + semester + '<br>' + ue ;
  previous_year = '<b>' + (year-1) + '</b><br>' + semester + '<br>' + ue ;
  previous = previous_ys[0] + '<br><b>' + previous_ys[1] + '</b><br>' + ue ;
  next = next_ys[0] + '<br>' + next_ys[1] + '<br>' + ue ;

  future = table_copy_button('F', '&nbsp;--&gt;&nbsp;',
			     'Dans le futur.<br>'
			     +'Action possible seulement si la table '
			     +"n'est pas vide.",
			     false, false) ;

  past_year = table_copy_button('PY', '&nbsp;--&gt;&nbsp;',
			   'Récupérer la table de l\'an passé.<br>'
			   +'Action possible seulement si la table courante '
			   +'est modifiable.<br>'
			   +'CECI FERME LA TABLE COURANTE, il faudra la rouvrir.'
			   ,
			   false, false) ;

  past = table_copy_button('P', '&nbsp;--&gt;&nbsp;',
			   'Récupérer la table du semestre passé.<br>'
			   +'Action possible seulement si la table courante '
			   +'est modifiable.<br>'
			   +'CECI FERME LA TABLE COURANTE, il faudra la rouvrir.'
			   ,
			   false, false) ;
    

  st = table_copy_button('ST', '&darr;',
			 "Copier le contenu d'un tableur dans TOMUSS",
			 false, false) ;

  ts = table_copy_button('TS', '&uarr;',
			 'Copier le contenu du tableau dans un tableur',
			 false, false) ;

  create_popup('import_div',
	       'Copie de table TOMUSS',
	       'Choisissez ce que vous voulez copier :<br>'
	       + table_copy_button('c', 'les définitions de colonne', 
				   'Les types, titres, commentaire...', true)
	       + 'et'
	       + table_copy_button('C', 'le contenu', 
				   'Les valeurs des cellules de la table.')
	       + 'et'
	       + table_copy_button('H', "l'historique", 
				   "L'historique de toutes les modifications")
	       + '<br>&nbsp;<br>'
	       + '<table class="table_copy_diagram"><tr><td colspan="2">Cliquez sur une flèche pour copier la bonne table.'
	       + '<th>Votre tableur préféré.<br>OpenOffice...<td><td></tr>'
	       + '<tr><td><td><td>' + st + '&nbsp;' + ts + '<td><td></tr>'
	       + '<tr><th>' + previous_year + '<td>' + past_year
	       + '<th rowspan="2"><b>' + current
	       + '<td rowspan="2">' + future + '<th rowspan="2">' + next + '</tr>'
	       + '<tr><th>' + previous + '<td>' + past
	       + '</table>'
	       , '', false) ;
}
