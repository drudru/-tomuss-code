// -*- coding: utf-8; mode: Java; c-basic-offset: 2; tab-width: 8; -*-
/*
  TOMUSS: The Online Multi User Simple Spreadsheet
  Copyright (C) 2015 Thierry EXCOFFIER, Universite Claude Bernard

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

  Contact: Thierry.EXCOFFIER@univ-lyon1.fr
*/
/*
  Modify:

  student_line_more_links
  ue_line_more_links
  generate_home_page_hook_with_ues
  generate_home_page_hook_without_ues

 */

function hide_rightclip()
{
}

function parse_options(value)
{
  var parsed = {} ;
  if ( value )
    {
      var options = value.split(",") ;
      for(var i in options)
	{
	  var option = options[i].split(":") ;
	  parsed[option[0]] = option[1] ;
	}
    }
  return parsed ;
}

function get_hash()
{
  var h = location.href.split("#")[1] || "" ;
  try { h = decodeURIComponent(h) ; }
  catch(e) {}
  return parse_options(h) ;
}

function get_option(name, default_value)
{
  try {
  return get_hash()[name]
    || (localStorage && parse_options(localStorage['homepage'])[name])
    || default_value ;
  } catch(e) { return get_hash()[name] || default_value ; } ;
}

function options_string(options)
{
  var t = [] ;
  for(var i in options)
    t.push(i + ":" + options[i]) ;
  return t.join(',') ;
}

function set_option(name, value, only_session)
{
  var h = get_hash() ;
  h[name] = value ;
  window.location.hash = encodeURIComponent(options_string(h)) ;

  if ( localStorage && !only_session )
    {
      try {
	var h = parse_options(localStorage['homepage']) ;
	h[name] = value ;
	localStorage['homepage'] = options_string(h) ;
      }
      catch(e) { alert('LocalStorage NOT WORKING: ASK HELP TO FIX YOUR BROWSER\n\n'
		       + navigator.userAgent + ':\n\n' + e) ; }
    }
}


function DisplayHomeTitle(node)
{
  return 'TOMUSS' ;
}
DisplayHomeTitle.need_node = [] ;

var suivi = {} ;
function DisplayHomeSemesters(node)
{
  var s = ['<select id="s" onchange="set_option(\'year_semester\', this.value, true);display_update_real()">'] ;
  var current = get_option("year_semester", '') ;
  if ( current === '' )
    {
      current = node.data[node.data.length - 1] ;
      if ( current )
	current = current[2] + '/' + current[3] ;
      else
	current = year_semester ; // No suivi server
    }
  s.push('<option>2008/Test</option>') ;
  for(var i in node.data)
    {
      var year_semester = node.data[i][2] +'/'+ node.data[i][3] ;
      s.push("<option"
	     + (year_semester == current ? ' selected' :  '')
	     + ">" + year_semester + '</option>');
      suivi[year_semester] = node.data[i][0] ;
    }
  s.push('</select>') ;
  return s.join('') ;
}

// XXX copy/paste of suivi_student.js
function DisplayHomeProfiling(node)
{
  if ( ! display_data['HomePreferences']['debug_home'] )
    return '' ;
  var t = [] ;
  node.data = display_data['Profiling'] ;
  for(var i in node.data)
    t.push([node.data[i], i]) ;
  t.sort(function(a,b) { return b[0] - a[0] ; }) ;
  return fast_tip(_('LINK_profiling'), t.join('<br>')) ;
}
DisplayHomeProfiling.need_node = ['HomePreferences'] ;


function year_semester()
{
  var s = document.getElementById("s") ;
  if ( s )
    return s.value ;
  // The semester menu list is not yet on screen: take the last one
  var hs = display_data['HomeSemesters'] ;
  hs = hs[hs.length - 1] ;
  return hs[2] + '/' + hs[3] ;
}

function current_year_semester()
{
  var s = display_data["HomeSemesters"] ;
  s = s[s.length - 1] ;
  return s[2] + '/' + s[3] ;
}

function first_university_year_semester()
{
  var ys = year_semester().split('/') ;
  var the_year = ys[0] ;
  var the_semester = ys[1] ;
  // Search first semester
  while ( semesters_year[myindex(semesters, the_semester)] != 0 )
    {
      ys = previous_year_semester(the_year, the_semester) ;
      if ( the_year < 2000 )
	return ['?', '?'] ;
      the_year = ys[0] ;
      the_semester = ys[1] ;
    }
  return [the_year, the_semester] ;
}

function url_ue_last(code)
{
  if ( code.indexOf('/') == -1 )
    {
      try
	{
	  if ( all_ues[code].login === undefined || code.indexOf("-") != -1 )
	    code = year_semester() + '/' + code ;
	  else
	    code = year_semester() +'/UE-' + code ;
	}
      catch(e)
	{
	  code = year_semester() + '/' + code ;
	}
    }
  else
    code = code_clean_up(code) ;
  return code ;
}

function base(path)
{
  return url + '/=' + ticket + '/' + path ;
}

function url_ue(code)
{
  return base(url_ue_last(code)) ;
}

function goto_url(path)
{
  if ( path === goto_url.last_url && (millisec() - goto_url.last_time) < 1000 )
    {
      Alert("ALERT_no_double_clic") ;
      return ;
    }
  goto_url.last_url = path ;
  goto_url.last_time = millisec() ;
    
  window.open(path) ;
}

function go(x)
{
  goto_url(base(year_semester() + "/" + x)) ;
}

function suivi_url(x)
{
  var s = suivi[test_bool(preferences.current_suivi) == yes
		? current_year_semester()
		: year_semester()
		] ;
  if ( s === undefined )
    s = suivi[current_year_semester()] ;
  return s + "/=" + ticket + '/' + x ;
}

function go_suivi(x)
{
  window.open(suivi_url(x)) ;
}

function open_ue(t, code)
{
  while( ! t.className.match(/\bue_line\b/) )
    t = t.parentNode ;
  if ( t.childNodes[t.childNodes.length-1].className.match('HomeUEMenu') )
    {
      t.onmouseleave() ;
      return ;
    }
  t.className += " ue_line_hover" ;
  var m = document.createElement("DIV") ;
  open_ue.code = code ;
  m.innerHTML = display_display(display_definition["HomeUEMenu"]) ;
  m = m.firstChild ;
  t.onmouseleave = function() {
    try { t.removeChild(m) ; t.className = t.className.replace(" ue_line_hover", "") ; } catch(e) {} ; t.onmouseleave = "" ; } ;
  t.appendChild(m) ;
}

function box_button(txt, url)
{
  return ['<div>' + txt.replace(/([-.@])/g, "$1 ") + '</div>', [], [],
	  'onclick="goto_url(\'' + url + '\')"'] ;
}

function DisplayHomeUEOpen(node)
{
  return box_button(_("B_home_edit"),
		    url_ue(open_ue.code)) ;
}
DisplayHomeUEOpen.need_node = [] ;
function DisplayHomeUEOpenRO(node)
{
  return box_button(_("B_home_display"),
		    url_ue(open_ue.code) + '/=read-only=') ;
}
DisplayHomeUEOpenRO.need_node = [] ;
function DisplayHomeUESignature(node)
{
  return box_button(_("B_home_signature"),
		    url_ue(open_ue.code) + '/=signatures-page=/=read-only=') ;
}
DisplayHomeUESignature.need_node = [] ;
function DisplayHomeUEPrint(node)
{
  return box_button(_("B_home_export_print"),
		    url_ue(open_ue.code) + '/=print-table=/=read-only=') ;
}
DisplayHomeUEPrint.need_node = [] ;

