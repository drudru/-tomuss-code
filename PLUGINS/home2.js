/* -*- coding: utf-8 -*- */
/*
  TOMUSS: The Online Multi User Simple Spreadsheet
  Copyright (C) 2008-2014 Thierry EXCOFFIER, Universite Claude Bernard

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
  Add more link to the UE menu on home page
*/
function ue_line_more_links(code)
{
  return '' ;
}

/*REDEFINE
  Add more link to the student menu on home page
*/
function student_line_more_links(login)
{
  return '' ;
}

function scrollTopElement(scrollable)
{
  while ( scrollable && scrollable.scrollTop === 0 )
    scrollable = scrollable.parentNode ;
  if ( scrollable && scrollable.scrollTop !== undefined )
    return scrollable ;
}

function resetScroll(scrollable)
{
  var s = scrollTopElement(scrollable) ;
  if (s)
    s.scrollTop = 0 ;
}


function _UE(name, responsable, intitule, parcours, code, login,
	     nr_students_ue, nr_students_ec, planning, tt, credit, old_names)
{
  this.name = name ;
  if ( parcours === undefined ) // || name.indexOf('etape-') == 0 )
    {
      parcours = '' ;
      code = '' ;
      nr_students_ue = 1 ;
      nr_students_ec = 0 ;
//      this.etape = true ;
    }
//  else
//    this.etape = false ;
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
  this.credit = credit ;
  this.old_names = old_names ;
  this.planning = planning ;

  var more = '' ;
  if ( credit >= 0 )
      more += '<br>' + credit + ' ' + _("MSG_home_credit") ;
  if ( old_names && old_names.length )
      more += '<br>' + _("MSG_home_old_codes") + old_names.join(' ') ;
  if ( more )
      more = '<span class="ue_more">' + more ;

  this.line = this.name + '\003' + this.intitule.toLowerCase() + more + '\001'
    + this.responsable.join(', ') + '\002' ;
  this.line_upper = replaceDiacritics(this.line.toUpperCase())
      .replace('\002', '') ;
  this.code = '<!-- ' + this.name + ' -->';
}

function UE(name, responsable, intitule, parcours, code, login,
	    nr_students_ue, nr_students_ec, planning, tt, credit, old_names)
{
  return new _UE(name, responsable, intitule, parcours,
		 code, login, nr_students_ue, nr_students_ec, planning, tt,
		 credit, old_names) ;
}


function check_and_replace(value, value_upper, search, search_upper)
{
  var i ;
  
  i = value_upper.indexOf(search_upper) ;
  if ( i != -1 )
      {
	  var v, left ;
	  left =  value.substr(0, i) ;
	  if ( left.match(/<[^>]*$/) )
	      return ;
	  v = left + '<u>' + value.substr(i, search.length)
	      + '</u>' + value.substr(i+search.length) ;
	  return v ;
      }
}

var all_ues_sorted ;
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
  if ( ue_line_over_plus ) // Can be undefined from storageEventHandler
    {
      ue_line_over_plus.childNodes[1].style.display = 'none' ;
      ue_line_over_plus.childNodes[1].innerHTML = '' ;
      ue_line_over_plus.childNodes[0].innerHTML = '+' ;
    }
}

