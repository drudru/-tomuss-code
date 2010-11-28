// -*- coding: utf-8 -*-
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

// HTML elements
var student ;
var student_display ;
var dates ;
var ampm ;
var startdate ;
var enddate ;
var start ;
var end ;
var sendabj ;
var datasend ;
var da_list ;
var comment ;

//
var current_abjs ;
var moving_date ;
var old_login ;

// Constants
var months = ["Jan","Fév","Mar","Avr","Mai","Jui","Jul",
	     "Aoû", "Sep","Oct","Nov","Déc"] ;

var months_long = ["Janvier","Février","Mars","Avril","Mai","Juin","Juillet",
	     "Août", "Septembre","Octobre","Novembre","Décembre"] ;

var days = ["Dim", "Lun", "Mar", "Mer", "Jeu", "Ven", "Sam"] ;

var days_long = ["Dimanche", "Lundi", "Mardi", "Mercredi",
		 "Jeudi", "Vendredi", "Samedi"] ;

var am = 'M' ;
var pm = 'A' ;
var contains_pm = new RegExp('.*(' + pm + '|' + pm.toLowerCase() + ').*') ;


function abj_init()
{
  student         = document.getElementById('student'        ) ;
  student_display = document.getElementById('student_display') ;
  dates           = document.getElementById('dates'          ) ;
  ampm            = document.getElementById('ampm'           ) ;
  startdate       = document.getElementById('startdate'      ) ;
  enddate         = document.getElementById('enddate'        ) ;
  start           = document.getElementById('start'          ) ;
  end             = document.getElementById('end'            ) ;
  sendabj         = document.getElementById('sendabj'        ) ;
  datasend        = document.getElementById('datasend'       ) ;
  da_list         = document.getElementById('da'             ) ;
  comment         = document.getElementById('abjcomment'     ) ;

  old_login = '' ;

  _today = new Date() ;
   _today.setHours(0,0,0,0) ;


   // Initialize date bar
   end.value = _today.getDate() + '/' + (_today.getMonth() + 1) + '/' +
     _today.getFullYear() + ' ' + pm ;
   
   ampm.childNodes[ampm.childNodes.length-1].full_time = _today.getDate()
     + '/' + (_today.getMonth() + 1) + '/' + _today.getFullYear() + ' ' + pm ;
   ampm.childNodes[ampm.childNodes.length-1].start_time = _today.getTime() ;
   
   var i = dates.childNodes.length - 2 ;
   
   while( i )
     {
       var td = dates.childNodes[i] ;
       var week_day = _today.getDay() ;
       
       td.innerHTML = days[week_day] + '<br>' + _today.getDate() + '<br>' +
	 months[_today.getMonth()] ;
       if ( week_day === 0 || week_day == 6 )
	 td.className = 'weekend' ;
       
       td = ampm.childNodes[i*2-1] ;
       td.innerHTML = am ;
       if ( week_day === 0 || week_day == 6 )
	 td.className = 'weekend' ;
       td.start_time = _today.getTime() ;
       td.full_time = _today.getDate() + '/' + (_today.getMonth() + 1) + '/' +
	 _today.getFullYear() + ' ' + am ;
       _today.setHours(12) ;
       
       td = ampm.childNodes[i*2+1-1] ;
       td.innerHTML = pm ;
       if ( week_day === 0 || week_day == 6 )
	 td.className = 'weekend' ;
       td.start_time = _today.getTime() ;
       td.full_time = _today.getDate() + '/' + (_today.getMonth() + 1) + '/' +
	 _today.getFullYear() + ' ' + pm ;
       
       _today.setHours(0) ;
       _today.setTime(_today.getTime() - 3600*1000) ;
       _today.setHours(0) ;

       i-- ;
     }
   
   start.value = _today.getDate() + '/' + (_today.getMonth() + 1) + '/' +
     _today.getFullYear() ;
   
   enddate.style.position = "absolute" ;
   startdate.style.position = "absolute" ;


  _today = new Date() ;

  end.onchange = update_cursor_from_text ;
  end.onkeypress = update_if_return ; // IE bug
  start.onchange = update_cursor_from_text ;
  start.onkeypress = update_if_return ; // IE bug
  
  startdate.childNodes[1].onmousedown = start_move ;
  enddate.childNodes[0].onmousedown = start_move ;
  startdate.childNodes[1].onmouseup = stop_move ;
  enddate.childNodes[0].onmouseup = stop_move ;
  
  document.getElementById('body').onmousemove = moving ;
  document.getElementById('body').onmouseup = stop_move ;

  update_cursor() ;
}


