// -*- coding: utf-8; mode: Java; c-basic-offset: 2; tab-width: 8; -*-
/*
  TOMUSS: The Online Multi User Simple Spreadsheet
  Copyright (C) 2008-2015 Thierry EXCOFFIER, Universite Claude Bernard

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
var minors = [] ;

function __(txt)
{
  var t ;
  for(var i in languages)
    {
	t = translations[languages[i]] ;
	if ( t && t[txt] )
	    return t[txt] ;
    }
  if ( translations['fr'] && translations['fr'][txt] )
    return translations['fr'][txt] ;
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

  for(var i=0; i<v.length; i++)
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
  if ( e === undefined )
    return ;
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

function hidden_txt(html, help, classname, id, myonshow)
{
  if ( id )
    id = ' id="' + id + '"' ;
  else
    id = '' ;
  if ( classname !== undefined )
    classname = ' ' + classname ;
  else
    classname = '' ;
  if ( myonshow === undefined )
    myonshow = '' ;

  if ( html === undefined )
    html = '????????' ;
  html = html.toString() ;
  html = html.replace('<a', '<a onfocus="hidden_over(event);" onblur="hidden_out();"') ;

  return '<div ' + id + 'class="tipped' + classname
    + '" onmouseover="hidden_over(event);' + myonshow
    + '" onmouseout="hidden_out();' + myonshow + '"><div class="help"><p>'
    + help + '<div></div></div><div class="text">' + html + '</div></div>' ;
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

function decode_uri(t)
{
  return unescape(t.toString().replace(/[$]/g, "%")) ;
}

function encode_uri_option(t)
{
  return encode_uri(t).replace(/_/g, '__')
    .replace(/[=]/g,'_E').replace(/:/g, '_C') ;
}

function decode_uri_option(t)
{
  return decode_uri(t).replace(/_E/g,'=').replace(/_C/g,':').replace(/__/g,'_');
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
  if ( e.altKey && e.ctrlKey )
    e.ctrlKey = false ; // XXX Because AltGr key set both!
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
  if ( window.innerWidth !== undefined )
      return window.innerWidth ;
  if ( document.documentElement
       && document.documentElement.clientWidth )
      return document.documentElement.clientWidth ;
  if ( document.body.clientWidth )
     return document.body.clientWidth ;
  return 1024 ;
}

function window_height()
{
  if ( window.innerHeight !== undefined )
      return window.innerHeight ;
  if ( document.documentElement
       && document.documentElement.clientHeight )
      return document.documentElement.clientHeight ;
  if ( document.body.clientHeight )
     return document.body.clientHeight ;
  return 768 ;
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
      {
      url = '' ;
      title = replace ;
      }
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
  return w ;
}

function new_window(data, mimetype)
{
  if ( mimetype === undefined )
    mimetype = 'text/plain' ;

  var w = window_open('untitled') ;
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

/*REDEFINE
  This function returns the URL of the student picture icon.
  30 pixel wide
*/
function student_picture_icon_url(login)
{
  if ( login )
    return url+'/=' + ticket + '/picture-icon/' + login_to_id(login) + '.JPG';
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


function catch_this_student(login)
{
  if ( confirm(_('MSG_bilan_take_student')) )
    {
      create_popup('import_div',
		   _('MSG_bilan_take_student').split("\n")[1],
		   '<iframe src="' + url + '/=' + ticket + '/referent_get/'
		   + login
		   + '" style="width:100%;height:5em">iframe</iframe>',
		   '', false) ;
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
Stats.prototype.merge = function(v)
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
} ;

Stats.prototype.add = function(v)
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
} ;

Stats.prototype.variance = function()
{
  return this.sum2/this.nr - (this.sum/this.nr)*(this.sum/this.nr)  ;
} ;

Stats.prototype.standard_deviation = function()
{
  return Math.pow(this.variance(), 0.5) ;
} ;

Stats.prototype.average = function()
{
  return this.sum / this.nr ;
} ;

Stats.prototype.mediane = function()
{
  if ( this.values.length )
    {
      this.values.sort(function(a,b){return a - b}) ;
      return this.values[Math.floor(this.values.length/2)] ;
    }
  else
    return Number(0);
} ;

Stats.prototype.uniques = function()
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
} ;

Stats.prototype.nr_uniques = function()
{
  var d = this.uniques() ;
  var j = 0 ;
  for(var i in d)
    if ( d[i] )
      j++ ;

  return j ;
} ;

