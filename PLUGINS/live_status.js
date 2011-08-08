var font_size = 14 ;
var move_speed = 0.0002 ;
var remove_time = 60*10 ; // 10 minutes inactivity : remove item
var highlight_time = 60 ; // Highlight the first 60 seconds
var normal_time    = 5*60 ; // Normal the first 5 minutes
var nr_points_in_graph = 1000 ; // The graph with time x axis
var graph_width = 500 ; // Graph width (should be same as in live_status.svg)
var max_number_of_action = 100 ; // To not freeze SVG
var root = document.getElementById('root') ;
var links = root.childNodes[0] ;
var nodes = root.childNodes[1] ;

if ( false )
  {
    remove_time /= 60 ;
    normal_time /= 60 ;
    highlight_time /= 60 ;
    move_speed *= 10 ;
  }

var templat = document.getElementById('templat') ;
var ticket_template = document.getElementById('ticket') ;
var node_template   = document.getElementById('node') ;
var table_template  = document.getElementById('table') ;
var link_template   = document.getElementById('link') ;
var action_template = document.getElementById('action') ;
var tspan_template  = document.getElementById('tspan') ;

var graphes ;
var graphes_data ;

var s = '' ;
for(var i in semesters)
  {
    s += 'g.' + semesters[i] + ' rect { fill: ' + semesters_color[i] + '; }\n';
  }
document.getElementById('computed').textContent = s ;


function g(x)
{
  var p, p_splited, g, s, gd ;
  if ( graphes === undefined )
    {
      graphes = [document.getElementById('data1'),
		 document.getElementById('data2'),
		 document.getElementById('data3')
		 ] ;
      graphes_data = [[],[],[]] ;
    }
  for(var ii in graphes)
    {
      g = graphes[ii] ;
      gd = graphes_data[ii] ;
      gd.push(-x[ii]);
      if ( gd.length > nr_points_in_graph+1 )
	gd.splice(0,1) ;
      s = '' ;
      for(var i in gd)
	s += ' ' + graph_width/nr_points_in_graph*i + ',' + gd[i] ;
      g.setAttribute('points', s) ;
    }
}


function debug(e, only, eject)
{
  var s = "" ;
  for(var a in e)
    {
      if ( only !== undefined && a.indexOf(only) == -1 )
	continue ;
      if ( eject !== undefined && a.indexOf(eject) != -1 )
	continue ;
      s += a + "=" + e[a] + "\n" ;
    }
  alert(s) ;
}


function rect_move(g, x, y)
{
  g.setAttribute('transform', 'translate(' + (x-g.w/2) + ',' + (y-g.h/2)
		 + ')') ;
  g.x = x ;
  g.y = y ;    
}

function new_rect(type, x, y, w, h, text, where, size_of_font)
{
  if ( size_of_font === undefined )
    size_of_font = font_size ;

  var g = type.cloneNode(true) ;
  g.w = w ;
  g.h = h ;
  rect_move(g, x, y) ;

  var r = g.firstChild ;
  r.setAttribute('width', w) ;
  r.setAttribute('height', h) ;
  r.setAttribute('stroke', 'black') ;

  var t = g.childNodes[1] ;
  // t.setAttribute('x', w/2) ;
  t.setAttribute('y', h/2 + size_of_font/2) ;
  t.setAttribute('font-size', size_of_font) ;
  text = text.split('\n') ;
  if ( text.length == 1 )
      t.textContent = text ;
  else
      {
      for(var i in text)
         t.childNodes[i].textContent = text[i] ;
      }
     

  if ( where === undefined )
    nodes.appendChild(g) ;
  else
    where.appendChild(g) ;
  return g ;
}

function link_move(g)
{
  var r = g.firstChild ;
  var a = g.a ;
  var b = g.b ;
    
  r.setAttribute('x1', a.x) ;
  r.setAttribute('y1', a.y) ;
  r.setAttribute('x2', b.x) ;
  r.setAttribute('y2', b.y) ;    
}

function new_link(a, b, length)
{
  var g = link_template.cloneNode(true) ;
  if ( length === undefined )
    length = window.innerWidth/20 ;
  g.length = length ;
  g.a = a ;
  g.b = b ;
  link_move(g) ;
  links.appendChild(g) ;
  return g ;
}

var nr_of_nodes = 0 ;
var table_nodes = {} ;
var table_links = {} ;
var table_action = [] ;

function move(a, b, dist_min, dist_max)
{
  var x1, y1, x2, y2, vx, vy, d, m ;

  x1 = a.x ;
  y1 = a.y ;
  x2 = b.x ;
  y2 = b.y ;
  vx = x2 - x1 ;
  vy = y2 - y1 ;
  d = Math.pow(vx * vx  +  vy * vy, 0.5) ;
  if ( d > dist_max )
    m = -move_speed * (d - dist_max) ;
  else if ( d > dist_min )
    return ;
  else
    m = move_speed * (dist_min - d) ;

  a.dx -= vx*m ;
  a.dy -= vy*m ;
  b.dx += vx*m ;
  b.dy += vy*m ;
}


