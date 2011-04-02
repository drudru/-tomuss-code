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

function update_line_menu()
{
  var nr ;

  if ( filtered_lines )
    nr = filtered_lines.length ;
  else
    nr = lines.length ;

  update_a_menu(2, table_attr.nr_lines, nr, Math.max(nr*1.5,
						     table_attr.nr_lines*1.1),
		document.getElementById('t_table_attr_nr_lines')) ;
}

function nr_lines_change(t)
{
  change_table_size(t);
  update_line_menu() ;
}
