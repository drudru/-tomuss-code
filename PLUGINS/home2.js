/* -*- coding: utf-8 -*- */
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

function _UE(name, responsable, intitule, parcours, code, login,
	     nr_students_ue, nr_students_ec, planning, tt)
{
  this.name = name ;
  if ( parcours === undefined )
    {
      parcours = '' ;
      code = '' ;
      login = '' ;
      nr_students_ue = 1 ;
      nr_students_ec = 0 ;
      responsable = [] ;
      this.etape = true ;
    }
  else
    this.etape = false ;
  this.responsable = responsable ;
  this.intitule = intitule ;
  this.parcours = parcours ;
  this.code_ade = code ;
  this.login = login ;
  this.nr_students_ue = nr_students_ue ;
  this.nr_students_ec = nr_students_ec ;
  if ( tt === undefined )
    tt = 0 ;
  this.tt = tt ;
    
  
  this.line = this.name + '\003' + this.intitule.toLowerCase() + '\001'
    + this.responsable.join(', ') + '\002' ;
  this.line_upper = replaceDiacritics(name).toUpperCase()  + '\003'
    + replaceDiacritics(intitule).toUpperCase() + '\001'
    + replaceDiacritics(responsable.join(', ')).toUpperCase() ;

  /*
    var lm = this.name.substr(this.name.length-1) ;
    if ( lm == 'M' || lm == 'L' )
    this.code = '<!-- ' + lm + this.name + ' -->';
    else
  */
  this.code = '<!-- ' + this.name + ' -->';
}

function UE(name, responsable, intitule, parcours, code, login,
	    nr_students_ue, nr_students_ec, planning, tt)
{
  return new _UE(name, responsable, intitule, parcours,
		 code, login, nr_students_ue, nr_students_ec, planning, tt) ;
}


function check_and_replace(value, value_upper, search, search_upper)
{
  var i ;
  
  i = value_upper.indexOf(search_upper) ;
  if ( i != -1 )
    return value.substr(0,i) + '<u>' + value.substr(i, search.length)
      + '</u>' + value.substr(i+search.length) ;
}

/*
  students = undefined : All the UE
  students = true      : UE with students
  students = false     : UE without students
*/

var all_ues_sorted ;

function display_ues(txt, students)
{
  if ( txt === '' )
    return '' ;
  if ( all_ues_sorted === undefined )
    {
      var t = [] ;
      for(var ue in all_ues)
	t.push( [all_ues[ue].code, all_ues[ue].name] ) ;
      t.sort() ;
      all_ues_sorted = [] ;
      for(var ue in t)
	all_ues_sorted.push( t[ue][1] ) ;
    }
  txt_upper = replaceDiacritics(txt).toUpperCase() ;
  var s = [], t, t_upper, t_replaced ;
  var i = 0 ;
  for(var ue in all_ues_sorted)
    {
      ue = all_ues_sorted[ue] ;
      if ( all_ues[ue] === undefined )
	alert(ue);
      ue = all_ues[ue] ;
      if (students===false&&(ue.nr_students_ue !== 0 || ue.nr_students_ec !== 0))
	continue ;
      if (students===true &&ue.nr_students_ue === 0 && ue.nr_students_ec === 0)
	continue ;
      t = ue.line ;
      t_upper = ue.line_upper ;

      if ( ue.etape )
	{
	  t_replaced = check_and_replace(t, t_upper, txt, txt_upper) ;
	  if ( t_replaced !== undefined )
	    {
	      s.push(ue.code + '<a href="javascript:go(\'' + ue.name + '\')">' + t_replaced + '</a>') ;
	      i++ ;
	    }
	}
      else
	{	 
	  if (students !== true || ue.nr_students_ue )
	    {
	      t_replaced = check_and_replace('UE-' + t, 'UE-' + t_upper,
					     txt, txt_upper) ;
	      if ( t_replaced !== undefined )
		{
		  s.push(ue.code + '<a href="javascript:go(\'UE-' + ue.name + '\')">' + t_replaced + '</a>') ;
		  i++ ;
		}
	    }
	  if (ue.nr_students_ec)
	    {
	      t_replaced = check_and_replace('EC-' + t, 'EC-' + t_upper,
					     txt, txt_upper) ;
	      if ( t_replaced !== undefined )
		{
		  s.push(ue.code + '<a href="javascript:go(\'EC-' + ue.name + '\')">' + t_replaced + '</a>') ;
		  i++ ;
		}
	    }
	}
      if ( i == 100 )
	{
	  s.push('[...]') ;
	  break ;
	}
      
    }
  return '<p>' + s.join('</p><p>').replace(/\003/g,' : ').replace(/\001/g,', <small>').replace(/\002/g,'</small>') ;
}