function do_extension(code)
{
  code = first_university_year_semester().join('/') + '/' + code ;
  if ( confirm(_("ALERT_home_extend_before") + url_ue_last(code) + "\n" +
	       _("ALERT_home_extend_after") + "\n\n" +
	       _("ALERT_are_you_sure") ) )
    {
      create_popup('import_popup',
		   _("ALERT_home_extend_before") + code,
		   '<iframe width="100%" src="'
		   + base(code) + '/extension"></iframe>',
		   '', false) ;
    }
}
function DisplayHomeUEUnsemestrialize(node)
{
  if ( open_ue.code && ! open_ue.code.match('.*/.*') )
    {
      if ( first_university_year_semester()[0] == '?' )
	return '' ;
      return '<div onclick="do_extension(\'' + open_ue.code
	+ '\')">' + _("B_home_unsemestrialize") + '</div>' ;
    }
  return '' ;
}
DisplayHomeUEUnsemestrialize.need_node = [] ;


function do_presence(t)
{
  var filters = '' ;
  try {
    var grp_seq = selected_grp_seq.split("<")[0].split("/") ;
    if ( grp_seq[1] !== undefined )
      filters = '/=filters=' + '0_3:' + grp_seq[1] + '=0_4:' + grp_seq[0] ;
  }
  catch(e) {} ;
  goto_url(url_ue(open_ue.code)
	   + filters
	   + '/=facebook=' + t.getAttribute('alt')
	   ) ;
}

var table_attr = {} ;
var selected_grp_seq ;
function the_columns(columns, grp_seq)
{
  var t = [] ;
  var options = [] ;
  var nb = 0 ;
  for(var i in grp_seq)
    {
      var option = i.split('/') ;
      options.push(i + '<br>' + grp_seq[i]) ;
      nb += grp_seq[i] ;
    }
  options.sort() ;
  options.push(_('MSG_home_~any~') + '<br>' + nb) ;
  selected_grp_seq = options[options.length-1] ;
  for(var i in columns)
    {
      if ( columns[i].type != "Prst" )
	continue ;
      var dates = columns[i].course_dates.split(/  */) ;
      var lines = ['<b>' + html(columns[i].title) + '</b>'] ;
      for(var j in dates)
	if ( dates[j] !== '' )
	  lines.push(get_date_tomuss_short(dates[j])) ;
      if ( columns[i].comment !== '' )
	lines.push(html(columns[i].comment)) ;
      t.push('<div class="Display" onclick="do_presence(this)"'
	     + ' alt=' + js2(columns[i].the_id)
	     + '><div>'
	     + lines.join("<br>")
	     + '</div></div>') ;
    }
  var e = document.getElementById("the_columns") ;
  if ( e )
    {
      if ( t.length )
	{
	  e.firstChild.innerHTML = _("MSG_home_presence") + '<br>'
	    + radio_buttons('selected_grp_seq', options,
			    options[options.length-1]) ;
	  e.childNodes[1].innerHTML = t.join(" ") ;
	}
      else
	e.firstChild.innerHTML = _("MSG_home_no_presence") ;
    }
  else console.log("==") ;
}

function DisplayHomeUEMenuColumns(node)
{
  var s = document.createElement("SCRIPT") ;
  s.src = url_ue(open_ue.code) + '/get_columns' ;
  the_body.appendChild(s) ;
  return '<div id="the_columns"><div>' + _("MSG_home_wait")
    + '</div><div></div></div>' ;
}
DisplayHomeUEMenuColumns.need_node = [] ;


function do_close_ue(code)
{
  create_popup('import_popup',
	       _("B_home_close_pages"),
	       '<iframe width="100%" src="'
	       + url_ue(code) + '/page_unload"></iframe>',
	       '', false) ;
}

function DisplayHomeUEClose(node)
{
  if ( i_am_root )
    return '<div onclick="do_close_ue(\'' + open_ue.code + '\')">'
    + _("B_home_close_pages") + '</div>' ;
  return '' ;
}
DisplayHomeUEClose.need_node = [] ;

function DisplayHomeLogout(node)
{
  return '<a href="'+ base('logout') + '">' + _("LABEL_logout") + '</a>';
}
DisplayHomeLogout.need_node = [] ;


function DisplayHomeLogin(node)
{
  return username ;
}
DisplayHomeLogin.need_node = [] ;


function DisplayHomeFeed(node)
{
  return '<a target="_blank" href="' + url
    + '/news.xml"><img style="border:0px;" src="_FILES_/feed.png"></a>' ;
}
DisplayHomeFeed.need_node = [] ;


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

function DisplayHomeHelp(node)
{
  return '<a href="javascript:home_help_popup()">' + _("TAB_?") + '</a>' ;
}
DisplayHomeHelp.need_node = [] ;

function language_change(t)
{
  function change_language()
  {
    languages = [preferences.language] ;
    display_update_real() ;
  }
  
  preference_change(t, "language=" + preferences.language) ;
  if ( translations[preferences.language] === undefined )
    {
      var t = document.createElement("SCRIPT") ;
      t.src = url_files + '/' + preferences.language + ".js"
      t.onload = change_language ;
      the_body.appendChild(t) ;
    }
  else
    change_language() ;
}
function DisplayHomePreferencesLanguages(node)
{
  return show_preferences_language() ;
}
DisplayHomePreferencesLanguages.need_node = [] ;

function change_text_size(t)
{
  set_option('text_size', preferences.text_size) ;
  the_body.style.fontSize = preferences.text_size ;
}

function DisplayHomePreferencesSize(node)
{
  return radio_buttons('preferences.text_size', ['70%', '100%', '150%', '200%'],
	               preferences.text_size,
                       "change_text_size(this)")
    + _("MSG_text_size") ;
 ;
}
DisplayHomePreferencesSize.need_node = [] ;

function current_suivi_change(t)
{
  preference_change(t,"current_suivi="+(preferences.current_suivi==yes ?1:0));
  display_update_real() ;
}
function DisplayHomePreferencesYearSemester(node)
{
  return radio_buttons('preferences.current_suivi', [no, yes],
	               test_bool(preferences.current_suivi),
                       "current_suivi_change(this)")
    + _("Preferences_current_suivi") ;
}
DisplayHomePreferencesYearSemester.need_node = [] ;

function home_3scrollbar_change(t)
{
  preference_change(t,"home_3scrollbar="
		    + (preferences.home_3scrollbar == yes ? 1 : 0));
  display_update_real() ;
}
function DisplayHomePreferences3ScrollBars(node)
{
  return '' ;
  /*
  return radio_buttons('preferences.home_3scrollbar', [no, yes],
	               test_bool(preferences.home_3scrollbar),
                       "home_3scrollbar_change(this)")
    + _("Preferences_home_3scrollbar") ;
  */
}
DisplayHomePreferences3ScrollBars.need_node = [] ;

