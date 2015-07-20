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

function safe_url(t)
{
  return t.replace(RegExp('[$%&?/]', 'g'), '_') ;
}

function upload_filename(t)
{
  t = t.replace("; ", "").split(' ')[1] ;
  if ( t )
    t = safe_url(t) ;
  return t ;
}

function upload_file_choosed(t, ue)
{
  t.nextSibling.value = t.value ;
  unload = document.createElement('IMG') ;
  unload.src = url_suivi + '/=' + ticket + '/unload/' + ue ;
  unload.width = unload.height = 1 ;
  the_body.appendChild(unload) ;
  t.parentNode.submit() ;
}

function upload_double_click(value)
{
  if ( value === '' )
    return value ;
  window.location = url + '/=' + ticket + '/' + year + '/' + semester + '/' + ue
    + '/upload_get/' + the_current_cell.column.the_id
    + '/' + the_current_cell.line_id
    + '/' + the_current_cell.line[1].value + ' ' + the_current_cell.line[2].value
    + ' ' + upload_filename(the_current_cell.cell.comment) ;
  return value ;
}

function upload_format_suivi()
{
  var value = DisplayGrades.value, upload_url, label ;
  var empty = (value === ''
	       || value == DisplayGrades.column.empty_is
	       ) || upload_filename(DisplayGrades.cell.comment) == undefined ;
  var s = [] ;
  if ( ! empty )
    s.push(_('MSG_upload_get')
	   + '<a target="_blank" href="'
	   + url + '/=' + ticket + '/' + year + '/' + semester
	   + '/' + DisplayGrades.ue.ue
	   + '/upload_get/' + DisplayGrades.column.the_id
	   + '/' + DisplayGrades.ue.line_id
	   + '/' + DisplayGrades.ue.ue + "_" + safe_url(DisplayGrades.column.title)
	   + "_" + upload_filename(DisplayGrades.cell.comment)
	   + '">'
	   + ' ' + html(upload_filename(DisplayGrades.cell.comment))
	   + '</a> ' + DisplayGrades.value + "KB") ;

  if ( cell_modifiable_on_suivi() )
    {
      s.push(
	'<form action="'+ url + '/=' + ticket + '/' + year + '/' + semester
	  + '/' + DisplayGrades.ue.ue + '/upload_post/'
	  + DisplayGrades.column.the_id
	  + '/' + DisplayGrades.ue.line_id
	  + '" method="POST" enctype="multipart/form-data">'
	  + (empty
	     ? _('MSG_upload_new')
	     : _('MSG_upload_change')
	    )	
	  + ' <input type="file" name="data" onchange="upload_file_choosed(this,'
	  + js2(DisplayGrades.ue.ue) + ')">'
	  + '<input type="text" name="filename" hidden=1>'
	  + '</form>'
      ) ;
    }
  if ( s.length === 0 )
    return _('MSG_no_file_uploaded') ;

  return s.join('<br>') ;
}