Stats.prototype.histo_max = function()
{
  var maxmax = 1 ;
  for(var i=0; i<20; i++)
    if ( this.histogram[i] > maxmax ) maxmax = this.histogram[i] ;
  return maxmax ;
} ;

Stats.prototype.maxmax = function()
{
  var maxmax = this.histo_max() ;
  for(var i in this.all_values)
    if ( this.all_values[i] > maxmax ) maxmax = this.all_values[i] ;
  return maxmax ;
} ;

// The final \n is important : see update_tip_from_value
Stats.prototype.html_resume = function()
{
  return _('B_s_minimum') +':&nbsp;'  +this.min            .toFixed(3)+'<br>' +
    _('B_s_maximum') +':&nbsp;'  +this.max                 .toFixed(3)+'<br>' +
    _('B_s_average')+':&nbsp;<b>'+this.average()       .toFixed(3)+'</b><br>' +
    _('B_s_mediane') +':&nbsp;'  +this.mediane()           .toFixed(3)+'<br>' +
    _('B_s_variance')+':&nbsp;'  +this.variance()          .toFixed(3)+'<br>' +
    _('B_s_stddev')  +':&nbsp;'  +this.standard_deviation().toFixed(3)+'<br>' +
    _('B_s_sum')+' '+this.nr+' '+_('B_s_sum_2')+':&nbsp;'
    +this.sum.toFixed(3)+'\n';
} ;

Stats.prototype.normalized_average = function()
{
  return (this.average() - this.v_min) / this.size ;
} ;

Stats.prototype.nr_abi = function() { return this.all_values[abi] ; } ;
Stats.prototype.nr_abj = function() { return this.all_values[abj] ; } ;
Stats.prototype.nr_ppn = function() { return this.all_values[ppn] ; } ;
Stats.prototype.nr_nan = function() { return this.all_values[''] ; } ;
Stats.prototype.nr_pre = function() { return this.all_values[pre] ; } ;
Stats.prototype.nr_yes = function() { return this.all_values[yes] ; } ;
Stats.prototype.nr_no  = function() { return this.all_values[no] ; } ;

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

Cell.prototype.toString = function()
{
  return 'C(v=' + this.value + ',a=' + this.author + ',d=' + this.date + ',c='
    + this.comment + ',h=' + this.history + ',k=' + this._key + ')' ;
} ;

function C(value,author,date,comment,history)
{
  return new Cell(value,author,date,comment,history) ;
}

Cell.prototype.save = function()
{
  this._save = this.value ;
} ;

Cell.prototype.restore = function()
{
  this.set_value_real(this._save) ;
} ;

Cell.prototype.value_html = function()
{
  return html(this.value) ;
} ;

function tofixed(n)
{
  return (Math.floor(n*100+0.0000001)/100).toFixed(2) ;
}
/*REDEFINE
  This function translates a english formatted number into the local format.
  Currently only used by column export.
*/
function local_number(n)
{
  if ( server_language == 'fr' )
    return n.replace('.',',') ;
  else
    return n ;
}


Cell.prototype.value_fixed = function()
{
  var v = Number(this.value) ;
  if ( isNaN(v) )
    return html(this.value) ;
  else
    if ( this.value === '' )
      return '' ;
    else
      return tofixed(v) ;
} ;

Cell.prototype.comment_html = function()
{
  return html(this.comment).replace(/\n/g, '<br>') ;
} ;

Cell.prototype.changeable = function(column)
{
  if ( ! table_attr.modifiable )
      return _("ERROR_table_read_only") ;
  if ( column.locked )
      return _("ALERT_locked_column") ;
  if ( this.author === '*' && this.value !== '')
    return _("ERROR_value_not_modifiable") + '\n'
      + _("ERROR_value_system_defined") ;
  if ( i_am_the_teacher )
    return true ;

  var r ;
  if ( column.cell_writable === '' )
    r = this.is_mine() ;
  else
    r = column.cell_writable_filter(this) ;

  if ( r )
    return true ;
  else
    return _("ERROR_value_defined_by_another_user") + table_attr.masters;
} ;

Cell.prototype.modifiable = function(column)
{
  return this.changeable(column) === true ;
} ;

Cell.prototype.is_mine = function()
{
  return (this.author== my_identity|| this.author === '' || this.value === ''
	  || myindex(minors, this.author) != -1
	  ) ;
} ;

