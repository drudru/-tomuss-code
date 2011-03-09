/*
    TOMUSS: The Online Multi User Simple Spreadsheet
    Copyright (C) 2009-2011 Thierry EXCOFFIER, Universite Claude Bernard

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

// Reconnexion marche pas, ne reçois pas les changements (pas de frame)

function Linear()
{
  /////////////////////////////////////////////////////////////////////////////
  /////////////////////////////////////////////////////////////////////////////
  /////////////////////////////////////////////////////////////////////////////
  this.informations_cell =
    [
     new Information
     (this,
      function() {
       if ( this.L.column().real_type.cell_compute )
	 return this.L.column().type +
	   ' est un résultat de calcul non modifiable.' ;
       else
	 return 'Valeur de la cellule.' ;
     },
      'Valeur',
      function() {
	var value = this.L.cell().value ;
	if ( value.toFixed && value !== 0 )
	  value = tofixed(value).replace(/[.]*0*$/,'') ;
	return value ;
      },
      function(value) { cell_set_value_real(this.L.data_lin(),
					    this.L.data_col(),
					    value);
      },
      function() {
	if ( this.L.column().real_type.cell_compute )
	  return 'La valeur est un résultat de calcul non modifiable.' ;
	return this.L.cell().changeable() ;
      },
      function() {
	var h = this.L.column().real_type.tip_cell ;
	if ( this.L.column().type == 'Note' )
	  h = h.replace('note', "note entre " +
			this.L.column().min + ' et ' + this.L.column().max )
	    return h + '.' ;
      }
      ),
     new Information
     (this,
      function() { return 'La dernière personne à avoir modifié la cellule.' },
      'Auteur',
      function() { return this.L.cell().author ; }
      ),
     new Information
     (this,
      function () { return 'Date de la dernière modification de la cellule.' },
      'Modifié',
      function() { return date_full(this.L.cell().date) ; }
      ),
     new Information
     (this,
      function() { return 'Un commentaire associé à la cellule, ' +
	  'les étudiants peuvent voir ce commentaire.' ; },
      'Commentaire',
      function() { return this.L.cell().comment ; },
      function(value) { comment_change(this.L.data_lin(),
				       this.L.data_col(),
				       value);
      },
      function() { return table_attr.modifiable ? true :
	  "Table non modifiable" ; }
      ),
     new Information
     (this,
      function() { return "Informations officielles sur l'étudiant."; },
      '',
      function() {
	var w ;
	if ( this.L.line()[5].value != 'ok' )
	  w = "L'étudiant n'est pas inscrit à l'U.E.<br>" ;
	else
	  w = "Il est inscrit.<br>" ;
	w += student_abjs(this.L.line()[0].value) ;
	return '\001' + w.replace(/[.]<br>$/,'') ; // \001 indicate HTML code
      }
      ),
     new Information
     (this,
      function() { return "Rang de la note dans la colonne." ; },
      'Rang',
      function() { return compute_rank(this.L.data_lin(), this.L.column()).replace('&nbsp;','').replace('/', ' sur ') ; }
      ),
     new Information
     (this,
      function() { return "L'historique indique les valeurs précédentes " +
	  "prises par la cellule et qui a fait la modification." },
      'Historique',
      function() { return this.L.cell().history ; }
      )
     ] ;
  /////////////////////////////////////////////////////////////////////////////
  /////////////////////////////////////////////////////////////////////////////
  /////////////////////////////////////////////////////////////////////////////
  this.informations_column =
    [
     new Information
     (this,
      function() {return "Titre de la colonne." ; },
      'Titre',
      function() { return this.L.column().title ; },
      function(value) {
	// this.L.column().real_type.set_title(value, this.L.column());
	column_attr_set(this.L.column(), 'title', value) ;
      },
      function() { return column_change_allowed_text(this.L.column()) ; },
      function() { return "Le titre ne doit pas contenir d'espace" ; }
      ),
     new Information
     (this,
      function() {return this.L.column().real_type.tip_type ; },
      'Type',
      function() { return this.L.column().type ; },
      function(value) {
	column_attr_set(this.L.column(), 'type', value) ;
	this.L.update_column() ;
      },
      function() { return column_change_allowed_text(this.L.column()) ; },
      function() { return "Les types possibles sont : Note, Prst, Moy, Text, Nmbr, Bool, Max, Date." ; }
      ),
     new Information
     (this,
      function() {return column_attributes['weight'].tip ; },
      'Poids',
      function()
      {
	var column = this.L.column() ;
	if ( column.real_type.set_weight != unmodifiable )
	  return column.real_weight ;
	else
	  return "" ;
      },
      function(value) {
	column_attr_set(this.L.column(), 'weight', value) ;
	this.L.update_column() ;
      },
      function() { return column_change_allowed_text(this.L.column()) ; },
      function() { return "Un nombre flottant indiquant le poids de cette colonne pour les moyennes pondérées." ; }
      ),
     new Information
     (this,
      function() {return this.L.column().real_type.tip_test ; },
      'Min Max',
      function()
      {
	var column = this.L.column() ;
	if ( column.real_type.set_test != unmodifiable )
	  return column.min + ' ' + column.max ;
	else
	  return "" ;
      },
      function(value) {
	column_attr_set(this.L.column(), 'minmax', value) ;
	this.L.update_column() ;
      },
      function() { return column_change_allowed_text(this.L.column()) ; },
      function() { return "La minimum et le maximum possible pour les notes.";}
      ),
     new Information
     (this,
      function() { return "Liste des noms de colonnes sur lesquelles porte le calcul." ; },
      'Formule',
      function()
      {
	var column = this.L.column() ;
	if ( column.average_from !== undefined )
	  return column.average_from.toString().replace(/,/g,' ') ;
	else
	  return "inutile" ;
      },
      function(value) {
	column_attr_set(this.L.column(), 'columns', value) ;
	this.L.update_column() ;
      },
      function() {
	var column = this.L.column() ;
	if ( column.real_type.set_weight == unmodifiable )
	  return "Cette valeur n'est pas modifiable pour une colonne de type "+
	    column.type + ". C'est seulement pour les formules." ;
	return column_change_allowed_text(column) ;
      },
      function() { return "Noms des colonnes séparées par des espaces";}
      ),
     new Information
     (this,
      function() { return "Une explication plus détaillée du titre de la colonne, cette information est diffusée aux étudiants." ; },
      'Commentaire',
      function() { return this.L.column().comment ; },
      function(value) {
	column_attr_set(this.L.column(), 'comment', value) ;
      },
      function() { return column_change_allowed_text(this.L.column()) ; },
      function() { return "Texte libre.";}
      ),
     new Information
     (this,
      function() {return 'Valeur par défaut des cellules vides.' ; },
      'ø',
      function() {return this.L.column().empty_is ; },
      function(value) {
	column_attr_set(this.L.column(), 'empty_is', value) ;
	this.L.update_column() ;
      },
      function() { return column_change_allowed_text(this.L.column()) ; },
      function() {
	var column = this.L.column() ;
	if ( column.type == 'Note' )
	  return "Par exemple <b>0</b> ou <b>ABINJ</b>." ;
	return "Un texte libre." ;
      }
      ),
     new Information
     (this,
      function() {return 'Statistiques concernant les notes de la colonne.'; },
      '',
      function() {
	var stats = compute_histogram(this.L.data_col()) ;
	var s ;
	if ( stats.nr )
	  s = stats.nr + ' notes. Moyenne ' + tofixed(stats.average()) +
	    '. Médiane ' + tofixed(stats.mediane()) + '. Écart-type ' +
	    tofixed(stats.standard_deviation()) + '. Minimum ' +
	    tofixed(stats.min) + '. Maximum ' + tofixed(stats.max)+ '.' ;
	else
	  s = 'Pas de notes.' ;
	if ( stats.nr_ppn )
	  s += ' ' + stats.nr_ppn + ' PPN.' ;
	if ( stats.nr_abi )
	  s += ' ' + stats.nr_abi + ' ABI.' ;
	if ( stats.nr_abj )
	  s += ' ' + stats.nr_abi + ' ABJ.' ;
	if ( stats.nr_pre )
	  s += ' ' + stats.nr_pre + ' Présents.' ;
	if ( stats.nr_yes )
	  s += ' ' + stats.nr_yes + ' Oui.' ;
	if ( stats.nr_no )
	  s += ' ' + stats.nr_yes + ' Non.' ;
	if ( stats.nr_nan )
	  s += ' ' + stats.nr_nan + ' valeurs qui ne sont pas des nombres.' ;
	return s.substr(0, s.length-1) ;
	}
      ),
     new Information
     (this,
      function() { return "Expression imposant une condition sur les lignes du tableau que l'on veut afficher. <a href=\"" + url + '/doc_filtre.html" target="_new_">Documentation sur la syntaxe de l\'expression</a>.' ; },
      'Filtre',
      function() { return this.L.column().filter ; },
      function(value) {
	var column = this.L.column() ;
	column.filter = value ;
        column.real_type.set_filter(value, column) ;
	update_filters() ;
	update_filtered_lines() ;
	this.L.lin = 0 ;
      },
      function() { return true ; },
      function() {
	return 'Par exemple <kbd>truc</kbd> pour avoir seulement ce qui commence par <b>truc</b>.';
      }
      )
     ] ;
  /////////////////////////////////////////////////////////////////////////////
  /////////////////////////////////////////////////////////////////////////////
  /////////////////////////////////////////////////////////////////////////////
  this.informations_table =
    [
     new Information
     (this,
      function() {return "Statistiques." ; },
      '',
      function() { return filtered_lines.length + " lignes affichées sur " +
	  (first_line_not_empty()+1) ; }
      ),
     new Information
     (this,
      function() {return "Commentaire sur la table, il est diffusé aux étudiants.";},
      'Commentaire',
      function() { return table_attr.comment ; },
      function(value) {
	table_attr_set('comment', value) ;
      },
      function() {
	if ( table_attr.modifiable && (i_am_the_teacher||teachers.length == 0))
	  return true ;
	return "Seul un responsable de l'U.E peut modifier ce commentaire";
      },
      function() { return "Un texte libre." ; }
      ),
     new Information
     (this,
      function() {return "Les responsables de l'U.E.";},
      'Responsables',
      function() { return teachers.toString().replace(/,/g,' ') ; },
      function(value) {
	table_attr_set('masters', value) ;
      },
      function() {
	if ( table_attr.modifiable&&(i_am_the_teacher||teachers.length == 0) )
	  return true ;
	return "Seul un responsable de l'U.E peut modifier la liste des responsables.";
      },
      function() { return "Les logins des responsables de l'U.E séparés par des espaces" ; }
      )
     ] ;
  /////////////////////////////////////////////////////////////////////////////
  /////////////////////////////////////////////////////////////////////////////
  /////////////////////////////////////////////////////////////////////////////
  this.informations = this.informations_cell
  this.information = this.informations[0] ;
  this.col = 3 ;
  this.lin = 0 ;
  this.top = document.getElementById('top') ;
  this.input_edit = false ;
  this.w('<h1>' + ue + ' ' + semester + ' ' + year + '</h1>' +
         '<h2>' + table_attr.table_title + '</h2>' +
         "Appuyez sur <kbd>point d'interrogation</kbd> pour avoir l'aide. "
	 ) ;
}


var linear_w_real_queue = [] ;

function linear_w_real()
{
  if ( L === undefined )
    return ;
  if ( linear_w_real_queue.length !== 0 )
    {
      var c = '' ;
      while(linear_w_real_queue.length !== 0)
	{
	  c += '<br>' + linear_w_real_queue.splice(0,1)[0] ;
	}
      var e = document.createElement('div') ;
      e.innerHTML = c.substr(4) ; // Remove first <br>
      L.top.appendChild(e) ;
      document.body.scrollTop = 10000000 ;
    }
  if ( L.input_to_init !== undefined )
    {
      L.input_edit = true ;
      L.input.value = L.input_to_init ;
      L.input.initial_value = L.input.value ;
      L.input_to_init = undefined ;
      L.input.style.display = '' ;
      L.input.select() ;
      L.input.focus() ;
      document.body.scrollTop = 10000000 ;
    }
}

setInterval(linear_w_real, 100) ;

function linear_w(x)
{
  linear_w_real_queue.push(x) ;
}


function column_list_all2()
{
  var t = column_list_all() ;
  t.push( add_empty_columns() ) ;
  return t ;
}

function linear_data_col() { return column_list_all2()[this.col]      ; }
function linear_data_lin() { return this.line()['number']             ; }
function linear_column()   { return columns[this.data_col()]          ; }
function linear_cell()     { return this.line()[this.data_col()]      ; }
function linear_line()
{
  // update_filtered_lines() ;
  if ( this.lin < filtered_lines.length )
    return filtered_lines[this.lin] ;
  else
    return lines[add_empty_lines()] ;
}

function linear_column_title()
{
  if ( this.hide_column_title )
    return '' ;
  var empty = '' ;
  if ( this.column().is_empty )
    empty = ' qui est vide' ;
  return 'Colonne <i>' + html(this.column().title) + '</i>' + empty + ', ' ;
}

function linear_line_title()
{
  if ( this.hide_line_title )
    return '' ;
  var cls = column_list_all2() ;
  var s = '' ;
  var line = this.line() ;
  for(var data_col in cls)
    {
      data_col = cls[data_col] ;
      if ( columns[data_col].freezed == 'F' )
	s += line[data_col].value + ', ' ;
    }
  if ( s.replace(/, /g, '') === '' )
    s = "Ligne vide, indiquez le numéro d'étudiant, " ;
  return s ;
}

function linear_update_column()
{
  var column = this.column() ;
  init_column(column) ;
  column.need_update = true ;
  update_columns() ;
}

function linear_go_right(quiet)
{
  this.hide_column_title = this.hide_line_title = this.hide_what = quiet ;
  var cls = column_list_all2() ;
  this.col++ ;
  if ( this.col >= cls.length )
    {
      this.col = cls.length - 1 ;
      this.w('Plus rien à droite.') ;
    }
  this.hide_line_title = true ;
  this.display() ;
  return true ;
}

function linear_go_left(quiet)
{
  this.hide_column_title = this.hide_line_title = this.hide_what = quiet ;
  this.col-- ;
  this.hide_line_title = true ;
  if ( this.col < 0  )
    {
      this.col = 0 ;
      this.w('Plus rien à gauche.') ;
    }
  this.display() ;
  return true ;
}

function linear_go_down(quiet)
{
  this.hide_column_title = this.hide_line_title = this.hide_what = quiet ;
  // update_filtered_lines() ;
  this.lin++ ;
  this.hide_column_title = true ;
  if ( this.lin >= filtered_lines.length  )
    {
      this.lin = filtered_lines.length ;
      this.w('Plus rien au dessous.') ;
    }
  this.display() ;
  return true ;
}

function linear_go_up(quiet)
{
  this.hide_column_title = this.hide_line_title = this.hide_what = quiet ;
  this.lin-- ;
  this.hide_column_title = true ;
  if ( this.lin < 0 )
    {
      this.lin = 0 ;
      this.w('Plus rien au dessus.') ;
    }
  this.display() ;
  return true ;
}

function linear_change_show(quiet)
{
  var i = myindex(this.informations, this.information) ;
  if ( i != -1 )
    {
      i = (i+1) % this.informations.length ;
      this.information = this.informations[i] ;
    }

  this.hide_column_title = this.hide_line_title = true ;
  this.hide_what = quiet ;
  this.display() ;
  return true ;
}

function linear_set_show(quiet, table, n, col)
{
  var c ;

  if ( this.informations == table && n === undefined )
    {
      this.change_show() ;
      return true ;
    }
  if ( n === undefined )
    c = 0 ;
  else
    {
      c = n ;
      this.informations_save = this.informations ;
      this.information_save = this.information ;
      this.col_save = this.col ;
      if ( col !== undefined )
	{
	  var cls = column_list_all() ;
	  for(var i in cls)
	    {
	      if ( columns[cls[i]].title == col )
		{
		  this.col = i ;
		  break ;
		}
	    }
	}
    }

  this.informations = table ;
  this.information = table[c] ;

  if ( ! quiet )
    this.display() ;
  if ( n !== undefined )
    this.edit(quiet) ;
  return true ;
}

function linear_onkeypress(event)
{
  event = the_event(event) ;
  if ( event.keyCode == 13 )
    {
      stop_event(event) ;
      L.stop_edit() ;
      return false ;
    }
  if ( event.keyCode != 27 )
    return true ;
  L.w("Modification annulée.") ;
  L.stop_edit(true) ;
  stop_event(event) ;
}

function linear_edit(quiet)
{
  var changeable = this.information.is_changeable() ;
  if ( changeable != true )
    {
      this.w(changeable) ;
      return true ;
    }
  if ( quiet != true && this.information.content )
    this.w(this.information.content());
  this.input_to_init = this.information.get_value() ;
  return true ;
}

function linear_stop_edit(abort)
{
  if ( ! this.input_edit ) // OPERA
    return ;
  if ( this.input.value != this.input.initial_value && abort === undefined )
    this.information.change(this.input.value) ;
  this.input_edit = false ;
  this.input.value = '' ;
  this.input.style.display = 'none' ;

  if ( this.informations_save !== undefined )
    {
      if ( ! abort )
	this.display() ;

      this.informations = this.informations_save ;
      this.information = this.information_save ;
      this.col = this.col_save ;
      this.informations_save = undefined ;
      this.information_save = undefined ;
      this.col_save = undefined ;

      if ( abort )
	return ;
    }
  else
    {
      if ( abort )
	return ;

      this.hide_column_title = this.hide_line_title = true ;
    }
  this.display() ;

  update_line(this.data_lin(), this.data_col()) ;

  if ( this.informations == this.informations_column )
    {
      columns[this.data_col()].need_update = true ;  
      update_columns() ;
    }
}

function linear_display()
{
  this.w(this.information.value()) ;
  this.hide_column_title = false ;
  this.hide_line_title = false ;
  this.hide_what = false ;
}

function linear_tip()
{
  var r = this.information.help() ;

  if ( this.information.is_changeable
       && this.information.is_changeable() == true )
    r += ' Tapez sur la touche <kbd>entrée</kbd> pour l\'éditer.' ;

  this.w(r) ;
  return true ;
}

function linear_sort(dir)
{
  var sorted = false ;
  if ( this.column() != sort_columns[0] )
    {
      sort_column(undefined, this.data_col()) ;
      sorted = true ;
    }
  if ( this.column().dir != dir )
    {
      sort_column(undefined, this.data_col()) ;
      sorted = true ;
    }
  if ( ! sorted ) // force the sort (the user modified the table)
    {
      sort_column(undefined, this.data_col()) ;
      sort_column(undefined, this.data_col()) ;
    }
  var s = "Trie la colonne <i>" + this.column().title + "</i> dans l'ordre " ;
  if ( dir == 1 )
    s += "croissant." ;
  else
    s += "décroissant." ;
  this.w(s) ;
  update_filtered_lines() ;
  this.display() ;
  return true ;
}

function linear_freeze()
{
  if ( this.column().freezed )
    this.w('La colonne est maintenant figée.') ;
  else
    this.w('La colonne n\'est plus figée.') ;
  freeze_column(this.column()) ;
  return true ;
}

function linear_hide()
{
  this.w("La colonne <i>" + html(this.column().title)
	 + "</i> est maintenant cachée.") ;
  this.column().hidden = 1 ;
  this.display() ;
  return true ;
}

function linear_print()
{
  print_page() ;
  return true ;
}

function linear_suivi()
{
  window.open(suivi + '/ ' + this.line()[0].value) ;
}


function linear_help()
{
  this.w
    ('<p>Chaque ligne du tableau contient les informations sur un étudiant. '+
     '<ul><li>Les touches curseur permettent de se déplacer dans le tableau.'+
     "<li><kbd>i</kbd> permet de naviguer parmi les informations affichables."+
     "<li><kbd>a</kbd> affiche une explication sur la valeur affichée."+
     "<li><kbd>entrée</kbd> permet d'éditer une valeur." +
     " <kbd>escape</kbd> annule la saisie en cours."+
     "<li>Si l'on utilise la touche majuscule en même temps qu'une des "+
     "touches précédentes alors seulement le minimum d'information est "+
     "affiché."+
     "<li><kbd>1</kbd> permet de naviguer dans le tableau."+
     "<li><kbd>2</kbd> permet d'avoir des informations sur les colonnes"+
     "<li><kbd>3</kbd> permet d'avoir des informations sur le tableau"+
     "<li><kbd>&gt;</kbd> et <kbd>&lt;</kbd> trient les lignes suivant le contenu de la colonne."+
     "<li><kbd>.</kbd> fige ou défige la colonne courante. Le contenu des colonnes figées est indiqué quand on change de ligne."+
     "<li><kbd>x</kbd> cache la colonne courante."+
     "<li><kbd>f</kbd> édite le filtre de la colonne courante."+
     "<li><kbd>n</kbd> édite le filtre sur les noms d'étudiant."+
     "<li><kbd>p</kbd> édite le filtre sur les prénoms d'étudiant."+
     "<li><kbd>t</kbd> affiche une page imprimable en tenant compte des filtres et des colonnes cachées."+
     "<li><kbd>s</kbd> ouvre une fenêtre pour faire le suivi de l'étudiant."+
     "</ul>"
     ) ;
  return true ;
}

Linear.prototype.data_col            = linear_data_col            ;
Linear.prototype.data_lin            = linear_data_lin            ;
Linear.prototype.cell                = linear_cell                ;
Linear.prototype.line                = linear_line                ;
Linear.prototype.column              = linear_column              ;
Linear.prototype.update_column       = linear_update_column       ;
Linear.prototype.column_title        = linear_column_title        ;
Linear.prototype.line_title          = linear_line_title          ;
Linear.prototype.display             = linear_display             ;
Linear.prototype.edit                = linear_edit                ;
Linear.prototype.stop_edit           = linear_stop_edit           ;
Linear.prototype.onkeypress          = linear_onkeypress          ;
Linear.prototype.go_right            = linear_go_right            ;
Linear.prototype.go_left             = linear_go_left             ;
Linear.prototype.go_down             = linear_go_down             ;
Linear.prototype.go_up               = linear_go_up               ;
Linear.prototype.help                = linear_help                ;
Linear.prototype.w                   = linear_w                   ;
Linear.prototype.change_show         = linear_change_show         ;
Linear.prototype.set_show            = linear_set_show            ;
Linear.prototype.tip                 = linear_tip                 ;
Linear.prototype.sort                = linear_sort                ;
Linear.prototype.freeze              = linear_freeze              ;
Linear.prototype.hide                = linear_hide                ;
Linear.prototype.print               = linear_print               ;
Linear.prototype.suivi               = linear_suivi               ;

function Information(L, help, value_info, get_value, change_value, changeable,
		     content)
{
  this.L            = L            ;
  this.help         = help         ;
  this.value_info   = value_info   ;
  this.get_value    = get_value    ;
  this.change_value = change_value ;
  this.changeable   = changeable   ;
  this.content      = content      ;
}

function information_value()
{
  var prepend ;

  if ( this.L.hide_what || this.value_info === '' )
    prepend = '&nbsp;' ;
  else
    prepend = '<u>' + this.value_info + '</u> ' ;

  if ( this.L.informations != this.L.informations_cell )
    {
      this.L.hide_line_title = true ;
      if ( this.L.information == this.L.informations_column[0]
	   || this.L.informations == this.L.informations_table)
	this.L.hide_column_title = true ;      
    }

  var value = this.get_value() ;
  if ( value.substr !== undefined && value.substr(0,1) == '\001' )
    value = value.substr(1) ;
  else
    value = html(value) ;

  return this.L.line_title() + this.L.column_title() + prepend
    + '<b>' + value + '</b>.' ;
}

function information_change(value)
{
  this.change_value(value) ;
}

function information_is_changeable()
{
  if ( this.change_value === undefined )
    return "Cette information n'est pas modifiable." ;
  return this.changeable() ;
}

Information.prototype.value         = information_value      ;
Information.prototype.change        = information_change     ;
Information.prototype.is_changeable = information_is_changeable ;

var L ;
var key_history = '' ;

/* The problem is that the server must not answer because it is impossible */
function send_key_history()
{
  if ( key_history === '' )
    return ;

  L.w('<img src="' + url + "/=" + ticket + '/' + year + '/' + semester
      + '/' + ue + '/' + page_id + '/key_history/'
      + encode_uri(key_history) +
      '">') ;
  key_history = '' ; // Do not send history more than once
}