function update_ues(txt)
{
  var with_students = display_ues(txt, true) ;
  var without_students = display_ues(txt, false) ;

  if ( without_students.length > 10 )
    without_students = "<h3>Les UE suivantes n'ont pas d'étudiants inscrits</h3>"
      + without_students ;


  document.getElementById('ue_list').innerHTML = with_students +
    without_students ;
}

var ue_line_over_last ;
var ue_line_over_plus ;

function ue_line_over_more()
{
  if ( ue_line_over_last )
    {
      ue_line_over_last.className += " ue_list_more" ;
    }
}

function ue_line_out_more()
{
  if ( ue_line_over_last )
    {
      ue_line_over_last.className = ue_line_over_last.className.replace(/ *ue_list_more/g, '') ;
    }
}

function ue_line_close()
{
  ue_line_out_more() ;
  ue_line_over_plus.childNodes[1].style.display = 'none' ;
  ue_line_over_plus.childNodes[1].innerHTML = '' ;
  ue_line_over_plus.childNodes[0].innerHTML = '+' ;
}

function ue_line_out(t)
{
  if ( ue_line_over_last )
    ue_line_over_last.className = ue_line_over_last.className.replace(/ *hover/g, '') ;
  ue_line_over_last = undefined ;
  if ( ue_line_over_plus )
    ue_line_over_plus.style.left = -1000 ;
}

function ue_set_favorite(t,code,nr)
{
  document.getElementById('feedback').innerHTML =
    '<img width="1" height="1" src="' + base + 'set_page/' + code + '/' + nr + '">' ;

  if ( nr === 0 )
    {
      delete ues_favorites[code] ;
    }
  else
    {
      ues_favorites[code] = nr ;
    }
  ue_line_close() ;
  all_ues_sorted = undefined ;
  update_ues2(document.getElementById('ue_input_name').value) ;
}

function close_frame()
{
  document.getElementById('feedback').innerHTML = '' ;
}

function do_extension(code)
{
  ue_line_close() ;
  if ( confirm("Extension de " + code + ".\n\nCette opération est irréversible.\nLes étudiants seront les mêmes pour les 2 semestres.\nVous êtes sûr vouloir le faire ?") )
    {
      var ys = first_university_year_semester() ;
      document.getElementById('feedback').innerHTML =
	'<div class="frame"><div onclick="close_frame()">Fermer</div><iframe src="'
	+ base + ys[0] + '/' + ys[1] + '/' + code
	+ '/extension"></iframe></div>' ;
    }
}

function do_delete(ue_code)
{
  var code ;
  ue_line_close() ;
  if ( confirm("Destruction de " + ue_code + ".\n\nCette DESTRUCTION est irréversible sauf pour l'administrateur TOMUSS.\nVous êtes sûr vouloir le faire ?") )
    {
      if ( ue_code.search('/') == -1 )
	code = base + year_semester() + '/' + ue_code ;
      else
	code = base + ue_code ;

      document.getElementById('feedback').innerHTML =
	'<div class="frame"><div onclick="close_frame()">Fermer</div><iframe src="'
	+ code + '/delete_this_table"></iframe></div>' ;
      
      for(var j in master_of)
	{
	  var i = master_of[j] ;
	  if ( i[0] + '/' + i[1] + '/' + i[2] == ue_code )
	    delete master_of[j] ;
	}
      ue_set_favorite(undefined, ue_code, 0) ;    
    }
}

