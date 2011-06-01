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
      return '</head><body id="body" onunload="send_key_history()" class="tomuss"  onkeydown="dispatch2(the_event(event))" onkeypress="dispatch(the_event(event))">' +
	'<style>' +
	'ul { margin-top: 0px ; margin-bottom: 0px; }\n' +
	'@media speech { u { pause-after: 1s; } }\n' +
	'@media aural { u { pause-after: 1s; } }\n' +
	'u { pause-after: 1s; }\n' +
	'</style>' +
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


  w += '<body id="body" class="tomuss" onunload="the_current_cell.change();store_unsaved()" onkeydown="the_current_cell.keydown(event, false)">' +
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
		 "<span class=\"comment\">Triangle s'il y a un commentaire.</span><br>" +
		 "<span class=\"today\">Le texte est gras si la cellule a été modifiée aujourd'hui.</span><br>" +
		 "<span class=\"is_an_abj\">Si ABINJ est souligné, cliquez dessus pour vérifier s'il a un justificatif.</span><br>" +
		 "<span class=\"non\">Le fond est rouge si l'étudiant n'est pas inscrit à l'UE.</span><br>" +
		 "<span class=\"tt\">Le fond est bleu si l'étudiant a un tiers temps.</span><br>" +
		 "<span class=\"filtered\">Le fond est jaune si la cellule est sélectionnée par le filtre de table</span>") + ',' ;
 w += hidden_txt('&nbsp;<img class="server"> ',
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

function column_attr_set(column, attr, value, td, force_save)
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

  if ( i_can_modify_column
       && ( ! column_attributes[attr].action || force_save ) )
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
  return i_am_the_teacher || !table_attr.masters[0] ;
}


function table_attr_set(attr, value, td)
{
  var old_value = table_attr[attr] ;

  if ( old_value == value )
    return  ;

  if ( ! table_attributes[attr].action && ! table_change_allowed()
       && ! i_am_root )
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

  if ( ! table_attributes[attr].action )
    append_image(td, 'table_attr_' + attr + '/' + encode_uri(value),
		 attr == 'modifiable') ;

  return value ;
}

function attr_update_user_interface(attr, column, force_update_header)
{
  if ( column.need_update )
    {
      update_columns() ;
      update_histogram(true) ;
    }
  if ( attr.display_table || column.need_update )
    table_fill(true, false, true) ;
  if ( attr.update_horizontal_scrollbar )
    update_horizontal_scrollbar() ;

  //  the_current_cell.update_headers() ;

  if ( (force_update_header || attr.update_headers)
       && column == the_current_cell.column )
    {
      the_current_cell.do_update_column_headers = true ;
      the_current_cell.update_headers() ;
    }
  if ( attr.what == 'table' )
    the_current_cell.update_table_headers();

  if ( attr.update_table_headers )
    table_header_fill() ;
}

function an_user_update(event, input, column, attr)
{
  var td = the_td(event) ;
  var new_value ;

  if ( input.selectedIndex !== undefined )
    new_value = input.options[input.selectedIndex].value ;
  else
    new_value = input.value.replace(/\t/g, ' ') ;

  if ( attr.what == 'column' )
    new_value = column_attr_set(column, attr.name, new_value, td) ;
  else
    new_value = table_attr_set(attr.name, new_value, td) ;

  if ( new_value === undefined )
    {
      if ( input.selectedIndex === undefined )
	input.value = input.theoldvalue ;
      else
	input.selectedIndex = input.theoldvalue ;
      return ;
    }

  if ( new_value === null )
    return ; // Not stored, but leave user input unchanged
  
  if ( input.selectedIndex === undefined )
    if ( attr.what == 'column' )
      input.value = attr.formatter(column, new_value) ;
    else
      input.value = attr.formatter(new_value) ;

  input.theoldvalue = new_value ;

  if ( attr == 'type' )
    init_column(column) ; // Need to update other attributes.

  attr_update_user_interface(attr, column) ;
  update_value_and_tip(input, new_value) ;
}

