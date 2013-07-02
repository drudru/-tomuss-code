// -*- coding: utf-8 -*-
/*
  TOMUSS: The Online Multi User Simple Spreadsheet
  Copyright (C) 2010-2011 Thierry EXCOFFIER, Universite Claude Bernard

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

document.write('<div class="menu">'
	       + '<p class="search"><b>Chercher le texte :</b><br><input id="input" onkeypress="key_pressed(event)" onkeydown="key_pressed(event)"></p>'
	       + '<div id="menu"></div>'
	       + '<div id="log"></div>'
	       + '</div>') ;


var last_key_time = 0 ;
var display = false ;
var input = document.getElementById('input') ;
var log = document.getElementById('log') ;
var divs = document.getElementsByTagName('DIV') ;
var menu = document.getElementById('menu') ;

function millisec()
{
  var d = new Date() ;
  return d.getTime() ;
}

function window_height()
{
  var height = window.innerHeight ;
  if ( height === undefined )
    return document.body.clientHeight ;
  return height ;
}


function diacritics_regex(s)
{
  var diacritics = [
		   "[aA\300-\306\340-\346]",
		   "[eE\310-\313\350-\353]",
		   "[iI\314-\317\354-\357]",
		   "[oO\322-\330\362-\370]",
		   "[uU\331-\334\371-\374]",
		   "[nN\321\361]",
		   "[cC\307\347]"
		   ];

  for (var i = 0; i < diacritics.length; i++)
    {
      s = s.replace(RegExp(diacritics[i], "g"), diacritics[i]);
    }
  return s ;
}

function key_pressed(event)
{
  if ( event === undefined )
    event = window.event ;
  if ( event.keyCode == 34 && event.type == 'keydown')
    {
      window.scrollBy(0, window_height()); 
    }
  if ( event.keyCode == 33 && event.type == 'keydown' )
    {
      window.scrollBy(0, -window_height()); 
    }
  display=true ;
  last_key_time = millisec() ;

  if ( input.value != input.old_value && input.value !== '' )
    {
      setTimeout(function() {
		   document.body.scrollTop = 0 ;
		 }, 100) ;
    }
}
function go_hash(name, keep_filter)
{
  if ( ! keep_filter )
  {
    input.value = '' ;
    filter() ;
    display = true ;
  }
  
  setTimeout(function() {
		   window.location.hash = name ;
		   set_current() ;
		   input.focus() ;
		 }, 1) ;
}

function go(name)
{
  if ( name.substr(0,1) == '#' )
    {
      var m = menu.childNodes[Number(name.substr(2))] ;
      var keep_filter = m.className.indexOf('unselected') == -1 ;
      go_hash(name, keep_filter) ;
    }
  else
    {
      input.value = decodeURI(name) ;
      document.body.scrollTop = 0 ;
      input.focus() ;
      display = true ;
    }
}

function set_current()
{
  for(var i in menu.childNodes)
    if ( menu.childNodes[i].className !== undefined )
      if ( window.location.hash == '#n' + i )
	menu.childNodes[i].className += ' current' ;   
      else
	menu.childNodes[i].className = menu.childNodes[i].className.replace(/ current/g, '') ;

  update_scrollbar(true);
}

var last_scrolltop = -1 ;
var fixed_bug = false ;

function update_scrollbar(forced)
{
  var child ;

  if ( forced != true && last_scrolltop == document.body.scrollTop )
    return ;
  last_scrolltop = document.body.scrollTop ;

  if ( !fixed_bug && menu.parentNode.offsetTop != 0 )
    {
      fixed_bug = true ;
      document.body.scrollTop = 0 ;
    }

  if ( fixed_bug )
    {
      menu.parentNode.style.position = 'absolute' ;
      menu.parentNode.style.top = last_scrolltop ;
    }
  for(var i in menu.childNodes)
    {
      var child = menu.childNodes[i] ;
      if ( ! child.getAttribute )
	continue ;
      i = divs[Number(child.getAttribute('the_div'))] ;  
      // Why the className is missing on first H1 ????
      if ( child.className === undefined )
	child.className = '' ;

      if ( i.offsetTop + i.offsetHeight > document.body.scrollTop &&
	   i.offsetTop < document.body.scrollTop + window_height() )
	child.className += ' onscreen' ;
      else
	child.className = child.className.replace(/ onscreen/g,'') ;
    }
}

function insert_highlight(element, content, pattern, pattern_safe)
{
  element.innerHTML = content.replace(RegExp('(>[^<]*)(' +pattern+ ')', 'mgi'),
	                              '$1<span class="filter">$2</span>') ;
}

function filter()
{
  update_scrollbar(false);

  if ( display == false )
    {
      if ( input.value !== input.old_value 
	   && input.value !== ''
	   && millisec() - last_key_time > 1000 )
	{
	  var i = document.createElement('IMG') ;
	  i.src = 'log/help/' + encodeURI(input.value) ;
	  log.appendChild(i) ;
	  input.old_value = input.value ;
	}
      return ;
    }

  display = false ;
	
	
  var v = input.value ;
	
  if ( v === '' )
    {
      // Restore initial state
      for(var i in text_divs)
	{
	  text_divs[i].style.display = '' ;
	  if ( menu.childNodes[i] )
	    menu.childNodes[i].className = 'unselected' ;
	  text_divs[i].innerHTML = content_divs[i] ;
	}
      set_current() ;
      return ;
    }
  // Protect special chars
  v = diacritics_regex(v.replace(/([*\\[.$+?()])/g, '\\$1')) ;
  var html ;
  var selected = [''] ;
  // Change the content
  for(var i in text_divs)
    {
      html = content_divs[i];
      div = text_divs[i];
  
      if ( html.search(RegExp(v,'gim')) == -1 )
        {
  	if ( div.id != 'menu' )
  	  {
  	    div.style.display = 'none' ;
  	    selected.push('unselected') ;
  	  }
        }
      else
        {
  	selected.push('') ;
  	div.style.display = '' ;
        }

      if ( div.id != 'menu' ) 
        {
  	  insert_highlight(div, html, v) ;
        }
      else
        // Does not work in firefox and chrome : WHY????
        for(var n in div.childNodes)
  	{
  	  if ( false && div.childNodes[n].innerHTML )
  	    {
  	      insert_highlight(div.childNodes[n],
  			       div.childNodes[n].innerHTML,
  			       v) ;
  	      break;
  	    }
  	}
    }
  // After because it was recreated
  var m ;
  for(var i in menu.childNodes)
    {
      m = menu.childNodes[i] ;
      if ( ! m.getAttribute )
        continue ;
      j = m.getAttribute('toc_number') ;
      if ( j === undefined )
        continue ;
      j = Number(j) ;
      m.className = class_divs[j] + ' ' + selected[j+1] ;
      if ( m.innerHTML !== undefined
  	 && m.innerHTML.search(RegExp(v,'gim')) != -1 )
        m.className += ' filter' ;
    }
  set_current() ;
}

var text_divs = [] ;
var content_divs = [] ;
var class_divs = [] ;

// Parse document content to create the Index of the menu

var menu_index = 0 ;
var hash_found = false ;
for(var i_div in divs)
  {
    if ( i_div == 0 )
      continue ;
    var div = divs[i_div] ;
    for(var ee in div.childNodes)
      {
        var e = div.childNodes[ee] ;
        if ( e.tagName && e.tagName.length == 2 )
          {
            text_divs.push(div) ;
            var m = document.createElement('A') ;
            m.href = 'javascript:go("#n' + class_divs.length + '");' ;
            m.innerHTML = e.innerHTML ;
            div.toc_number = class_divs.length ;
            m.setAttribute('toc_number', class_divs.length) ;
            m.setAttribute('the_div', i_div) ;
	    if ( e.tagName == 'H2' || e.tagName == 'H3'
		 || (window.level4 && e.tagName == 'H4'))
	    {
              if ( menu_index++ % 2 == 0)
		m.className = 'highlight' ;
	    }
	    else
	      m.style.display = 'none' ;
            m.className += ' ' + e.tagName ;
	    // XXX e.textContent & and " should be escaped
            e.innerHTML = '<a name="n' + class_divs.length + '">'
	      + '<a name="' + e.textContent + '">'
	      + e.innerHTML + '</a></a>' ;
	    if ( '#' + e.textContent == window.location.hash.toString()
	       || "#n" + class_divs.length == window.location.hash.toString())
	      hash_found = true ;
            class_divs.push(m.className) ;
            content_divs.push(div.innerHTML) ;
            menu.appendChild(m) ;
            break ;
          }
      }
  }
text_divs.push(menu) ;
content_divs.push(menu.innerHTML) ;

if ( window.location.hash !== '' && ! hash_found )
  {
    input.value = decodeURI(window.location.hash.toString().substr(1)) ;
  }
display = true ;

input.focus() ;

setInterval("filter()", 100) ;

if ( hash_found )
  input.old_value = input.value ;
else
  setTimeout("document.body.scrollTop = 0 ;", 200) ;