Cell.prototype.set_value_real = function(v)
{
  this.value = v ;
  this._key = undefined ;
  login_to_line_id.dict = undefined ; // Clear cache
  return this ; // To be compatible with Python set_value method
} ;

Cell.prototype.set_value = function(value)
{
  if ( this.history !== '' || this.value !== '' )
     this.history += this.value + '\n('+ this.date + ' ' + this.author + '),·';
  this.set_value_real(value) ;
  this.author = my_identity ;
  var d = new Date() ;
  this.date = '' + d.getFullYear() +
    two_digits(d.getMonth()+1) +
    two_digits(d.getDate()) +
    two_digits(d.getHours()) +
    two_digits(d.getMinutes()) +
    two_digits(d.getSeconds()) ;
  return this ;
} ;

Cell.prototype.set_comment = function(v)
{
  this.comment = v ;
} ;

Cell.prototype.is_not_empty = function()
{
  return this.value.toString() !== '' || this.comment !== '' ;
} ;

Cell.prototype.is_empty = function()
{
  return this.value.toString() === '' && this.comment === '' ;
} ;

function get_author(author)
{
  if ( author === '' )
    return '' ;
  if ( author === '*' )
    return 'tomuss' ;
  if ( author === '?' )
    return '?' ;

  return author ;
}

function get_author2(column)
{
  return get_author(column.author);
}


Cell.prototype.get_author = function()
{
  return get_author(this.author) ;
} ;

// Allow to sort correctly and intuitivly mixed data types
Cell.prototype.key = function(empty_is)
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
} ;

function js(t)
{
  return '"' + t.toString().replace(/\\/g,'\\\\')
    .replace(/"/g,'\\"').replace(/\n/g,'\\n')
    + '"' ;
}

function js2(t)
{
  return "'" + t.toString().replace(/\\/g,'\\\\')
    .replace(/'/g,"\\'").replace(/[\n\r]/g,'\\n').replace(/"/g,'\\042')
    + "'" ;
}

Cell.prototype.get_data = function()
{
  var v ;
  if ( this.value.toFixed )
    v = this.value ;
  else
    v = js(this.value) ;
  return 'C(' + v + ',' + js(this.author) + ',' + js(this.date) + ',' + js(this.comment) + ')' ;
} ;

Cell.prototype.date_DDMMYYYY = function()
{
   var x = this.date ;
   return x.slice(6, 8) + '/' + x.slice(4, 6) + '/' + x.slice(0, 4) ;
} ;

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
  this.save_interval = 60000 ;
  this.close_if_unused = this.save_interval ;
  this.ping_interval = 5 * this.save_interval ;
  this.start_o = new Date() ;
  this.last_close=this.last_ping=this.last_interaction=this.start = millisec();
}

GUI_record.prototype.save = function()
{
  if ( ! window.gui_record )
    return ;
  if ( this.events.length == 0 )
    return ;
  var s = [] ;
  for(var i in this.events)
    if ( this.events[i][0] !== undefined ) // XXX it may happen: but how?
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
  setInterval(GUI_save, this.save_interval) ;
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
  try { connection_state.reconnect() ; } catch(e) { } ;
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
  var now = millisec() ;
  if ( ! connection_state.connection_open )
    {
      if ( now - GUI.last_ping > GUI.ping_interval )
	{
	  // To keep the table loaded on server side
	  // in order to keep the resync buffer.
	  connection_state.reconnect_real() ;
	  GUI.last_ping = now ;
	  GUI.last_close = now - 1 ;
	}
      else
	{
	  if ( now - GUI.last_ping > GUI.save_interval / 10
	       && GUI.last_close < GUI.last_ping )
	    {
	      // No answer to the last ping
	      click_to_revalidate_ticket() ;
	      GUI.last_close = now ;
	    }
	}
      return ;
    }
  GUI.save() ;
  if ( now - GUI.last_interaction > GUI.close_if_unused )
    {
      // Do not close immediatly to let read the data
      if ( now - GUI.last_ping > 1000 )
	{
	  connection_state.close_connection() ;
	  GUI.last_close = now ;
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
	    if ( preferences.debug_table )
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
	  if ( preferences.debug_table )
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
Current.prototype.update_column_headers = function()
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
} ;

Current.prototype.update_cell_headers = function()
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
  t_editor.value = cell.value ;
  t_editor.disabled = !cell.modifiable(this.column) ;
} ;

Current.prototype.update_table_headers = function()
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
	  || myindex(table_attr.managers, my_identity) != -1 ;
      else
	editable = !attributes.need_authorization || !disabled  ;
      update_attribute_value(e, attributes, table_attr, editable) ;
    }
} ;