function header_change_on_update(event, input, what)
{
  var column = the_current_cell.column ;

  if ( what.match(/^column_attr_/) )
    an_user_update(event, input, column,
		   column_attributes[what.replace('column_attr_','')]) ;
  else if ( what.match(/^table_attr_/) )
    an_user_update(event, input, column,
		   table_attributes[what.replace('table_attr_','')]) ;
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
  var classe='', onkey='', before='', after='' ;
  // Don't call onblur twice (IE bug) : so no blur if not focused
  var onblur='if(element_focused===undefined)return;element_focused=undefined;';

  if ( options && (!options.search || options.search('"') != -1) )
    alert('BUG : header_input parameter: ' + the_id + ' ' + options) ;

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
    {
      before = '<div class="one_line">' + before ;
      after = '</div>' ;
    }

  return before+'<input style="margin-top:0px" type="text" id="' + the_id + '" class="' + classe
    + '" onfocus="if ( this.tomuss_editable === false ) this.blur() ; else { this.className=\'\';element_focused=this;}" '
    + ' onblur="' + onblur
    + '" onkeyup="' + onkey  +'">' + after ;
}

function an_input_attribute(attr, options, prefix_id, prefix_)
{
  var tip = attr.tip ;
  if ( i_am_root )
    tip += '<hr><b>' + prefix_id + attr.name + '</b>' ;
  var the_id = prefix_id + attr.name ;

  switch(attr.gui_display)
    {
    case 'GUI_input':
      return hidden_txt(header_input(the_id, prefix_ + attr.name,options),tip);
    case 'GUI_a':
      return hidden_txt('<a href="javascript:'
			+ attr.action + '(\'' + the_id + '\')"' +
			' id="' + the_id + '">' +
			attr.title + '</a>', tip) ;
    case 'GUI_none':
      return attr.title ;
    case 'GUI_button':
      return hidden_txt('<input type="button" class="gui_button" id="'
			+ the_id + '" '
			+ 'onclick="' + attr.action + '(this);'
			+ 'setTimeout(\'linefilter.focus()\',100)"'
			+ ' value="' + attr.title + '">',
			tip) ;
    case 'GUI_select':
      var opts = '' ;
      for(var i in options)
	opts += '<OPTION VALUE="' + options[i][0] + '">'
                                  + options[i][1] + '</OPTION>' ;
      
      return hidden_txt('<select style="margin:0px" onfocus="take_focus(this);" id="'
			+ the_id + '" onChange="this.blur();'
                        + "header_change_on_update(event,this,'" +
			prefix_ + attr.name + "');"
			+ attr.action + '(this)"'
                        + ' onblur="if(element_focused===undefined)return;element_focused=undefined;">'
                        + opts + '</select>',
			tip) ;
    default:
      alert('BUG gui_display') ;
    }
}

function column_input_attr(attr, options)
{
  return an_input_attribute(column_attributes[attr], options,
			    "t_column_", "column_attr_") ;
}

function table_input_attr(attr, options)
{
  return an_input_attribute(table_attributes[attr], options,
			    "t_table_attr_", "table_attr_") ;
}

/* tabbed view */

function create_tabs(name, tabs)
{
  var s = ['<div class="tabs" id="' + name + '"><div class="titles">'] ;
  for(var i in tabs)
     s.push('<span id="title_' + tabs[i][0] + '" onclick="select_tab(\'' + name + "','" +
            tabs[i][0] + '\')">' + tabs[i][0]
             + '</span>') ;
  s.push('</div><div class="contents">') ;
  for(var i in tabs)
     s.push('<div class="content" id="title_' + tabs[i][0] + '">'
             + tabs[i][1] + '</div>') ;
  s.push('</div></div>') ;

  return s.join('') ;
}

function select_tab(name, tab)
{
  var tabs = document.getElementById(name) ;
  for(var child = tabs.childNodes[1].firstChild;child;child=child.nextSibling)
     if ( child.id != 'title_' + tab )
         child.style.display = 'none' ;
     else
         child.style.display = '' ;

  for(var child = tabs.childNodes[0].firstChild;child;child=child.nextSibling)
        if ( child.id != 'title_' + tab )
            child.className = '' ;
        else
            child.className = 'tab_selected' ;

}