function ue_line_out(t)
{
  hide_the_tip_real(true) ;
  if ( ue_line_over_last )
    ue_line_over_last.className = ue_line_over_last.className.replace(/ *hover/g, '') ;
  ue_line_over_last = undefined ;
  if ( ue_line_over_plus )
    ue_line_over_plus.style.left = '-1000px' ;
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

function do_extension(code)
{
  ue_line_close() ;
  if ( confirm(_("ALERT_home_extend_before") + code + "\n" +
	       _("ALERT_home_extend_after") + "\n\n" +
	       _("ALERT_are_you_sure") ) )
    {
      var ys = first_university_year_semester() ;
      create_popup('import_popup',
		   _("ALERT_home_extend_before") + code,
		   '<iframe width="100%" src="'
		   + base + ys[0] + '/' + ys[1] + '/' + code
		   + '/extension"></iframe>',
		   '', false) ;
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
      t = '<img class="safety" src="_FILES_/safe.png"><a href="javascript:'+href
	    + '\')">' + _("B_home_edit") + '</a>'
	    + '<br><img class="safety" src="_FILES_/verysafe.png">'
	    + '<a href="javascript:'+ href
	    + '/=read-only=\')">' + _("B_home_display") + '</a>'
	    + '<br><img class="safety" src="_FILES_/verysafe.png">'
	    + '<a href="javascript:'+ href + '/=print-table=/=read-only=\')">'
	    + _("B_home_export_print") + '</a>'
	    + '<br><img class="safety" src="_FILES_/verysafe.png">'
	    + '<a href="javascript:'+ href
	    + '/=signatures-page=/=read-only=\')">' + _("B_home_signature")
	    + '</a>' ;
      if ( i_am_root )
	t += '<br><img class="safety" src="_FILES_/unsafe.png">'
	    + '<a href="javascript:' + href
	    + '/page_unload\')">' + _("B_home_close_pages") + '</a>' ;

      t += ue_line_more_links(code) ;

      var txt, n ;
      // UE Not in a semester cannot be in favorites
      if ( code && ! code.match('.*/.*') )
	{
	  n = ues_favorites[code] ;	  
	  if (n !== undefined && n > 0 )
	    {
	      t +=  '<br><img class="safety" src="_FILES_/verysafe.png"><a href="javascript:ue_set_favorite(this,\''
		+ code + '\',' + ( n%1000000 - 1000000 )
		    + ');">' + _("B_home_remove_bookmark") + '</a>' ;
	      txt = _("B_home_bookmark_first") ;
	    }
	  else
	    {
	      txt = _("B_home_bookmark") ;
	      if ( n === undefined )
		n = 0 ;
	    }

	  var nr = ues_favorites_sorted[0] ;
	  if ( nr !== undefined )
	    nr = (1 + Math.floor(ues_favorites[nr]/1000000))*1000000
	      + (n+1000000) % 1000000 ;
	  else
	    nr = 1000000 + n ;
	  
	  
	  t +=  '<br><img class="safety" src="_FILES_/verysafe.png"><a href="javascript:ue_set_favorite(this,\'' + code
	    + '\',' + nr + ');">' + txt + '</a>' ;
	}
      
      if ( ues_favorites[code] )
	t += '<br><img class="safety" src="_FILES_/verysafe.png">'
            + _("MSG_home_nr_view_before")
	    + ((1000000+ues_favorites[code])%1000000)
	    +  _("MSG_home_nr_view_after") ;

      if ( code && ! code.match('.*/.*') )
	{
	  t +=  '<br><img class="safety" src="_FILES_/unsafe.png"><a href="javascript:do_extension(\'' + code + '\');">' + _("B_home_unsemestrialize") + '</a>' ;
	}

      ue_line_over_plus.childNodes[1].style.display = 'block' ;
      ue_line_over_plus.childNodes[1].innerHTML = t ;
      ue_line_over_plus.childNodes[0].innerHTML = '&times; ' + title ;
    }
}

var ue_line_over_plus_width ;
var ue_line_over_code ;

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
  ue_line_over_plus.style.left = pos[0] + t.offsetWidth - ue_line_over_plus_width + 'px';
  ue_line_over_plus.style.top = pos[1] + 'px' ;
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

  var message = '<img class="safety" src="_FILES_/verysafe.png">'
	+ _("B_home_bookmark") ;
  for(var i in favstu)
    if ( login == favstu[i][0] )
      {
	message = '<img class="safety" src="_FILES_/safe.png">'
	      + _("B_home_remove_bookmark") ;
	break ;
      }

  var more_link1 = '' ;
  if ( i_am_a_referent )
      more_link1 = '<img class="safety" src="_FILES_/verysafe.png">'
	+ '<a href="javascript:goto_url(base+\'bilan/' + login + '\')">'
	+ _("B_home_bilan_tomuss") + '</a><br>' ;

    var send_mail = _("MSG_unknown_mail") + '<br>' ;
  if ( the_student_mails[login] !== '' )
    send_mail = '<img class="safety" src="_FILES_/verysafe.png">'
	+ '<a href="mailto:' + the_student_mails[login]
	+ '">' + _("B_home_sendmail") + '</a><br>' ;

    var more_link = '<span id="student_referent">' + _("MSG_home_referent_is")
	+ '</span><br>';

  document.getElementById('feedback').innerHTML =
	'<iframe style="width:1;height:1;border:0px" src="' + base
	+ 'referent/' + login + '"></iframe>' ;

  if ( i_am_a_referent )
    {
      if ( ! i_am_referent_of(login) )
	{
	  more_link += '<img class="safety" src="_FILES_/veryunsafe.png">'
		+ '<a href="javascript:referent_get(\'' + login
		+ '\')">' + _("MSG_home_become_referent") + '</a><br>' ;
	}
    }

  ue_line_over_plus.childNodes[0].innerHTML = '&times;' ;
  ue_line_over_plus.childNodes[1].style.display = 'block' ;
  ue_line_over_plus.childNodes[1].innerHTML = 
	'<img class="safety" src="_FILES_/verysafe.png">'
	+ '<a href="javascript:go_suivi_student(\'' + the_login(login)
	+ '\')">' + _("MSG_home_suivi") + '</a><br>'
	+ student_line_more_links(login)
	+ more_link1
	+ send_mail
	+ '<a href="javascript:toggle_favorite_student(\'' + login
	+ '\')">' + message + '</a><br>' + more_link
	+ '<img class="photo" src="' + student_picture_url(login) + '">'
        + (suivi[year_semester()] !== undefined ?
	   '<img class="bigicone" src="'+suivi[year_semester()] + '/_' + login
	   + '"><br>'
	   + '<small>' + _("TIP_home_squares") + '</small>'
	   : '') ;
}

function get_ue(code)
{
  code = code.replace(/-[0-9]$/, '') ;
  if ( all_ues[code] )
    return all_ues[code] ;
  code = code.split("-")[1] ;
  if ( all_ues[code] )
    return all_ues[code] ;
}

