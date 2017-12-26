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

Classes:
  * NotationGrade : grade, max and comment
  * NotationQuestion : question, max, steps, type
    + NotationGrade
  * Notation : question list

The question list and the grade list:
  * are updated on each keystroke
  * are stored on student change
  The grades of all the students are computed on popup close.

Type of question:
  * 0 : Q question
  * 1 : D deleted question
  * 2 : B question bonus
  * 3 : C comment

Priorities:
  * 0, 1, 2, 3... for the original question list
  * ...           for the remote created questions
  * 1000, 1001... for the localy created questions (updated after merging)
  * 9999          for the empty question (updated to 1000... if filled)

  XXX BAD: these comments indicate some lines to be modified synchronously
*/

var notation_debug = false ;
var notation_types = "QDBC" ;

// TODO
// XXX Feedback sauvegarde

function trunc(x)
{
  return Number(x.toFixed(3)) ;
}

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
    g = RegExp('^ *([-0-9.]*)[-0-9. ]*/([0-9.]*) *(.*)').exec(value) ;
    g = [g[1], g[2], g[1] === '' && g[3] === '' ? this.comment : g[3]] ;
  }
  catch(e) {
    g = RegExp('^ *([-0-9.]*)(.*)').exec(value) ;
    g = [g[1], undefined, g[2] || this.comment] ;
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
  if ( isNaN(value) || value === '' )
    value = this.stored ;
  if ( isNaN(max) || max === '' )
    max = this.max ;
  this.max = Math.max(0.1, Math.min(100, max)) ;
  if ( this.max != max )
    error = "MSG_notation_max_error" ;
  this.stored = Math.max(this.min === undefined ? -99999 : this.min,
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

  if ( dict.substr )
    {
      g = RegExp('([^ ]*) ([0-9]*)([' + notation_types
		 + '])([0-9.]*) (.*)').exec(dict) ;
      if ( g.length != 6 )
	alert("Can not parse: " + dict) ;
      this.id = g[1] ;
      this.steps = Number(g[2]) ;
      this.type = myindex(notation_types, g[3]) ;
      this.max = Number(g[4]) ;
      this.question = g[5] ;
    }
  else
    {
      for(var key in dict)
	this[key] = dict[key] ;
    }
  this.initial_value = this.hash() ;
  this.stats = new Stats() ;
  this.set_grade() ;
}

NotationQuestion.prototype.toJSON = function()
{
  return this.id + ' ' + this.steps + notation_types.substr(this.type,1)
    + this.max + ' ' + this.question ;
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
  this.new_grade(txt, not_graded) ;
} ;

NotationQuestion.prototype.new_grade = function(txt, not_graded)
{
  this.grade = new NotationGrade(txt) ;
  this.grade.not_graded = not_graded ;
  this.set_min() ;
} ;

NotationQuestion.prototype.set_min = function()
{
  if ( this.is_a_bonus() )
    this.grade.min = -this.grade.max ;
  else
    this.grade.min = 0 ;
}

NotationQuestion.prototype.remove_grade = function(v)
{
  this.stats.all_values[v]-- ;
  this.stats.nr-- ;
  this.stats.sum -= v ;
  this.stats.sum2 -= v*v ;
} ;

NotationQuestion.prototype.set_grade_to = function(value)
{
  this.remove_grade(this.grade.grade) ;
  this.grade.set_grade(value, this.max) ;
  this.grade.not_graded = false ;
  this.stats.add(this.grade.grade) ;
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
    + ' ondrop="Notation.on_paste(event)"'
    + ' onfocus="Notation.on_focus(event)"'
    + ' spellcheck="true"'
    + (modifiable ? '' : ' disabled')
    + '><div class="bonus_comment">'
    + (questions_modifiable
       ? hidden_txt('<span class="bonus">Ⓑ</span>', _('TIP_bonus_toggle'))
       : '<span class="bonus not_modifiable">Ⓑ</span>'
      ) + '<br>'
    + ((questions_modifiable && ! this.somebody_is_graded())
       ? hidden_txt('<span class="make_comment">Ⓒ</span>',
		    _('TIP_make_comment'))
       : ''
      ) + '<br>'
    + '</div><canvas tabindex="0" onfocus="Notation.on_focus(event)"></canvas>'
    + '<div class="incdec">'
    + (questions_modifiable
       ? '<span class="inc">⊕</span><br><span class="dec">⊖</span>'
       : '&nbsp;<br>&nbsp;')
    + '</div>'
    + '<input'
    + (modifiable ? '' : ' disabled')
    + ' onpaste="Notation.on_paste(event)"'
    + ' ondrop="Notation.on_paste(event)"'
    + ' onfocus="Notation.on_focus(event)"'
    + ' spellcheck="true"'
    + ' value="' + encode_value(comment) + '"'
    + ' class="' + c_class + '">'
    + (false && notation_debug
       ? '<br>' + this.id
       + ' priority=' + this.priority
       + ' initial_value=' + this.initial_value
       + ' somebody_is_graded=' + this.somebody_is_graded()
       + ' questions_modifiable=' + questions_modifiable
       : '')
    + '</div>' ;
} ;

NotationQuestion.prototype.suivi = function()
{
  if ( this.is_a_bonus() && this.grade.stored == 0 && this.grade.comment === '')
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
  this.remove_grade(this.grade.grade) ;
  var error = this.grade.set_comment(value) ;
  if ( this.max != this.grade.max && ! column_modifiable )
    error = "MSG_notation_not_allowed" ;
  else
    {
      this.max = this.grade.max ;
      this.set_min() ;
      this.stats.add(this.grade.grade) ;
    }

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
  var canvas = document.getElementById(this.id) ;
  if ( ! canvas )
    return ; // deleted question
  canvas = canvas.getElementsByTagName('CANVAS')[0] ;
  if ( ! canvas )
    return ;
  canvas.width = canvas.offsetWidth ;
  canvas.height = canvas.offsetHeight ;

  var c = canvas.getContext("2d") ;

  function line(x1, y1, x2, y2)
  {
    c.beginPath() ;
    c.moveTo(canvas.width * x1, canvas.height * y1) ;
    c.lineTo(canvas.width * x2, canvas.height * y2) ;
    c.closePath() ;
    c.stroke() ;
  }
  if ( this.grade.not_graded )
  {
    c.fillStyle = "#FFF" ;
    c.fillRect(0, 0, canvas.width, canvas.height) ;
  }
  if ( ! this.grade.not_graded )
  {
    c.fillStyle = '#'+["F44","DA4","888","AD4","4F4","4F4"][
      Math.floor(5 * this.get_x_center())] ;
    c.fillRect(canvas.width * this.get_x_left(), 0,
	       canvas.width * this.slots_width(), canvas.height) ;
  }
  for(var i = 0 ; i <= this.nr_slots() ; i++)
  {
    var x = i / this.nr_slots() ;
    line(x, 0, x, i % this.steps === 0 ? 1 : 0.5) ;
  }
  c.fillStyle = "#000" ;
  c.font = "10px sans";
  for(var i = 0 ; i <= this.get_max(); i++)
    c.fillText(
      trunc(this.is_a_bonus() ? i - this.get_max()/2 : i),
      canvas.width * (i/this.get_max_right() + this.slots_width()/2) - 4,
      canvas.height - 1);
  c.strokeStyle = "#000" ;
  line(0, 0, 1, 0) ;
  if ( this.stats.nr >= 5 )
    {
      var avg = this.stats.average() ;
      if ( this.is_a_bonus() )
	avg = avg + 0.5 ;
      var stddev = this.stats.standard_deviation() / 2 ;
      if ( this.max_graded <= this.stats.nr )
	c.fillStyle = c.strokeStyle = "#44F" ;
      else
	c.fillStyle = c.strokeStyle = "#0FF" ;
      line(avg - stddev, 0.125, avg + stddev, 0.125) ;
      c.beginPath() ;
      c.arc(avg * canvas.width, canvas.height/8,canvas.height/6, 0,2*Math.PI);
      c.closePath() ;
      c.fill() ;
    }
} ;

NotationQuestion.prototype.is_a_question = function() {
  return this.type === 0 ; } ;

NotationQuestion.prototype.is_a_bonus = function() {
  return this.type === 2 ; } ;

NotationQuestion.prototype.is_a_comment = function() {
  return this.type === 3 ; } ;

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

NotationQuestion.prototype.toggle_comment = function() {
  this.set_grade_to(1 - this.grade.stored) ;
  var toggle = document.getElementById(this.id) ;
  toggle.className = 'a_comment' + ( this.grade.stored ? ' selected' : '') ;
  var stat = toggle.getElementsByTagName("SPAN")[0] ;
  stat.innerHTML = Number(stat.innerHTML) + (this.grade.stored ? 1 : -1) ;
  toggle.focus() ; // XXX This does not work !
} ;

NotationQuestion.prototype.somebody_is_graded = function(id)
{
  return this.stats.nr != 0 ;
} ;

function Notation()
{
}

Notation.prototype.log = function(txt)
{
  if ( notation_debug )
    console.log(txt) ;
} ;

Notation.prototype.start = function()
{
  if ( this.notation_window_open )
    return ;
  this.notation_window_open = true ;
  this.jump_old = the_current_cell.jump.bind(the_current_cell) ;
  this.popup_is_open = popup_is_open ;
  var me = this ;
  popup_is_open = function() { return me.stop_event ; } ;
  the_current_cell.jump = this.jump.bind(this) ;
  this.init(the_current_cell.column) ;
  create_popup(
    'notation_content',
    '<style>'
      + 'DIV.notation_content { border: 2px solid black; top: 10em ; right: 1em; bottom: 0px; left: 25%; padding: 0px }'
      + 'DIV.notation_content .the_completions { display: block; position: absolute; right: 0px }'
      + 'DIV.notation_content .the_questions { white-space: nowrap ; position: absolute; top: 3em ; right: 0px; left: 0px ; overflow-x: auto; overflow-y: scroll }'
      + 'DIV.notation_content .the_comments { position: absolute; bottom: 0px; overflow: auto; border-top: 1px solid #000 }'
      + 'DIV.notation_content .empty { color: #888 }'
      + 'DIV.notation_content INPUT { font-size: 100% }'
      + 'DIV.notation_content DIV * { vertical-align: middle }'
      + 'DIV.notation_content INPUT.question { width: 20% }'
      + 'DIV.notation_content INPUT.comment_input { width: 40% ; }'
      + 'DIV.notation_content CANVAS { width: 20% ; height: 1.4em ; opacity: 0.5 ; cursor: pointer }'
      + 'DIV.notation_content .incdec, DIV.notation_content .bonus_comment {line-height: 0.8em ; }'
      + 'DIV.notation_content .incdec, DIV.notation_content .bonus_comment, .edit_comment {cursor: pointer }'
      + 'DIV.notation_content .focus CANVAS { opacity: 1 }'
      + 'DIV.notation_content .incdec, DIV.notation_content .bonus_comment { display: inline-block; text-align: right; }'
      + 'DIV.notation_content .incdec, DIV.notation_content .bonus_comment .bonus, DIV.notation_content .bonus_comment .make_comment { opacity:0 ; }'
      + 'DIV.notation_content .last_ones { background: #FFF }'
      + 'DIV.notation_content H1 { position: relative ; height: 1.5em}'
      + 'DIV.type2 .bonus { color: #00F }'
      + 'DIV.notation_content DIV.a_comment { display: inline-block; border: 2px solid #FFF; margin: 4px ; }'
      + 'DIV.notation_content DIV.a_comment:hover { background: #FFF }'
      + 'DIV.notation_content DIV.a_comment.selected { border: 2px solid black }'
      + "DIV.notation_content DIV.a_comment.selected:before { content: '☑'  }"
      + "DIV.notation_content DIV.a_comment:before { content: '☐'  }"
      + 'DIV.notation_content .a_completion { border: 1px solid black; margin: 4px ; white-space: normal; font-size: 80% }'
      + 'DIV.notation_content .a_completion:hover { background: #FFF }'
      + 'DIV.notation_content .stat { color: #888 ; margin: 0.2em }'
      + '#notation_student { }'
      + '#notation_column { position: absolute ; right: 4em;}'
      + '#notation_grade {  }'
      + 'DIV.notation_content .focus DIV.incdec, DIV.notation_content .focus DIV.bonus_comment *, DIV.notation_content .type2 .bonus_comment .bonus { opacity: 1 }'
      + '</style>'
      + '<h1>'
      + '<span id="notation_column">' + html(this.column.title) + '</span>'
      + '<span id="notation_student"></span>: '
      + '<span id="notation_grade"></span><br>'
      + '<span id="notation_other"></span>'
      + '<span id="notation_error"></span>'
      + '</h1>',
    '<div id="notation_content"'
      + ' onmouseup="Notation.on_mouse_up(event)"'
      + ' onmousedown="Notation.on_mouse_down(event)"'
      + ' onkeyup="Notation.on_keyup(event)"'
      + ' onkeydown="Notation.on_keydown(event)"'
      + ' onmousemove="Notation.on_mouse_move(event)"'
      + '></div>',
    '', false) ;
  this.local_priority = 1000 ;
  this.popup_close = popup_close ;
  this.notation_student = document.getElementById("notation_student") ;
  this.notation_grade   = document.getElementById("notation_grade") ;
  this.notation_content = document.getElementById("notation_content") ;
  this.notation_error   = document.getElementById("notation_error") ;
  this.notation_other   = document.getElementById("notation_other") ;
  popup_close = this.close.bind(this) ;
  this.select_current_line() ;
  this.update_popup() ;
  this.update_popup() ; // To compute good sizes for question and comments
  if ( this.column.comment === '' )
    this.notation_error.innerHTML = '<div style="position:absolute;top: 6em; font-weight: normal; color: #000; font-size: 150%">'
  + _("MSG_notation_introduction") + '</div>' ;
  else
    {
      if ( this.modifiable )
	{
	  this.notation_error.innerHTML = _("MSG_notation_help") ;
	  this.notation_error.style.color = "#888" ;
	}
    }
  this.focus(this.question_list()[0], 2 /* XXX BAD */) ;
} ;

Notation.prototype.init = function(column)
{
  this.column = column ;
  this.column_modifiable = column_change_allowed(column) ;
  this.parse_questions(column.comment) ;
} ;

Notation.prototype.parse_questions = function(txt)
{
  this.log("parse questions") ;
  var questions ;
  try {
    questions = JSON.parse(txt) ;
  } catch(e) {
    questions = [] ;
  }
  this.questions = {} ;
  for(var i in questions)
  {
    var question = new NotationQuestion(questions[i]) ;
    question.priority = Number(i) ;
    this.questions[question.id] = question ;
  }
} ;

Notation.prototype.save_current_line = function()
{
  this.log("save_current_line " + (this.line ? this.line[0].value : "?")) ;
  this.save_questions() ;
  this.save_grades() ;
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

Notation.prototype.get_the_commented_line = function(line)
{
  if ( this.column.groupcolumn === '' )
    return line ;

  var col = data_col_from_col_title(this.column.groupcolumn) ;
  if ( ! col )
    return line ;

  var group = line[col].value.toString() ;
  if ( group === '' )
    return line ;
  var group_lines = [] ;
  for(var line_key in lines)
  {
    if ( lines[line_key][col].value.toString() == group
	 && lines[line_key][this.column.data_col].comment !== '' )
      group_lines.push(lines[line_key]) ;
  }
  if ( group_lines.length > 1 )
    {
      var message = _("ALERT_notation_conflict") + '\n' ;
      for(var i in group_lines)
	message += group_lines[i][0].value + ' ' + group_lines[i][1].value
	+ ' ' + group_lines[i][2].value + '\n' ;
      alert(message) ;
      return group_lines[0] ;
    }
  return group_lines.length ? group_lines[0] : line ;
} ;

Notation.prototype.init_cell = function(line)
{
  this.line = this.get_the_commented_line(line) ;
  this.cell = this.line[this.column.data_col] ;
  this.parse_grades(this.cell.comment) ;
  this.modifiable = this.cell && this.cell.is_mine() || i_am_the_teacher ;
} ;

Notation.prototype.select_current_line = function()
{
  this.log("select_current_line " + the_current_cell.line[0].value) ;
  the_current_cell.tr.className += ' currentformline' ;
  this.init_cell(the_current_cell.line) ;
  this.notation_error.innerHTML = "" ;
  this.notation_student.innerHTML = html(this.line[0].value)
    + ' ' + html(this.line[1].value) + ' ' + html(this.line[2].value) ;
  if ( this.line != the_current_cell.line )
    this.notation_other.innerHTML = '→ '
    + html(the_current_cell.line[1].value) + ' '
    + html(the_current_cell.line[2].value) + ' ' ;
  else
    this.notation_other.innerHTML = '' ;
} ;

Notation.prototype.question_list = function(with_deleted)
{
  var questions = [] ;
  for(var i in this.questions)
    if ( this.questions[i].is_a_question_or_bonus()
	 || with_deleted
       )
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
  if ( ! this.jump_from_notation )
    this.stop_event = false ;
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
  if ( this.cancel_save )
    this.cancel_save = false ;
  else
    this.clear_current_line() ;

  the_current_cell.jump = this.jump_old ;
  popup_close = this.popup_close ;
  popup_close() ;
  popup_is_open = this.popup_is_open ;
  this.update_all_grades() ;
  table_fill(true, true, true, true) ;
  this.notation_window_open = false ;
} ;

Notation.prototype.merge_question_changes = function()
{
  var current = this.questions ;
  var current_sorted = this.question_list() ;
  this.parse_questions(this.column.comment) ;
  var remotes = this.question_list(true) ;
  this.questions = current ;
  this.log("Merge before: " + JSON.stringify(this.questions)) ;
  this.log("Merge remote: " + JSON.stringify(remotes)) ;
  current = this.question_list(true) ;
  var done = {} ;
  for(var i in remotes)
  {
    var remote = remotes[i] ;
    var local = this.questions[remote.id] ;
    done[remote.id] = true ;
    if ( ! local )
    {
      this.log('New question from somebody: ' + remote.id) ;
      this.questions[remote.id] = remote ;
    }
    else if ( local.initial_value == local.hash() )
    {
      this.log('Not changed by local user: ' + remote.id) ;
      remote.grade = this.questions[remote.id].grade ; // Keep grades
      this.questions[remote.id] = remote ;
    }
    else
    {
      this.log('Changed by local user: ' + remote.id) ;
      this.log('initial_hash: ' + local.initial_value) ;
      this.log('current hash: ' + local.hash()) ;
      this.questions[remote.id].priority = remote.priority ;
    }
  }
  // Only local questions
  for(var i in current_sorted)
    if ( ! done[current_sorted[i].id]
	 && ! this.is_the_last(current_sorted[i])  )
      current_sorted[i].priority = this.local_priority++ ;

  this.log("Merge after: " + JSON.stringify(this.questions)) ;
} ;

Notation.prototype.save_questions = function()
{
  if ( ! this.column_modifiable )
    return ;
  this.log("save questions") ;
  this.merge_question_changes() ;
  var questions = [] ;
  for(var question in this.questions)
  {
    question = this.questions[question] ;
    if ( ! this.is_the_last(question) )
      {
	questions.push(question) ;
	question.initial_value = question.hash() ;
      }
  }
  this.sort_questions(questions) ;
  var v = JSON.stringify(questions) ;
  this.log("save questions old: " + this.column.comment) ;
  this.log("save questions new: " + v) ;
  if ( v != this.column.comment )
  {
    column_attr_set(this.column, 'comment', v) ;
    column_attr_set(this.column, 'minmax', '[0;' + this.maximum() + ']') ;
    the_current_cell.do_update_column_headers = true ;
    the_current_cell.update_column_headers() ;
  }
} ;

Notation.prototype.is_the_last = function(question) {
  if  ( question.question !== '' )
    return false ;
  var questions = this.question_list() ;
  return question == questions[questions.length-1] ; } ;


Notation.prototype.merge_grade_changes = function()
{
  var grades ;
  try { grades = JSON.parse(this.cell.comment) ; }
  catch(e) { return ; }
  this.log("Remote: " + this.cell.comment) ;
  for(var grade in grades)
  {
    var question = this.questions[grade] ;
    if ( ! question )
      continue ;
    if ( question.grade.not_graded || ! question.grade.local_change )
    {
      this.log("Merge remote grade: " + grade) ;
      question.new_grade(grades[grade]) ;
    }
    else
      this.log("Keep local grade: " + grade) ;
  }
  for(var i in this.questions)
    {
      var question = this.questions[i] ;
      if ( ! question.grade.local_change && grades[question.id] === undefined )
      {
	this.log("Remote grade removed: " + question.id) ;
	question.grade.set_grade(0) ;
      }
    }
} ;

Notation.prototype.get_json_grades = function()
{
  var grades = {} ;
  for(var i in this.questions)
    {
      var question = this.questions[i] ;
      if ( question.grade.not_graded )
	continue ;
      if ( question.is_a_comment() && question.grade.grade === 0)
	continue ;
      grades[i] = question.grade ;
    }
  return JSON.stringify(grades) ;
} ;

Notation.prototype.save_grades = function()
{
  if ( ! this.modifiable )
    return ;
  this.log("save student") ;
  this.merge_grade_changes() ;
  var v = this.get_json_grades() ;
  if ( v == '{}' )
    v = ''
  this.log("Old: " + this.cell.comment) ;
  this.log("New: " + v) ;
  if ( v != this.cell.comment )
    {
      this.log("Store into " + this.line.line_id + ' ' + this.column.data_col);
      comment_change(this.line.line_id, this.column.data_col, v) ;
      for(var i in this.questions)
	this.questions[i].grade.local_change = false ;
    }
} ;

Notation.prototype.contain_empty_question = function()
{
  this.log("contain_empty_question") ;
  for(var i in this.questions)
    if ( this.questions[i].is_an_empty_question() )
      return true ;
  return false ;
} ;

Notation.prototype.add_empty_question_if_needed = function(txt, max)
{
  this.log("add_empty_question_if_needed") ;
  if ( this.contain_empty_question() )
    return ;
  var id = this.unused_id() ;
  this.questions[id] = new NotationQuestion({id: id, priority: 9999}) ;
  if ( txt )
    this.questions[id].question = txt ;
  switch(max)
  {
  case _("MSG_Bonus").toLowerCase():
    this.questions[id].type = 2 ;
    this.questions[id].max = 5 ;
    break ;
  case undefined:
    break ;
  default:
    this.questions[id].max = Number(max) ;
    break ;
  }

  if ( this.notation_error )
  {
    this.notation_error.innerHTML = '' ;
    this.update_error() ;
  }

  return this.questions[id] ;
} ;

Notation.prototype.maximum = function()
{
  var sum = 0 ;
  for(var i in this.questions)
    if ( this.questions[i].is_not_an_empty_question() )
      sum += this.questions[i].max ;
  return trunc(sum) ;
} ;

Notation.prototype.get_grade = function()
{
  var sum = 0 ;
  for(var i in this.questions)
    if ( this.questions[i].is_not_an_empty_question() )
      sum += this.questions[i].grade.grade * this.questions[i].max ;
  return trunc(sum) ;
} ;

Notation.prototype.get_bonus = function()
{
  var sum = 0 ;
  for(var i in this.questions)
    if ( this.questions[i].is_not_an_empty_bonus(i) )
      sum += this.questions[i].grade.stored ;
  return trunc(sum) ;
} ;

Notation.prototype.focus = function(question, what)
{
  if ( ! question )
    return ;
  this.log("focus " + question.id + ' what=' + what);
  var e = document.getElementById(question.id) ;
  if ( ! e || ! e.childNodes )
    return ;
  if ( ! this.modifiable )
    what = 2 ; // XXX BAD
  if ( what != -1 )
    e = e.childNodes[what] ;
  e.focus() ;
  try { set_selection(e, 0, 0) ; } catch(e) { } ;
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
  if ( this.old_focused )
     this.old_focused.className = this.old_focused.className.replace(/ *focus/,
								     '') ;
  this.old_focused = event.line ;
  event.line.className += ' focus' ;
  if ( this.is_an_empty_value(event.target.value) )
  {
    event.target.value = '' ;
    event.target.className = event.target.className.replace(/ *empty/, "") ;
    return ;
  }
  this.update_completions(event) ;
} ;

Notation.prototype.update_title = function()
{
  this.log("update title") ;
  var s = this.get_grade() + '/' + this.maximum() ;
  var b = this.get_bonus() ;
  if ( b )
    s += ' → ' + trunc(this.get_grade()+this.get_bonus()) +'Ⓑ/'+ this.maximum() ;
  this.notation_grade.innerHTML = s ;
} ;

Notation.prototype.sort_questions = function(questions)
{
  // JS dictionary order is random
  questions.sort(function(a,b) { return a.priority - b.priority ; }) ;
} ;

function get_scroll_size(e)
{
  try { return e.lastChild.offsetTop + e.lastChild.offsetHeight ; }
  catch(e) { return 1 ; }
}

Notation.prototype.update_popup = function()
{
  this.log("update") ;
  var i ;
  this.add_empty_question_if_needed() ;
  this.compute_stats() ;
  this.update_title() ;
  var question_size = get_scroll_size(this.notation_content.childNodes[0]) ;
  var comment_size = get_scroll_size(this.notation_content.childNodes[1]) ;
  var questions = [] ;
  for(i in this.questions)
    if ( this.questions[i].is_a_question_or_bonus() )
      questions.push(this.questions[i]) ;
  this.sort_questions(questions) ;
  var s = [] ;
  s.push('<div id="the_questions" class="the_questions">') ;
  s.push('<div class="the_completions" id="the_completions"></div>') ;
  for(i in questions)
      s.push(questions[i].html(this.modifiable, this.column_modifiable)) ;
  s.push('</div>') ;

  questions = [] ;
  for(i in this.questions)
    if ( this.questions[i].is_a_comment() )
      questions.push(this.questions[i]) ;
  questions.sort(function(a, b) { return a.question < b.question
				  ? -1
				  : (a.question > b.question ? 1 : 0) ; }) ;
  s.push('<div class="the_comments">') ;
  for(i in questions)
    s.push('<div tabindex="0" class="a_comment'
	   + (questions[i].grade.stored ? " selected" : "")
	   + (questions[i].priority >= 1000 ? " last_ones" : "")
	   + '" id="' + questions[i].id + '">'
	   + '<span class="stat">' + questions[i].stats.sum + '</span>'
	   + html(questions[i].question)
	   + (notation_debug ? " " + questions[i].id : "")
	   + ((questions[i].somebody_is_graded() || ! this.column_modifiable)
	      ? '' : ' <span class="edit_comment">✎</span>')
	   + '</div>') ;
  s.push('</div>') ;

  this.notation_content.innerHTML = s.join('') ;
  this.the_completions = document.getElementById("the_completions") ;
  for(i in this.questions)
    if ( this.questions[i].is_a_question_or_bonus() )
      if ( this.questions[i].is_a_question_or_bonus() )
	this.questions[i].draw_canvas() ;

  var percent = 100 * comment_size / (question_size + comment_size) ;
  percent = Math.max(percent, 7) ;
  this.notation_content.childNodes[0].style.bottom = percent + '%' ;
  this.notation_content.childNodes[1].style.top = (100 - percent) + '%' ;
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
  last_user_interaction = millisec() ;
  event = the_event(event) ;
  event.line = event.target ;
  while( ! event.line.id )
    event.line = event.line.parentNode ;
  event.question = this.questions[event.line.id] ;
  event.what = '' ;
  if ( event.line.childNodes.length == 5 )
    {
      // On a question line
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
    }
  else
    {
      event.child_nr = -1 ;
      if ( event.target.className == 'stat' )
	event.target = event.target.parentNode ;
    }
  return event ;
} ;

Notation.prototype.on_mouse_move = function(event, force)
{
  event = this.get_event(event) ;
  if (!force && event.what != 'canvas')
    return ;
  if ( ! event.question )
    return ;
  if ( this.button_pressed_on != event.question.id )
    return ;

  if ( event.what == 'canvas' && event.question.question !== "")
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
    if ( event.comment_input )
      event.comment_input.value = event.question.grade_and_comment() ;
  }
  event.question.draw_canvas() ;
  this.update_title() ;
} ;

Notation.prototype.on_mouse_down = function(event)
{
  this.log("on_mouse_down") ;
  event = this.get_event(event) ;
  this.stop_event = true ;

  GUI.add("notation_mouse_down", event, event.what) ;

  if ( ! event.question )
    {
      if ( event.target.className == 'a_completion' )
	{
	  if ( this.modifiable )
	    {
	      var completion = event.target.textContent ;
	      event.target = this.old_focused.childNodes[4] ;
	      event.question = this.questions[this.old_focused.id] ;
	      event.target.value = completion.replace(/^[0-9]* /, "") ;
	      event.line = this.old_focused ;
	      this.on_comment_change(event) ;
	      event.target.value = event.question.grade_and_comment() ;
	    }
	  else
	    alert(_("ERROR_value_defined_by_another_user")) ;
	}
    return ;
    }
  this.button_pressed_on = event.question.id ;
  if (event.what == 'canvas')
    event.target.focus() ;
  else
  {
    if ( ! this.column_modifiable )
      return ;
    switch(event.target.className.split(' ')[0])
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
    case 'make_comment':
      event.question.type = 3 ;
      event.line.className = event.line.className.replace(
	  /type[0-9]/, 'type3') ;
      this.update_popup() ;
      break ;
    case 'a_comment':
      if ( this.modifiable )
	event.question.toggle_comment() ;
      else
	alert(_("ERROR_value_defined_by_another_user")) ;
      break ;
    case 'edit_comment':
      var v = prompt(_("MSG_notation_edit_comment"), event.question.question) ;
      if ( v )
	{
	  event.question.question = v ;
	  if ( v === '' )
	    event.question.type = 1 ;
	  this.update_popup() ;
	}
      break ;
    }
  }
  if ( this.modifiable )
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
  GUI.add("notation_paste", event, event.what) ;
  var me = this ;
  if ( event.what == 'comment' )
    setTimeout(function() { me.on_comment_change(event) ; }, 100) ;
  else if ( event.what == 'question' )
    setTimeout(function() { me.on_question_change(event) ; }, 100) ;
} ;

