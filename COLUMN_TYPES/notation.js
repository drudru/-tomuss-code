/*
  TOMUSS: The Online Multi User Simple Spreadsheet
  Copyright (C) 2016 Thierry EXCOFFIER, Universite Claude Bernard

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

/*
  Classes :
  * NotationGrade : grade, max and comment
  * NotationQuestion : question, max, steps, type
  + NotationGrade
  * Notation : question list

  The question list and the grade list:
  * are updated on each keystroke
  * are stored on student change
  The grades of all the students are computed on popup close.

  Type of question :
  * 0 : question
  * 1 : deleted question
  * 2 : question bonus

  XXX BAD: these comments indicate some lines to modified synchronously
*/

// TODO
// XXX Export global
// XXX Global Comments
// XXX Comment completion
// XXX Feedback sauvegarde

function NotationGrade(txt)
{
  this.comment = '' ;
  this.stored = 0 ;
  this.max = 1 ;
  this.set_comment(txt) ;
  this.local_change = false ;
  this.not_graded = true ;
}

NotationGrade.prototype.set_comment = function(value)
{
  var g ;
  try {
    g = RegExp('^ *([-0-9.]*)[-0-9. ]*/([0-9.]*) *((.|\n)*)', 'm').exec(value) ;
    g = [Number(g[1]), Number(g[2]), g[3]] ;
  }
  catch(e) {
    g = RegExp('^ *([-0-9.]*)', 'm').exec(value) ;
    g = [isNaN(g[1]) ? this.stored : Number(g[1]), this.max, this.comment] ;
  }
  var error = this.set_grade(g[0], g[1]) ;
  this.local_change |= this.comment != g[2] ;
  this.not_graded &= ! this.local_change ;
  this.comment = g[2] ;
  return error ;
} ;

NotationGrade.prototype.set_grade = function(value, max)
{
  var old_stored = this.stored ;
  var error ;
  this.max = Math.max(0.1, Math.min(100, max)) ;
  if ( this.max != max )
    error = "MSG_notation_max_error" ;
  this.stored = Math.max(this.min === undefined ? -9999 : this.min,
			 Math.min(this.max, value)) ;
  if ( this.stored != value )
    error = "MSG_notation_value_error" ;
  this.grade = this.stored / this.max ;
  this.local_change |= old_stored != this.stored ;
  this.not_graded &= ! this.local_change ;
  return error ;
} ;

NotationGrade.prototype.toJSON = function()
{
  return (this.stored + "/" + this.max + " " + this.comment).trim() ;
} ;

function NotationQuestion(dict)
{
  this.question = "" ;
  this.max = 1 ;
  this.steps = 2 ;
  this.type = 0 ;
  for(var key in dict)
    this[key] = dict[key] ;
  this.initial_value = this.hash() ;
  this.set_grade() ;
}

NotationQuestion.prototype.toJSON = function()
{
  var d = {id: this.id} ;
  for(var key in notation_default)
    if ( this[key] != notation_default[key] )
      d[key] = this[key] ;
  return d ;
} ;

NotationQuestion.prototype.hash = function()
{
  return this.question + this.max + this.steps + this.type ;
} ;

NotationQuestion.prototype.grade_and_comment = function()
{
  var v = this.grade.grade * this.max ;
  if ( this.steps == 2 )
    v = v.toFixed(1) ;
  else if ( this.steps > 2 )
    v = v.toFixed(2) ;
  v = '     ' + v ;
  v = v.substr(v.length-5, 5) ; // Right justify
  return v + '/' + this.max + ' ' + this.grade.comment ;
} ;

NotationQuestion.prototype.set_grade = function(txt)
{
  var not_graded = ! txt ;
  if ( not_graded )
    txt = "0/" + this.max ;
  this.grade = new NotationGrade(txt) ;
  this.grade.not_graded = not_graded ;
} ;

