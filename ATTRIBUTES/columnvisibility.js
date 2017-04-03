// -*- coding: utf-8 -*-
/*
    TOMUSS: The Online Multi User Simple Spreadsheet
    Copyright (C) 2014,2017 Thierry EXCOFFIER, Universite Claude Bernard

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

function column_visibility_formatter(column, value)
{
  var input = document.getElementById('t_column_visibility_date') ;
  var s = document.getElementById('t_column_visibility') ;
  if ( input )
    {
      set_editable(input, value == 0) ;
      input.style.display = value == 0 ? "inline" : "none" ;
      if ( value != 0 && value != 3 && value != 4 )
	s.style.width = "99%" ;
      else
	s.style.width = "25%" ;
      if ( value != 3 || value != 4 )
      {
	var e = document.getElementById("visibility_link") ;
	e.href = suivi.split('/=')[0]
	  + (value == 3 ? "/public/" : "/public_login/" )
	  + year + "/" + semester + "/" + ue ;
	e.innerHTML = value == 3 ? _("MSG_visibility_link") : _("MSG_visibility_login")  ;
      }
    }
  return value ;
}
