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
  return t.replace(RegExp('[$%&?/\\\\: `]', 'g'), '_') ;
}

function upload_filename(t)
{
  return safe_url(t.replace(/^[^;]*; [^ ]* */, '')) ;
}

function iframe_write(iframe, hook, content)
{
  var iframew = iframe.contentWindow
    ? iframe.contentWindow
    : (iframe.contentDocument.document
       ? iframe.contentDocument.document
       : iframe.contentDocument) ;
  iframew.document.open();
  iframew.upload_file_choosed = hook ;
  iframew.document.write(content) ;
  iframew.document.close();
}

function upload_popup(t, ue, col_id, lin_id, title)
{
  function upload_file_choosed(t)
  {
    var div = document.createElement("DIV") ;
    div.style.fontWeight = "bold" ;
    div.innerHTML = _("MSG_abj_wait") ;
    t.parentNode.appendChild(div) ;
    t.nextSibling.value = t.value ;
    t.parentNode.submit() ;
    try {
      if ( url_suivi === undefined )
	return ;
      }
    catch(e) { return ; }
    unload = document.createElement('IMG') ;
    unload.src = url_suivi + '/=' + ticket + '/unload/' + ue ;
    unload.width = unload.height = 1 ;
    the_body.appendChild(unload) ;
    for(var i in display_data['Grades'][0])
      {
	var obj_ue =  display_data['Grades'][0][i] ;
	if ( obj_ue.ue == ue )
	{
	  for(var j in obj_ue.columns)
	    {
	      if ( obj_ue.columns[j].the_id == col_id )
	      {
		var cell = obj_ue.line[j] ;
		cell[0] = "?" ;
		cell[1] = cell[1] || "" ;
		cell[2] = cell[2] || "" ;
		cell[3] = "; ? " + t.value ;
		DisplayGrades.no_hover = false ;
		display_update_real() ;
		break ;
	      }
	    }
	  break ;
	}
      }
  }
  var width = 24 ; // em
  var pos = findPos(t) ;
  var div = document.createElement('DIV') ;
  div.style.position = "absolute" ;
  div.style.left = pos[0] + "px" ;
  div.style.top = pos[1] + "px" ;
  div.style.background = "#FFF" ;
  div.style.width = width + 'em' ;
  div.style.border = "4px solid #000" ;
  div.style.zIndex = 100000 ;
  div.style.opacity = 0.9 ;
  div.innerHTML = '<button style="float:right;margin:0px" onclick="the_body.removeChild(this.parentNode)">×</button>'
    + '<span style="font-size: 150%">' + _("MSG_upload_new") + '</span>'
    + (title ? title : '') ;
  the_body.appendChild(div) ;
  var free_right = window_width() - (div.offsetWidth + div.offsetLeft) ;
  if ( free_right < 0 )
     div.style.left  = (div.offsetLeft + free_right) + 'px' ;

  var iframe = document.createElement('IFRAME') ;
  iframe.style.width = (width - 0.5) + 'em' ;
  iframe.style.height = "15em" ;
  div.appendChild(iframe) ;
  iframe_write(iframe,
	       upload_file_choosed,
	       '<body style="width:' + (width - 1) + 'em">'
      + '<form action="'+ url + '/=' + ticket + '/' + year + '/' + semester
      + '/' + ue + '/upload_post/' + col_id + '/' + lin_id
      + '" method="POST" enctype="multipart/form-data">'
      + _('MSG_upload_file')
      + '<br>'
      + '<input type="file" name="data" onchange="upload_file_choosed(this)">'
      + '<input type="text" name="filename" hidden=1><br>'
      + (t == the_current_cell.input ?
	 the_current_cell.column.upload_max : DisplayGrades.column.upload_max)
	       + "KB " + _("Maximum")
      + '</form>') ;
}

function upload_double_click(value)
{
  if ( value === '' )
    {
      var ok = the_current_cell.cell.changeable(the_current_cell.line,
						the_current_cell.column) ;
      if ( ok !== true )
	{
	  alert(ok) ;
	  return value ;
	}
      upload_popup(the_current_cell.input, ue,
		   the_current_cell.column.the_id, the_current_cell.line_id,
		   '→' + html(the_current_cell.column.title) + '<br>'
		   + html(the_current_cell.line[1].value + ' '
			  + the_current_cell.line[2].value)) ;
      return value ;
    }
  var more = "" ;
  if ( the_current_cell.cell.history.indexOf("·") != -1 )
    {
      if ( ! confirm(_("CONFIRM_upload_last")) )
	more = "~" ;
    }
  window.open(url + '/=' + ticket + '/' + year + '/' + semester + '/' + ue
	      + '/upload_get/' + the_current_cell.column.the_id
	      + '/' + the_current_cell.line_id + more
	      + '/' + the_current_cell.line[1].value + ' '
	      + the_current_cell.line[2].value
	      + ' ' + upload_filename(the_current_cell.cell.comment)) ;
  return value ;
}

function upload_format_suivi()
{
  var value = DisplayGrades.value, upload_url, label ;
  var empty = (value === ''
	       || value == DisplayGrades.column.empty_is
	       ) ;
  var s = [] ;
  if ( ! empty )
    s.push('<a target="_blank" href="'
	   + url + '/=' + ticket + '/' + year + '/' + semester
	   + '/' + DisplayGrades.ue.ue
	   + '/upload_get/' + DisplayGrades.column.the_id
	   + '/' + DisplayGrades.ue.line_id
	   + '/' + DisplayGrades.ue.ue + "_" + safe_url(DisplayGrades.column.title)
	   + "_" + upload_filename(DisplayGrades.cell.comment)
	   + '">'
	   + _('MSG_upload_get')
	   + ' ' + html(upload_filename(DisplayGrades.cell.comment))
	   + '</a> ' + DisplayGrades.value + "KB") ;

  if ( cell_modifiable_on_suivi() )
    {
      s.push(
	'<a class="clickable" style="color:blue" onclick="upload_popup(this,'
	  + js2(DisplayGrades.ue.ue)
	  + ',' + js2(DisplayGrades.column.the_id)
	  + ',' + js2(DisplayGrades.ue.line_id)
	  + ',' + js2('→' + DisplayGrades.column.title) + ')">'
	  + (empty
	     ? _('MSG_upload_new')
	     : _('MSG_upload_change')
	    )
	  + '</a>') ;
    }
  if ( s.length === 0 )
    return _('MSG_no_file_uploaded') ;

  return s.join('<br>') ;
}