function ue_line_click_more()
{
  if ( ue_line_over_plus.childNodes[1].style.display != 'none' )
    {
      ue_line_close() ;
    }
  else
    {
      var code = ue_line_over_code ;
      var title ;
      if ( code && code.match('.*/.*') )
	title = code ;
      else
	title = year_semester() + '/' + code ;
	
      var href ;
      if ( code && code.split('/').length == 1 )
	href = "go('" + code ;
      else
	{
	  href = "goto_url('" + base + (ue_line_over_last.childNodes[1].textContent || ue_line_over_last.childNodes[1].innerText);
	}

      var t ;
      t = '<img class="safety" src="_URL_/safe.png"><a href="javascript:'+ href
	+ '\')">Éditer la table</a>' ;

      t += '<br><img class="safety" src="_URL_/verysafe.png"><a href="javascript:'+ href
	+ '/=read-only=\')">Afficher la table sans la modifier</a>' ;

      t += '<br><img class="safety" src="_URL_/verysafe.png"><a href="javascript:'+ href
	+ '/=print-table=/=read-only=\')">Exporter ou imprimer la table</a>' ;

      t += '<br><img class="safety" src="_URL_/verysafe.png"><a href="javascript:'+ href
	+ '/=signatures-page=/=read-only=\')">Feuille d\'émargement</a>' ;
      if ( i_am_root )
	t += '<br><img class="safety" src="_URL_/unsafe.png"><a href="javascript:'+ href
	  + '/page_unload\')">Ferme les pages sur les navigateurs</a>' ;

      t += ue_line_more_links(code) ;

      var txt, n ;
      // UE Not in a semester cannot be in favorites
      if ( code && ! code.match('.*/.*') )
	{
	  n = ues_favorites[code] ;	  
	  if (n !== undefined && n > 0 )
	    {
	      t +=  '<br><img class="safety" src="_URL_/verysafe.png"><a href="javascript:ue_set_favorite(this,\''
		+ code + '\',' + ( n%1000000 - 1000000 )
		+ ');">Enlever de vos favoris</a>' ;
	      txt = 'Passer en premier de vos favoris' ;
	    }
	  else
	    {
	      txt = 'Mettre dans la liste de vos favoris' ;
	      if ( n === undefined )
		n = 0 ;
	    }

	  var nr = ues_favorites_sorted[0] ;
	  if ( nr !== undefined )
	    nr = (1 + Math.floor(ues_favorites[nr]/1000000))*1000000
	      + (n+1000000) % 1000000 ;
	  else
	    nr = 1000000 + n ;
	  
	  
	  t +=  '<br><img class="safety" src="_URL_/verysafe.png"><a href="javascript:ue_set_favorite(this,\'' + code
	    + '\',' + nr + ');">' + txt + '</a>' ;
	}
      
      if ( ues_favorites[code] )
	t += '<br><img class="safety" src="_URL_/verysafe.png">Vous avez consulté cette table ' + 
	  ((1000000+ues_favorites[code])%1000000) + ' fois' ;

      if ( code && ! code.match('.*/.*') )
	{
	  t +=  '<br><img class="safety" src="_URL_/unsafe.png"><a href="javascript:do_extension(\'' + code + '\');">Passer cette UE en NON-SEMESTRIALISÉ</a>' ;
	}

      if ( is_the_current_semester()
	   || semester() == 'Test'
	   || (code && code.match('.*/.*'))
	   )
	if ( code )
	  t +=  '<br><img class="safety" src="_URL_/unsafe.png"><a href="javascript:do_delete(\'' + code + '\');">Détruire '+ title + '</a>' ;
	else
	  t +=  '<br><img class="safety" src="_URL_/unsafe.png"><a href="javascript:do_delete(\'' + (ue_line_over_last.childNodes[1].textContent || ue_line_over_last.childNodes[1].innerText) + '\');">Détruire cette table</a>' ;

      ue_line_over_plus.childNodes[1].style.display = 'block' ;
      ue_line_over_plus.childNodes[1].innerHTML = t ;
      ue_line_over_plus.childNodes[0].innerHTML = '&times; ' + title ;
    }
}

var ue_line_over_plus_width ;
var ue_line_over_code ;

// To be redefined
function ue_line_more_links(code)
{
  return '' ;
}