Notation.prototype.compute_stats = function()
{
  this.global_comments = {} ;
  for(var question in this.questions)
    {
      this.questions[question].stats = new Stats() ;
      if ( this.questions[question].is_a_comment() )
	this.global_comments[this.questions[question].question] = 1 ;
    }
  for(var line_id in lines)
  {
    try {
      g = JSON.parse(lines[line_id][this.column.data_col].comment) ;
      for(var id in g)
      {
	var grade = new NotationGrade(g[id]) ;
	var question = this.questions[id] ;
	if(question.is_a_question() || question.is_a_bonus())
	{
	  question.stats.add(grade.stored / grade.max) ;
	  if ( this.global_comments[grade.comment] === undefined )
	    this.global_comments[grade.comment] = 0 ;
	  this.global_comments[grade.comment]++ ;
	}
	else if ( question.is_a_comment() )
	  question.stats.add(1) ;
      }
    }
    catch(e) { }
  }
  this.global_comments_sorted = [] ;
  for(var i in this.global_comments)
    this.global_comments_sorted.push(i) ;
  this.global_comments_sorted.sort() ;
  this.max_graded = 0 ;
  for(var question in this.questions)
    this.max_graded = Math.max(this.questions[question].stats.nr,
			       this.max_graded) ;
  for(var question in this.questions)
    this.questions[question].max_graded = this.max_graded ;
} ;

