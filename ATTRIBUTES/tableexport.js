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

function table_export()
{
  var s = 'Faites un copié collé du tableau suivant dans l\'import de colonnes si vous voulez les mettre dans une autre table.<pre>\n' ;

  s += '<table border><tr>' ;
  for(var c in column_attributes)
    if ( ! column_attributes[c].computed && c != 'position' )
      s += bs + '<small>' + c ;
  var cls = column_list_all();

  for(var column in cls)
    {
      column = columns[cls[column]] ;
      if ( column.is_empty )
	continue ;
      if ( column.author == '*' ) // ro_user
	continue ;
      s += '<tr>' ;
      for(var c in column_attributes)
	if ( ! column_attributes[c].computed && c != 'position'  )
	  s += bs + column_attributes[c].formatter(column, column[c]) ;
      s += '\n</tr>' ;
    }
  s += '\n</table>\n' ;
  new_window(s, 'text/html') ;
}