function ue_line_over(code, t, click_more)
{
  ue_line_over_code = code ;

  while ( t.tagName != 'TR' )
    t = t.parentNode ;

  if ( ue_line_over_plus === undefined )
    {
      ue_line_over_plus = document.createElement('DIV') ;
      ue_line_over_plus.className = 'ue_list_more' ;
      ue_line_over_plus.innerHTML = '<div class="title">+</div><div class="more"></div>' ;
      ue_line_over_plus.onmouseover = ue_line_over_more ;
      ue_line_over_plus.onmouseout = ue_line_out_more ;

      document.body.appendChild(ue_line_over_plus) ;
      ue_line_over_plus_width = ue_line_over_plus.offsetWidth ;
      
    }

  if ( t === ue_line_over_last )
    return ;

  ue_line_out() ;

  var pos = findPos(t) ;
  ue_line_over_plus.style.left = pos[0] + t.offsetWidth - ue_line_over_plus_width;
  ue_line_over_plus.style.top = pos[1] ;
  ue_line_over_last = t ;
  if ( click_more === undefined )
    ue_line_over_plus.childNodes[0].innerHTML = '?' ;
  else
    ue_line_over_plus.childNodes[0].innerHTML = '+' ;

  /*
    if ( no_menu )
    {
    ue_line_over_plus.childNodes[1].innerHTML = '<div class="no_menu">'
    + no_menu(t) + '</div>' ;
    ue_line_over_plus.childNodes[0].onclick = function() { } ;
    }
  */
  ue_line_over_plus.childNodes[1].style.display = 'none' ;

  if ( click_more === undefined )
    click_more = function() {
      alert(ue_line_over_last.textContent || ue_line_over_last.innerText);
    } ;

  ue_line_over_plus.childNodes[0].onclick = click_more ;
  t.className += ' hover' ;
}

// To be redefined
function student_line_more_links(login)
{
  return '' ;
}

function get_student_information(login)
{
  var i ;
  for(i in favstu)
    if ( favstu[i][0] == login )
      return favstu[i] ;
  for(i in the_last_login_list)
    if ( the_last_login_list[i][0] == login )
      return the_last_login_list[i] ;
  for(i in referent_of)
    if ( referent_of[i][0] == login )
      return referent_of[i] ;
}

function toggle_favorite_student(login)
{
  document.getElementById('feedback').innerHTML =
    '<img width="1" height="1" src="' + base + 'favorite_student/' + login
    + '">' ;

  var done = false ;

  var infos = get_student_information(login) ;
  for(var i in favstu)
    if ( favstu[i][0] == login )
      {
	delete favstu[i] ;
	done = true ;
	break ;
      }
  if ( ! done && infos )
    {
      favstu.push(infos) ;
      done = true ;
    }

  if ( done )
    {
      update_favorite_student();	
      ue_line_close() ;
      ue_line_out() ;
    }
}

function i_am_referent_of(login)
{
  login = login_to_id(login) ;
  for(var i in referent_of)
    if ( referent_of[i][0] == login )
      return true ;
  return false ;
}

function referent_get(login)
{
  document.getElementById('feedback').innerHTML =
    '<img width="1" height="1" src="' + base + 'referent_get/' + login + '">' ;

  if ( i_am_referent_of(login) )
    return ;

  var done = false ;
  var infos = get_student_information(login) ;

  if ( infos )
    {
      referent_of.push(infos) ;
      done = true ;
    }

  if ( done )
    {
      update_referent_of_done = false ;
      update_referent_of();	
      ue_line_close() ;
      ue_line_out() ;
    }
}

window.set_the_referent = function(x) {
  document.getElementById('student_referent').innerHTML = x ; } ;