function current_debug_change(t)
{
  preference_change(t,"debug_home="+(preferences.debug_home==yes ?1:0));
  preferences.debug_home = preferences.debug_home == yes ;
  display_update_real() ;
}
function DisplayHomePreferencesDebug(node)
{
  if ( ! i_am_root )
    return '' ;
  return radio_buttons('preferences.debug_home', [no, yes],
	               test_bool(preferences.debug_home),
                       "current_debug_change(this)")
    + _("Preference_debug_suivi") ;
}
DisplayHomePreferencesDebug.need_node = [] ;

function home_preferences_popup()
{
  var s = [_('MSG_home_preferences')] ;
  var children = display_definition['HomePreferences'].children ;
  for(var i in children)
    s.push(display_display(children[i])) ;

  create_popup('top_right', 'TOMUSS <span class="copyright">'
	       + tomuss_version + '</span>',
	       s.join(''),'', false) ;
}

var preferences ;

function DisplayHomePreferences(node)
{
  display_do_debug = node.data['debug_home'] ;
  preferences = node.data ;
  languages = [preferences.language] ;
  if ( ! preferences.text_size )
    preferences.text_size = get_option('text_size', '100%') ;
  the_body.style.fontSize = preferences.text_size ;
  return '<a href="javascript:home_preferences_popup()">≡</a>' ;
}

// The message may start with some 3 hexdigit colors:
//    #backgroundColor #ForegroundColor #BorderColor
// #F00 #FFF to have white on a red background
function DisplayHomeMessage(node)
{
  if ( node.data !== '' )
    {
      var d = node.data.match(RegExp("((#[0-9A-F]{3}  *)*)(.*)")) ;
      var cols = d[1] ? d[1].split(/  */) : [] ;
      return [d[3], [], ["background:" + (cols[0] || "#FFF"),
			 "color:" + (cols[1] || "#000"),
			 "border: 4px solid " + (cols[2] || "#000")
			 ], ''] ;
    }
  return '' ;
}

function em_size_in_pixel()
{
  var o = document.createElement('DIV') ;
  o.style.width = '1em' ;
  the_body.appendChild(o) ;
  var w = o.offsetWidth ;
  the_body.removeChild(o) ;
  return w ;
}

function DisplayHomeColumns(node)
{
  if ( ! DisplayHomeColumns.init_done )
    {
      DisplayHomeColumns.init_done = true ;
      the_body.onresize = function()
	{
	  if ( ! do_touchstart.touch ) // No resize on tablet and phone
	    display_update_real() ;
	} ;
      
      the_body.addEventListener("touchstart", do_touchstart, false) ;
    }

  display_do_debug = preferences.debug_home ;
  i_am_root = myindex(root, username) != -1 ; // XXX yet in lib.js
  var s = ['<style>',
	   '.HomeUE .ue_line_hover {width:', window_width()   - 40,'px ;}',
	   '.HomeStudents .ue_line_hover{width:',window_width()/2 - 20,'px ;}',
	   'DIV.tabs .ue_line_hover {width:',window_width()   - 30,'px ;}',
	   'DIV.tabs .ue_title, DIV.tabs .ue_more { width:',window_width() - 165,'px ;}',
	   '.ue_title, .ue_more {width:',  window_width() - 170, 'px;}',
	   '.HomeStudents .ue_title, .HomeStudents .ue_more {width:',
	   window_width()/2   - 120, 'px;}',
	   '</style>',
	   '<title>', _("MSG_home_title"), '</title>'
	  ] ;
  DisplayHomeColumns.large_screen = 50 * em_size_in_pixel() < window_width() ;
   if ( DisplayHomeColumns.large_screen )
    {
      s.push('<table><tbody><tr><td width="50%">' + _("TH_home_ue")
	     + '<td width="25%">' + _("TH_home_students")
	     + '<td width="25%">' + _('TH_home_right') + '</tr><tr>'
	    ) ;
      for(var i in node.children)
      {
	s.push("<td>") ;
	s.push(display_display(node.children[i])) ;
      }
      s.push("</tbody></table>") ;
    }
  else
    {
      s.push(create_tabs('home3', [
	[ _("TH_home_ue"), display_display(node.children[0])],
	[ _("TH_home_students"), display_display(node.children[1])],
	[ _("TH_home_right"), display_display(node.children[2])]
      ])) ;
      DisplayHomeColumns.tab = selected_tab('home3') || DisplayHomeColumns.tab;
      if ( ! DisplayHomeColumns.tab )
	DisplayHomeColumns.tab = _("TH_home_ue") ;
      setTimeout("select_tab('home3',"+js(DisplayHomeColumns.tab) + ")", 0) ;
    }
      return s.join('') ;
}
DisplayHomeColumns.need_node = [] ;

function _UE(name, responsable, intitule, parcours, code, login,
	     nr_students_ue, nr_students_ec, planning, tt, credit, old_names)
{
  this.name = name ;
  if ( parcours === undefined )
    {
      parcours = '' ;
      code = '' ;
      nr_students_ue = 1 ;
      nr_students_ec = 0 ;
    }
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
}

function UE(name, responsable, intitule, parcours, code, login,
	    nr_students_ue, nr_students_ec, planning, tt, credit, old_names)
{
  return new _UE(name, responsable, intitule, parcours,
		 code, login, nr_students_ue, nr_students_ec, planning, tt,
		 credit, old_names) ;
}

function get_info(code)
{
  var info ;
  try { info = all_ues[code] ; }
  catch(e) { }
  if ( ! info )
    info = all_ues[code.split('-')[1]] ;
  if ( ! info )
    info = {name: code} ;
  return info ;
}

function fast_tip(txt, help)
{
  return '<div class="fast_tip">' + txt + '<div>' + help + '</div></div>' ;
}

function code_clean_up(code)
{
  return code.replace(/<!--/g,"").replace(/-->/g,"").replace(/<.?small>/g,"");
}

function code_create(year_semester_ue)
{
  if ( ! year_semester_ue[3] )
    year_semester_ue.push(year_semester_ue.join('/')) ;
  return year_semester_ue[3] ;
}

function ue_set_favorite(event, code, nr)
{
  event = the_event(event) ;
  var t = event.target ;
  var img = document.createElement('IMG') ;
  var bookmarked = get_info(code).is_bookmarked ;
  var code_ue = code_clean_up(code) ;
  if ( bookmarked )
    code_ue = bookmarked ;
  else if ( code_ue.indexOf('/') == -1 )
    code_ue = year_semester() + '/' + code_ue ;
  img.src = base(code_ue + '/bookmark') ;
  t.appendChild(img) ;

  if ( bookmarked )
  {
    get_info(code).is_bookmarked = false ;
    for(var i in display_data['HomeUEBookmarked'])
      if ( display_data['HomeUEBookmarked'][i][3] == bookmarked )
	{
	  display_data['HomeUEBookmarked'].splice(i, 1) ;
	  break ;
	}
  }
  else
    {
      display_data['HomeUEBookmarked'].push(code_ue.split('/')) ;
    }
  create_ue_lists.done = false ;
  create_ue_lists() ;
  setTimeout(display_update_real, 1000) ;
  stop_event(event) ;
}

