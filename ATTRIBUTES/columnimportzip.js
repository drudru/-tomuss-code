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
  hide_the_tip_real(true) ;
  var div = document.createElement("DIV") ;
  div.innerHTML = '<p style="color:red">' + _("MSG_abj_wait") + '</p>' ;
  t.nextSibling.value = t.value ;
  progress_submit(t.parentNode, t.value.match(RegExp("[.]pdf$", "i"))) ;
  var e = t.parentNode.parentNode.firstChild ;
  while ( e !== t.parentNode )
    {
      var next = e.nextSibling ;
      e.parentNode.removeChild(e) ;
      e = next ;
    }
}

function import_zip()
{
  create_popup("import_zip", _("TITLE_column_attr_import_zip"),
	       _("TIP_column_attr_import_zip")
	       + '<h2>' + _('MSG_upload_file') + '</h2>'
	       + '<form action="' + get_the_upload_url()
	       + '/=' + ticket + '/' + year + '/' + semester
	       + '/' + ue + '/import_zip/' + the_current_cell.column.the_id
	       + '" method="POST" enctype="multipart/form-data">'
	       + '<input type="file" name="data" onchange="upload_file_choosed(this)">'
	       + '<input type="text" name="filename" hidden=1>'
	       + '</form><div id="iframe_pdf"></div>',
          '', false) ;
}


function ImportPDF(name, nr_pages)
{
  hide_the_tip_real(true) ;
  
  var local_this = this ;
  this.iframe = document.getElementById("iframe_pdf") ;
  this.name = name ;
  this.nr_pages = nr_pages ;
  this.scroll_left = 10 ;
  this.scroll_top = 50 ;
  this.scroll_done = true ;
  this.page_height = 6 ;
  this.iframe.innerHTML = (
    "<style>"
      + "#pdfimport { width: 100% ; position: relative; }"
      + "#pdfimport .page {"
      + "    height: " + this.page_height + "em ;"
      + "    overflow: scroll ;"
      + "    margin: 0px ;"
      + "    right: 0px ; left: 0px ;"
      + "    transition: top 0.5s ; "
      + "    position: absolute ;"
      + "}"
      + "#pdfimport .student {"
      + "    font-size: 150% ;"
      + "    color: #00F ;"
      + "    width: 110% ;" // Negative margin-right
      + "    height: 1.2em ;"
      + "    background: #DDF ;"
      + "    transition: top 0.5s ; "
      + "    right: 0px ; left: 0px ;"
      + "    position: absolute ;"
      + "    z-index: 1 ;"
      + "}"
      + "#pdfimport .highlight_allowed:hover,"
      + "#pdfimport .moving {"
      + "    background: #BBF ;"
      + "}"
      + "#pdfimport .student SPAN {"
      + "    cursor: pointer;"
      + "    position: absolute;"
      + "    width: 5%;"
      + "    text-align: center;"
      + "    transition: opacity 0.5s;"
      + "}"
      + "#pdfimport > *:first-child *"
      + "    { pointer-events: none ; }"
      + "#pdfimport > *:first-child .pdfup,"
      + "#pdfimport > *:first-child .pdfdown,"
      + "#pdfimport > *:first-child .student_swap"
      + "    { display: none }"
      + "#pdfimport .pdfup { left: 0% }"
      + "#pdfimport .pdfdown { left: 5% }"
      + "#pdfimport .student_swap { left: 10% }"
      + "#pdfimport .student_swap B {"
      + "    margin-right: -0.5em; font-size:120%"
      + "}"
      + "#pdfimport .student .name {"
      + "    left: 15% ;"
      + "    font-size: 80% ;"
      + "    color: #000 ;"
      + "    width: 80% ;"
      + "    pointer-events: none ;"
      + "    bottom: 0px ;"
      + "    text-align: left;"
      + "}"
      + "#pdfimport .empty .name { opacity: 0.25 }"
      + "#pdfimport > *:first-child .pdfup,"
      + "#pdfimport > *:first-child .pdfdown,"
      + "#pdfimport > *:first-child .swap"
      + "    { display: none }"
      + "#pdfimport .previous_empty .pdfdown,"
      + "#pdfimport .next_empty .pdfup"
      + "    { opacity: 0.2 ; pointer-events: none ; }"
      + "</style>"
      + '<button id="pdf_button_import">'
      + _("MSG_column_attr_import_zip_pdf") + '</button><br><br>'
      + '<div id="pdfimport"></div>') ;
  var the_lines = [] ;
  for(var i in filtered_lines)
  {
    line = filtered_lines[i] ;
    if ( ! line_empty(line) )
      the_lines.push(line) ;
  }
  var pages_per_student = nr_pages / the_lines.length ;
  if ( pages_per_student < 1 )
    pages_per_student = 1 ;
  this.blocks = document.getElementById("pdfimport") ;
  this.blocks.onmousedown = function(event) {local_this.mousedown(event) ;};
  this.button = document.getElementById("pdf_button_import") ;
  this.button.onclick = this.send.bind(this) ;
  this.button.disabled = 1 ;
  this.iframe.onmousemove = this.mousemove.bind(this) ;
  this.iframe.onmouseup = this.mouseup.bind(this) ;
  this.iframe_container = this.iframe.parentNode ;
  this.will_scroll() ;
  var last_page = 0 ;

  function student_onclick(event)
  {
          local_this.click(event) ;
  } ;
  function page_onscroll(event)
  {
	var target = the_event(event).target
	local_this.scroll_top = target.scrollTop ;
	local_this.scroll_left = target.scrollLeft ;
	local_this.will_scroll() ;
  } ;
  for(var i in the_lines)
  {
    var line = the_lines[i] ;
    var student = document.createElement("DIV") ;
    student.is_student = true ;
    student.innerHTML =
      '<span class="student_swap"><b>↑</b>↓</span>'
      + '<span class="pdfdown">▲</span>'
      + '<span class="pdfup">▼</span>'
      + '<span class="name">'
      + html(line[0].value)+" "+html(line[1].value)+" "+html(line[2].value)
      + '</span>' ;
    student.pdfline = line ;
    student.onclick = student_onclick ;
    this.blocks.appendChild(student) ;
    var new_page = Math.min(Math.floor(pages_per_student * (Number(i)+1)),
			    nr_pages) ;
    for(var j = last_page; j < new_page; j++)
    {
      var page = document.createElement("DIV") ;
      var img = document.createElement("IMG") ;
      page.appendChild(img) ;
      page.onscroll = page_onscroll ;
      this.blocks.appendChild(page) ;
      if ( j == 0 )
	this.to_load = page ;
    }
    last_page = new_page ;
  }
  this.to_load_number = 1 ;
  this.update() ;
}

