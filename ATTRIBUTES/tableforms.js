/*
    TOMUSS: The Online Multi User Simple Spreadsheet
    Copyright (C) 2011-2013 Thierry EXCOFFIER, Universite Claude Bernard

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

var table_forms_element ;
var table_forms_table_fill ;
var table_forms_allow_next_table_fill ;

function table_forms_resize()
{
    if ( ! table_forms_element )
	return ;

    var tr = table_forms_element.getElementsByTagName('tbody')[0].firstChild ;
    var data_col = tr.data_col ;
    var top_left_e = table.childNodes[0].childNodes[data_col] ;
    var bottom_right_e = table.childNodes[nr_headers
					  + table_attr.nr_lines - 1]
	.childNodes[table_attr.nr_columns-1] ;
    var top_left = findPos(top_left_e) ;
    var bottom_right = findPos(bottom_right_e) ;

    var form = table_forms_element ;
    form.style.left = top_left[0] + 'px' ;
    form.style.top = top_left[1] + 'px' ;
    form.style.width = (bottom_right[0] + bottom_right_e.offsetWidth
			- top_left[0]) + 'px' ;
    form.style.height = (bottom_right[1] + bottom_right_e.offsetHeight
			 - top_left[1]) + 'px' ;
    form.lastChild.style.height = (form.offsetHeight
				   - form.firstChild.offsetHeight - 6) + 'px' ;
}

function table_forms_tr(e)
{
    while( e.tagName != 'TR' )
	e = e.parentNode ;
    return e;
}

function table_forms_empty_empty_is()
{
  element_focused.value = '' ;
  var tr = table_forms_tr(element_focused) ;
  tr.className = tr.className.toString().replace(/ *default */, '') ;
}

function table_forms_goto(event)
{
    var input = the_event(event).target ;
    if ( element_focused === input )
	return ;
    element_focused = input ;
    element_focused.id = "table_forms_keypress" ;
    element_focused.initial_value = element_focused.value ;
    var e = table_forms_tr(input) ;
    var cls_all = column_list(0, columns.length) ;
    if ( e.className.indexOf('default') != -1 )
      {
	// Without timeout, this does not work on IE
	// The default value come back
        setTimeout(table_forms_empty_empty_is, 1) ;
      }

    /* XXX NOT WORKING : WHY ? */
    
    var col = columns[e.data_col].col ;
    if ( col )
	{
	    // Yet on screen
	    the_current_cell.jump_old(the_current_cell.lin,
				      col,
				      true,
				      the_current_cell.line_id,
				      e.data_col
				      ) ;
	    return ;
	}
    
    for(var col in cls_all)
	{
	    if ( cls_all[col].data_col == e.data_col )
		{
		    table_forms_allow_next_table_fill = false ;
		    page_horizontal(0, col, true) ;
		    break ;
		}
	}
}

// Save the form cell content in the TOMUSS table
function table_forms_save_input(input)
{
    if ( input.value != the_current_cell.cell.value )
	{
	  if ( ! modification_allowed_on_this_line(the_current_cell.line_id,
						   the_current_cell.data_col,
						   input.value) )
		{
		    return ;
		}
	}

    var tr = table_forms_tr(input) ;
    
    cell_set_value_real(the_current_cell.line_id, tr.data_col,
			input.value, tr.firstChild.firstChild) ;
    update_line(the_current_cell.line_id, tr.data_col) ;
}

function table_forms_blur(event)
{
    var input = the_event(event).target ;
    table_forms_save_input(input) ;
    var tr = table_forms_tr(input) ;
    if ( tr.data_col == the_current_cell.data_col )
	input.value = the_current_cell.cell.value ; // Oui => OUI
    if ( input.value === '' )
      {
        input.value = columns[tr.data_col].empty_is ;
	if ( input.value )
	  tr.className += ' default' ;
      }
    element_focused = undefined ;
    table_forms_update_computed_values(the_current_cell) ;
}

function table_forms_update_computed_values(THIS)
{
    var t = table_forms_element.getElementsByTagName('tbody')[0] ;
    for(i in t.childNodes)
	{
	    tr = t.childNodes[i] ;
	    if ( ! tr.lastChild )
		continue ;
	    if ( columns[tr.data_col].real_type.cell_compute )
		{
		    cell = THIS.line[tr.data_col] ;
		    tr.lastChild.firstChild.value = cell.value ;
		}
	}
}

function table_forms_keypress(event)
{
    var input = the_event(event).target ;

    if ( event.keyCode == 13 || event.keyCode == 9 )
	{
	    if ( element_focused.tagName == 'SELECT' )
	         return ; // Completion menu
	    if ( input.tagName == 'INPUT' || event.keyCode == 9  )
		{
		    var tr ;
		    if ( event.shiftKey )
			tr = input.parentNode.parentNode.previousSibling ;
		    else
			tr = input.parentNode.parentNode.nextSibling ;
		    if ( tr )
			{
			    var n_input = tr.firstChild.nextSibling.firstChild;
			    n_input.id = "table_forms_keypress" ;
			    element_focused = n_input;
			    setTimeout(function() { n_input.focus() ; }, 1);
			}
		}
	    else
		setTimeout(function() { table_forms_save_input(input) ; },
			   1) ;
	}
}

