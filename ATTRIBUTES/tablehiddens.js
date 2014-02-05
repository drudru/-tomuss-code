// -*- coding: utf-8 -*-
/*
    TOMUSS: The Online Multi User Simple Spreadsheet
    Copyright (C) 2014 Thierry EXCOFFIER, Universite Claude Bernard

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

    Contact: Thierry.EXCOFFIER@univ-lyon1.fr
*/

function update_hiddens_menu()
{
  var s = ['<option>' + _('SELECT_hiddens') + '</option>'] ;
  for(var data_col in columns)
  {
    if ( ! column_empty(data_col) && columns[data_col].hidden )
      s.push('<option value="' + data_col + '">'
	     + _('SELECT_hiddens') + ' «' + html(columns[data_col].title)
	     + "»</option>") ;
  }
  
  document.getElementById('t_table_attr_hiddens').innerHTML = s.join('') ;
}

function hiddens_change(t)
{
  var data_col = t.value ;
  var column = columns[data_col] ;
  if ( ! column )
    return ;
  column.hidden = 0 ;
  table_fill(false, true) ;
}