function student_set_favorite(event, code, favorite)
{
  favorite = ! favorite ;
  event = the_event(event) ;
  var t = event.target ;
  var img = document.createElement('IMG') ;
  img.src = base('favorite_student/') + code ;
  t.appendChild(img) ;
  if ( ! favorite )
    {
      for(var i in display_data['HomeStudentFavorites'])
	if ( display_data['HomeStudentFavorites'][i][0] == code )
      {
	display_data['HomeStudentFavorites'].splice(i, 1) ;
	break ;
      }
      is_a_favorite[code] = false ;
    }
  else
    {
      display_data['HomeStudentFavorites'].push(students_info[code]) ;
    }
  setTimeout(display_update_real, 1000) ;
  stop_event(event) ;
}

function action_set_favorite(event, code, favorite)
{
  is_a_favorite_action[code] = ! favorite ;
  try {
    localStorage["favorite_actions"] = JSON.stringify(is_a_favorite_action) ;
  } catch(e) { } ;
  display_update_real() ;
}

function get_ue_table(t)
{
  while( ! t.firstChild || ! t.firstChild.getAttribute
	 || ! t.firstChild.getAttribute("alt") )
    t = t.parentNode ;
  return t ;
}


function get_ue_table_title(t)
{
  return get_ue_table(t).firstChild.getAttribute("alt") ;
}

function select_ue_sort(t)
{
  set_option('S' + get_ue_table_title(t), t.value) ;
  display_update_real() ;
}

function select_code_filter(t)
{
  set_option('F' + get_ue_table_title(t), t.value, true) ;
  display_update_real() ;
}

function select_open_close(t, event)
{
  set_option('B' + get_ue_table_title(t), t.innerHTML == '⇧' ? '⇩' : '⇧') ;
  var title = t.parentNode.parentNode.parentNode ;
  title.className = title.className.replace(/ is_(open|close)/, '') ;
  if ( t.innerHTML == '⇧' )
    {
      title.className += " is_close" ;
      t.innerHTML = '⇩' ;
      t.nextSibling.innerHTML = _("TIP_open") ;
      t = get_ue_table(t) ;
      while( t.childNodes[1] )
	t.removeChild(t.childNodes[1]) ;
    }
  else
    {
      title.className += " is_close" ;
      if ( get_ue_table(t).parentNode.id )
	{
	  update_job.todo[get_ue_table(t).parentNode.id] = true ;
	  periodic_work_add(update_job) ;
	}
      else
	display_update_real() ;
    }
  stop_event(event) ;
}


var ue_sorters = {
  'A': function(a,b) { return a > b ? 1 : (a == b ? 0 : -1) ; },
  'α': function(a,b) {
    a = get_info(a).intitule || '' ;
    b = get_info(b).intitule || '' ;
    return a > b ? 1 : (a == b ? 0 : -1) ;
  },
  '☆': function(a,b) {
    a = get_info(a).nr_access || 0 ;
    b = get_info(b).nr_access || 0 ;
    return b - a ;
  },
  '★': function(a,b) {
    return !get_info(a).is_bookmarked - !get_info(b).is_bookmarked ;
  },
  '#': function(a,b) {
    a = get_info(a).nr_students_ue || 0 ;
    b = get_info(b).nr_students_ue || 0 ;
    return b - a ;
  },
  'surname+firstname': function(a,b) {
    a = a[2] + ' ' + a[1] ;
    b = b[2] + ' ' + b[1] ;
    return a > b ? 1 : (a == b ? 0 : -1) ;
  }
} ;

