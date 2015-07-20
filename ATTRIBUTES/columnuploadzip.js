// -*- coding: utf-8 -*-
/*
  TOMUSS: The Online Multi User Simple Spreadsheet
  Copyright (C) 2015 Thierry EXCOFFIER, Universite Claude Bernard

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

function upload_zip()
{
  var s = url + '/=' + ticket + '/' + year + '/' + semester + '/' + ue
    + '/upload_zip/' + the_current_cell.column.the_id
    + '/' ;
  var t = [] ;
  for(var i in filtered_lines)
    t.push(filtered_lines[i].line_id) ;
  t.push(ue + "_" + safe_url(the_current_cell.column.title) + ".zip")
  s += t.join('/') ;

  window.open(s) ;
}