function new_new_interface()
{
  var o, t ;

  // CELLULE / Cellule

  t = ['<table class="cell"><tr><td>'] ;
  t.push(hidden_txt('<a href="" target="_blank">' +
		    '<img id="t_student_picture" class="phot"></a>',
		    'Cliquez sur la photo pour voir la fiche de suivi '
		    + 'de l\'étudiant')) ;
  t.push('</td><td class="cell_values">') ;
  t.push(one_line('<span id="t_value"></span>',
		  "Valeur de la cellule.")) ;
  t.push(one_line('<span id="t_student_firstname"></span>',
		  "Prénom de l'étudiant.")) ;
  t.push(one_line('<span id="t_student_surname"></span>',
		  "Nom de l'étudiant.")) ;
  t.push(hidden_txt(header_input('comment', '',
				 'empty onblur=comment_on_change(event)')
		    + '<br>',
		    "Tapez un commentaire pour cette cellule<br>" +
		    "afin de ne pas oublier les choses importantes.<br>" +
		    "<b>ATTENTION : les étudiants voient ce commentaire</b>",
		    'one_line'));
  t.push(hidden_txt(header_input('linefilter', '',
				 'empty onkey=line_filter_change(this)'),
		    "<span class=\"shortcut\">(Alt-8)</span>" +
		    "<b>Filtre les lignes</b><br>" +
		    "Seules les lignes contenant une valeur filtrée " +
		    "seront affichées.<br>" +
		    "Tapez le début de ce que vous cherchez.",
		    'one_line'
		    )) ;
  t.push(hidden_txt('<span id="t_student_id" style="display:none"></span>', "Numéro d'étudiant.")) ;
  t.push('</td></tr></table>') ;
  o = [['Cellule', t.join('\n')]] ;

  // CELLULE / Historique

  t = [] ;
  t.push(one_line('Saisie par : <span id="t_author"></span>',
		  "Personne qui a modifié la cellule pour la dernière fois :"
		  )) ;
  t.push(one_line('Le <span id="t_date"></span>',
		  "Date ou la cellule a été modifiée pour la dernière fois."
		  )) ;
  t.push(one_line('Historique :<br><span id="t_history"></span>',
		  "Valeurs précédentes prises par la cellule.<br>"+
		  "De la plus ancienne à la plus récente.<br>" +
		  "Le nom de la personne qui a fait la modification<br>" +
		  "est indiqué si la valeur précédente n'était<br>" +
		  "pas saisie par elle.")) ;
  o.push(['Historique', t.join('\n')]) ;
		 
  // CELLULE / ?

  t = [] ;
  t.push(hidden_txt('La <a href="_URL_/doc_table.html" target="_blank">' +
		    'documentation</a><br>',
		    "Cliquez sur le lien pour avoir tous les détails sur<br>" +
		    "l'utilisation de ce tableur")) ;
  t.push(hidden_txt('<span class="ro">S</span>' +
		    '<span class="comment">t</span>' +
		    '<span class="today">y</span>' +
		    '<span class="is_an_abj">l</span>' +
		    '<span class="non">e</span>' +
		    '<span class="tt">s</span> d\'affichage',
		    "<span class=\"ro\">Le texte est gris si la cellule " +
		    "est définie par quelqu'un d'autre.</span><br>" +
		    "<span class=\"comment\">Triangle s'il y a un " +
		    "commentaire.</span><br>" +
		    "<span class=\"today\">Le texte est gras si la cellule " +
		    "a été modifiée aujourd'hui.</span><br>" +
		    "<span class=\"is_an_abj\">Si ABINJ est souligné, " +
		    "cliquez dessus pour vérifier s'il a un justificatif." +
		    "</span><br>" +
		    "<span class=\"non\">Le fond est rouge si l'étudiant " +
		    "n'est pas inscrit à l'UE.</span><br>" +
		    "<span class=\"tt\">Le fond est bleu si l'étudiant " +
		    "a un tiers temps.</span><br>" +
		    "<span class=\"filtered\">Le fond est jaune si la " +
		    "cellule est sélectionnée par le filtre de table</span>"
		    ));
  t.push('<br>Feedback : ') ;
  t.push(hidden_txt('&nbsp;<img class="server"> ',
		    'Ce petit carré apparaît quand :<br>' +
		    'on essaye de stocker la valeur sur le serveur,<br>' +
		    'si cela dure plus de 5 secondes il y a un ' +
		    '<b>problème</b> (réseaux ?),<br>' +
		    'évitez de saisir des valeurs dans ces conditions.')) ;
  t.push(hidden_txt('&nbsp;<img class="server" src="_URL_/ok.png"> ',
		    'Ce petit carré apparaît quand :<br>' +
		    'la valeur a été <b>stockée avec succès</b> ' +
		    'sur le serveur')) ;
  t.push(hidden_txt('&nbsp;<img class="server" src="_URL_/bad.png"> ',
		    'Ce petit carré apparaît quand :<br>' +
		    'le serveur <b>refuse de stocker cette valeur</b>.<br>' +
		    'C\'est certainement du à un problème de droit')) ;
  t.push(hidden_txt('&nbsp;<img class="server" src="_URL_/bug.png">',
		    'Ce petit carré apparaît quand :<br>' +
		    'Il y a un <b>bug</b> quelque part,<br>'+
		    'le responsable du logiciel a reçu un message ' +
		    'le prévenant.')) ;
  t.push('<br>') ;

  o.push(['?', t.join('\n')]) ;

  // CELLULE

  var w = [] ;

  w.push('<table id="menutop" class="tabbed_headers"><tr><td class="tabbed_headers">') ;
  w.push( create_tabs('cellule', o) ) ;

  // COLUMN / Column

  t = [] ;
  t.push(column_input_attr('title', 'one_line')) ;

  var options = [] ;
  for(var type_i in types)
    {
      if ( types[type_i].full_title )
	options.push([types[type_i].title, types[type_i].full_title]) ;
      else
	options.push([types[type_i].title, types[type_i].title]) ;
    }
  t.push('<div class="one_line">') ;
  t.push(column_input_attr('type', options)) ;
  t.push(column_input_attr('enumeration')) ;
  t.push(column_input_attr('minmax')) ;
  t.push('</div>') ;
  t.push(column_input_attr('stats', 'one_line')) ;
  t.push(column_input_attr('comment', 'empty one_line')) ;
  t.push(hidden_txt(header_input("columns_filter",'',
				 'empty one_line onkey=columns_filter_change(this)'),
		    "Seules les <b>colonnes</b> dont le nom est filtré " +
		    "seront affichées.<br>" +
		    "Tapez le début de ce que vous cherchez.<br>" +
		    "Pour plus d'information, regardez l'aide sur les filtres."
		    )) ;
  o = [['Colonne', t.join('\n')]] ;

  // COLUMN / Formula

  t = [] ;
  t.push('Coloriage :') ;
  t.push(column_input_attr('red')) ;
  t.push(column_input_attr('green')) ;
  t.push('<br>') ;
  t.push(column_input_attr('columns')) ;
  t.push('<br>') ;
  t.push(column_input_attr('test_filter')) ;
  t.push('<br>') ;
  t.push(column_input_attr('weight', 'before=Poids=')) ;
  t.push(column_input_attr('empty_is', 'before=Cellule vide =')) ;

  o.push(['Formule', t.join('\n')]) ;

  // COLUMN / Display

  var x ="<br>Ce changement n'est pas visible par les autres utilisateurs.";

  t = [] ;
  t.push(column_input_attr('visibility_date')) ;
  t.push('Déplace colonne : ') ;
  t.push(hidden_txt('<a href="javascript:do_move_column_left();">«</a>',
		    "<b>Décale la colonne vers la gauche</b>" + x)) ;
  t.push(column_input_attr('position')) ;
  t.push(hidden_txt('<a href="javascript:do_move_column_right();">»</a>',
		    "<b>Décale la colonne vers la droite</b>" + x)) ;
  t.push('<br>') ;
  t.push('Largeur colonne : ') ;
  t.push(hidden_txt('<a href="javascript:smaller_column();">-</a>',
		    "<b>Amincir la colonne</b>" + x)) ;
  t.push(column_input_attr('width')) ;
  t.push(hidden_txt('<a href="javascript:bigger_column();">+</a>',
		    "<b>Élargir la colonne</b>" + x)) ;
  t.push('<br>') ;
  t.push(column_input_attr('freezed')) ;
  t.push('<br>') ;
  t.push(column_input_attr('hidden')) ;

  o.push(['Affiche', t.join('\n')]) ;

  // COLUMN / Action

  t = [] ;
  t.push(column_input_attr('import') + '<br>') ;
  t.push(column_input_attr('fill') + '<br>') ;
  t.push(column_input_attr('export') + '<br>') ;
  t.push(column_input_attr('delete') + '<br>') ;
  t.push(one_line('<span id="t_column_author"></span>',
		  "Personne qui a modifié la définition<br>" +
		  "de la colonne pour la dernière fois :")) ;

  o.push(['Action', t.join('\n')]) ;

  // COLUMN / Help

  o.push(['?', 'bla bla bla']) ;

  // COLUMN

  w.push('</td><td class="tabbed_headers">') ;
  w.push( create_tabs('column', o) ) ;


  // Table / Table

  t = [] ;
 
  t.push(hidden_txt('<span id="nr_filtered_lines"></span> lignes filtrées',
		    "C'est le nombre de lignes qui sont affichées<br>\n" +
		    "après avoir appliqués les filtres")) ;

  t.push(hidden_txt('sur <span id="nr_not_empty_lines"></span>',
		    "C'est le nombre de lignes dans le tableau total<br>\n" +
		    "y compris les lignes vidées")) ;
  t.push('<br>') ;
  t.push(hidden_txt(table_input_attr('nr_lines') +  'lignes, ' +
		    table_input_attr('nr_columns') + ' colonnes',
		    "Taille du tableau affiché sur l'écran")) ;
  t.push('<br>') ;
  t.push(table_input_attr('facebook')) ;
  t.push(table_input_attr('print')) ;
  t.push(table_input_attr('abj')) ;
  t.push(table_input_attr('mail')) ;
  t.push('<br>') ;

  t.push(table_input_attr("comment",'empty')) ;
  t.push('<br>') ;
  t.push(hidden_txt(header_input('fullfilter', '',
				 'empty onkey=full_filter_change(this)'),
		    "Seule les <b>colonnes et lignes</b> contenant " +
		    "une valeur filtrée<br>seront affichées " +
		    "(c'est un filtre).<br>" +
		    "Tapez le début de ce que vous cherchez.<br>"
		    )) ;

  o = [['Table', t.join('\n')]] ;

  // Table / Paramétrage

  t = [] ;
  
  t.push("Nb colonnes affichées " +
	 table_input_attr('default_nr_columns')) ;
  t.push('<br>') ;

  t.push("Droits d'accès :" +
	 table_input_attr('private', [[0,'Publique'],[1,'Privée']]));
  t.push(" " +
	 table_input_attr('modifiable',
			  [[0,'Non Modifiable'],[1,'Modifiable']])) ;
  t.push('<br>') ;

  if ( semester == 'Printemps' || semester == 'Automne' )
    t.push('Affiche étudiant :' +
	   table_input_attr('official_ue', [[0,'Invisible'],[1,'Visible']])) ;
  else
    t.push('&nbsp;') ;

  t.push('<br>') ;
  t.push('Début/fin : ' + table_input_attr('dates','empty')) ;
  t.push('<br>') ;
  t.push(table_input_attr('masters','empty')) ;

  o.push(['Paramétrage', t.join('\n')]) ;

  // Table / Action

  t = [] ;

  t.push(table_input_attr('autosave')) ;
  t.push('<br>') ;
  t.push(table_input_attr('statistics')) ;
  t.push('<br>') ;
  t.push(table_input_attr('t_import') + ' / ' + table_input_attr('t_export')) ;
  t.push('<br>') ;
  t.push(table_input_attr('bookmark')) ;
  t.push('<br>') ;
  t.push(table_input_attr('linear')) ;
  t.push(table_input_attr('update_content')) ;
  t.push(hidden_txt('<a href="javascript:change_popup_on_red_line()">.</a>',
		    "Basculer entre le mode tenant compte ou non<br>" +
		    "des inscriptions pédagogiques."
		    ,'','popup_on_red_line')) ;

  o.push(['Action', t.join('\n')]) ;

  // Table / Help

  o.push(['Aide', 'bla bla bla']) ;

  w.push('</td><td class="tabbed_headers">') ;
  w.push( create_tabs('table', o) ) ;

  w.push('</td></tr></table>') ;
  w.push('<script>select_tab("cellule", "Cellule")</script>') ;
  w.push('<script>select_tab("column", "Colonne")</script>') ;
  w.push('<script>select_tab("table", "Table")</script>') ;

  return w.join('\n') ;
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
   '</td><td class="cell_values">' +
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
      options.push([types[type_i].title, types[type_i].full_title]) ;
    else
      options.push([types[type_i].title, types[type_i].title]) ;
  }
 
 w += column_input_attr('type', options) +
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
   column_input_attr('position') +
   hidden_txt('<a href="javascript:do_move_column_right();">»</a>',
	      "<b>Décale la colonne vers la droite</b><br>" +
	      "Ce changement n'est pas visible par les autres utilisateurs."
	      ) +
   '</td><td>' +

   hidden_txt('<a href="javascript:smaller_column();">-</a>',
	      "<b>Amincir la colonne</b><br>" +
	      "Ce changement n'est pas visible par les autres utilisateurs."
	      ) + '&nbsp;' +
   column_input_attr('width') +
   hidden_txt('<a href="javascript:bigger_column();">+</a>',
	      "<b>Élargir la colonne</b><br>" +
	      "Ce changement n'est pas visible par les autres utilisateurs."
	      ) + '</td><td>' +
   column_input_attr('import') + '</td><td>' +
   column_input_attr('fill') + '</td><td>' +
   column_input_attr('export') + '</td><td>' +
   column_input_attr('delete') + '</td><td>' +
   column_input_attr('freezed') + '</td><td>' +
   column_input_attr('hidden') +
   '</td></tr></table></div>' +

   column_input_attr('stats') +
 
   '<td class="space"><td class="blocktop">' +
   hidden_txt('<span id="nr_filtered_lines"></span>/<span id="nr_not_empty_lines"></span> lignes',
	      "Nombre de lignes filtrées et<br>" +
	      "nombre de lignes dans le tableau total") + ', ' +

   table_input_attr('nr_lines') +  '&times;' +
   table_input_attr('nr_columns') + '<br>' +
   table_input_attr('facebook') +
   table_input_attr('print') +
   table_input_attr('abj') +
   table_input_attr('mail') +
   table_input_attr('statistics') + '<br>' +

   '<div class="menu">' +
   hidden_txt('<a href="javascript:change_popup_on_red_line()">&nbsp;</a>',
	      "Cliquez-ici pour basculer entre le mode tenant compte<br>" +
	      "des inscriptions pédagogiques et celui n'en tenant pas compte."
	      ,'','popup_on_red_line') +

   table_input_attr('bookmark') + ', ' +
   table_input_attr('autosave') + ', ' +
   table_input_attr('linear') + ', ' +
   table_input_attr('t_import') + ', ' +
   table_input_attr('t_export') + ', ' +
   table_input_attr('update_content') + '<br>' +
   table_input_attr('private',    [[0,'Publique'],[1,'Privée']]) +
   table_input_attr('modifiable', [[0,'Non Modifiable'],[1,'Modifiable']]) ;

 if ( semester == 'Printemps' || semester == 'Automne' )
   w += table_input_attr('official_ue', [[0,'Invisible'],[1,'Visible']]) ;

 w += table_input_attr('default_nr_columns') + '<br></div>' +
   table_input_attr('dates','empty') +
   '</tr><tr><td class="blockbottom">' +
   one_line('<span id="t_author"></span>',
	    "Personne qui a modifié la cellule pour la dernière fois :") +
   hidden_txt(header_input('comment','',
			   'empty onblur=comment_on_change(event)')
	      + '<br>',
	      "Tapez un commentaire pour cette cellule<br>" +
	      "afin de ne pas oublier les choses importantes.<br>" +
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
   table_input_attr('masters','empty') +
   table_input_attr("comment",'empty') + '<br>' +
   hidden_txt(header_input('fullfilter', '',
			   'empty onkey=full_filter_change(this)'),
	      "Seule les <b>colonnes et lignes</b> contenant une valeur filtrée<br>seront affichées (c'est un filtre).<br>" +
	      "Tapez le début de ce que vous cherchez.<br>"
	     ) +
   '</tr></table>' ;

 return w ;
}