function student_click_more(t)
{
  if ( ue_line_over_plus.childNodes[1].style.display != 'none' )
    {
      ue_line_close() ;
      return ;
    }
  var login = ue_line_over_last.childNodes[1].textContent || ue_line_over_last.childNodes[1].innerText ;

  var message = '<img class="safety" src="_URL_/verysafe.png">Ajouter aux favoris' ;
  for(var i in favstu)
    if ( login == favstu[i][0] )
      {
	message = '<img class="safety" src="_URL_/safe.png">Retirer des favoris' ;
	break ;
      }

  var more_link1 = '' ;
  if ( i_am_a_referent )
    more_link1 = '<img class="safety" src="_URL_/verysafe.png"><a href="javascript:goto_url(base+\'bilan/' + login + '\')">Bilan TOMUSS de l\'étudiant</a><br>' ;

  var send_mail = 'Adresse mail inconnue.<br>' ;
  if ( the_student_mails[login] !== '' )
    send_mail = '<img class="safety" src="_URL_/verysafe.png"><a href="mailto:' + the_student_mails[login]
      + '">Envoyer un mail</a><br>' ;

  var more_link = '<span id="student_referent">Son référent est...</span><br>';

  document.getElementById('feedback').innerHTML = '<iframe style="width:1;height:1;border:0px" src="' + base + 'referent/' + login + '"></iframe>' ;

  if ( i_am_a_referent )
    {
      if ( ! i_am_referent_of(login) )
	{
	  more_link += '<img class="safety" src="_URL_/veryunsafe.png"><a href="javascript:referent_get(\'' + login +
	    '\')">Je veux être référent pédagogique de cet étudiant</a><br>' ;
	}
    }

  ue_line_over_plus.childNodes[0].innerHTML = '&times;' ;
  ue_line_over_plus.childNodes[1].style.display = 'block' ;
  ue_line_over_plus.childNodes[1].innerHTML = 
    '<img class="safety" src="_URL_/verysafe.png"><a href="javascript:go_suivi_student(\'' + the_login(login) + '\')">Suivi de l\'étudiant.</a><br>'
    + student_line_more_links(login)
    + more_link1
    + send_mail
    + '<a href="javascript:toggle_favorite_student(\'' + login
    + '\')">' + message + '</a><br>' + more_link
    + '<img class="photo" src="' + student_picture_url(login) + '">'
    + '<img class="bigicone" src="'+suivi[year_semester()] + '/_'+ login
    + '"><br>'
    + '<small>Carré de couleur de gauche : les présences<br>'
    + 'Carré de couleur de droite : les notes</small>' ;
}


function ue_line(ue, code, content)
{
  var html_class = '' ;

  if ( ue )
    {
      if (code.match(/^UE-/) && ue.nr_students_ue)
	html_class += ' with_students' ;
      if (code.match(/^EC-/) == 0 && ue.nr_students_ec)
	html_class += ' with_students' ;
    }

  var tt ;
  var c = code.substr(3).split('-')[0] ;
  if ( all_ues[c] && all_ues[c].tt )
    tt = hidden_txt('<img class="tt" src="tt.png">',
		    'Il y a au moins<br>un tiers temps<br>qui suit l\'UE') ;
  else
    tt = '' ;

  return '<tr class="' + html_class + '" onmouseover="ue_line_over(\'' + code + '\',this,ue_line_click_more);" onclick="javascript:go(\'' + code
    + '\')"><td>' + tt + content + '</td></tr>' ;

}

function ue_line_join(s)
{
  return s.join('\n')
    .replace('<td>', '<td >')
    .replace(/\003/g,'</td><td class="title">')
    .replace(/\001/g,'</td><td>')
    .replace(/\002/g,'') ;
}

function display_ue_list(s, txt, txt_upper, names)
{
  var ue_code ;
  for(var ue_code in names)
    {
      ue_code = names[ue_code] ;
      var apogee = ue_code.replace(/-[0-9]$/,'').replace(/^(UE|EC)-/,'') ;
      ue = all_ues[apogee] ;
      if ( ue === undefined )
	{
	  t = ue_code + '\003?\001\002' ;
	  t_upper = t ;
	}
      else
	{
	  t = ue.line.replace(/.*\003/, ue_code + '\003') ;
	  t_upper = ue.line_upper.replace(/.*\003/, ue_code + '\003') ;
	}
      t_replaced = check_and_replace(t, t_upper, txt, txt_upper) ;
      
      s.push(ue_line(ue, ue_code, t_replaced ? t_replaced : t)) ;
    }
}

var ues_spiral ;
var ues_favorites_sorted ;

function update_ues_master_of(txt, txt_upper)
{
  if ( master_of.length === 0 )
    return ;

  var s = ['<tr><th colspan="3">' +
	   hidden_txt('Vos tables',
		      'Ces tables TOMUSS ne correspondent pas à des UE<br>Mais vous en êtes un des responsables')
	   + '</th></tr>'] ;
  master_of.sort();
  for(var i in master_of)
    {
      i = master_of[i] ;
      var code = i[0] + '/' + i[1] + '/' + i[2] ;
      s.push('<tr onmouseover="ue_line_over(\''
	     + code + '\',this,ue_line_click_more);" '
	     + 'onclick="javascript:goto_url(\'' + base + code
	     + '\')"><td></td><td colspan="2">' + code + '</td></tr>') ;
    }
  s = ue_line_join(s) ;

  document.getElementById('ue_list').childNodes[3].innerHTML = '<table class="with_margin uelist"><colgroup><col class="code"><col class="title"><col class="responsable"></colgroup>' + s + '</table>' ;
}

