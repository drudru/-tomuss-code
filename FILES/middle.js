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

/*REDEFINE
This function is called to set the UE title links on the page.
*/
function change_title()
{
  var p_title_links = document.getElementById('title_links') ;
  if ( p_title_links == undefined )
     return ; // Linear interface
  // Use table_attr.code for example
  // p_title_links.innerHTML = '<a href="">xxx</a>' ;
}

/*REDEFINE
Some table lines must not be modified.
This function return 'true' to allow the line editing.
*/
function modification_allowed_on_this_line(data_lin,
					   data_col)
{
  if ( tr_classname === undefined )
    return true ;
  if ( ! popup_on_red_line )
    return true ;
  if ( lines[data_lin][tr_classname].value == 'non' )
    return true ; // Returns false here to forbid red line editing
  return true ;
}

/*REDEFINE
*/
function update_student_information(line)
{
}

function head_html()
{
  if ( window.location.pathname.search('=read-only=') != -1 )
    table_attr.modifiable = false ;

  if ( window.location.pathname.search('/=linear=') != -1 )
    preferences.interface = 'L' ;
  if ( preferences.interface == 'L' )
    {
      return '</head><body id="body" onunload="send_key_history()" class="tomuss">' +
	'<style>' +
	'ul { margin-top: 0px ; margin-bottom: 0px; }\n' +
	'@media speech { u { pause-after: 1s; } }\n' +
	'@media aural { u { pause-after: 1s; } }\n' +
	'u { pause-after: 1s; }\n' +
	'</style>' +
	'<script src="' + url + '/linear.js"> </script>' +
	'<div id="loading_bar"><div></div></div>' +
	'<div id="top"></div><input onkeydown="dispatch2(the_event(event))" onkeypress="dispatch(the_event(event))" style="width:1em"><div id="log"></div>' ;
    }

  var w ;

  if ( semester == 'Printemps' || semester == 'Automne' )
    w = '<link href="' + suivi.split('/=')[0] + '/rss2/' + ue + '" rel="alternate" title="TOMUSS" type="application/rss+xml">' ;
  else
    w = '' ;



  w += '<title>' + ue + ' ' + year + ' ' + semester + ' ' + my_identity
    + '</title></head>' ;


  w += '<body id="body" class="tomuss" onunload="the_current_cell.change();" onkeydown="the_current_cell.keydown(event, false)">' +
    // This message is visible in FireFox (bug ?)
    //   '<noscript>Activez JavaScript et réactualisez la page</noscript>'+
   '<div class="identity">' +
   '<p>' +
   '<a href="' + url + '/=' + ticket + '/logout">Déconnexion</a> <b>' +
    my_identity + '</b>' ;

    if ( semester == 'Printemps' || semester == 'Automne' )
      w += '<a href="' + suivi.split('/=')[0] + '/rss2/' + ue + '"><img style="border:0px" src="' + url + '/feed.png"></a>' ;

 w += hidden_txt('<a href="_URL_/doc_table.html" target="_blank">Documentation</a>',
		 "Cliquez sur le lien pour avoir tous les détails sur<br>" +
		 "l'utilisation de ce tableur") + ', ' ;

 w += hidden_txt('<span class="ro">S</span><span class="comment">t</span><span class="today">y</span><span class="is_an_abj">l</span><span class="non">e</span><span class="tt">s</span>',
		 "<span class=\"ro\">Le texte est gris si la cellule est définie par quelqu'un d'autre.</span><br>" +
		 "<span class=\"comment\">Le texte est en italique s'il y a un commentaire.</span><br>" +
		 "<span class=\"today\">Le texte est gras si la cellule a été modifiée aujourd'hui.</span><br>" +
		 "<span class=\"is_an_abj\">Si ABINJ est souligné, cliquez dessus pour vérifier s'il a un justificatif.</span><br>" +
		 "<span class=\"non\">Le fond est rouge si l'étudiant n'est pas inscrit à l'UE.</span><br>" +
		 "<span class=\"tt\">Le fond est bleu si l'étudiant a un tiers temps.</span><br>" +
		 "<span class=\"filtered\">Le fond est jaune si la cellule est sélectionnée par le filtre de table</span>") + ',' ;
 w += hidden_txt('&nbsp;<img class="server" src="data:"> ',
	    'Ce petit carré apparaît quand :<br>' +
	    'on essaye de stocker la valeur sur le serveur,<br>' +
	    'si cela dure plus de 5 secondes il y a un <b>problème</b> (réseaux ?),<br>' +
	    'évitez de saisir des valeurs dans ces conditions.') ;
 w += hidden_txt('&nbsp;<img class="server" src="_URL_/ok.png"> ',
	    'Ce petit carré apparaît quand :<br>' +
	    'la valeur a été <b>stockée avec succès</b> sur le serveur') ;
 w += hidden_txt('&nbsp;<img class="server" src="_URL_/bad.png"> ',
	    'Ce petit carré apparaît quand :<br>' +
	    'le serveur <b>refuse de stocker cette valeur</b>.<br>' +
	    'C\'est certainement du à un problème de droit') ;
 w += hidden_txt('&nbsp;<img class="server" src="_URL_/bug.png">',
	    'Ce petit carré apparaît quand :<br>' +
	    'Il y a un <b>bug</b> quelque part,<br>'+
	    'le responsable du logiciel a reçu un message le prévenant.') +
   ', ' ;
 w += hidden_txt('<a href="' + url + '/=' + ticket + '/0/Preferences/'
		 + my_identity2 + '" target="_blank">Préférences</a>',
		 "Ce lien vous permet de régler les préférences.<br>" +
		 "Les préférences sont appliquées à <b>tous</b> les tableaux");
 
 w += '</div><h1>'  ;

 var semester_class ;
 if ( semester == 'Printemps' )
   semester_class = "spring" ;
 else if ( semester == 'Automne' )
   semester_class = "autumn" ;
 else
   semester_class = '' ;

 var options ;
 if ( semester_class !== '' )
   {
     options = "__OPTIONS__" ;
     options = options.replace('>' + year + '/' + semester,
			       ' selected>' + year + '/' + semester) ;

     options = '<select onchange="semester_change(this);" class="'
       + semester_class + '">' + options + '</select>' ;
   }
 else
   {
     options = '<span class="' + semester_class + '">' + year + ' '
       + semester + '</span>' ;
   }

 w += options + ' ' + ue ;
 w += '<span id="title_links"></span></h1><h1><span id="t_table_attr_table_title"></span></h1>' ;

 return w ;
}