NotationQuestion.prototype.set_grade_to = function(value)
{
  if ( this.is_a_bonus() )
    this.grade.min = -this.grade.max ;
  else
    this.grade.min = 0 ;
  this.grade.set_grade(value, this.max) ;
  this.grade.not_graded = false ;
} ;

NotationQuestion.prototype.html = function(modifiable, questions_modifiable)
{
  var q, comment ;
  var q_class = "question" ;
  var c_class = "comment_input" ;
  if ( this.is_fully_empty_question() )
  {
    q = _("MSG_notation_question") ;
    q_class += ' empty' ;
    comment = _("MSG_notation_comment") ;
    c_class += ' empty' ;
  }
  else
  {
    q = this.question ;
    comment = this.grade_and_comment() ;
  }
  // XXX BAD
  return '<div id="' + this.id + '" class="type' + this.type + '">'
    + '<input value="' + encode_value(q) + '"'
    + ' class="' + q_class + '"'
    + ' onpaste="Notation.on_paste(event)"'
    + ' onfocus="Notation.on_focus(event)"'
    + (modifiable ? '' : ' disabled')
    + '>'
    + (questions_modifiable
       ? hidden_txt('<span class="bonus">Ⓑ</span>', _('TIP_bonus_toggle'))
       : '<span class="bonus not_modifiable">Ⓑ</span>'
      )
    + '<canvas tabindex="0"></canvas>'
    + '<div class="incdec">'
    + (questions_modifiable
       ? '<span class="inc">⊕</span><br><span class="dec">⊖</span>'
       : '&nbsp;<br>&nbsp;')
    + '</div>'
    + '<input'
    + (modifiable ? '' : ' disabled')
    + ' onfocus="Notation.on_focus(event)"'
    + ' onpaste="Notation.on_paste(event)"'
    + ' value="' + encode_value(comment) + '"'
    + ' class="' + c_class + '">'
    + '</div>' ;
} ;

NotationQuestion.prototype.suivi = function()
{
  if ( this.is_a_bonus() && this.grade.stored == 0 )
    return '' ;
  return '<tr><td style="text-align:right">'
    + (this.is_a_question()
       ? this.grade.stored + '/' + this.grade.max
       : (this.grade.stored > 0 ? '+' : '') + this.grade.stored)
    + '<td>' + html(this.question)
    + (this.grade.comment !== ''
       ? '<br><em>' + html(this.grade.comment).replace(/\n/g, '<br>') + '</em>'
       : '')
    + '</tr>' ;
} ;

NotationQuestion.prototype.set_comment = function(value, column_modifiable)
{
  var error = this.grade.set_comment(value) ;
  if ( this.max != this.grade.max && ! column_modifiable )
    error = "MSG_notation_not_allowed" ;
  else
    this.max = this.grade.max ;
  return error ;
} ;

/*
max = 2 steps = 2                               get_max   get_max_right
             0        0.5        1        1.5        2        2.5
             |---------|---------|---------|---------|---------|
             |                   |                   |
get_value01  0.......................................1
get_x_left   0........................................xxxxxxxxx1
get_x_center 0xxxxx.......................................xxxxx1
get_slot_width                    <=======>
*/

NotationQuestion.prototype.get_max = function() {
  return this.is_a_bonus() ? this.max * 2 : this.max ; } ;

NotationQuestion.prototype.get_value01 = function() {
  return this.is_a_bonus() ? (this.grade.grade + 1)/2 : this.grade.grade ; } ;

NotationQuestion.prototype.get_max_right = function() {
  return this.get_max() + 1/this.steps ; } ;

NotationQuestion.prototype.get_x_left = function() {
  return this.get_value01() * this.get_max() / this.get_max_right() ; } ;

NotationQuestion.prototype.get_x_center = function() {
  return this.get_x_left()  +  this.slots_width() / 2 ; } ;

NotationQuestion.prototype.nr_slots = function() {
  return this.get_max() * this.steps + 1 ; } ;

NotationQuestion.prototype.slots_width = function() {
  return 1 / this.nr_slots() ; } ;