function dispatch(x)
{
  if ( x == 'init' )
    {
      L = new Linear() ;
      L.input = document.getElementsByTagName('INPUT')[0] ;
      L.input.style.width = '100%' ;
      L.input.style.display = 'none' ;
      L.display() ;
      return ;
    }
  if ( L.input_edit )
    {
      L.onkeypress(x) ;
      return ;
    }
  if ( x.keyCode == 13 && L.input_edit === false )
    {
      // Do not take into account the 'Return' just after a 'stop_edit'
      L.input_edit = 0 ;
      return ;
    }
  L.input_edit = 0 ;

  if ( x.altKey || x.ctrlKey )
    return ;

  var k = '' ;
  if ( x.which )
    k = String.fromCharCode(x.which) ;
  else
    k = String.fromCharCode(x.keyCode) ;
  if ( k == null )
    k = '' ;
  k = k.toLowerCase() ;



  switch( x.keyCode )
    {
    case 39: k = 'R' ; break ; 
    case 37: k = 'L' ; break ; 
    case 40: k = 'D' ; break ; 
    case 38: k = 'U' ; break ; 
    case 13: k = 'C' ; break ; 
    }

  r =  k == '?'  && L.help()
    || k == 'R'  && L.go_right(x.shiftKey)
    || k == 'r'  && L.go_right(x.shiftKey)
    || k == 'L'  && L.go_left(x.shiftKey)
    || k == 'l'  && L.go_left(x.shiftKey)
    || k == 'D'  && L.go_down(x.shiftKey)
    || k == 'd'  && L.go_down(x.shiftKey)
    || k == 'U'  && L.go_up(x.shiftKey)
    || k == 'u'  && L.go_up(x.shiftKey)
    || k == 'C'  && L.edit(x.shiftKey)
    || k == 'i'  && L.change_show(x.shiftKey)
    || k == 'h'  && L.tip()
    || k == 'a'  && L.tip()
    || k == '1'  && L.set_show(false, L.informations_cell)
    || k == '2'  && L.set_show(false, L.informations_column)
    || k == '3'  && L.set_show(false, L.informations_table)
    || k == '>'  && L.sort(1)
    || k == '<'  && L.sort(-1)
    || k == '.'  && L.freeze()
    || k == 'f'  && L.set_show(x.shiftKey, L.informations_column, 8)
    || k == 'n'  && L.set_show(x.shiftKey, L.informations_column, 8, 'Nom')
    || k == 'p'  && L.set_show(x.shiftKey, L.informations_column, 8, 'Prénom')
    || k == 'x'  && L.hide()
    || k == 't'  && L.print()
    || k == 's'  && L.suivi()
    ;

  if ( x.shiftKey )
    key_history += '_' ;
  key_history += k ;

  if ( r && x.keyCode !== undefined )
    {
      stop_event(x) ;
    }
  else
    {
      L.input.value = '' ;
      if ( my_identity == 'thierry.excoffier' )
	L.w('<small><small>' + k + ':' + x.keyCode + '</small></small>') ;
    }
}

function dispatch2(x)
{
  if ( navigator.appName == 'Microsoft Internet Explorer'
       || navigator.appName.toString().indexOf('Chrome') != -1)
    if ( x.keyCode == 39 || x.keyCode == 37 ||
	 x.keyCode == 40 || x.keyCode == 38 )
      {
	dispatch(x) ;
      }
}