function ue_line(ue, code, content)
{
  var html_class = '' ;
  if ( ue )
    {
      if (ue.nr_students_ue)
	html_class += ' with_students' ;
      else if (code.match(/^EC-/) == 0 && ue.nr_students_ec)
	html_class += ' with_students' ;
    }

  var ue = get_ue(code) ;
  var tt ;
  if ( ue && ue.tt )
      tt = hidden_txt('<img class="tt" src="'
		      + url + '/tt.png">', _("TIP_home_tt")) ;
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

      var ue = get_ue(ue_code) ;
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
var display_years = {} ;

function toggle_year(year)
{
  ue_line_out() ;
  display_years[year] = ! display_years[year] ;
  update_ues_master_of() ;
}

function update_ues_master_of(txt, txt_upper)
{
  if ( master_of.length === 0 )
    return ;

  var s = [] ;
  master_of.sort();
  var years = {}, last_year ;
  for(var i in master_of)
    {
      i = master_of[i] ;
      var code = i[0] + '/' + i[1] + '/' + i[2] ;
      var ue = get_ue(i[2]) ;
      if ( ue && myindex(ue.login, username) != -1 )
	  continue ; // Yet in Spiral table
      years[i[0]] = true ;
      last_year = i[0] ;
      if ( display_years[i[0]] )
	s.push('<tr onmouseover="ue_line_over(\''
	       + code + '\',this,ue_line_click_more);" '
	       + 'onclick="javascript:goto_url(\'' + base + code
	       + '\')"><td></td><td colspan="2">' + code + '</td></tr>') ;
    }
  var style, buttons = '' ;
  for(var i in years)
  {
    style = display_years[i] ? 'background:#8F8' : '' ;
    buttons += ' <a id="year' + i + '" href="javascript:toggle_year('
      + i + ')" style="' + style + '">' + i + '</a>' ;
  }

  s = ue_line_join(s) ;
  document.getElementById('ue_list_masters').innerHTML =
    '<table class="with_margin uelist">'
    + '<colgroup><col class="code">'
    + '<col class="title">'
    + '<col class="responsable">'
    + '</colgroup>'
    + '<tr><th colspan="3">'
    + hidden_txt(_("TH_home_master_of"), _("TIP_home_master_of"))
    + '</th></tr>'
    + '<tr><th colspan="3">' + buttons + '</th></tr>'
    + s + '</table>' ;
  if ( display_years[last_year] === undefined )
    toggle_year(last_year) ;
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
      if ( get_ue(i) && ues_favorites[i] >= 0 )
	ues_favorites_sorted.push(i) ;
    }
  ues_favorites_sorted.sort(cmp_favorites) ;
  ues_favorites_sorted= ues_favorites_sorted.slice(0,preferences.nr_favorites);

  if ( test_bool(preferences.favoris_sort) === yes )
    ues_favorites_sorted.sort() ;
  
  var s = ['<tr><th colspan="3">' +
	   hidden_txt(_("TH_home_bookmark_ue"),
		      _("TIP_home_bookmark_ue_before")
		      + ' <span class="ue_list_more_help">+</span> '
		      + _("TIP_home_bookmark_ue_after"))
	   + '</th></tr>'] ;
  display_ue_list(s, txt, txt_upper, ues_favorites_sorted) ;
  s = ue_line_join(s) ;
  document.getElementById('ue_list_favorites').innerHTML = '<table class="with_margin uelist"><colgroup><col class="code"><col class="title"><col class="responsable"></colgroup>' + s + '</table>' ;
}

function update_ues_spiral(txt, txt_upper)
{
  if ( ues_spiral === undefined || ues_spiral.length === 0 )
    return ;
  ues_spiral_sorted = true ;
  var s = ['<tr><th colspan="3">' +
	   hidden_txt(_("TH_home_ue_master"), _("TIP_home_ue_master"))
	   + '</th></tr>'] ;
  display_ue_list(s, txt, txt_upper, ues_spiral) ;
  s = ue_line_join(s) ;
  document.getElementById('ue_list_spiral').innerHTML = '<table class="with_margin uelist"><colgroup><col class="code"><col class="title"><col class="responsable"></colgroup>' + s + '</table>' ;
}