NotationQuestion.prototype.draw_canvas = function()
{
  var canvas = document.getElementById(this.id
				      ).getElementsByTagName('CANVAS')[0] ;
  canvas.width = canvas.offsetWidth ;
  canvas.height = canvas.offsetHeight ;

  var c = canvas.getContext("2d") ;
  if ( this.grade.not_graded )
  {
    c.fillStyle = "#FFF" ;
    c.fillRect(0, 0, canvas.width, canvas.height) ;
  }
  c.fillStyle = "#000" ;
  for(var i = 0 ; i <= this.nr_slots() ; i++)
  {
    var x = canvas.width * i / this.nr_slots() ;
    c.beginPath() ;
    c.moveTo(x, 0) ;
    c.lineTo(x, canvas.height * (i % this.steps === 0 ? 0.5 : 0.25)) ;
    c.closePath() ;
    c.stroke() ;
  }
  if ( ! this.grade.not_graded )
  {
    c.fillStyle = '#'+["F44","DA4","888","AD4","4F4","4F4"][
      Math.floor(5 * this.get_x_center())] ;
    c.fillRect(canvas.width * this.get_x_left(), 0,
	       canvas.width * this.slots_width(), canvas.height) ;
  }
  c.fillStyle = "#000" ;
  c.font = "10px sans";
  for(var i = 0 ; i <= this.get_max(); i++)
    c.fillText(
      Number((this.is_a_bonus() ? i - this.get_max()/2 : i).toFixed(3)),
      canvas.width * (i/this.get_max_right() + this.slots_width()/2) - 4,
      canvas.height - 1);
} ;

NotationQuestion.prototype.is_a_question = function() {
  return this.type === 0 ; } ;

NotationQuestion.prototype.is_a_bonus = function() {
  return this.type === 2 ; } ;

NotationQuestion.prototype.is_a_question_or_bonus = function() {
  return this.is_a_question() || this.is_a_bonus() ; } ;

NotationQuestion.prototype.is_an_empty_question = function() {
  return this.is_a_question() && this.question === '' ; } ;

NotationQuestion.prototype.is_not_an_empty_question = function() {
  return this.is_a_question() && this.question !== '' ; } ;

NotationQuestion.prototype.is_not_an_empty_bonus = function() {
  return this.is_a_bonus() && this.question !== '' ; } ;

NotationQuestion.prototype.is_fully_empty_question = function() {
  return this.is_an_empty_question()
    && this.grade.grade === 0 && this.grade.comment === '' ; } ;

var notation_default = new NotationQuestion({}) ;
delete notation_default["initial_value"] ;
delete notation_default["grade"] ;

function Notation()
{
}

Notation.prototype.log = function(txt)
{
  // console.log(txt) ;
} ;