function semester_change(t)
{
  t.blur() ;
  window.open(url + '/=' + ticket + '/'
	      + t.childNodes[t.selectedIndex].innerHTML + '/' + ue) ;
}


function one_line(text, tip)
{
  return '<div class="one_line">' + hidden_txt(text, tip) + '</div>' ;
}

function column_attr_set(column, attr, value, td)
{
  var old_value = column[attr] ;
  var i_can_modify_column = column_change_allowed(column) ;

  if ( old_value == value )
    {
      if ( ! i_can_modify_column )
	return ;
      // Save the value even if the value is unmodified
      if ( attr != 'width' && attr != 'position' )
	return ;
    }

  if ( column_attributes[attr].need_authorization && ! i_can_modify_column )
    {
      if ( column.author == '*' )
	alert_append("Vous n'êtes pas autorisé à modifier cette valeur,\ncar elle a été définie par le système") ;
      else
	alert_append("Vous n'êtes pas autorisé à modifier cette valeur.\nSeul '" + column.author + "' qui a saisie la valeur peut le faire.\nOu bien l'un des responsables d'UE : " + teachers) ;
      return ;
    }

  if ( column.is_empty && column.data_col > 0
       && columns[column.data_col-1].is_empty )
    {
      alert_append("Il faut créer les colonnes de gauche à droite.\n\n" +
	    "Quand vous rechargerez la page, les colonnes ne\n" +
	    "seront pas dans le même ordre.\n" +
	    "C'est un bug compliqué à corriger, cela ne sera pas fait.") ;
    }

  var new_value = column_parse_attr(attr, value, column, td === undefined) ;

  if ( old_value === new_value && attr != 'width' && attr != 'position' )
    return ;

  if ( column_attributes[attr].empty(column, old_value) && new_value == '')
    return ; // The value stays empty...

  if ( new_value === null )
    return null ; // Do not store, but leave unchanged in user interface

  if ( create_column(column) && attr == 'title' )
    return new_value ; // The title is yet sended to the server

  column[attr] = new_value ;  

  if ( i_can_modify_column )
    {
      append_image(td, 'column_attr_' + attr + '/' + column.the_id + '/' +
		   encode_uri(new_value)) ;
      if ( column.author != my_identity )
	{
	  column.author = my_identity ;
	  the_current_cell.do_update_column_headers = true ;
	}
    }

  return new_value ;
}