function update_ues_searched(txt, txt_upper)
{
    var s, t, t_upper, t_replaced, prefix ;

  s = [] ;

  for(var ue in all_ues_sorted)
    {
      ue = all_ues_sorted[ue] ;
      ue = all_ues[ue] ;
      t = ue.line ;
      t_upper = ue.line_upper ;
      if ( false && ue.etape )
	{
	  t_replaced = check_and_replace(t, t_upper, txt, txt_upper) ;
	  if ( t_replaced !== undefined )
	    s.push(ue_line(ue, ue.name, t_replaced)) ;
	}
      else
	{
	  if ( ue.name.match('-') )
	      prefix = '' ;
	  else
	      prefix = 'UE-' ;
	  t_replaced = check_and_replace(prefix+ t, prefix + t_upper,
					 txt, txt_upper) ;
	  if ( t_replaced !== undefined )
	    s.push(ue_line(ue, prefix + ue.name, t_replaced)) ;
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
	    s.push('<tr><td colspan="3">' + _("TIP_home_truncated")
		   + '</td></tr>') ;
	  break ;
	}
      
    }
  if ( s.length == 0 && txt != 'UNFOUNDABLETEXT\001' )
    s.push('<tr><th colspan="3" style="background-color:white">'
	   + _("TIP_home_no_ue") + '</td></tr>');

  s = ue_line_join(s) ;
  if ( document.getElementById('ue_list_search') )
    document.getElementById('ue_list_search').innerHTML = '<table class="with_margin uelist searchresult"><colgroup><col class="code"><col class="title"><col class="responsable"></colgroup>' + s + '</table>' ;
}

function update_ues2(txt)
{
  try { if ( all_ues['!exists'] ) return ; } // Never return here
  catch(e) { return ; } // If all_ues is not defined: do nothing.

  if ( all_ues_sorted === undefined )
    {
      // Initialize sorted UES
      var t = [] ;
      ues_spiral = [] ;
      for(var ue in all_ues)
	{
	  if ( myindex(all_ues[ue].login, username) != -1 )
	      {
		if ( ue.match(/-/) ) // ue.substr(0, 6) == 'etape-' )
		  ues_spiral.push(ue) ;
		else
		  ues_spiral.push('UE-' + ue) ;
	      }
	  t.push( [all_ues[ue].code, all_ues[ue].name] ) ;
	}
      t.sort() ;
      all_ues_sorted = [] ;
      for(var ue in t)
	all_ues_sorted.push( t[ue][1] ) ;
    }

  resetScroll(document.getElementById('scrollable_left')) ;

  ue_line_out() ;

  if ( txt === '' )
    txt = 'UNFOUNDABLETEXT\001' ;
  var txt_upper = replaceDiacritics(txt).toUpperCase() ;

  update_ues_searched(txt, txt_upper) ;
  update_ues_favorites(txt, txt_upper) ;
  update_ues_spiral(txt, txt_upper) ;
  update_ues_master_of(txt, txt_upper) ;
  update_ues_unsaved() ;

  try
  {
    if ( window.localStorage )
      window.addEventListener('storage', storageEventHandler, false);
  }
  catch(e)
  {
  }
}

function storageEventHandler(e)
{
  ue_line_close() ;
  update_ues_unsaved() ;
}