Notation.prototype.start = function()
{
  if ( ! this.jump_old )
    this.jump_old = the_current_cell.jump.bind(the_current_cell) ;
  this.column = the_current_cell.column ;
  the_current_cell.jump = this.jump.bind(this) ;
  create_popup(
    'notation_content',
    '<style>'
      + 'DIV.notation_content { border: 2px solid black; top: 10em ; left: 23em ; right: 1em; bottom: 0px }'
      + '#notation_content { white-space: nowrap }'
      + 'DIV.notation_content .empty { color: #888 }'
      + 'DIV.notation_content INPUT { font-size: 100% }'
      + 'DIV.notation_content DIV * { vertical-align: middle }'
      + 'DIV.notation_content INPUT.question { width: 20% }'
      + 'DIV.notation_content INPUT.comment_input { width: 52% ; }'
      + 'DIV.notation_content CANVAS { width: 20% ; height: 1.5em ; opacity: 0.5 ; cursor: pointer }'
      + 'DIV.notation_content DIV:hover > CANVAS { opacity: 1 }'
      + 'DIV.notation_content .incdec, DIV.notation_content .bonus { opacity:0 ; display: inline-block; text-align: right; transition: opacity 2s }'
      + 'DIV.notation_content H1 { position: relative ; height: 1.5em}'
      + 'DIV.type2 .bonus { color: #00F }'
      + '#notation_student { }'
      + '#notation_column { position: absolute ; right: 4em;}'
      + '#notation_grade {  }'
      + 'CANVAS:hover + DIV.incdec, DIV.incdec:hover, .question:hover + DIV SPAN.bonus, SPAN.bonus:hover, DIV.notation_content .type2 .bonus { opacity: 1 }'
      + '</style>'
      + '<h1>'
      + '<span id="notation_column">' + html(this.column.title) + '</span>'
      + '<span id="notation_student"></span>: '
      + '<span id="notation_grade"></span> '
      + '<span id="notation_error"></span></h1>',
    '<div id="notation_content"'
      + ' onmouseup="Notation.on_mouse_up(event)"'
      + ' onmousedown="Notation.on_mouse_down(event)"'
      + ' onkeyup="Notation.on_keyup(event)"'
      + ' onmousemove="Notation.on_mouse_move(event)"'
      + '></div>',
    '', false) ;
  this.popup_close = popup_close ;
  this.notation_student = document.getElementById("notation_student") ;
  this.notation_grade   = document.getElementById("notation_grade") ;
  this.notation_content = document.getElementById("notation_content") ;
  this.notation_error   = document.getElementById("notation_error") ;
  popup_close = this.close.bind(this) ;
  this.parse_questions(this.column.comment) ;
  this.select_current_line() ;
  this.add_empty_question_if_needed() ;
  this.column_modifiable = column_change_allowed(this.column) ;
  this.update_popup() ;
  this.notation_error.innerHTML = _("MSG_notation_help") ;
  this.notation_error.style.color = "#888" ;
  this.focus(this.question_list()[0], 2 /* XXX BAD */) ;
} ;

Notation.prototype.parse_questions = function(txt)
{
  this.log("parse") ;
  var questions ;
  try {
    questions = JSON.parse(txt) ;
  } catch(e) {
    questions = [] ;
  }
  this.questions = {} ;
  for(var i in questions)
  {
    questions[i].priority = i ;
    this.questions[questions[i].id] = new NotationQuestion(questions[i]) ;
  }
} ;

Notation.prototype.save_current_line = function()
{
  this.log("save_current_line " + (this.line ? this.line[0].value : "?")) ;
  this.save_grades() ;
  this.save_questions() ;
} ;

Notation.prototype.clear_current_line = function()
{
  this.log("clear_current_line") ;
  this.save_current_line() ;
  the_current_cell.tr.className =
    the_current_cell.tr.className.replace(/ *currentformline/, '') ;
} ;

Notation.prototype.parse_grades = function(txt)
{
  var grades ;
  try { grades = JSON.parse(txt) ; }
  catch(e) { grades = {} ; }
  for(var i in this.questions)
    this.questions[i].set_grade(grades[i]) ;
} ;

Notation.prototype.select_current_line = function()
{
  this.log("select_current_line " + the_current_cell.line[0].value) ;
  the_current_cell.tr.className += ' currentformline' ;
  this.line = the_current_cell.line ;
  this.cell = this.line[this.column.data_col] ;
  this.parse_grades(this.cell.comment) ;
  this.modifiable = this.cell && this.cell.is_mine() || i_am_the_teacher ;
  this.notation_error.innerHTML = "" ;
} ;

Notation.prototype.question_list = function()
{
  var questions = [] ;
  for(var i in this.questions)
    if ( this.questions[i].is_a_question_or_bonus() )
      questions.push(this.questions[i]) ;
  this.sort_questions(questions) ;
  return questions ;
} ;

Notation.prototype.jump = function(lin, col, do_not_focus, line_id, data_col)
{
  this.log("jump") ;
  this.clear_current_line() ;
  this.jump_old(lin, col, do_not_focus, line_id, data_col) ;
  this.select_current_line() ;
  this.update_popup() ;
} ;