Notation.prototype.update_error = function(error, element)
{
  if ( error )
  {
    this.notation_error.style.color ='#F00' ;
    if ( element )
      element.style.color = this.notation_error.style.color ;
    this.notation_error.style.fontSize = "100%" ;
    this.notation_error.innerHTML = _(error) ;
  }
  else
    this.notation_error.innerHTML = '' ;
} ;

Notation.prototype.on_comment_change = function(event)
{
  this.log("on_comment_change " + event.target.value) ;
  var error = event.question.set_comment(event.target.value,
					 this.column_modifiable) ;
  this.update_error(error, event.target) ;
  event.question.draw_canvas() ;
  this.update_title() ;
  if ( event.keyCode != 8 )
  {
    var completion = this.update_completions(event) ;
    if ( completion )
    {
      do_autocompletion(event.target, event.target.value + completion) ;
      event.question.set_comment(event.target.value, this.column_modifiable) ;
    }
  }
} ;

Notation.prototype.update_completions = function(event)
{
  var current = event.question.grade.comment.toLowerCase() ;
  var completions = [] ;
  var remain ;
  for(var comment in this.global_comments_sorted)
    {
      comment = this.global_comments_sorted[comment] ;
      if ( comment.substr(0, current.length).toLowerCase() == current )
	{
	  completions.push('<div class="a_completion"><span class="stat">'
			   + this.global_comments[comment]
			   + '</span> ' + html(comment) + '</div>') ;
	  remain = comment.substr(current.length) ;
	}
    }
  this.the_completions.innerHTML = completions.join("") ;
  this.the_completions.style.top = document.getElementById("the_questions")
    .scrollTop + 'px' ;
  this.the_completions.style.left = event.line.childNodes[4].offsetLeft
    + event.line.childNodes[4].offsetWidth + "px" ;
  if ( completions.length == 1 )
    return remain ;
} ;

