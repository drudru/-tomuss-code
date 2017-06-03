// -*- coding: utf-8 -*-
/*
  TOMUSS: The Online Multi User Simple Spreadsheet
  Copyright (C) 2015-2017 Thierry EXCOFFIER, Universite Claude Bernard

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
	       + '/' + ue + '/import_zip/' + popup_column().the_id
	       + '" method="POST" enctype="multipart/form-data">'
	       + _('MSG_upload_file')
	       + '<br>'
	       + '<input type="file" name="data" onchange="upload_file_choosed(this)">'
	       + '<input type="text" name="filename" hidden=1>'
	       + '</form>') ;
}


function ImportPDF(iframe, name, nr_pages)
{
  hide_the_tip_real(true) ;
  iframe.getElementsByTagName("P")[0].style.display = "none" ;
  
  var local_this = this ;
  this.name = name ;
  this.nr_pages = nr_pages ;
  this.pages = [] ;
  this.ready_pages = 0 ;
  this.scroll_current = [50, 0] ;
  this.margin = 2.5 ;
  iframe.write("<style>"
	       + "#pdfimport   { position: relative ; width: 100% ; }"
	       + "#pdfpages    { position: absolute; left: 25%; width: 75% }"
	       + "#pdfstudents { position: absolute; width: 100%; }"
	       + "#pdfstudents .studentname { text-align: right; width: 25% }"
	       + "#pdfpages DIV {"
	       + "    height: 5em ;"
	       + "    overflow: scroll ;"
	       + "    margin: 0px ;"
	       + "}"
	       + "#pdfpages DIV.first, #pdfstudents > DIV { margin-top: " + this.margin + "em}"
	       + "#pdfstudents > DIV {"
	       + "-webkit-transition: margin-top 0.5s, top 0.5s ; "
	       + "        transition: margin-top 0.5s, top 0.5s ; "
	       + "}"
	       + "#pdfstudents > DIV {"
	       + "    position: absolute ;"
	       + "    width: 100% ;"
	       + "}"
	       + "DIV.first .pdfup, DIV.first .pdfdown, DIV.first .studentswap{"
	       + "   display: none ; }"
	       + ".pdfmenu {"
	       + "    position: absolute;"
	       + "    font-weight: bold ;"
	       + "    font-size: 120% ;"
	       + "    color: #00F ;"
	       + "    z-index: 1 ;"
	       + "    margin-top: -" + this.margin*0.7 + "em;"
	       + "    width: 100% ;"
	       + "}"
	       + ".pdfmenu SPAN { cursor: pointer; position: absolute }"
	       + ".pdfup { left: 30% }"
	       + ".pdfdown { left: 25% }"
	       + ".studentswap { left: 20% }"
	       + "</style>"
	       + _("MSG_column_attr_import_zip_pdf")
	       + '<div id="pdfimport">'
	       + '<div id="pdfstudents"></div>'
	       + '<div id="pdfpages"></div>'
	       + '</div>') ;
  var pages_per_student = nr_pages / filtered_lines.length ;
  if ( pages_per_student < 1 )
    pages_per_student = 1 ;
  this.students = iframe.getElementById("pdfstudents") ;
  this.button = iframe.getElementsByTagName("BUTTON")[0] ;
  this.button.onclick = this.send.bind(this) ;
  this.button.disabled = 1 ;
  for(var i in filtered_lines)
  {
    var line = filtered_lines[i] ;
    var student = iframe.createElement("DIV") ;
    student.innerHTML = '<div class="pdfmenu">'
      + '<span class="studentswap">⇵</span>'
      + '<span class="pdfdown">▲</span>'
      + '<span class="pdfup">▼</span>'
      + '</div>'
      + '<div class="studentname">'
      + html(line[0].value) + "<br>"
      + html(line[1].value) + "<br>"
      + html(line[2].value) + '</div>' ;
    student.pdfpage = Math.floor(pages_per_student * i) ;
    student.pdfline = line ;
    student.onclick = function(event) { local_this.click(event) ; } ;
    this.students.appendChild(student) ;
  }
  this.pages = iframe.getElementById("pdfpages") ;
  for(var i = 0 ; i < nr_pages ; i++)
  {
    var page = iframe.createElement("DIV") ;
    page.innerHTML = '<img>' ;
    page.onscroll = function(event) {
      var target = the_event(event).target
      local_this.scroll(target.scrollTop, target.scrollLeft) ; } ;
    this.pages.appendChild(page) ;
  }
  this.update() ;
}

window.ImportPDF = ImportPDF ; // To allow the IFRAME to use it

ImportPDF.prototype.scroll = function(top, left)
{
  this.scroll_current = [top, left] ;
  for(var i = 0 ; i < this.pages.childNodes.length ; i++)
  {
    this.pages.childNodes[i].scrollTop = top ;
    this.pages.childNodes[i].scrollLeft = left ;
  }
} ;

ImportPDF.prototype.undo = function() {
  for(var i in this.undo_pdf)
    this.undo_pdf[i][0].pdfpage = this.undo_pdf[i][1] ;
} ;

ImportPDF.prototype.nr_pages_student = function(student)
{
  if ( student.nextSibling )
    return student.nextSibling.pdfpage - student.pdfpage ;
  else
    return this.nr_pages - student.pdfpage ;
} ;

ImportPDF.prototype.remove_student_without_pdf = function()
{
  for(var i = 0 ; i < this.students.childNodes.length ; i++)
  {
    var student = this.students.childNodes[i] ;
    if ( this.nr_pages_student(student) == 0 )
    {
      if ( confirm(_("MSG_referent_remove_student")
		   + student.pdfline[0].value + " " + student.pdfline[1].value
		   + " " + student.pdfline[2].value) )
	this.students.removeChild(student) ;
      else
	this.undo() ;
      return ;
    }
  }
} ;

ImportPDF.prototype.click = function(event)
{
  var t = the_event(event).target ;
  var student = t ;
  while( student.pdfpage === undefined )
    student = student.parentNode ;
  var dir ;
  if ( t.className == 'pdfup' )
    dir = 1 ;
  else if ( t.className == 'pdfdown' )
    dir = -1 ;
  if ( dir )
  {
    this.undo_pdf = [] ;
    while ( student )
    {
      this.undo_pdf.push([student, student.pdfpage]) ;
      student.pdfpage += dir ;
      student = student.nextSibling ;
    }
  }
  else if ( t.className == 'studentswap' )
  {
    var s = student.previousSibling ;
    this.students.removeChild(student) ;
    this.students.insertBefore(student, s) ;
    var p = s.pdfpage ;
    s.pdfpage = student.pdfpage ;
    student.pdfpage = p ;
  }
  this.remove_student_without_pdf() ;
  this.update() ;
} ;

ImportPDF.prototype.update = function()
{
  for(var i = 0 ; i < this.pages.childNodes.length ; i++)
  {
    this.pages.childNodes[i].className = "" ;
  }
  var previous_student, previous_page ;
  for(var i = 0 ; i < this.students.childNodes.length ; i++)
  {
    var student = this.students.childNodes[i] ;
    var page = this.pages.childNodes[student.pdfpage] ;
    student.style.top = page.offsetTop + "px" ;
    page.className = "first" ;
    if ( previous_student )
    {
      previous_student.style.height = (page.offsetTop
				       - previous_page.offsetTop) + 'px' ;
      student.className = "" ;
    }
    else
    {
      student.className = "first" ;
    }
    previous_page = page ;
    previous_student = student ;
  }
} ;

ImportPDF.prototype.add = function()
{
  var img = this.pages.childNodes[this.ready_pages++].getElementsByTagName(
    "IMG")[0] ;
  var page = "00000" + this.ready_pages ;
  var scroll_current = this.scroll_current ;
  page = page.substr(page.length - 6) ;

  img.src = url + "/=" + ticket + '/tmp/' + this.name + '/p' + page + '.png' ;

  setTimeout(function() { img.scrollTop = scroll_current[0] ;
			  img.scrollLeft = scroll_current[1] ; },
	     1000) ;

  if ( this.ready_pages == this.nr_pages )
    this.button.disabled = 0 ;
} ;

ImportPDF.prototype.send = function()
{
  var d = {} ;
  for(var i = 0 ; i < this.students.childNodes.length ; i++)
  {
    var student = this.students.childNodes[i] ;
    d[student.pdfline.line_id] = (student.pdfpage + 1)
      + '\001' + this.nr_pages_student(student) ;
  }

  do_post_data(d,
	       url + '/=' + ticket + '/' + year + '/' + semester + '/' + ue
	       + '/upload_pdf/' + page_id + '/' + popup_column().the_id) ;  
} ;



