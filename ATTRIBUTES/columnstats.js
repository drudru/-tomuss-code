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
var t_column_histogram ;
var t_column_average ;

function update_histogram_real()
{
  do_update_histogram = false ;
  if ( the_current_cell.data_col == update_histogram_data_col )
    return ;
  if ( ! t_column_histogram )
    return ;
  update_histogram_data_col = the_current_cell.data_col ;

  var dx = (t_column_histogram.the_width-1) / 27 ;
  var dy = t_column_histogram.the_height ;
  var font_size = Math.min( (dx/0.9).toFixed(0), (dy/2.4).toFixed(0) ) ;
  var the_style =
    'g { pointer-events: none;}' +
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

  if ( ! svg_object )
    {
      var d ;
      try
	{
	  d = document.createElementNS("http://www.w3.org/2000/svg", 'svg');
	  d.setAttribute('width', 1000) ;
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

  histogram_bar('ppn',0*dx,dx,dy,maxmax,stats.nr_ppn(),false,0,0,svg_object);
  histogram_bar('abi',1*dx,dx,dy,maxmax,stats.nr_abi(),false,0,0,svg_object);
  histogram_bar('abj',2*dx,dx,dy,maxmax,stats.nr_abj(),false,0,0,svg_object);
  histogram_bar('pre',3*dx,dx,dy,maxmax,stats.nr_pre(),false,0,0,svg_object);
  histogram_bar('oui',4*dx,dx,dy,maxmax,stats.nr_yes(),false,0,0,svg_object);
  histogram_bar('non',5*dx,dx,dy,maxmax,stats.nr_no (),false,0,0,svg_object);
  histogram_bar('nan',6*dx,dx,dy,maxmax,stats.nr_nan(),false,0,0,svg_object);

  for(i=0; i<20; i++)
    histogram_bar(i, (i+7)*dx, dx, dy, maxmax, stats.histogram[i],
		  true, stats.v_min, stats.v_max, svg_object
		 ) ;

  i = stats.average() ;
  if ( i > 1 )
    i = i.toFixed(1) ;
  else
    i = i.toFixed(2) ;
  t_column_average.innerHTML = i ;
  update_tip_from_value(t_column_average, '<!--INSTANTDISPLAY-->' +
			stats.nr + _("MSG_columnstats_values")
			+ '<br>' + stats.html_resume()) ;

  t = '<!--INSTANTDISPLAY-->' ;
  if(stats.nr_nan()) t+=_("MSG_columnstats_empty")+':'+stats.nr_nan()+' ' ;
  if(stats.nr_ppn()) t+=_("MSG_columnstats_ppn")  +':'+stats.nr_ppn()+' ' ;
  if(stats.nr_abi()) t+=_("MSG_columnstats_abi")  +':'+stats.nr_abi()+' ' ;
  if(stats.nr_abj()) t+=_("MSG_columnstats_abj")  +':'+stats.nr_abj()+' ' ;
  if(stats.nr_pre()) t+=_("MSG_columnstats_pre")  +':'+stats.nr_pre()+' ' ;
  if(stats.nr_yes()) t+=_("MSG_columnstats_yes")  +':'+stats.nr_yes()+' ' ;
  if(stats.nr_no() ) t+=_("MSG_columnstats_no")   +':'+stats.nr_no() +' ' ;
  if(stats.nr )      t+=_("MSG_columnstats_grade")+':'+stats.nr      +' ' ;

  // + '\n' : explanation in update_tip_from_value
  update_tip_from_value(t_column_histogram, t + '\n') ;
}

function update_histogram(force)
{
  var t_column_stats = document.getElementById('t_column_stats') ;
  t_column_histogram = document.getElementById('t_column_histogram') ;
  t_column_average = document.getElementById('t_column_average') ;
  if ( ! t_column_stats )
    return ;
  if ( !  t_column_histogram )
  {
    var tr = document.createElement('TR') ;
    var td1 = document.createElement('TD') ;
    var td2 = document.createElement('TD') ;
    td1.innerHTML = hidden_txt('<div id="t_column_histogram"></div>',
			       _("TITLE_column_attr_stats_histo")) ;
    td2.className = 'm' ;
    td2.innerHTML = hidden_txt('<div id="t_column_average"></div>',
			       _("TITLE_column_attr_stats_average") + '\n') ;
    tr.appendChild(td1) ;
    tr.appendChild(td2) ;
    t_column_stats.appendChild(tr) ;
    update_histogram(force) ;
    return ;
  }
  if ( force )
    update_histogram_data_col = -1 ;

  if ( t_column_histogram && t_column_histogram.offsetWidth )
  {
    t_column_histogram.the_height = t_column_histogram.offsetHeight ;
    t_column_histogram.the_width = t_column_histogram.offsetWidth ;
  }

  if ( update_histogram_id )
    clearTimeout(update_histogram_id) ;

  update_histogram_id = setTimeout(update_histogram_real, 300) ;
}
