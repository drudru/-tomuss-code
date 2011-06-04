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

function scrollLeft()
{
  if ( document.body.scrollLeft !== undefined )
    return document.body.scrollLeft ;
  return window.screenX ;
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

var base64_replace = "%\r\n!#$&'()*+/[\\]^`\"<>" ;

function base64(s)
{
  var i, len ;
  /* Bad for SVG with diacritics
     for(i = 128 ; i < 256 ; i++)
     replace += String.fromCharCode(i) ;
  */
  len = base64_replace.length ;
  for(i=0; i<len; i++)
    {
      var code = base64_replace.charCodeAt(i) ;
      s = s.replace(RegExp('\\' + base64_replace.substr(i,1), 'g'),
		    '%' +
		    '0123456789ABCDEF'.charAt(code/16) +
		    '0123456789ABCDEF'.charAt(code%16)
		    ) ;
    }
  return s ;
}

function base64_decode(s)
{
  var i, len ;
  len = base64_replace.length ;
  for(i=len-1; i>=0; i--)
    {
      var code = base64_replace.charCodeAt(i) ;
      s = s.replace(RegExp('%' +
			   '0123456789ABCDEF'.charAt(code/16) +
			   '0123456789ABCDEF'.charAt(code%16),
			   'g'),
		    base64_replace.substr(i,1)
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

function mailto_url_usable(mails)
{
  if ( mails.length < max_url_length || ! on_windows() )
    return true ;
  return false ;
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

  if ( display === undefined && mailto_url_usable(mails) )
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
    return  '_URL_/=' + ticket + '/picture/' + login_to_id(login) + '.JPG' ;
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
  this.sum = 0 ;
  this.sum2 = 0 ;
  this.nr = 0 ;
  this.histogram = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] ;
  this.v_min = v_min ;
  this.v_max = v_max ;
  this.size = v_max - v_min ;
  this.values = [] ; // numeric ones
  this.all_values = {} ;
  this.all_values[abi] = 0 ;
  this.all_values[abj] = 0 ;
  this.all_values[pre] = 0 ;
  this.all_values[ppn] = 0 ;
  this.all_values[yes] = 0 ;
  this.all_values[no] = 0 ;
  this.all_values[''] = 0 ;
  if ( empty_is )
    this.empty_is = empty_is ;
  else
    this.empty_is = '' ;    
}

// This function does not works when merging things with not the same size
function stats_merge(v)
{
  var value ;
  this.min = Math.min(this.min, v.min) ;
  this.max = Math.max(this.max, v.max) ;
  this.nr += v.nr ;
  for(var i in this.histogram)
    this.histogram[i] += v.histogram[i] ;
  for(var i in v.values)
    {
      value = this.v_min + this.size * (v.values[i] - v.v_min)/v.size ;
      this.values.push(value) ;
      this.sum += value ;
      this.sum2 += value * value ;
    }
  for(var i in v.all_values)
    if ( this.all_values[i] )
      this.all_values[i] += v.all_values[i] ;
    else
      this.all_values[i] = v.all_values[i] ;
}

function stats_add(v)
{
  if ( v === '' )
    v = this.empty_is ;
  if ( this.all_values[v] )
    this.all_values[v]++ ;      
  else
    this.all_values[v] = 1 ; 
  if ( v === '' )
    return ;
  v = a_float(v) ;
  if ( isNaN(v) )
    return ;
  delete this.all_values[v] ;
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
  return Math.pow(this.variance(), 0.5) ;
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

function stats_uniques()
{
  var d = {} ;
  for(var i in this.values)
    if ( d[this.values[i]] )
      d[this.values[i]]++ ;
    else
      d[this.values[i]] = 1 ;
  for(var i in this.all_values)
    if ( d[this.all_values[i]] )
      d[i] += this.all_values[i] ;
    else
      d[i] = this.all_values[i] ;
  return d ;
}

function stats_nr_uniques()
{
  var d = this.uniques() ;
  var j = 0 ;
  for(var i in d)
    if ( d[i] )
      j++ ;

  return j ;
}
function stats_histo_max()
{
  var maxmax = 1 ;
  for(var i=0; i<20; i++)
    if ( this.histogram[i] > maxmax ) maxmax = this.histogram[i] ;
  return maxmax ;
}

function stats_maxmax()
{
  var maxmax = this.histo_max() ;
  for(var i in this.all_values)
    if ( this.all_values[i] > maxmax ) maxmax = this.all_values[i] ;
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

function stats_normalized_average()
{
  return (this.average() - this.v_min) / this.size ;
}

Stats.prototype.add = stats_add  ;
Stats.prototype.variance = stats_variance  ;
Stats.prototype.standard_deviation = stats_standard_deviation  ;
Stats.prototype.html_resume = stats_html_resume ;
Stats.prototype.average = stats_average ;
Stats.prototype.mediane = stats_mediane ;
Stats.prototype.maxmax = stats_maxmax ;
Stats.prototype.histo_max = stats_histo_max ;
Stats.prototype.merge = stats_merge ;
Stats.prototype.uniques = stats_uniques ;
Stats.prototype.nr_uniques = stats_nr_uniques ;
Stats.prototype.nr_abi = function() { return this.all_values[abi] ; } ;
Stats.prototype.nr_abj = function() { return this.all_values[abj] ; } ;
Stats.prototype.nr_ppn = function() { return this.all_values[ppn] ; } ;
Stats.prototype.nr_nan = function() { return this.all_values[''] ; } ;
Stats.prototype.nr_pre = function() { return this.all_values[pre] ; } ;
Stats.prototype.nr_yes = function() { return this.all_values[yes] ; } ;
Stats.prototype.nr_no  = function() { return this.all_values[no] ; } ;
Stats.prototype.normalized_average = stats_normalized_average ;


/*
 * The selection functions came from :
 * http://stackoverflow.com/questions/401593/javascript-textarea-selection/403526#403526
 */

function get_selection(e)
{
    //Mozilla and DOM 3.0
    if('selectionStart' in e)
    {
        var l = e.selectionEnd - e.selectionStart;
        return { start: e.selectionStart,
                   end: e.selectionEnd,
                length: l,
                  text: e.value.substr(e.selectionStart, l) };
    }
    //IE
    else if(document.selection)
    {
        e.focus();
        var r = document.selection.createRange();
        var tr = e.createTextRange();
        var tr2 = tr.duplicate();
        tr2.moveToBookmark(r.getBookmark());
        tr.setEndPoint('EndToStart', tr2);
        if (r == null || tr == null)
	  return { start: e.value.length,
                     end: e.value.length,
                  length: 0,
                    text: '' };
	//for some reason IE doesn't always count the \n and \r in the length
        var text_part = r.text.replace(/[\r\n]/g, '.');
        var text_whole = e.value.replace(/[\r\n]/g, '.');
        var the_start = text_whole.indexOf(text_part, tr.text.length);
        return { start: the_start,
                   end: the_start + text_part.length,
                length: text_part.length,
                  text: r.text };
    }
    //Browser not supported
    else return { start: e.value.length,
                    end: e.value.length,
                 length: 0, text: '' };
}

function replace_selection(e, replace_str)
{
    selection = get_selection(e);
    var start_pos = selection.start;
    var end_pos = start_pos + replace_str.length;
    e.value = e.value.substr(0, start_pos) + replace_str
              + e.value.substr(selection.end, e.value.length);
    set_selection(e, start_pos, end_pos);
    return {start: start_pos,
              end: end_pos,
           length: replace_str.length,
             text: replace_str};
}

function set_selection(e, start_pos, end_pos)
{
    //Mozilla and DOM 3.0
    if('selectionStart' in e)
    {
        e.focus();
        e.selectionStart = start_pos;
        e.selectionEnd = end_pos;
    }
    //IE
    else if(document.selection)
    {
      var i ;
      e.focus();
      var tr = e.createTextRange();
      tr.moveEnd('textedit', -1);
      tr.moveStart('character', start_pos);
      tr.moveEnd('character', end_pos - start_pos);
      tr.select();
    }
    return get_selection(e);
}

function wrap_selection(e, left_str, right_str, sel_offset, sel_length)
{
    var the_sel_text = get_selection(e).text;
    var selection =  replace_selection(e, left_str + the_sel_text + right_str);
    if(sel_offset !== undefined && sel_length !== undefined)
      selection = set_selection(e, selection.start + sel_offset,
				selection.start + sel_offset + sel_length);
    else
      if(the_sel_text == '')
	selection = set_selection(e, selection.start + left_str.length,
				  selection.start + left_str.length);
    return selection;
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

function js(t)
{
  return '"' + t.toString().replace(/\\/g,'\\\\')
    .replace(/"/g,'\\"').replace(/\n/g,'\\n')
    + '"' ;
}

function js2(t)
{
  return "'" + t.toString().replace(/\\/g,'\\\\')
    .replace(/'/g,"\\'").replace(/\n/g,'\\n')
    + "'" ;
}

function cell_get_data()
{
  var v ;
  if ( this.value.toFixed )
    v = this.value ;
  else
    v = js(this.value) ;
  return 'C(' + v + ',' + js(this.author) + ',' + js(this.date) + ',' + js(this.comment) + ')' ;
}

Cell.prototype.save = cell_save ;
Cell.prototype.get_data = cell_get_data ;
Cell.prototype.restore = cell_restore ;
Cell.prototype.value_html = cell_value_html ;
Cell.prototype.value_fixed = cell_value_fixed ;
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

function set_select_by_value(element, value)
{
  var options = element.getElementsByTagName('OPTION') ;
  for(var i in options)
    {
      if ( options[i].value == value || options[i].text == value )
	{
	  element.selectedIndex = i ;
	  return ;
	}
    }
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
       item.contentEditable = !!editable;
     item.tomuss_editable = !!editable ;
     // item.disabled = ! editable ; // No more tip on unsensitives
   };

function update_attribute_value(e, attr, table, editable)
{
  var value = table[attr.name] ;
  var formatted ;

  if ( value === undefined )
    return ;

  if ( attr.what == 'table' )
    formatted = attr.formatter(value) ;
  else
    formatted = attr.formatter(table, value) ;

  switch(e.tagName)
    {
    case 'SELECT':
      set_select_by_value(e, value) ;
      break ;
    case 'INPUT':
      if ( e.type != 'button' )
	{
	  if ( attr.what == 'table' )
	    update_input(e, formatted, attr.empty(value)) ;
	  else
	    update_input(e, formatted, attr.empty(table, value)) ;

	  // XXX In some case 'the_current_cell.column' is undefined
	  if ( the_current_cell.column && attr.tip[the_current_cell.column.type] )
	    tip_top(e).firstChild.innerHTML = attr.tip[the_current_cell.column.type] ;
	}
      break ;
    case 'A':
      var x = e.className.replace('linkstroked', '') ;
      var old_class = e.className ;
      if ( ! value && attr.strokable )
	x += ' linkstroked' ;
      if ( !!value != (old_class.search('linkstroked') == -1) )
	{
	  highlight_add(e) ;
	  // Classname change must be done before 'highlight_add'
	  // And 'highlight_add' should not erase classname
	  // But if classname is not erased, it brokes thing
	  // when there is 'empty' class
	  x += ' highlight1' ;
	}
      e.className = x.replace(/^ */,'') ;

      if ( attr.tip.toLowerCase === undefined )
	{
	  var tip ;
	  if ( e.className.search('linkstroked') == -1 )
	    tip = attr.tip[1] ;
	  else
	    tip = attr.tip[0] ;
	  if ( i_am_root )
	    tip += '<hr><b>' + e.id + '</b>' ;
	  tip_top(e).firstChild.innerHTML = tip ;
	}
      return ;
    default:
      return ;
    }
  set_editable(e, editable) ;
}

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
	  if ( e.tagName == 'INPUT' || e.tagName == 'SPAN' ) // XXX
	    update_value_and_tip(e,
				 column_attributes[attr].formatter(column,
								   column[attr]
								   )) ;
	  continue ;
	}
      if ( ! column_modifiable_attr(attr, column) )
	{
	  e.parentNode.style.display = 'none' ;
	  continue ;
	}
      if ( column_attributes[attr].gui_display == 'GUI_none' )
	eval(column_attributes[attr].action + '()') ;
      e.parentNode.style.display = '' ;
      update_attribute_value(e, column_attributes[attr], column,
			     !column_attributes[attr].need_authorization
			     || !disabled) ;
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
  var disabled ;
  var editable ;
  for(var attr in table_attributes)
    {
      var attributes = table_attributes[attr] ;
      e = document.getElementById('t_table_attr_' + attr) ;
      if ( ! e )
	continue ;
      if ( attributes.only_masters && ! ( i_am_the_teacher || i_am_root ) )
	e.style.display = 'none' ;
      else
	e.style.display = '' ;

      // In the loop because its value may change on attr masters
      disabled = ! table_change_allowed() || ! table_attr.modifiable ;
      if ( attr == 'modifiable' )
	editable = table_change_allowed() ;
      else if ( attr == 'masters' )
	editable = !disabled
	  || i_am_root || i_am_the_teacher
	  || (table_attr.modifiable && !table_attr.masters[0]) ;
      else
	editable = !attributes.need_authorization || !disabled  ;

      update_attribute_value(e, attributes, table_attr, editable) ;
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
  this.tr.className += ' highlight_current' ;
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

function current_cell_modifiable()
{
  return this.cell.modifiable() && this.column.real_type.cell_is_modifiable ;
}
   
// Update input from real table content (external change)
function current_update(do_not_focus)
{
  var lin, col ;

  lin = this.lin ;
  col = this.col ;

  if ( lin >= table_attr.nr_lines + nr_headers )
    lin = table_attr.nr_lines + nr_headers - 1 ;
  if ( col >= table_attr.nr_columns - 1 )
    col = table_attr.nr_columns - 1 ;

  this.jump(lin, col, do_not_focus) ;
}

function current_cursor_down()
{
  this.change() ;
  if ( this.lin == table_attr.nr_lines + nr_headers - 1 )
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

  if ( this.col == table_attr.nr_columns - 1 )
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
    case 55: /* AZERTY: 1/& */
    case 49: /* QWERTY: 1/! */
      toggle_display_tips() ;
      break ;

    case 189: /* AZERTY: 8/_ */
    case 109: /* AZERTY: 8/_ */
    case 95:  /* AZERTY: 8/_ */
    case 56:  /* QWERTY: 8/ * */
      linefilter.focus() ;
      if (linefilter.select)
	linefilter.select();
      break;

    case 16:
    case 0:
      break ;
    case 18: // ALT
      // Navigator must process the event
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
	  if ( alt_shortcut(event, this.td) )
	    return true ; // Navigator must process event
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
	}
    }

  // __d('alt=' + event.altKey + ' ctrl=' + event.ctrlKey + ' key=' + key + ' charcode=' + event.charCode + ' which=' + event.real_event.which + '\n') ;

  var selection ;
  if ( event.target === this.input )
    selection = get_selection(this.input) ;

  switch(key)
    {
    case 40: this.cursor_down() ; break ;
    case 13: this.cursor_down() ; break ;
    case 38: this.cursor_up()   ; break ;
    case 34: next_page()        ; break ;
    case 33: previous_page()    ; break ;
    case 37:
      if ( event.shiftKey )
	return true ;
      if ( event.ctrlKey
	   || this.input.value.length === 0
	   || !this.cell_modifiable()
	   || ((selection.end === this.input.textLength ||
		selection.end === this.input.value.length ||
		selection.end === 0)
	       && selection.start === 0)
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
      if ( event.shiftKey )
	return true ;
      if ( event.ctrlKey
	   || this.input.value.length === 0
	   || !this.cell_modifiable()
	   || this.input.textLength == selection.end
	   || this.input.value.length == selection.end
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
      if ( ! this.cell_modifiable() )
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
      // completion only in table cells
      if (  event.target === this.input && key >= 64
	    && event.ctrlKey === false
	    && this.input.textLength == selection.end ) // No control code
	setTimeout("the_current_cell.do_completion()") ;
      return true ;
    }
  stop_event(event) ;
  return false ;
}

function current_do_completion()
{
  alert_merged = '' ;
  var completion = this.column.real_type.cell_test(this.input.value,
						   this.column) ;
  alert_merged = false ;
  if ( completion && completion.substr
       && completion.substr(0, this.input.value.length).toLowerCase()
       == this.input.value.toLowerCase())
    {
      completion = completion.substr(this.input.value.length) ;
      this.input.value += completion ;
      set_selection(this.input,
		    this.input.value.length - completion.length,
		    this.input.value.length) ;
    }
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
  this.input.value = toggle(this.input.value, this.column) ;
  this.change() ;
  this.update() ;
}

Current.prototype.jump                  = current_jump                  ;
Current.prototype.change                = current_change                ;
Current.prototype.keydown               = current_keydown               ;
Current.prototype.update                = current_update                ;
Current.prototype.cursor_down           = current_cursor_down           ;
Current.prototype.cursor_up             = current_cursor_up             ;
Current.prototype.cursor_left           = current_cursor_left           ;
Current.prototype.cursor_right          = current_cursor_right          ;
Current.prototype.focus                 = current_focus                 ;
Current.prototype.toggle                = current_toggle                ;
Current.prototype.cell_modifiable       = current_cell_modifiable       ;
Current.prototype.do_completion         = current_do_completion         ;
Current.prototype.update_headers        = current_update_headers        ;
Current.prototype.update_headers_real   = current_update_headers_real   ;
Current.prototype.update_cell_headers   = current_update_cell_headers   ;
Current.prototype.update_column_headers = current_update_column_headers ;
Current.prototype.update_table_headers  = current_update_table_headers  ;