var last_used_tspan = 0 ;

function action_move(d)
{
  var t ;
  var j ;
  var ts ;

  j = 0 ;
  for(var ii in table_action)
    {
      i = table_action[ii] ;
      t = (d - i.t)/i.duration ;

      if ( t < 1 )
	{
	  if ( j == max_number_of_action )
	    break ;

	  ts = action_template.childNodes[j] ;
	  if ( ts === undefined )
	    {	      
	      action_template.appendChild(tspan_template.cloneNode(true)) ;
	      ts = action_template.childNodes[j] ;
	    }
	  ts.textContent = i.action ;
	  ts.setAttribute('x', i.a.x + t * (i.b.x - i.a.x)) ;
	  ts.setAttribute('y', i.a.y + t * (i.b.y - i.a.y)) ;
	  ts.setAttribute('style', '') ;
	  j++ ;
	  
	}
      else
	{
	  if ( i.c )
	    {
	      i.a = i.b ;
	      i.b = i.c ;
	      i.c = undefined ;
	      i.t = d ;
	      i.duration /= 2 ;
	      return ;
	    }
	  delete table_action[ii];
	}
    }
  for(var i=j; i<last_used_tspan; i++)
    {
      action_template.childNodes[i].setAttribute('style', 'display:none') ;
    }
  
  last_used_tspan = j ;
}

function highlight(obj, unused_time)
{
  if ( unused_time < highlight_time )      
    obj.setAttribute('class', 'x1');
  else if ( unused_time < normal_time )      
    obj.setAttribute('class', 'x2');
  else if ( unused_time < remove_time )      
    obj.setAttribute('class', 'x3');
  else
    obj.setAttribute('class', 'x4');
}

function compute()
{
  var dd = millisec() ;
  var unused_time, dx, dy, distance, m ;

  // Nodes go away from center, but not too much if it is an IP
  for(var g in table_nodes)
    {
      dx = table_nodes[g].x - window.innerWidth/2 ;
      dy = table_nodes[g].y - window.innerHeight/2 ;
      distance = Math.pow(dx * dx + dy * dy, 0.5) ;
      if ( table_nodes[g].is_node )
	{
	  m = distance - window.innerHeight/8 ;
	  if ( m > 0 )
	    {
	      m = Math.pow(m, 1);
	      dx *= -m ;
	      dy *= -m ;
	    }
	}
      else
	if ( distance > 10000 )
	  table_nodes[g].used = 0 ; // Will kill it
      table_nodes[g].dx = dx / distance ;
      table_nodes[g].dy = dy / distance ;
    }
  // Nodes try to get away from the other nodes.
  nr_of_nodes = 0 ;
  for(var g in table_nodes)
    {
      unused_time = (dd - table_nodes[g].used) / 1000 ;
      if ( unused_time > remove_time )
        {
	  table_nodes[g].parentNode.removeChild(table_nodes[g]) ;
	  table_nodes[g].is_deleted = true ;
	  delete table_nodes[g] ;
	  continue ;
	}
      nr_of_nodes++ ;
      highlight(table_nodes[g].firstChild, unused_time) ;
      for(var h in table_nodes)
	{
	  if ( h > g )
	    {
	      move(table_nodes[g], table_nodes[h], 100, 1000000) ;
	    }
	}     
    }

  // Links between push or pull them depending on distance
  for(var link in table_links)
    {
      link = table_links[link] ;
      move(link.a, link.b, link.length, link.length) ;
    }

  var n = table_nodes['N'] ;
  if ( n )
    {
      n.dx = n.dy = 0 ;
      n.x = window.innerWidth / 2 ;
      n.y = window.innerHeight / 2 ;
    }
  var n = table_nodes[''] ;
  if ( n )
    {
      n.dx = n.dy = 0 ;
      n.x = window.innerWidth / 2 ;
      n.y = 20 ;
    }
  var n = table_nodes['/LDAP'] ;
  if ( n )
    {
      n.dx = n.dy = 0 ;
      n.x = 150 ;
      n.y = 150 ;
    }
  var n = table_nodes['/LDAP2'] ;
  if ( n )
    {
      n.dx = n.dy = 0 ;
      n.x = 150 ;
      n.y = window.innerHeight - 150 ;
    }
  var n = table_nodes['/LDAP3'] ;
  if ( n )
    {
      n.dx = n.dy = 0 ;
      n.x = window.innerWidth - 150 ;
      n.y = window.innerHeight - 150 ;
    }
  var n = table_nodes['/BaseIP'] ;
  if ( n )
    {
      n.dx = n.dy = 0 ;
      n.x = window.innerWidth - 150 ;
      n.y = 150 ;
    }

  for(var g in table_nodes)
    {
      g = table_nodes[g] ;
      rect_move(g, g.x + g.dx, g.y + g.dy) ;
    }
  
  for(var i in table_links)
    {
      unused_time = (dd - table_links[i].used) / 1000 ;      
      if ( table_links[i].a.is_deleted || table_links[i].b.is_deleted )
	{
	  table_links[i].parentNode.removeChild(table_links[i]) ;
	  delete table_links[i] ;
	  continue ;
	}
      highlight(table_links[i].firstChild, unused_time) ;
      link_move(table_links[i]) ;
    }
  
  action_move(dd) ;
}