function table_change_allowed()
{
  return i_am_the_teacher || i_am_root || !table_attr.masters[0] ;
}


function table_attr_set(attr, value, td)
{
  var old_value = table_attr[attr] ;

  if ( old_value == value )
    return  ;

  if ( ! table_change_allowed() )
    {
      alert_append("Vous n'êtes pas autorisé à modifier cette valeur.\nSeul l'un des responsables d'UE peut le faire : " + teachers) ;
      return ;
    }

  value = table_attributes[attr].formatter(value) ;

  if ( old_value == value )
    return  ;

  if ( value === undefined )
    return old_value ;

  table_attr[attr] = value ;

  append_image(td, 'table_attr_' + attr + '/' + encode_uri(value),
	       attr == 'modifiable') ;

  return value ;
}

function attr_update_user_interface(attr, column, force_update_header)
{
  attr = column_attributes[attr] ;

  if ( column.need_update )
    {
      update_columns() ;
      update_histogram(true) ;
    }
  if ( attr.display_table || column.need_update )
    table_fill(true, false, true) ;
  if ( attr.update_horizontal_scrollbar )
    update_horizontal_scrollbar() ;

  if ( (force_update_header || attr.update_headers)
       && column == the_current_cell.column )
    {
      the_current_cell.do_update_column_headers = true ;
      the_current_cell.update_headers() ;
    }
if ( attr.update_table_headers )
    table_header_fill() ;
}

function header_change_on_update(event, input, what)
{
  var column = the_current_cell.column ;

  if ( what.match(/^column_attr_/) )
    {
      var td = the_td(event) ;
      var attr = what.replace('column_attr_','') ;
      var new_value ;

      if ( input.selectedIndex !== undefined )
	new_value = index_to_type(input.selectedIndex) ;
      else
	new_value = input.value ;

      new_value = column_attr_set(column, attr, new_value, td) ;

      if ( new_value === undefined )
	{
	  input.value = input.theoldvalue ;
	  return ;
	}

      if ( new_value === null )
	return ; // Not stored, but leave user input unchanged
      
      if ( input.selectedIndex === undefined )
	input.value = column_attributes[attr].formatter(column, new_value) ;

      if ( attr == 'type' )
	init_column(column) ; // Need to update other attributes.

      input.theoldvalue = new_value ;
      attr_update_user_interface(attr, column) ;
    }

  if ( what.match(/^table_attr_/) )
    {
      var td = the_td(event) ;
      var attr = what.replace('table_attr_','') ;
      var new_value ;

      if ( input.selectedIndex !== undefined )
	new_value = input.selectedIndex ;
      else
	new_value = input.value ;

      new_value = table_attr_set(attr, new_value, td) ;

      if ( new_value === undefined )
	{
	  if ( input.selectedIndex === undefined )
	    input.value = input.theoldvalue ;
	  else
	    input.selectedIndex = Number(table_attr[attr]) ;
	  return ;
	}
      
      if ( input.selectedIndex === undefined )
	input.value = table_attributes[attr].formatter(new_value) ;

      input.theoldvalue = new_value ;
      the_current_cell.update_table_headers();
    }
  else
    {
      // Input in the TABLE
      switch(input.parentNode.parentNode.className)
	{
	case 'filter':
	  column.filter = set_filter_generic(input.value, column) ;
	  update_filters() ;
	  update_histogram(true) ;
	  table_fill(true, false, true) ;
	  break ;
	}
    }
}

/*
  The definition of an input that dispatch update correctly
  and return focus in the table on key up/down/return
*/
function header_input(the_id, the_header_name, options)
{
  var classe='', onkey='', before='' ;
  // Don't call onblur twice (IE bug) : so no blur if not focused
  var onblur='if(element_focused===undefined)return;element_focused=undefined;';

  if ( options && options.search('"') != -1 )
    alert('BUG : header_input parameter') ;

  if ( the_header_name !== '' )
    {
      onblur += "header_change_on_update(event,this,'"+the_header_name + "');";
    }

  if ( options && options.search('empty') != -1 )
    {
      onblur += "if ( this.value === '') this.className = 'empty';" ;
      classe = 'empty' ;
    }
  if ( options && options.search('onblur=') != -1 )
    onblur += options.split('onblur=')[1].split(' ')[0] + ';' ;
  if ( options && options.search('onkey=') != -1 )
    onkey = options.split('onkey=')[1].split(' ')[0] ;
  if ( options && options.search('before=') != -1 )
    before = options.split('before=')[1].split(' ')[0] ;
  if ( options && options.search('one_line') != -1 )
    classe += ' one_line' ;

  return before+'<input type="text" id="' + the_id + '" class="' + classe
    + '" onfocus="if ( this.tomuss_editable === false ) this.blur() ; else { this.className=\'\';element_focused=this;}" '
    + ' onblur="' + onblur
    + '" onkeyup="' + onkey  +'">' ;
}


