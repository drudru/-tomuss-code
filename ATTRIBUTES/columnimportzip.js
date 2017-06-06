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
  this.iframe = iframe ;
  this.name = name ;
  this.nr_pages = nr_pages ;
  this.scroll_left = 10 ;
  this.scroll_top = 50 ;
  this.scroll_done = true ;
  this.margin = 2.5 ; // Space between students
  this.page_height = 5 ;
  iframe.write("<style>"
	       + "#pdfimport   { position: relative ; width: 100% ; }"
	       + "#pdfpages    { position: absolute; left: 25%; width: 75% }"
	       + "#pdfstudents { position: absolute; width: 100%; }"
	       + "#pdfstudents .studentname { text-align: right; width: 25% }"
	       + ".next_empty .studentname { opacity: 0.25 }"
	       + "#pdfpages DIV {"
	       + "    height: " + this.page_height + "em ;"
	       + "    overflow: scroll ;"
	       + "    margin: 0px ;"
	       + "}"
	       + "#pdfpages DIV.last { margin-bottom: " + this.margin + "em}"
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
	       + "DIV.previous_empty .pdfdown, DIV.next_empty .pdfup"
	       + "{ opacity: 0.2 ; pointer-events: none ; }"
	       + ".pdfmenu {"
	       + "    position: absolute;"
	       + "    font-weight: bold ;"
	       + "    font-size: 120% ;"
	       + "    color: #00F ;"
	       + "    z-index: 1 ;"
	       + "    margin-top: -" + this.margin*0.6 + "em;"
	       + "    width: 100% ;"
	       + "}"
	       + ".pdfmenu SPAN { cursor: pointer; position: absolute }"
	       + ".pdfup { left: 30% }"
	       + ".pdfdown { left: 25% }"
	       + ".studentswap { left: 20% }"
	       + "</style>"
	       + _("MSG_column_attr_import_zip_pdf") + '<br><br>'
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
  this.will_scroll() ;
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
    page.onscroll = function(event) {
      var target = the_event(event).target
      local_this.scroll_top = target.scrollTop ;
      local_this.scroll_left = target.scrollLeft ;
      local_this.will_scroll() ; } ;
    page.pdfnumber = i + 1 ;
    this.pages.appendChild(page) ;
  }
  this.to_load = this.pages.firstChild ;
  this.update() ;
}

window.ImportPDF = ImportPDF ; // To allow the IFRAME to use it

ImportPDF.prototype.scroll = function()
{
  for(var i = 0 ; i < this.pages.childNodes.length ; i++)
  {
    if ( this.pages.childNodes[i].firstChild
	 && this.pages.childNodes[i].firstChild.offsetHeight > 0 )
    {
      this.pages.childNodes[i].scrollTop = this.scroll_top ;
      this.pages.childNodes[i].scrollLeft = this.scroll_left ;
    }
  }
  this.scroll_done = true ;
} ;

ImportPDF.prototype.nr_pages_student = function(student)
{
  if ( student.nextSibling )
    return student.nextSibling.pdfpage - student.pdfpage ;
  else
    return this.nr_pages - student.pdfpage ;
} ;

ImportPDF.prototype.student_empty = function(student)
{
  return this.pages.childNodes[student.pdfpage].pdfnumber == 0 ;
} ;

ImportPDF.prototype.translate = function(student, direction)
{
  while ( student )
  {
    student.pdfpage += direction ;
    student = student.nextSibling ;
  }
} ;

ImportPDF.prototype.remove_page_if_empty = function(student, page)
{
  if ( page.pdfnumber == 0 )
  {
    this.pages.removeChild(page) ;
    this.translate(student.nextSibling, -1) ;
    this.nr_pages-- ;
    return true ;
  }
} ;

ImportPDF.prototype.remove_student_without_pdf = function()
{
  for(var i = 0 ; i < this.students.childNodes.length ; i++)
  {
    var student = this.students.childNodes[i] ;
    if ( this.nr_pages_student(student) == 0 )
    {
      // Add empty page
      var page = this.iframe.createElement('DIV') ;
      page.pdfnumber = 0 ;
      if ( student.nextSibling )
	this.pages.insertBefore(page, this.pages.childNodes[student.pdfpage]);
      else
	this.pages.appendChild(page) ;
      this.translate(student.nextSibling, 1) ;
      this.nr_pages++ ;
      continue ;
    }
    if ( this.nr_pages_student(student) == 1 )
      continue ;
    if ( this.remove_page_if_empty(student,
				   this.pages.childNodes[student.pdfpage]))
      continue ;
    this.remove_page_if_empty(
      student,
      this.pages.childNodes[student.pdfpage
			    + this.nr_pages_student(student)-1
			   ]);
  }
} ;

ImportPDF.prototype.click = function(event)
{
  var t = the_event(event).target ;
  var student = t ;
  while( student.pdfpage === undefined )
    student = student.parentNode ;
  if ( t.className == 'pdfup' )
    this.translate(student, 1) ;
  else if ( t.className == 'pdfdown' )
    this.translate(student, -1) ;
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
  var previous_empty ;
  for(var i = 0 ; i < this.students.childNodes.length ; i++)
  {
    var student = this.students.childNodes[i] ;
    var page = this.pages.childNodes[student.pdfpage] ;
    var nr_pages = this.nr_pages_student(student) ;
    this.pages.childNodes[student.pdfpage + nr_pages - 1].className = "last" ;
    student.style.top = page.offsetTop + "px" ;
    student.style.height = nr_pages * this.page_height + 'em' ;
    var cls = [] ;
    if ( i == 0 )
      cls.push('first') ;
    if ( student.previousSibling && this.student_empty(student.previousSibling) )
      cls.push('previous_empty') ;
    if ( this.student_empty(student) )
      cls.push('next_empty') ;
    student.className = cls.join(' ') ;
    previous_empty = page.pdfnumber == 0 ;
  }
} ;

ImportPDF.prototype.will_scroll = function()
{
  if ( this.scroll_done )
  {
    this.scroll_done = false ;
    setTimeout(this.scroll.bind(this),
	       this.button.disabled != 0 ? 1000 : 100) ;
  }
} ;

ImportPDF.prototype.add = function()
{
  while( this.to_load.pdfnumber === 0 )
    this.to_load = this.to_load.nextSibling ;
  var page = "00000" + this.to_load.pdfnumber ;
  page = page.substr(page.length - 6) ;
  this.to_load.innerHTML =
    '<img src="' + url + "/=" + ticket + '/tmp/' + this.name + '/p'
    + page + '.png">' ;

  this.to_load = this.to_load.nextSibling ;
  this.will_scroll() ;

  while( this.to_load && this.to_load.pdfnumber === 0 )
    this.to_load = this.to_load.nextSibling ;
  if ( ! this.to_load )
    this.button.disabled = 0 ;
} ;

ImportPDF.prototype.send = function()
{
  var d = {} ;
  for(var i = 0 ; i < this.students.childNodes.length ; i++)
  {
    var student = this.students.childNodes[i] ;
    var first_page = this.pages.childNodes[student.pdfpage].pdfnumber ;
    if ( first_page )
      d[student.pdfline.line_id] = first_page
      + '\001' + this.nr_pages_student(student) ;
  }

  do_post_data(d,
	       url + '/=' + ticket + '/' + year + '/' + semester + '/' + ue
	       + '/upload_pdf/' + page_id + '/' + popup_column().the_id) ;  
} ;