Current.prototype.update_headers_real = function()
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
} ;

Current.prototype.update_headers = function()
{
  periodic_work_add(this.update_headers_real.bind(this)) ;
}

Current.prototype.jump = function(lin, col, do_not_focus, line_id, data_col)
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
      setTimeout(this.focus.bind(this),100) ; // For Opera
      this.focus() ;
    }
  this.update_headers() ; //this.previous_col == this.col) ;

  // Remove a copy bug of Firefox that insert tag when copying
  while( this.input_div.firstChild.tagName != 'INPUT' )
    this.input_div.removeChild(this.input_div.firstChild) ;

  table_highlight_column() ;
} ;

Current.prototype.jump_if_possible = function(line_id, data_col, do_not_focus)
{
  var td = td_from_line_id_data_col(line_id, data_col) ;
  if ( td )
    this.jump(lin_from_td(td), col_from_td(td), do_not_focus) ;
}

Current.prototype.focus = function()
{
  //this.input.contentEditable = this.cell.modifiable() ;
  this.input.focus() ;
  if ( this.input.select )
    this.input.select() ;
  this.input_div_focus() ;
} ;

Current.prototype.cell_modifiable = function()
{
  return this.cell.modifiable(this.column) ;
} ;
   
// Update input from real table content (external change)
Current.prototype.update = function(do_not_focus)
{
  var lin, col ;

  lin = this.lin ;
  col = this.col ;

  if ( lin >= table_attr.nr_lines + nr_headers )
    lin = table_attr.nr_lines + nr_headers - 1 ;
  if ( col >= table_attr.nr_columns - 1 )
    col = table_attr.nr_columns - 1 ;

  this.jump(lin, col, do_not_focus) ;
} ;

Current.prototype.cursor_down = function()
{
  this.change() ;
  if ( this.lin == table_attr.nr_lines + nr_headers - 1 )
    {
      next_page(true, 1) ;
      // table_fill_try() ; // Want change NOW (bad input if fast typing)
    }
  else
    this.jump(this.lin + 1, this.col) ;
} ;

Current.prototype.cursor_up = function()
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
} ;

Current.prototype.cursor_right = function()
{
  this.change() ;

  if ( this.col == table_attr.nr_columns - 1 )
    next_page_horizontal() ;
  else
    this.jump(this.lin, this.col + 1) ;
} ;

Current.prototype.cursor_left = function()
{
  this.change() ;
  if ( this.col === 0 || ( column_offset !== 0 && this.col == nr_freezed() ) )
    previous_page_horizontal() ;
  else
    this.jump(this.lin, this.col - 1) ;  
} ;

function control_f()
{
  select_tab("cellule", _("TAB_cell")) ;
  linefilter.focus() ;
  if (linefilter.select)
    linefilter.select();  
}

function focus_on_cell_comment()
{
  select_tab("cellule", _("TAB_cell")) ;
  the_comment.focus() ;
}

Current.prototype.focus_on_editor = function()
{
  document.getElementById("t_editor").value = this.input.value;
  select_tab("cellule", "✎") ;
  document.getElementById("t_editor").focus() ;
} ;

function triggerKeyboardEvent(el, keyCode)
{
    var eventObj = document.createEventObject
      ? document.createEventObject()
      : document.createEvent("Events") ;
  
    if(eventObj.initEvent){
      eventObj.initEvent("keydown", true, true) ;
    }
  
    eventObj.keyCode = 0 ;
    eventObj.which = 0 ;
    eventObj.charCode = keyCode ;
    eventObj.target = el ;

    if ( el.dispatchEvent )
      el.dispatchEvent(eventObj) ;
    else
      el.fireEvent("onkeydown", eventObj) ;
}

function select_go_up(down)
{
  if ( element_focused.my_selected_index != element_focused.selectedIndex )
    {
      // The SELECT object change itself the line when using keys.
      // So do not change it ourself.
      element_focused.my_selected_index = -1 ;
      // XXX The first keystroke when SELECT is active
      // move twice on FireFox
    }
  else
    {
      var nb_item = element_focused.childNodes.length ;
      element_focused.selectedIndex = (element_focused.selectedIndex
				       + element_focused.childNodes.length
				       + (down === 1 ? 1 : -1)) % nb_item ;
      element_focused.my_selected_index = element_focused.selectedIndex;
    }
}

