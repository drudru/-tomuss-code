// -*- coding: utf-8; mode: Java; c-basic-offset: 2; tab-width: 8; -*-

var unload_element ;
var display_data ;
var display_do_debug = true ;

function start_display()
{
  display_create_tree() ;
  display_data = {} ;
  var display_suivi = document.getElementById('display_suivi') ;
  if ( ! display_suivi )
    return ; // It will be created with initialize_suivi_real

  // Protect the last DVI.display_suivi in case of multiple student display
  var p = display_suivi.parentNode ;
  display_suivi.id = '' ;
  var e = document.createElement('DIV') ;
  e.id = 'display_suivi' ;
  p.appendChild(e) ;
  column_get_option_running = true ; // Do not set option in URL
}

function display_update(key_values, top)
{
  the_body = document.getElementsByTagName('BODY')[0] ;
  for(var i in key_values)
    display_data[key_values[i][0]] = key_values[i][1] ;
  display_update.top = top ;
  try { display_update_real() ; }
  catch(e) { console.log(e) ; } ;
}

function display_create_tree()
{
   for(var i in display_definition)
     {
       display_definition[i].children = [] ;
       display_definition[i].name = i ;
       display_definition[i].containers = display_definition[i][0] ;
       display_definition[i].priority = display_definition[i][1] ;
       display_definition[i].js = 'Display'
	 + (display_definition[i][2] || i ) ;
       try {
	 display_definition[i].fct = eval(display_definition[i].js) ;
	 }
       catch(e)
	 {
	 }
     }
   for(var i in display_definition)
     for(var j=0; j<display_definition[i].containers.length; j++)
       if ( ! display_definition[display_definition[i].containers[j]
				 ])
	 alert('Unknown parent for ' + i + ' ' + j ) ;
       else
	 display_definition[display_definition[i].containers[j]
			    ].children.push(display_definition[i]) ;
   for(var i in display_definition)
       display_definition[i].children.sort(function(a,b)
					   {return a.priority - b.priority;});
}

function display_display_debug(event, txt)
{
  var t = document.getElementById('display_display_tip') ;
  if ( ! t )
    {
      var e = document.createElement('DIV') ;
      e.id = 'display_display_tip' ;
      e.style.position = 'absolute' ;
      e.style.background = '#000' ;
      e.style.color = '#FFF' ;
      e.style.opacity = 0.7 ;
      e.style.fontSize = "70%" ;
      e.style.zIndex = 10000 ;
      the_body.appendChild(e) ;
      display_display_debug.e = e ;
    }
  event = the_event(event) ;
  if ( display_display_debug.target !== event.target )
    display_display_debug.e.innerHTML = txt ;
  else
    display_display_debug.e.innerHTML += '<hr>' + txt ;
  display_display_debug.target = event.target ;
  var pos = findPos(event.target) ;
  display_display_debug.e.style.left = pos[0]+event.target.offsetWidth + 'px' ;
  display_display_debug.e.style.top = pos[1]+event.target.offsetHeight + 'px' ;
}

// The display function returns a string (html) or an array
// [ "html content",
//   ["html class1", "html class2"...],
//   ["style1", "style2"...],
//   "other attributes"]
function display_display(node)
{
  node.data = display_data[node.name] ;
  if ( node.data === "" )
    return '' ;
  if ( node.fct === undefined )
    console.log(node) ;
  var need_node = node.fct.need_node ;
  if ( node.data === undefined && need_node === undefined)
    return '' ;  
  for(var i in need_node)
    if ( display_data[need_node[i]] === undefined )
      return '' ;
  var content = node.fct(node) ;
  var classes = ['Display', node.js, node.name] ;
  var styles = [] ;
  var more = '' ;
  if ( content instanceof Array)
    {
      classes = classes.concat(content[1]) ;
      styles = styles.concat(content[2]) ;
      more = ' ' + content[3] ;
      content = content[0] ;
    }
  if ( content === '' || ! content )
    return '' ;
  if ( styles.length )
    styles = ' style="' + styles.join(';') + '"' ;
  else
    styles = '' ;

  if ( display_do_debug && content.indexOf("display_display_debug") == -1 )
    {
      var s = [] ;
      var n = node ;
      while(n)
	{
	  s.push(n.name + '(' + n.priority + ')') ;
	  n = display_definition[n.containers[0]] ;
	}
      more += ' onmouseover="display_display_debug(event,'
	+ js2(s.join('<br>')) + ')"' ;
    }
  

  content = '<div class="' + classes.join(' ') + '"' + styles + more + '>'
    + content + '</div>' ;

  return content ;
}