function cmp_favorites(x,y)
{
  return ues_favorites[y] - ues_favorites[x] ;
}

function update_ues_favorites(txt, txt_upper)
{
  if ( ues_favorites.length === 0 )
    return ;

  ues_favorites_sorted = [] ;
  var begin ;
  for(var i in ues_favorites)
    {
      // XXX Find a better way to sort 'semester' tables from the others tables
      if ( ues_favorites[i] > 0
	   && ( i.substr(2 ,1) == '-'
		|| i.substr(0,6) == 'etape-'
		))
	ues_favorites_sorted.push(i) ;
    }

  ues_favorites_sorted.sort(cmp_favorites) ;
  ues_favorites_sorted= ues_favorites_sorted.slice(0,preferences.nr_favorites);

  if ( preferences.favoris_sort === "OUI" )
    ues_favorites_sorted.sort() ;
  
  var s = ['<tr><th colspan="3">' +
	   hidden_txt('UE Favorites',
		      'Vous pouvez modifier cette liste en cliquant sur le <span class="ue_list_more_help">+</span>.<br>Le nombre de favoris est modifiable dans les préférences,<br>ainsi que l\'ordre du tri.')
	   + '</th></tr>'] ;
  display_ue_list(s, txt, txt_upper, ues_favorites_sorted) ;
  s = ue_line_join(s) ;
  document.getElementById('ue_list').childNodes[1].innerHTML = '<table class="with_margin uelist"><colgroup><col class="code"><col class="title"><col class="responsable"></colgroup>' + s + '</table>' ;
}

function update_ues_spiral(txt, txt_upper)
{
  if ( ues_spiral === undefined || ues_spiral.length === 0 )
    return ;
  ues_spiral_sorted = true ;
  var s = ['<tr><th colspan="3">' +
	   hidden_txt('Responsable des UE',
		      'Ce sont les UE pour lesquelles vous êtes<br>indiqué comme responsable dans GASEL')
	   + '</th></tr>'] ;
  display_ue_list(s, txt, txt_upper, ues_spiral) ;
  s = ue_line_join(s) ;
  document.getElementById('ue_list').childNodes[2].innerHTML = '<table class="with_margin uelist"><colgroup><col class="code"><col class="title"><col class="responsable"></colgroup>' + s + '</table>' ;
}

function update_ues_searched(txt, txt_upper)
{
  var s, t, t_upper, t_replaced ;

  s = [] ;

  for(var ue in all_ues_sorted)
    {
      ue = all_ues_sorted[ue] ;
      ue = all_ues[ue] ;
      t = ue.line ;
      t_upper = ue.line_upper ;

      if ( ue.etape )
	{
	  t_replaced = check_and_replace(t, t_upper, txt, txt_upper) ;
	  if ( t_replaced !== undefined )
	    s.push(ue_line(ue, ue.name, t_replaced)) ;
	}
      else
	{
	  t_replaced = check_and_replace('UE-' + t, 'UE-' + t_upper,
					 txt, txt_upper) ;
	  if ( t_replaced !== undefined )
	    s.push(ue_line(ue, 'UE-' + ue.name, t_replaced)) ;
	  if (ue.nr_students_ec)
	    {
	      t_replaced = check_and_replace('EC-' + t, 'EC-' + t_upper,
					     txt, txt_upper) ;
	      if ( t_replaced !== undefined )
		s.push(ue_line(ue, 'EC-' + ue.name, t_replaced));
	    }
	}
      if ( s.length == 100 )
	{
	  s.push('<tr><td colspan="3">La liste a été tronquée</td></tr>') ;
	  break ;
	}
      
    }
  if ( s.length == 0 && txt != 'UNFOUNDABLETEXT\001' )
    s.push('<tr><th colspan="3" style="background-color:white">Aucune UE ne correspond à votre recherche</td></tr>');

  s = ue_line_join(s) ;
  document.getElementById('ue_list').childNodes[0].innerHTML = '<table class="with_margin uelist searchresult"><colgroup><col class="code"><col class="title"><col class="responsable"></colgroup>' + s + '</table>' ;
}

