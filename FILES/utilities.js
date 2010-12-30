/* -*- coding: utf-8 -*- */
/*
    TOMUSS: The Online Multi User Simple Spreadsheet
    Copyright (C) 2008-2010 Thierry EXCOFFIER, Universite Claude Bernard

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

var tip ;

function a_float(txt)
{
  if ( txt.replace )
    return Number(txt.replace(',', '.')) ;
  else
    return Number(txt) ;
}

/* Extract a number from 'txt' after the first string 'after'.
   If it is not possible, return 'default_value'
*/
function get_number(txt, after, default_value)
{
  txt = (' ' + txt).split(after) ;

  if ( txt.length != 2 )
    return default_value ;

  txt = txt[1].replace(',', '.') ;
  var i = txt.search(/[^-0-9.]/) ;
  if ( i != -1 )
    txt = txt.slice(0, i) ;
  if ( txt === '' )
    return default_value ;
  return Number(txt) ;
}

function millisec()
{
  var d = new Date() ;
  return d.getTime() ;
}

/* Return a Date from text like : JJ/MM/AAAA */
/* Or a number of day or hours or minutes from now as 5j 4h 3m */
function get_date(value)
{
  value = value.toString() ;
  var v = value.split('/') ;
  var d ;

  if ( v.length == 1 )
    {
      if ( value.length <= 1 )
	return false ;

      v = Number(value.substr(0, value.length-1)) ;
      if ( isNaN(v) )
	return false ;

      d = new Date() ;
      d.reverse = true ;
      switch( value.substr(value.length-1).toLowerCase() )
	{
	case 'a':
	case 'y': d.setTime(d.getTime() - v*365*24*60*60*1000) ; break ;
	case 'm': d.setTime(d.getTime() - v*30*24*60*60*1000) ; break ;
	case 'w':
	case 's': d.setTime(d.getTime() - v*7*24*60*60*1000) ; break ;
	case 'j':
	case 'd': d.setTime(d.getTime() - v*24*60*60*1000) ; break ;
	case 'h': d.setTime(d.getTime() - v*60*60*1000) ; break ;
	default:  return false ;
	}
      d.sup = d ;
      return d ;
    }

  for(var i in v)
    if ( isNaN(Number(v[i])) )
      return false ;
  /*
  if ( v.length == 1 )
    {
      d = new Date(v[0], 0,      1) ;
      d.sup = new Date() ;
      d.sup.setTime(d.getTime()) ;
      d.sup.setMonth(11) ;
      d.sup.setDate(31) ;
    }
    else */ if ( v.length == 2 )
    {
      d = new Date(v[1], v[0]-1, 1) ;
      d.sup = new Date() ;
      d.sup.setTime(d.getTime()) ;
      d.sup.setDate(31) ;
      if ( d.sup.getDate() < 4 )
	d.sup.setDate(-d.sup.getDate()) ;
    }
  else if ( v.length == 3 )
    {
      d = new Date(v[2], v[1]-1, v[0]) ;
      d.sup = new Date() ;
      d.sup.setTime(d.getTime()) ;
    }
  else
    return false ;
  d.sup.setHours(23, 59, 59) ;
  return d ;
}

function get_date_inf(value)
{
  var d ;
  var v = value.toString().split('/') ;
  if ( v.length == 3 )
    {
      d = new Date(v[2], v[1]-1, v[0]) ;
      if ( d )
	return d.getTime() ;
    }
  if ( v.length == 4 )
    {
      d = new Date(v[2], v[1]-1, v[0], v[3]) ;
      if ( d )
	return d.getTime() ;
    }
  return 1e100 ;
}

function get_date_sup(value)
{
  var d ;
  var v = value.toString().split('/') ;
  if ( v.length == 3 )
    {
      d = new Date(v[2], v[1]-1, v[0]) ;
      if ( d )
	return d.getTime() + 3600*24*1000 ;
    }
  if ( v.length == 4 )
    {
      d = new Date(v[2], v[1]-1, v[0], v[3]) ;
      if ( d )
	return d.getTime() + 3600*1000 ;
    }
  return -1e100 ;
}

function formatte_date(d)
{
  return d.getDate() + '/' + (d.getMonth() + 1) + '/' + d.getFullYear() ;
}

function left_justify(text, size)
{
  return (text + '                                       ').substr(0,size).replace(/ /g, '&nbsp;') ;
}

function two_digits(x)
{
  if ( x < 10 )
    return '0' + x ;
  return x.toString() ;
}

// var jours = ["Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"] ;
var jours = ["Dim", "Lun", "Mar", "Mer", "Jeu", "Ven", "Sam"] ;
var jours_full = ["Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"] ;

function date(x)
{
  if ( x === '' )
    return '' ;

  var year = x.slice(0, 4) ;
  var month = x.slice(4, 6) ;
  var day = x.slice(6, 8) ;
  var hours = x.slice(8, 10) ;
  var minutes = x.slice(10, 12) ;
  var seconds = x.slice(12, 14) ;

  var d = new Date(year, month-1, day, hours, minutes, seconds).getDay() ;

  return jours[d] + ' ' + day + '/' + month + '/' + year + ' ' + hours + "h" + minutes + '.' + seconds ;
}

var months_full = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre' ] ;
function date_full(x)
{
  if ( x === '' )
    return '' ;

  var year = x.slice(0, 4) ;
  var month = x.slice(4, 6) ;
  var day = x.slice(6, 8) ;
  var hours = x.slice(8, 10) ;
  var minutes = x.slice(10, 12) ;
  var seconds = x.slice(12, 14) ;

  var d = new Date(year, month-1, day, hours, minutes, seconds).getDay() ;

  return jours_full[d] + ' ' + day + ' ' + months_full[month-1] + ' ' + year + ' à ' + hours + " heure " + minutes + ' minutes et ' + seconds + ' secondes' ;
}

// Code snippet from http://www.quirksmode.org/js/findpos.html
function findPos(obj)
{
  var curleft = 0 ;
  var curtop = 0;
  if (obj.offsetParent)
    {
      do {
	curleft += obj.offsetLeft;
	curtop += obj.offsetTop;
      } while ((obj = obj.offsetParent));
    }
  return [curleft,curtop];
}
function findPosX(obj)
{
  return findPos(obj)[0] ;
}

function findPosY(obj)
{
  return findPos(obj)[1] ;
}

function dict_size(d)
{
  var i = 0 ;
  for(var ii in d)
    i++ ;
  return i ;
}

function html(t)
{
  if ( t.replace === undefined )
    return t ; // Number
  else
    return t.replace(/&/g, '&amp;').replace(/>/g, '&gt;').replace(/</g, '&lt;') ;
}

function the_event(e)
{
  if ( e === undefined )
    e = window.event ;

  var event = clone_event(e) ; 
  event.real_event = e ;

  if ( event.pageX )
    {
      event.x = event.pageX ;
      event.y = event.pageY ;
    }

  if ( event.target === undefined )
    event.target = event.srcElement ;
  
  return event ;
}

function myindex(table, x)
{
  if ( table.indexOf )
    return table.indexOf(x) ;
  // For NodeList (not an Array) or Navigator with this method
  for(var i in table)
    if ( table[i] === x )
      return Number(i) ;
  return -1 ;
}


var displayed_tip ;
var select_with_focus  ;// To be blurred if a tip appear.
var id_add_some_help ;

function take_focus(t)
{
  if ( t.tomuss_editable == false )
    {
      t.blur() ;
      return ;
    }
  select_with_focus = t ;
  t.onblur = function() { select_with_focus = undefined ; } ;
  hidden_out() ;
}

function add_some_help()
{
  __d(displayed_tip.nodeName + ' ' + displayed_tip.className + ' : ');
  for(var i in displayed_tip.childNodes)
    __d(displayed_tip.childNodes[i].nodeName + '/' + displayed_tip.childNodes[i].className + ' ' );
  __d('\n');
  displayed_tip.childNodes[0].childNodes[1].innerHTML = '*XXX*';
}

function remove_some_help()
{
//  displayed_tip.childNodes[0].childNodes[1].innerHTML = 'Y';
}