function display_ues(title, tip, codes, options)
{
  var order = get_option('S' + title, options.default_order) ;
  var opened = get_option('B' + title, '⇧') == '⇧' ;
  var s = ['<div class="ue_list">'] ;
  if ( options.hide_open_close )
    opened = true ;
  if ( ! options.hide_title )
    {
      s.push('<div class="table_title ' + (opened ? 'is_open' : 'is_close')
	     + '" alt=' + js2(title)
	     + (options.hide_sort
		&& ! options.code_filter
		&& ! options.hide_open_close
		? ' onclick="select_open_close(this.getElementsByTagName(\'SPAN\')[0],event)"'
		: ''
		)
	     + '>'
	     + (options.before_title || '')
	     + (tip ? hidden_txt(_(title), tip) : _(title))
	     ) ;
      if ( display_data['HomePreferences']['debug_home'] )
	s.push('<small>' + display_ues.nb++ + '</small>') ;
      if ( options.title_second_line )
	s.push("<br>" + options.title_second_line) ;
      if ( ! options.hide_open_close )
	s.push('<div class="open_close ue_icons">'
	       + fast_tip('<span onclick="select_open_close(this,event)">'
			  + (opened ? '⇧' : '⇩')
			  + '</span>',
			  opened ? _("TIP_close") : _("TIP_open")
			 )
	       + '</div>'
	      ) ;
      s.push('<div class="select_ue_sort">') ;
      var current ;
      if ( options.code_filter )
      {
	var t = [] ;
	for(var i in options.code_filter)
	  t.push(i) ;
	t.sort() ;
	current = get_option('F' + title, t[t.length - 1]) ;
	s.push('<select onchange="select_code_filter(this)">') ;
	for(var i in t)
	  s.push('<option' + (t[i] == current ? ' selected' : '')
		 + ' value="' + t[i] + '">'
		 + (_('MSG_home_' + t[i]) == 'MSG_home_' + t[i]
		    ? t[i] : _('MSG_home_' + t[i]))
		 + '</option>') ;
	s.push('</select>') ;
      }
      else if ( ! options.hide_sort )
      {
	s.push('<select onchange="select_ue_sort(this)">') ;
	for(var i in ue_sorters)
	  if ( i.length == 1 )
	    s.push('<option' + (i == order ? ' selected' : '')
		   + ' value="' + i + '">'
		   + _('sort_' + i) + '</option>') ;
	s.push("</select>") ;
      }
      s.push('</div></div>') ;
    }
  var favorite, new_nr ;
  if ( !opened )
    codes = [] ;
  if (! options.do_not_sort )
    codes.sort(ue_sorters[order]) ;
  var nr_displayed = 0, classes ;
  var display_student_icon = options.students && (options.code_filter
						  || codes.length < 40) ;
  var nr_max = get_option('C' + title, options.nr_max) ;
  for(var ue in codes)
  {
    if ( nr_displayed == nr_max )
      {
	s.push('<b onclick="set_option('
	       + js2('C' + title) + ',' +  nr_max*4
	       + ',true);display_update_real()">'
	       + _("MSG_see_following") + '</b>') ;
	break ;
      }
    ue = codes[ue] ;
    if ( options.students )
      {
	classes = ' ' + (ue[4] ? 'first_registration': '') + ' ' + ue[6]
	  + ' ' + (ue[5] ? 'tt' : '') + ' ' ;
	if ( current != '~any~' && classes.indexOf(' ' + current + ' ') == -1 )
	  continue
	if ( is_a_favorite[ue[0]] )
	  favorite = '★' ;
	else
	  favorite = '☆' ;
	favorite = '<tt onclick="student_set_favorite(event,'+ js2(ue[0]) + ','
	  + is_a_favorite[ue[0]] +')" class="icon">' + favorite + '</tt>' ;
      }
    else if ( options.actions )
      {
	if ( options.favorite_toggle )
	  {
	    if ( is_a_favorite_action[ue[3]] )
	      favorite = '★' ;
	    else
	      favorite = '☆' ;
	    favorite = '<tt onclick="action_set_favorite(event,'+ js2(ue[3])
	      + ',' + is_a_favorite_action[ue[3]] +')" class="icon">'
	      + favorite + '</tt>' ;
	  }
	else
	  favorite = '' ;
      }
    else
      {
	if ( current && code_clean_up(ue).substr(0, current.length) != current)
	  continue ;
	info = get_info(ue) ;
	if ( info.is_bookmarked )
	  favorite = '★' ;
	else
	  favorite = '☆' ;
	if ( info.is_master_of && favorite == '☆' )
	  favorite = '' ; // ♚
	else
	  favorite = '<tt onclick="ue_set_favorite(event,' + js2(ue)
	    + ')" class="icon">' + favorite + '</tt>' ;
      }
    if ( options.students )
      s.push(
	'<div class="ue_line ' + classes + '" onclick="open_student(this,'
	+ js2(ue[0]) + ')" ondblclick="go_suivi(' + js2(ue[0]) + ')">'
	+ '<div class="ue_right"><div class="ue_title">'
	+ string_highlight(html(ue[2] + ' ' + title_case(ue[1])),
			   ask_login_list)
	+ '</div>'
	+ '<div class="ue_more">'
	+ (students_info[ue[0]][7]
	   ? fast_tip(students_info[ue[0]][7],_("MSG_suivi_referent_is"))
	   : ' ')
	+ '</div>'
	+ '</div><div class="ue_code">'
	+ string_highlight(ue[0], ask_login_list)
	+ '</div><div class="ue_icons">'
	+ fast_tip(favorite,
		   is_a_favorite[ue[0]]
		   ? _("B_home_remove_bookmark")
		   : _("B_home_bookmark"))
	+ ' ' + ( display_student_icon && suivi[year_semester()]
		  ? fast_tip('<img src="' + suivi[year_semester()]
			     + '/=' + ticket
			     + '/_' + ue[0] + '">',
			     _("TIP_home_squares"))
		  : '')
	+ ' ' + (ue[5]
		 ? fast_tip('<tt class="icon">♿</tt>',
			    _("MSG_print_tt_title"))
		 : '')
	+ '</div></div>'
	     ) ;
    else if ( options.actions )
      {
	var el, eld, help, link = ue ;
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
	if ( display_do_debug )
	  {
	    help += '<br>PLUGIN:' + link[7]
	      + '<br>FILE:' + link[8]
	      + '<br>PRIORITY:' + link[1] ;
	  }
	s.push('<div class="ue_line">'
	       + el
	       + '<img class="safety" src="_FILES_/' + link[2] + '.png">'
	       + link[3] + eld + '<div class="ue_more">' + favorite + help
	       + '</div></div>'
	       ) ;
      }
    else
      {
	var code = ue ;
	if ( code.match('/') )
	  code = code.replace(RegExp("(/[^/]*)$"),
			      '<span class="path_code">$1</span>') ;
	s.push('<div class="ue_line" onclick="open_ue(this,' + js2(ue)
	       + ')" ondblclick="goto_url(' + js2(url_ue(ue)) + ')">'
	       + '<div class="ue_right"><div class="ue_title">'
	       + (info.nr_students_ue ? '<b>' : '')
	       + string_highlight(html(info.intitule || ''),
				  search_ue_list.txt)
	       + (info.credit > 0 ? ' <span class="ue_credits">'
		  + info.credit + ' ' + _("MSG_home_credit") + '</span>' : '')
	       + (info.nr_students_ue ? '</b>' : '')
	       + '</div><div class="ue_more">'
	       + string_highlight(html(info.responsable
				       ? info.responsable.join(', ')
				       : ''), search_ue_list.txt) + ' '
	       + (info.old_names
		  ? fast_tip(string_highlight(html(info.old_names.join(' ')),
					      search_ue_list.txt),
			     _("MSG_home_old_codes"))
		  : '')
	       + '</div></div><div class="ue_code">'
	       + string_highlight(code, search_ue_list.txt)
	       + '</div><div class="ue_icons">'
	       + fast_tip(favorite,
			  (info.is_bookmarked
			   ? _("B_home_remove_bookmark")
			   : _("B_home_bookmark"))
			  + (info.nr_access
			     ? '<br>' + _("MSG_home_nr_view_before")
			     + info.nr_access
			     + _("MSG_home_nr_view_after")
			     : '')
			  )
	       + ' ' + (info.tt
			? fast_tip('<tt class="icon">♿</tt>',
				   info.tt + ' ' + _("MSG_print_tt_title"))
			: '')
	       + ' ' + (info.nr_students_ue
			? ' ' + fast_tip(info.nr_students_ue,
					 info.nr_students_ue
					 + ' ' + _("TH_home_students")
					 )
			: '')
	       + '</div></div>'
	       ) ;
      }
    nr_displayed++ ;
  }
  s.push("</div>") ;
  return s.join('') ;
}
display_ues.nb = 0 ;