function table_forms_drop(event)
{
    if ( element_focused )
	element_focused.blur() ;
    the_event(event).target.focus();
    table_forms_goto(event) ;
}

function table_forms_update(THIS)
{
    var t = table_forms_element.getElementsByTagName('tbody')[0] ;
    var i, tr, cell ;
    if ( THIS.line[0].value === '' )
	{
	    table_forms_element.getElementsByTagName('h1')[0].innerHTML =
		_("TITLE_tableforms") ;
	}
    else
	{
	    table_forms_element.getElementsByTagName('h1')[0].innerHTML =
		html(THIS.line[0].value) + ' ' + html(THIS.line[1].value)
		+ ' ' + html(THIS.line[2].value) ;
	}
    
    for(i in t.childNodes)
	{
	    tr = t.childNodes[i] ;
	    if ( ! tr.lastChild )
		continue ;
	    cell = THIS.line[tr.data_col] ;
	    tr.className = '' ;
	    if ( cell.value !== '' )
	        tr.lastChild.firstChild.value = cell.value ;
	    else
	      {
	        tr.lastChild.firstChild.value = columns[tr.data_col].empty_is;
		if ( columns[tr.data_col].empty_is )
		  tr.className += 'default ' ;
	      }
	    var img = tr.getElementsByTagName('IMG') ;
	    if ( img.length )
		img[0].parentNode.removeChild(img[0]) ;
	    if ( ! columns[tr.data_col].real_type.cell_is_modifiable
		 || ! cell.modifiable(columns[tr.data_col]) )
		tr.className += 'ro' ;
	}
}

function table_forms_jump(lin, col, do_not_focus, line_id, data_col)
{
    var new_class = this.tr.className.replace(/ *currentformline/, '') ;

    this.tr.className = new_class ;
    this.jump_old(lin, col, do_not_focus, line_id, data_col) ;
    table_forms_update(this) ;
    this.tr.className += ' currentformline' ;
    this.input.className += ' currentformline' ;
}

function table_forms_close()
{
    if ( element_focused )
	element_focused.blur() ;
    Current.prototype.jump = Current.prototype.jump_old ;
    table_fill_real = table_forms_table_fill ;

    table_forms_element.parentNode.removeChild(table_forms_element) ;
    table_forms_element = undefined ;
    table_fill(false, true) ;
}

function table_forms()
{
    var data_col, column, line, t, tb, s, td_title, td_value ;

    if ( table_forms_element )
	{
	    table_forms_resize() ;
	    return ;
	}
    Current.prototype.jump_old = Current.prototype.jump ;
    Current.prototype.jump = table_forms_jump ;
    
    table_forms_allow_next_table_fill = true ;
    table_forms_table_fill = table_fill_real ;

    table_fill_real = function() {
	if ( table_forms_allow_next_table_fill )
	    {
		table_forms_table_fill() ;
		setTimeout(table_forms_resize, 1) ;
	    }

	table_forms_allow_next_table_fill = true ;
    } ;

    table_forms_element = document.createElement('DIV') ;
    table_forms_element.innerHTML = '<BUTTON class="close" OnClick="table_forms_close()">&times;</BUTTON><h1></h1><div class="formtable"></div>' ;
    the_body.appendChild(table_forms_element) ;
    table_forms_element.className = 'tableform' ;
    t = document.createElement('table') ;
    table_forms_element.lastChild.appendChild(t) ;
    tb =  document.createElement('tbody') ;
    t.appendChild(tb) ;
    var cls = column_list_all() ;
    var e =' onfocus="table_forms_goto(event)" onblur="table_forms_blur(event)" onkeydown="table_forms_keypress(event)" ondrop="table_forms_drop(event)"';
    for(data_col in cls)
	{
	    data_col = cls[data_col] ;
	    column = columns[data_col] ;
	    if ( column.freezed )
		continue ;
	    if ( column.is_empty )
		continue ;
	    if ( column.hidden )
		continue ;
	    
	    line = document.createElement('tr') ;
	    line.data_col = data_col ;

	    td_title = document.createElement('td') ;
	    line.appendChild(td_title) ;
	    td_title.className = "ctitle" ;
	    td_title.innerHTML = '<tt><span></span></tt><b>' + html(column.title)
		+ '</b>. <small><em>'
		+ html(column.comment.split('///')[0]) + '</em></small>';

	    td_value = document.createElement('td') ;
	    line.appendChild(td_value) ;
	    var attribs = column.comment.split('///') ;
	    var more, nr_line = 1 ;
	    if ( column.type == 'Text' )
		nr_line = 2 ;
	    if ( attribs.length > 1 )
		{
		    attribs = attribs[1].split(' ') ;
		    nr_line = Number(attribs[0]) ;
		    more = ' rows="' + nr_line + '"' ;
		    if ( attribs[1] )
			{
			    more += ' style="background:#' +
				attribs[1].replace(/[^0-9A-Z]/g,'') + ';"' ;
			}
		}
	    else
		more = ''
	    if ( nr_line == 1 )
		td_value.innerHTML = '<INPUT' + e + more + '>' ;
	    else
		td_value.innerHTML = '<TEXTAREA' + e + more + '></TEXTAREA>' ;
	    tb.appendChild(line) ;
	}
    table_forms_resize() ;
    table_forms_update(the_current_cell) ;
    hide_the_tip(true) ;
}