Notation.prototype.update_all_grades = function()
{
  this.log("update_all_grades") ;
  var cell, v ;
  for(var line_id in lines)
  {
    cell = lines[line_id][this.column.data_col] ;
    if ( cell.comment === '')
      continue ;
    this.parse_grades(cell.comment) ;
    v = this.get_grade() + this.get_bonus() ;
    if ( v !== cell.value )
    {
      cell_set_value_real(line_id, this.column.data_col, v.toString()) ;
      update_line(line_id, this.column.data_col)  ;
    }
  }
} ;

Notation.prototype.close = function()
{
  this.log("close") ;
  this.clear_current_line() ;
  the_current_cell.jump = this.jump_old ;
  popup_close = this.popup_close ;
  popup_close() ;
  this.update_all_grades() ;
  table_fill(true, true, true, true) ;
} ;

Notation.prototype.merge_question_changes = function()
{
  var current = this.questions ;
  this.parse_questions(this.column.comment) ;
  var externes = this.questions ;
  this.questions = current ;
  var priority = millisec() ;
  for(var i in externes)
  {
    if ( ! this.questions[i] )
    {
      // New question from somebody
      this.questions[i] = externes[i] ;
      this.questions[i].priority = priority + i ;
    }
    else if ( this.questions[i].initial_value == this.questions[i].hash() )
    {
      // Not changed by local user
      var saved_priority = this.questions[i].priority ;
      this.questions[i] = externes[i] ;
      this.questions[i].priority = saved_priority ;
    }
  }
} ;

Notation.prototype.save_questions = function()
{
  this.log("save questions") ;
  this.merge_question_changes() ;
  var questions = [] ;
  for(var question in this.questions)
    if ( ! this.questions[question].is_the_last )
      questions.push(this.questions[question]) ;
  this.sort_questions(questions) ;
  var v = JSON.stringify(questions) ;
  if ( v != this.column.comment )
  {
    column_attr_set(this.column, 'comment', v) ;
    column_attr_set(this.column, 'minmax', '[0;' + this.maximum() + ']') ;
    the_current_cell.do_update_column_headers = true ;
    the_current_cell.update_column_headers() ;
  }
} ;

Notation.prototype.merge_grade_changes = function()
{
  var grades ;
  try { grades = JSON.parse(this.cell.comment) ; }
  catch(e) { return ; }

  for(var grade in grades)
  {
    var question = this.questions[grade] ;
    if ( ! question )
      continue ;
    if ( question.grade.not_graded || ! question.grade.local_change )
    {
      // Get the grade from somebody else
      question.grade = new NotationGrade(grades[grade]) ;
      question.grade.not_graded = false ;
    }
  }
} ;

Notation.prototype.get_json_grades = function()
{
  var grades = {} ;
  for(var i in this.questions)
    if ( ! this.questions[i].grade.not_graded )
      grades[i] = this.questions[i].grade ;
  return JSON.stringify(grades) ;
} ;

Notation.prototype.save_grades = function()
{
  this.log("save student") ;
  this.merge_grade_changes() ;
  var v = this.get_json_grades() ;
  if ( v != this.cell.comment && v !== '{}' )
    comment_change(this.line.line_id, this.column.data_col, v) ;
} ;

Notation.prototype.contain_empty_question = function()
{
  this.log("contain_empty_question") ;
  for(var i in this.questions)
    if ( this.questions[i].is_an_empty_question() )
      return true ;
  return false ;
} ;

Notation.prototype.add_empty_question_if_needed = function()
{
  this.log("add_empty_question_if_needed") ;
  if ( this.contain_empty_question() )
    return ;
  var id = this.unused_id() ;
  this.questions[id] = new NotationQuestion({id: id, priority: millisec()}) ;
  this.update_popup() ;
} ;

Notation.prototype.maximum = function()
{
  var sum = 0 ;
  for(var i in this.questions)
    if ( this.questions[i].is_not_an_empty_question() )
      sum += this.questions[i].max ;
  return Number(sum.toFixed(3)) ;
} ;