function tip_top(tt)
{
  var i ;

  if ( tt === undefined || tt.tagName === undefined )
    {
      return undefined ;
    }

  i = 0 ;
  while( tt.tagName != 'DIV' || tt.className.indexOf('tipped') == -1 )
    {
      tt = tt.parentNode ;
      i++ ;
      if ( i == 10 )
	{
	  debug(tt) ;
	  return undefined ;
	}
    }
  return tt ;
}

var display_tips = false ; // Overriden by lib.js

function hidden_over(event)
{
  if ( displayed_tip !== undefined )
    return ;

  if ( ! display_tips )
    return ;

  if ( select_with_focus )
    return ;

  event = the_event(event) ;

  var t = tip_top(event.target) ;
  
  displayed_tip = t ;
  t.childNodes[0].style.top = '' ;
  t.childNodes[0].style.right = '' ;
  t.childNodes[0].style.display = 'inline' ;

  // Get size and position of object and tip box.

  var pos = findPos(t.childNodes[1]) ;
  var x = pos[0] ;
  var y = pos[1] ;
  var tiph = t.childNodes[0].offsetHeight ;
  var tipw = t.childNodes[0].offsetWidth ;
  var oh, ow ;
  var tag ;
  // The DOM tree is not the same for every browser.
  // There is certainly a bug in the generated HTML
  // This loop turn around the possible bug.
  for(var i=0; i<4; i++)
    {
      switch(i)
	{
	case 0: tag = t ; break ; // Bug FireFox
	case 1: tag = t.childNodes[1] ; break ;
	case 2: tag = t.childNodes[1].firstChild ; break ;
	case 3: tag = t.childNodes[1].firstChild.firstChild ; break ;
	}
      
      oh = tag.offsetHeight ;
      ow = tag.offsetWidth ;
      if ( oh !== 0 )
	break ;
    }

  // The default is to put the tip box under the object.

  // If it it is right truncated, align it to the right
  if ( x + tipw > window_width())
    t.childNodes[0].style.right = '0px' ;
  else
    t.childNodes[0].style.left = x ;

  if ( y + oh + tiph - scrollTop() < window_height() )
    {
      t.childNodes[0].style.top = y + oh + 2;
    }
  else
    {
      // If it is bottom truncated, 
      var top = y - tiph ;
      if ( top > 0 )
	t.childNodes[0].style.top = top ;
      else
	{
	  // It is top truncated : move it right or left.
	  t.childNodes[0].style.top = '0' ;
	  if ( x + ow + tipw > window_width() )
	    t.childNodes[0].style.left = '0' ;
	  else
	    t.childNodes[0].style.left = x + ow ;
	}
    }

  // XXX
  //  id_add_some_help = setTimeout(add_some_help, 1000) ;

  if ( tip )
    tip.style.display = 'none' ;
}

function hidden_out()
{
  if ( displayed_tip )
    {
      if ( id_add_some_help !== undefined )
	{
	  clearTimeout(id_add_some_help) ;
	  id_add_some_help = undefined ;
	}
      remove_some_help() ;
      displayed_tip.childNodes[0].style.display = 'none' ;
      displayed_tip = undefined ;
    }
}

function hidden_txt(html, help, classname, id)
{
  if ( id )
    id = ' id="' + id + '"' ;
  else
    id = '' ;
  if ( classname !== undefined )
    classname = ' ' + classname ;
  else
    classname = '' ;

  if ( html === undefined )
    html = '????????' ;
  html = html.toString() ;
  html = html.replace('<a', '<a onfocus="hidden_over(event);" onblur="hidden_out();"') ;

  return '<div ' + id + 'class="tipped' + classname + '" onmouseover="hidden_over(event);" onmouseout="hidden_out();"><div class="help" onmousemove="hidden_out();">' + help + '<div></div><div></div></div><var class="tipped">' + html + '</var></div>' ;

}


function hidden(html, help, classname, id)
{
  document.write(hidden_txt(html, help, classname, id)) ;
}