function select_go_down()
{
  select_go_up(1) ;
}

function select_terminate(event)
{
  event.target = element_focused ;
  element_focused.onchange(event) ;
}

function focus_on_column_filter()
{
  select_tab("column", _("TAB_column")) ;
  document.getElementById('columns_filter').focus() ;
}

function select_all_cells_with_a_comment()
{
  select_tab("table", _("TAB_table")) ;
  var f = document.getElementById('fullfilter') ;
  f.value = "#" ;
  f.focus() ;
}

function clear_line_filter()
{
  linefilter.value = '' ;
  control_f() ;
}

function focus_on_rounding()
{
  select_tab("column", _("TAB_formula")) ;
  document.getElementById('t_column_rounding').focus() ;
}

function cancel_input_editing()
{
  element_focused.value = element_focused.initial_value ;
  var a = element_focused ;
  the_current_cell.focus() ; // XXX The input value is unchanged without this
  a.focus() ;
  // Launch filter updating
  triggerKeyboardEvent(a, -1) ;
}

Current.prototype.cancel_cell_editing = function()
{
  this.input.value = this.initial_value ;
  this.input.blur() ;
  this.focus() ;
}

function cancel_select_editing()
{
  login_list_hide() ;
  if ( element_focused )
      cancel_input_editing() ;
  else
    {
      // Do not cancel the current value in order
      // to allow to enter value not in the selection list
      // cancel_cell_editing() ;
    }
}

function fill_column_with_value()
{
  fill_column() ;
  var room = Filler.filler.rooms[Filler.filler.index[0]] ;
  room.get_toggle().checked = true ;
  room.get_name().value = the_current_cell.input.value ;
  room.get_name().focus() ;
  room.get_name().select() ;
  Filler.filler.update_html() ;
}

var last_input_key_time ;

/*
  First selector indicate:
    S Shift pressed
    C Control pressed
    A Alt pressed
    P Popup opened
    F last_user_interaction - last_input_key_time < 10
    T The focus is on the table
    i The focus is on a table cell (in_input===true)
    t The focus is on a TEXTAREA
    s The focus is on a SELECT
    f The focus is on #table_forms_keypress
    L The cursor is at the left of the input
    R The cursor is at the right of the input
    M The current cell is modifiable
  If prefixed by a '!' then the condition must be false

  Second selector is a list of key or keycode.
  If undefined all the keycode are accepted

  The last item is the function to call (first argument is the event)
  When it is called, no more tests are done and the event is cancelled.
  If there is no function: nothing is done and the event is not stopped.
*/
var shortcuts ;

function init_shortcuts()
{
  if ( shortcuts )
    return ;
  shortcuts = [
["F", [229]],            // http://stackoverflow.com/questions/25043934
["P", [27]             , "popup_close"],
["P"],
["s", [27]             , "cancel_select_editing"],
["!T", [27]            , "cancel_input_editing"],
["T", [27]             , "cancel_cell_editing"],
["t"],
["f"],                   //  key < 41 && key != 27 : return
["s", [38]             , "select_go_up"],
["Ss", [9]             , "select_go_up"],
["s", [40, 9]          , "select_go_down"],
["s", [13]             , "select_terminate"],
// ["s", undefined        ],  // key < 40 && key != 8 : return
["C", [33, 34]],         //  Do not touch control next/previous page
["A", [33]             , "previous_page_horizontal"],
["A", [34]             , "next_page_horizontal"],
["A", ['1', '&', '7']  , "toggle_display_tips"],
["A", ['8','_','m','½'], "control_f", "deprecated"],
["A", [0, 16]          , "test_nothing"],
["A", [":", ";", "¿"]  , "focus_on_cell_comment"],
["A", [13]             , "focus_on_editor"],
["C", [13, "D"]        , "fill_column_with_value"],
["!T", [37, 39]],        // Do not touch left/right cursor
["S", [37, 39]],         // Do not touch left/right cursor
["A", [37, 39]],         // Do not touch left/right cursor
["C", ["F"]            , "control_f"],
["C", ["P"]            , "print_selection"],
["SC", ["0"]           , "select_all_cells_with_a_comment"],
["C", ["0"]            , "focus_on_column_filter"],
["SC", ["(", '5', '9'] , "clear_line_filter"],
["SC", ["!","$","%",161,164,165], "focus_on_rounding"],
["C", [38]             , "first_page"],
["", [38]              , "cursor_up"],
["C", [40]             , "last_page"],
["", [40]              , "cursor_down"],
["S", [13]             , "cursor_up"],
["", [13]              , "cursor_down"],
["", [33]              , "previous_page"],
["", [34]              , "next_page"],
["Si", [9]             , "cursor_left"],
["i", [9]              , "cursor_right"],
["C", [37]             , "cursor_left"],
["C", [39]             , "cursor_right"],
["L", [37]             , "cursor_left"],
["R", [39]             , "cursor_right"],
["S", [113]            , "focus_on_cell_comment"],
["C"],
["!M", undefined       , "test_nothing"], // Stop event
		 ] ;
}