Notation.prototype.get_grade = function()
{
  var sum = 0 ;
  for(var i in this.questions)
    if ( this.questions[i].is_not_an_empty_question() )
      sum += this.questions[i].grade.grade * this.questions[i].max ;
  return Number(sum.toFixed(3)) ;
} ;

Notation.prototype.get_bonus = function()
{
  var sum = 0 ;
  for(var i in this.questions)
    if ( this.questions[i].is_not_an_empty_bonus(i) )
      sum += this.questions[i].grade.stored ;
  return sum ;
} ;

Notation.prototype.focus = function(question, what)
{
  if ( ! question )
    return ;
  this.log("focus " + question.id + ' what=' + what);
  for(var i in this.notation_content.childNodes)
  {
    if ( this.notation_content.childNodes[i].id == question.id )
    {
      if ( ! this.modifiable )
	what = 2 ; // XXX BAD
      var e = this.notation_content.childNodes[i].childNodes ;
      if ( e )
      {
	e = e[what] ;
	e.focus() ;
	try { set_selection(e, 0, 0) ; } catch(e) { } ;
      }
      break ;
    }
  }
} ;

Notation.prototype.is_an_empty_value = function(value)
{
  return value === '' || value == _("MSG_notation_question")
    || value == _("MSG_notation_comment") ;
} ;

Notation.prototype.on_focus = function(event)
{
  this.log("on_focus") ;
  event = this.get_event(event) ;
  if ( this.is_an_empty_value(event.target.value) )
  {
    event.target.value = '' ;
    event.target.className = event.target.className.replace(/ *empty/, "") ;
    return ;
  }
} ;

Notation.prototype.update_title = function()
{
  this.log("update title") ;
  this.notation_student.innerHTML = html(this.line[0].value)
    + ' ' + html(this.line[1].value) + ' ' + html(this.line[2].value) ;
  var s = this.get_grade() + '/' + this.maximum() ;
  var b = this.get_bonus() ;
  if ( b )
    s += ' → ' + (this.get_grade()+this.get_bonus()) +'Ⓑ/'+ this.maximum() ;
  this.notation_grade.innerHTML = s ;
} ;

Notation.prototype.sort_questions = function(questions)
{
  // JS dictionary order is random
  questions.sort(function(a,b) { return a.priority - b.priority ; }) ;
} ;

Notation.prototype.update_popup = function()
{
  this.log("update") ;
  var i ;
  this.update_title() ;
  var questions = [] ;
  for(i in this.questions)
    if ( this.questions[i].is_a_question_or_bonus() )
      questions.push(this.questions[i].html(this.modifiable,
					    this.column_modifiable)) ;
  this.sort_questions(questions) ;
  this.notation_content.innerHTML = questions.join('') ;
  for(i in this.questions)
  {
    if ( this.questions[i].is_a_question_or_bonus() )
      this.questions[i].draw_canvas() ;
    this.questions[i].is_the_last = false ;
  }
  this.questions[i].is_the_last = true ;
} ;


Notation.prototype.unused_id = function()
{
  this.log("unused_id") ;
  var used_ids = {} ;
  for(var i in this.questions)
    used_ids[this.questions[i].id] = true ;
  for(var i=0;;i++)
    if ( ! used_ids[page_id + '_' + i] )
      return page_id + '_' + i ;
} ;

Notation.prototype.get_event = function(event)
{
  event = the_event(event) ;
  event.line = event.target ;
  while( ! event.line.id )
    event.line = event.line.parentNode ;
  event.question = this.questions[event.line.id] ;
  event.what = '' ;
  event.question_input = event.line.childNodes[0] ; // XXX BAD
  event.canvas         = event.line.childNodes[2] ; // XXX BAD
  event.comment_input  = event.line.childNodes[4] ; // XXX BAD
  event.child_nr       = myindex(event.line.childNodes, event.target) ;
  switch(event.target)
  {
  case event.question_input: event.what = 'question' ; break ;
  case event.canvas        : event.what = 'canvas'   ; break ;
  case event.comment_input : event.what = 'comment'  ; break ;
  }
  return event ;
} ;