function parse_date(t)
{
  if ( t === undefined )
    return new Date() ;
  text = t.split(/[ \/AMPamp]/) ; /* \/ because of old netscape versions */
  if ( text[0] === '' )
    text[0] = _today.getDate() ;
  if ( text.length == 1 )
    text[1] = _today.getMonth()+1 ;
  if ( text.length == 2 )
    text[2] = _today.getFullYear() ;
  var y = text[2] ;
  if ( y < 100 )
    y = Number(y) + (_today.getFullYear() / 100).toFixed(0) * 100 ;
  if ( t.search(contains_pm) != -1 )
    h = 12 ;
  else
    h = 0 ;

  var d = new Date(y, text[1]-1, text[0], h) ;

  return d ;
}

function update_cursor_end()
{
  var e = parse_date(end.value).getTime() ;

  for(var i = 1; ; i++)
    {
      var td = ampm.childNodes[i] ;
      if ( td === undefined )
	{
	  enddate.td_index = i ;
	  enddate.style.left = "auto" ;
	  enddate.style.right = 0 ;
	  break ;
	}
      if ( e <= td.start_time )
	{
	  enddate.td_index = i ;
	  enddate.style.left = td.offsetLeft + td.offsetWidth - enddate.childNodes[0].offsetWidth/2  ;
	  break ;
	}
    }
}

function update_cursor_start()
{
  var e = parse_date(start.value).getTime() ;
  for(var i = 1; ; i++)
    {
      var td = ampm.childNodes[i] ;
      if ( td === undefined )
	break ;
      if ( e < td.start_time )
	{
	  startdate.td_index = i - 1 ;
	  if ( i == 1 )
	    startdate.style.left = 0 ;
	  else
	    startdate.style.left = td.offsetLeft - start.offsetWidth - td.offsetWidth - startdate.childNodes[1].offsetWidth/2 ;
	  break ;
	}
    }
}

function nice_date_short(d)
{
  var date = parse_date(d) ;
  var s = days[date.getDay()] + ' ' ;
  if ( date.getDate() < 10 )
    s += '0' ;
  s += date.getDate() + '/' ;
  if ( date.getMonth() < 9 )
    s += '0' ;
  s += (date.getMonth()+1) + '/' + date.getFullYear()
    + (date.getHours() < 8 ? 'M' : 'A') ;
  return s ;
}

function nice_date(d)
{
  return nice_date_short(d).replace(/M$/, ' Matin')
    .replace(/A$/, ' Après-midi') ;
}

function date_to_store(d)
{
  d = parse_date(d) ;
  return d.getDate() + '/' + (d.getMonth() + 1) + '/' +
    d.getFullYear() + '/' + (d.getHours() < 8 ? 'M' : 'A') ;
}

function update_button_real()
{
  sendabj.value = 'Sauvegarder l\'ABJ du\n' + nice_date(date_to_store(start.value))
    + '\nau\n' + nice_date(date_to_store(end.value)) ;
}

function update_button()
{
  if ( parse_date(start.value).getTime() > parse_date(end.value).getTime() )
    {
      if ( moving_date == enddate )
	start.value = end.value ;
      else
	end.value = start.value ;
    }
 update_button_real() ;
}

function update_cursor()
{
  update_button() ;
  update_cursor_start() ;
  update_cursor_end() ;

  for(var i = 0; ; i++)
    {
      var td = ampm.childNodes[i] ;
      if ( td === undefined )
	break ;
      if ( i >= startdate.td_index && i <= enddate.td_index )
	td.style.background = "white" ;
      else
	td.style.background = "#DDD" ;
    }
    
}

function update_cursor_from_text(event)
{
  event = the_event(event) ;
  input = event.target ;
  input.value = date_to_store(input.value) ;
  update_cursor() ;
}

function time_stamp()
{
  var t = new Date() ;
  return t.getTime() ;
}

function is_a_student_login()
{
  return student.value.length == 8 ;
}

function get_image(src)
{
  var img = document.createElement('IMG') ;
  img.src = baset + student.value + src + '/' + time_stamp() ;
  datasend.appendChild(img) ;
}

function send_abj()
{
  if ( ! is_a_student_login() )
    return ;

  for(var abj in current_abjs)
    {
      if ( date_to_store(current_abjs[abj][0]) == date_to_store(start.value)
	   && date_to_store(current_abjs[abj][1]) == date_to_store(end.value) )
	{
	  alert("Cette ABJ existe déjà !") ;
	  return ;
	}
    }
  get_image('/addabj/' +
	    date_to_store(start.value) + '/' + date_to_store(end.value)
	    + '/' + encode_uri(comment.value)) ;
  comment.value = '' ;
}

function del_abj(fro, to)
{
  get_image('/delabj/'+ date_to_store(fro) + '/' + date_to_store(to)) ;
}