function detect_small_screen(force)
{
  if ( window_width() == detect_small_screen.window_width )
    return ;
  detect_small_screen.window_width = window_width() ;
      
  var smallscreen, width, lefts = [], div ;
  var divs = document.getElementsByTagName('DIV') ;
  var default_theme = "theme" + semester.substr(0,1) ;
  var top_class = the_body.className
    .replace(/ (teacher_view|student_view|hide_right_column)[^ ]*/, '')
    .replace(/theme_/, "theme")
    .replace(/theme\b/, default_theme) ;
  if ( top_class.indexOf("theme") == -1 )
    top_class += ' ' + default_theme ;
  for(i = 0 ; i < divs.length ; i++)
    {
      div = divs[i] ;
      if ( div === undefined || div.className === undefined )
	continue ;
      if ( div.className.toString().indexOf('BodyLeft') != -1 )
	{
	  lefts.push(div) ;
	  continue ;
	}
      if ( div.className.toString().indexOf('BodyRight') == -1 )
	continue ;

      if ( lefts.length != 0 )
	lefts[lefts.length-1].style.minHeight = (div.offsetHeight+50) + 'px' ;
      if ( detect_small_screen.initial_width === undefined
	   || detect_small_screen.initial_width < div.offsetWidth )
	{
	  detect_small_screen.initial_width = div.offsetWidth ;
	}
      smallscreen = detect_small_screen.initial_width / window_width() > 0.35 ;
    }
  if ( is_a_teacher )
    top_class += ' teacher_view' ;
  else
    top_class += ' student_view' ;
  if ( smallscreen )
    top_class += ' hide_right_column_1' ;
  for(var item in display_data['Preferences'])
    if ( item != 'hide_right_column' || display_data['Preferences'][item] == 1 )
      top_class += ' ' + item + '_' + display_data['Preferences'][item] ;

  // To not relaunch CSS animation
  if ( the_body && the_body.className != top_class )
    {
      the_body.className = top_class ;
      hide_rightclip() ;
    }
  smallscreen = top_class.indexOf('hide_right_column_1') != -1 ;
  detect_small_screen.small_screen = smallscreen ;
  var twidth = window_width() - (smallscreen
				? 110
				 : (detect_small_screen.initial_width + 30)
				) ; // +30 for FireFox
  if ( twidth > 100 )
    for(var i in lefts)
      lefts[i].style.maxWidth = twidth + 'px' ;
  try {
    hide_cellbox_tip() ;
  }
  catch(e)
    { } ;
}

var display_update_nb = 0 ;
var older_students = '' ;

function display_update_real()
{
  if ( display_update.top === undefined )
    return "" ;
  if ( display_update_nb == 0 )
    setInterval(detect_small_screen, 100) ;
  document.getElementById('display_suivi').innerHTML = display_display(display_definition[display_update.top]) ;

  display_update_nb++ ;
  detect_small_screen.window_width = 0 ; // Force update
  detect_small_screen() ;
}

function DisplayHorizontal(node, separator)
{
   var children = [] ;
   if ( separator === undefined )
     separator = '&nbsp;' ;
   if ( node.data !== undefined )
     children.push(node.data) ;
   var c ;
   for(var i in node.children)
     {
       c = display_display(node.children[i]) ;
       if ( c )
	 children.push(c) ;
     }
   return children.join(separator) ;
}
DisplayHorizontal.need_node = [] ;

function DisplayVertical(node)
{
  return DisplayHorizontal(node, '') ;
}
DisplayVertical.need_node = [] ;