Notation.prototype.on_mouse_move = function(event, force)
{
  event = this.get_event(event) ;
  if (!force && event.what != 'canvas')
    return ;
  if ( this.button_pressed_on != event.question.id )
    return ;

  if ( event.what == 'canvas')
  {
    // -4 because of borders
    var x = (event.x - findPosX(event.target) - 4) / event.target.offsetWidth ;
    if ( event.question.is_a_bonus() )
      x *= 2 ;
    x = x / event.question.get_max() * event.question.get_max_right() ;
    x = x * event.question.max * event.question.steps ;
    x = Math.floor(x) / event.question.steps ;
    if ( event.question.is_a_bonus() )
      x -= event.question.max ;
    event.question.set_grade_to(x) ;
    event.comment_input.value = event.question.grade_and_comment() ;
  }
  event.question.draw_canvas() ;
  this.update_title() ;
} ;

Notation.prototype.on_mouse_down = function(event)
{
  this.log("on_mouse_down") ;
  event = this.get_event(event) ;

  if ( ! event.question )
    return ;
  this.button_pressed_on = event.question.id ;
  if (event.what != 'canvas')
  {
    if ( ! this.column_modifiable )
      return ;
    switch(event.target.className)
    {
    case 'inc':
      event.question.steps = Math.min(event.question.steps+1, 10) ;
      break ;
    case 'dec':
      event.question.steps = Math.max(event.question.steps-1, 1) ;
      break ;
    case 'bonus':
      if ( event.question.is_a_question() )
	event.question.type = 2 ;
      else if ( event.question.is_a_bonus() )
	event.question.type = 0 ;
      event.line.className = event.line.className.replace(
	  /type[0-9]/, 'type' + event.question.type) ;
      break ;
    }
  }
  this.on_mouse_move(event, true) ;
} ;

Notation.prototype.on_mouse_up = function(event)
{
  this.log("on_mouse_up") ;
  this.button_pressed_on = false ;
} ;

Notation.prototype.on_paste = function(event)
{
  this.log("on_paste") ;
  event = this.get_event(event) ;
  var me = this ;
  if ( event.what == 'comment' )
    setTimeout(function() { me.on_comment_change(event) ; }, 100) ;
  else if ( event.what == 'question' )
    setTimeout(function() { me.on_question_change(event) ; }, 100) ;
} ;

Notation.prototype.get_comments = function(id)
{
  var g, comments = [] ;
  for(var line_id in lines)
  {
    try {
      g = JSON.parse(lines[line_id][this.column.data_col].comment) ;
      if ( g[id] )
	comments.push(g[id].replace(/[^ ]* */, "")) ;
    }
    catch(e) { }
  }
  return comments ;
} ;

Notation.prototype.on_comment_change = function(event)
{
  this.log("on_comment_change " + event.target.value) ;
  var error = event.question.set_comment(event.target.value,
					 this.column_modifiable) ;
  var length = this.get_json_grades().length ;
  if ( length > max_url_length )
    error = "MSG_notation_to_much_comment" ;
  if ( error )
  {
    this.notation_error.style.color = event.target.style.color = '#F00';
    this.notation_error.style.fontSize = "100%" ;
    this.notation_error.innerHTML = _(error) ;
  }
  else
  {
    this.notation_error.style.color = "#888" ;
    this.notation_error.style.fontSize = "70%" ;
    event.target.style.color = '#000' ;
    this.notation_error.innerHTML = length +'/'+ max_url_length ;
  }
  event.question.draw_canvas() ;
  this.update_title() ;

/* XXX Not saved because no onchange event on completion selection
  ask_login_list = "" ;
  var comments = this.get_comments(event.question.id) ;
  var completions = [] ;
  var current = event.question.grade.comment ;
  for(var i in comments)
    if ( comments[i].substr(0, current.length) == current )
      completions.push([comments[i], "", "", "", comments[i]]) ;
  if ( completions.length > 0 )
  {
    element_focused_saved = event.target ;
    var e = element_focused_saved.onchange ;
    login_list("", completions, event.question.grade.comment) ;
    element_focused_saved.onchange = e ;
  }
//  login_list_hide() ;
*/

} ;