// Merge all information from Favorites, Bookmark and MasterOf
// into 'all_ues' and create the lists to display.
// create_ue_lists.all_ues[ue] contains the original UE list
function create_ue_lists()
{
  if ( create_ue_lists.done
       && create_ue_lists.favorite_list.length != 0 )
    return ;
  create_ue_lists.favorite_list = [] ;
  create_ue_lists.master_of_list = [] ;
  create_ue_lists.acceded_list = [] ;
  create_ue_lists.unsaved_list = [] ;
  create_ue_lists.max = 0 ;
  try { all_ues[0] ; }
  catch(e) {
    setTimeout(create_ue_lists, 100) ;
    return ;
  }
  if ( ! create_ue_lists.yet_done )
    {
      create_ue_lists.all_ues = {} ;
      for(var ue in all_ues)
	create_ue_lists.all_ues[ue] = all_ues[ue] ;
    }

  var ue_first = [] ;
  for(var code in display_data['HomeUENrAccess'])
    if ( code.substr(0,3) == 'UE-' )
      ue_first.push(code) ;
  for(var code in display_data['HomeUENrAccess'])
    if ( code.substr(0,3) != 'UE-' )
      ue_first.push(code) ;
  var is_bookmarked = {} ;
  for(var code in display_data['HomeUEBookmarked'])
    {
      code = display_data['HomeUEBookmarked'][code][2] ;
      is_bookmarked[code] = true ;
      // Allow to see never visited table in favorites:
      if ( ! display_data['HomeUENrAccess'][code]
	   && ! display_data['HomeUENrAccess'][code.replace(/^UE-/, "")]
	   && get_info(code).intitule
	   )
	create_ue_lists.favorite_list.push(code) ;
    }
	
  for(var code in ue_first)
  {
    code = ue_first[code] ;
    if ( code == 'undefined' )
      continue ;
    var nr = display_data['HomeUENrAccess'][code] ;
    create_ue_lists.acceded_list.push(code) ;
    if ( is_bookmarked[code]
	 && (create_ue_lists.all_ues[code]
	     || create_ue_lists.all_ues[code.replace(/^UE-/, "")]
	     ))
      create_ue_lists.favorite_list.push(code) ;
    create_ue_lists.max = Math.max(create_ue_lists.max, nr) ;

    if ( ! create_ue_lists.yet_done )
      {
	all_ues[code] = get_info(code) ;
	if ( all_ues[code].nr_access === undefined )
	  all_ues[code].nr_access = 0 ;
	all_ues[code].nr_access += nr ;
      }
  }
  create_ue_lists.max = Math.round(create_ue_lists.max) ;

  function add_to(year_semester_ue, list, force_add)
  {
    var code = code_create(year_semester_ue) ;
    if ( get_info(year_semester_ue[2]).nr_students_ue !== undefined )
      {
	if ( force_add )
	  list.push(code) ;
	return {} ;
      }
    var ue = all_ues[code] = get_info(code) ;
    ue.intitule = year_semester_ue[2] ;
    list.push(code) ;
    return ue ;
  }
  
  for(var i in display_data['HomeUEBookmarked'])
    {
      var year_semester_ue = display_data['HomeUEBookmarked'][i] ;
      add_to(year_semester_ue, create_ue_lists.master_of_list) ;
      get_info(year_semester_ue[3]).is_bookmarked = year_semester_ue[3] ;
    }

  for(var i in display_data['HomeUEMasterOf'])
    {
      var ue = add_to(display_data['HomeUEMasterOf'][i],
		      create_ue_lists.master_of_list) ;
      ue.is_master_of = true ;
      if ( ue.is_bookmarked )
	create_ue_lists.master_of_list.pop() ;
    }

  create_ue_lists.ues_teacher = [] ;
  for(var ue in create_ue_lists.all_ues)
  {
    if ( myindex(all_ues[ue].login, username) == -1 )
      continue ;
    if ( ue.match(/-/) ) // ue.substr(0, 6) == 'etape-' )
      create_ue_lists.ues_teacher.push(ue) ;
    else
      create_ue_lists.ues_teacher.push('UE-' + ue) ;
  }

  // List of unsaved tables
  try {
    var index = localStorage && localStorage['index'] ;
    if ( index && index !== '' )
      {
	index = index.substr(1).split('\n') ;
	for(var i in index)
	  {
	    add_to(index[i].substr(1).split('/'),
		   create_ue_lists.unsaved_list, true) ;
	  }
      }
  }
  catch(e) {} ;

  create_ue_lists.done = true ;
  create_ue_lists.yet_done = true ;
}

function storageEventHandler(e)
{
  create_ue_lists.done = false ;
  update_job.todo['HomeUEUnsaved'] = true ;
  periodic_work_add(update_job) ;
}

function DisplayHomeUEUnsaved(node)
{
  if ( window.localStorage && ! DisplayHomeUEUnsaved.done )
    {
      window.addEventListener('storage', storageEventHandler, false);
      DisplayHomeUEUnsaved.done = true ;
    }
  create_ue_lists() ;
  if ( create_ue_lists.unsaved_list.length == 0 )
    return [' ', [], [], 'id="HomeUEUnsaved"'] ;
  return [display_ues("TH_home_unsaved_tables",
		      _("TIP_home_unsaved_tables"),
		      create_ue_lists.unsaved_list,
		      {hide_open_close: true, hide_sort: true,
			  default_order: "A"}),
	  [], [], 'id="HomeUEUnsaved"'] ;
}
DisplayHomeUEUnsaved.need_node = ['HomeUEBookmarked' ,'HomeUENrAccess',
				  'HomeUEMasterOf', 'HomeSemesters',
				  'HomePreferences'] ;

function DisplayHomeUENrAccess(node)
{
  create_ue_lists() ;
  if ( create_ue_lists.favorite_list.length == 0 )
    return '' ;
  return [display_ues("TH_home_bookmark_ue",
		      _("TIP_home_bookmark_ue_before") + '★',
		      create_ue_lists.favorite_list,
		      {default_order:'★'}),
	  [], [], 'id="HomeUENrAccess"'] ;
}
DisplayHomeUENrAccess.need_node = DisplayHomeUEUnsaved.need_node ;

function DisplayHomeUEAcceded(node)
{
  create_ue_lists() ;
  return [display_ues("TH_home_acceded_ue", "", create_ue_lists.acceded_list,
		      {default_order: '☆', nr_max: 5}),
	  [], [], 'id="HomeUEAcceded"'] ;
}
DisplayHomeUEAcceded.need_node = DisplayHomeUENrAccess.need_node ;

function DisplayHomeUEBookmarked(node)
{
  create_ue_lists() ;
  if ( create_ue_lists.master_of_list.length == 0 )
    return '' ;
  years = {} ;
  for(var i in create_ue_lists.master_of_list)
    years[code_clean_up(create_ue_lists.master_of_list[i]).split('/')[0]]=true;
  return [display_ues("TH_home_master_of", _("TIP_home_master_of"),
		      create_ue_lists.master_of_list,
		      {default_order: 'A', code_filter: years}),
	  [], [], 'id="HomeUEBookmarked"'] ;
}
DisplayHomeUEBookmarked.need_node = DisplayHomeUENrAccess.need_node ;

function DisplayHomeUETeacher(node)
{
  create_ue_lists() ;
  if ( create_ue_lists.ues_teacher.length == 0 )
    return '' ;
  return [display_ues("TH_home_ue_master", _("TIP_home_ue_master"),
		      create_ue_lists.ues_teacher,
		      {default_order: 'A'}),
	  [], [], 'id="HomeUETeacher"'] ;
}
DisplayHomeUETeacher.need_node = DisplayHomeUENrAccess.need_node ;

function DisplayHomeUEMasterOf(node)
{
  return '' ;
}

function string_contains(string, value)
{
  if ( string )
    return replaceDiacritics(string.toUpperCase()).indexOf(value) != -1 ;
}

function string_highlight(string, txt)
{
  if ( txt == '' )
    return string ;
  var u = replaceDiacritics(string.toUpperCase()) ;
  i = u.indexOf(txt) ;
  if ( i == -1 )
    return string ;
  return string.substr(0, i)
    + '<span class="highlight">' + string.substr(i, txt.length)
    + '</span>'
    + string_highlight(string.substr(i + txt.length)) ;
}

function search_ue_list(txt)
{
  txt = replaceDiacritics(txt.toUpperCase()) ;
  search_ue_list.txt = html(txt) ;
  if ( txt == '' )
    return '' ;
  var ues = [], done = {} ;
  for(var ue in all_ues)
    {
      ue = all_ues[ue] ;
      if ( done[ue.name] )
	continue ;
      done[ue.name] = true ;
      if ( string_contains(ue.intitule, txt)
	   || string_contains(ue.name, txt)
	   || ( ue.responsable
		&& string_contains(ue.responsable.join(', '), txt)
	      )
	   || ( ue.old_names
		&& string_contains(ue.old_names.join(' '), txt)
	      )
	 )
	if ( ue.nr_students_ue != undefined
	     && ! ue.name.match(/-/) ) // 'etape-'
	  ues.push('UE-' + ue.name) ;
	else
	  ues.push(ue.name) ;
    }
  if ( ues.length == 0 )
    return '<b>' + _("MSG_home_nothing") + '</b>' ;
  return display_ues("TH_home_search", '', ues,
		     {nr_max: 100, hide_title: true, default_order: "A"}) ;
}

