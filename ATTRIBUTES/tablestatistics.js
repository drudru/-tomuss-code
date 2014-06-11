// -*- coding: utf-8 -*-
/*
  TOMUSS: The Online Multi User Simple Spreadsheet
  Copyright (C) 2011-2012 Thierry EXCOFFIER, Universite Claude Bernard

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

  svg = '<div class="s_graph"><object type="image/svg+xml;charset=utf-8" height="'
    + height + 'px" width="' + width + 'px" data="data:text/xml;charset=utf-8,' +
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
  var w = get_tip_element() ;
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
      w.style.left = '-10000px' ;
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
  w.innerHTML = stat_zoom_header(column) + '<br>'
      + _("MSG_stat_flower_horizontal") + '<br>'
      + _("MSG_stat_flower_vertical") + '</div>'
    + stat_display_flower(stats_groups, all_stats, column, 12) ;
  set_element_relative_position(t, w) ;
  w.style.display = 'block' ;
}

function stat_display_one_flower(s, v, p, x, y, stat, group, zoom, hide_histo)
{
  if ( stat === undefined )
    return '' ;
  var o, t ;
  var r = Math.log(stat.nr+1)/2 * zoom ;
  if ( zoom > 2 )
    o = 0.2 ;
  else
    o = 1 ;
  v.push('<circle style="fill:#000;opacity:' + o + '" cx="'
	 + x + '" cy="' + y + '" r="' + r + '"/>') ;
  if ( zoom > 2 )
    {
      t = group.replace(/\001/g,' ').split('\n') ;
      if ( group.length/t.length > 30 )
	fs = 8 ;
      else if ( group.length/t.length > 20 )
	fs = 10 ;
      else if ( group.length/t.length > 10 )
	fs = 12 ;
      else
	fs = 14 ;
      s.push('<text style="fill:#000;font-size:' + fs
	     + 'px;text-anchor:middle;dominant-baseline:middle" x="' + x
	     + '" y="' + y + '">') ;
      for(var i in t)
	s.push('<tspan x="' + x + '" dy="' + (i==0 ? -fs*(t.length-1.5) :(fs+1)) + 'px"'
	       + '>' + html(t[i]) + '</tspan>') ;
      s.push('</text>') ;
      if ( ! hide_histo )
      {
	x = Number(x) ;
	y = Number(y) ;
	var rh = 20*r/stat.nr ;
	var sw = (r/3.14).toFixed(2) ;
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
  return r ;
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
  var s, p ;

  v.push('<path style="stroke:#F00" d="M ' + X(0.25) + ' ' + Y(0) +
	 ' L ' + X(0.25) + ' ' + Y(1) + '"/>') ;
  v.push('<path style="stroke:#888" d="M ' + X(0.5) + ' ' + Y(0) +
	 ' L ' + X(0.5) + ' ' + Y(1) + '"/>') ;
  v.push('<path style="stroke:#0F0" d="M ' + X(0.75) + ' ' + Y(0) +
	 ' L ' + X(0.75) + ' ' + Y(1) + '"/>') ;

  s = [] ;
  p = [] ;
  for(var group in groups)
    {
      group = groups[group] ;
      stat = all_stats[group + '\001' + column] ;
      if ( stat && stat.nr != 0 && group != _("MSG_stat_TOTAL_row") )
	stat_display_one_flower(s, v, p,
				X(stat.normalized_average()),
				Y(2*stat.standard_deviation()/stat.size),
				stat, group, zoom) ;
    }
  if ( zoom > 2 )
    {      
      v = p.concat(v.concat(s)) ;
    }
  return '<object type="image/svg+xml" height="' + height 
    + 'px" width="' + width + 'px" data="data:text/xml;charset=utf-8,' +
    base64('<?xml version="1.0" encoding="UTF-8" standalone="no"?>' +
	   '<svg xmlns="http://www.w3.org/2000/svg" style="background:white">' +
	   '<g>' + v.join('\n') + '</g>' + '</svg>') + '"></object><div>'  ;

}

function stat_display_fractal_flower(groups, sorted_cols, all_stats, zoom)
{
  var s=[], v=[], p=[] ;
  var stat, size = .4 ;

  if ( zoom === undefined )
    zoom = 1 ;

  var width = stat_svg_height * zoom ;
  var height = stat_svg_height * zoom ;
  function X(c) { return (width*c).toFixed(1) ; } ;
  function Y(c) { return (height*(1-c)).toFixed(1) ; } ;

  var title = '' ;
  if ( zoom > 2 )
    title = html(ue) + '\n' + html(semester) + '\n' + html(year) ;

  stat = all_stats[_("MSG_stat_TOTAL_row")+'\001TOTAL'] ;
  if ( stat === undefined )
    for(var i in groups)
      {
	stat = all_stats[groups[i] + '\001TOTAL'] ;
	break ;
      }

  var central_radius = stat_display_one_flower(s, v, p, X(0.5), Y(0.5),
					       stat, title, zoom) ;
  p.push('<circle style="fill:none;stroke:#888" cx="' + X(0.5) + '" cy="' + Y(0.5) + '" r="'
	 + (central_radius+width/2*size) + '"/>') ;
  p.push('<circle style="fill:none;stroke:#F00" cx="' + X(0.5) + '" cy="' + Y(0.5) + '" r="'
	 + (central_radius+width/4*size) + '"/>') ;
  p.push('<circle style="fill:none;stroke:#0F0" cx="' + X(0.5) + '" cy="' + Y(0.5) + '" r="'
	 + (central_radius+3*width/4*size) + '"/>') ;
  p.push('<circle style="fill:none;stroke:#FF0" cx="' + X(0.5) + '" cy="' + Y(0.5) + '" r="'
	 + (central_radius+width*size) + '"/>') ;

  var flowers_s = [] ;
  var flowers_v = [] ;
  var flowers_p = [] ;
  var flowers_nr = [] ;
  var s2, v2, p2 ;
  var hide_histo = sorted_cols.length > 7 ;

  for(var column in sorted_cols)
    {
      column = sorted_cols[column] ;
      if ( column == 'TOTAL' )
	continue ;
      
      stat = all_stats[_("MSG_stat_TOTAL_row") + '\001' + column] ;
      if ( stat === undefined || stat.nr == 0 )
	continue ;
      
      s2 = [] ;
      v2 = [] ;
      p2 = [] ;
      stat_display_one_flower(s2, v2, p2, 0., 0., stat,
			      columns[column].title, zoom/4,
			      hide_histo) ;
      flowers_nr.push(stat.normalized_average()) ;
      flowers_s.push(s2.join('\n')) ;
      flowers_v.push(v2.join('\n')) ;
      flowers_p.push(p2.join('\n')) ;
    }


  for(var j=-2; j<columns.length; j++)
    {
      var _all_stats = {} ;
      var _stats_groups = [] ;
      var _grouped_by ;
      var title = '' ;
      var data_col = j ;
      
      _grouped_by = grouped_by ;
      switch(j)
	{
	case -2: statistics_author(sorted_cols, _all_stats, _stats_groups) ;
	  break;
	case -1: statistics_date(sorted_cols, _all_stats, _stats_groups) ;
	  break;
	default:
	  if ( data_col == 'TOTAL' )
	    continue ;
	  var stat = compute_stats(lines, data_col) ;
	  var nr_uniques = stat.nr_uniques() ;
	  if ( data_col != 3 && data_col != 4
	       && (nr_uniques > 10 || nr_uniques <= 1) )
	    continue ;
	  grouped_by = {} ;
	  grouped_by[data_col] = true ;
	  statistics_values(sorted_cols, _all_stats, _stats_groups) ;
	  title = columns[data_col].title + '\n' ;
	  break;
	}
      compute_column_totals(_stats_groups, sorted_cols, _all_stats) ;
      compute_line_totals(_stats_groups, sorted_cols, _all_stats) ;
      for(var group in _stats_groups)
	{
	  group = _stats_groups[group] ;
	  stat = _all_stats[group + '\001TOTAL'] ;
	  if ( stat && stat.nr != 0 && group != _("MSG_stat_TOTAL_row") )
	    {
	      s2 = [] ;
	      v2 = [] ;
	      p2 = [] ;
	      stat_display_one_flower(s2, v2, p2, 0., 0.,
				      stat, title + group, zoom/4,
				     hide_histo) ;
	      flowers_nr.push(stat.normalized_average()) ;
	      flowers_s.push(s2.join('\n')) ;
	      flowers_v.push(v2.join('\n')) ;
	      flowers_p.push(p2.join('\n')) ;
	    }
	}
      grouped_by = _grouped_by ;
    }

  var angle, teta =  2*3.14 / flowers_s.length ;
  var translate, d ;
  angle = 0 ;
  for(var i=0; i<flowers_s.length; i++)
    {
      d = central_radius + width * size * flowers_nr[i] ;
      translate = '<g transform="translate('
	+ (width/2 + Math.cos(angle) * d) + ','
	+ (height/2 + Math.sin(angle) * d) + ')">' ;
      s.push( translate + flowers_s[i] + '</g>' ) ;
      v.push( translate + flowers_v[i] + '</g>' ) ;
      p.push( translate + flowers_p[i] + '</g>' ) ;
      angle += teta ;
    }
 
  if ( zoom > 2 )
    {    
      v = p.concat(v.concat(s)) ;
    }
  v = '<g>' + v.join('\n') + '</g>' ;

  return '<object type="image/svg+xml;charset=utf-8" height="' + height 
    + 'px" width="' + width + 'px" data="data:text/xml;charset=utf-8,' +
    base64('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n' +	   
	   '<svg onclick="w=window.open();w.document.write(html(base64_decode(\'' + base64('<svg xmlns="http://www.w3.org/2000/svg">' + v + '</svg>')+ '\')))" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" style="background:white">' +
	   '<script xlink:href="' + url + '/utilities.js"></script>' +
	   v + '</svg>') + '"></object>'  ;
  
}

function stat_fractal_flower_zoom(t)
{
  var w = window_open(ue + '_flower') ;
  w.document.open('text/html;charset=utf-8') ;
  w.document.write
      (_("MSG_stat_flower_explanations")
       + stat_display_fractal_flower(stats_groups, sorted_cols,
				     all_stats,
				     window_width() / stat_svg_height
				    )
       ) ;
  w.document.close() ;
}


function stat_display_flowers(s, groups, sorted_cols, all_stats)
{
  s.push('<tr><th>' +
	 hidden_txt(_("TH_stat_last_line"), _("TIP_stat_last_line")));
  for(var column in sorted_cols)
    {
      column = sorted_cols[column] ;
      s.push('<td><div class="s_graph">'
	     + stat_display_flower(groups, all_stats, column)
	     + '<div class="s_clickable" onclick="stat_flower_zoom(this,'
	     + js2(column) + ');setTimeout(\'scrollTop(10000000);\',100) ;"></div></div></td>') ;
    }
  s.push('<td><div class="s_graph">'
	 + stat_display_fractal_flower(groups, sorted_cols, all_stats)
	 + '<div class="s_clickable" onclick="stat_fractal_flower_zoom(this)'
	 + '"></div></div></td>') ;

  s.push('</tr>') ;
}


function compute_stats(lines, data_col)
{
  var column = columns[data_col] ;
  var s = new Stats(Number(column.min), Number(column.max), column.empty_is) ;
  s = new Stats(column.min, column.max, column.empty_is) ;
  for(var line in lines)
    s.add(lines[line][data_col].value) ;
  return s ;
}

var colorations = {
    "B_stat_colorles": 100,
    "B_stat_colored": 1.5,
    "B_stat_very_colored": 1
} ;

function stat_span(s, value_type, value, html_class)
{
    if ( values_to_display[_('B_' + value_type)] )
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
	  td.push([stats.normalized_average(),
		   stats.nr + (stats.all_values[pre]
			       ? stats.all_values[pre]:0)]);
    }

  w.innerHTML = '<div class="s_graph_zoomed">'
      + _("MSG_stat_line_help") + '<br>' + a_graph([td], 4) + '</div>' ;

  set_element_relative_position(t, w) ;
  w.style.display = 'block' ;
}

function stat_zoom_header(data_col, group)
{
  var s = '<div class="s_stat_tip">' ;
  if ( data_col == 'TOTAL' )
      s += _("MSG_stat_TOTAL_col") ;
  else
      s += _("MSG_stat_column")+'<b>' + html(columns[data_col].title) + '</b>';

  if ( group !== undefined )
    {
      if ( regrouping == _("B_stat_group_author") )
	  s += _("MSG_stat_author") + '<b>' + group + '</b>' ;
      else
	if ( group != _("MSG_stat_TOTAL_row") )
	  {
	    s += _("MSG_stat_lines") ;
	    j = 0 ;
	    for(var i in grouped_by)
	      if ( grouped_by[i] )
		s += ' ' + html(columns[i].title) +
		  '=<b>' + group.split('\001')[j++] + '</b>' ;
	  }
    }
  else
    {
      if ( regrouping == _("B_stat_group_author") )
	  s += _("MSG_stat_author_grouping") ;
      else
	{
	  s += _("MSG_stat_grouped_by") + '<b>' ;
	  for(var i in grouped_by)
	    if ( grouped_by[i] )
	      s += ' ' + html(columns[i].title) ;
	  s += '</b>' ;
	}
    }

  return s ;
}

function stat_zoom(t, data_col, group)
{
  var w = stat_tip_window(t, '\003' + data_col + group) ;
  if ( ! w )
    return ;
  var stats = all_stats[group + '\001' + data_col] ;
  var s, value, j ;
  s = stat_zoom_header(data_col, group) ;
  if ( stats.nr )
    {
      s += '<table><tr><td>' ;
      s += _("B_s_minimum") + ': ' + stats.min.toFixed(3)
	  + ', ' + _("B_s_maximum") + ': ' + stats.max.toFixed(3)
	  + '<br>' + _("B_s_average") + ': '+ stats.average().toFixed(3)
	  + ', ' + _("B_s_mediane") + ': ' + stats.mediane().toFixed(3)
	  + '<br>' + _("B_s_variance") + ': ' + stats.variance().toFixed(3)
	  + ', ' +  _("B_s_stddev") +': '+stats.standard_deviation().toFixed(3)
	  + '<br>' + _("B_s_sum") + ' ' + stats.nr + ' ' + _("B_s_sum_2")
	  + ': ' + stats.sum.toFixed(3)
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
	    + value + '</span><div>'
	    + (stats.v_min + i/20.*stats.size).toFixed(1).replace(/[.]*0*$/,'')
	    + '</div></div>' ;
	}
      s += '<div style="left:40em;border:0px"><div>'
	+ stats.v_max + '</div></div>' ;
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
  if ( group == _("MSG_stat_TOTAL_row") )
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

  if ( values_to_display[_('B_s_histogram')] )
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
s_colors[tnr] = 'FAA' ;
s_colors[abj] = '88F' ;
s_colors[ppn] = '0FF' ;

var all_stats = {} ;

function stats_histogram(stats, z)
{
  var s = '<div class="s_histogram">' ;
  var color ;

  for(var i in stats.histogram)
    {
      if ( values_to_display[_('B_s_histogram')] )
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
    s.push(display_button("'" + _('B_' + attr) + "'", title,
			  values_to_display[_('B_'+attr)] ,
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
	  if ( sorted_groups[group] == _("MSG_stat_TOTAL_row") )
	    continue ;
	  s = all_stats[sorted_groups[group] + '\001' + column] ;
	  if ( s )
	    stats.add(s.average()) ;
	}

      for(var group in sorted_groups)
	{
	  if ( sorted_groups[group] == _("MSG_stat_TOTAL_row") )
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
	  if ( sorted_groups[group] == _("MSG_stat_TOTAL_row") )
	    continue ;
	  s = all_stats[sorted_groups[group] + '\001' + column] ;
	  if ( s )
	    stats.add(all_stats[sorted_groups[group] + '\001'
				+ column].standard_deviation()) ;
	}
	  
      for(var group in sorted_groups)
	{
	  if ( sorted_groups[group] == _("MSG_stat_TOTAL_row") )
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
  for(var i in lines)
    {
      key = compute_groups_key(grouped_by, lines[i]) ;
      if ( grouped_lines[key] === undefined )
	grouped_lines[key] = [] ;
      grouped_lines[key].push(lines[i]) ;
    }

  for(var i in grouped_lines)
    groups.push(i) ;
  groups.sort() ;

  for(var group in grouped_lines)
    {
      i++ ;
      for(var column in sorted_cols)
	if ( sorted_cols[column] != 'TOTAL' )
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
	  if ( sorted_cols[column] == "TOTAL" )
	    continue ;
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

function statistics_date(sorted_cols, all_stats, groups)
{
  var days = {}, cell, col, key, stats, td, tds, day ;

  for(var line in lines)
    {
      line = lines[line] ;
      for(var column in sorted_cols)
	{
	  if ( sorted_cols[column] == "TOTAL" )
	    continue ;
	  column = sorted_cols[column] ;
	  cell = line[column] ;
	  col = columns[column] ;
	  day = cell.date.substr(0,4) + ' ' + cell.date.substr(4,2) ;
	  // + (cell.date.substr(6,2)/10).toFixed(0) ;
	  key = day + '\001' + column ;
	  if ( all_stats[key] === undefined )
	    all_stats[key] = new Stats(col.min, col.max, col.empty_is) ;
	  all_stats[key].add(cell.value) ;
	  days[day] = true ;
	}
    }
  for(day in days)
    groups.push(day) ;
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
      column = sorted_cols[column] ;
      if ( column != 'TOTAL' )
	stats = new Stats(columns[column].min, columns[column].max, '') ;
      else
	stats = new Stats(0, 20, '') ;
      for(var group in groups)
	{
	  key = groups[group] + '\001' + column ;
	  if ( all_stats[key] )
	    stats.merge(all_stats[key]) ;
	}
      all_stats[_("MSG_stat_TOTAL_row") + '\001' + column] = stats ;
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

  // document.getElementById('tip').style.display = 'none' ;

  sorted_cols = [] ;
  for(var c in columns)
    if ( columns_to_display[c] )
      sorted_cols.push(c) ;
  sorted_cols.sort(function(a,b)
	      { return columns[a].position - columns[b].position ; }) ;

  var stats = new Stats(0,20,'') ;
  var s = ['<div style="text-align:center;font-weight:bold">' + ue + ' ' + semester + ' ' + year + '</div>'], td ;
  var td_width = 0 ;
  nr_decimals = Number(nr_decimals) ;
  if ( values_to_display[_('B_s_average')] )
    td_width += 2 + nr_decimals ;
  if ( values_to_display[_('B_s_mediane')] )
    td_width += (2 + nr_decimals)*0.7 ;
  if ( td_width < 3.5 )
    td_width = 3.5 ;

  td_width /= 1.5 ;

  s.push('<table class="colored">') ;
  s.push('<tr><th>') ;

  var t = [] ;

  t.push('<div class="s_td">') ;
  t.push('<div class="s_center">') ;
  a_value_button(t, 's_average', _('B_s_average_')) ;
  a_value_button(t, 's_mediane', _("B_s_mediane_")) ;
  t.push('</div>') ;
  a_value_button(t, 's_histogram', _("B_s_histogram_")) ;
  a_value_button(t, 's_stddev', _("B_s_stddev_")) ;
  a_value_button(t, 's_nr', _("B_s_nr_")) ;
  a_value_button(t, 's_minimum', _("B_s_minimum_")) ;
  a_value_button(t, 's_maximum', _("B_s_maximum_")) ;
  t.push('</div>') ;

  s.push(hidden_txt(t.join('\n'), _("TIP_stat_explanation"))) ;

  for(var column in sorted_cols)
    s.push('<th onclick="button_toggle(columns_to_display,'
	   + sorted_cols[column] +
	   ',document.getElementById(\'columns_to_display\').getElementsByTagName(\'SPAN\')['
	   + columns[sorted_cols[column]].ordered_index
	   + ']); do_printable_display=true"><div style="min-width:'
	   + td_width + 'em">'
	   + hidden_txt(html(columns[sorted_cols[column]].title),
			_("TIP_stat_th_column"))
	   + '</div></th>') ;
  s.push('<th>'
	 + hidden_txt(_("MSG_stat_TOTAL_col"), _("TIP_stat_th_column_total"))
	 + '<th>'
	 + hidden_txt(_("TH_stat_th_trend"), _("TIP_stat_th_trend"))
	 );
  s.push('</tr>') ;

  var line_sum = Stats(0, 20, '') ;

  // Creates statistics table

  all_stats = {} ;
  stats_groups = [] ;
  if ( regrouping == _("B_stat_group_author") )
    statistics_author(sorted_cols, all_stats, stats_groups) ;
  else if ( regrouping == _("B_stat_group_month") )
    statistics_date(sorted_cols, all_stats, stats_groups) ;
  else
    statistics_values(sorted_cols, all_stats, stats_groups) ;

  // Compute line/column totals
  compute_column_totals(stats_groups, sorted_cols, all_stats) ;
  if ( stats_groups.length != 1)
    stats_groups.push(_("MSG_stat_TOTAL_row")) ;
  compute_line_totals(stats_groups, sorted_cols, all_stats) ;
  sorted_cols.push('TOTAL') ;

  // Coloring

  for(var i in colorations)
      if ( _(i) == coloration )
	  color_coef = colorations[i] ;
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

function strange_grades()
{
  var stats = [], v ;
  for(var c in columns)
  {
    if ( columns[c].type !== 'Note' )
      continue ;
    if ( columns[c].weight.substr(0,1) === '+'
       || columns[c].weight.substr(0,1) === '-')
      continue ;
    var s=0, s2=0, n=0 ;
    for(var line in lines)
    {
      v = lines[line][c].value ;
      if ( v !== '' )
      {
	v = Number(v) ;
	if ( ! isNaN(v) )
	{
	  s += v ;
	  s2 += v*v ;
	  n++ ;
	}
      }
    }
    if ( n > 2 )
      stats.push([c, s/n, Math.pow((s*s - s2)/n, 0.5), 1000, -1000]) ;
  }
  if ( stats.length < 3 )
  {
    Alert("ALERT_stat_need_more_data") ;
    return ;
  }

  var students = [] ;
  for(var line in lines)
  {
    line = lines[line] ;
    var norms = [] ;
    var sum = 0, n = 0 ;
    for(var s in stats)
    {
      s = stats[s] ;
      v = line[s[0]].value ;
      if ( v !== '' && ! isNaN(v) )
      {
	v = (v - s[1]) / s[2] ;
	norms.push( v ) ;
	sum += v ;
	n++ ;
      }
      else
	norms.push('') ;
    }
    if ( n > 2 )
    {
      sum /= n ;
      var maxi = 0 ;
      for(var i in norms)
      {
	if ( isNaN(norms[i]) ||  norms[i] === '')
	  continue ;
	norms[i] -= sum ;
	maxi = Math.max(maxi, Math.abs(norms[i])) ;
	if ( norms[i] < stats[i][3] )
	  stats[i][3] = norms[i] ;
	if ( norms[i] > stats[i][4] )
	  stats[i][4] = norms[i] ;	  
      }
      students.push([maxi, line].concat(norms)) ;
    }
  }
  students.sort(function(a,b) { return b[0] - a[0] ; }) ;
    
  v = _("MSG_stat_strange_grade_help")
    + '<table class="colored" style="width:10%"><tr><th><th><th>' ;
  for(var i in stats)
    v += '<th>' + columns[stats[i][0]].title + '<br>'
    + stats[i][1].toFixed(2) ;
  var lin ;
  for(var s in students)
  {
    s = students[s] ;
    var lin = s[1], color ;
    v += '<tr><td>'+lin[0].value + '<td>'+lin[1].value + '<td>'+lin[2].value ;
    for(var c in s)
    {
      if ( c < 2 )
	continue ;
      if ( s[c] > 0 )
      {	
	color = "FEDCBA9876543210".substr(Math.floor(15.99*s[c]/stats[c-2][4]),1);
	color = color + "F" + color ;
      }
      else if ( s[c] <= 0 )
      {
	color = "FEDCBA9876543210".substr(Math.floor(15.99*s[c]/stats[c-2][3]),1);
	color = "F" + color + color ;
      }
      else
	color = "#FFF" ;
      v += '<td style="background:#' + color + '">' + lin[stats[c-2][0]].value;
    }
    v += '</tr>\n' ;
  }
  v += '</table>' ;

  create_popup('strange_grades export_div', _("TITLE_stat_strange_grades"), v, '', false) ;

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
  p.push('var values_to_display={};');
  p.push('var grouped_by = {};') ;
  p.push('var coloration = "";') ;
  p.push('var nr_decimals = "1";') ;
  p.push('var regrouping;') ;
  p.push('var color_coef ;') ;
  p.push('var ue = ' + js(ue) + ';') ;
  p.push('var display_tips = true ;') ;
  p.push('var columns = ' + columns_in_javascript() + ';') ;
  p.push('var lines ;') ;
  p.push('function initialize() {') ;
  p.push('if ( ! wait_scripts("initialize()") ) return ;') ;
  p.push('lib_init();') ;
  p.push('values_to_display[_("B_s_average")]=true;')
  p.push('regrouping = _("B_stat_group_value");') ;
  p.push('lines = ' + lines_in_javascript() + ';') ;
  p.push('setInterval("statistics_display()", 200);') ;
  p.push('}') ;
  p.push('</script>') ;
  p.push('<p class="hidden_on_paper">' + _("MSG_stat_export_spreadsheet"));
  p.push('<br><a class="hidden_on_paper" href="javascript:strange_grades()">' + _("MSG_stat_strange_grades")
	 + '</a>');
  p.push('<table class="hidden_on_paper">') ;

  var t = [], cols = column_list_all() ;
  for(var data_col in cols)
    {
      data_col = cols[data_col].toString() ;
      if ( ! columns[data_col].is_empty )
	t.push(display_button(data_col, columns[data_col].title,
			      ! columns[data_col].hidden
			      && columns[data_col].type == 'Note',
			      'columns_to_display',
			      html(columns[data_col].comment)));
    }
  print_choice_line(p, _("MSG_stat_columns_to_display"),
		    _("TIP_stat_columns_to_display"),
		    t.join(' '),
		    'columns_to_display') ;

  t = [] ;
  var column ;
  for(var data_col in cols)
    {
      data_col = cols[data_col].toString() ;
      column = columns[data_col] ;
      if ( column.is_empty )
	continue ;
      var stats = compute_stats(filtered_lines, data_col) ;
      if ( true || filtered_lines.length / stats.nr_uniques() > 1 )
	{
	  var comment = html(column.comment) ;
	  if ( comment )
	    comment += '<br>' ;
	  comment += stats.nr_uniques() + ' ' + _("MSG_stat_uniq_values")
	  
	  t.push(display_button(data_col, column.title,
				column.title == 'Seq' || column.title == 'Grp',
				'grouped_by', comment));
	}
    }
  print_choice_line(p, _("MSG_stat_group_by"), _("TIP_stat_group_by"),
		    t.join(' '),
		    'grouped_by') ;
      
  print_choice_line(p, _("MSG_stat_nr_digit"), _("TIP_stat_nr_digit"),
		    radio_buttons('nr_decimals', ['0', '1', '2', '3'], '1'),
		    'nr_decimals') ;

  t = [] ;
  for(var i in colorations)
      t.push([_(i), _(i.replace('B','TIP'))]) ;
  print_choice_line(p, _("MSG_stat_coloring"), _("TIP_stat_coloring"),
		    radio_buttons('coloration', t, _("B_stat_colored")),
		    'coloration') ;

  print_choice_line(p, _("MSG_stat_group_by"), _("TIP_stat_group_by"),
		    radio_buttons('regrouping',
				  [[_("B_stat_group_value"),
				    _("TIP_stat_group_value")],
				   [_("B_stat_group_author"),
				    _("TIP_stat_group_author")],
				   [_("B_stat_group_month"),
				    _("TIP_stat_group_month")],
				   ],_("B_stat_group_value")),
		    'regrouping') ;

  p.push('</table>') ;
  p.push('<div style="clear:both" id="content"></div>') ;
  p.push('<script>') ;
  // The timeout is for IE (100 is not enough)
  p.push('setTimeout(initialize, 200) ;') ;
  p.push('</script>') ;

  var w = window_open(url + '/files/' + version + '/ok.png') ;
  w.document.open('text/html') ;
  w.document.write(html_begin_head(true) + p.join('\n')) ;
  w.document.close() ;
  return w ;
}