var popup_old_values = {} ;

function popup_close()
{
  element_focused = undefined ;
  var e = document.getElementById('popup_id') ;
  if ( e )
    {
      popup_old_values[e.className] = e.getElementsByTagName('TEXTAREA'
							     )[0].value ;
      e.parentNode.removeChild(e);
    }
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

function create_popup(html_class, title, before, after, default_answer)
{
  popup_close() ;

  var popup = document.getElementById('popup') ;
  var new_value ;

  if ( default_answer )
    {
      var new_value = popup_old_values['import_export ' + html_class] ;
      if ( new_value === undefined )
	new_value = default_answer ;
      new_value = html(new_value) ;
    }
  else
    new_value = '' ;

  popup.innerHTML += '<div id="popup_id" class="import_export ' +
    html_class + '"><h2>' + title
    + '</h2>' + before +
    '<TEXTAREA ROWS="10" class="popup_input" onfocus="element_focused=this;">'+
    new_value + '</TEXTAREA>' +
    '<BUTTON class="close" OnClick="popup_close()">&times;</BUTTON>' +
    after ;

  popup.column = the_current_cell.column ;

  popup.getElementsByTagName('TEXTAREA')[0].focus() ;
}



function tail_html()
{
  if ( preferences.interface == 'L' )
    return '<span id="server_feedback"></span><div id="authenticate"></div>';

  var a = '<p class="copyright"><span id="server_feedback"></span></p>' +
    '<div id="log"></div>' +
    '<div id="message">&nbsp;</div>' +
    "<div id=\"saving\">Les données sont en train d'être envoyées au serveur.<br>Veuillez patienter (ou vérifiez votre connexion réseau)</div>" +
    '<div id="authenticate"></div>' +
    '<div id="current_input_div">' +
    '<input id="current_input" ' +
    'ondblclick="the_current_cell.toggle();" ' +
    'OnKeyDown="the_current_cell.keydown(event, true)" ' +
    'OnBlur="the_current_cell.focused=false;the_current_cell.change()" ' +
    '>' +
    '</div>' ;
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
  i_am_root = myindex(root, my_identity) != -1 ;

  if ( window.location.pathname.search('=new-interface=') != -1 )
      document.write(new_new_interface()) ;
  else
      document.write(new_interface()) ;
/* onmouseout is here because it must contains the tip
    If you change the content, read 'table_init' in 'lib.js'
*/
  
  var w = '<div class="horizontal_scrollbar"><img src="' + url
    + '/prev.gif" onclick="javascript:previous_page_horizontal();">'
    + '<div id="horizontal_scrollbar"></div><img src="' + url
    + '/next.gif" onclick="javascript:next_page_horizontal();"></div>' +
    '<div>' ;
  
  if ( ! scrollbar_right )
    w += '<div id="vertical_scrollbar"></div>' ;
  w += '<div id="divtable" class="colored"><div id="hover"></div>'
    + '<div id="tip"></div></div>' ;
  if ( scrollbar_right )
    w += '<div id="vertical_scrollbar"></div>' ;
  w += '</div><div id="popup"></div>'
    + '</div><div id="loading_bar"><div></div></div>' ;
  document.write(w) ;
}