ImportPDF.prototype.mousedown = function(event)
{
  event = the_event(event) ;
  if ( ! event.target.is_student )
    return ;
  if ( event.target !== this.blocks.firstChild )
    this.move_student = event.target ;
  stop_event(event) ;
} ;

ImportPDF.prototype.mouseup = function(event)
{
  if ( this.move_student )
  {
    this.move_student = undefined ;
    stop_event(event) ;
  }
} ;

ImportPDF.prototype.move_before = function(block, other)
{
  if ( other )
    this.blocks.insertBefore(block, other) ;
  else
    this.blocks.appendChild(block) ;
} ;

ImportPDF.prototype.move_after = function(block, other)
{
  if ( other.nextSibling )
    this.blocks.insertBefore(block, other.nextSibling) ;
  else
    this.blocks.appendChild(block) ;
} ;

ImportPDF.prototype.mousemove = function(event)
{
  if ( ! this.move_student )
    return ;
  event = the_event(event) ;
  var y = event.y - findPosY(this.blocks) - this.height_page / 2 ;
  for(var block = this.blocks.firstChild ; block ; block = block.nextSibling)
  {
    if ( block.offsetTop > y )
    {
      if ( this.move_student !== block )
      {
	this.move_before(this.move_student, block) ;
	this.update_later() ;
      }
      break ;
    }
    if ( block === this.blocks.lastChild && this.move_student !== block )
    {
      this.move_after(this.move_student, block) ;
      this.update_later() ;
    }
  }
  var scroll = this.blocks.parentNode ;
  if ( y < scroll.scrollTop )
    scroll.scrollTop -= 10 ;
  if ( y > scroll.scrollTop + this.iframe_container.offsetHeight )
    scroll.scrollTop += 10 ;
} ;


ImportPDF.prototype.scroll = function()
{
  for(var block = this.blocks.firstChild ; block ; block = block.nextSibling)
  {
    if ( ! block.is_student )
    {
      block.scrollTop = this.scroll_top ;
      block.scrollLeft = this.scroll_left ;
    }
  }
  this.scroll_done = true ;
} ;