function update_block_content(name)
{
  var e = document.getElementById(name) ;
  if ( ! e )
    return ;
  var node = display_definition[name] ;
  node.data = display_data[name.replace('Display', '')] ;
  var html = node.fct(node) ;
  if ( html instanceof Array)
    html = html[0] ;
  e.innerHTML = html ;
}

function update_job()
{
  for(var block in update_job.todo)
    {
      update_block_content(block) ;
      delete update_job.todo[block] ;
      return true ;
    }
  return false ;
}
update_job.todo = [] ;

function search_ue_change(t)
{
  if ( t.value == search_ue_change.last_value )
    return ;
  search_ue_change.last_value = t.value ;
  set_option('ue', t.value) ;
  document.getElementById("ue_search_result").innerHTML =
    search_ue_list(t.value) ;

  for(var i in display_definition['HomeUE'].children)
    update_job.todo[display_definition['HomeUE'].children[i].name] = true ;
  periodic_work_add(update_job)
}
search_ue_change.last_value = get_option('ue', '') ;

function DisplayHomeUE(node)
{
  var s = [display_ues("TH_home_search", _("TIP_home_search_ue"), [],
		       {default_order: 'A', hide_open_close: true})
	  ] ;
  s[0] = s[0].substr(0, s[0].length - 6) ; // Remove last </div>
  s.push('<div class="search_box"><input id="search_ue" onkeyup="search_ue_change(this)" onpaste="t=this;setTimeout(function(){search_ue_change(t);},100)" value="' + encode_value(search_ue_change.last_value) + '"></div></div>') ;
  s.push('<div id="ue_search_result" class="ue_list">') ;
  if ( search_ue_change.last_value )
    s.push(search_ue_list(search_ue_change.last_value)) ;
  s.push('</div>') ;
  var children = display_definition['HomeUE'].children ;
  setTimeout(function() { document.getElementById('search_ue').select() ; },
	     100) ;
  for(var i in children)
    s.push(display_display(children[i])) ;
  return s.join('') ;
}
DisplayHomeUE.need_node = ['HomePreferences'] ;

function university_year()
{
  var ys = year_semester().split('/') ;
  var i = myindex(semesters, ys[1]) ;
  if ( i == -1 )
    return Number(ys[0]) ;
  return Number(ys[0]) + semesters_year[i] ;
}

var is_a_favorite = {} ;
var is_a_favorite_action = {} ;
var is_a_refered = {} ;
var students_info = {} ;

function student_notepad_link(path)
{
  return fast_tip('<a href="' + path + '" target="_blank">' + _("TH_home_notepad") + '</a>',
		  _("TIP_home_notepad")) ;
}

function get_student_list(t)
{
  while( t.className != 'ue_list' )
    t = t.parentNode ;
  var s = [] ;
  for(var i = 1 ; i < t.childNodes.length; i++)
    s.push(t.childNodes[i].childNodes[1].innerHTML) ;
  return s ;
}

function send_mails(t)
{
  var students = get_student_list(t) ;
  var s = [] ;
  for(var i in students)
    s.push(students_info[students[i]][3]) ;
  my_mailto(s.join(','), true) ;
}
function student_mails_link()
{
  return fast_tip('<a onclick="send_mails(this)">'
		    + _("TH_home_mail") + '</a>', _("TIP_home_mail")) ;
}

function go_suivi_students(t)
{
  go_suivi(get_student_list(t).join(',')) ;
}
function student_suivi_link()
{
  return fast_tip('<a onclick="go_suivi_students(this)" target="_blank">'
		  + _("TH_home_suivi") + '</a>', _("TIP_home_suivi")) ;
}