Notation.prototype.on_question_change = function(event)
{
  this.log("on_question_change " + event.target.value) ;
  event.question.question = event.target.value ;
  if ( event.question.question !== '' )
    event.question.is_the_last = false ;
} ;

Notation.prototype.on_keyup = function(event)
{
  event = this.get_event(event) ;
  var questions = this.question_list() ;
  var question_index = myindex(questions, event.question) ;

  switch(event.keyCode)
  {
  case 38: // Cursor up
  case 40: // Cursor down
  case 13: // Return
    if ( event.what == 'question' || event.what == 'comment' )
    {
      var s = get_selection(event.target) ;
      if ( event.what == 'question' )
      {
	this.save_current_line() ;
	this.add_empty_question_if_needed() ;
      }
    }
    questions = this.question_list() ;
    this.focus(questions[question_index	+ (event.keyCode == 38 ? -1 : 1)],
	       event.child_nr) ;
    break ;
  case 37: // Cursor left
  case 39: // Cursor right
    if ( event.what == 'canvas' )
    {
      var x = event.question.grade.grade ;
      x += (event.keyCode == 37 ? -1 : 1)
	* 1/(event.question.max * event.question.steps) ;
      event.question.set_grade_to(x * event.question.max) ;
      event.comment_input.value = event.question.grade_and_comment() ;
      event.question.draw_canvas() ;
      this.update_title() ;
    }
    break ;
  case 34: // Next page
  case 33: // Previous page
    if ( event.keyCode == 34 )
      the_current_cell.cursor_down() ;
    else
      the_current_cell.cursor_up() ;
    setTimeout(function() {
      Notation.focus(questions[question_index], event.child_nr) ; }, 100) ;
    break ;
  default:
    if ( event.target.value == event.target.old_value )
      break ;
    event.target.old_value = event.target.value ;
    if ( event.what == 'comment' )
      this.on_comment_change(event) ;
    else if ( event.what == 'question' )
      this.on_question_change(event) ;
  }

  if ( event.what == 'question' && event.target.value === ''
       && ! event.question.is_the_last
     )
  {
    if ( confirm(_("ALERT_delete_line")) )
    {
      event.question.type = 1 ;
      this.update_popup() ;
    }
  }
} ;

Notation.prototype.suivi = function()
{
  var questions = this.question_list() ;
  s = ['<style>',
       '.DisplayTypeNotation + .CellBottom .DisplayCellColumn,',
       '.DisplayTypeNotation + .CellBottom .DisplayCellComment',
       '{ display: none }',
       '.DisplayTypeNotation .DisplayCellValue .tipped .text',
       '{ display: block }',
       'TABLE.notation_suivi { border-spacing: 0px }',
       'TABLE.notation_suivi TD',
       '{ border: 1px solid #888 ; font-size:120%; vertical-align:top ; }',
       '</style>',
       '<table class="notation_suivi" style="overflow:scroll;">'
      ] ;
  for(var question in questions)
  {
    question = questions[question] ;
    s.push(question.suivi());
  }
  s.push("</table>");
  return s.join("") ;
} ;

Notation = new Notation() ; // Only one instance

function notation_open(value, column)
{
  Notation.start() ;
  return value ;
}

function notation_format_suivi()
{
  Notation.parse_questions(DisplayGrades.column.comment) ;
  Notation.parse_grades(DisplayGrades.cell.comment) ;
  return hidden_txt(
    html(DisplayGrades.cell.value + '/' + DisplayGrades.column.max),
    Notation.suivi()) ;
}