function update_ues_unsaved()
{
  try {
    if ( window.localStorage === undefined )
      return ;
    }
  catch(e)
    {
      return ;
    }
  var index = localStorage['index'] ;
  if ( ! index )
    {
      document.getElementById('ue_list_unsaved').innerHTML = '' ;
      return ;
    }
  var s = ['<tr><th colspan="3">' +
	   hidden_txt(_("TH_home_unsaved_tables"),_("TIP_home_unsaved_tables"))
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
  document.getElementById('ue_list_unsaved').innerHTML = '<table class="with_margin uelist"><colgroup><col class="code"><col class="title"><col class="responsable"></colgroup>' + s + '</table>' ;
}


var update_referent_of_done ;

function cmp_students(a,b)
{
  a = a[2]+' '+a[1] ;
  b = b[2]+' '+b[1] ;
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
  var classes = i[6] ;
  if ( i[4] )
    classes += ' first_registration' ;
    
  return '<tr onmouseover="ue_line_over(\'' + i[0] + '\',this,student_click_more);" '
    + 'onclick="javascript:go_suivi_student(\'' + i[0]
    + '\')"><td>' + hide_icon
    + '<td class="student_id">' + i[0] + '<td class="'
    + classes + '">'
    + (i[5]
       ? '<img class="tt" src="' + url + '/tt.png">'
       : '')
    + i[2] + ' ' + title_case(i[1])
    + '</tr>' ;
}

function update_favorite_student()
{
  update_a_student_list('the_favorite_students', favstu,
			_("TH_home_bookmark_student"),
			'javascript:go_favoris()') ;
}

function update_referent_of()
{
  if ( update_referent_of_done )
    return ;
  update_referent_of_done = true ;
  update_a_student_list('the_students', referent_of,
			_("TH_home_refered_student"),
			'javascript:go_referent()') ;
}

function go_import_list()
{
  create_popup('import_list',
	       _("TH_home_import_refered"), _("MSG_home_import_refered"),
	       _("MSG_home_import_refered_after")
	       + '<BUTTON OnClick="go_import_list_do();">'
	       + _("B_home_import_refered")
	       + '</BUTTON>.',
	       '') ;
}

function go_import_list_do()
{
  var values = popup_text_area().value.split(/[ \t\n,;.:]+/) ;

  create_popup('import_list',
	       _("TH_home_import_refered"),
	       '<iframe width="100%" src="' + base + 'referent_get/'
	       + values.join('/') + '">' + '</iframe>',
	       _("MSG_home_reload"),
	       false) ;
}

function send_mails(e)
{
  my_mailto(document.getElementById(e).mails, true) ;
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

  the_students.mails = m.join(',') ;

  var blocnote = hidden_txt('<a href="' + notes + '">'
			    + _("TH_home_notepad") + '</a>',
			    _("TIP_home_notepad")) ;

  var mails = hidden_txt('<a href="javascript:send_mails(' + js2(html_id)
			 + ')">'
			 + _("TH_home_mail") + '</a>',
			 _("TIP_home_mail")) ;

  var suivis = hidden_txt('<a href="javascript:go_suivi_student(\''
			  + logins.join(',') + '\')">'
			  + _("TH_home_suivi") + '</a>',
			  _("TIP_home_suivi")) ;


  var import_list = '';
  if ( html_id === 'the_students')
    import_list = hidden_txt('<a href="javascript:go_import_list(\''
			     + logins.join(',') + '\')">'
			     + _("TH_home_import") + '</a>',
			     _("TIP_home_import")) ;

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

function login_list_to_html(results)
{
  var s = [] ;
  for(var infos in results)
    s.push(student_line(results[infos], results.length > 20)) ;
  if ( results.length === 0 )
      s = ['<tr><td colspan="3" style="color:black">' + _("MSG_home_nothing")
	   + '</tr>'] ;
  if ( s.length >= 99 )
      s.push('<tr><td colspan="3" style="color:black">' + _("MSG_home_clipped")
	     + '</tr>') ;

  return s.join('\n') ;
}

// This function may be called by 'login_list' plugin.
function full_login_list(login, results, add)
{
  if ( ! document.getElementById('students_list') )
    {
      // We are in a table, not the home page
      login_list(login, results) ;
      return ;
    }
  if ( last_login_cache[login] === undefined )
      last_login_cache[login] = {'student':[],'teacher':[]} ;
   
  results.sort(cmp_students) ;
  last_login_cache[login][add] = results ;

  if ( login != the_last_login_asked )
    return ;

  if ( add == 'student' )
      the_last_login_list = results ;

  
  document.getElementById('students_list').innerHTML =
	'<b>' + _("MSG_home_students") + '</b>'
	+ '<table class="student_list" style="margin-top:0">'
	+ '<colgroup><col class="student_icon"><col class="student_id">'
	+ '<col></colgroup>'
	+ login_list_to_html(last_login_cache[login]['student']) + '</table>'
	+ '<b>' + _("MSG_home_staff") + '</b>'
	+ '<table class="student_list" style="margin-top:0">'
	+ '<colgroup><col class="student_icon"><col class="student_id">'
	+ '<col></colgroup>'
	+ login_list_to_html(last_login_cache[login]['teacher']) + '</table>'
}

var update_students_timeout ;

function update_students()
{
  var input = document.getElementById('search_name') ;
  var what = replaceDiacritics(input.value) ;
  what = what.replace(/ *$/,'') ;
  // Normalise to logins
  what = what.split(/  +/) ;
  for(var i in what)
      what[i] = the_login(what[i]) ;
  what = what.join(' ') ;

  if ( what == input.old_value )
    return ;

  input.old_value = what ;
  resetScroll(document.getElementById("scrollable_center")) ;
  
  ue_line_out() ;

  the_last_login_asked = what ;
  if ( what === '' )
    {
      document.getElementById('students_list').innerHTML = '' ;
      return ;
    }
  if ( last_login_cache[what] )
    {
      full_login_list(what, last_login_cache[what]['teacher'], 'teacher') ;
      full_login_list(what, last_login_cache[what]['student'], 'student') ;
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
  document.getElementById('students_list').innerHTML = _("MSG_home_searching");
  update_students_timeout = undefined ;
}

function year_semester()
{
  var s = document.getElementById("s") ;
  return s.childNodes[s.selectedIndex].innerHTML ;
}

function is_the_current_semester()
{
  var s = document.getElementById("s") ;
  return s.selectedIndex == s.childNodes.length - 1 ;
}

function is_the_last_semester()
{
  var s = document.getElementById("s") ;
  return s.selectedIndex == s.childNodes.length - 2 ;
}

function current_year_semester()
{
  var s = document.getElementById("s") ;
  return s.childNodes[s.childNodes.length - 1].innerHTML ; 
}

function first_university_year_semester()
{
  var ys = current_year_semester().split('/') ;
  var the_year = ys[0] ;
  var the_semester = ys[1] ;
  // Search first semester
  while ( semesters_year[myindex(semesters, the_semester)] != 0 )
    {
      ys = previous_year_semester(the_year, the_semester) ;
      the_year = ys[0] ;
      the_semester = ys[1] ;
    }
  return [the_year, the_semester] ;
}

var goto_url_last_url ;
var goto_url_last_time ;

function goto_url(url)
{
  if ( url === goto_url_last_url && (millisec() - goto_url_last_time) < 1000 )
    {
      Alert("ALERT_no_double_clic") ;
      return ;
    }
  goto_url_last_url = url ;
  goto_url_last_time = millisec() ;
    
  window.open(url) ;
  // window.location = url ;
}

function go(x)
{
  goto_url(base + year_semester() + "/" + x) ;
}

function the_year()
{
  return Number(year_semester().split('/')[0]) ;
}

function do_action(action, html_class, help)
{
  if ( html_class == 'veryunsafe' )
    if (! confirm(help + '\n\n' + _("ALERT_are_you_sure2")) )
      return ;
  if ( action.substr(0,1) == '/' )
    goto_url(url + action) ;
  else
    goto_url(base + action) ;
}

function university_year()
{
  var ys = year_semester().split('/') ;
  var i = myindex(semesters, ys[1]) ;
  if ( i == -1 )
    return Number(ys[0]) ;
  return Number(ys[0]) + semesters_year[i] ;
}

function semester()
{
  return year_semester().split('/')[1] ;
}

function go_referent()
{
  var ys = first_university_year_semester() ;
  var s = base + university_year() + "/Referents/" + username2 ;
  if ( semester() != ys[1] )
      s += '/=column_offset=5' ;
  goto_url(s) ;
}

function go_favoris()
{
  var s = base + university_year() + "/Favoris/" + username2 ;
  goto_url(s) ;
}

function go_year(x)
{
  goto_url(base + university_year() + "/" + x) ;
}

function go_year_after(x)
{
  goto_url(base + x + '/' + the_year()) ;
}

function go_suivi(x)
{
  var s = suivi[year_semester()] ;
  if ( s === undefined )
    s = suivi[current_year_semester()] ;
  goto_url(s + "/" + x) ;
}

function go_suivi_student(x)
{
  var s = suivi[year_semester()] ;
  
  if ( s && test_bool(preferences.current_suivi) == no )
    goto_url(s + "/" + x) ;
  else
    goto_url(suivi[current_year_semester()] + "/" + x) ;
}

function change_icones()
{
  document.getElementsByTagName('BODY')[0].className = semester() ;

  var icones = document.getElementsByTagName("IMG") ;
  var i_base = suivi[year_semester()] ;
  if ( i_base === undefined )
    return ;

  for(var img in icones)
  {
    img = icones[img] ;
    if ( img.className == 'icone' || img.className == 'bigicone' )
      img.src = i_base + '/' + img.src.replace(RegExp('.*/'), '') ;
  }
}

function favoris_sort_change(t)
{
  preference_change(t, "favoris_sort="+(preferences.favoris_sort==yes ? 1 : 0));
  generate_home_page_ue_change_real(true) ;
}

function current_suivi_change(t)
{
  preference_change(t,"current_suivi="+(preferences.current_suivi==yes ?1:0));
}

function home_3scrollbar_change(t)
{
  home_resize_event(true) ;
  preference_change(t,"home_3scrollbar="
		    + (preferences.home_3scrollbar == yes ? 1 : 0));
}

function nr_favorites_change(t, event)
{
  event = the_event(event) ;
  if ( event.keyCode != 13 )
    return ;
  preferences.nr_favorites = t.value ;
  preference_change(t.parentNode, "nr_favorites=" + preferences.nr_favorites);
  generate_home_page_ue_change_real(true) ;
}

function home_preferences_popup()
{
  if ( popup_is_open() )
    {
      popup_close() ;
      return ;
    }
  create_popup('top_right', _("LABEL_preferences"),
	        _('MSG_home_preferences')
	       + '<p>'
	       + show_preferences_language()
	       + '<p>'
	       + radio_buttons('preferences.favoris_sort', [no, yes],
	                       test_bool(preferences.favoris_sort),
                               "favoris_sort_change(this)")
	       + _("Preferences_favoris_sort")
	       + '<p>'
	       + '<span><input value="' + preferences.nr_favorites
	       + '" style="width:1.5em;background:#080;color:#FFF"'
	       + ' onkeypress="nr_favorites_change(this, event)"></span> '
	       + _("Preferences_nr_favorites")
	       + '<br>' + _("MSG_enter")
	       + '<p>'
	       + radio_buttons('preferences.current_suivi', [no, yes],
	                       test_bool(preferences.current_suivi),
                               "current_suivi_change(this)")
	       + _("Preferences_current_suivi")
	       + '<p>'
	       + radio_buttons('preferences.home_3scrollbar', [no, yes],
	                       test_bool(preferences.home_3scrollbar),
                               "home_3scrollbar_change(this)")
	       + _("Preferences_home_3scrollbar")
	       ,'', false) ;
}

function home_help_popup()
{
  if ( popup_is_open() )
    {
      popup_close() ;
      return ;
    }
  create_popup('top_right', 'TOMUSS <span class="copyright">'
	       + tomuss_version + '</span>',
	       _("MSG_home_welcome")
	       + '<p>'
	       + '<a href="_FILES_/doc_table.html" target="_blank">'
	       + _("LABEL_documentation") + '</a>'
	       + '<p>'
	       + '<a href="mailto:' + admin + '">'
	       + _("MSG_suivi_student_mail_link") + '</a>'
	       ,'', false) ;
}

function generate_home_page_top()
{
    var t = '<TITLE>' + _("MSG_home_title") + '</TITLE>'
    + '<BODY'
    + ' onkeypress="if (the_event(event).keyCode==27) ue_line_close();">'
    + '<table class="identity">'
    + '<tr><td>'
    + '<a href="' + url + '/=' + ticket + '/logout">'
    + _("LABEL_logout") + '</a><br><b>' + username + '</b>'
    + '<td class="icons">&nbsp;'
    + '<a target="_blank" href="' + url
    + '/news.xml"><img style="border:0px;" src="'
    + '_FILES_/feed.png"></a>&nbsp;'
    + '<a href="javascript:home_help_popup()">' + _("TAB_?")+'</a>&nbsp;'
    + '<a href="javascript:home_preferences_popup()">⚙</a>&nbsp;'
    + '</tr></table>'
    + '</div>'
    + information_message
    + bad_password_message
  // Do not insert spaces in the next line
    + '<H1 style="margin-top: 0;">TOMUSS <select id="s" onchange="change_icones()" style="font-size:70%; vertical-align:top">'
    + semester_list + '</select></H1>' ;
  document.write(t) ;
}

function generate_home_page_ue_change_real(force)
{
  var input = document.getElementById('ue_input_name') ;
  if ( force || input.value != input.old_value )
  {
    update_ues2(input.value) ;
    input.old_value = input.value ;
  }
}

function generate_home_page_ue_change()
{
  setTimeout(generate_home_page_ue_change_real, 100) ;
}

function generate_home_page_ue()
{
    var t = '<h2>' + _("TH_home_ue") + '</h2>'
	+ '<table class="uelist searchresult">'
	+ '<tr><th colspan="3">'
	+ hidden_txt(_("TH_home_search"), _("TIP_home_search_ue"))
	+ '</th></tr>'
	+ '<tr class="search"><td colspan="3">'
	+ hidden_txt('<input style="border: 1px outset grey;" '
		     + 'type="button" value="'
		     + encode_value(_("TH_home_do_search"))
		     + '" onclick="generate_home_page_ue_change()">',
		     _("TIP_home_do_search"))
	+ '<input class="search_field" id="ue_input_name" class="keyword" onkeyup="generate_home_page_ue_change()" onpaste="generate_home_page_ue_change()" value="">'
	+ '</td>'
	+ '</tr>'
	+ '</table><div class="scrollable" id="scrollable_left">'
	+ '<div id="ue_list" class="ue_list">'
	+ '<div id="ue_list_search">' + _("TIP_home_ue_loading") + '</div>'
	+ '<div id="ue_list_unsaved"></div>'
	+ '<div id="ue_list_favorites"></div>'
	+ '<div id="ue_list_spiral"></div>'
	+ '<div id="ue_list_masters"></div>'
	+ '</div><br><br><br><br><br><br><br><br><br><br><br><br><br></div>' ;
    document.write(t) ;
}

function generate_home_page_students_change()
{
  setTimeout(update_students, 100) ;
}

function generate_home_page_students()
{
    var t = '<h2>' + _("TH_home_students") + '</h2>'
	+ '<table class="uelist searchresult">'
	+ '<tr><th class="student_id">'
	+ hidden_txt(_("TH_home_search"), _("TIP_home_search_student"))
	+ '</th></tr>'
	+ '<tr class="search"><td>'
	+ hidden_txt('<input style="border: 1px outset grey;" '
		     + 'type="button" value="' + encode_value(_("TH_home_do_search"))
		     + '" onclick="update_students()">',
		     _("TIP_home_do_search"))
	+ '<input class="search_field" id="search_name" class="keyword" onkeyup="update_students()" onpaste="generate_home_page_students_change()" value="">'
	+ '</td></tr></table><div class="scrollable" id="scrollable_center">'
	+ '<div id="students_list"></div>'
	+ '<div id="the_favorite_students"></div>'
	+ '<div id="the_students"></div><br><br><br><br><br><br><br><br><br><br><br><br><br><br></div>' ;
    document.write(t) ;
}

function collapse(event)
{
  var e = the_event(event).target ;
  while( e.tagName != 'TABLE' )
    e = e.parentNode ;
  if ( e.className.toString().match(' collapsed') )
    e.className = e.className.toString().replace(' collapsed', "")
  else
    e.className += ' collapsed' ;
  ue_line_out() ;
}

function generate_home_page_actions()
{
    var t = '<h2>' + _('TH_home_right') + '</h2><div id="scrollable_right" class="scrollable">' ;
    var boxes = {}, link_name, link_help ;
    var nb_actions = 0 ;
    for(var i in links)
    {
        if ( links[i][7] === '' )
	  links[i][7] = links[i][4] ; // Translation ID is the URL
 	if ( links[i][3] === '' )
	    links[i][3] = _('LINK_' + links[i][7]) ;
	if ( links[i][6] === '' )
	{
	    links[i][6] = _('HELP_' + links[i][7]) ;
	    if ( links[i][6] == 'HELP_' + links[i][7] )
		links[i][6] = '' ;
	}
        if ( links[i][4].substr(0,1) == '/' )
	  links[i][4] = "javascript:do_action('" + links[i][4].substr(1)
        + "','" + links[i][2] + "'," + js2(links[i][6]) +  ")" ;
	link_name = links[i][0] ;
        nb_actions++ ;
	if ( boxes[link_name] )
	    boxes[link_name].push(links[i]) ;
        else
	    boxes[link_name] = [ links[i] ] ;
    }
    var sorted_boxes = [] ;
    for(var box_name in boxes)
    {
	var box_title = _('BOX_' + box_name) ;
	if ( box_title === 'BOX_' + box_name )
	    box_title = box_name ;
	sorted_boxes.push([box_title, box_name]) ;
    }
    sorted_boxes.sort() ;
    var collapse = nb_actions > 50 ? ' collapsed' : '' ;
    for(var box_name in sorted_boxes)
    {
	box_name = sorted_boxes[box_name] ;
	box = boxes[box_name[1]] ;
	box.sort(
	    function(x,y)
	    {
		if ( x[1] != y[1] )
		    return x[1] - y[1] ;
		if ( x[3] < y[3] )
		    return -1 ;
		else
		    return 1 ;
	    }) ;
	t += '<table class="uelist' + collapse
	+ '"><tr><th onclick="collapse(event)">' + box_name[0]
	    +'</th></tr>\n' ;
	for(var link in box)
	{
	  link = box[link] ;
	  var el, eld, help ;
	  if ( link[4] === '' || link[3].toUpperCase().indexOf('INPUT') != -1 )
	  {
	    el = '' ;
	    eld = '' ;
	  }
	  else
	  {
	    el = '<a class="' + link[2] + '" href="' + link[4]
	      + '" target="' + link[5] + '" style="width:100%;display:block">';
	    eld = '</a>' ;
	  }
	  help = link[6] ;
	  if ( i_am_root )
	    help += '<br>PLUGIN:' + link[7] + '<br>FILE:' + link[8] ;
	  help += '<br>PRIORITY:' + link[1] ;
	  t += '<tr class="action" onmouseover="ue_line_over(\'\',this)"><td>'
	    + el
            + '<img class="safety" src="_FILES_/' + link[2] + '.png">'
	    + link[3] + '<var class="help">' + help
	    + '</var>' + eld + '</td></tr>' ;
	}
      t += '</table>' ;
    }
    t += '<br><br><br><br><br><br><br><br><br><br><br><br><br><br></div>' ;
    document.write(t) ;
}

var home_page_height ;

function home_resize_event(force)
{
  var height = window_height() ;

  if ( force || home_page_height != height )
  {
    home_page_height = height ;
    var cols = ["scrollable_right", "scrollable_left", "scrollable_center"] ;
    if ( test_bool(preferences.home_3scrollbar) == yes )
    {
      for(var e in cols)
	{
	  e = document.getElementById(cols[e]) ;
	  e.style.height = height - findPosY(e) - e.scrollTop - 8 + 'px' ;
	  e.onscroll = ue_line_out ;
	}
    }
  else
    {
      for(var e in cols)
	{
	  e = document.getElementById(cols[e]) ;
	  e.style.height = 'auto' ;
	}      
    }
    ue_line_out() ;
  }
  return true ;
}

/*REDEFINE
  Change whatever you want on the home page.
  It is called when 'all_ues' load is done.
*/
function generate_home_page_hook_with_ues()
{
}

/*REDEFINE
  Change whatever you want on the home page.
  It is called as soon as possible.
  The 'all_ues' variable is not usable.
*/
function generate_home_page_hook_without_ues()
{
}

var generate_home_page_hook_not_called = true ;
function generate_home_page_hook()
{
  if ( generate_home_page_hook_not_called )
  {
    generate_home_page_hook_without_ues() ;
    generate_home_page_hook_not_called = false ;
  }
      
  try {
    all_ues[''] ;
    generate_home_page_hook_with_ues() ;
  } catch(e) { // Wait all_ues.js loading
    setTimeout(generate_home_page_hook, 1000) ;
  }
}

function generate_home_page()
{
    lib_init() ;
    // To take a new ticket after 4 hours
    setTimeout("window.location.reload()", 1000*3600*4) ;
    generate_home_page_top() ;
    document.write('<TABLE id="top2" class="top2"><TR><TD class="top2" width="40%">') ;
    generate_home_page_ue() ;
    document.write('</TD><TD class="top2" width="20%">') ;
    generate_home_page_students() ;
    document.write('</TD><TD class="top2" id="rightpart" width="20%">') ;
    generate_home_page_actions() ;
    document.write('</TD></TR></TABLE>') ;
    // update_ues2('') ;
    update_referent_of() ;
    update_favorite_student() ;
    document.getElementById('ue_input_name').focus() ;
    document.getElementById('ue_input_name').select() ;
    change_icones() ;
    generate_home_page_hook() ;

    document.write('<div id="feedback"></div>') ;
    periodic_work_add(home_resize_event) ;
}