function update_ues2(txt, clicked)
{
  if ( all_ues_sorted === undefined )
    {
      // Initialize sorted UES
      var t = [] ;
      ues_spiral = [] ;
      for(var ue in all_ues)
	{
	  if ( myindex(all_ues[ue].login, username) != -1 )
	    ues_spiral.push('UE-' + ue) ;
	  t.push( [all_ues[ue].code, all_ues[ue].name] ) ;
	}
      t.sort() ;
      all_ues_sorted = [] ;
      for(var ue in t)
	all_ues_sorted.push( t[ue][1] ) ;

      document.getElementById('ue_list').innerHTML =
	'<div></div><div></div><div></div><div></div><div></div>' ;
    }

  ue_line_out() ;

  if ( txt === '' )
    txt = 'UNFOUNDABLETEXT\001' ;
  var txt_upper = replaceDiacritics(txt).toUpperCase() ;

  update_ues_searched(txt, txt_upper) ;
  update_ues_favorites(txt, txt_upper) ;
  update_ues_spiral(txt, txt_upper) ;
  update_ues_master_of(txt, txt_upper) ;
  update_ues_unsaved() ;

  if ( window.localStorage )
    {
      try
	{
	  window.addEventListener('storage', storageEventHandler, false);
	}
      catch(e)
	{
	}
    }
}

function storageEventHandler(e)
{
  ue_line_close() ;
  update_ues_unsaved() ;
}

function update_ues_unsaved()
{
  if ( ! window.localStorage )
    return ;
  var index = localStorage['index'] ;
  if ( ! index )
    {
      document.getElementById('ue_list').childNodes[4].innerHTML = '' ;
      return ;
    }
  var s = ['<tr><th colspan="3">' +
	   hidden_txt('Table avec des donnée non sauvegardée',
		      'VISITEZ CES TABLES POUR SAUVER LEUR CONTENU.<br>\nEn effet, le contenu de ces tables est en parti dans votre navigateur')
	   + '</th></tr>'] ;
  var unsaved = index.substr(1).split('\n') ;
  for(var i in unsaved)
    {
      i = unsaved[i].substr(1) ;
      s.push('<tr class="unsaved_data" onmouseover="ue_line_over(\''
	     + i + '\',this,ue_line_click_more);" '
	     + 'onclick="javascript:goto_url(\'' + base + i
	     + '\')"><td></td><td colspan="2">' + i + '</td></tr>') ;
    }
  s = ue_line_join(s) ;
  document.getElementById('ue_list').childNodes[4].innerHTML = '<table class="with_margin uelist"><colgroup><col class="code"><col class="title"><col class="responsable"></colgroup>' + s + '</table>' ;
}


var update_referent_of_done ;

function title_case(txt)
{
  return txt.substr(0,1) + txt.substr(1).toLowerCase() ;
}

function cmp_students(a,b)
{
  a = a[2]+a[1] ;
  b = b[2]+b[1] ;
  if ( a < b ) return -1 ;
  if ( a > b ) return 1 ;
  return 0 ;
}

var the_student_mails = {} ;

function student_line(i, hide_icon)
{
  the_student_mails[i[0]] = i[3] ;
  if ( hide_icon )
    hide_icon = '&nbsp;' ;
  else
    hide_icon = '<img class="icone" src="' + suivi[year_semester()] + '/_'
      + i[0] + '">' ;
  return '<tr onmouseover="ue_line_over(\'' + i[0] + '\',this,student_click_more);" '
    + 'onclick="javascript:go_suivi_student(\'' + i[0]
    + '\')"><td>' + hide_icon
    + '<td class="student_id">' + i[0] + '<td>'
    + i[2] + ' ' + title_case(i[1])
    + '</tr>' ;
}

function update_favorite_student()
{
  update_a_student_list('the_favorite_students', favstu,
			'étudiants favoris', 'javascript:go_favoris()') ;
}

function update_referent_of()
{
  if ( update_referent_of_done )
    return ;
  update_referent_of_done = true ;
  update_a_student_list('the_students', referent_of,
			'étudiants liés', 'javascript:go_referent()') ;
}

function go_import_list()
{
  create_popup('import_list',
	       "Devenir référent d'une liste d'étudiants",
	       "Indiquez les <b>numéros d'étudiants</b> dont "
	       + "vous voulez devenir référent pédagogique",
	       'Puis cliquez sur : <BUTTON OnClick="go_import_list_do();">Je veux être le référent pédagogique !</BUTTON>.',
	       '') ;
}