function go_import_list_do()
{
  var values = popup_text_area().value.split(/[ \t\n,;.:]+/) ;

  create_popup('import_list',
	       _("TH_home_import_refered"),
	       '<iframe width="100%" src="' + base('referent_get/')
	       + values.join('/') + '">' + '</iframe>',
	       _("MSG_home_reload"),
	       false) ;
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

function student_import_link()
{
  return fast_tip('<a href="javascript:go_import_list()">'
		  + _("TH_home_import") + '</a>', _("TIP_home_import")) ;
}

function DisplayHomeStudentPicture(node)
{
  return fast_tip('<img src="' + student_picture_url(open_student.code) + '">',
		  '<img src="' + student_picture_url(open_student.code) + '">'
		  );
}
DisplayHomeStudentPicture.need_node = [] ;

function DisplayHomeStudentMail(node)
{
  var mail = students_info[open_student.code][3] ;
  return '<a href="mailto:' + mail + '">' + mail + '</a>' ;
}
DisplayHomeStudentMail.need_node = [] ;

function DisplayHomeStudentSuivi(node)
{
  return box_button(_("MSG_home_suivi"), suivi_url(open_student.code)) ;
}
DisplayHomeStudentSuivi.need_node = [] ;

function DisplayHomeStudentBilan(node)
{
  if ( i_am_a_referent )
    return box_button(_("B_home_bilan_tomuss"),
		      base('bilan/') + open_student.code) ;
  return '' ;
}
DisplayHomeStudentBilan.need_node = [] ;

function DisplayHomeStudentGet(node)
{
  if ( display_definition["HomeStudentMenu"].table == "MSG_home_staff" )
    return '' ;
  if ( i_am_a_referent && ! is_a_refered[open_student.code] )
    return '<div onclick="javascript:catch_this_student('
      + js2(open_student.code) + ')">'
      + _("MSG_bilan_take_student").split("\n")[0] + '</div>' ;
  return '' ;
}
DisplayHomeStudentGet.need_node = [] ;

function open_student(t, code)
{
  display_definition["HomeStudentMenu"].table = get_ue_table_title(t) ;
  while( ! t.className.match(/\bue_line\b/) )
    t = t.parentNode ;
  if ( t.childNodes[t.childNodes.length-1].className.match('HomeStudentMenu') )
    {
      t.onmouseleave() ;
      return ;
    }
  t.className += " ue_line_hover" ;
  var m = document.createElement("DIV") ;
  open_student.code = code ;
  m.innerHTML = display_display(display_definition["HomeStudentMenu"]) ;
  m = m.firstChild ;
  t.onmouseleave = function() {
    try { t.removeChild(m) ;  t.className = t.className.replace(" ue_line_hover", "") ; } catch(e) {} ; t.onmouseleave = "" ; } ;
  t.appendChild(m) ;
}

function get_possible_filters(node, dict)
{
  var filter = {'tt': true, 'first_registration': true, '~any~': true} ;
  for(var i in node.data)
    {
      dict[node.data[i][0]] = true ;
      students_info[node.data[i][0]] = node.data[i] ;
      if ( node.data[i][6] )
	{
	  var t = node.data[i][6].split(/  */) ;
	  if ( t[0] !== '' )
	    for(var j in t)
	      filter[t[j]] = true ;
	}
    }
  return filter ;
}

function DisplayHomeStudentFavorites(node)
{
  if ( node.data.length == 0 )
    return '' ;
  var notebook = base(university_year()
		      + "/Favoris/"
		      + username.replace(/\./g, "__")
		      ) ;
  return [display_ues(_("TH_home_bookmark_student"), '', node.data,
		      {students:true, hide_sort: true,
			  before_title: node.data.length + ' ',
			  default_order: 'surname+firstname',
			  code_filter:get_possible_filters(node, is_a_favorite),
			  title_second_line: student_notepad_link(notebook)
			  + '/' + student_mails_link()
			  + '/' + student_suivi_link()
			  }),
	  [], [], 'id="HomeStudentFavorites"'] ;
}

function current_semester()
{
  return year_semester().split('/')[1] ;
}

function DisplayHomeStudentRefered(node)
{
  if ( node.data.length == 0 )
    return '' ;

  var notebook = base(university_year()
		      + "/Referents/"
		      + username.replace(/\./g, "__")
		      + (current_semester()!=first_university_year_semester()[1]
			 ? '/=column_offset=5'
			 : '')
		      ) ;
  
  return [display_ues(_("TH_home_refered_student"), '', node.data,
		      {students:true, hide_sort: true,
			  before_title: node.data.length + ' ',
			  code_filter: get_possible_filters(node, is_a_refered),
			  default_order: 'surname+firstname',
			  title_second_line:
			'<small>'
			  + student_notepad_link(notebook)
			  + '/' + student_mails_link()
			  + '/' + student_suivi_link()
			  + '/' + student_import_link()
			  + '</small>'
			  }),
	  [], [], 'id="HomeStudentRefered"'] ;
}

// This function may be called by 'login_list' plugin.
function full_login_list(login, results, add)
{
  if ( full_login_list.cache[login] === undefined )
      full_login_list.cache[login] = {'student':[], 'teacher':[]} ;

  full_login_list.cache[login][add] = results ;

  for(var i in results)
    {
      var i = results[i] ;
      if ( students_info[i[0]] === undefined )
	students_info[i[0]] = i ;
    }

  if ( login != ask_login_list )
    return ;

  if ( full_login_list.style )
    full_login_list.style.display = "none" ;

  if ( add == 'student' )
    update_job.todo['HomeStudentStudents'] = true ;
  else
    update_job.todo['HomeStudentTeachers'] = true ;
  periodic_work_add(update_job) ;
}
full_login_list.cache = {} ;

function update_students_real(t)
{
  update_students_real.pending = false ;
  if ( ask_login_list.length <= 1 )
    return ;
  var s = document.createElement('SCRIPT') ;
  s.src = base('login_list/') + encode_uri(ask_login_list) ;
  document.getElementsByTagName('BODY')[0].appendChild(s) ;
  if ( t )
    full_login_list.style = t.parentNode.lastChild.style ;
}

function search_student_change(t)
{
  ask_login_list = replaceDiacritics(t.value.trim()).toUpperCase() ;
  set_option('student', ask_login_list) ;
  if ( t.value.trim().length >= 2
       && full_login_list.cache[ask_login_list] === undefined
       )
    {
      if ( t.parentNode.lastChild.style )
	t.parentNode.lastChild.style.display = "block" ;
      if ( ! update_students_real.pending )
	{
	  update_students_real.pending = true ;
	  setTimeout(function() { update_students_real(t) ; }, 1000) ;
	}
    }
  update_job.todo['HomeStudentStudents' ] = true ;
  update_job.todo['HomeStudentTeachers' ] = true ;
  update_job.todo['HomeStudentFavorites'] = true ;
  update_job.todo['HomeStudentRefered'  ] = true ;
  periodic_work_add(update_job) ;
}

function DisplayHomeStudentStudents(node)
{
  var s = [] ;
  try {
    s = full_login_list.cache[ask_login_list].student ;
  } catch(e) {} ;
  return [display_ues("MSG_home_students", "", s,
		      {students:true, hide_sort: true,
			  default_order: 'surname+firstname',
			  //  code_filter: get_possible_filters(s)
			  }),
	  [], [], 'id="HomeStudentStudents"'] ;
}
DisplayHomeStudentStudents.need_node = [] ;

function DisplayHomeStudentTeachers(node)
{
  var s = [] ;
  try {
    s = full_login_list.cache[ask_login_list].teacher ;
  } catch(e) {} ;
  return [display_ues("MSG_home_staff", "", s,
		      {students:true, hide_sort: true,
			  default_order: "surname+firstname",
			  }),
	  [], [], 'id="HomeStudentTeachers"'] ;
}
DisplayHomeStudentTeachers.need_node = [] ;

function DisplayHomeStudents(node)
{
  if ( ask_login_list === undefined )
    {
      ask_login_list = get_option('student', '') ;
      update_students_real() ;
    }

  var s = [display_ues("TH_home_search", _("TIP_home_search_student"), [],
  {students:true, default_order: 'A', hide_sort: true, hide_open_close: true,
   default_order: "surname+firstname"})
	   ] ;
  s[0] = s[0].substr(0, s[0].length - 6) ; // Remove last </div>
  s.push('<div class="search_box"><input id="students_list" onkeyup="search_student_change(this)" onpaste="t=this;setTimeout(function(){search_student_change(t);},100)" value="'
	 + encode_value(ask_login_list && ask_login_list.toLowerCase() || '')
	 + '"><div style="display:none">' + _("MSG_home_searching")
	 + '</div></div></div>') ;
  var children = display_definition['HomeStudents'].children ;
  for(var i in children)
    s.push(display_display(children[i])) ;
  return s.join('') ;
}
DisplayHomeStudents.need_node = ['HomePreferences'] ;


function do_action(action, html_class, help)
{
  if ( html_class == 'veryunsafe' )
    if (! confirm(help + '\n\n' + _("ALERT_are_you_sure2")) )
      return ;
  if ( action.substr(0,1) == '/' )
    goto_url(url + action) ;
  else
    goto_url(base(action)) ;
}

function go_year(x)
{
  goto_url(base(university_year()) + "/" + x) ;
}

function go_year_after(x)
{
  goto_url(base(x + '/' + the_year())) ;
}

function the_year()
{
  return Number(year_semester().split('/')[0]) ;
}

function DisplayHomeActions(node)
{
  var links = node.data ;
  var boxes = {}, link_name, link_help, favorites = [] ;
  var nb_actions = 0 ;
  try {
  is_a_favorite_action = JSON.parse(localStorage["favorite_actions"] || "{}") ;
  } catch(e) { } ;
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
      if ( is_a_favorite_action[links[i][3]] )
	favorites.push(links[i]) ;
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
  var t = [] ;
  if ( favorites.length )
    t.push(display_ues('', '', favorites, {
	  actions: true, hide_sort: true, do_not_sort: true,
	    favorite_toggle: true })) ;
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
      t.push(display_ues(box_name[0], '', box, {
	    actions: true, hide_sort: true, do_not_sort: true,
	      favorite_toggle: links.length > 30})) ;
    }

  var children = display_definition['HomeActions'].children ;
  for(var i in children)
    t.push(display_display(children[i])) ;
  return t.join('') ;
}

function do_touchstart()
{
  do_touchstart.touch = true ;
}

function initialize_home3()
{
  lib_init() ;
}

