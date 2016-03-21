// -*- coding: utf-8 -*-
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

function facebook_picture(line, more)
{
  var url = '<A HREF="' + suivi + '/' + line[0].value + '">' ;
  var firstname = title_case(line[1].value) ;
  if ( ! more )
    more = '' ;
    
  return '<DIV CLASS="facebook"><DIV CLASS="content"><IMG CLASS="pic" SRC="'
    + student_picture_url(line[0].value) + '"><BR>' + url
    + firstname + '<BR>' + line[2].value + '</A></DIV>' + more + '</DIV>' ;
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

function facebook_click(event)
{
  event = the_event(event) ;
  var value = event.target.innerHTML ;
  var a = event.target.parentNode.parentNode.parentNode.getElementsByTagName('A')[0] ;
  var student = a.href.toString().replace(new RegExp(".*/", ""), "") ;
  var line_id = login_to_line_id(login_to_id(student)) ;
  var data_col = the_phone_popup_column.data_col ;
  if ( lines[line_id][data_col].value == value )
    return ;
  var items = event.target.parentNode.parentNode.childNodes ;
  for(var i=0; i<items.length; i++)
    {
      items[i].className = 'item' ;
      items[i].childNodes[0].innerHTML = "" ; // Remove feedback
      items[i].style.border = "" ;
    }
  cell_set_value(event.target.parentNode, value, line_id, data_col)
  update_cell_at(line_id, data_col) ;
  try {
    the_current_cell.update(true) ;
    } catch(e) { console.log(e) ; } // For phone_facebook
  event.target.parentNode.className = 'selecteditem' ;
  event.target.parentNode.style.border = "0.1em solid "
    + event.target.parentNode.style.color ;
  clearTimeout(update_histogram_id) ; // For phone_facebook
}

var the_phone_popup_column

function phone_facebook(column_id)
{
  var cls, v, color ;
  var t = [] ;
  var column ;
  if ( column_id ) // From home page
    column = columns[data_col_from_col_id(column_id)] ;
  else
    column = the_current_cell.column ;
  the_phone_popup_column = column ;
  var vals = column.real_type.cell_completions("", column) ;
  if ( vals.length == 0 )
    return true ;
  if ( vals.length <= 4 )
    fontsize = 200 ;
  else if ( vals.length <= 6 )
    fontsize = 160 ;
  else if ( vals.length <= 8 )
    fontsize = 120 ;
  else
    fontsize = 100 ;
  for(var line in filtered_lines)
    {
      line = filtered_lines[line] ;
      if ( line[0].value === '' )
	continue ;
      var more = '<div class="items" style="font-size:' + fontsize + '%">' ;
      if ( line[column.data_col].modifiable(line, column) )
      {
	for(var i in vals)
	{
	  if ( vals[i] == line[column.data_col].value )
	    cls = 'selecteditem' ;
	  else
	    cls = 'item' ;
	  if ( vals[i] == abi )
	    color = "F00" ;
	  else if ( vals[i] == abj )
	    color = "00F" ;
	  else if ( vals[i] == pre )
	    color = "0F0" ;
	  else
	    color = "888" ;
	  v = html(vals[i]) ;
	  if ( v == '' )
	    v = '&nbsp;' ;
	  more += '<div class="' + cls + '" style="color:#' + color
	    + (cls == 'selecteditem' ? ';border: 0.1em solid #' + color : '')
	    + '"><span></span><div onclick="facebook_click(event)">'
	    + v + '</div></div>' ;
	}
      }
      more += '</div>' ;
      t.push(facebook_picture(line, more)) ;
    }

  create_popup('phone_facebook',
	       html(year + ' ' + semester + ' ' + ue
		    + ' ' + column.title),
	       t.join(''),
	       '', false) ;
  if ( column_id )
    {
      var e = document.getElementById('popup_id') ;
      e.style.left = 0 ;
      e.style.right = 0 ;
      e.style.top = 0 ;
      e.style.bottom = 0 ;
      e.style.height = "auto" ;
      e.getElementsByTagName('BUTTON')[0].style.display = "none" ;
    }
}

function tablefacebook(replace, column_id)
{
  var p, s, line ;
  /*
  if ( ! phone_facebook() )
    return ;
  */
  if ( do_touchstart.touch_device || column_id )
    {
      if ( ! phone_facebook(column_id) )
	return ;
    }

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
  p.push('setTimeout(initialize,200) ;') ; // Timeout for IE
  p.push('</script>') ;

  var w = window_open(url + '/files/' + version + '/ok.png', replace) ;
  w.document.open('text/html') ;
  w.document.write(html_begin_head(true) + p.join('\n')) ;
  w.document.close() ;
  return w ;
}
