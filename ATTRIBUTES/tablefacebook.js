// -*- coding: utf-8 -*-
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

function facebook_picture(line)
{
  var url = '<A HREF="' + suivi + '/' + line[0][0] + '">' ;
  var firstname = line[1][0] ;
  if ( firstname.length >= 2 )
    firstname = firstname.substr(0,1)+ firstname.substr(1).toLowerCase() ;
    
  return '<DIV CLASS="facebook">' + url +
    '<IMG SRC="' + student_picture_url(line[0][0]) + '"><BR>' +
    firstname + '<br>' + line[2][0] + '</A></DIV>' ;
}

function compute_groups_key(line)
{
  var s = [] ;
  for(var data_col in grouped_by)
    s.push(line[data_col][0]) ;
  return s.join('\001') ;
}

function groups_values()
{
  var g = {}, s ;
  for(var data_lin in lines)
    g[compute_groups_key(lines[data_lin])] = true ;
  tabl = [] ;
  for(var gg in g)
    tabl.push(gg) ;
  tabl.sort() ;
  return tabl ;
}

function facebook_display()
{
  var groups = groups_values() ;
  var s = [] ;
  var first = '' ;

  if ( groups.length == 1 )
    {
      s.push('<h2>' + year + ' ' + semester + ' ' + ue + '</h2>') ;
      for(var i in lines)
	s.push(facebook_picture(lines[i])) ;
    }
  else
    for(var group in groups)
      {
	group = groups[group] ;
	s.push('<h2 style="' + first + 'clear:both">'
	       + year + ' ' + semester + ' ' + ue) ;
	first = 'page-break-before:always;' ;
	var i = 0 ;
	for(var g in grouped_by)
	  {
	    s.push(' ' + grouped_by[g] + '=' + group.split('\001')[i++] ) ;
	  }
	s.push("</h2>")
	for(var data_lin in lines)
	  if ( compute_groups_key(lines[data_lin]) == group )
	    s.push(facebook_picture(lines[data_lin])) ;
      }
  document.getElementById('content').innerHTML = s.join('\n') ;
}

function facebook_toggle(data_col, tag)
{
  if ( grouped_by[data_col] )
    {
      delete grouped_by[data_col] ;
      tag.style.background = '' ;
      tag.style.color = '' ;
    }
  else
    {
      tag.style.background = 'black' ;
      tag.style.color = 'white' ;
      grouped_by[data_col] = columns[data_col] ;
    }
}

function facebook_a_toggle(data_col)
{
  return '<span class="facebook_column" onclick="facebook_toggle('
    + data_col + ',this);facebook_display();">'
    + html(columns[data_col].title) + '</span>' ;
}

function tablefacebook()
{
  var p, s, line ;

  p = [
       '<p class="hidden_on_paper">',
       'Ce préambule ne sera pas imprimé. ',
       'Seuls les étudiants filtrés apparaissent ici. ',
       'L\'ordre d\'affichage est celui du tableau. ',
       '<p class="hidden_on_paper">',
       'Si vous voulez une page par groupe d\'étudiants, ',
       'il vous suffit de cliquer sur ',
       facebook_a_toggle(3), ' et ', facebook_a_toggle(4), '.',
       'Si vous avez une colonne indiquant un nom de salle, ',
       'vous pouvez la sélectionner pour avoir une feuille par salle :</p>',
       '<p class="hidden_on_paper facebook_columns">'
       ] ;
  for(var data_col in columns)
    {
      if ( columns[data_col].is_empty )
	continue ;
      if ( columns[data_col].hidden )
	continue ;
      if ( data_col == 3 || data_col == 4 )
	continue ;
      p.push(facebook_a_toggle(data_col) + ' ') ;
    }

  p.push('<div style="clear:both" id="content">') ;
  p.push('<script>var grouped_by=[], lines = [') ;
  s = [] ;
  for(var data_lin in filtered_lines)
    {
      line = filtered_lines[data_lin] ;
      if ( line[0].value !== '' )
	{
	  var t = [] ;
	  for(var data_col in columns)
	    t.push(line[data_col].get_data()) ;
	  s.push('[' + t.join(',') + ']') ;
	}
    }
  p.push( s.join(',\n') ) ;
  p.push( '] ;') ;
  p.push( 'var columns = [') ;
  s = [] ;
  for(var data_col in columns)
    s.push(js(columns[data_col].title)) ;
  p.push(s.join(',')) ;
  p.push( '] ;') ;
  p.push( 'ue=' + js(ue)) ;
  // turn around IE bug : do not call facebook_display yet....
  p.push('setTimeout("facebook_display()", 100);') ;
  p.push('</script>') ;

  var w = window_open() ;
  w.document.open('text/html') ;
  w.document.write(html_begin_head(true) + p.join('\n')) ;
  w.document.close() ;
  return w ;

}
