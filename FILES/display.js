// -*- coding: utf-8; mode: Java; c-basic-offset: 2; tab-width: 8; -*-

var unload_element ;
var display_data ;
var display_do_debug = false ;
var node_to_element = {} ;

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
  if ( display_do_debug )
    console.log("==================== Display update ======================") ;
  the_body = document.getElementsByTagName('BODY')[0] ;
  var only_leaf_change = true ; // to not redraw whole screen on leaf change
  for(var i in key_values.slice())
  {
    var name = key_values[i][0] ;
    display_data[name] = key_values[i][1] ;
    if ( display_definition[name].children.length || ! node_to_element[name])
	only_leaf_change = false ;
    // Force to redraw leaves XXX DIRECTLY depending on this one
    for(var i in display_definition[name].needed_by)
    {
      var o = display_definition[name].needed_by[i] ;
      if ( display_definition[o].children.length || ! node_to_element[o] )
          only_leaf_change = false ;
      if ( display_data[o] !== undefined )
	key_values.push([o, display_data[o]]) ;
    }
  }
  display_update.top = top ;
  try { display_update_real(only_leaf_change ? key_values : undefined) ; }
  catch(e) { console.log(e) ; } ;
}

function display_create_tree()
{
   for(var i in display_definition)
     {
       var dd = display_definition[i] ;
       dd.children = [] ;
       dd.name = i ;
       dd.containers = dd[0] ;
       dd.priority = dd[1] ;
       dd.js = 'Display' + (dd[2] || i ) ;
       dd.needed_by = [] ;
       try { dd.fct = eval(dd.js) ; } catch(e) { }
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
    {
       display_definition[i].children.sort(function(a,b)
					   {return a.priority - b.priority;});
       var need = display_definition[i].need_node ;
       for(var i in need)
	      display_definition[need[i]].needed_by.push(i) ;
    }
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
  var start ;
  if ( display_do_debug )
    start = millisec() ;
  if ( node.fct === undefined )
    console.log(node) ;
  var need_node = node.fct.need_node ;
  if ( node.data === undefined && need_node === undefined)
    return '<div class="Display ' + node.name + '" style="display:none"></div>' ;
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
    content = '' ;
  else
    {
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
    }

  if ( display_do_debug )
    {
      var dt = millisec() - start ;
      if ( dt > 1 )
	console.log(node.name + ':' + dt + 'ms') ;
    }
  return content ;
}

function detect_small_screen(force)
{
  if ( !force && window_width() == detect_small_screen.window_width )
    return ;
  detect_small_screen.window_width = window_width() ;
      
  var smallscreen, width, lefts = [], div ;
  var divs = document.getElementsByTagName('DIV') ;
  var top_class = '' ;
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
  var prefs = display_data['Preferences'] || display_data['HomePreferences'] ;
  for(var item in prefs)
    if ( item != 'hide_right_column' || !smallscreen )
      top_class += ' ' + item + '_' + prefs[item] ;

  // Set the good theme
  if ( top_class.indexOf("theme_") == -1 )
    top_class = "theme_ " + top_class ;
  var s ;
  try { s = year_semester().split("/")[1] ; }
  catch(e) { s = semester ; }
  s = get_theme(s.substr(0,1)) ;
  top_class = top_class.replace(/theme_([^ ]+) /, "theme$1 ")
    .replace("theme_ ", "theme" + s + " ") ;

  if ( top_class.match("black_and_white_1") )
    top_class = top_class.replace(/theme([^ ]+) /, "themeBW ") ;

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

function display_update_real(key_values)
{
  if ( display_update.top === undefined )
    return "" ;
  if ( display_update_nb == 0 )
    setInterval(detect_small_screen, 100) ;

  if ( key_values )
  {
        for(var i in key_values)
	{
	  i = key_values[i][0] ;
	  node_to_element[i].outerHTML = display_display(display_definition[i]) ;
	}
  }
  else
  {
       document.getElementById('display_suivi').innerHTML = display_display(display_definition[display_update.top]) ;

       var divs = document.getElementById('display_suivi').getElementsByTagName("DIV") ;

       node_to_element = {} ;
       for(var i = 0 ; i < divs.length ; i++)
	 {
	    var div = divs[i] ;
	    if ( div.className.match(/\bDisplay\b/) )
	      {
		var cls = div.className.split(/ +/) ;
		for(var j = 0 ; j < cls.length ; j++ )
		  node_to_element[cls[j]] = div ;
	      }
         }
  }

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

function display_debug_information()
{
  return i_am_root ;
  return display_data['Preferences']
    && display_data['Preferences']['debug_suivi']
    || display_data['HomePreferences']
    && display_data['HomePreferences']['debug_home'] ;
}

function DisplayProfiling(node)
{
  if ( ! display_debug_information() )
    return '' ;
  var t = [] ;
  for(var i in node.data)
    t.push([node.data[i], i]) ;
  t.sort(function(a,b) { return b[0] - a[0] ; }) ;
  return hidden_txt('⌚',
		    '<!--INSTANTDISPLAY-->' + _('LINK_profiling')
		    + '<br>' + t.join('<br>')) ;
}
DisplayProfiling.need_node = [] ;

function display_display_tree(node, s)
{
  if ( node === undefined )
    {
      var s = [] ;
      for(var node in display_definition)
	{
	  node = display_definition[node] ;
	  if ( node.containers.length == 0 )
	    {
	      s.push("<ul>") ;
	      display_display_tree(node, s) ;
	      s.push("</ul><hr>") ;
	    }
	}
      new_window(s.join(''), "text/html") ;
      return ;
    }
  s.push("<li> [" + node.priority + '] <b>' + html(node.name) + '</b>'
	 + ('Display' + node.name != node.js ? ' ' + node.js : '')
	 + (display_data[node.name]
	    ? (' <span style="font-size: 70%">'
	       + html(JSON.stringify(display_data[node.name])
		      .replace(/,/g, ', ').substr(0,1000))
	       + '</span>'
	       )
	    : '')
	 )
    ;
  if ( node.children.length )
    {
      s.push("<ul>") ;
      for(var i in node.children)
	display_display_tree(node.children[i], s) ;
      s.push("</ul>") ;
    }
}

function DisplayTree(node)
{
  if ( ! display_debug_information() )
    return '' ;
  return '<a href="javascript:display_display_tree()">🌳</a>' ;
}
DisplayTree.need_node = [] ;