function encode_uri(t)
{
  // Use %01 to encode / because APACHE make a mess with it
  // Use %02 to encode ? because APACHE make a mess with it
  return encodeURI(t).replace(/\?/g, "%02").replace(/#/g, "%23")
    .replace(/[.]/g, "%2E").replace(/&/g, "%26").replace(/\//g, "%01") ;
}

function encode_uri_option(t)
{
  return encode_uri(t).replace(/[=]/g,'%03').replace(/:/g, '%04') ;
}

function decode_uri_option(t)
{
  return unescape(t.replace(/%01/g,'/').replace(/%02/g,'?')
		  .replace(/%03/g,'=').replace(/%04/g,':')) ;
}

function debug(e, only, eject, hide_empty)
{
  var s = "" ;
  for(var a in e)
    {
      if ( only !== undefined && a.indexOf(only) == -1 )
	continue ;
      if ( eject !== undefined && a.indexOf(eject) != -1 )
	continue ;
      if ( hide_empty && e[a] === '' )
	continue ;
      s += a + "=" + e[a] + "\n" ;
    }
  alert(s) ;
}

function clone_event(event)
{
  var e = new Object() ;
  if ( e === undefined )
    alert_real('BIG1');
  if ( event === undefined )
    alert_real('BIG2');
  e.type = event.type ;
  e.button = event.button ;
  e.keyCode = event.keyCode ;
  e.shiftKey = event.shiftKey ;
  e.metaKey = event.metaKey ;
  e.ctrlKey = event.ctrlKey ;
  e.altKey = event.altKey ;
  e.target = event.target ;
  e.srcElement = event.srcElement ;
  e.pageX = event.pageX ;
  e.pageY = event.pageY ;
  e.x = event.x ;
  e.y = event.y ;
  e.which = event.which ;
  if ( e.type == 'keypress' )
    e.charCode = event.charCode ;
  if ( event.detail )
    e.wheelDelta = -event.detail ;
  else
    e.wheelDelta = event.wheelDelta ;
  return e ;
}

function scrollTop()
{
  if ( document.body.scrollTop !== undefined )
    return document.body.scrollTop ;
  return window.screenY ;
}

function window_width()
{
  var ww = window.innerWidth ;
  if ( ww === undefined )
    return document.body.clientWidth ;
  else
    return ww ;
}

function window_height()
{
  var height = window.innerHeight ;
  if ( height === undefined )
    return document.body.clientHeight ;
  return height ;

}

function base64(s)
{
  var i, len ;
  var replace = "%\r\n!#$&'()*+/[\\]^`\"<>" ;
  /* Bad for SVG with diacritics
  for(i = 128 ; i < 256 ; i++)
    replace += String.fromCharCode(i) ;
  */
  len = replace.length ;
  for(i=0; i<len; i++)
    {
      var code = replace.charCodeAt(i) ;
      s = s.replace(RegExp('\\' + replace[i], 'g'),
		    '%' +
		    '0123456789ABCDEF'.charAt(code/16) +
		    '0123456789ABCDEF'.charAt(code%16)
		    ) ;
    }
  return s ;
}

var max_url_length = 1000 ;

function on_windows()
{
  return navigator.platform.indexOf('Win') != -1 ;
}

function window_open(url)
{
  var w ;
  if ( url )
    w = window.open(url) ;
  else
    w = window.open() ;
  if ( ! w )
     alert('Vous devez autoriser les "popup" dans votre navigateur') ;
  return w ;
}

function new_window(data, mimetype)
{
  if ( mimetype === undefined )
    mimetype = 'text/plain' ;

  var w = window_open() ;
  w.document.open(mimetype) ;
  w.document.write(data) ;
  w.document.close() ;
  return w ;
}

function mail_sort(x, y)
{
  if ( x.search('@') != -1 && y.search('@') == -1 )
    return -1 ;
  if ( y.search('@') != -1 && x.search('@') == -1 )
    return 1 ;
  if ( x.split('.')[1] > y.split('.')[1] )
    return 1 ;
  if ( x.split('.')[1] < y.split('.')[1] )
    return -1 ;
  if ( x > y )
    return 1 ;
  if ( x < y )
    return -1 ;
  return 0 ;
}

function my_mailto(mails, display)
{
  if ( mails.search('@') == -1 )
    {
      alert("Désolé, votre navigateur n'a pas encore reçu les adresses mails.\nRéessayez dans quelques secondes.") ;
      return ;
    }

  mails = mails.split(',') ;
  mails.sort(mail_sort) ;
  mails = mails.join(',') ;

  if ( display === undefined &&
       (mails.length < max_url_length || ! on_windows()) )
    {
      window.location = 'mailto:?bcc=' + mails ;
      return ;
    }
  var message = "Copiez la liste suivante dans votre logiciel de messagerie :\n\n" ;

  if ( display === undefined )
    {
      message = "Microsoft Windows interdit de lancer automatiquement\nle logiciel de messagerie quand il y a trop d'adresses.\nVous êtes donc obligé de recopier la liste en faisant un copié collé.\n\n" + message ;
    }

  return new_window(message + mails + '\n\n') ;
}

function my_csv(csv_content)
{
  if ( on_windows() )
    {
      new_window("Faites un copié/collé de cette page dans votre tableur\n\n" + csv_content, 'text/csv') ;
      return ;
    }

  window.location = 'data:text/csv;utf8,' + base64(csv_content) ;
}

/* From Olavi Ivask's Weblog */
function replaceDiacritics(s)
{
  if ( s.search(/[\300-\377]/) == -1 )
    return s ;

  var diacritics =[
		   /[\300-\306]/g, /[\340-\346]/g, // A, a
		   /[\310-\313]/g, /[\350-\353]/g, // E, e
		   /[\314-\317]/g, /[\354-\357]/g, // I, i
		   /[\322-\330]/g, /[\362-\370]/g, // O, o
		   /[\331-\334]/g, /[\371-\374]/g,  // U, u
		   /[\321]/g, /[\361]/g, // N, n
		   /[\307]/g, /[\347]/g // C, c
		   ];

  var chars = ['A','a','E','e','I','i','O','o','U','u','N','n','C','c'];

  for (var i = 0; i < diacritics.length; i++)
    {
      s = s.replace(diacritics[i],chars[i]);
    }
  return s ;
}

/*REDEFINE
This function returns the URL of the student picture.
*/
function student_picture_url(login)
{
  if ( login )
    return 'http://www.org/' + login_to_id(login) + '.png' ;
  return '' ;
}

function replace_dot_by_coma()
{
  var td = document.getElementsByTagName('TD') ;
  for(var i in td)
    {
      i = td[i] ;
      if ( i.innerHTML )
	i.innerHTML = i.innerHTML.replace(RegExp('([0-9])[.]([0-9])'),
					  '$1,$2') ;
    }
}

function replace_coma_by_dot()
{
  var td = document.getElementsByTagName('TD') ;
  for(var i in td)
    {
      i = td[i] ;
      if ( i.innerHTML )
	i.innerHTML = i.innerHTML.replace(RegExp('([0-9])[,]([0-9])'),
					  '$1.$2') ;
    }
}

// From: http://codingforums.com/showthread.php?t=11156

function HueToRgb(m1, m2, hue)
{
  var v;
  if (hue < 0)
    hue += 1;
  else if (hue > 1)
    hue -= 1;
  
  if (6 * hue < 1)
    v = m1 + (m2 - m1) * hue * 6;
  else if (2 * hue < 1)
    v = m2;
  else if (3 * hue < 2)
    v = m1 + (m2 - m1) * (2/3 - hue) * 6;
  else
    v = m1;
  
  return '0123456789ABCDEF'.substr(v*15, 1) ;
}

// h : 0...1
// l : 0...1
// s : 0...1
function hls2rgb(hue, l, s)
{
  var m1, m2;
  var r, g, b ;
  if (s == 0)
    return '#FFF' ;
  else
    {
      if (l <= 0.5)
	m2 = l * (s + 1);
      else
	m2 = l + s - l * s;
      m1 = l * 2 - m2;
      return '#'
	+ HueToRgb(m1, m2, hue + 1/3)
	+ HueToRgb(m1, m2, hue)
        + HueToRgb(m1, m2, hue - 1/3) ;
    }
}



function parseLineCSV(lineCSV)
{
  lineCSV = lineCSV.replace(/[\n\r]*$/, '') ;
  // Work around IE bug
  lineCSV = lineCSV.replace(/,/g,"\001,").split(',');
  for (var i in lineCSV)
    lineCSV[i] = lineCSV[i].replace(/\001$/g,"") ;
  
  var inside = false;
  var CSV = [] ;  
  var cell, first_char, last_char ;
  for (var i in lineCSV)
    {
      cell = lineCSV[i] ;
      first_char = cell.substr(0,1) ;
      last_char = cell.substr(cell.length-1,1) ;
      if ( first_char == '"' && last_char == '"' )
	{
	  cell = cell.substr(1, cell.length-2).replace(/""/g, '\001') ;
	}
      else
	{
	  cell = cell.replace(/""/g, '\001') ;
	  if ( inside !== false )
	    {
	      if ( last_char === '"' )
		{
		  cell = inside + ',' + cell.substr(0, cell.length-1) ;
		  inside = false ;
		}
	      else
		{
		  inside += ',' + cell ;
		  cell = undefined ;
		}
	    }
	  else
	    {
	      if ( first_char === '"' )
		{
		  inside = cell.substr(1, cell.length-1) ;
		  cell = undefined ;
		}
	    }
	}
      if ( cell !== undefined )
	{
	  CSV.push( cell.replace(/\001/g, '"') ) ;
	}
    }
  return CSV;
}

/* Helper function to load data */

var loading_bar ;
var loading_bar_2 ;

function P(t)
{
  if ( lines.length === 0 )
    {
      loading_bar = document.getElementById('loading_bar') ;
      if ( loading_bar )
	{
	  loading_bar_2 = loading_bar.childNodes[0] ;
	  loading_bar.style.display = 'block' ;
	}
    }
  lines.push(t) ;
  if ( loading_bar )
    {
      loading_bar_2.style.width = (100*lines.length/lines_to_load) + '%' ;

      if ( lines.length == lines_to_load )
	{
	  loading_bar.style.display = 'none' ;
	}
    }
}


/******************************************************************************
 *
 *
 *
 *
 *
 *
 *****************************************************************************/

function Stats(v_min, v_max, empty_is)
{
  this.min = 1e40 ;
  this.max = -1e40 ;
  this.nr_abi = 0 ;
  this.nr_abj = 0 ;
  this.nr_ppn = 0 ;
  this.nr_nan = 0 ;
  this.nr_pre = 0 ;
  this.nr_yes = 0 ;
  this.nr_no = 0 ;
  this.sum = 0 ;
  this.sum2 = 0 ;
  this.nr = 0 ;
  this.histogram = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] ;
  this.v_min = v_min ;
  this.v_max = v_max ;
  this.size = v_max - v_min ;
  this.values = [] ;
  if ( empty_is )
    this.empty_is = empty_is ;
  else
    this.empty_is = '' ;    
}

function stats_add(v)
{
  if ( v === '' )
    v = this.empty_is ;
  switch(v)
    {
    case '' : this.nr_nan++ ; return ;
    case abi: this.nr_abi++ ; return ;
    case abj: this.nr_abj++ ; return ;
    case ppn: this.nr_ppn++ ; return ;
    case pre: this.nr_pre++ ; return ;
    case yes: this.nr_yes++ ; return ;
    case no : this.nr_no++ ; return ;
    }
      
  v = a_float(v) ;
  if ( isNaN(v) ) { this.nr_nan++ ; return ; }
      
  if ( v < this.min )
    this.min = v ;
  if ( v > this.max )
    this.max = v ;
  this.sum += v ; 
  this.sum2 += v*v ; 
  var i = Math.floor(20*((v - this.v_min) / this.size)) ;
  if ( i < 0 )
    i = 0 ;
  else if ( i >= 20 )
    i = 19 ;
  this.histogram[i]++ ;
  this.values.push(v) ;
  this.nr++ ;
}

function stats_variance()
{
  return this.sum2/this.nr - (this.sum/this.nr)*(this.sum/this.nr)  ;
}

function stats_standard_deviation()
{
  return Math.pow(this.variance(),0.5) ;
}

function stats_average()
{
  return this.sum / this.nr ;
}

function stats_mediane()
{
  if ( this.values.length )
    {
      this.values.sort(function(a,b){return a - b}) ;
      return this.values[Math.floor(this.values.length/2)] ;
    }
  else
    return Number(0);
}

function stats_maxmax()
{
  var maxmax = 1 ;
  if ( this.nr_abi > maxmax ) maxmax = this.nr_abi ;
  if ( this.nr_abj > maxmax ) maxmax = this.nr_abj ;
  if ( this.nr_ppn > maxmax ) maxmax = this.nr_ppn ;
  if ( this.nr_nan > maxmax ) maxmax = this.nr_nan ;
  if ( this.nr_pre > maxmax ) maxmax = this.nr_pre ;
  if ( this.nr_yes > maxmax ) maxmax = this.nr_yes ;
  if ( this.nr_no > maxmax ) maxmax = this.nr_no ;
  for(var i=0; i<20; i++)
    if ( this.histogram[i] > maxmax ) maxmax = this.histogram[i] ;
  return maxmax ;
}

// The final \n is important : see update_tip_from_value
function stats_html_resume()
{
  return 'Min:&nbsp;' + this.min                 .toFixed(3) + '<br>' +
    'Max:&nbsp;'      + this.max                 .toFixed(3) + '<br>' +
    'Moy:&nbsp;<b>'   + this.average()           .toFixed(3) + '</b><br>' +
    'Méd:&nbsp;'      + this.mediane()           .toFixed(3) + '<br>' +
    'Var:&nbsp;'      + this.variance()          .toFixed(3) + '<br>' +
    'É-T:&nbsp;'      + this.standard_deviation().toFixed(3) + '<br>' +
    'Sum:&nbsp;'      + this.sum                 .toFixed(3) + '\n' ;
}

Stats.prototype.add = stats_add  ;
Stats.prototype.variance = stats_variance  ;
Stats.prototype.standard_deviation = stats_standard_deviation  ;
Stats.prototype.html_resume = stats_html_resume ;
Stats.prototype.average = stats_average ;
Stats.prototype.mediane = stats_mediane ;
Stats.prototype.maxmax = stats_maxmax ;

/******************************************************************************
 *
 *
 *
 * UE list displayer
 *
 *
 *
 *****************************************************************************/

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
  if ( confirm("Cette opération est irréversible.\nLes étudiants seront les mêmes pour l'automne et le printemps.\nVous êtes sûr de vouloir le faire ?") )
    {
      var year = the_year() ;
      if ( semester() == 'Automne')
	year++ ;

      document.getElementById('feedback').innerHTML =
	'<div class="frame"><div onclick="close_frame()">Fermer</div><iframe src="'
	+ base + year + '/Printemps/' + code + '/extension"></iframe></div>' ;
    }
}