function display_short_cuts()
{
  var t = [] ;
  init_shortcuts() ;
  for(var i in shortcuts)
    {
      var shortcut = shortcuts[i] ;
      if ( shortcut[2] === undefined
	   || shortcut[2] === "test_nothing"
	   || shortcut[1] === undefined
	   || shortcut[0].match(/[a-zFTLR]/)
	   || shortcut[3]
	   )
	continue ;
      var key = shortcut[1][0] ;
      switch(key)
	{
        case   9: key = '⇥'  ; break ;
        case  27: key = 'Esc'; break ;
        case  13: key = '⏎'  ; break ;
        case  33: key = '⎗'  ; break ;
        case  34: key = '⎘'  ; break ;
        case  37: key = '←' ; break ;
        case  38: key = '↑'  ; break ;
        case  39: key = '→' ; break ;
        case  40: key = '↓'  ; break ;
        case 113: key = 'F2' ; break ;
	}
      t.push([_('SHORTCUT_' + shortcut[2]),
	      shortcut[0].replace('C', 'Ctrl ').replace('S', 'Shft ')
	      .replace('A', 'Alt ').replace(/[P]/, ''),
	      key]) ;
    }
  t.sort() ;
  var s = '' ;
  for(var i=0; i<t.length; i++)
    {
      for(var j=i+1; j<t.length; j++)
	if ( t[i][0] != t[j][0] )
	  break ;
	else
	  t[j][0] = undefined ;
      s += '<tr><td class="modifier">' + t[i][1]
	+ '<td class="key">' + t[i][2]
	+ (t[i][0] ? '<td rowspan="' + (j-i) + '">' + t[i][0] : '')
	+ '</tr>' ;
    }
  return '<div class="shortcuts"><table>' + s + '</table></div>' ;
}