function moving(event)
{
  if ( moving_date === undefined )
    return true;

  event = the_event(event) ;

  var input, arrow ;

  if ( moving_date == startdate )
    {
      input = moving_date.childNodes[0] ;
      arrow = moving_date.childNodes[1] ;
      moving_date.style.left = event.x - input.offsetWidth -
	arrow.offsetWidth/2  ;
    }
  else
    {
      input = moving_date.childNodes[1] ;
      arrow = moving_date.childNodes[0] ;
      moving_date.style.left = event.x - arrow.offsetWidth/2  ;
    }

  for(var i = 1; ; i++)
    {
      var td = ampm.childNodes[i] ;
      if ( td === undefined )
	break ;
      if ( event.x < td.offsetLeft +  td.offsetWidth )
	{
	  // comment.value = event.x + ' ' + td.offsetLeft + ' '+  td.offsetWidth ;
	  if ( input.value != td.full_time )
	    {
	      input.value = td.full_time ;
	      update_cursor() ;
	    }
	  break ;
	}
    }
  stop_event(event);
  return false ;
}

function start_move(event)
{
  event = the_event(event) ;
  moving_date = event.target.parentNode ;
  stop_event(event);
  return false ;
}

function update_if_return(event)
{
  event = the_event(event) ;
  if ( event.keyCode == 13 )
    {
      update_cursor_from_text(event) ;
      stop_event(event) ;
      return false ;
    }
  return true ;
}

function stop_move(event)
{
  moving_date = undefined ;
  return false ;
}

function display_abjs(abjs)
{
  current_abjs = abjs ;
  if ( abjs.length == 0 )
    return ;
  s = '<TABLE class="display_abjs colored">' ;
  s += '<TR><TH COLSPAN="6">ABJ saisies</TH></TR>' ;
  s += '<TR><TH>Début</TH><TH>Fin</TH><TH>Durée</TH><TH>Actions</TH><TH>Saisie par</TH><TH>Commentaire</TH></TR>' ;
  var abj_days = 0 ;
  for(var abj in abjs)
    {
      var d = (0.5 + (parse_date(abjs[abj][1]).getTime()
		      - parse_date(abjs[abj][0]).getTime())/(1000*86400)) ;
      abj_days += d ;
      s += '<TR><TD style="text-align:right">' + nice_date_short(abjs[abj][0]) +
	'</TD><TD style="text-align:right">' + nice_date_short(abjs[abj][1]) +
	'</TD><TD style="text-align:right">' + d.toFixed(1) +
	'</TD><TD><A href="#" onclick="del_abj(\'' +
	date_to_store(abjs[abj][0]) + '\',\'' +
	date_to_store(abjs[abj][1]) + '\');return false;">Détruire</a>' +
	'</TD><TD>' + abjs[abj][2] +
	'</TD><TD>' + html(abjs[abj][3]) +
	'</TD></TR>' ;
    }
  s += '</TABLE>' ;
  s += "Nombre de jours d'ABJ : " + abj_days.toFixed(1) ;
  append_html(s) ;
}

function display_da(das)
{
  current_da = das ;
  if ( das.length == 0 )
    return ;
  s = '<TABLE class="display_da colored">' ;
  s += '<TR><TH COLSPAN="5">Dispenses d\'assiduité saisies</TH></TR>' ;
  s += '<TR><TH>UE</TH><TH>Début</TH><TH>Actions</TH><TH>Saisie par</TH><TH>Commentaire</TH></TR>' ;
  for(var da in das)
    {
      s += '<TR><TD>' + das[da][0] +
	'</TD><TD>' + nice_date_short(das[da][1]) +
	'</TD><TD><A href="#" onclick="rem_da(\'' + das[da][0] +
	'\');return false;">Détruire</a>' +
	'</TD><TD>' + das[da][2] +
	'</TD><TD>' + das[da][3] +
	'</TD></TR>' ;
    }
  s += '</TABLE>' ;
  append_html(s) ;
}

function ues_without_da(da)
{
  while(da_list.childNodes[1])
    da_list.removeChild(da_list.childNodes[1]) ;
  for(var i in da)
    {
      var o = document.createElement('option') ;
      o.innerHTML = da[i] ;
      da_list.appendChild(o) ;
    }
}

function add_an_da()
{
  if ( ! is_a_student_login() )
    return ;

  var v = da_list.childNodes[da_list.selectedIndex].value ;
  if ( !v )
    v = da_list.childNodes[da_list.selectedIndex].innerHTML ;

  var dateda = date_to_store(document.getElementById('dateda').value) ;
  dateda = dateda.substr(0, dateda.length-2) ; // Remove /M /A
  document.getElementById('dateda').value = dateda ;

  get_image('/add_da/' + v + '/' + dateda + '/' + encode_uri(comment.value)) ;
  comment.value = '' ;
}

function rem_da(ue)
{
  get_image('/rem_da/' + ue) ;
}

function login_change_force()
{
  if ( ! is_a_student_login() )
    return ;

  student_display.innerHTML = "<IMG><p class=\"wait\">Attendez le chargement des données s'il vous plait." ;

  get_image('/display') ;
}

function login_change()
{
  if ( student.value == old_login )
    return ;
  old_login = student.value ;
  login_change_force() ;
}

function set_html(s)
{
  student_display.innerHTML = s ;
}

function append_html(s)
{
  student_display.innerHTML += s ;
}
