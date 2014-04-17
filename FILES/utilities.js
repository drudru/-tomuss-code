// -*- coding: utf-8; mode: Java; c-basic-offset: 2; tab-width: 8; -*-
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

var languages ;

function __(txt)
{
  var t ;
  for(var i in languages)
    {
	t = translations[languages[i]][txt] ;
	if ( t )
	    return t ;
    }
  return txt ;
}

function _(txt)
{
    try
	{
	    languages = preferences.language.split(",") ;
	    _ = __ ;
	}
    catch(e)
	{
	    _ = function(x) { return x ; }
	}
  return _(txt) ;
}


function a_float(txt)
{
  if ( txt.replace )
    return Number(txt.replace(',', '.')) ;
  else
    return Number(txt) ;
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

function title_case(txt)
{
  if ( txt.length >= 2 )
    return txt.substr(0,1) + txt.substr(1).toLowerCase() ;
  return txt ;
}

/*****************************************************************************/
/*****************************************************************************/
/* Date Time management */
/*****************************************************************************/
/*****************************************************************************/

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
  var d, time ;

  if ( v.length == 1 && isNaN(value.substr(value.length-1)) )
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

  if ( v[2] !== undefined )
    {
      var x = v[2].split(/[ _]/) ;
      if ( x.length == 2 )
	{
	  v[2] = x[0] ;
	  x = x[1].split(/[:h]/) ;
	  if ( x.length == 2 && !isNaN(x[0]) && !isNaN(x[1]) )
	    time = [Number(x[0]), Number(x[1])] ;
	}
    }

  for(var i in v)
    if ( isNaN(Number(v[i])) )
      return false ;

  if ( v.length == 1 )
      {
	d = new Date() ;
	v.push(d.getMonth()+1) ;
      }
  if ( v.length == 2 )
      {
	d = new Date() ;
	v.push(d.getFullYear()) ;
      }
  if ( v.length == 3 )
      {
	if ( v[2] < 100 )
	  v[2] = Number(v[2]) + 2000 ;
	d = new Date(v[2], v[1]-1, v[0]) ;
	d.sup = new Date() ;
	d.sup.setTime(d.getTime()) ;
      }
    else
      return false ;

  if ( time === undefined )
      d.sup.setHours(23, 59, 59) ;
  else
    {
      d.setHours(time[0], time[1], 0) ;
      d.sup.setHours(time[0], time[1], 59) ;
    }
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

function get_date_tomuss(yyyymmddhhmmss)
{
  var year    = yyyymmddhhmmss.slice(0 , 4 ) ;
  var month   = yyyymmddhhmmss.slice(4 , 6 ) ;
  var day     = yyyymmddhhmmss.slice(6 , 8 ) ;
  var hours   = yyyymmddhhmmss.slice(8 , 10) ;
  var minutes = yyyymmddhhmmss.slice(10, 12) ;
  var seconds = yyyymmddhhmmss.slice(12, 14) ;
  return new Date(year, month-1, day, hours, minutes, seconds) ;    
}

function get_date_tomuss_short(yyyymmddMA)
{
  var year    = yyyymmddMA.slice(0 , 4 ) ;
  var month   = yyyymmddMA.slice(4 , 6 ) ;
  var day     = yyyymmddMA.slice(6 , 8 ) ;
  var d = new Date(year, month-1, day) ;
  d = d.formate('%d/%m/%Y') ;
  if ( yyyymmddMA.substr(8) == ampms[0] )
    d += ' ' + ampms_full[0] ;
  else if ( yyyymmddMA.substr(8) == ampms[1] )
    d += ' ' + ampms_full[1] ;
  return d ;
}

// See strftime for documentation
Date.prototype.formate = function(format)
{
    var ap = Number(this.getHours() >= 12 ) ;    
    var ampm      = ampms     [ap] ;
    var ampm_full = ampms_full[ap] ;
    return format
    .replace('%Y', this.getFullYear())
    .replace('%m', two_digits(this.getMonth()+1))
    .replace('%d', two_digits(this.getDate()))
    .replace('%H', two_digits(this.getHours()))
    .replace('%M', two_digits(this.getMinutes()))
    .replace('%S', two_digits(this.getSeconds()))
    .replace('%a', days[this.getDay()])
    .replace('%A', days_full[this.getDay()])
    .replace('%B', months_full[this.getMonth()])
    .replace('%b', months[this.getMonth()])
    .replace('%p', ampm)
    .replace('%P', ampm_full)
    ;
}


function date(x)
{
  if ( x === '' )
    return '' ;
  return get_date_tomuss(x).formate('%a %d/%m/%Y %H:%M.%S') ;
}

function date_full(x)
{
  if ( x === '' )
    return '' ;
  return get_date_tomuss(x).formate(_("MSG_full_date")) ;
}

// Code snippet from http://www.quirksmode.org/js/findpos.html
function findPos(x)
{
  var curleft = 0 ;
  var curtop = 0;
  var obj = x ;
  if (obj.offsetParent)
    {
      do {
	curleft += obj.offsetLeft;
	curtop += obj.offsetTop;
      } while ((obj = obj.offsetParent));

      // Search a scrollable area, but not the BODY one
      while( x && x.scrollTop === 0 )
	x = x.parentNode ;
      if ( x && x.tagName != 'HTML' && x.tagName != 'BODY' && x.scrollTop )
	{
	  curleft -= x.scrollLeft ;
	  curtop -= x.scrollTop ;
	}
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
    return t.toString() ; // Number
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
  if ( e.touches )
    {
      if ( e.touches.length == 1 )
	{
	  var finger0 = e.touches[0] ;
	  event.x = finger0.pageX ;
	  event.y = finger0.pageY ;
	  event.one_finger = true ;
	}
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

function tip_top(tt)
{
  var i ;

  if ( tt === undefined || tt.tagName === undefined )
    {
      return undefined ;
    }

  i = 0 ;
  var debug = '' ;
  while( tt.tagName !== 'TD' && tt.tagName !== 'TH' &&
	 (tt.className ? tt.className.toString().indexOf('tipped') == -1
	  : true) )
    {
      debug = tt.tagName + '\n' + debug ;
      tt = tt.parentNode ;
      i++ ;
      if ( i == 10 || !tt )
	{
	  alert('tip_top:\n' + debug) ;
	  return undefined ;
	}
    }
  if ( tt.tagName === 'TD' || tt.tagName === 'TH' )
    {
      var t = tt ;
      while( t.tagName != 'TABLE' )
	t = t.parentNode ;
      if ( t.className.toString().indexOf('not_tip_top') != -1 )
	return tip_top(t) ;
    }
  return tt ;
}

function compute_tip(element)
{
  if ( element.offsetHeight === 0 )
    return '' ;

  var value = element.selectedText ;
  if ( ! value )
    value = element.value ;
  if ( value )
    value = '<div class="more">' + html(value) + '</div>' ;
  else
    value = '' ;

  var t = tip_top(element) ;
  return t.childNodes[0].innerHTML + value ;
}

function hidden_over(event)
{
  event = the_event(event) ;
  var target = event.target ;

  if ( target.tagName == 'OPTION' )
    return ;
  if ( target.tagName == 'svg' )
  {
    target = target.parentNode ;
  }
  
  var value = compute_tip(target) ;
  show_the_tip(target, value, target.id ? target.id : target.textContent) ;
}

function hidden_out()
{
  hide_the_tip_real() ;
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

  return '<div ' + id + 'class="tipped' + classname + '" onmouseover="hidden_over(event);" onmouseout="hidden_out();"><div class="help"><p>' + help + '<div></div></div><div class="text">' + html + '</div></div>' ;
}


function hidden(html, help, classname, id)
{
  document.write(hidden_txt(html, help, classname, id)) ;
}

// To synchronize with Python canonize and JavaScript decode_uri_option
function encode_uri(t)
{
  // We use $ in place of % because we don't want the proxies
  // or Apache or Single Sign On services to mess with the data content.
  // $$ => $ by replace method (to cancel positionnal argument)
  return encodeURI(t)
    .replace(/\$/g, "$$24").replace(/\?/g, "$$3F").replace(/#/g, "$$23")
    .replace(/[.]/g, "$$2E").replace(/&/g, "$$26").replace(/\//g, "$$2F")
    .replace(/[+]/g, "$$2B").replace(/%0A/g, "$$0A").replace(/%0D/g, "$$0D") ;
}

function encode_uri_option(t)
{
  return encode_uri(t).replace(/_/g, '__')
    .replace(/[=]/g,'_E').replace(/:/g, '_C') ;
}

function decode_uri_option(t)
{
  return unescape(t.toString().replace(/\$2F/g,'/').replace(/\$3F/g,'?')
		  .replace(/\$23/g,'#').replace(/\$2E/g,'.')
		  .replace(/\$26/g,'&').replace(/\$2B/g,'+').replace(/\$20/g,' ')
		  .replace(/_E/g,'=').replace(/_C/g,':').replace(/__/g,'_')
		  .replace(/\$24/g, '$')) ;
}

function encode_value(txt)
{
  return txt.replace(/&/g, "&#38;").replace(/"/g, '&#34;')
            .replace(/\?/g, "&#63;");
}


function encode_lf_tab(txt)
{
  return txt.replace(/\n/g, '⏎').replace(/\t/g, '⇥') ;
}

function decode_lf_tab(txt)
{
  return txt.replace(/⏎/g, '\n').replace(/⇥/g, '\t') ;
}

// Adapted from Andrea Azzola's Blog
function do_post_data(dictionary, url)
{
  // Create the form object
  var form = document.createElement("form") ;
  form.setAttribute("method", "post") ;
  form.setAttribute("action", url) ;
  form.setAttribute("enctype", "multipart/form-data") ;
  form.setAttribute("encoding", "multipart/form-data") ; // For IE
  form.setAttribute("target", "_blank") ;

  // For each key-value pair
  for (key in dictionary)
  {
    var hiddenField = document.createElement("input") ;
    // 'hidden' is the less annoying html data control
    hiddenField.setAttribute("type", "hidden") ;
    hiddenField.setAttribute("name", key) ;
    hiddenField.setAttribute("value", dictionary[key]) ;
    form.appendChild(hiddenField) ;    
  }
  document.body.appendChild(form) ;
  form.submit() ;
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

function debug_tree(e)
{
  var s = "" ;
  while(e)
  {
    s += e.tagName + '.(' + e.className + ')\n' ;
    e = e.parentNode ;
  }
  alert(s) ;
}
    

function Alert(m, more)
{
    if ( more === undefined )
	more = ''
    alert(_(m) + "\n" + more) ;
}

function Write(m, more)
{
    if ( more === undefined )
	more = ''
    document.write(_(m) + more) ;
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

function scrollTop(value)
{
  if ( value === undefined )
    {
      if ( document.body.scrollTop !== undefined )
	return document.body.scrollTop ;
      return window.screenY ;
    }
  else
    {
      if ( document.body.scrollTop !== undefined )
	document.body.scrollTop = value ;
      else
	window.screenY = value ;
    }
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

function on_mac()
{
  return navigator.platform.indexOf('Macintosh') != -1 ;
}

var window_counter = 0 ;
function window_open(url, replace)
{
  var w ;
  var title = window_counter++ ;
  if ( replace )
      title = replace ;
  try {
    w = window.open(url, title) ;
  }
  catch(e) {
    // XXX IE
    w = window.open() ;
  }
  if ( ! w )
    {
      Alert("ALERT_popup") ;
    }
  setTimeout(function() { if ( w.outerHeight === 0 ) popup_blocker = true ;},
	     500) ;
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
  if ( mails.length < max_url_length )
    return true ;
  if ( on_windows() || on_mac() )
    return false ;
  return true ;
}

function my_mailto(mails, display)
{
  if ( mails.search('@') == -1 )
    {
      Alert("ALERT_no_mail") ;
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
  var message = _("ALERT_copy_mail")  + "\n\n" ;

  if ( display === undefined )
      message = _("ALERT_copy_mail_microsoft") + "\n\n" + message ;

  return new_window(message + mails + '\n\n') ;
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
    return url + '/=' + ticket + '/picture/' + login_to_id(login) + '.JPG' ;
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
  lineCSV = lineCSV.replace(/\t/g,"\001\t").split('\t');
  for (var i in lineCSV)
    lineCSV[i] = lineCSV[i].replace(/\001$/g, "") ;
  
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

function P(k,t)
{
  lines[k] = t ;
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
  return _('B_s_minimum') +':&nbsp;'  +this.min            .toFixed(3)+'<br>' +
    _('B_s_maximum') +':&nbsp;'  +this.max                 .toFixed(3)+'<br>' +
    _('B_s_average')+':&nbsp;<b>'+this.average()       .toFixed(3)+'</b><br>' +
    _('B_s_mediane') +':&nbsp;'  +this.mediane()           .toFixed(3)+'<br>' +
    _('B_s_variance')+':&nbsp;'  +this.variance()          .toFixed(3)+'<br>' +
    _('B_s_stddev')  +':&nbsp;'  +this.standard_deviation().toFixed(3)+'<br>' +
    _('B_s_sum')+' '+this.nr+' '+_('B_s_sum_2')+':&nbsp;'
    +this.sum.toFixed(3)+'\n';
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

function compute_histogram(data_col)
{
  var stats = new Stats(columns[data_col].min, columns[data_col].max,
			columns[data_col].empty_is) ;
  for(var line in filtered_lines)
    if ( filtered_lines[line][0].value || filtered_lines[line][1].value )
      stats.add(filtered_lines[line][data_col].value) ;
  return stats ;
}


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
  return html(this.comment).replace(/\n/g, '<br>') ;
}

function cell_changeable(column)
{
  if ( ! table_attr.modifiable )
      return _("ERROR_table_read_only") ;
  if ( ! this.is_mine() )
    {
      if ( ! i_am_the_teacher )
	  return _("ERROR_value_defined_by_another_user") + table_attr.masters;
      if ( this.author === '*')
	  return _("ERROR_value_not_modifiable") + '\n'
	    + _("ERROR_value_system_defined") ;
    }
  if ( column.locked )
      return _("ALERT_locked_column") ;
  return true ;
}

function cell_modifiable(column)
{
  return this.changeable(column) === true ;
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

function get_author(author)
{
  if ( author === '' )
    return '' ;
  if ( author === '*' )
    return 'tomuss' ;

  return author ;
}

function get_author2(column)
{
  return get_author(column.author);
}


function cell_get_author()
{
  return get_author(this.author) ;
}

function cell_never_modified()
{
  return this.author === '' ;
}

// Allow to sort correctly and intuitivly mixed data types
function cell_key(empty_is)
{
  if ( this._key !== undefined )
    return this._key ;

  var x, date, s, i ;
  var v = this.value ;
  if ( v === '' )
    v = empty_is ;

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
	      if ( isNaN(x) )
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

function cell_date_DDMMYYYY()
{
   var x = this.date ;
   return x.slice(6, 8) + '/' + x.slice(4, 6) + '/' + x.slice(0, 4) ;
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
Cell.prototype.get_author = cell_get_author ;
Cell.prototype.date_DDMMYYYY = cell_date_DDMMYYYY ;

/*
 * GUI recording
 * Debug mode if =gui-record= in the URL
 */

function GUI_record()
{
  if ( /=gui-record=/.test(window.location.pathname) )
    {
      this.debug = document.createElement('PRE') ;
      this.debug.style.position = 'fixed' ;
      this.debug.style.right = this.debug.style.bottom = '40px' ;
      this.debug.style.width = '40em' ;
      this.debug.style.height = '50%' ;
      this.debug.style.background = 'white' ;
      this.debug.style.overflow = 'auto' ;
    }
  this.start = millisec() ;
  this.start_o = new Date() ;
  this.last_interaction = this.start ;
}

GUI_record.prototype.save = function()
{
  if ( ! gui_record )
    return ;
  if ( this.events.length == 0 )
    return ;
  var s = [] ;
  for(var i in this.events)
    s.push('[' + this.events[i][0]
	   + ',"' + this.events[i][1] + '"'
	   + (this.events[i][2] ? ',' + js(this.events[i][2]) : '')
	   + ']') ;
  var fd ;
  try {
    fd = new FormData() ;
  }
  catch(e)
    {
      return ;
    }

  fd.append("table", year + '/' + semester + '/' + ue) ;
  fd.append("start", this.start_o.formate("%Y%m%d%H%M%S")) ;
  fd.append("data", '[' + s.join(',') + ']') ;
  
  if ( window.XMLHttpRequest )
    {
      this.mxmlhttp = new XMLHttpRequest();
      this.mxmlhttp.open("POST", url + '/=' + ticket + '/gui_record', true) ;
      this.mxmlhttp.send(fd) ;
    }
  this.events = [] ;
}

GUI_record.prototype.initialize = function()
{
  this.events = [] ;

  this.body = document.getElementsByTagName('H1')[0] ;
  if ( this.debug )
    this.body.appendChild(this.debug) ;
  this.initialized = true ;
  // Save once per minute
  setInterval(GUI_save, 60000) ;
}

GUI_record.prototype.add = function(attr_name, event, value) {
  if ( ! this.initialized )
    this.initialize() ;
  if ( event )
    {
      event = the_event(event) ;
      if ( event.target.tagName == 'INPUT' )
	value = event.target.value ;
      else if ( /^t_column_/.test(attr_name)  )
	value = the_current_cell.column[attr_name.replace("t_column_","")] ;
      else if ( /^t_table_attr_/.test(attr_name)  )
	value = table_attr[attr_name.replace("t_table_attr_","")] ;
      else
	value = '?' ;
    }
  if ( attr_name == 'tip' && ! value )
    {
      var last = this.events[this.events.length-1] ;
      // If the tip is visible less than 0.1s do not record it
      if (last && millisec() - this.start - last[0] < 100 && last[1] == 'tip')
	{
	  this.events.splice(this.events.length-1, 1) ;
	  if ( this.debug !== undefined )
	    this.debug.innerHTML += 'Remove previous event\n' ;
	  return ;
	}	  
    }
  this.last_interaction = millisec() ;
  this.events.push([this.last_interaction - this.start, attr_name, value]) ;
  if ( this.debug !== undefined )
    {
      this.debug.innerHTML += this.events[this.events.length-1] + '\n' ;
      this.debug.scrollTop = 100000000 ;
    }
  
  if ( connection_state == 'no_connection' )
    reconnect(true) ;

} ;

GUI_record.prototype.add_key = function(event, value) {
  var id = (
	    (event.metaKey ? 'M' : '') +
	    (event.shiftKey ? 'S' : '') +
	    (event.ctrlKey ? '^' : '') +
	    event.keyCode
	    ) ;
  if ( value === undefined )
    {
      if ( element_focused )
	value = "input" ;
      else
	value = "cell" ;
    }
  this.add(id, "", value) ;
} ;

var GUI = new GUI_record() ;
function GUI_save()
{
  GUI.save() ;
  if ( millisec() - GUI.last_interaction > 60000 )
    {
      /* Close connection in order to free open socket */
      if ( xmlhttp )
	{
	  xmlhttp.abort() ;
	  xmlhttp = undefined ;
	  connection_state = 'no_connection' ;
	  document.getElementById('connection_state').innerHTML += '...' ;
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

function set_select_by_value(element, value)
{
  var options = element.getElementsByTagName('OPTION') ;
  for(var i in options)
    {
      if ( options[i].value == value || options[i].text == value )
	{
	  element.selectedIndex = i ;
	  element.selectedText = options[i].text ;
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
  this.line_id = '' ;
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

  var tip_id, tip_content, tip_exists ;
  // XXX In some case 'the_current_cell.column' is undefined
  if ( the_current_cell.column )
      {
	  var tip_id = 'TIP_' + attr.what + '_attr_' + attr.name ;
	  tip_content = _(tip_id) ;
	  tip_exists =  tip_id != tip_content ;
	  if ( ! tip_exists && attr.what == 'column' )
	      {
		  tip_id += '__' + the_current_cell.column.type ;
		  tip_content = _(tip_id) ;
		  tip_exists =  tip_id != tip_content ;
	      }
      }
  switch(attr.gui_display)
  {
    case 'GUI_select':
      set_select_by_value(e, value) ;
      break ;
    case 'GUI_input':
      if ( attr.what == 'table' )
	update_input(e, formatted, attr.empty(value)) ;
      else
	update_input(e, formatted, attr.empty(table, value)) ;

      if ( tip_exists )
	{
	    if ( i_am_root )
	       tip_content += '<hr><b>' + e.id + '</b>' ;
	    try {
		tip_top(e).firstChild.innerHTML = tip_content ;
	    }
	    catch(e) {
		// XXX IE has an unknown exception here...
	    }
	}
      break ;
    case 'GUI_a':
      var x = e.className.replace('linkstroked', '') ;
      var old_class = e.className ;
      if ( ! value && attr.strokable )
	x += ' linkstroked' ;
      if ( attr.strokable
	   && !!value != (old_class.search('linkstroked') == -1) )
	{
	  highlight_add(e) ;
	  // Classname change must be done before 'highlight_add'
	  // And 'highlight_add' should not erase classname
	  // But if classname is not erased, it brokes thing
	  // when there is 'empty' class
	  x += ' highlight1' ;
	}
      e.className = x.replace(/^ */,'') ;

      if ( ! tip_exists )
	{
	  if ( value )
	      tip_id += '__1' ;
	  else
	      tip_id += '__0' ;
	  tip_content = _(tip_id) ;
	  if ( i_am_root )
	    tip_content += '<hr><b>' + e.id + '</b>' ;
	  tip_top(e).firstChild.innerHTML = tip_content ;
	}
      return ;
    case 'GUI_button':
      break ;
    case 'GUI_type':
      e.innerHTML = _('B_' + value) ;
      break ;
    case 'GUI_none':
      if ( e.tagName == 'SPAN' )
	{
	  if ( e.innerHTML != formatted )
	    highlight_add(e) ;
	  e.innerHTML = formatted ;
	}
      return ;
    default:
      alert('BUG GUI:' + attr.gui_display) ;
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
	  update_attribute_value(e, column_attributes[attr], column, false);
	  continue ;
	}
      if ( ! column_modifiable_attr(attr, column) )
	{
	  if ( column_attributes[attr].always_visible )
	  {
	    e.parentNode.style.opacity = 0.3 ;
	    e.value = '' ;
	    set_editable(e, false) ;
	  }
	  else
	    e.parentNode.style.display = 'none' ;
	  continue ;
	}
      if ( column_attributes[attr].gui_display == 'GUI_none' )
	eval(column_attributes[attr].action + '()') ;
      if ( column_attributes[attr].always_visible )
      {
	e.parentNode.style.opacity = '' ;
	set_editable(e, true) ;
      }
      else
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
      set_editable(the_comment, cell.modifiable(this.column)) ;
    }

  update_value_and_tip(t_value, cell.value) ;

  var s = ['<table class="colored not_tip_top">'] ;
  s.push('<tr><th>' + _("B_Date") + '<th>' + _('TH_who') + '<th>'
	 + _("TH_value") + '</tr>') ;
  s.push('<tr><td>' + date(cell.date) + '<td>'
	 + cell.get_author() + '<td>'
	 + html(cell.value) + '</tr>') ;
  var h = cell.history.split('),·') ;
  h.pop() ;
  h.reverse() ;
  for(var i in h)
  {
    i = h[i].split('\n(') ;
    var date_author = i[1].split(' ') ;
    s.push('<tr><td>' + date(date_author[0]) + '<td>'
	   + get_author(date_author[1])
	   + '<td>' + html(i[0]) + '</tr>') ;
  }
  s.push('</table>') ;
  t_history.innerHTML = s.join('\n') ;
      
  update_tip_from_value(t_student_picture.parentNode,
			'<!--INSTANTDISPLAY-->' + line_resume(this.line_id),'');
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
	// XXX i_am_the_teacher is not yet updated on first display
	// It is clearly not a nice code.
	editable = !disabled
	  || i_am_root || myindex(table_attr.masters, my_identity) != -1
	  || (table_attr.modifiable && !table_attr.masters[0])
	  || myindex(table_attr.managers, my_identity) != -1
      else
	editable = !attributes.need_authorization || !disabled  ;
      update_attribute_value(e, attributes, table_attr, editable) ;
    }
}

function current_update_headers_real()
{
  var img ;

  if ( author )
    author.innerHTML = this.cell.author ;
  if ( modification_date )
    modification_date.innerHTML = date(this.cell.date) ;

  var tip = get_tip_element() ;
  update_student_information(this.line) ;
  this.update_cell_headers() ;
  this.update_column_headers() ;

  var s_abjs = student_abjs(this.line[0].value) ;
  if ( s_abjs !== "")
    {
      if ( ! body_on_mouse_up_doing )
      {
	// Only abjs if not scrolling
	tip.innerHTML = student_abjs(this.line[0].value) ;     
	tip.style.display = "block" ;
	set_tip_position(this.td) ;
      }
    }
  else
    {
      if ( tip.tip_target )
	{
	  tip.innerHTML = compute_tip(tip.tip_target) ;
	  if ( tip.innerHTML == 'undefined' )
	    {
	      tip.do_not_hide = false ;
	      hide_the_tip_real() ;
	    }
	  else
	    set_tip_position(tip.tip_target) ;
	}
      else
      {
	tip.do_not_hide = false ;
	hide_the_tip_real() ;
      }
    }

  // Remove green square from top menu
  var t = t_menutop.getElementsByTagName('IMG') ;
  for(img in t)
    {
      img = t[img] ;
      if ( img && img.request && img.request.saved )
	img.parentNode.removeChild(img) ;
    }
  // Update hidden columns menu
  update_hiddens_menu() ;
}

function current_update_headers_()
{
    the_current_cell.update_headers_real() ;
}

function current_update_headers()
{
    periodic_work_add(current_update_headers_) ;
}

function current_jump(lin, col, do_not_focus, line_id, data_col)
{
  if ( data_col === undefined )
    data_col = data_col_from_col(col) ;
  if ( line_id === undefined )
      {
	  do
	      {
		  line_id = line_id_from_lin(lin) ;
		  if ( line_id === undefined )
		      add_a_new_line() ;
	      }
	  while( line_id === undefined ) ;
      }

  var line = lines[line_id] ;
  if ( ! line )
    {
      alert('BUG current jump:' + line_id) ;
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
      if ( ! cell.modifiable(columns[data_col]) )
	{
	  save.focus() ;
	  if ( element_focused === undefined )
	    {
	      save.onfocus() ;
	    }
	}
    }

  /* Removed the 19/1/2010 In order to select RO values
     if (  ! cell.modifiable(column) )
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
  this.previous_line_id = this.line_id ;
  this.line_id = line_id ;
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
  // 3 is the border size (see input_div_focus())
  this.input_div.style.left = pos[0] - 3 + 'px' ;
  this.input_div.style.top = pos[1] - 3 + border + 'px' ;
  this.input_div.style.width = this.td.offsetWidth + 'px' ;
  this.input_div.style.height = this.td.offsetHeight - border + 'px' ;
  this.input.className = this.td.className + ' ' + this.tr.className ;
  this.input.value =columns[this.data_col].real_type.formatte(this.cell.value,
							      this.column);
  this.initial_value = this.input.value ;

  // Update position in scrollbar
  if ( vertical_scrollbar && this.previous_line_id != this.line_id )
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
      periodic_work_add(login_list_ask) ;
    }
  this.update_headers() ; //this.previous_col == this.col) ;

  // Remove a copy bug of Firefox that insert tag when copying
  while( this.input_div.firstChild.tagName != 'INPUT' )
    this.input_div.removeChild(this.input_div.firstChild) ;
}

function current_jump_if_possible(line_id, data_col, do_not_focus)
{
  var td = td_from_line_id_data_col(line_id, data_col) ;
  if ( td )
    this.jump(lin_from_td(td), col_from_td(td), do_not_focus) ;
}

function current_focus()
{
  //this.input.contentEditable = this.cell.modifiable() ;
  this.input.focus() ;
  if ( this.input.select )
    this.input.select() ;
  this.input_div_focus() ;
}

function current_cell_modifiable()
{
  return this.cell.modifiable(this.column)
      && this.column.real_type.cell_is_modifiable ;
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
      next_page(true, 1) ;
      // table_fill_try() ; // Want change NOW (bad input if fast typing)
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
	  previous_page(true, 1) ;
	  // table_fill_try() ; // Want change NOW (bad input if fast typing)
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

function control_f()
{
  select_tab("cellule", _("TAB_cell")) ;
  linefilter.focus() ;
  if (linefilter.select)
    linefilter.select();  
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
      control_f() ;
      break;
    case 16:
    case 0:
      break ;
    case 191: /* Qwerty / */
    case 59: /* Azerty / */
    case 58: /* Azerty : */
	select_tab("cellule", _("TAB_cell")) ;
	the_comment.focus() ;
	break ;
    case 18: // ALT
      // Navigator must process the event
    default:
	// alert(event.charCode);
      return true ;
    }
  stop_event(event) ; // Else ALTs are navigator shortcut
  return false ;
}

function triggerKeyboardEvent(el, keyCode)
{
    var eventObj = document.createEventObject
      ? document.createEventObject()
      : document.createEvent("Events") ;
  
    if(eventObj.initEvent){
      eventObj.initEvent("keydown", true, true) ;
    }
  
    eventObj.keyCode = keyCode ;
    eventObj.which = keyCode ;
    
    if ( el.dispatchEvent )
      el.dispatchEvent(eventObj) ;
    else
      el.fireEvent("onkeydown", eventObj) ;
}

function current_keydown(event, in_input)
{
  last_user_interaction = millisec() ;
  event = the_event(event) ;
  var key = event.keyCode ;
  if ( popup_is_open() )
    {
      if ( key == 27 )
	{
	  GUI.add_key(event, "popup-close") ;
	  popup_close() ;
	}
      return ;
    }
  if ( element_focused )
    {
      if ( element_focused.tagName == 'TEXTAREA' )
	return ;
      else if ( element_focused.id == "table_forms_keypress" )
	{
	  if ( key < 41 && key != 27 )
	    return ;
	}
      else if ( element_focused.tagName == 'SELECT' )
	{
	  // Autocompletion menu
	  var nb_item = element_focused.childNodes.length ;
	  if ( key == 38 || key == 40 )
	    {
	      GUI.add_key(event, "select") ;
	      if ( element_focused.my_selected_index
		   != element_focused.selectedIndex )
		{
		  // The SELECT object change itself the line when using keys.
		  // So do not change it ourself.
		  element_focused.my_selected_index = -1 ;
		  // XXX The first keystroke when SELECT is active
		  // move twice on FireFox
		  return ;
		}

	      element_focused.selectedIndex = (element_focused.selectedIndex
					       + key - 39) % nb_item ;
	      element_focused.my_selected_index =element_focused.selectedIndex;
	      stop_event(event) ;
	      return ;
	    }
	  else if ( key == 13 || key == 27 )
	    {
	      GUI.add_key(event, "select") ;
	      event.target = element_focused ;
	      element_focused.onchange(event) ;
	      stop_event(event) ;
	      return ;
	    }
	  if ( key < 40 && key != 8 )
	    return ;
	}
    }
       
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
	  if (key == 37 || key == 39)
	    return ;
	}
    }
  if ( (key == 35 || key == 36) && ! event.ctrlKey)
    return ;

  if ( event.ctrlKey )
    {
      switch( key )
	{
	case 70: // F
	  GUI.add_key(event, "find") ;
	  control_f() ;
	  stop_event(event) ;
	  return false ;
	case 80: // P
	  GUI.add_key(event, "print") ;
	  print_selection() ;
	  stop_event(event) ;
	  return false ;
	case 33:
	case 34:
	  // Let the browser change the tab
	  return true ;
	}
    }

  // __d('alt=' + event.altKey + ' ctrl=' + event.ctrlKey + ' key=' + key + ' charcode=' + event.charCode + ' which=' + event.real_event.which + '\n') ;

  var selection ;
  if ( event.target.tagName === 'INPUT' )
    selection = get_selection(event.target) ;
  switch(key)
    {
    case 40: this.cursor_down() ; GUI.add_key(event) ; break ;
    case 13: this.cursor_down() ; GUI.add_key(event) ; break ;
    case 38: this.cursor_up()   ; GUI.add_key(event) ; break ;
    case 34: next_page()        ; GUI.add_key(event) ; break ;
    case 33: previous_page()    ; GUI.add_key(event) ; break ;
    case 36: first_page()       ; GUI.add_key(event) ; break ;
    case 35: last_page()        ; GUI.add_key(event) ; break ;
    case 37:
      if ( event.shiftKey )
	return true ;
      if ( event.ctrlKey
	   || this.input.value.length === 0
	   || !this.cell_modifiable()
	   || (selection && selection.start === 0 
	       && (selection.end === this.input.textLength ||
		   selection.end === this.input.value.length ||
		   selection.end === 0)
	       )
	   )
	{
	  GUI.add_key(event) ;
	  this.cursor_left() ;
	}
      else
	return true ;
      break ;
    case 9:
      GUI.add_key(event) ;
      if ( event.shiftKey )
	  this.cursor_left() ;
      else
	  this.cursor_right() ;
      break ;
    case 39:
      if ( event.shiftKey )
	return true ;
      if ( selection && ( event.ctrlKey
			  || this.input.value.length === 0
			  || !this.cell_modifiable()
			  || this.input.textLength == selection.end
			  || this.input.value.length == selection.end
			  )
	   )
	{
	  GUI.add_key(event) ;
	  this.cursor_right() ;
	}
      else
	return true ;
      break ;
    case 27: // Escape Key
      // alert('' + this.input.value + '/' + this.initial_value) ;
      GUI.add_key(event) ;
      if ( element_focused )
	{
	  element_focused.value = element_focused.initial_value ;
	  var a = element_focused ;
	  this.focus() ; // XXX The input value is unchanged without this
	  a.focus() ;
	  // Launch filter updating
	  triggerKeyboardEvent(a, -1) ;
	}
      else
	{
	  this.input.value = this.initial_value ;
	  this.input.blur() ;
	  this.focus() ;
	}
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
      // completion
      
      if ( selection
	   && (key >= 48 || key == 8)
	   && event.ctrlKey === false
	   && event.target.value.length == selection.end ) // No control code
	{
	  if ( do_completion_for_this_input == undefined )
	    {
	      do_completion_for_this_input = event.target ;
	      setTimeout('the_current_cell.do_completion(' + (key==8) +')', 1);
	    }
	}
      return true ;
    }
  stop_event(event) ;
  return false ;
}

var do_completion_for_this_input ;

function current_do_completion(backspace)
{
  var completion, completions = [] ;
  var input = do_completion_for_this_input ;

  do_completion_for_this_input = undefined ;

  if ( input == this.input || input.id == "table_forms_keypress" )
    {
      var c = this.column.real_type.cell_completions(input.value,this.column) ;
      if ( c != input.value )
	{
	  // It is an enumeration
	  for(var i in c)
	    completions.push([c[i], "", "", "", c[i]]) ;
	  completions.sort() ;
	}
      else if ( this.column.completion )
	{
	  // Auto completion from content
	  var uniques = compute_histogram(this.column.data_col).uniques() ;
	  var value_low = input.value.toLowerCase() ;
	  var value_len = input.value.length ;
	  
	  for(var i in uniques)
	    if ( uniques[i] && i != "" )
	      if ( value_low == i.toLowerCase().substr(0, value_len) )
		completions.push([i, "", "", "", i]) ;
	  completions.sort() ;
	  if ( completions.length != 1 )
	    completions.splice(0,0,[input.value, "", "", "", input.value]) ;
	}
      else
	{
	  // Replace value by it normal completion
	  alert_merged = '' ;
	  completion =this.column.real_type.cell_test(input.value,this.column);
	  alert_merged = false ;
	  if ( completions.length != 1 )
	    completions.push([completion, "", "", "", completion]) ;
	}
    }
  else if ( input.id == 't_column_columns' )
    {
      var names = input.value.split(' ') ;
      var last = names[names.length-1].toLowerCase() ;
      for(var column in columns)
	{
	  column = columns[column] ;
	  if ( column.title.substr(0, last.length).toLowerCase() == last )
	    {
	      names[names.length-1] = column.title ;
	      completions.push([column.title, "", "", "", names.join(' ')]) ;
	    }
	}
      completions.sort() ;
      names[names.length-1] = '' ;
      if ( completions.length == 0)
	{
	  completions.push([_("MSG_columns_completion_before"),
			    "", last, "", names.join(' ')]) ;
	  completions.push([_("MSG_columns_completion_after"),
			    "", "", "", names.join(' ')]) ;
	}
      if ( completions.length > 1 )
	completions.splice(0,0,["", "", "", "", names.join(' ')]) ;
    }

  if ( completions.length > 1 )
    {
      ask_login_list = "" ;
      login_list("", completions, last) ;
      return;
    }
  login_list_hide() ;
  
  if ( completions.length == 0 || backspace )
    return ;

  completion = completions[0][4] ;

  if ( completion && completion.substr
       && completion.substr(0, input.value.length).toLowerCase()
       == input.value.toLowerCase())
    {
      var length = input.value.length ;
      if (window.KeyEvent)
	{
	  input.value = "" ;
	  for(var i=0; i<completion.length; i++)
	    {
	      triggerKeyboardEvent(input, completion.charCodeAt(i)) ;
	      if (input.value.length == 0)
		{
		    // Hit a bug, fallback on a classic method
		    input.value = completion ;
		    break ;
		}
	    }
	}
      else
	input.value = completion ;
      
      set_selection(input,
		    length,
		    input.value.length) ;
    }
}

var current_change_running = false ;

/*REDEFINE
  This function returns true if the ID is missing on the line.
  It is called for each interactive cell change.
  If 'true' is returned, an alert is displayed to the user.
*/
function current_missing_id(value)
{
  return (this.data_col !== 0
	  && lines[this.line_id][0].is_empty()
	  && value !=='') ;
}


function current_input_div_focus()
{
  if ( this.focused )
    this.input_div.style.border = "3px solid blue" ;
  else
    this.input_div.style.border = "3px solid gray" ;  
}

function current_change()
{
  this.input_div_focus() ;
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
  if ( myindex(semesters, semester) != -1 )
    {
      if ( this.data_col === 0 )
	{
	  /* Verify ID */
	  if ( value !== '' )
	    if ( login_to_line_id(value) !== undefined )
	      {
		  Alert("ALERT_duplicate_id") ;
		this.input.value = this.initial_value ;
		current_change_running = false ;
		GUI.add("cell_change_error", undefined, "duplicate_id") ;
		return ;
	      }
	}
    }
  if ( ! modification_allowed_on_this_line(this.line_id,this.data_col, value) )
    {	    
      this.input.value = this.initial_value ;
      current_change_running = false ;
      GUI.add("cell_change_error", undefined, "not_allowed") ;
      return ;
    }
  if ( this.missing_id(value) )
    {
	Alert("ALERT_missing_id") ;
    }
  if ( this.column && this.column.real_repetition && value !== '' )
    {
      var n = 0 ;
      var verify_lines ;

      if ( this.column.real_repetition > 0 )
	verify_lines = lines ;
      else
	{
	  verify_lines = [] ;
	  var grp = this.line[3].value ; // XXX should seach column name
	  var seq = this.line[4].value ;
	  for(var line in lines)
	    {
	      line = lines[line] ;
	      if ( line[3].value == grp && line[4].value == seq )
		verify_lines.push(line) ;
	    }
	}

      for(var line in verify_lines)
	if ( verify_lines[line][this.data_col].value == value )
	  n++ ;
      if ( n >= Math.abs(this.column.real_repetition) )
	{
	    alert(_("ALERT_duplicate_before") + n + _("ALERT_duplicate_after")
		  + Math.abs(this.column.real_repetition)) ;
	  this.input.value = this.initial_value ;
	  current_change_running = false ;
	  GUI.add("cell_change_error", undefined, "repetition_not_allowed") ;
	  return ;
	}
    }

  this.input.blur() ; // If have focus : problem with page change
  this.input.value = cell_set_value(this.td, value,
				    this.line_id, this.data_col) ;
  this.initial_value = this.input.value ;

  update_line(this.line_id, this.data_col) ;
  current_change_running = false ;
  GUI.add("cell_change", undefined, this.input.value) ;
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
Current.prototype.jump_if_possible      = current_jump_if_possible      ;
Current.prototype.change                = current_change                ;
Current.prototype.input_div_focus       = current_input_div_focus       ;
Current.prototype.keydown               = current_keydown               ;
Current.prototype.update                = current_update                ;
Current.prototype.cursor_down           = current_cursor_down           ;
Current.prototype.cursor_up             = current_cursor_up             ;
Current.prototype.cursor_left           = current_cursor_left           ;
Current.prototype.cursor_right          = current_cursor_right          ;
Current.prototype.focus                 = current_focus                 ;
Current.prototype.toggle                = current_toggle                ;
Current.prototype.cell_modifiable       = current_cell_modifiable       ;
Current.prototype.missing_id            = current_missing_id            ;
Current.prototype.do_completion         = current_do_completion         ;
Current.prototype.update_headers        = current_update_headers        ;
Current.prototype.update_headers_real   = current_update_headers_real   ;
Current.prototype.update_cell_headers   = current_update_cell_headers   ;
Current.prototype.update_column_headers = current_update_column_headers ;
Current.prototype.update_table_headers  = current_update_table_headers  ;
