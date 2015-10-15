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

/*REDEFINE
  Send the url allowing to jump over a web frontend not allowing big files.
  It is only used for importing zip file.
  It is not used for the student file uploading.
*/
function get_the_upload_url()
{
  return url ;
}

function upload_file_choosed(t)
{
  var div = document.createElement("DIV") ;
  div.innerHTML = '<p style="color:red">' + _("MSG_abj_wait") + '</p>' ;
  t.parentNode.appendChild(div) ;
  t.nextSibling.value = t.value ;
  t.parentNode.submit() ;
}

function import_zip()
{
  create_popup("import_zip", _("TITLE_column_attr_import_zip"),
	       '<iframe id="frame_import_zip"></iframe>', '', false) ;
  
  var iframe = document.getElementById("frame_import_zip") ;
  iframe_write(iframe, upload_file_choosed,
	       _("TIP_column_attr_import_zip")
	       + '<p>'
	       + '<form action="' + get_the_upload_url()
	       + '/=' + ticket + '/' + year + '/' + semester
	       + '/' + ue + '/import_zip/' + the_current_cell.column.the_id
	       + '" method="POST" enctype="multipart/form-data">'
	       + _('MSG_upload_file')
	       + '<br>'
	       + '<input type="file" name="data" onchange="upload_file_choosed(this)">'
	       + '<input type="text" name="filename" hidden=1>'
	       + '</form>') ;
}