function column_input_attr(attr, options)
{
  return hidden_txt(header_input("t_column_" + attr,
				 "column_attr_" + attr,
				 options)
		    ,'') ;
}

function table_input_attr(attr, options, tip)
{
  return hidden_txt(header_input("t_table_attr_" + attr,
				 "table_attr_" + attr,
				 options)
		    ,tip) ;
}

function column_select(attr, options, tip)
{
  var s = '<SELECT onfocus="take_focus(this);" id="t_column_' + attr
    + '" onChange="this.blur();header_change_on_update(event, this, \'column_attr_' + attr + '\');">' ;
  for(var i in options)
    s += '<OPTION>' + options[i] + '</OPTION>' ;
  return hidden_txt(s + '</SELECT>', '') ;
}

function table_select(attr, options, tip)
{
  var s = '<SELECT id="t_' + attr + '" onblur="if(element_focused===undefined)return;element_focused=undefined;" onchange="header_change_on_update(event,this,\''+ attr + '\');" onfocus="take_focus(this);">' ;

  for(var i in options)
    s += '<OPTION>' + options[i] + '</OPTION>' ;

  s += '</SELECT>' ;
  
  return hidden_txt(s, tip) ;
}

function new_interface()
{
var w ;

/* The boxes title */

 w = '<table id="menutop"><tr>\n<td>' +
   hidden_txt('Cellule &amp; ligne\n',
	      "Informations concernant la cellule active dans le tableau",
	      'title') +
   '<td class="space"><td>' +
   hidden_txt('Colonne\n',
	      "Informations concernant la colonne contenant<br>" +
	      "la cellule active dans le tableau",
	      'title') +
   '<td class="space"><td>' +
   hidden_txt('Tableau\n',
	      "Informations concernant le tableau complet",
	      'title') +
   '</tr><tr>' +

/* The boxes top part */

   '<td class="blocktop"><table class="cell"><tr><td>' +
   hidden_txt('<a href="" target="_blank"><img id="t_student_picture" class="phot"></a>',
	      'Cliquez sur la photo pour voir la fiche de suivi de l\'étudiant') +
   '</td><td>' +
   one_line('<span id="t_value"></span>', "Valeur de la cellule.") +
   one_line('<span id="t_student_firstname"></span>',"Prénom de l'étudiant.")+
   one_line('<span id="t_student_surname"></span>',"Nom de l'étudiant.")+
   one_line('<span id="t_student_id"></span>', "Numéro d'étudiant.")+
   one_line('<span id="t_date"></span>',
	    "Date ou la cellule a été modifiée pour la dernière fois.")+
   one_line('<span id="t_history"></span>',
	    "Valeurs précédentes prises par la cellule.<br>"+
	    "De la plus ancienne à la plus récente.<br>" +
	    "Le nom de la personne qui a fait la modification<br>" +
	    "est indiqué si la valeur précédente n'était<br>" +
	    "pas saisie par elle.") +
   '</td></tr></table><td class="space"><td class="blocktop">' +
   column_input_attr('title', 'one_line') +
   '<div>' ;

var options = [] ;
for(var type_i in types)
  {
    if ( types[type_i].full_title )
      options.push(types[type_i].full_title) ;
    else
      options.push(types[type_i].title) ;
  }
 
 w += column_select('type', options, '') +
   column_input_attr('red') +
   column_input_attr('green') +
   column_input_attr('weight') +
   column_input_attr('minmax') +
   column_input_attr('test_filter') +
   '<div><div style="height: 1.5em">' +
   column_input_attr('visibility_date') +
   column_input_attr('empty_is', 'before=&#8709;=') +
   column_input_attr('enumeration') +
   column_input_attr('columns') + '&nbsp;</div>' +

/* Use a TABLE because text-align: justify doesn't work */
   '<div class="menu"><table><tr><td>' +
   hidden_txt('<a href="javascript:do_move_column_left();">«</a>',
	      "<b>Décale la colonne vers la gauche</b><br>" +
	      "Ce changement n'est pas visible par les autres utilisateurs."
	      ) +
   hidden_txt('<span id="t_save_position"><a href="javascript:save_position_column(the_current_cell.column,document.getElementById(\'t_save_position\'))">P</a></span>',
	      "<b>Sauve la position courante de cette colonne</b>.<br>" +
	      "Le changement sera alors visible par les autres."
	      ) +
   hidden_txt('<a href="javascript:do_move_column_right();">»</a>',
	      "<b>Décale la colonne vers la droite</b><br>" +
	      "Ce changement n'est pas visible par les autres utilisateurs."
	      ) +
   '</td><td>' +

   hidden_txt('<a href="javascript:smaller_column();">-</a>',
	      "<b>Amincir la colonne</b><br>" +
	      "Ce changement n'est pas visible par les autres utilisateurs."
	      ) + '&nbsp;' +
   hidden_txt('<span id="t_save_width"><a href="javascript:save_width_column(the_current_cell.column,document.getElementById(\'t_save_width\'))">L</a></span>',
	      "<b>Sauve la largeur courante de cette colonne</b>.<br>" +
	      "Le changement sera alors visible par les autres."
	      ) + '&nbsp;' +
   hidden_txt('<a href="javascript:bigger_column();">+</a>',
	      "<b>Élargir la colonne</b><br>" +
	      "Ce changement n'est pas visible par les autres utilisateurs."
	      ) + '</td><td>' +
   hidden_txt('<a href="javascript:import_column();">Imp.</a>',
	      "<b>Importer</b> des valeurs dans cette colonne.<br>" +
	      "Cliquez pour avoir plus d'information"
	      ) + '</td><td>' +
   hidden_txt('<a href="javascript:fill_column();">Remp.</a>',
	      "<b>Remplir</b> cette colonne avec des valeurs.<br>" +
	      "Plusieurs méthodes sont possibles."
	      ) + '</td><td>' +
   hidden_txt('<a href="javascript:export_column();">Exp.</a>',
	      "<b>Exporter</b> les valeurs de cette colonne<br>" +
	      "afin de les importer dans les fichiers pour APOGÉE<br>" +
	      "Cliquez pour avoir plus d'information"
	      ) + '</td><td>' +
   hidden_txt('<a href="javascript:column_delete();">Dét.</a>',
	      "<b>Détruit cette colonne</b> si elle est vide.<br>" +
	      "CETTE ACTION N'EST PAS RÉVERSIBLE"
	      ) + '</td><td>' +
   hidden_txt('<a href="javascript:freeze_column();" id="t_column_fixed">Fige</a>',
	      "<b>Fige ou défige cette colonne</b><br>" +
	      "Une fois figée elle est toujours affichée,<br>" +
	      "même quand il y a des filtres ou décalages.<br>" +
	      "Les colonnes figées sont callées à gauche du tableau."
	      ) + '</td><td>' +
   hidden_txt('<a href="javascript:hide_column();">&times;</a>',
	      "<b>Cache cette colonne</b><br>" +
	      "Ce changement n'est pas visible par les<br>" +
	      "autres utilisateurs.<br>" +
	      "Une fois cachée, il faut actualiser la page<br>" +
	      "pour la faire réapparaître"
	      ) +

   '</td></tr></table></div><table id="t_column_stats"><tr><td>' +


   hidden_txt('<div id="t_column_histogram"></div>',
	      "Histogramme des valeurs des cellules de la colonne<br>"+
	      "en tenant compte du filtrage.<br>"+
	      "Les colonnes de gauche indiquent le nombre de cases<br>"+
	      "contenant des valeurs particulières :<br>" +
	      "PPN, ABI, ABJ, PRE, OUI, NON et vide"
	      ) + '</td><td class="m">' +

   hidden_txt('<div id="t_column_average"></div>',
	      "Moyenne des nombres de la colonne.") + '</td></tr></table>' +
 
   '<td class="space"><td class="blocktop">' +
   hidden_txt('<span id="nr_filtered_lines"></span>/<span id="nr_not_empty_lines"></span> lignes',
	      "Nombre de lignes filtrées et<br>" +
	      "nombre de lignes dans le tableau total") + ', ' +

   hidden_txt('<select onfocus="take_focus(this);" id="nr_lines" onChange="this.blur();change_table_size(this);update_line_menu()"></select>',
	      "Nombre de <b>lignes</b> affichées sur l'écran.") + '&times;' +
   hidden_txt("<select onfocus=\"take_focus(this);\" id=\"nr_cols\" onChange=\"this.blur();change_table_size(this);update_column_menu()\"></select>",
	      "Nombre de <b>colonnes</b> affichées sur l'écran.") + '<br>' +
   hidden_txt('<select onfocus="take_focus(this);" onchange="this.blur();if ( this.selectedIndex == 1) students_pictures() ; else if ( this.selectedIndex == 2) students_pictures_per_grp_seq(); this.selectedIndex = 0 ;"><option selected="1">Trombinoscope</option><option>Des étudiants filtrés</option><option>Idem, une page par groupe</option></select>',
	      'Ouvre une nouvelle page avec le <b>trombinoscope</b>.<br>' +
	      'Seuls les étudiants filtrés seront affichés.<br>' +
	      "L'ordre d'affichage est celui de la table.<br>" +
	      "Le deuxième choix permet d'imprimer une page par groupe.") +
   hidden_txt('<select onfocus="take_focus(this);" onchange="this.blur();if ( this.selectedIndex == 1) print_page(); else if ( this.selectedIndex == 2) signatures_page() ; if ( this.selectedIndex == 3) signatures_page_grp_seq() ; if ( this.selectedIndex == 4) signatures_page_per_column() ; if ( this.selectedIndex == 5) goto_resume() ; if ( this.selectedIndex == 6) abj_per_day() ; this.selectedIndex = 0 ;"><option selected="1">Imprime</option><option>Table totale filtrée</option><option>Émargement filtrée</option><option>Émargement par groupe</option><option>Émargement par valeur</option><option>ABJ, DA et TT</option><option>ABJ par date</option></select>',
	      "Ceci permet d'ouvrir une nouvelle fenêtre<br>" +
	      "faite pour être imprimée ou <b>exportée</b> vers un tableur.<br>"+
	      'Seuls les étudiants filtrés seront affichés.') +
   hidden_txt('<select onmousedown="javascript:mail_window();setTimeout(\'linefilter.focus()\',100)"><option>Mails</option></select>',
	      "Gestion des mails") +
   hidden_txt('<select onfocus="take_focus(this);" onchange="this.blur();if ( this.selectedIndex == 1) statistics(); else if ( this.selectedIndex == 2) statistics_per_group() ; if ( this.selectedIndex == 3) statistics_authors() ; else if ( this.selectedIndex == 4) table_graph(); this.selectedIndex = 0 ;"><option selected="1">Statistiques</option><option>Totales</option><option>Par groupe d\'étudiant</option><option>Par enseignant</option><option>Représentation graphique de la table</option></select>',
	      "Ceci permet d'ouvrir une nouvelle fenêtre<br>" +
	      "contenant des <b>statistiques</b> sur les notes.<br>" +
	      'Les statistiques concernent les lignes et colonnes filtrées.'
	      ) + '<br>' +

   '<div class="menu">' +
   hidden_txt('<a href="javascript:change_popup_on_red_line()">&nbsp;</a>',
	      "Cliquez-ici pour basculer entre le mode tenant compte<br>" +
	      "des inscriptions pédagogiques et celui n'en tenant pas compte."
	      ,'','popup_on_red_line') +
   hidden_txt('<a href="javascript:bookmark_this();">Options</a>',
	      '<b>Sauve les options d\'affichage</b><br>' +
	      'Une fois ce lien suivi vous arriverez sur une page (identique)<br>' +
	      'sur laquelle vous pourrez garder un signet (favori) vous<br>' +
	      'permettant de retrouver les paramètres d\'affichage&nbsp;:<br>' +
	      '* Nombre de lignes/colonnes.<br>' +
	      '* Les colonnes cachées.<br>' +
	      '* Les colonnes figées.<br>' +
	      '* Les filtres.<br>' +
	      '* Les colonnes triées.<br>' +
	      '* ...') + ', ' +
   hidden_txt('<a href="javascript:auto_save_deactivate();">AutoSauve</a>',
	      "<b>Désactive la sauvegarde automatique</b><br>" +
	      'Actuellement, chaque fois que vous modifiez une valeur,<br>' +
	      'elle est immédiatement sauvegardée.<br>' +
	      'En suivant ce lien, vous pourrez sauvegarder seulement<br>' +
	      'au moment où vous le désirez.', '','auto_save_deactivate') +

   hidden_txt('<a href="javascript:auto_save_activate();" style="text-decoration: line-through">AutoSauve</a>',
	      'Sauvegarde les modifications qui n\'ont pas encore été sauvegardées,<br>' +
	      'puis revient à la sauvegarde automatique.<br>' +
	      'Si vous ne VOULEZ PAS sauvegarder, rechargez (réactualisez) la page.',
	      '', 'auto_save_activate') + ', ' +
   hidden_txt('<a href="javascript:window.location = \'/=\' + ticket + \'/\' + year + \'/\' + semester + \'/\' + ue + \'/=linear=\';" >Lin.</a>',
	      "<b>Interface utilisateur linéaire.</b><br>" +
	      "Si vous suivez ce lien l'interface utilisateur deviendra linéaire<br>"+
	      'Cette interface linéaire est adaptée aux petits écrans.<br>' +
	      'Elle permet de naviguer en utilisant de gros caractères.') +
   ', ' +
   hidden_txt('<a href="javascript:import_columns();">Imp.</a>',
	      'Importe les définitions des colonnes.') + ', ' +

   hidden_txt('<a href="javascript:export_columns();">Exp.</a>',
	      'Exporte les définitions des colonnes (pas le contenu de la table)')+ '<br>' +
   
   table_select('table_attr_private',
		['Publique', 'Privée'],
		'Une table publiques est visible/modifiable par TOUS les <b>enseignants</b>.<br>Une table privée est seulement visible/modifiable par les responsables,<br>les étudiants pourront néanmoins voir leur suivi.') +

   table_select('table_attr_modifiable',
		['Non Modifiable', 'Modifiable'],
		'Dans une table «Non Modifiable» <b>personne</b> ne peut changer son contenu.') ;

 w += table_input_attr('default_nr_columns','',
		       "Impose ce nombre de colonnes affichées à tous le monde<br>" +
		       "'0' indique que ce nombre dépend de la taille écran."
		       ) ;

   w += '<br></div>' +

   table_input_attr('dates','empty',
		    "Dates du premier cours et dernier examen.<br>" +
		    "Par exemple : 20/1/2010 12/5/2010<br>" +
		    "Les ABJ en dehors de cet intervalle ne seront pas affichées.") +
   '</tr><tr><td class="blockbottom">' +

   one_line('<span id="t_author"></span>',
	    "Personne qui a modifié la cellule pour la dernière fois :") +
   hidden_txt(header_input('comment','',
			   'empty onblur=comment_on_change(event)')
	      + '<br>',
	      "Tapez un commentaire pour cette cellule<br>" +
	      "afin de ne pas oublier les choses importantes.<br>" +
	      "Le texte des cellules avec un commentaire est en italique.<br>"+
	      "<b>ATTENTION : les étudiants voient ce commentaire</b>") +
   hidden_txt(header_input('linefilter','',
			   'empty onkey=line_filter_change(this)'),
	      "<span class=\"shortcut\">(Alt-8)</span>" +
	      "<b>Filtre les lignes</b><br>" +
	      "Seules les lignes contenant une valeur filtrée seront affichées.<br>" +
	      "Tapez le début de ce que vous cherchez."
	      ) +
   '<td class="space"><td class="blockbottom">' +
   one_line('<span id="t_column_author"></span>',
	    "Personne qui a modifié la définition<br>" +
	    "de la colonne pour la dernière fois :") +
   column_input_attr('comment', 'empty one_line') +
   hidden_txt(header_input("columns_filter",'',
			   'empty onkey=columns_filter_change(this)'),
	      "Seules les <b>colonnes</b> dont le nom est filtré seront affichées.<br>" +
	      "Tapez le début de ce que vous cherchez.<br>" +
	      "Pour plus d'information, regardez l'aide sur les filtres.") +
   '<td class="space"><td class="blockbottom">' +
   table_input_attr('masters','empty',"Liste des LOGINS d'enseignants ayant tous les droits sur la table.<br>Les logins sont séparés par un espace.<br><b>Ajoutez votre nom en premier !</b><br>Tapez sur la touche «Entrée» pour valider.") +
   table_input_attr("comment",'empty',
		    "Tapez un commentaire pour cette table.<br>" +
		    "Ce commentaire sera visible par les étudiants<br>" +
		    "dans leur suivi, précédé du texte : " +
		    "«<em>Petit message</em>»"
		    ) + '<br>' +
   hidden_txt(header_input('fullfilter', '',
			   'empty onkey=full_filter_change(this)'),
	      "Seule les <b>colonnes et lignes</b> contenant une valeur filtrée<br>seront affichées (c'est un filtre).<br>" +
	      "Tapez le début de ce que vous cherchez.<br>"
	     ) +
 '</tr></table>' +

/* onmouseout is here because it must contains the tip
    If you change the content, read 'table_init' in 'lib.js'
*/
   '<div class="horizontal_scrollbar"><img src="' + url + '/prev.gif" onclick="javascript:previous_page_horizontal();"><div id="horizontal_scrollbar"></div><img src="' + url + '/next.gif" onclick="javascript:next_page_horizontal();"></div>' +
   '<div>' ;

 if ( ! scrollbar_right )
   w += '<div id="vertical_scrollbar"></div>' ;
w += '<div id="divtable" class="colored"><div id="hover"></div><div id="tip"></div></div>' ;
 if ( scrollbar_right )
   w += '<div id="vertical_scrollbar"></div>' ;
 w += '</div><div id="popup"></div>' +
   '</div><div id="loading_bar"><div></div></div>' ;

 return w ;
}

