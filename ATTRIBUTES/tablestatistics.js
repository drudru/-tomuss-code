// -*- coding: utf-8 -*-
/*
  TOMUSS: The Online Multi User Simple Spreadsheet
  Copyright (C) 2011 Thierry EXCOFFIER, Universite Claude Bernard

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

// finir les messages d'aide.
// faire disparaitre colonne en cliquant sur le titre
// groupage par date
// graphique total

var stat_svg_height = 35 ;
var stat_svg_width = 120 ;

// all_values is a table of table of pairs(value, nr)
// There is a line per table
function a_graph(all_values, zoom)
{
  var s, all, rgb, values, max ;

  if ( zoom === undefined )
    zoom = 1 ;

  var width = stat_svg_width * zoom ;
  var height = stat_svg_height * zoom ;
  var lw = Math.pow(zoom, 0.5) ;
  var c ;
  function X(c) { return (width*(Number(c)+0.5)/values.length).toFixed(1) ; };
  function Y(c) { return (height*(1-c)).toFixed(1) ; } ;

  all = [] ;
  for(var i in all_values)
    {
      if ( zoom == 1 )
	rgb = hls2rgb(i/all_values.length, 0.3, 1) ;
      else
	rgb = '#000' ;
      s = '<path d="M ' ;
      values = all_values[i] ;
      for(c in values)
	if ( ! isNaN(values[c][0]) )
	  s += X(c) + ' ' + Y(values[c][0]) + ' L ' ;
      all.push(s.replace(/ L $/,'') + '" style="stroke-width:' + lw
	       + ';fill:none;stroke:' + rgb + '"/>\n') ;

      s = '<path d="M ' ;
      max = 0 ;
      for(c in values)
	if ( values[c][1] > max )
	  max = values[c][1] ;
      for(c in values)
	if ( ! isNaN(values[c][1]) )
	  s += X(c) + ' ' + Y(values[c][1]/max) + ' L ' ;
      all.push(s.replace(/ L $/,'') + '" style="stroke-width:' + lw +
	       ';fill:none; stroke-dasharray: ' + 2*zoom + ',' + zoom
	       + ';stroke:' + rgb + '"/>\n') ;
    }

  if ( zoom != 1 )
    {
      c = 0.1 ;
      all.push('<text transform="rotate(-90),translate(' + (-height)
	       + ')" style="font-size:70%">') ;
      for(var column in sorted_cols)
	{
	  if ( ! columns[sorted_cols[column]] )
	    continue ; // TOTAL
	  all.push('<tspan x="0" y="' + X(c) + '">'
		   + html(columns[sorted_cols[column]].title) + '</tspan>') ;
	  c += 1 ;
	}
      all.push('</text>') ;
      all.push('<path style="stroke:#F00" d="M ' + X(0) + ' ' + 3*height/4
	       + ' L ' + width + ' ' + 3*height/4 + '"/>') ;
      all.push('<path style="stroke:#888" d="M ' + X(0) + ' ' + height/2
	       + ' L ' + width + ' ' + height/2 + '"/>') ;
      all.push('<path style="stroke:#0F0" d="M ' + X(0) + ' ' + height/4
	       + ' L ' + width + ' ' + height/4 + '"/>') ;
      all.push('<text style="font-size:70%">') ;
      all.push('<tspan x="0" y="' + Y(0.25) + '">5</tspan>') ;
      all.push('<tspan x="0" y="' + Y(0.5) + '">10</tspan>') ;
      all.push('<tspan x="0" y="' + Y(0.75) + '">15</tspan>') ;
      all.push('<tspan x="0" y="' + Y(0) + '">0</tspan>') ;
      all.push('</text>') ;
    }

  svg = '<div class="s_graph"><object type="image/svg+xml;utf-8" height="'
    + height + 'px" width="' + width + 'px" data="data:image/svg+xml;utf-8,' +
    base64('<?xml version="1.0" encoding="UTF-8" standalone="no"?>' +
	   '<svg xmlns="http://www.w3.org/2000/svg" style="background:white">' +
	   '<g>' + all.join('\n') + '</g>' + '</svg>')
    + '"></object><div>' ;

  return svg ;
}

var stat_current_zoom ;
var stat_current_zoom_t ;

function stat_tip_window(t, x)
{
  var w = document.getElementById('tip') ;
  if ( stat_current_zoom_t )
    {
      if ( stat_current_zoom_t.parentNode )
	stat_current_zoom_t.parentNode.style.background = '' ;
      else
	{
	  // The object was destroyed by a content change
	  stat_current_zoom = undefined ;
	}
    }
  if ( stat_current_zoom == x )
    {
      stat_current_zoom = undefined ;
      // Not display='none' : bad first positionning because the width
      // is not computed.
      w.style.left = -10000 ;
      w.style.right = 'auto' ;
      return ;
    }
  stat_current_zoom_t = t ;
  stat_current_zoom = x ;
  t.parentNode.style.background = '#FF6' ;
  return w ;
}

function stat_flower_zoom(t, column)
{
  var w = stat_tip_window(t, column) ;
  if ( ! w )
    return ;
  w.innerHTML = stat_display_flower(stats_groups, all_stats, column, 12) ;
  set_element_relative_position(t, w) ;
  w.style.display = 'block' ;
}

function stat_display_flower(groups, all_stats, column, zoom)
{
  if ( zoom === undefined )
    zoom = 1 ;

  var width = stat_svg_height * zoom ;
  var height = stat_svg_height * zoom ;
  var v = [], stat ;
  function X(c) { return (width*c).toFixed(1) ; } ;
  function Y(c) { return (height*(1-c)).toFixed(1) ; } ;
  var x, y, s, r, rd, p, a, sw, rh, o, fs ;

  v.push('<path style="stroke:#F00" d="M ' + X(0.25) + ' ' + Y(0) +
	 ' L ' + X(0.25) + ' ' + Y(1) + '"/>') ;
  v.push('<path style="stroke:#888" d="M ' + X(0.5) + ' ' + Y(0) +
	 ' L ' + X(0.5) + ' ' + Y(1) + '"/>') ;
  v.push('<path style="stroke:#0F0" d="M ' + X(0.75) + ' ' + Y(0) +
	 ' L ' + X(0.75) + ' ' + Y(1) + '"/>') ;

  if ( column == 'TOTAL' )
    rd = sorted_cols.length ;
  else
    rd = 1 ;
  s = [] ;
  p = [] ;
  for(var group in groups)
    {
      group = groups[group] ;
      stat = all_stats[group + '\001' + column] ;
      if ( stat && stat.nr != 0 && group != 'TOTAL' )
	{
	  x = X(stat.normalized_average()) ;
	  y = Y(2*stat.standard_deviation()/stat.size) ;
	  r = Math.pow(stat.nr/rd, 0.5)/4 * zoom ;
	  if ( zoom > 2 )
	    o = 0.2 ;
	  else
	    o = 1 ;
	  v.push('<circle style="fill:#000;opacity:' + o + '" cx="'
		 + x + '" cy="' + y + '" r="' + r  + '"/>') ;
	  if ( zoom > 2 )
	    {
	      if ( group.length > 6 )
		fs = '50' ;
	      else
		fs = '70' ;
	      s.push('<text style="fill:#000;font-size:' + fs
		     + '%;text-anchor:middle;dominant-baseline:middle" x="' + x + '" y="' + y + '">'
		     + html(group.replace(/\001/g,''))
		     + '</text>') ;
	      x = Number(x) ;
	      y = Number(y) ;
	      rh = 10 / rd ;
	      sw = r.toFixed(1) / 2 ;
	      for(var i in stat.histogram)
		{
		  a = i*3.14/10 + 3.14/2 ;
		  p.push('<path style="opacity:0.6;stroke-width:'
			 + sw + 'px;stroke-linecap:round;stroke:#' +
			 s_colors[i] + '" d="M '
			 + x + ' ' + y +
			 ' L ' + (x+Math.cos(a)*stat.histogram[i]*rh)
			 + ' ' + (y+Math.sin(a)*stat.histogram[i]*rh)
			 + '"/>') ;
		}
	    }
	}
    }
  if ( zoom > 2 )
    {      
      v = p.concat(v.concat(s)) ;
    }

  return '<object type="image/svg+xml;utf-8" height="' + height 
    + 'px" width="' + width + 'px" data="data:image/svg+xml;utf-8,' +
    base64('<?xml version="1.0" encoding="UTF-8" standalone="no"?>' +
	   '<svg xmlns="http://www.w3.org/2000/svg" style="background:white">' +
	   '<g>' + v.join('\n') + '</g>' + '</svg>') + '"></object><div>'  ;

}

function stat_display_flowers(s, groups, sorted_cols, all_stats)
{
  s.push('<tr><th>Moy/E.T.') ;
  for(var column in sorted_cols)
    {
      column = sorted_cols[column] ;
      s.push('<td><div class="s_graph">'
	     + stat_display_flower(groups, all_stats, column)
	     + '<div class="s_clickable" onclick="stat_flower_zoom(this,'
	     + js2(column) + ')"></div></div></td>') ;
    }
  s.push('</tr>') ;
}


function compute_stats(lines, data_col)
{
  var column = columns[data_col] ;
  var s = new Stats(column.min, column.max, column.empty_is) ;
  for(var line in lines)
    s.add(lines[line][data_col].value) ;
  return s ;
}

var values_names = {
  's_average': 'moyenne',
  's_stddev': 'écart type',
  's_nr': 'nombre de valeurs',
  's_minimum': 'minimum',
  's_maximum': 'maximum',
  's_mediane': 'médiane',
  's_histogram': 'histogramme'
} ;

var colorations = {
  'couleurs': 1.5,
  'incolore': 100,
  'plein de couleurs': 1
} ;

function stat_span(s, value_type, value, html_class)
{
  if ( values_to_display[values_names[value_type]] )
    s.push('<span class="' + value_type + ' ' + html_class + '">'
	   + value + "</span>") ;
}

function stat_graph_zoom(t, group)
{
  var w = stat_tip_window(t, '\002' + group) ;
  if ( ! w )
    return ;

  var td = [], stats, key ;
  for(var column in sorted_cols)
    {
      column = sorted_cols[column] ;
      key = group + '\001' + column ;
      stats = all_stats[key] ;
      if ( stats == undefined )
	td.push(0) ;
      else
	if ( ! isNaN(column) ) // Not the TOTAL
	  td.push([stats.normalized_average(), stats.nr]);
    }

  w.innerHTML = '<div class="s_graph_zoomed"><small>'
    + 'Ligne pleine : évolution des notes au cours des séances<br>'
    + 'Ligne pointillée : évolution du nombre de notes<br>'
    + a_graph([td], 4) + '</div>' ;

  set_element_relative_position(t, w) ;
  w.style.display = 'block' ;
}

function stat_zoom(t, data_col, group)
{
  var w = stat_tip_window(t, '\003' + data_col + group) ;
  if ( ! w )
    return ;
  var stats = all_stats[group + '\001' + data_col] ;
  var s = '<div class="s_stat_tip">', value, j ;
  if ( data_col == 'TOTAL' )
    s += 'TOTAL' ;
  else
    s += 'Colonne : <b>' + html(columns[data_col].title) + '</b>' ;
  if ( regrouping == 'auteur' )
    s += '. Auteur : <b>' + group + '</b>' ;
  else
    if ( group != 'TOTAL' )
      {
	s += ', pour les lignes : ' ;
	j = 0 ;
	for(var i in grouped_by)
	  if ( grouped_by[i] )
	    s += ' ' + html(columns[i].title) +
	      '=<b>' + group.split('\001')[j++] + '</b>' ;
      }

  if ( stats.nr )
    {
      s += '<table><tr><td>' ;
      s += 'Minimum : ' + stats.min.toFixed(3)
	+ ', Maximum: ' + stats.max.toFixed(3)
	+ '<br>Moyenne : '+ stats.average().toFixed(3)
	+ ', Médiane : ' + stats.mediane().toFixed(3)
	+ '<br>Variance : ' + stats.variance().toFixed(3)
	+ ', Écart-Type : ' + stats.standard_deviation().toFixed(3)
	+ '<br>Somme des ' + stats.nr + ' valeurs : ' + stats.sum.toFixed(3)
	+ '<td class="s_enumeration">' ;
  
      for(var i in stats.all_values)
	if ( stats.all_values[i] )
	  {
	    if ( i === '' )
	      s += 'vide' ;
	    else
	      s += i ;
	    s += ':' + stats.all_values[i] + '<br>' ;
	  }
      s += '</tr></table>' ;
    }

  var max ;
  if ( stats.nr )
    {
      s += '<div class="s_zoomed_histogram s_zoomed_histogram_note">\n' ;
      max = stats.histo_max() ;
      for(var i in stats.histogram)
	{
	  if ( stats.histogram[i] )
	    value = stats.histogram[i]  ;
	  else
	    value = '' ;
	  s += '<div style="height:' + (100*stats.histogram[i]/max)
	    + '%;left:' + (2*i)
	    + 'em;background:#' + s_colors[i] + '"><span>'
	+ value + '</span><div>' + i + '</div></div>' ;
	}
    }
  else
    {
      s += '<div class="s_zoomed_histogram s_zoomed_histogram_enum">\n' ;
      max = stats.maxmax() ;
      var nr_cols = 0
      for(var ii in all_values)
	if ( stats.all_values[ii] )
	  nr_cols++ ;
      i = 0 ;
      for(var ii in all_values)
	{
	  if ( stats.all_values[ii] )
	    value = stats.all_values[ii]  ;
	  else
	    continue ;
	  s += '<div style="height:' + (100*stats.all_values[ii]/max)
	    + '%;width:' + 100./nr_cols + '%; left:' + 100*i/nr_cols
	    + '%;background:#' + s_colors[ii] + '"><span>'
	    + value + '</span><div>' + ii + '</div></div>' ;
	  i++ ;
	}
    }
  s += '</div></div>\n' ;

  w.innerHTML = s ;
  set_element_relative_position(t, w) ;
  w.style.display = 'block' ;
}

function display_stats_td(s, stats, data_col, group)
{
  var z = 2 ;
  if ( group == 'TOTAL' )
    z /= stats_groups.length ;
  if ( data_col == 'TOTAL' )
    z /= sorted_cols.length ;

  if ( stats.nr == 0 )
    {
      s.push('<td><div class="stat_enum" onclick="stat_zoom(this,\''
	     + data_col + "'," + js2(group) + ')">') ;
      for(var i in stats.all_values)
	if ( stats.all_values[i] )
	  s.push(i + ':' + stats.all_values[i] + '<br>') ;
      s.push('</div></td>') ;
      return ;
    }

  s.push('<td><div class="s_td" onclick="stat_zoom(this,\''
	 + data_col + "'," + js2(group) + ')">') ;

  if ( values_to_display['histogramme'] )
    s.push(stats_histogram(stats, z)) ;

  s.push('<div class="s_center">') ;
  stat_span(s, 's_average', stats.average().toFixed(nr_decimals),
	    stats.average_class
	    ) ;
  stat_span(s, 's_mediane', stats.mediane().toFixed(nr_decimals), '') ;
  s.push('</div>') ;
  stat_span(s, 's_nr'     , stats.nr, stats.nr_class) ;
  stat_span(s, 's_minimum', stats.min.toFixed(nr_decimals), '') ;
  stat_span(s, 's_maximum', stats.max.toFixed(nr_decimals), '') ;
  stat_span(s, 's_stddev' , stats.standard_deviation().toFixed(nr_decimals),
	    stats.stddev_class) ;
  s.push('</td>') ;
}

var s_colors = {} ;

for(i=0;i<20;i++)
  s_colors[i] = i<5 ? 'F44' : (i<10 ? 'DA0' : (i<15 ? '9C9' : '0F0')) ;
s_colors[pre] = '8F8' ;
s_colors[abi] = 'F88' ;
s_colors[abj] = '88F' ;
s_colors[ppn] = '0FF' ;

var all_stats = {} ;

function stats_histogram(stats, z)
{
  var s = '<div class="s_histogram">' ;
  var color ;
  for(var i in stats.histogram)
    {
      if ( values_to_display['histogramme'] )
	color = s_colors[i] ;
      else
	color = 'BBB' ;

      s += '<div style="height:' + (stats.histogram[i]*z).toFixed(0)
	+ 'px;left:' + (2*(i-10)) + 'px;background:#' + color + '"></div>' ;
    }

  return s + '</div>' ;
}

function a_value_button(s, attr, title, tip, not_escape)
{
  s.push(display_button("'" + values_names[attr] + "'", title,
			values_to_display[values_names[attr]] ,
			'values_to_display', tip, not_escape, attr)) ;
}

function horizontal_coloring(all_stats, groups, sorted_cols)
{
  var key, stats ;

  for(var group in groups)
    {
      group = groups[group] ;
      stats = new Stats(0, 20, '') ;
      for(var column in sorted_cols)
	{
	  if ( isNaN(sorted_cols[column]) ) // TOTAL
	    continue ;
	  key = group + '\001' + sorted_cols[column] ;
	  if ( ! all_stats[key] )
	    continue ;
	  stats.add(all_stats[key].nr) ;
	}

      for(var column in sorted_cols)
	{
	  if ( isNaN(sorted_cols[column]) ) // TOTAL
	    continue ;
	  key = group + '\001' + sorted_cols[column] ;
	  td = all_stats[key] ;
	  if ( ! td )
	    continue ;
	  if ( td.nr < stats.average() - color_coef*stats.standard_deviation())
	    td.nr_class = 's_stat_red' ;
	  else
	    if ( td.nr > stats.average()
		 + color_coef*stats.standard_deviation())
	      td.nr_class = 's_stat_green' ;
	}
    }
}

function vertical_coloring(all_stats, sorted_groups, sorted_cols)
{
  var td, stats, s ;

  for(var column in sorted_cols)
    {
      column = sorted_cols[column] ;

      stats = new Stats(0, 20, '') ;
      for(var group in sorted_groups)
	{
	  if ( sorted_groups[group] == 'TOTAL' )
	    continue ;
	  s = all_stats[sorted_groups[group] + '\001' + column] ;
	  if ( s )
	    stats.add(s.average()) ;
	}

      for(var group in sorted_groups)
	{
	  if ( sorted_groups[group] == 'TOTAL' )
	    continue ;
	  td = all_stats[sorted_groups[group] + '\001' + column] ;
	  if ( ! td )
	    continue ;
	  if ( td.average() < stats.average()
	       - color_coef*stats.standard_deviation())
	    td.average_class = 's_stat_red' ;
	  else
	    if ( td.average() > stats.average()
		 + color_coef*stats.standard_deviation())
	      td.average_class = 's_stat_green' ;
	}

      stats = new Stats(0, 20, '') ;
      for(var group in sorted_groups)
	{
	  if ( sorted_groups[group] == 'TOTAL' )
	    continue ;
	  s = all_stats[sorted_groups[group] + '\001' + column] ;
	  if ( s )
	    stats.add(all_stats[sorted_groups[group] + '\001'
				+ column].standard_deviation()) ;
	}
	  
      for(var group in sorted_groups)
	{
	  if ( sorted_groups[group] == 'TOTAL' )
	    continue ;
	  td = all_stats[sorted_groups[group] + '\001' + column] ;
	  if ( ! td )
	    continue ;
	  if ( td.standard_deviation() < stats.average()
	       - color_coef*stats.standard_deviation())
	    td.stddev_class = 's_stat_red' ;
	  else
	    if ( td.standard_deviation() > stats.average()
		 + color_coef*stats.standard_deviation())
	      td.stddev_class = 's_stat_green' ;
	}
    }
}


function statistics_values(sorted_cols, all_stats, groups)
{
  var grouped_lines = {} ;
  var key ;
  for(var data_lin in lines)
    {
      key = compute_groups_key(grouped_by, lines[data_lin]) ;
      if ( grouped_lines[key] === undefined )
	grouped_lines[key] = [] ;
      grouped_lines[key].push(lines[data_lin]) ;
    }

  for(var i in grouped_lines)
    groups.push(i) ;
  groups.sort() ;

  for(var group in grouped_lines)
    {
      i++ ;
      for(var column in sorted_cols)
	all_stats[group + '\001' + sorted_cols[column]] =
	  compute_stats(grouped_lines[group], sorted_cols[column]);
    }
}

function statistics_author(sorted_cols, all_stats, groups)
{
  var authors_name = {}, cell, col, key, stats, td, tds, author ;

  for(var line in lines)
    {
      line = lines[line] ;
      for(var column in sorted_cols)
	{
	  column = sorted_cols[column] ;
	  cell = line[column] ;
	  col = columns[column] ;
	  key = cell.author + '\001' + column ;
	  if ( all_stats[key] === undefined )
	    all_stats[key] = new Stats(col.min, col.max, col.empty_is) ;
	  all_stats[key].add(cell.value) ;
	  authors_name[cell.author] = true ;
	}
    }
  for(var author in authors_name)
    if ( author.length > 1 )
      groups.push(author) ;
  groups.sort() ;
}

function stat_display_line(s, i_group, group, sorted_cols, all_stats,
			   all_values, td, groups)
{
  var key, stats, tds, merge ;

  s.push('<tr><th>' + group.replace(/[\001\002]/g, ' ') + '</th>') ;
  for(var column in sorted_cols)
    {
      column = sorted_cols[column] ;
      key = group + '\001' + column ;
      stats = all_stats[key] ;
      if ( stats == undefined )
	{
	  s.push('<td>&nbsp;</td>') ;
	  td.push(0) ;
	}
      else
	{
	  display_stats_td(s, stats, column, group) ;
	  if ( ! isNaN(column) ) // Not the TOTAL
	    td.push([stats.normalized_average(), stats.nr]);
	}
    }

  tds = new Array(groups.length) ;
  tds[i_group] = td ;
  
  s.push('<td><div class="s_graph">' + a_graph(tds)
	 + '<div class="s_clickable" onclick="stat_graph_zoom(this,'
	 + js2(group) + ')"></div></div></td>') ;
  s.push('</tr>') ;
}


function stat_display_table(s, groups, sorted_cols, all_stats, all_values)
{
  var td ;

  for(var i_group in groups)
    {
      td = [] ;
      group = groups[i_group] ;
      stat_display_line(s, i_group, groups[i_group], sorted_cols,
			all_stats, all_values, td, groups)
      all_values.push(td) ;
    }
}

function compute_column_totals(groups, sorted_cols, all_stats)
{
  var stats, key ;

  for(var column in sorted_cols)
    {
      stats = new Stats(0, 20, '') ;
      column = sorted_cols[column] ;
      for(var group in groups)
	{
	  key = groups[group] + '\001' + column ;
	  if ( all_stats[key] )
	    stats.merge(all_stats[key]) ;
	}
      all_stats['TOTAL\001' + column] = stats ;
    }
}

function compute_line_totals(groups, sorted_cols, all_stats)
{
  var stats, key ;

  for(var group in groups)
    {
      stats = new Stats(0, 20, '') ;
      for(var column in sorted_cols)
	{
	  key = groups[group] + '\001' + sorted_cols[column] ;
	  if ( all_stats[key] )
	    stats.merge(all_stats[key]) ;
	}
      all_stats[groups[group] + '\001TOTAL'] = stats ;
    }
}

var sorted_cols ;
var stat_groups ;

function statistics_display()
{
  if ( ! do_printable_display )
    return ;
  do_printable_display = false ;

  document.getElementById('tip').style.display = 'none' ;

  sorted_cols = [] ;
  for(var c in columns)
    if ( columns_to_display[c] )
      sorted_cols.push(c) ;
  sorted_cols.sort(function(a,b)
	      { return columns[a].position - columns[b].position ; }) ;

  var stats = new Stats(0,20,'') ;
  var s = [ue + ' ' + semester + ' ' + year], td ;
  var td_width = 0 ;
  nr_decimals = Number(nr_decimals) ;
  if ( values_to_display[values_names['s_average']] )
    td_width += 2 + nr_decimals ;
  if ( values_to_display[values_names['s_mediane']] )
    td_width += (2 + nr_decimals)*0.7 ;
  if ( td_width < 3.5 )
    td_width = 3.5 ;

  td_width /= 1.5 ;

  s.push('<table class="colored">') ;
  s.push('<tr><th><div class="s_td">') ;
  s.push('<div class="s_center">') ;

  a_value_button(s, 's_average', 'Moy', 'moyenne') ;
  a_value_button(s, 's_mediane', 'med', 'médiane') ;
  s.push('</div>') ;
  a_value_button(s, 's_histogram', 'Histogram.', 'Histo') ;
  a_value_button(s, 's_stddev', 'E.T.', 'Écart-type') ;
  a_value_button(s, 's_nr', 'Nbr.', 'Nombre') ;
  a_value_button(s, 's_minimum', 'min', 'Min') ;
  a_value_button(s, 's_maximum', 'max', 'Max') ;
  for(var column in sorted_cols)
    s.push('<th><div style="min-width:' + td_width + 'em">' + html(columns[sorted_cols[column]].title) + '</div></th>') ;
  s.push('<th>TOTAL<th>&Eacute;volution') ;
  s.push('</tr>') ;

  var line_sum = Stats(0, 20, '') ;

  // Creates statistics table

  all_stats = {} ;
  stats_groups = [] ;
  if ( regrouping == 'auteur' )
    statistics_author(sorted_cols, all_stats, stats_groups) ;
  else
    statistics_values(sorted_cols, all_stats, stats_groups) ;

  // Compute line/column totals
  compute_column_totals(stats_groups, sorted_cols, all_stats) ;
  if ( stats_groups.length != 1)
    stats_groups.push('TOTAL') ;
  compute_line_totals(stats_groups, sorted_cols, all_stats) ;
  sorted_cols.push('TOTAL') ;

  // Coloring

  color_coef = colorations[coloration] ;
  vertical_coloring(all_stats, stats_groups, sorted_cols) ;
  horizontal_coloring(all_stats, stats_groups, sorted_cols) ;

  // Display table

  var all_values = [] ;
  stat_display_table(s, stats_groups, sorted_cols, all_stats, all_values) ;

  stat_display_flowers(s, stats_groups, sorted_cols, all_stats) ;

  s.push('</table>') ;
    
  document.getElementById('content').innerHTML = s.join('\n') ;
}

//////////////////////////////////////////////////////////////////////////////
// Generate full statistic page
//////////////////////////////////////////////////////////////////////////////

function display_statistics(object)
{
  var p = [ printable_introduction() ] ;
  p.push('<script>') ;
  p.push('var do_printable_display = true ;') ;
  p.push('var columns_to_display = {};') ;
  p.push('var values_to_display = {"moyenne":true};') ;
  p.push('var grouped_by = {};') ;
  p.push('var coloration = "";') ;
  p.push('var nr_decimals = "1";') ;
  p.push('var regrouping = "valeur";') ;
  p.push('var color_coef ;') ;
  p.push('var ue = ' + js(ue) + ';') ;
  p.push('var display_tips = true ;') ;
  p.push('var columns = ' + columns_in_javascript() + ';') ;
  p.push('var lines ;') ;
  p.push('function initialize() {') ;
  p.push('if ( ! wait_scripts("initialize()") ) return ;') ;
  p.push('lines = ' + lines_in_javascript() + ';') ;
  p.push('setInterval("statistics_display()", 200);') ;
  p.push('}') ;
  p.push('</script>') ;
  p.push('<p class="hidden_on_paper">Exporter dans un tableur : faites un copier/coller de toute la page dans votre tableur (Ctrl-A Ctrl-C Ctrl-V)');
  p.push('<table class="hidden_on_paper">') ;

  var t = [] ;
  for(var data_col in columns)
    if ( ! columns[data_col].is_empty )
      t.push(display_button(data_col, columns[data_col].title,
			    ! columns[data_col].hidden
			    && columns[data_col].type == 'Note',
			    'columns_to_display',
			    html(columns[data_col].comment)));
  print_choice_line(p, 'Colonnes à afficher',
		    'Choisissez les colonnes à afficher.',
		    t.join(' '),
		    'columns_to_display') ;

  t = [] ;
  var column ;
  for(var data_col in columns)
    {
      column = columns[data_col] ;
      if ( column.is_empty )
	continue ;
      var stats = compute_stats(filtered_lines, data_col) ;
      if ( filtered_lines.length / stats.nr_uniques() > 1 )
	t.push(display_button(data_col, column.title,
			      column.title == 'Seq' || column.title == 'Grp',
			      'grouped_by',
			      html(column.comment
				   + '\n(' + stats.nr_uniques() +
				   ' valeurs différentes)')));
    }
  print_choice_line(p, 'Regrouper par',
		    'Critère indiquant quand il faut changer de page lors de l\'impression.<br>On peut utiliser ceci pour faire une feuille d\'émargement par salle de TP ou enseignant.',
		    t.join(' '),
		    'grouped_by') ;
      
  print_choice_line(p, 'Nombre de décimales',
		    'Nombre de chiffres affichés après la virgule',
		    radio_buttons('nr_decimals', ['0', '1', '2', '3'], '1'),
		    'nr_decimals') ;

  t = [] ;
  for(var i in colorations)
    t.push(i) ;
  print_choice_line(p, 'Coloration',
		    'En rouge les valeurs trop petites et en vert les trop grandes.',
		    radio_buttons('coloration', t, 'couleurs'),
		    'coloration') ;

  print_choice_line(p, 'Regrouper par',
		    "Qu'est ce que l'on regroupe",
		    radio_buttons('regrouping', ['valeur', 'auteur'],'valeur'),
		    'regrouping') ;

  p.push('</table>') ;
  p.push('<div style="clear:both" id="content"></div>') ;
  p.push('<div id="tip"></div>') ;
  p.push('<script>') ;
  // The timeout is for IE
  p.push('setTimeout("initialize() ;",100) ;') ;
  p.push('</script>') ;

  var w = window_open() ;
  w.document.open('text/html') ;
  w.document.write(html_begin_head(true) + p.join('\n')) ;
  w.document.close() ;
  return w ;
}