Notation.prototype.on_question_change = function(event)
{
  this.log("on_question_change " + event.target.value) ;
  event.question.question = event.target.value ;
  if ( this.is_the_last(event.question) && event.question.question !== '' )
    event.question.priority = this.local_priority++ ;
} ;

Notation.prototype.on_keydown = function(event)
{
  event = this.get_event(event) ;
  if ( event.keyCode == 27 // Escape
       && ! confirm(_("ALERT_notation_save")) )
    this.cancel_save = true ;

  if ( event.keyCode == 13
       || event.keyCode == 38
       || event.keyCode == 40
       || event.keyCode == 33
       || event.keyCode == 34
       || (event.keyCode == 32
	   && event.target.className.split(' ')[0] == 'a_comment'
	   )
       || ((event.keyCode == 37 || event.keyCode == 39)
	   && event.what == 'canvas')
     )
    stop_event(event) ;
} ;

Notation.prototype.on_keyup = function(event)
{
  event = this.get_event(event) ;
  this.log("keyup what=" + event.what + ' question=' + event.question.id) ;
  var questions = this.question_list() ;
  var question_index = myindex(questions, event.question) ;
  if ( event.keyCode <= 40 && event.keyCode != 37 &&  event.keyCode != 39)
    GUI.add_key(event, "notation_key") ;

  if ( event.target.className.split(' ')[0] == 'a_comment'
     && (event.keyCode == 32 || event.keyCode == 13) )
  {
    event.question.toggle_comment() ;
    return ;
  }

  switch(event.keyCode)
  {
  case 38: // Cursor up
  case 40: // Cursor down
  case 13: // Return
    if ( event.what == 'question' || event.what == 'comment' )
    {
      var s = get_selection(event.target) ;
      if ( ! this.contain_empty_question() )
	this.update_popup() ;
    }
    questions = this.question_list() ;
    this.focus(questions[question_index	+ (event.keyCode == 38 ? -1 : 1)],
	       event.child_nr) ;
    stop_event(event) ;
    break ;
  case 37: // Cursor left
  case 39: // Cursor right
    if ( event.what == 'canvas' && event.question.question !== "" )
    {
      if ( ! this.modifiable )
	break ;
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
    this.jump_from_notation = true ;
    if ( event.keyCode == 34 )
      the_current_cell.cursor_down() ;
    else
      the_current_cell.cursor_up() ;
    this.jump_from_notation = false ;
    setTimeout(function() {
      Notation.focus(event.question, event.child_nr) ; }, 100) ;
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
       && ! this.is_the_last(event.question)
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
  s = ['<div style="overflow:auto;max-height:20em"><style>',
       '.DisplayTypeNotation + .CellBottom .DisplayCellColumn,',
       '.DisplayTypeNotation + .CellBottom .DisplayCellComment',
       '{ display: none }',
       '.DisplayTypeNotation .DisplayCellValue .tipped .text',
       '{ display: block }',
       'TABLE.notation_suivi { border-spacing: 0px }',
       'TABLE.notation_suivi TD',
       '{ border: 1px solid #888 ; font-size:120%; vertical-align:top ; }',
       '</style>',
       '<table class="notation_suivi">'
      ] ;
  for(var question in questions)
    s.push(questions[question].suivi());
  s.push("</table>");
  var c = []
  for(var question in this.questions)
    {
      question = this.questions[question] ;
      if ( question.is_a_comment() && question.grade.stored )
	c.push(html(question.question));
    }
  return s.join("") + c.join('<br>') + '</div>' ;
} ;

Notation.prototype.get_question_from_question = function(question)
{
  question = question.toLowerCase() ;
  for(var j in this.questions)
    if ( this.questions[j].question.toLowerCase() == question )
      return this.questions[j] ;
} ;

Notation.prototype.import_do = function(csv)
{
  if ( csv.length < 2 )
    return "???" ;
  var question_texts = csv[0].split(/\t/) ;
  var questions = [] ;
  var column = popup_column() ;
  var messages = "" ;

  this.init(column)
  for(var i=3; i < question_texts.length; i += 2)
    {
      var question = question_texts[i+1] ;
      var max = question_texts[i].toLowerCase() ;
      var q = this.get_question_from_question(question) ;
      if ( q )
      {
	if ( isNaN(max) && max != _("MSG_Bonus").toLowerCase() )
	  return max + "=NaN && " + max + "!=" + _("MSG_Bonus") ;
	if ( q.is_a_bonus() && max != _("MSG_Bonus").toLowerCase() )
	  return q.question + ' : ' + _("MSG_Bonus") + ' ?' ;
	if ( q.is_a_question() && q.max != Number(max) )
	  return q.question + "\n" + q.max + ' != ' + max ;
      }
      else
	{
	  q = this.add_empty_question_if_needed(question, max) ;
	  messages += "\n/" + max + ' ' + question ;
	}
      questions.push(q) ;
    }
  if ( messages !== "" )
    if ( ! confirm(_("MSG_notation_confirm_import") + '\n' + messages) )
      return _("MSG_tablelinear_cancel") ;
  var g ;
  for(var i in csv)
    {
      if ( i == 0 )
	continue ;
      var grades = csv[i].split(/ *\t */) ;
      if ( grades[0] === '' || ! grades[0] )
	continue ;
      var lin_id = login_to_line_id(grades[0]) ;
      if ( ! lin_id )
	return grades[0] + ' ???' ;
      this.init_cell(lines[lin_id]) ;
      for(var j in questions)
	{
	  g = grades[3 + 2*j] ;
	  if ( g === '' )
	    continue ;
	  if ( isNaN(g) )
	    return questions[j].question + ": " + g + "=NaN" ;
	  if ( g > questions[j].max )
	    return questions[j].question + ": " + g + ">" + questions[j].max ;
	  questions[j].set_grade(g + '/' + questions[j].max) ;
	  questions[j].set_comment(grades[4 + 2*j], true) ;
	}
      this.save_grades() ;
    }
  this.save_questions() ; // Must be after
  this.update_all_grades() ;
  table_fill(true, true, true, true) ;
}

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

function notation_export()
{
  Notation.parse_questions(the_current_cell.column.comment) ;
  Notation.column = the_current_cell.column ;
  var questions = Notation.question_list() ;
  var data_col = the_current_cell.data_col ;
  var csv = [] ;
  var g ;

  t = [_("COL_TITLE_ID"), _("COL_TITLE_surname"), _("COL_TITLE_firstname")] ;
  for(var question in questions)
  {
    question = questions[question] ;
    if ( question.is_a_bonus() )
      t.push(_("MSG_Bonus")) ;
    else
      t.push(question.max) ;
    t.push(html(question.question)) ;
  }
  csv.push('<tr><th>' + t.join('<th>') + '</tr>\n') ;

  t = ['', '', ''] ;
  for(var question in questions)
    {
      t.push(_("B_Note")) ;
      t.push(_("TH_comment")) ;
    }
  csv.push(['<tr><th>' + t.join('<th>') + '</tr>\n']) ;

  for(var lin in filtered_lines)
  {
    line = filtered_lines[lin] ;
    t = [line[0].value, line[2].value, line[1].value] ;
    try {
      g = JSON.parse(Notation.get_the_commented_line(line)[data_col].comment) ;
    }
    catch(e) { g = undefined }
    if ( g )
    {
      for(var question in questions)
      {
	question = questions[question] ;
	if ( g[question.id] )
	{
	  var grade = new NotationGrade(g[question.id]) ;
	  t.push(trunc(grade.grade * question.max)) ;
	  t.push(html(grade.comment)) ;
	}
	else
	{
	  t.push("???") ;
	  t.push("") ;
	}
      }
      for(var question in g)
	{
	  if ( ! Notation.questions[question]
	      || ! Notation.questions[question].is_a_comment() )
	    continue ;
	  if ( g[question] && g[question].substr(0,1) != '0' )
	    t.push(Notation.questions[question].question) ;
	}
    }
    csv.push('<tr><td>' + t.join('<td>') + '</tr>\n') ;
  }
  create_popup('notation_export', _("MSG_print_popup_title"),
	      '',
	       '<style>DIV.import_export.notation_export { bottom: 3em; left: 3em; right: 3em; top: 3em ; border: 4px solid green }</style>'
	       + '<table class="colored" style="height: 20em;font-size: 50%;">'
	       + csv.join('') + '</table>',
	       false) ;
}

function notation_import_do()
{
  var error = Notation.import_do(popup_value()) ;
  if ( error )
    alert(error) ;
  else
    popup_close() ;
}

function notation_import()
{
  if ( ! column_change_allowed(this.column) )
    {
      alert(_("ERROR_value_not_modifiable")) ;
      return ;
    }
  var c = _("TH_comment").substr(0, 7) ;
  var g = _("B_Note").substr(0, 7) ;
  var example = [
    [_("COL_TITLE_ID"), _("COL_TITLE_surname"), _("COL_TITLE_firstname"),
     2, "Quest X", 2, "Quest Y", _("MSG_Bonus"), "Z"],
    ['', '', '', g, c, g, c, g, c],
    [],
    ["1160000", "", "", 2   , "Good!"  , 1, "Bien"   , 1   , "Super!"],
    ["1160001", "", "", 0.5 , "False"  , 1, "Faux"   , 0   , ""],
    ["1160002", "", "", 0.25, "Bad :-(", 0, "Mauvais", -0.5, "Spelling"]
  ] ;
  for(var i = 0 ; i < 3 && i < filtered_lines.length; i++)
    {
      example[i+3][0] = filtered_lines[i][0].value.substr(0,7) ;
      example[i+3][1] = filtered_lines[i][2].value.substr(0,4) + '…' ;
      example[i+3][2] = filtered_lines[i][1].value.substr(0,4) + '…' ;
    }
  for(var i = 0 ; i < example.length; i++)
      example[i] = example[i].join("\t") ;

  var title = _("MSG_notation_import_title") + ' «'
    + the_current_cell.column.title + '»' ;
  create_popup('import_div', title,
	       caution_message() + _("MSG_notation_import"),
	       '<button onclick="notation_import_do()">'
	       + title + '</button><p>'
	       + _("MSG_notation_import_warning"),
	       example.join('\n')) ;
}