function popup_close()
{
  element_focused = undefined ;
  var e = document.getElementById('popup_id') ;
  if ( e )
    e.parentNode.removeChild(e);
}

function parse_lines(text)
{
  text = text.replace(/\r\n/g, '\n').replace(/\n\r/g, '\n').
              replace(/\r/g, '\n').replace(/ *\n */g, "\n").
              replace(/ *$/g, "").split('\n') ;

  while ( text.length > 1 && text.length && text[text.length-1] === '' )
    text.pop() ;

  return text ;
}

function popup_value()
{
  var e = document.getElementById('popup_id') ;
  text_area = e.getElementsByTagName('TEXTAREA')[0] ;
  return parse_lines(text_area.value) ;
}

function popup_set_value(value)
{
  var e = document.getElementById('popup_id') ;
  text_area = e.getElementsByTagName('TEXTAREA')[0] ;
  text_area.value = value ;
  text_area.focus() ;
  text_area.select() ;
}

function popup_is_open()
{
  return !! document.getElementById('popup_id') ;
}


function popup_column()
{
  return document.getElementById('popup').column ;
}

function create_popup(html_class, title, before, after)
{
  popup_close() ;

  var popup = document.getElementById('popup') ;

  popup.innerHTML += '<div id="popup_id" class="import_export ' +
    html_class + '"><h2>' + title
    + '</h2>' + before +
    '<TEXTAREA ROWS="10" class="popup_input" onfocus="element_focused=this;"></TEXTAREA>'+
    '<BUTTON class="close" OnClick="popup_close()">&times;</BUTTON>' +
    after ;

  popup.column = the_current_cell.column ;
}