function go_import_list_do()
{
  var values = popup_text_area().value.split(/[ \t\n,;.:]+/) ;

  create_popup('import_list',
	       "Résultat de l'opération :",
	       '<iframe width="100%" src="' + base + 'referent_get/'
	       + values.join('/') + '">' + '</iframe>',
	       "Actualisez la page d'accueil pour voir la nouvelle liste.",
	       false) ;
}


function update_a_student_list(html_id, student_list, title, notes)
{
  var the_students = document.getElementById(html_id) ;

  if ( student_list.length === 0 )
    return ;
  
  var s = [] ;
  var m = [] ;
  var logins = [] ;

  student_list.sort(cmp_students) ;
  for(var i in student_list)
    {
      i = student_list[i] ;
      s.push(student_line(i, student_list.length > 100)) ;
      m.push(i[3]) ;
      logins.push(i[0]) ;
    }

  var blocnote = hidden_txt('<a href="' + notes + '">Blocnote</a>',
			    'Pour prendre des notes sur ces étudiants') ;

  var mails = hidden_txt('<a href="mailto:?bcc=' + m.join(',') + '">Mail</a>',
			 "Envoi d'un message à ces étudiants") ;

  var suivis = hidden_txt('<a href="javascript:go_suivi_student(\''
			  + logins.join(',') + '\')">Suivi</a>',
			  "Afficher le suivi de ces étudiants") ;


  var import_list = '';
  if ( html_id === 'the_students')
    import_list = hidden_txt('<a href="javascript:go_import_list(\''
			     + logins.join(',') + '\')">Import</a>',
			     "Devenir référent d'une liste d'étudiants") ;

  the_students.innerHTML =
    '<table class="with_margin student_list">'
    + '<colgroup><col class="student_icon"><col class="student_id"><col></colgroup>'
    + '<tr><th colspan="3">' + student_list.length + ' ' +title + '<br><small>'
    + blocnote + '/' + mails + '/' + suivis + '/' + import_list
    + '</small></th></tr>'
    + s.join('\n') + '</table>' ;
}

var the_last_login_list ;
var the_last_login_asked ;
var last_login_cache = {} ;

// This function may be called by 'login_list' plugin.
function full_login_list(login, results, add)
{
  if ( ! document.getElementById('students_list') )
    {
      // We are in a table, not the home page
      login_list(login, results) ;
      return ;
    }

  var s = [], firstname, surname, icone ;

  if ( add )
    {
      // Not used. And there is a bug
      results = results.concat(results, last_login_cache[login]) ;
      results.sort(cmp_students) ;
      last_login_cache[login] = results ;
    }
  else
    {
      results.sort(cmp_students) ;
      last_login_cache[login] = results ;
    }

  if ( login != the_last_login_asked )
    return ;

  the_last_login_list = results ;
  for(var infos in results)
    s.push(student_line(results[infos], results.length > 20)) ;
  if ( results.length === 0 )
    s = ['<tr><td colspan="3" style="color:black">Recherche infructueuse</tr>'] ;
  if ( s.length >= 99 )
    s.push('<tr><td colspan="3" style="color:black">Liste tronquée...</tr>') ;
  document.getElementById('students_list').innerHTML =
    '<table class="student_list" style="margin-top:0">'
    + '<colgroup><col class="student_icon"><col class="student_id"><col></colgroup>'
    + s.join('\n') + '</table>' ;
}

var update_students_timeout ;

function update_students()
{
  var input = document.getElementById('search_name') ;
  var what = replaceDiacritics(input.value) ;
  what = what.replace(/ *$/,'') ;

  if ( what == input.old_value )
    return ;

  input.old_value = what ;

  ue_line_out() ;
  the_last_login_asked = what ;
  if ( what === '' )
    {
      document.getElementById('students_list').innerHTML = '' ;
      return ;
    }
  if ( last_login_cache[what] )
    {
      full_login_list(what, last_login_cache[what]) ;
      return ;
    }
  if ( update_students_timeout )
    clearTimeout(update_students_timeout) ;
  
  update_students_timeout = setTimeout(update_students_real, 500) ;
}

function update_students_real()
{
  var s = document.createElement('SCRIPT') ;
  s.src = base + 'login_list/' + encode_uri(the_last_login_asked) ;
  document.getElementsByTagName('BODY')[0].appendChild(s) ;
  document.getElementById('students_list').innerHTML = 'Recherche en cours' ;
  update_students_timeout = undefined ;
}
