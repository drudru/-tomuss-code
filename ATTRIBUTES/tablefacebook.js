// -*- coding: utf-8 -*-
/*
    TOMUSS: The Online Multi User Simple Spreadsheet
    Copyright (C) 2008-2012 Thierry EXCOFFIER, Universite Claude Bernard

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
  var url = '<A HREF="' + suivi + '/' + line[0].value + '">' ;
  var firstname = title_case(line[1].value) ;
    
  return '<DIV CLASS="facebook">' + url +
    '<IMG SRC="' + student_picture_url(line[0].value) + '"><BR>' +
    firstname + '<br>' + line[2].value + '</A></DIV>' ;
}

function facebook_display()
{
  var groups = compute_groups_values(grouped_by) ;
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
	    s.push(' ' + columns[g].title + '=' + group.split('\001')[i++] ) ;
	  }
	s.push("</h2>")
	for(var line_id in lines)
	  if ( compute_groups_key(grouped_by, lines[line_id]) == group )
	    s.push(facebook_picture(lines[line_id])) ;
      }
  document.getElementById('content').innerHTML = s.join('\n') ;
}

function facebook_a_toggle(data_col)
{
  return '<span class="button_toggle" onclick="button_toggle(grouped_by,'
    + data_col + ',this);facebook_display();">'
    + html(columns[data_col].title) + '</span>' ;
}

function tablefacebook(replace)
{
  var p, s, line ;

  p = [printable_introduction(),
       '<p class="hidden_on_paper">',
       _("MSG_facebook_grp"), facebook_a_toggle(3), _("MSG_facebook_and"),
       facebook_a_toggle(4), '.<br>',
       _("MSG_facebook_paging"), '</p>',
       '<p class="hidden_on_paper toggles">'
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
  p.push('<script>') ;
  p.push( 'ue=' + js(ue) + ';') ;
  p.push( 'var columns = ') ;
  p.push(columns_in_javascript()) ;
  p.push( ';') ;
  p.push('var grouped_by=[], lines ;') ;
  p.push('function initialize()') ;
  p.push('{') ;
  p.push('if ( ! wait_scripts("initialize()") ) return ; ') ;
  p.push('lines = ' + lines_in_javascript() + ';') ;
  p.push('facebook_display();') ;
  p.push('}') ;
  p.push('setTimeout(initialize,100) ;') ; // Timeout for IE
  p.push('</script>') ;

  var w = window_open('', replace) ;
  w.document.open('text/html') ;
  w.document.write(html_begin_head(true) + p.join('\n')) ;
  w.document.close() ;
  return w ;
}