function fill_column()
{
  var m = '' ;

  if ( auto_save )
    m = '<div style="text-align:right" id="stop_the_auto_save">' +
      'Cette opération ne sera pas annulable.<br>' +
      'Désactivez la <a href="#" onclick="auto_save_deactivate();document.getElementById(\'stop_the_auto_save\').style.display=\'none\';">'+
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
  popup_close() ;
  table_fill() ;
}


function tail_html()
{
  if ( preferences.interface == 'L' )
    {
      return '<span id="server_feedback"></span><div id="authenticate"></div>'
	+ "<script>lib_init() ; dispatch('init');</script>";
    }

  var a = '<p class="copyright"><span id="server_feedback"></span></p>' +
    '<div id="log"></div>' +
    '<div id="message">&nbsp;</div>' +
    '<div id="authenticate"></div>' +
    '<div id="current_input_div">' +
    '<input id="current_input" ' +
    'ondblclick="the_current_cell.toggle();" ' +
    'OnKeyDown="the_current_cell.keydown(event, true)" ' +
    'OnBlur="the_current_cell.focused=false;the_current_cell.change()" ' +
    '>' +
    '</div>' +
    '<img id="t_sort_down" src="' + url + '/sort_down.png" width="12">' +
    '<img id="t_sort_up" src="' + url + '/sort_up.png" width="12">' ;

  if ( ue != 'VIRTUALUE' )
    a += '<iframe id="server_answer" style="width:1px;height:1px;border:0px;position:absolute;top:0px;left:0px" src="' + url + '/sort_up.png"></iframe>' +
    '</body>' ;
  return a ;
}

function insert_middle()
{
  if ( preferences.interface == 'L' )
    {
      return ;
    }
  document.write(new_interface()) ;
}