setInterval(compute, 100) ;

function update_time(node, action, dd)
{
  if ( action == 'pong' )
    {
      if ( dd - node.used > normal_time*1000 )
	node.used = dd - normal_time*1000 ;
    }
  else
    node.used = dd ;
}

// Indicate the 'ticket' (LDAP requester) as busy
function b(ticket)
{
  var n = table_nodes[ticket] ;
  if ( n )
    {
      n.firstChild.setAttribute('style', 'fill: #F00') ;
    }
}

// Release lock
function r(ticket)
{
  var n = table_nodes[ticket] ;
  if ( n )
    n.firstChild.setAttribute('style', '') ;
}

function d(ip, ticket, access_right, time, action, year, semester, ue)
{
  var dd = millisec() ;
  var w = window.innerWidth ;
  var h = window.innerHeight ;
  var x, y ;

  if ( table_nodes[ip] === undefined )
    {
      var angle = 0 ;
      var numbers = ip.split('.') ;
      for(var i in numbers)
	angle += numbers[i] ;
      if ( isNaN(angle) )
	angle = 0 ;
      else
	angle = Math.PI * (angle % 360) / 180.

      table_nodes[ip] = new_rect(node_template,
				 w/2 + w/8*Math.sin(angle),
				 h/2 + h/8*Math.cos(angle),
				 font_size*8, font_size+6, ip) ;
      table_nodes[ip].is_node = true ;
    }
  update_time(table_nodes[ip], action, dd) ;
  if ( table_nodes[ticket] === undefined )
    {
      if ( table_nodes[ip] )
	{
	  x = 2*(table_nodes[ip].x - w/2) + w/2 + Math.random()*10 ;
	  y = 2*(table_nodes[ip].y - h/2) + h/2 ;	  
	}
      else
	{
	  x = Math.random()*w ;
	  y = h / 2 ;
	}
      var t = ticket.split('/')[1] ;
      if ( t === undefined )
	t = '' ;
      table_nodes[ticket] = new_rect(ticket_template, x, y,
				     font_size*(t.length+1)/2,2*font_size+4,
				     t + '\n' + access_right) ;
      if ( access_right.search(/R/) != -1 )
	{
	  table_nodes[ticket].setAttribute('class', 'ticket_root') ;
	}
      else if ( access_right.search(/[JR]/) != -1 )
	{
	  table_nodes[ticket].setAttribute('class', 'ticket_abj') ;
	}
      else if ( access_right.search(/T/) != -1 )
	{
	  table_nodes[ticket].setAttribute('class', 'ticket_teacher') ;
	}
    }
  update_time(table_nodes[ticket], action, dd) ;
  r(ticket) ;

  var full_ue = year + '/' + semester + '/' + ue ;
  if ( ue && table_nodes[full_ue] === undefined )
    {
      if ( table_nodes[ticket] )
	{
	  x = 1.1*(table_nodes[ticket].x - w/2) + w/2 + Math.random()*10 ;
	  y = 1.1*(table_nodes[ticket].y - h/2) + h/2 ;	  
	}
      else
	{
	  x = Math.random()*w ;
	  y = h / 2 ;
	}

      table_nodes[full_ue] = new_rect(table_template, x, y,
				      font_size*8, 3*font_size+4,
				      year + '\n' + semester + '\n' + ue) ;
      table_nodes[full_ue].is_table = true ;
      table_nodes[full_ue].setAttribute('class', semester) ;
    }
  if ( ue )
    update_time(table_nodes[full_ue], action, dd) ;
  var link = ip + '/' + ticket ;
  if ( table_links[link] === undefined )
    table_links[link] = new_link(table_nodes[ip], table_nodes[ticket]) ;
  update_time(table_links[link], action, dd) ;

  if ( ue )
    {
      link = ticket + '/' + full_ue ;
      if ( table_links[link] === undefined )
	table_links[link] = new_link(table_nodes[ticket],
				     table_nodes[full_ue],1);
      update_time(table_links[link], action, dd) ;
    }
  var a = [] ;
  a.a = table_nodes[ip] ;
  a.b = table_nodes[ticket] ;
  a.c = table_nodes[full_ue] ;
  a.t = dd ;
  a.action = action ;
  a.duration = 50 * Math.pow(1000000*time, 0.5) ;
  table_action.push(a) ;

  if ( nr_of_nodes >= 2 )
    {
      font_size = 15 - Math.log(nr_of_nodes) / Math.log(2) / 2 ;
    }
}

