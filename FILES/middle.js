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
function modification_allowed_on_this_line(line_id, data_col)
{
  if ( myindex(semesters, semester) == -1 )
    return true ;
  if ( tr_classname === undefined )
    return true ;
  if ( ! popup_on_red_line )
    return true ;
  if ( lines[line_id][tr_classname].value == 'non' )
    return true ; // Returns false here to forbid red line editing
  return true ;
}

function update_student_information_default(line)
{
  if ( columns[0].type != 'Login' && columns[0].title != 'ID' )
    return ;
  var src = student_picture_url(line[0].value) ;
  if ( src != t_student_picture.src )
    {
      t_student_picture.src = '/tip.png' ;
      if ( line[0].value )
	t_student_picture.src = student_picture_url(line[0].value) ;
    }
  t_student_picture.parentNode.href = suivi + '/' + line[0].value ;
}

/*REDEFINE
*/
function update_student_information(line)
{
  update_student_information_default(line) ;
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

  if ( myindex(semesters, semester) != -1 )
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

  if ( myindex(semesters, semester) != -1 )
      w += '<a href="' + suivi.split('/=')[0] + '/rss2/' + ue + '"><img style="border:0px" src="' + url + '/feed.png"></a>' ;

  if ( false )
    {
      w += hidden_txt('<b><a href="' + url + '/=' + ticket + '/' + year + '/'
		      + semester + '/' + ue + '/=new-interface=">'
		      + '&beta;</a></b> ',
		      'Essayez la futur interface de TOMUSS !') ;
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
		      "<span class=\"filtered\">Le fond est jaune si la cellule est sélectionnée par un filtre</span>") + ',' ;
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
    }
 w += hidden_txt('<a href="' + url + '/=' + ticket + '/0/Preferences/'
		 + my_identity2 + '" target="_blank">Préférences</a>',
		 "Ce lien vous permet de régler les préférences.<br>" +
		 "Les préférences sont appliquées à <b>tous</b> les tableaux");
 
 w += '</div><h1>'  ;

 var semester_color = semesters_color[myindex(semesters, semester)] ;

 var options ;
 if ( semester_color )
   {
     options = "__OPTIONS__" ;
     options = options.replace('>' + year + '/' + semester,
			       ' selected>' + year + '/' + semester) ;
     options = '<select onchange="semester_change(this);" '
       + 'style="background:' + semester_color + '">'
       + options + '</select>' ;
   }
 else
   {
     options = '<span>' + year + ' ' + semester + '</span>' ;
   }

 w += options + ' ' + ue + ' ' + table_attr.table_title ;
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
       && ( columns_filter_value || full_filter) )
    {
      alert_append("On a pas le droit de créer des colonnes quand "
		   + "il y a un filtre de colonne ou table. "
		   + "Désolé, vous devez enlever les filtres."
		   ) ;
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
    {
      new_value = input.options[input.selectedIndex].value ;
      input.selectedText = input.options[input.selectedIndex].text ;
    }
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
  else
    attr.formatter(column, new_value) ;
  input.theoldvalue = new_value ;

  if ( attr == 'type' )
    init_column(column) ; // Need to update other attributes.

  attr_update_user_interface(attr, column) ;
  compute_tip(input);
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

function header_input_focus(e)
{
  if ( e.tomuss_editable === false )
    {
      e.blur() ;
      return ;
    }
  e.className = '' ; // Remove 'empty' class
  element_focused = e ;

  // To resize the INPUT tag if it is larger than the tab.
  // For example: the Table Dates
  var x = e.offsetLeft ;
  var width = e.parentNode.parentNode.parentNode.offsetWidth ;
  var margin = 5 ;
  if ( x + e.offsetWidth > width + 1 )
    {
      e.style.width = '' + (width - x - margin) + 'px' ;
    }
}

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
  if ( options && options.search('beforeclass=') != -1 )
    before = '<span class="' + options.split('beforeclass=')[1].split(' ')[0]
      + '">' + before + '</span>' ;
  if ( options && options.search('after=') != -1 )
    after = options.split('after=')[1].split(' ')[0] ;
  if ( options && options.search('one_line') != -1 )
    {
      before = '<div class="one_line">' + before ;
      after += '</div>' ;
    }

  return before+'<input style="margin-top:0px" type="text" id="' + the_id + '" class="' + classe
    + '" onfocus="header_input_focus(this)" onblur="' + onblur
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
      return hidden_txt('<span class="gui_button" id="'
			+ the_id + '" '
			+ 'onclick="' + attr.action + '(this);'
			+ 'setTimeout(\'linefilter.focus()\',100)"'
			+ '>' + attr.title + '</span>',
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

function create_tabs(name, tabs, more)
{
  if ( more === undefined )
    more = '' ;

  var s = ['<div class="tabs" id="' + name + '"><div class="titles">'] ;
  for(var i in tabs)
     s.push('<span id="title_' + tabs[i][0] + '" onclick="select_tab(\'' + name + "','" +
            tabs[i][0] + '\');the_current_cell.input.focus()">' + tabs[i][0]
             + '</span>') ;
  s.push(more + '</div><div class="contents">') ;
  for(var i in tabs)
     s.push('<div class="content" id="title_' + tabs[i][0] + '">'
             + tabs[i][1] + '</div>') ;
  s.push('</div></div>') ;

  return s.join('') ;
}

function select_tab(name, tab)
{
  var tabs = document.getElementById(name) ;
  if ( ! tabs )
    return ;
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

  column_attributes['hidden'].title = 'Cacher la colonne' ;
  column_attributes['import'].title = '<b>Importer</b> des valeurs dans la colonne' ;
  column_attributes['fill'].title = '<b>Remplir</b> la colonne avec des valeurs' ;
  column_attributes['export'].title = '<b>Exporter</b> la colonne pour APOGÉE' ;
  column_attributes['delete'].title = '<b>Détruire</b> définitivement la colonne' ;
  column_attributes['position'].title = "position" ;
  column_attributes['width'].title = "largeur" ;

  table_attributes['autosave'].title = 'Enregistrement automatique' ;
  table_attributes['t_import'].title = '<b>Importer</b>' ;
  table_attributes['t_export'].title = '<b>Exporter</b>' ;
  table_attributes['bookmark'].title = "Créer un signet avec les <b>options d'affichage</b>" ;
  table_attributes['linear'].title = "Linéaire" ;
  table_attributes['update_content'].title = "Forcer la mise à jour" ;

  var doc_link = '<div class="one_line">' +
    hidden_txt('<a href="_URL_/doc_table.html" target="_blank">' +
	       'Documentation complète et intéractive</a>',
	       "Cliquez sur le lien pour avoir tous les détails sur<br>" +
	       "l'utilisation de ce tableur") + '</div>' ;


  // CELLULE / Cellule

  t = ['<table class="cell"><tr><td>'] ;
  t.push(hidden_txt('<a href="" target="_blank">' +
		    '<img id="t_student_picture" class="phot"></a>',
		    'Cliquez sur la photo pour voir la fiche de suivi '
		    + 'de l\'étudiant')) ;
  t.push('</td><td class="cell_values">') ;
  t.push(one_line('<span id="t_student_surname"></span>',
		  "Nom de l'étudiant.")) ;
  t.push(one_line('<span id="t_student_firstname"></span>',
		  "Prénom de l'étudiant.")) ;
  t.push(one_line('<span id="t_value"></span>',
		  "Valeur de la cellule.")) ;
  t.push(hidden_txt(header_input('comment', '',
				 'empty one_line onblur=comment_on_change(event)'),
		    "<span class=\"shortcut\">(Alt-/)</span>" +
		    "Tapez un commentaire pour cette cellule<br>" +
		    "afin de ne pas oublier les choses importantes.<br>" +
		    "<b>ATTENTION : les étudiants voient ce commentaire</b>"));
  t.push(hidden_txt(header_input('linefilter', '',
				 'empty one_line onkey=line_filter_change(this)'),
		    "<span class=\"shortcut\">(Alt-8)</span>" +
		    "<b>Filtre les lignes</b><br>" +
		    "Seules les lignes contenant une valeur filtrée " +
		    "seront affichées.<br>" +
		    "Tapez le début de ce que vous cherchez.")) ;
  t.push(hidden_txt('<span id="t_student_id" style="display:none"></span>', "Numéro d'étudiant.")) ;
  t.push('</td></tr></table>') ;
  o = [['Cellule', t.join('\n')]] ;

  // CELLULE / Historique

  t = [] ;
  t.push(hidden_txt('<div id="t_history"></div>',
		    "Valeurs précédentes prises par la cellule.<br>"+
		    "De la plus récente à la plus ancienne."
		    )) ;
  o.push(['Historique', t.join('\n')]) ;
		 
  // CELLULE / ?

  t = [] ;
  t.push(doc_link) ;
  t.push('<div class="one_line">') ;
  t.push(hidden_txt('<span class="ro">S</span>' +
		    '<span class="comment">t</span>' +
		    '<span class="today">y</span>' +
		    '<span class="is_an_abj">l</span>' +
		    '<span class="non">e</span>' +
		    '<span class="tt">s</span> d\'affichage utilisés dans la table',
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
		    "cellule est sélectionnée par un filtre</span>"
		    ));
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
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
  t.push(hidden_txt(' carré vert = sauvegarde réussie !',
		    "Mettez le curseur sur les petits carrés pour savoir<br>"
		    + "ce qu'ils représentent")) ;
  t.push('</div>') ;
  
  t.push('<div class="one_line">') ;
  t.push(hidden_txt
	 ('ALT-8 : édite le filtre de lignes',
	  "Le filtre de ligne permet de n'afficher que les lignes<br>"
	  +"qui contiennent le début de ce que vous avez tapé.<br>"
	  +"Par exemple le NOM, PRÉNOM ou numéro d'étudiant"
	  )) ;
  t.push('</div>')
  t.push('<div class="one_line">') ;
  t.push(hidden_txt('ALT-1 : cache les bulles d\'aide',
		    "Au cas où les bulles d'aide soient gênantes<br>"
		    +"Vous pouvez aussi l'indiquer dans vos préférences")) ;
  t.push('</div>') ;
  o.push(['?', t.join('\n')]) ;

  // CELLULE

  var w = [] ;

  w.push('<table id="menutop" class="tabbed_headers"><tr><td class="tabbed_headers">') ;
  w.push(create_tabs('cellule', o,
		     '<a id="autosavelog" href="#" onclick="table_autosave_toggle()">Enregistrer les modifications</a>' +
		     '<a id="tablemodifiableFB" href="#" onclick="select_tab(\'table\', \'Paramétrage\')">Tableau non modifiable</a>' +
		     '<span style="border:0px" id="server_feedback"></span>' +
		     '<var style="border:0px;white-space:nowrap" id="log"></var>')) ;

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
  t.push(column_input_attr('test_filter')) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(column_input_attr('stats')) ;
  t.push('</div>') ;
  t.push(column_input_attr('comment', 'empty one_line')) ;
  t.push(hidden_txt(header_input("columns_filter",'',
				 'empty one_line onkey=columns_filter_change(this)'),
		    "Seules les <b>colonnes</b> dont le nom est filtré " +
		    "seront affichées.<br>" +
		    "Tapez le début de ce que vous cherchez.<br>" +
		    "Pour plus d'information, regardez l'aide sur les filtres.")) ;
  o = [['Colonne', t.join('\n')]] ;

  // COLUMN / Formula

  t = [] ;
  t.push('<div class="one_line">') ;
  t.push(column_input_attr('red',
			   'before=Rougir beforeclass=widthleft')) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(column_input_attr('green',
			   'before=Verdir beforeclass=widthleft')) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(column_input_attr('empty_is',
			   'before=Si&nbsp;vide beforeclass=widthleft')) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(column_input_attr('columns',
			   'before=Formule beforeclass=widthleft')) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(column_input_attr('weight', 'before=Poids beforeclass=widthleft')) ;
  t.push(column_input_attr('repetition','before=&nbsp;&nbsp;Répétition&nbsp;'));
  t.push('</div>') ;

  o.push(['Formule', t.join('\n')]) ;

  // COLUMN / Display

  var x ="<br>Ce changement n'est pas visible par les autres utilisateurs.";

  t = [] ;
  t.push('<div class="one_line">') ;
  t.push(column_input_attr('visibility_date',
			   'before=Visible&nbsp;le&nbsp;:&nbsp; beforeclass=widthleft'
			   )) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(column_input_attr('course_dates',
			   'before=Dates cours&nbsp;:&nbsp; beforeclass=widthleft'
			   )) ;
  t.push('</div>') ;
  t.push('<div class="one_line" style="text-align:center">') ;
  t.push(hidden_txt('<img src="' + url + '/prev.gif" style="height:1em" onclick="do_move_column_left();">',
		    "<b>Décale la colonne vers la gauche</b>" + x)) ;
  t.push(column_input_attr('position')) ;
  t.push(hidden_txt('<img src="' + url + '/next.gif" style="height:1em" onclick="do_move_column_right();">',
		    "<b>Décale la colonne vers la droite</b>" + x)) ;
  t.push('&nbsp;') ;
  /*
  t.push('</div>') ;
  t.push('<div class="one_line" style="text-align:center">') ;
  */
  t.push(hidden_txt('<a href="javascript:smaller_column();"><img src="' + url + '/next.gif" style="height:1em;border:0"><img src="' + url + '/prev.gif" style="height:1em;border:0"></a>',
		    "<b>Amincir la colonne</b>" + x)) ;
  t.push(column_input_attr('width')) ;
  t.push(hidden_txt('<a href="javascript:bigger_column();"><img src="' + url + '/prev.gif" style="height:1em;border:0"><img src="' + url + '/next.gif" style="height:1em;border:0"></a>',
		    "<b>Élargir la colonne</b>" + x)) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;

  t.push(column_input_attr('modifiable',
			  [[0,'Personne ne peut modifier à partir du suivi'],
			   [1,'Les enseignants peuvent modifier à partir du suivi'],
			   [2,'Les étudiants peuvent modifier leur valeur à partir du suivi'],
			   ])) ;

  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(column_input_attr('freezed')) ;
  t.push('.') ;
  t.push(column_input_attr('hidden')) ;
  t.push('</div>') ;

  o.push(['Affiche', t.join('\n')]) ;

  // COLUMN / Action

  t = [] ;
  t.push('<div class="one_line">') ;
  t.push(column_input_attr('export')) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(column_input_attr('import')) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(column_input_attr('fill')) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(column_input_attr('delete')) ;
  t.push('</div>') ;
  t.push(one_line('Définie par '
		  + '<span id="t_column_author"></span>',
		  "Personne qui a modifié la définition<br>" +
		  "de la colonne pour la dernière fois :")) ;

  o.push(['Action', t.join('\n')]) ;

  // COLUMN / Help

  t = [] ;
  t.push(doc_link) ;
  t.push('<div class="one_line">') ;
  t.push(hidden_txt('Ce que vous faites est sauvegardé automatiquement',
		    "Quand vous saisissez une note dans une cellule<br>"
		    + 'un <img class="server" src="_URL_/ok.png"> '
		    +"apparaît pour indiquer que la sauvegarde est OK.<br>"
		    +'S\'il n\'y a pas eu de <img class="server" '
		    + 'src="_URL_/ok.png"> la sauvegarde n\'est pas garantie.'
		    )) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(hidden_txt("Rien n'est caché aux étudiants par défaut",
		    "Vous pouvez rendre la table complète invisible<br>"
		    +"en l'indiquant dans l'onglet « Paramétrage ».<br>"
		    +"Vous pouvez aussi indiquer une date de visiblité<br>"
		    +"dans l'onglet « Affiche » de la colonne."
		    )) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(hidden_txt('<a target="_blank" href="_URL_/doc_table.html#Calcul de moyenne">Comment calculer une moyenne</a> ?',
		    "Il est recommandé de lire le sommaire de la documentation.")) ;
  t.push('</div>') ;

  o.push(['?', t.join('\n')]) ;

  // COLUMN

  w.push('</td><td class="tabbed_headers">') ;
  w.push( create_tabs('column', o) ) ;


  // Table / Table

  t = [] ;
 
  t.push('<div class="one_line">') ;
  t.push(hidden_txt('<span id="nr_filtered_lines"></span> lignes filtrées sur ',
		    "C'est le nombre de lignes dans le tableau<br>\n" +
		    "après avoir appliqué les filtres")) ;

  t.push(hidden_txt('<span id="nr_not_empty_lines"></span>',
		    "C'est le nombre de lignes dans le tableau total<br>\n" +
		    "<b>sans compter les lignes vidées</b>")) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(table_input_attr('nr_lines').replace('</select>',
					      '</select> lignes') + ', ') ;
  t.push(table_input_attr('nr_columns').replace('</select>',
					      '</select> colonnes')) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(table_input_attr('facebook')) ;
  t.push(table_input_attr('print')) ;
  t.push(table_input_attr('abj')) ;
  t.push(table_input_attr('mail')) ;
  t.push(table_input_attr('statistics')) ;
  t.push('</div>') ;

  t.push(table_input_attr("comment", 'empty one_line')) ;

  t.push(hidden_txt(header_input('fullfilter', '',
				 'empty one_line onkey=full_filter_change(this)'),
		    "Seule les <b>colonnes et lignes</b> contenant " +
		    "une valeur filtrée<br>seront affichées " +
		    "(c'est un filtre).<br>" +
		    "Tapez le début de ce que vous cherchez.<br>"
		    )) ;

  o = [['Table', t.join('\n')]] ;

  // Table / Paramétrage

  t = [] ;
  
  t.push('<div class="one_line">') ;
  t.push(table_input_attr('default_nr_columns',
			  'before=Nb&nbsp;colonnes&nbsp;affichées&nbsp;:&nbsp;')) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push("Droits d'accès : " +
	 table_input_attr('private', [[0,'Publique'],[1,'Privée']]));
  t.push(" " +
	 table_input_attr('modifiable',
			  [[0,'Non Modifiable'],[1,'Modifiable']])) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;

  if ( myindex(semesters, semester) != -1 )
    t.push('Affichage étudiant : ' +
	   table_input_attr('official_ue', [[0,'Invisible'],[1,'Visible']])) ;
  else
    t.push('&nbsp;') ;

  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(table_input_attr('dates',
			  'empty before=Début/fin&nbsp;:&nbsp;')) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(table_input_attr('masters','empty before=Responsables&nbsp;:&nbsp;')) ;
  t.push('</div>') ;

  o.push(['Paramétrage', t.join('\n')]) ;

  // Table / Action

  t = [] ;

  t.push('<div class="one_line">') ;
  t.push(table_input_attr('t_export')) ;
  t.push('/') ;
  t.push(table_input_attr('t_import')) ;
  t.push(' les définitions de colonnes') ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(table_input_attr('t_copy')) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(table_input_attr('autosave')) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(table_input_attr('bookmark')) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(table_input_attr('linear')) ;
  t.push('.') ;
  t.push(table_input_attr('update_content')) ;
  t.push(hidden_txt('<a href="javascript:change_popup_on_red_line()">.</a>',
		    "Basculer entre le mode tenant compte ou non<br>" +
		    "des inscriptions pédagogiques."
		    ,'','popup_on_red_line')) ;
  t.push('</div>') ;

  o.push(['Action', t.join('\n')]) ;

  // Table / Help

  o.push(['?',
	  '<div class="scroll_auto">'
	  + doc_link
	  + 'Tout le monde peut remplir des cases vides. '
	  + 'Mais seul les responsables de la table peuvent modifier '
	  + 'les notes et commentaires saisis par les autres enseignants. '
	  + "Si personne n'est responsable de la table, n'importe qui "
	  + " à le droit d'en prendre la responsabilité."
	  ]) ;

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
	    "De la plus ancienne à la plus récente.") +
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
   table_input_attr('nr_columns') +
   '<div class="one_line">' +
   table_input_attr('facebook') +
   table_input_attr('print') +
   table_input_attr('abj') +
   table_input_attr('mail') +
   table_input_attr('statistics') +
   '</div>' +

   '<div class="one_line">' +
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
   table_input_attr('update_content') +
   '</div>' +
   table_input_attr('private',    [[0,'Publique'],[1,'Privée']]) +
   table_input_attr('modifiable', [[0,'Non Modifiable'],[1,'Modifiable']]) ;

 if ( myindex(semesters, semester) != -1 )
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
      if ( e.getElementsByTagName('TEXTAREA')[0] )
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

function popup_text_area()
{
  return document.getElementById('popup_id').getElementsByTagName('TEXTAREA')[0] ;
}

function popup_value()
{
  return parse_lines(popup_text_area().value) ;
}

function popup_set_value(value)
{
  var text_area = popup_text_area() ;
  text_area.value = value ;
  text_area.focus() ;
  text_area.select() ;
}

function popup_get_element()
{
  var popup = document.getElementById('popup') ;
  if ( ! popup )
    {
      popup = document.createElement('div') ;
      popup.id = 'popup' ;
      document.getElementsByTagName('BODY')[0].appendChild(popup) ;
    }
  return popup ;
}

function popup_is_open()
{
  return !! document.getElementById('popup_id') ;
}

function popup_column()
{
  return popup_get_element().column ;
}

function create_popup(html_class, title, before, after, default_answer)
{
  popup_close() ;

  var new_value ;

  if ( default_answer )
    {
      new_value = popup_old_values['import_export ' + html_class] ;
      if ( new_value === undefined )
	new_value = default_answer ;
      new_value = html(new_value) ;
    }
  else
    new_value = '' ;

  var s = '<div id="popup_id" class="import_export ' + html_class
           + '"><h2>' + title + '</h2>' + before ;
  if ( default_answer !== false )
    s += '<TEXTAREA WRAP="off" ROWS="10" class="popup_input" onfocus="element_focused=this;">'+ new_value + '</TEXTAREA>' ;

  s += '<BUTTON class="close" OnClick="popup_close()">&times;</BUTTON>'+after ;

  var popup = popup_get_element() ;
  popup.innerHTML = s ;
  if ( the_current_cell )
    popup.column = the_current_cell.column ;

  if ( default_answer !== false )
    popup.getElementsByTagName('TEXTAREA')[0].focus() ;
}



function tail_html()
{
  if ( preferences.interface == 'L' )
    return '<span id="server_feedback"></span><div id="authenticate"></div>';

  var a ;

  if ( false )
    {
    a = '<p class="copyright"><span id="server_feedback"></span></p>'
        + '<div id="log"></div>' ;
    }
  else
    a = '<p class="copyright"></p>';

  a += "<div id=\"saving\">Les données sont en train d'être envoyées au serveur.<br>Veuillez patienter (ou vérifiez votre connexion réseau)</div>" +
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

  if ( true )
      document.write(new_new_interface()) ;
  else
      document.write(new_interface()) ;
/* onmouseout is here because it must contains the tip
    If you change the content, read 'table_init' in 'lib.js'
*/
  
  var hs = '<div class="horizontal_scrollbar"><img src="' + url
    + '/prev.gif" onclick="javascript:previous_page_horizontal();">'
    + '<div id="horizontal_scrollbar"></div><img src="' + url
    + '/next.gif" onclick="javascript:next_page_horizontal();"></div>' +
    '<div>' ;
  var w ;

  if ( true )
    w = '' ;
  else
    w = hs ;
  
  if ( ! scrollbar_right )
    w += '<div id="vertical_scrollbar"></div>' ;
  w += '<div id="divtable" class="colored"><div id="hover"></div></div>' ;
  if ( scrollbar_right )
    w += '<div id="vertical_scrollbar"></div>' ;
  if ( true )
    w += hs ;

  w += '</div></div><div id="loading_bar"><div></div></div>' ;
  document.write(w) ;
}