ImportPDF.prototype.student_empty = function(student)
{
  return ! student.nextSibling || student.nextSibling.is_student ;
} ;

ImportPDF.prototype.previous_student = function(student)
{
  do
    student = student.previousSibling ;
  while( student && ! student.is_student ) ;
  return student ;
} ;

ImportPDF.prototype.next_student = function(student)
{
  do
    student = student.nextSibling ;
  while( student && ! student.is_student ) ;
  return student ;
} ;

ImportPDF.prototype.translate = function(student, direction)
{
  for(; student; student = this.next_student(student))
  {
    if ( direction == 1
	 && student.nextSibling && ! student.nextSibling.is_student )
      this.move_after(student, student.nextSibling) ;
    if ( direction == -1
	 && student.previousSibling && ! student.previousSibling.is_student )
      this.move_before(student, student.previousSibling) ;
  }
} ;

ImportPDF.prototype.click = function(event)
{
  var t = the_event(event).target ;
  var student = t ;
  while( ! student.is_student )
    student = student.parentNode ;
  if ( t.className == 'pdfup' )
    this.translate(student, 1) ;
  else if ( t.className == 'pdfdown' )
    this.translate(student, -1) ;
  else if ( t.className == 'student_swap' )
  {
    var previous_student = this.previous_student(student) ;
    var s1 = previous_student.nextSibling ;
    if ( s1 === student )
      this.move_before(student, previous_student) ;
    else
    {
      var s2 = student.nextSibling ;
      this.move_before(student, s1) ;
      this.move_before(previous_student, s2) ;
    }
  }
  this.update_later() ;
} ;

ImportPDF.prototype.update = function()
{
  var cls ;
  var top = 0 ;
  for(var block = this.blocks.firstChild ; block ; block = block.nextSibling)
  {
    block.style.top = top + "px" ;
    if ( block.is_student )
    {
      if ( ! this.height_student  &&  block.offsetHeight > 20)
        this.height_student = block.offsetHeight ;
      top += this.height_student || 20 ;
      cls = ["student"] ;
      if ( block.previousSibling && block.previousSibling.is_student )
	cls.push('previous_empty') ;
      if ( ! block.nextSibling || block.nextSibling.is_student )
	cls.push('next_empty') ;
      if ( this.move_student == block )
	cls.push("moving") ;
      if ( ! this.move_student && block !== this.blocks.firstChild )
	cls.push("highlight_allowed") ;
    }
    else
    {
      if ( ! this.height_page &&  block.offsetHeight > 20)
        this.height_page = block.offsetHeight ;
      top += this.height_page || 60 ;
      cls = ["page"] ;
    }
    block.className = cls.join(' ') ;
  }
} ;

ImportPDF.prototype.update_later = function()
{
  periodic_work_add(this.update.bind(this)) ;
  // setTimeout(this.update.bind(this), 100) ;
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
  var page = "00000" + this.to_load_number++ ;
  this.to_load.firstChild.src = url + "/=" + ticket + '/tmp/' + this.name
    + '/p' + page.substr(page.length - 6) + '.png' ;
  do
    this.to_load = this.to_load.nextSibling ;
  while( this.to_load && this.to_load.is_student ) ;
  this.will_scroll() ;

  if ( ! this.to_load )
    this.button.disabled = 0 ;

  this.update_later() ;
} ;

ImportPDF.prototype.send = function()
{
  var d = {} ;
  var page = 1 ;
  for(var block = this.blocks.firstChild ; block ; )
  {
    var nr_pages = -1 ;
    var student = block ;
    do {
      block = block.nextSibling ;
      nr_pages++ ;
    }
    while( block && ! block.is_student ) ;
    if ( nr_pages )
      d[student.pdfline.line_id] = page + '\001' + nr_pages ;
    page += nr_pages ;
  }
  create_popup("import_zip", _("TITLE_column_attr_import_zip"),
'<iframe style="width:100%; height:90% ; border:0px" name="iframe_pdf"></iframe>',
          '', false) ;

  do_post_data(d,
	       url + '/=' + ticket + '/' + year + '/' + semester + '/' + ue
	       + '/upload_pdf/' + page_id + '/' + popup_column().the_id,
               "iframe_pdf") ;
} ;
