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

var table_forms_element ;

function table_forms_resize()
{
    if ( ! table_forms_element )
	return ;
    var top_left_e = table.childNodes[0].childNodes[3] ;
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

function table_forms_goto(event)
{
    var input = the_event(event).target ;
    if ( element_focused === input )
	return ;
    element_focused = input ;
    var e = table_forms_tr(input) ;
    var cls_all = column_list(0, columns.length) ;
    for(var col in cls_all)
	if ( cls_all[col].data_col == e.data_col )
	    {
		page_horizontal(0, col, true) ;
		break ;
	    }
}

function table_forms_blur(event)
{
    var input = the_event(event).target ;
    var tr = table_forms_tr(input) ;
    cell_set_value_real(the_current_cell.line_id, tr.data_col,
			input.value, tr.firstChild.firstChild) ;
    input.value = the_current_cell.cell.value ;
    element_focused = undefined ;
}

function table_forms_keypress(event)
{
    var input = the_event(event).target ;
    var save = the_current_cell.input ;
    the_current_cell.input = input ;
    element_focused = undefined ;
    input.id = "table_forms_keypress" ;
    the_current_cell.keydown(event) ;
    element_focused = input ;
    the_current_cell.input = save ;
}

function table_forms_drop(event)
{
    if ( element_focused )
	element_focused.blur() ;
    the_event(event).target.focus();
    table_forms_goto(event) ;
}

function table_forms_jump(lin, col, do_not_focus, line_id, data_col)
{
    var new_class = this.tr.className.replace(/ *currentformline/, '') ;
    var line_change = (this.lin != lin) ;
    
    this.tr.className = new_class ;
    this.jump_old(lin, col, true, line_id, data_col) ;
    var t = table_forms_element.getElementsByTagName('tbody')[0] ;
    var i, tr, cell ;
    if ( line_change )
	{
	    table_forms_element.getElementsByTagName('h1')[0].innerHTML =
		html(this.line[0].value) + ' ' + html(this.line[1].value)
		+ ' ' + html(this.line[2].value) ;
	    for(var i in t.childNodes)
		{
		    tr = t.childNodes[i] ;
		    if ( ! tr.lastChild )
			continue ;
		    cell = this.line[tr.data_col] ;
		    tr.lastChild.firstChild.value = cell.value ;
		    var img = tr.getElementsByTagName('IMG') ;
		    if ( img.length )
			    img[0].parentNode.removeChild(img[0]) ;
		    if ( ! cell.modifiable() )
			tr.className = 'ro' ;
		    else
			tr.className = '' ;
		}
	}
    this.tr.className += ' currentformline' ;
    this.input.className += ' currentformline' ;
}

function table_forms_close()
{
    if ( element_focused )
	element_focused.blur() ;
    Current.prototype.jump = Current.prototype.jump_old ;
    table_forms_element.parentNode.removeChild(table_forms_element) ;
    table_forms_element = undefined ;
    table_fill() ;
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
	    if ( data_col < 3 )
		continue ;
	    column = columns[data_col] ;
	    if ( column.is_empty )
		continue ;
	    if ( column.hidden )
		continue ;
	    
	    line = document.createElement('tr') ;
	    line.data_col = data_col ;

	    td_title = document.createElement('td') ;
	    line.appendChild(td_title) ;
	    td_title.className = "ctitle" ;
	    td_title.innerHTML = '<tt><b></b></tt><b>' + html(column.title)
		+ '</b>. <small><em>' + html(column.comment) + '</em></small>';

	    td_value = document.createElement('td') ;
	    line.appendChild(td_value) ;
	    if ( column.type == 'Text' )
		td_value.innerHTML = '<TEXTAREA' + e + '></TEXTAREA>' ;
	    else
		td_value.innerHTML = '<INPUT' + e + '>' ;
	    tb.appendChild(line) ;
	}
    table_forms_resize() ;
    the_current_cell.jump(3,0) ; // XXX To force form update
    the_current_cell.jump(2,0) ;
}