function do_delete(ue_code)
{
  var code ;
  ue_line_close() ;
  if ( confirm("Cette DESTRUCTION est irréversible sauf pour l'administrateur TOMUSS.\nVous êtes sûr de vouloir le faire ?") )
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
	

      t += ue_line_more_links(code) ;

      var txt, n ;
      // UE Not in Printemps/Automne cannot be in favorites
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

      if ( code && ! code.match('.*/.*') && (
		    (semester() == 'Printemps' && is_the_current_semester())
		    || (semester() == 'Automne' && is_the_last_semester())
			))
	{
	  t +=  '<br><img class="safety" src="_URL_/unsafe.png"><a href="javascript:do_extension(\'' + code + '\');">Passer cette UE en NON-SEMESTRIALISÉE</a>' ;
	}

      if ( is_the_current_semester() || semester() == 'Test' )
	if ( code )
	  t +=  '<br><img class="safety" src="_URL_/unsafe.png"><a href="javascript:do_delete(\'' + code + '\');">Détruire cette table</a>' ;
	else
	  t +=  '<br><img class="safety" src="_URL_/unsafe.png"><a href="javascript:do_delete(\'' + (ue_line_over_last.childNodes[1].textContent || ue_line_over_last.childNodes[1].innerText) + '\');">Détruire cette table</a>' ;

  ue_line_over_plus.childNodes[1].style.display = 'block' ;
      ue_line_over_plus.childNodes[1].innerHTML = t ;
      ue_line_over_plus.childNodes[0].innerHTML = '&times;' ;
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
  if ( table_attr.mails[login] !== '' )
    send_mail = '<img class="safety" src="_URL_/verysafe.png"><a href="mailto:' + table_attr.mails[login]
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


function ue_line(with_students, code, content)
{
  var tt ;
  var c = code.substr(3).split('-')[0] ;
  if ( all_ues[c] && all_ues[c].tt )
    tt = hidden_txt('<img class="tt" src="tt.png">',
		    'Il y a au moins un étudiant inscrit dans cette UE<br>'
		    + 'avec un tiers temps') ;
  else
    tt = '' ;

  return '<tr' + with_students + ' onmouseover="ue_line_over(\'' + code + '\',this,ue_line_click_more);" onclick="javascript:go(\'' + code
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
	  t = ue_code + '\003\001???\002???' ;
	  t_upper = t ;
	}
      else
	{
	  t = ue.line.replace(/.*\003/, ue_code + '\003') ;
	  t_upper = ue.line_upper.replace(/.*\003/, ue_code + '\003') ;
	}
      t_replaced = check_and_replace(t, t_upper, txt, txt_upper) ;
      var with_students = '' ;
      
      if (ue && ue.nr_students_ue)
	with_students = ' class="with_students"' ;
      
      s.push(ue_line(with_students, ue_code,
		     t_replaced ? t_replaced : t)) ;
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
  for(var i in master_of)
    {
      i = master_of[i] ;
      var code = i[0] + '/' + i[1] + '/' + i[2] ;
      s.push('<tr onmouseover="ue_line_over(\'' + code + '\',this,ue_line_click_more);" '
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
  for(var i in ues_favorites)
    if ( ues_favorites[i] > 0 )
      ues_favorites_sorted.push(i) ;

  ues_favorites_sorted.sort(cmp_favorites) ;
  ues_favorites_sorted= ues_favorites_sorted.slice(0,preferences.nr_favorites);
  
  var s = ['<tr><th colspan="3">' +
	   hidden_txt('UE Favorites',
		      'Vous pouvez modifier cette liste en cliquant sur le <span class="ue_list_more_help">+</span>.<br>Le nombre de favoris est modifiable dans les préférences')
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
		      'Ce sont les UE pour lesquelles vous êtes<br>indiqué comme responsable dans la fiche SPIRAL')
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
	    s.push(ue_line('', ue.name, t_replaced)) ;
	}
      else
	{
	  var with_students = '' ;
	  if (ue.nr_students_ue)
	    with_students = ' class="with_students"' ;
	  
	  t_replaced = check_and_replace('UE-' + t, 'UE-' + t_upper,
					 txt, txt_upper) ;
	  if ( t_replaced !== undefined )
	    s.push(ue_line(with_students, 'UE-' + ue.name, t_replaced)) ;
	  if (ue.nr_students_ec)
	    {
	      t_replaced = check_and_replace('EC-' + t, 'EC-' + t_upper,
					     txt, txt_upper) ;
	      if ( t_replaced !== undefined )
		s.push(ue_line(with_students, 'EC-' + ue.name, t_replaced));
	    }
	}
      if ( s.length == 100 )
	{
	  s.push('<tr><td colspan="3">La liste a été tronquée.</td></tr>') ;
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
	'<div></div><div></div><div></div><div></div>' ;
    }

  ue_line_out() ;

  if ( txt === '' )
    txt = 'UNFOUNDABLETEXT\001' ;
  var txt_upper = replaceDiacritics(txt).toUpperCase() ;

  update_ues_searched(txt, txt_upper) ;
  update_ues_favorites(txt, txt_upper) ;
  update_ues_spiral(txt, txt_upper) ;
  update_ues_master_of(txt, txt_upper) ;
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

function student_line(i, hide_icon)
{
  table_attr.mails[i[0]] = i[3] ;
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
			'Étudiants favoris', 'javascript:go_favoris()') ;
}

function update_referent_of()
{
  if ( update_referent_of_done )
    return ;
  update_referent_of_done = true ;
  update_a_student_list('the_students', referent_of,
			'Étudiants référés', 'javascript:go_referent()') ;
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
      s.push(student_line(i)) ;
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

  the_students.innerHTML =
    '<table class="with_margin student_list">'
    + '<colgroup><col class="student_icon"><col class="student_id"><col></colgroup>'
    + '<tr><th colspan="3">' + student_list.length + ' ' +title + '<br><small>'
    + blocnote + '/' + mails + '/' + suivis + '</small></th></tr>'
    + s.join('\n') + '</table>' ;
}

var the_last_login_list ;
var the_last_login_asked ;
var last_login_cache = {} ;

function full_login_list(login, results)
{
  if ( ! document.getElementById('students_list') )
    {
      // We are in a table, not the home page
      login_list(login, results) ;
      return ;
    }

  var s = [], firstname, surname, icone ;

  if ( last_login_cache[login] === undefined )
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
  document.getElementById('students_list').innerHTML =
    '<table class="student_list" style="margin-top:0">'
    + '<colgroup><col class="student_icon"><col class="student_id"><col></colgroup>'
    + s.join('\n') + '</table>' ;
}


function update_students()
{
  var what = replaceDiacritics(document.getElementById('search_name').value) ;
  what = what.replace(/ *$/,'') ;
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
    
  var s = document.createElement('SCRIPT') ;
  s.src = base + 'login_list/' + encode_uri(what) ;
  document.getElementsByTagName('BODY')[0].appendChild(s) ;
  document.getElementById('students_list').innerHTML = 'Recherche en cours' ;
}

/******************************************************************************
 *
 *
 *
 *
 *
 *
 *****************************************************************************/


function Cell(value,author,date,comment,history)
{
  if ( value === undefined )
    {
      value = '' ;
      author = '' ;
      date = '' ;
      comment = '' ;
      history = '' ;
    }
  else if ( author === undefined )
    {
      author = '' ;
      date = '' ;
      comment = '' ;
      history = '' ;
    }
  else if ( date === undefined )
    {
      date = '' ;
      comment = '' ;
      history = '' ;
    }
  else if ( comment === undefined )
    {
      comment = '' ;
      history = '' ;
    }
  else if ( history === undefined )
    {
      history = '' ;
    }

  this.value = value ;
  this.author = author ;
  this.date = date ;
  this.comment = comment ;
  this.history = history ;
}

function cell_tostring()
{
  return 'C(v=' + this.value + ',a=' + this.author + ',d=' + this.date + ',c='
    + this.comment + ',h=' + this.history + ',k=' + this._key + ')' ;
}

function C(value,author,date,comment,history)
{
  return new Cell(value,author,date,comment,history) ;
}

function cell_save()
{
  this._save = this.value ;
}

function cell_restore()
{
  this.set_value(this._save) ;
}

function cell_value_html()
{
  return html(this.value) ;
}

function tofixed(n)
{
  return (Math.floor(n*100+0.0000001)/100).toFixed(2) ;
}

function tofixedlocal(n)
{
  return tofixed(n).replace('.',',') ;
}

function tofixedapogee(n)
{
  return n.toFixed(3).replace('.',',') ;
}


function cell_value_fixed()
{
  var v = Number(this.value) ;
  if ( isNaN(v) )
    return html(this.value) ;
  else
    if ( this.value === '' )
      return '' ;
    else
      return tofixed(v) ;
}

function cell_value_export()
{
  var xx = a_float(this.value) ;
  if ( isNaN(xx) )
    {
      xx = this.value.toString() ;
      switch(xx)
	{
	case 'NaN': return '' ;
	case abi: return 'ABI' ;
	case abj: return abjvalue ;
	case ppn: return ppnvalue ;
	default: return xx ;
	}
    }
  else
    return tofixedapogee(xx) ;
}


function cell_comment_html()
{
  return html(this.comment) ;
}

function cell_changeable(cell)
{
  if ( ! table_attr.modifiable )
    return "Cette table a été passée en lecture seulement par son responsable";
  if ( ! this.is_mine() )
    {
      if ( ! i_am_the_teacher )
	return "Vous n'avez pas le droit de modifier une valeur saisie par quelqu'un d'autre à moins d'être un responsable de l'UE" ;
      if ( this.author === '*')
	return "Cette valeur n'est pas modifiable car elle est officielle, si elle est fausse il faut prévenir un responsable" ;
    }
  return true ;
}

function cell_modifiable(cell)
{
  return this.changeable() === true ;
}

function cell_is_mine()
{
  return (this.author== my_identity|| this.author === '' || this.value === '');
}

function cell_set_value2(v)
{
  this.value = v ;
  this._key = undefined ;
}

function cell_set_weight(v)
{
  this.weight = v ;
}

function cell_set_comment(v)
{
  this.comment = v ;
}

function cell_is_not_empty()
{
  return this.value.toString() !== '' || this.comment !== '' ;
}

function cell_is_empty()
{
  return this.value.toString() === '' && this.comment === '' ;
}

function cell_never_modified()
{
  return this.author === '' ;
}

// Allow to sort correctly and intuitivly mixed data types
function cell_key()
{
  if ( this._key !== undefined )
    return this._key ;

  var x, date, s, i ;

  var v = this.value ;
  var n = a_float(v) ;
  if ( isNaN(n) )
    {
      if ( v.toLowerCase )
	this._key = '\003' + replaceDiacritics(v.toLowerCase()) ; // Strings
      else
	{
	  this._key = '\004' + v ; // NaN
	  return this._key ;
	}

      // Check date...
      date = v.split('/') ;
      if ( date.length == 3 )
	{
	  /* It seems like a date, french reverse order */
	  s = '' ;
	  for(i=0; i <3 ; i++)
	    {
	      x = Number(date[i].split(' ')[0]) ;
	      if ( isNaN(i) )
		{
		  break ;
		}
	      x = '0000' + x.toString() ;
	      s = x.substr(x.length-4) + s ;
	    }
	  if ( i == 3 )
	    // Should format hours (date[2] end) to be perfect
	    this._key = '\002' + s + date[2] ; // Dates
	  
	}
    }
  else
    {
      if ( v === '' )
	this._key = '\005' ;
      else
	{
	  // Number
	  n += 2000000000 ;
	  x = '           ' + n.toFixed(10) ;
	  this._key = '\001' + x.substr(x.length-23) ; // Numbers
	}
    }
  return this._key ;
}


Cell.prototype.save = cell_save ;
Cell.prototype.restore = cell_restore ;
Cell.prototype.value_html = cell_value_html ;
Cell.prototype.value_fixed = cell_value_fixed ;
Cell.prototype.value_export = cell_value_export ;
Cell.prototype.set_value = cell_set_value2 ;
Cell.prototype.set_weight = cell_set_weight ;
Cell.prototype.set_comment = cell_set_comment ;
Cell.prototype.comment_html = cell_comment_html ;
Cell.prototype.modifiable = cell_modifiable ;
Cell.prototype.changeable = cell_changeable ;
Cell.prototype.is_mine = cell_is_mine ;
Cell.prototype.key = cell_key ;
Cell.prototype.is_empty = cell_is_empty ;
Cell.prototype.is_not_empty = cell_is_not_empty ;
Cell.prototype.never_modified = cell_never_modified ;
Cell.prototype.toString = cell_tostring ;


/******************************************************************************
 *
 *
 *
 *
 *
 *
 *****************************************************************************/

function svg_rect(x, y, width, height, classe)
{
  var r = document.createElementNS("http://www.w3.org/2000/svg",'rect') ;
  r.setAttribute('x', x);
  r.setAttribute('y', y);
  if ( width < 0 )
    width = 0 ;
  r.setAttribute('width', width);
  r.setAttribute('height', height);
  if ( classe )
    r.setAttribute('class', classe);
  return r ;
}

function svg_text(text)
{
  var r = document.createElementNS("http://www.w3.org/2000/svg",'text') ;
  if ( r.textContent !== undefined )
     r.textContent = text ;
  else
     r.innerText = text ;
  return r ;
}

function histogram_bar(cls, x, dx, dy, maxmax, v, is_note, val_min, val_max,
		       container)
{
  var h = (dy*v) / maxmax ;

  if ( is_note )
    {
      label = (val_max - val_min) * cls / 20. + val_min ;
      if ( isNaN(label) )
	label = '' ;
      else
	if ( val_max - val_min >= 20 )
	  label = label.toFixed(0) ;
	else
	  label = label.toFixed(1) ;
    }
  else
    label = cls ;

  var r = svg_rect(x, dy - h, dx, h, 'a' + cls) ;
  container.appendChild(r) ;
  r = svg_text(label) ;
  r.setAttribute('transform', 'translate(' + (x+dx/1.5) + ',0),rotate(-90)');
  container.appendChild(r) ;
}

var update_histogram_data_col = -1 ;
var update_histogram_id ;
var svg_object, svg_style ;

function update_histogram_real()
{
  do_update_histogram = false ;
  if ( the_current_cell.data_col == update_histogram_data_col )
    return ;
  update_histogram_data_col = the_current_cell.data_col ;


  var dx = (t_column_histogram.offsetWidth-1) / 27 ;
  var dy = t_column_histogram.offsetHeight ;
  var font_size = Math.min( (dx/0.9).toFixed(0), (dy/2.4).toFixed(0) ) ;
  var the_style =
    'rect { stroke: #000 ; stroke-opacity: 0.5 ; stroke-width:1 }' +
    '.a0, .a1, .a2, .a3, .a4 { fill: #F00 }' +
    '.a5, .a6, .a7, .a8, .a9 { fill: #FA0 }' +
    '.a10, .a11, .a12, .a13, .a14 { fill: #AFA }' +
    '.a15, .a16, .a17, .a18, .a19 { fill: #0F0 }' +
    '.appn { fill: #F8F }' +
    '.anan { fill: #FFF }' +
    '.aabi { fill: #F88 }' +
    '.aabj { fill: #88F }' +
    '.apre { fill: #8F8 }' +
    '.aoui { fill: #8FF }' +
    '.anon  { fill: #FF8 }' +
    'text { text-anchor:end; font-size:' + font_size + 'px; }' ;
  var stats = compute_histogram(the_current_cell.data_col) ;
  var i ;
  var maxmax = stats.maxmax() ;
  var s = '' ;

  if ( ! svg_object )
    {
      var d ;
      try
	{
	  d = document.createElementNS("http://www.w3.org/2000/svg",
					   'svg');
	}
      catch(err)
	{
	  return ;
	}
      t_column_histogram.appendChild(d) ;
      svg_style=document.createElementNS("http://www.w3.org/2000/svg",'style');
      d.appendChild(svg_style) ;
      svg_object = document.createElementNS("http://www.w3.org/2000/svg", 'g');
      d.appendChild(svg_object) ;
    }
  if ( svg_style.textContent !== undefined )
     svg_style.textContent = the_style ;
  else
     svg_style.innerText = the_style ;

  while ( svg_object.firstChild )
    svg_object.removeChild(svg_object.firstChild) ;

  s+= histogram_bar('ppn',0*dx,dx,dy,maxmax,stats.nr_ppn,false,0,0,svg_object);
  s+= histogram_bar('abi',1*dx,dx,dy,maxmax,stats.nr_abi,false,0,0,svg_object);
  s+= histogram_bar('abj',2*dx,dx,dy,maxmax,stats.nr_abj,false,0,0,svg_object);
  s+= histogram_bar('pre',3*dx,dx,dy,maxmax,stats.nr_pre,false,0,0,svg_object);
  s+= histogram_bar('oui',4*dx,dx,dy,maxmax,stats.nr_yes,false,0,0,svg_object);
  s+= histogram_bar('non',5*dx,dx,dy,maxmax,stats.nr_no ,false,0,0,svg_object);
  s+= histogram_bar('nan',6*dx,dx,dy,maxmax,stats.nr_nan,false,0,0,svg_object);

  for(i=0; i<20; i++)
    s += histogram_bar(i, (i+7)*dx, dx, dy, maxmax, stats.histogram[i],
		       the_current_cell.column.real_type.should_be_a_float,
		       the_current_cell.column.min,
		       the_current_cell.column.max,
		       svg_object
		       ) ;

  i = stats.average() ;
  if ( i > 1 )
    i = i.toFixed(1) ;
  else
    i = i.toFixed(2) ;
  t_column_average.innerHTML = i ;
  update_tip_from_value(t_column_average,
			stats.nr + ' valeurs<br>' + stats.html_resume()) ;

  t = "Vide (ou inclassable) : " + stats.nr_nan + '<br>' ;
  if ( stats.nr_ppn ) t += "Peut Pas Noter : " + stats.nr_ppn + '<br>' ;
  if ( stats.nr_abi ) t += "ABI : " + stats.nr_abi + '<br>' ;
  if ( stats.nr_abj ) t += "ABJ : " + stats.nr_abj + '<br>' ;
  if ( stats.nr_pre ) t += "Présent : " + stats.nr_pre + '<br>' ;
  if ( stats.nr_yes ) t += "OUI : " + stats.nr_yes + '<br>' ;
  if ( stats.nr_no  ) t += "NON : " + stats.nr_no + '<br>' ;
  if ( stats.nr )     t += "Notes : " + stats.nr + '<br>' ;

  // + '\n' : explanation in update_tip_from_value
  update_tip_from_value(t_column_histogram, t + '\n') ;
}

function update_histogram(force)
{
  if ( t_column_histogram === undefined )
    return ;
  if ( force )
    update_histogram_data_col = -1 ;

  if ( update_histogram_id )
    clearTimeout(update_histogram_id) ;

  update_histogram_id = setTimeout(update_histogram_real, 300) ;
}

function Current()
{
  this.input = document.getElementById('current_input') ;
  this.input_div = document.getElementById('current_input_div') ;
  this.lin = nr_headers ;
  this.col = 0 ;
  this.data_lin = 0 ;
  this.data_col = 0 ;
}


if ( navigator.appName == 'Opera' )
  var set_editable = function() { } ;
else
  var set_editable = function(item, editable){
    if (  item.selectedIndex === undefined ) // XXX: FireFox bug
      item.contentEditable = editable;
    item.tomuss_editable = editable ;
    // item.disabled = ! editable ; // No more tip on unsensitives
  };

// Update ALL the columns headers saw by the user.
function current_update_column_headers()
{
  if ( this.do_update_column_headers == false )
    return ;
  this.do_update_column_headers = false ;

  var column = this.column ;
  var disabled = ! table_attr.modifiable || ! column_change_allowed(column) ;
  var e, help ;

  for(var attr in column_attributes)
    {
      e = document.getElementById('t_column_' + attr) ;
      if ( ! e )
	continue ;
      if ( column_attributes[attr].computed )
	{
	  update_value_and_tip(e,
			       column_attributes[attr].formatter(column,
								 column[attr])
			       ) ;
	  continue ;
	}
      if ( column.real_type['set_' + attr] == unmodifiable )
	{
	  e.parentNode.style.display = 'none' ;
	  continue ;
	}
      e.parentNode.style.display = '' ;
      if ( attr == 'type' )
	{
	  e.selectedIndex = column.real_type.index ;
	  // e.value = column.type ;
	  // highlight_add(e) ; // Why is it necessary ?
	}
      else
	{
	  update_input(e,
		       column_attributes[attr].formatter(column, column[attr]),
		       column_attributes[attr].empty(column, column[attr])
		       ) ;
	}

      set_editable(e, !column_attributes[attr].need_authorization
		   || !disabled) ;

      e = tip_top(e) ;
      // alert(e.innerHTML + '\n\n' + column.real_type['tip_' + attr]);
      // All the tests are for the 'author' column attribute
      // It does not work with IE.
      if ( e )
	{
	  help = column.real_type['tip_' + attr] ;
	  if ( help )
	    e.firstChild.firstChild.innerHTML = help ;
	}
    }

  if ( t_column_histogram )
    {
      if ( true )
	{
	  t_column_histogram.style.display = '' ;
	  t_column_average.style.display = '' ;
	  update_histogram() ;
	}
      else
	{
	  t_column_histogram.style.display = 'none' ;
	  t_column_average.style.display = 'none' ;
	}
    }
  var v ;
  if ( column.freezed )
    v = 'Défige' ;
  else
    v = 'Fige' ;
  if (t_column_fixed.innerHTML != v )
    {
      t_column_fixed.innerHTML = v ;
      highlight_add(t_column_fixed) ;
    }
}

function current_update_cell_headers()
{
  var cell = this.cell ;

  if ( the_comment )
    {
      update_input(the_comment, cell.comment, cell.comment === '') ;
      set_editable(the_comment, cell.modifiable()) ;
    }

  update_value_and_tip(t_value, cell.value) ;
  update_value_and_tip(t_history, cell.history) ;
  update_value_and_tip(t_date, date(cell.date)) ;
  if ( cell.author )
    update_value_and_tip(t_author, cell.author) ;
  else
    update_value_and_tip(t_author, '.') ;
  update_tip_from_value(t_student_picture.parentNode,
			line_resume(this.data_lin), '') ;
}

function current_update_table_headers()
{
  var disabled = ! table_change_allowed() || ! table_attr.modifiable ;

  for(var attr in table_attributes)
    {
      var attributes = table_attributes[attr] ;
      e = document.getElementById('t_table_attr_' + attr) ;
      if ( ! e )
	continue ;
      if ( attributes.only_masters
	   && ! ( i_am_the_teacher || myindex(root, my_identity) != -1 )
	   )
	e.style.display = 'none' ;
      else
	e.style.display = '' ;

      if ( e.selectedIndex !== undefined )
	e.selectedIndex = Number(table_attr[attr]) ;
      else
	if ( e.tagName == 'INPUT' )
	  update_input(e,
		       attributes.formatter(table_attr[attr]),
		       attributes.empty(table_attr[attr])
		       ) ;
	else
	  e.innerHTML = attributes.formatter(table_attr[attr]) ;
      if ( attr == 'modifiable' )
	set_editable(e, table_change_allowed()) ;
      else
	set_editable(e, !attributes.need_authorization || !disabled) ;
    }
}

function current_update_headers_real()
{
  var img ;

  this.do_update_headers = false ;
  if ( author )
    author.innerHTML = this.cell.author ;
  if ( modification_date )
    modification_date.innerHTML = date(this.cell.date) ;

  tip.style.display = "none" ;
  update_student_information(this.line) ;
  this.update_cell_headers() ;
  this.update_column_headers() ;

  var s_abjs = student_abjs(this.line[0].value) ;
  if ( s_abjs !== "")
    {
      tip.innerHTML = student_abjs(this.line[0].value) ;     
      tip.style.display = "block" ;
      set_tip_position(this.td) ;
    }
  else
    tip.style.display = "none" ;

  // Remove green square from top menu
  var t = t_menutop.getElementsByTagName('IMG') ;
  for(img in t)
    {
      img = t[img] ;
      if ( img && img.request && img.request.saved )
	img.parentNode.removeChild(img) ;
    }
}

function current_update_headers()
{
  this.do_update_headers = true ;
}

function current_jump(lin, col, do_not_focus, data_lin, data_col)
{
  if ( data_col === undefined )
    data_col = data_col_from_col(col) ;
  if ( data_lin === undefined )
    data_lin = data_lin_from_lin(lin) ;

  var line = lines[data_lin] ;
  if ( ! line )
    {
      alert('BUG current jump:' + data_lin) ;
    }

  var cell = line[data_col] ;

  if ( ! do_not_focus && element_focused && element_focused.tagName == 'INPUT')
    {
      // Save value before changing of current cell
      var save = element_focused ;
      save.blur() ;
      if ( save.onblur )
	{
	  save.onblur(save) ;
	}
      if ( ! cell.modifiable() )
	{
	  save.focus() ;
	  if ( element_focused === undefined )
	    {
	      save.onfocus() ;
	    }
	}
    }

  /* Removed the 19/1/2010 In order to select RO values
  if (  ! cell.modifiable() )
    do_not_focus = true ;
  */

  this.lin = lin ;
  this.previous_col = this.col ;
  this.col = col ;
  this.tr = table.childNodes[lin] ;
  remove_highlight() ;
  the_current_line = this.tr ;
  this.tr.className += ' highlight' ;
  this.td = this.tr.childNodes[col] ;
  if ( data_col != this.data_col )
    this.do_update_column_headers = true ;
  this.data_col = data_col ;
  this.column = columns[this.data_col] ;
  this.previous_data_lin = this.data_lin ;
  this.data_lin = data_lin ;
  this.line = line ;
  this.cell = cell ;

  var pos = findPos(this.td) ;
  var border ;
  if ( this.tr.className.indexOf('separator') != -1 )
    border = 1 ;
  else
    border = 0 ;

  // Nicer display with this, but focus loss on horizontal scrolling
  //this.input_div.style.display = 'none' ;
  this.input_div.style.left = pos[0] - 3 ;
  this.input_div.style.top = pos[1] - 3 + border ;
  this.input_div.style.width = this.td.offsetWidth ;
  this.input_div.style.height = this.td.offsetHeight - border ;

  this.input.className = this.td.className + ' ' + this.tr.className ;

  // message.innerHTML += '('; // XXX
  this.input.value = columns[this.data_col].real_type.formatte(this.cell.value);
  // message.innerHTML += ')';
  this.initial_value = this.input.value ;

  // Update position in scrollbar
  if ( vertical_scrollbar && this.previous_data_lin != this.data_lin )
    update_vertical_scrollbar_cursor() ;
  if ( horizontal_scrollbar && this.previous_col != this.col )
    update_horizontal_scrollbar_cursor() ;

  //this.input_div.style.display = '' ;

  if ( ! do_not_focus )
    {
      // If focus is done immediatly, the middle button paste
      // insert HTML source into the <div> element !
      // This is a firefox bug (see next comment)
      // The next line is not good : fast input garbaged on non empty cell
      // setTimeout("the_current_cell.focus() ;", 1) ;

      // DO NOT REMOVE THE STRING TO PASS THE FUNCTION.
      // IT WILL BREAK THINGS BECAUSE IT IS NO MORE A METHOD BUT A FUNCTION
      setTimeout('the_current_cell.focus()',100) ; // Opera
      the_current_cell.focus() ;
    }
  this.update_headers() ; //this.previous_col == this.col) ;

  // Remove a copy bug of Firefox that insert tag when copying
  while( this.input_div.firstChild.tagName != 'INPUT' )
    this.input_div.removeChild(this.input_div.firstChild) ;
}

function current_focus()
{
  //this.input.contentEditable = this.cell.modifiable() ;
  this.input.focus() ;
  if ( this.input.select )
    this.input.select() ;
}

// Update input from real table content (external change)
function current_update(do_not_focus)
{
  var lin, col ;

  lin = this.lin ;
  col = this.col ;

  if ( lin >= nr_lines + nr_headers )
    lin = nr_lines + nr_headers - 1 ;
  if ( col >= nr_cols - 1 )
    col = nr_cols - 1 ;

  this.jump(lin, col, do_not_focus) ;
}

function current_cursor_down()
{
  this.change() ;
  if ( this.lin == nr_lines + nr_headers - 1 )
    {
      next_page(true) ;
      table_fill_try() ; // Want change NOW (bad input if fast typing)
    }
  else
    this.jump(this.lin + 1, this.col) ;
}

function current_cursor_up()
{
  this.change() ;
  if ( this.lin == nr_headers )
    {
      if ( line_offset !== 0 )
	{
	  previous_page(true) ;
	  table_fill_try() ; // Want change NOW (bad input if fast typing)
	}
    }
  else
    this.jump(this.lin - 1, this.col) ;
}

function current_cursor_right()
{
  this.change() ;

  if ( this.col == nr_cols - 1 )
    next_page_horizontal() ;
  else
    this.jump(this.lin, this.col + 1) ;
}

function current_cursor_left()
{
  this.change() ;
  if ( this.col === 0 || ( column_offset !== 0 && this.col == nr_freezed() ) )
    previous_page_horizontal() ;
  else
    this.jump(this.lin, this.col - 1) ;  
}

function alt_shortcut(event, td)
{
  switch(event.charCode)
    {
    case 38: /* AZERTY: 1/& */
    case 49: /* QWERTY: 1/! */
      toggle_display_tips() ;
      break ;

    case 233: /* AZERTY: 2/é */
    case 50:  /* QWERTY: 2/@ */
      // toggle_display_picture() ;
      break ;

    case 34:  /* AZERTY: 3/" */
    case 222: /* AZERTY: 3/" */
    case 51:  /* QWERTY: 3/# */
      the_comment.focus() ;
      break ;

    case 39:  /* AZERTY: 4/' */
    case 52:  /* QWERTY: 4/$ */
      freeze_column() ;
      break ;

      //  case 68:
      //  case 100:
    case 40:  /* AZERTY: 5/( */
    case 53:  /* QWERTY: 5/% */
      hide_column() ;
      break ;

    case 45:  /* AZERTY: 6/- */
    case 54:  /* QWERTY: 6/^ */
      do_move_column_left() ;
      break ;

    case 232: /* AZERTY: 7/è */
    case 55:  /* QWERTY: 7/& */
      do_move_column_right() ;
      break ;

    case 109: /* AZERTY: 8/_ */
    case 95:  /* AZERTY: 8/_ */
    case 56:  /* QWERTY: 8/ * */
      linefilter.focus() ;
      if (linefilter.select)
	linefilter.select();
      break;

    case 231: /* AZERTY: 9/ç */
    case 57:  /* QWERTY: 9/( */
      smaller_column() ;
      break ;

    case 224: /* AZERTY: 0/à */
    case 48:  /* QWERTY: 0/) */
      bigger_column() ;
      break ;

    case 16:
    case 18:
    case 0:
      break ;
    default:
	return true ;
    }


  stop_event(event) ; // Else ALTs are navigator shortcut
  return false ;
}

function current_keydown(event, in_input)
{
  if ( element_focused && element_focused.tagName == 'TEXTAREA' )
    return ;

  event = the_event(event) ;
  var key = event.keyCode ;

  if ( popup_is_open() )
    {
      if ( key == 27 )
	popup_close() ;
      return ;
    }

  if ( ! element_focused )
    this.focused = true ; // this is in fact 'current_cell'

  if ( event.altKey && ! event.ctrlKey )
    {
      if ( event.charCode === undefined )
	{
	  // IE case
	  event.charCode = event.keyCode ;
	  alt_shortcut(event, this.td) ;
	  stop_event(event) ;
	  return false ;
	}
      return ;
    }
  if ( in_input )
    {
      // Manage only left and right
      if ( key != 37  && key != 39 )
	return ;
    }
  else
    {
      // Do not manage left and right cursor if an <input> is focused
      if ( element_focused )
	{
	  if (key == 37  || key == 39)
	    return ;
	  if ( element_focused.tagName == 'TEXTAREA' )
	    return ;
	}
    }

  // __d('alt=' + event.altKey + ' ctrl=' + event.ctrlKey + ' key=' + key + ' charcode=' + event.charCode + ' which=' + event.real_event.which + '\n') ;

  switch(key)
    {
    case 40: this.cursor_down() ; break ;
    case 13: this.cursor_down() ; break ;
    case 38: this.cursor_up()   ; break ;
    case 34: next_page()        ; break ;
    case 33: previous_page()    ; break ;
    case 37:
      if ( event.ctrlKey
	   || this.input.value.length === 0
	   || !this.cell.modifiable()
	   || ((this.input.selectionEnd === this.input.textLength ||
		this.input.selectionEnd === this.input.value.length ||
	       this.input.selectionEnd === 0)
	       && this.input.selectionStart === 0)
	   )
	this.cursor_left() ;
      else
	return true ;
      break ;
    case 9:
      if ( event.shiftKey )
	  this.cursor_left() ;
      else
	  this.cursor_right() ;
      break ;
    case 39:
      if ( event.ctrlKey
	   || this.input.value.length === 0
	   || !this.cell.modifiable()
	   || (this.input.selectionEnd !== undefined
	       && (this.input.textLength == this.input.selectionEnd
		   || this.input.value.length == this.input.selectionEnd
		   )
	       )
	   )
	this.cursor_right() ;
      else
	return true ;
      break ;
    case 27: // Escape Key
      //alert('' + this.input.value + '/' + this.initial_value) ;
      this.input.value = this.initial_value ;
      this.input.blur() ;
      this.input.focus() ;
      break ;
    default:
      if ( ! this.cell.modifiable() )
	{
	  if ( event.ctrlKey === false && element_focused === undefined )
	    {
	      // We don't want to allow cell content modification
	      // XXX : Should not allow ^X and ^V
	      // Added the 2009-06-22
	      stop_event(event) ;
	      return false ;
	    }
	}
      return true ;
    }
  stop_event(event) ;
  return false ;
}

/* For Opera, to stop next/previous page */
/* For Opera, to stop ctrl left/right page */
function current_keypress(event)
{
  if ( popup_is_open() )
    return ;

  event = the_event(event) ;
  /*
  if ( this.column.type == 'Login' )
    {
      if ( this.input.value.length > 4 )
	ask_login_list = this.input.value ; // A thread will read it
    }
  */
  if ( event.altKey || event.metaKey  )
    {
      if ( ! event.ctrlKey ) // Alt Gr Key on FireFox/Window XP
	{
	  return false ;

	  alt_shortcut(event, this.td) ;
	  stop_event(event) ;
	  return false ;
	}
    }

  if ( event.altKey !== true && event.shiftKey !== true
       && event.ctrlKey !== true )
    {
      if ( event.keyCode == 33 || event.keyCode == 34
	   // This line block up/down cursor in TEXTAREA
	   || ( (event.keyCode == 38 || event.keyCode == 40)
		&& event.target.tagName == 'INPUT' ) 
	   )
	{
	  stop_event(event) ;
	  return false ;
	}
    }
  return true ;
}


var current_change_running = false ;

function current_change()
{
  if ( this.blur_disabled )
    return ;

  // Save modification in header before moving.
  if ( element_focused !== undefined )
    {
      if ( element_focused.blur )
	element_focused.blur() ;
    }

  if ( this.input.value == this.initial_value )
    return ;

  // Because the function can popup an alert that remove focus from cell
  // This function must be ran only once
  if ( current_change_running )
    return ;

  var value = this.input.value.replace(/^[ \t]*/,'').replace(/[ \t]*$/,'') ;
  if ( value == this.initial_value )
    return ;


  current_change_running = true ;

  // XXX This test should in the template.
  if ( semester == 'Printemps' || semester == 'Automne' )
    {
      if ( this.data_col === 0 )
	{
	  /* Verify ID */
	  if ( value !== '' )
	    if ( login_to_line(value) !== undefined )
	      {
		alert("Ce numéro d'étudiant existe déjà !") ;
		this.input.value = this.initial_value ;
		current_change_running = false ;
		return ;
	      }
	}
      else
	if ( this.data_col !== 0 && lines[this.data_lin][0].is_empty()
	     && value !== '' )
	  {
	    alert("Vous devez impérativement saisir un numéro d'étudiant") ;
	  }
      if ( value !== ''
	   && ! modification_allowed_on_this_line(this.data_lin,this.data_col))
	{	    
	  this.input.value = this.initial_value ;
	  current_change_running = false ;
	  return ;
	}
    }
  this.input.blur() ; // If have focus : problem with page change
  this.input.value = cell_set_value(this.td, value,
				    this.data_lin, this.data_col) ;
  this.initial_value = this.input.value ;

  update_line(this.data_lin, this.data_col) ;
  current_change_running = false ;
}

function current_toggle()
{
  if ( this.td.className.search('ro') != -1 && this.column.type != 'URL' )
    return ;

  var toggle = this.column.real_type.ondoubleclick ;
  if ( toggle === undefined )
    {
      return ;
    }
  this.input.value = toggle(this.input.value) ;
  this.change() ;
  this.update() ;
}

Current.prototype.jump                  = current_jump                  ;
Current.prototype.change                = current_change                ;
Current.prototype.keydown               = current_keydown               ;
Current.prototype.keypress              = current_keypress              ;
Current.prototype.update                = current_update                ;
Current.prototype.cursor_down           = current_cursor_down           ;
Current.prototype.cursor_up             = current_cursor_up             ;
Current.prototype.cursor_left           = current_cursor_left           ;
Current.prototype.cursor_right          = current_cursor_right          ;
Current.prototype.focus                 = current_focus                 ;
Current.prototype.toggle                = current_toggle                ;
Current.prototype.update_headers        = current_update_headers        ;
Current.prototype.update_headers_real   = current_update_headers_real   ;
Current.prototype.update_cell_headers   = current_update_cell_headers   ;
Current.prototype.update_column_headers = current_update_column_headers ;
Current.prototype.update_table_headers  = current_update_table_headers  ;