Current.prototype.keydown = function(event, in_input)
{
  init_shortcuts() ;
  last_user_interaction = millisec() ;
  event = the_event(event) ;
  var key = event.keyCode ;
  var selection ;
  if ( event.target.tagName === 'INPUT' )
    selection = get_selection(event.target) ;
  var fast = (last_user_interaction - last_input_key_time < 10) ;
  last_input_key_time = last_user_interaction ;
  for(var shortcut in shortcuts)
    {
      shortcut = shortcuts[shortcut] ;
      var state = true ;
      for(var selector=0; selector<shortcut[0].length; selector++)
	{
	  switch(shortcut[0].substr(selector,1))
	    {
	    case 'C': state = event.ctrlKey          ; break ;
	    case 'S': state = event.shiftKey         ; break ;
	    case 'A': state = event.altKey           ; break ;
	    case 'P': state = popup_is_open()        ; break ;
	    case 'T': state = ! element_focused      ; break ;
	    case 'i': state = in_input               ; break ;
	    case 'M': state = this.cell_modifiable() || element_focused ;
	      break ;
	    case 'F': state = fast                   ; break ;
	    case 't': state = element_focused
		&& element_focused.tagName == 'TEXTAREA' ;
		break ;
	    case 's': state = element_focused
		&& element_focused.tagName == 'SELECT' ;
		break ;
	    case 'f': state = element_focused
		&& element_focused.id == 'table_forms_keypress' ;
		break ;
	    case 'L':
	      state = this.input.value.length === 0
		|| !this.cell_modifiable()
		|| (selection && selection.start === 0
		    && (selection.end === this.input.textLength ||
			selection.end === this.input.value.length ||
			selection.end === 0)
		    ) ;
	      break ;
	    case 'R':
	      state = selection && (this.input.value.length === 0
				    || !this.cell_modifiable()
				    || this.input.textLength == selection.end
				    || this.input.value.length == selection.end
				    ) ;
	      break ;
	    case '!': break ;
	    default:
	      alert('Bug shortcut') ;
	    }
	  if ( selector>0 && shortcut[0].substr(selector-1,1) == '!' )
	    state = !state ;
	  if ( ! state )
	    {
	      // console.log("Bad selector:" + shortcut[0]) ;
	      break ;
	    }
	}
      if ( ! state )
	continue ; //  Bad selector: next shortcut
      if ( shortcut[1] !== undefined )
	{
	  state = false ;
	  for(var test_key in shortcut[1])
	    {
	      test_key = shortcut[1][test_key] ;
	      if ( test_key === key ||
		   (test_key.toLowerCase && test_key.charCodeAt(0) === key))
		{
		  state = true ;
		  break ;
		}
	    }
	}
      if ( !state )
	{
	  // console.log("Bad keys:" + shortcut[0] + ' ' + shortcut[1]) ;
	  continue ;
	}
      // console.log(shortcut[0] + "/" + shortcut[1] + '/' + (shortcut[2] ? shortcut[2] : 'undefined')) ;
      if ( shortcut[2] !== undefined )
	{
	  GUI.add_key(event, shortcut[2]) ;

	  // Use method if it exists, if not use a function
	  try      { eval("this." + shortcut[2] + "(event)") ; }
	  catch(e) { eval(shortcut[2])(event) ; }
	  stop_event(event) ;
	  return false ;
	}
      return true ;
    }
  // console.log("No selector match selection=" + selection + " key=" + key + " value.length=" + event.target.value.length ) ;

  // completion

  if ( selection
       && (key >= 48 || key == 8)
       && event.target.value.length == selection.end ) // No control code
    {
      if ( do_completion_for_this_input == undefined )
	{
	  do_completion_for_this_input = event.target ;
	  setTimeout('the_current_cell.do_completion(' + (key==8) +')', 1);
	}
    }
  return true ;
} ;

var do_completion_for_this_input ;

Current.prototype.do_completion = function(backspace)
{
  var completion, completions = [] ;
  var input = do_completion_for_this_input ;

  do_completion_for_this_input = undefined ;

  if ( input == this.input || input.id == "table_forms_keypress" )
    {
      if ( this.column.type == 'Login' )
	{
	  login_list_ask() ;
	  return ;
	}

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
	  if ( completion != input.value )
	    completions.push([completion, "", "", "", completion]) ;
	}
    }
  else if ( input.id == 't_column_columns'
	    || input.id == 't_column_groupcolumn')
    {
      var names = input.value.split(' ') ;
      var last = names[names.length-1].toLowerCase() ;
      for(var column in columns)
	{
	  if ( column_empty(column) )
	    continue ;
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
	      // Done this way to right scroll when there is a long value
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
} ;

var current_change_running = false ;

/*REDEFINE
  This function returns true if the student ID is missing on the line.
  It is called for each interactive cell change.
  If 'true' is returned, an alert is displayed to the user.
*/
Current.prototype.missing_id = function(value)
{
  return (this.data_col !== 0
	  && lines[this.line_id][0].is_empty()
	  && value !=='') ;
} ;


Current.prototype.input_div_focus = function()
{
  if ( this.focused )
    this.input_div.style.border = "3px solid blue" ;
  else
    this.input_div.style.border = "3px solid gray" ;  
} ;

Current.prototype.change = function(value)
{
  this.input_div_focus() ;
  
  if ( this.blur_disabled )
    return ;

  hide_the_tip_real(true) ; // To hide the enumeration menu

  // Save modification in header before moving.
  if ( element_focused !== undefined )
    {
      if ( element_focused.blur )
	element_focused.blur() ;
    }
  if ( value === undefined )
    value = this.input.value ;
  
  if ( value == this.initial_value )
    return ;

  // Because the function can popup an alert that remove focus from cell
  // This function must be ran only once
  if ( current_change_running )
    return ;

  value = value.replace(/^[ \t]*/,'').replace(/[ \t]*$/,'') ;
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
} ;

Current.prototype.toggle = function()
{
  var toggle = this.column.real_type.ondoubleclick ;
  if ( toggle === undefined )
    return ;
  var value = toggle(this.input.value, this.column) ;
  if ( this.td.className.search('ro') != -1 )
    return ;
  this.input.value = value ;
  this.change() ;
  this.update() ;
} ;
