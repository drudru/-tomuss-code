/*
    TOMUSS: The Online Multi User Simple Spreadsheet
    Copyright (C) 2008-2012 Thierry EXCOFFIER, Universite Claude Bernard

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

    Contact: Thierry.EXCOFFIER@bat710.univ-lyon1.fr
*/

/*REDEFINE
Some table lines must not be modified.
This function return 'true' to allow the line editing.
*/
function modification_allowed_on_this_line(line_id, data_col)
{
  if ( myindex(semesters, semester) == -1 )
    return true ;
  if ( tr_classname === undefined )
    return true ;
  if ( ! popup_on_red_line )
    return true ;
  if ( lines[line_id][tr_classname].value == 'non' )
    return true ; // Returns false here to forbid red line editing
  return true ;
}

function update_student_information_default(line)
{
  if ( columns[0].type != 'Login' && columns[0].title != 'ID' )
    return ;
  var src = student_picture_url(line[0].value) ;
  if ( src != t_student_picture.src )
    {
      t_student_picture.src = '_URL_/tip.png' ;
      if ( line[0].value )
	t_student_picture.src = student_picture_url(line[0].value) ;
    }
  t_student_picture.parentNode.href = suivi + '/' + line[0].value ;
}

/*REDEFINE
  Template can redefine this function.
*/
function update_student_information(line)
{
  update_student_information_default(line) ;
}

function head_html()
{
  if ( window.location.pathname.search('=read-only=') != -1 )
    table_attr.modifiable = false ;

  if ( window.location.pathname.search('/=linear=') != -1 )
    preferences.interface = 'L' ;
  if ( preferences.interface == 'L' )
    {
      return '</head><body id="body" onunload="send_key_history()" class="tomuss"  onkeydown="dispatch2(the_event(event))" onkeypress="dispatch(the_event(event))">' +
	'<style>' +
	'ul { margin-top: 0px ; margin-bottom: 0px; }\n' +
	'@media speech { u { pause-after: 1s; } }\n' +
	'@media aural { u { pause-after: 1s; } }\n' +
	'u { pause-after: 1s; }\n' +
	'</style>' +
	'<div id="loading_bar"><div></div></div>' +
	'<div id="top"></div><input onkeydown="dispatch2(the_event(event))" onkeypress="dispatch(the_event(event))" style="width:1em"><div id="log"></div>' ;
    }

  var w ;

  if ( myindex(semesters, semester) != -1 )
    w = '<link href="' + suivi.split('/=')[0] + '/rss2/' + ue + '" rel="alternate" title="TOMUSS" type="application/rss+xml">' ;
  else
    w = '' ;

  w += '<title>' + ue + ' ' + year + ' ' + semester + ' ' + my_identity
    + '</title></head>' ;

  w += '<body id="body" class="tomuss" onunload="the_current_cell.change();store_unsaved()" onkeydown="the_current_cell.keydown(event, false)">' +
    // This message is visible in FireFox (bug ?)
    //   '<noscript>Activez JavaScript et réactualisez la page</noscript>'+
   '<div class="identity">' +
   '<p>' +
      '<a href="' + url + '/=' + ticket + '/logout">'
      + _('LABEL_logout') + '</a> <b>' + my_identity + '</b>' ;

  if ( myindex(semesters, semester) != -1 )
      w += '<a href="' + suivi.split('/=')[0] + '/rss2/' + ue + '"><img style="border:0px" src="' + url + '/feed.png"></a>' ;

 w += hidden_txt('<a href="' + url + '/=' + ticket + '/0/Preferences/'
		 + my_identity2 + '" target="_blank">' + _('LABEL_preferences')
		 + '</a>', _('TIP_preferences')) + ', '
    + hidden_txt(_('MSG_connected'), _('TIP_connection_state'), '',
		 'connection_state')
    + hidden_txt(_('MSG_updating'), _('TIP_updating'), '', 'updating')
    + '</div><div id="charsize" style="position:absolute;top:-999px">8</div>'
    + '<h1>' ;

 var semester_color = semesters_color[myindex(semesters, semester)] ;

 var options ;
 if ( semester_color )
   {
     options = "__OPTIONS__" ;
     if ( options.indexOf( year + '/' + semester) === -1 )
       options += '<option>' +  year + '/' + semester + '</option>' ;
     options = options.replace('>' + year + '/' + semester,
			       ' selected>' + year + '/' + semester) ;
     options = '<select onchange="semester_change(this);" '
       + 'style="background:' + semester_color + '">'
       + options + '</select>' ;
   }
 else
   {
     options = '<span>' + year + ' ' + semester + '</span>' ;
   }

 w += options + ' ' + ue + ' ' + table_attr.table_title + '</h1>' ;

 return w ;
}

function semester_change(t)
{
  t.blur() ;
  window.open(url + '/=' + ticket + '/'
	      + t.childNodes[t.selectedIndex].innerHTML + '/' + ue) ;
  for(var i=0;i<t.childNodes.length;i++)
      if ( t.childNodes[i].innerHTML == year + '/' + semester )
	  {
	      t.selectedIndex = i ;
	      break ;
	  }
}


function one_line(text, tip)
{
  return '<div class="one_line">' + hidden_txt(text, tip) + '</div>' ;
}

function column_attr_set(column, attr, value, td, force_save)
{
  var old_value = column[attr] ;
  var i_can_modify_column = column_change_allowed(column) ;

  if ( !i_can_modify_column && i_am_the_teacher && attr == 'width' )
      i_can_modify_column = true ;

  if ( old_value == value )
    {
	if ( !i_can_modify_column )
	    return ;
      // Save the value even if the value is unmodified
      if ( attr != 'width' && attr != 'position' )
	return ;
    }

  if ( column_attributes[attr].need_authorization && ! i_can_modify_column )
    {
      if ( column.author == '*' )
	  alert_append(_("ERROR_value_not_modifiable") + '\n'
		       + _("ERROR_value_system_defined")) ;
      else
	  alert_append(_("ERROR_value_not_modifiable") + '\n'
		       + _("ERROR_value_defined_by_another_user") + teachers) ;
      return ;
    }

  if ( column.is_empty && column.data_col > 0
       && ( columns_filter_value || full_filter) )
    {
	alert_append(_('ERROR_column_creation')) ;
	return ;
    }
  if ( column.is_empty && column.data_col > 0
       && columns[column.data_col-1].is_empty )
      alert_append(_("ERROR_column_left_to_right")) ;

  var new_value = column_parse_attr(attr, value, column, td === undefined) ;

  if ( old_value === new_value && attr != 'width' && attr != 'position' )
    return ;

  if ( column_attributes[attr].empty(column, old_value) && new_value == '')
    return ; // The value stays empty...

  if ( new_value === null )
    return null ; // Do not store, but leave unchanged in user interface

  if ( create_column(column) && attr == 'title' )
    return new_value ; // The title is yet sended to the server

  column[attr] = new_value ;

  if ( i_can_modify_column
       && ( ! column_attributes[attr].action || force_save ) )
    {
      append_image(td, 'column_attr_' + attr + '/' + column.the_id + '/' +
		   encode_uri(new_value)) ;
      if ( column.author != my_identity )
	{
	  column.author = my_identity ;
	  the_current_cell.do_update_column_headers = true ;
	}
    }

  return new_value ;
}

function table_change_allowed()
{
  return i_am_the_teacher || !table_attr.masters[0] ;
}


function table_attr_set(attr, value, td)
{
  var old_value = table_attr[attr] ;

  if ( old_value == value )
    return  ;

  if ( ! table_attributes[attr].action && ! table_change_allowed()
       && ! i_am_root )
    {
      alert_append(_("ERROR_value_not_modifiable") + '\n'
		   + _("ERROR_value_defined_by_another_user") + teachers) ;
      return ;
    }

  value = table_attributes[attr].formatter(value) ;

  if ( old_value == value )
    return  ;

  if ( value === undefined )
    return old_value ;

  table_attr[attr] = value ;

  if ( ! table_attributes[attr].action )
    append_image(td, 'table_attr_' + attr + '/' + encode_uri(value),
		 attr == 'modifiable') ;

  return value ;
}

function attr_update_user_interface(attr, column, force_update_header)
{
  if ( column.need_update )
    {
      update_columns() ;
      update_histogram(true) ;
    }
  if ( attr.display_table || column.need_update )
    table_fill(true, false, true) ;
  if ( attr.update_horizontal_scrollbar )
    update_horizontal_scrollbar() ;

  //  the_current_cell.update_headers() ;

  if ( (force_update_header || attr.update_headers)
       && column == the_current_cell.column )
    {
      the_current_cell.do_update_column_headers = true ;
      the_current_cell.update_headers() ;
    }
  if ( attr.what == 'table' )
    the_current_cell.update_table_headers();

  if ( attr.update_table_headers )
    table_header_fill() ;
}

function an_user_update(event, input, column, attr)
{
  var td = the_td(event) ;
  var new_value ;

  if ( input.selectedIndex !== undefined )
    {
      new_value = input.options[input.selectedIndex].value ;
      input.selectedText = input.options[input.selectedIndex].text ;
    }
  else
    new_value = input.value.replace(/\t/g, ' ') ;

  if ( attr.what == 'column' )
    new_value = column_attr_set(column, attr.name, new_value, td) ;
  else
    new_value = table_attr_set(attr.name, new_value, td) ;

  if ( new_value === undefined )
    {
      // The value can't be modified, it must be resetted to old value
      if ( input.selectedIndex === undefined )
      {
	if ( input.value != input.theoldvalue )
	  input.value = input.theoldvalue ;
      }
      else
	input.selectedIndex = input.theoldvalue ;
      return ;
    }

  if ( new_value === null )
    return ; // Not stored, but leave user input unchanged
  if ( input.selectedIndex === undefined )
    if ( attr.what == 'column' )
      input.value = attr.formatter(column, new_value) ;
    else
      input.value = attr.formatter(new_value) ;
  else
    attr.formatter(column, new_value) ;
  input.theoldvalue = new_value ;

  if ( attr == 'type' )
    init_column(column) ; // Need to update other attributes.

  attr_update_user_interface(attr, column) ;
  compute_tip(input);
}

function filter_change_column(value, column)
{
    column.filter = set_filter_generic(value, column) ;
    update_filters() ;
    update_histogram(true) ;
    table_fill(true, false, true) ;
}

function header_change_on_update(event, input, what)
{
  var column = the_current_cell.column ;

  if ( what.match(/^column_attr_/) )
    an_user_update(event, input, column,
		   column_attributes[what.replace('column_attr_','')]) ;
  else if ( what.match(/^table_attr_/) )
    an_user_update(event, input, column,
		   table_attributes[what.replace('table_attr_','')]) ;
  else
    {
      // Input in the TABLE
      switch(input.parentNode.parentNode.className)
	{
	case 'filter':
	    filter_change_column(input.value, column) 
	  break ;
	}
    }
}

/*
  The definition of an input that dispatch update correctly
  and return focus in the table on key up/down/return
*/

function header_input_focus(e)
{
  if ( e.tomuss_editable === false )
    {
      e.blur() ;
      return ;
    }
  e.className = '' ; // Remove 'empty' class
  element_focused = e ;

  // To resize the INPUT tag if it is larger than the tab.
  // For example: the Table Dates
  var x = e.offsetLeft ;
  var width = e.parentNode.parentNode.parentNode.offsetWidth ;
  var margin = 5 ;
  if ( x + e.offsetWidth > width + 1 )
    {
      e.style.width = '' + (width - x - margin) + 'px' ;
    }
}

function header_input(the_id, the_header_name, options)
{
  var classe='', onkey='', before='', after='' ;
  // Don't call onblur twice (IE bug) : so no blur if not focused
  var onblur='if(element_focused===undefined)return;element_focused=undefined;';

  if ( options && (!options.search || options.search('"') != -1) )
    alert('BUG : header_input parameter: ' + the_id + ' ' + options) ;

  if ( the_header_name !== '' )
    {
      onblur += "header_change_on_update(event,this,'"+the_header_name + "');";
    }

  if ( options && options.search('empty') != -1 )
    {
      onblur += "if ( this.value === '') this.className = 'empty';" ;
      classe = 'empty' ;
    }
  if ( options && options.search('onblur=') != -1 )
    onblur += options.split('onblur=')[1].split(' ')[0] + ';' ;
  if ( options && options.search('onkey=') != -1 )
    onkey = options.split('onkey=')[1].split(' ')[0] ;
  if ( options && options.search('before=') != -1 )
    before = options.split('before=')[1].split(' ')[0] ;
  if ( options && options.search('beforeclass=') != -1 )
    before = '<span class="' + options.split('beforeclass=')[1].split(' ')[0]
      + '">' + before + '</span>' ;
  if ( options && options.search('after=') != -1 )
    after = options.split('after=')[1].split(' ')[0] ;
  if ( options && options.search('one_line') != -1 )
    {
      before = '<div class="one_line">' + before ;
      after += '</div>' ;
    }

  return before+'<input style="margin-top:0px" type="text" id="' + the_id + '" class="' + classe
    + '" onfocus="header_input_focus(this)" onblur="' + onblur
    + '" onkeyup="' + onkey  +'">' + after ;
}

function an_input_attribute(attr, options, prefix_id, prefix_)
{
  var tip = _('TIP_' + prefix_ + attr.name) ;
  if ( tip === 'TIP_' + prefix_ + attr.name )
    tip = '' ;
  if ( i_am_root )
    tip += '<hr><b>' + prefix_ + attr.name + '</b>' ;
  var the_id = prefix_id + attr.name ;
  var title = _('TITLE_' + prefix_ + attr.name) ;

  switch(attr.gui_display)
    {
    case 'GUI_input':
      return hidden_txt(header_input(the_id, prefix_ + attr.name,options),tip);
    case 'GUI_a':
      return hidden_txt('<a href="javascript:'
			+ attr.action + '(\'' + the_id + '\')"' +
			' id="' + the_id + '">' +
			title + '</a>', tip) ;
    case 'GUI_none':
      return title ;
    case 'GUI_type':
    case 'GUI_button':
      return hidden_txt('<button class="gui_button" id="'
			+ the_id + '" '
			+ 'onclick="' + attr.action + '(this);'
			+ 'setTimeout(\'linefilter.focus()\',100)"'
			+ '>' + title + '</button>',
			tip) ;
    case 'GUI_select':
      var opts = '' ;
      for(var i in options)
	opts += '<OPTION VALUE="' + options[i][0] + '">'
	  + _(options[i][1]) + '</OPTION>' ;
      
      return hidden_txt('<select style="margin:0px" onfocus="take_focus(this);" id="'
			+ the_id + '" onChange="this.blur();'
                        + "header_change_on_update(event,this,'" +
			prefix_ + attr.name + "');"
			+ attr.action + '(this)"'
                        + ' onblur="if(element_focused===undefined)return;element_focused=undefined;">'
                        + opts + '</select>',
			tip) ;
    default:
      alert('BUG gui_display') ;
    }
}

function column_input_attr(attr, options)
{
  return an_input_attribute(column_attributes[attr], options,
			    "t_column_", "column_attr_") ;
}

function table_input_attr(attr, options)
{
  return an_input_attribute(table_attributes[attr], options,
			    "t_table_attr_", "table_attr_") ;
}

/* tabbed view */

function create_tabs(name, tabs, more)
{
  if ( more === undefined )
    more = '' ;

  var s = ['<div class="tabs" id="' + name + '"><div class="titles">'] ;
  for(var i in tabs)
     s.push('<span id="title_' + tabs[i][0] + '" onclick="select_tab(\'' + name + "','" +
            tabs[i][0] + '\');">' + tabs[i][0]
             + '</span>') ;
  s.push(more + '</div><div class="contents">') ;
  for(var i in tabs)
     s.push('<div class="content" id="title_' + tabs[i][0] + '">'
             + tabs[i][1] + '</div>') ;
  s.push('</div></div>') ;

  return s.join('') ;
}

function select_tab(name, tab)
{
  var tabs = document.getElementById(name) ;
  if ( ! tabs )
    return ;
  for(var child = tabs.childNodes[1].firstChild;child;child=child.nextSibling)
     if ( child.id != 'title_' + tab )
         child.style.display = 'none' ;
     else
         child.style.display = '' ;

  for(var child = tabs.childNodes[0].firstChild;child;child=child.nextSibling)
        if ( child.id != 'title_' + tab )
            child.className = '' ;
        else
            child.className = 'tab_selected' ;
}

function selected_tab(name)
{
  var tabs = document.getElementById(name) ;
  if ( ! tabs )
    return ;
  for(var child = tabs.childNodes[0].firstChild;child;child=child.nextSibling)
        if ( child.className == 'tab_selected' )
	    return child.id.substr(6) ;
}

function new_new_interface()
{
  var o, t ;

  var doc_link = '<div class="one_line">' +
    hidden_txt('<a href="_URL_/doc_table.html" target="_blank">' +
	       _("LABEL_documentation") + '</a>',  _("TIP_documentation"))
      + '</div>' ;


  // CELLULE / Cellule

  t = ['<table class="cell"><tr><td>'] ;
  t.push(hidden_txt('<a href="" target="_blank">' +
		    '<img id="t_student_picture" class="phot"></a>',
		    _("TIP_cell_attr_student_picture"))) ;
  t.push('</td><td class="cell_values">') ;
  t.push(one_line('<span id="t_student_surname"></span>',
		  _("TIP_cell_attr_student_surname"))) ;
  t.push(one_line('<span id="t_student_firstname"></span>',
		  _("TIP_cell_attr_student_firstname"))) ;
  t.push(one_line('<span id="t_value"></span>', _("TIP_cell_value"))) ;
  t.push(hidden_txt(header_input
		    ('comment', '',
		     'empty one_line onblur=comment_on_change(event)'),
		    "<span class=\"shortcut\">(Alt-/)</span>"
		    + _("TIP_cell_comment"))) ;
  t.push(hidden_txt(header_input('linefilter', '',
				 'empty one_line onkey=line_filter_change(this)'),
		    "<span class=\"shortcut\">(Alt-8)</span>" +
		    _("TIP_cell_filter"))) ;
  t.push(hidden_txt('<span id="t_student_id" style="display:none"></span>',
		    _("TIP_cell_student_number"))) ;
  t.push('</td></tr></table>') ;
  o = [[_('TAB_cell'), t.join('\n')]] ;

  // CELLULE / Historique

  t = [] ;
  t.push(hidden_txt('<div id="t_history"></div>', _("TIP_cell_history"))) ;
  o.push([_('TAB_history'), t.join('\n')]) ;
		 
  // CELLULE / ?

  t = [] ;
  t.push(doc_link) ;
  t.push('<div class="one_line">') ;
  t.push(hidden_txt(_("LABEL_styles"), _("TIP_styles"))) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(hidden_txt('&nbsp;<img class="server"> ',
		    _("TIP_square") + _("TIP_orange_square"))) ;
  t.push(hidden_txt('&nbsp;<img class="server" src="_URL_/ok.png"> ',
		    _("TIP_square") + _("TIP_green_square"))) ;
  t.push(hidden_txt('&nbsp;<img class="server" src="_URL_/bad.png"> ',
		    _("TIP_square") + _("TIP_red_square"))) ;
  t.push(hidden_txt('&nbsp;<img class="server" src="_URL_/bug.png">',
		    _("TIP_square") + _("TIP_violet_square"))) ;
  t.push(hidden_txt(_("LABEL_square"), _("TIP_LABEL_square"))) ;
  t.push('</div>') ;
  
  t.push('<div class="one_line">') ;
  t.push(hidden_txt(_("LABEL_ALT8"), _("TIP_ALT8"))) ;
  t.push('</div>')
  t.push('<div class="one_line">') ;
  t.push(hidden_txt(_("LABEL_ALT1"), _("TIP_ALT1"))) ;
  t.push('</div>') ;
  o.push([_('TAB_?'), t.join('\n')]) ;

  // CELLULE

  var w = [] ;

  w.push('<table id="menutop" class="tabbed_headers"><tr><td class="tabbed_headers">') ;
  w.push(create_tabs('cellule', o,
		     '<a id="autosavelog" href="#" onclick="table_autosave_toggle()">'
		     + _("LABEL_save") +'</a>' +
		     '<a id="tablemodifiableFB" href="#" onclick="select_tab(\'table\', \''
		     + _("TAB_parametrage") + '\')">'
		     + _("LABEL_table_ro") + '</a>' +
		     '<span style="border:0px" id="server_feedback"></span>' +
		     '<var style="border:0px;white-space:nowrap" id="log"></var>')) ;

  // COLUMN / Column

  t = [] ;
  t.push(column_input_attr('title', 'one_line')) ;

  var options = [] ;
  for(var type_i in types)
    options.push([types[type_i].title, 'B_' + types[type_i].title]) ;
  t.push('<div class="one_line">') ;
  t.push(column_input_attr('type', options)) ;
  t.push(column_input_attr('completion')) ;
  t.push(column_input_attr('enumeration')) ;
  t.push(column_input_attr('test_filter')) ;
  t.push(column_input_attr('minmax')) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push('<table id="t_column_stats"></table>') ;
  t.push('</div>') ;
  t.push(column_input_attr('comment', 'empty one_line')) ;
  t.push(hidden_txt(header_input
		    ("columns_filter",'',
		     'empty one_line onkey=columns_filter_change(this)'),
		    _("TIP_column_filter"))) ;
  o = [[_("TAB_column"), t.join('\n')]] ;

  // COLUMN / Formula

  t = [] ;
  t.push('<div class="one_line">') ;
  t.push(column_input_attr('empty_is',
			   'before=' + _("BEFORE_column_attr_empty_is")
			   + ' beforeclass=widthleft')) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(column_input_attr('columns', 'before='+_("BEFORE_column_attr_columns")
			   + ' beforeclass=widthleft')) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(column_input_attr('best', 'before=' + _("BEFORE_column_attr_remove")
			   + ' after=' + _("BEFORE_column_attr_best")
			   + ' beforeclass=widthleft')) ;
  t.push(column_input_attr('worst','after='+_("BEFORE_column_attr_worst") )) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(column_input_attr('rounding',
			   'before=' + _("BEFORE_column_attr_rounding")
			   + ' beforeclass=widthleft')) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(column_input_attr('weight', 'before=' +_("BEFORE_column_attr_weight")
			   + ' beforeclass=widthleft')) ;
  t.push('&nbsp;&nbsp;') ;
  t.push(column_input_attr('repetition','before='
			   + _("BEFORE_column_attr_repetition")
			   + '&nbsp;'));
  t.push('</div>') ;

  o.push([_("TAB_formula"), t.join('\n')]) ;

  // COLUMN / Display

  var x = "<br>" + _("TIP_not_visible_by_others") ;

  t = [] ;
  t.push('<div class="one_line">') ;
  t.push(column_input_attr('visibility_date',
			   'before=' + _("BEFORE_column_attr_visibility_date")
			   + ' beforeclass=widthleft')) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(column_input_attr('red', 'before=' + _("BEFORE_column_attr_red")
			   + ' beforeclass=widthleft')) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(column_input_attr('green', 'before=' + _("BEFORE_column_attr_green")
			   + ' beforeclass=widthleft')) ;
  t.push('</div>') ;
  t.push('<div class="one_line" style="text-align:center">') ;
  t.push(hidden_txt('<img src="' + url + '/prev.gif" style="height:1em" onclick="do_move_column_left();">',
		    _("TIP_column_move_left") + x)) ;
  t.push(column_input_attr('position')) ;
  t.push(hidden_txt('<img src="' + url + '/next.gif" style="height:1em" onclick="do_move_column_right();">',
		    _("TIP_column_move_right") + x)) ;
  t.push('&nbsp;') ;
  /*
  t.push('</div>') ;
  t.push('<div class="one_line" style="text-align:center">') ;
  */
  t.push(hidden_txt('<a href="javascript:smaller_column();"><img src="' + url + '/next.gif" style="height:1em;border:0"><img src="' + url + '/prev.gif" style="height:1em;border:0"></a>',
		    _("TIP_column_thinner") + x)) ;
  t.push(column_input_attr('width')) ;
  t.push(hidden_txt('<a href="javascript:bigger_column();"><img src="' + url + '/prev.gif" style="height:1em;border:0"><img src="' + url + '/next.gif" style="height:1em;border:0"></a>',
		    _("TIP_column_larger") + x)) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(column_input_attr('freezed')) ;
  t.push('. ') ;
  t.push(column_input_attr('hidden')) ;
  t.push('</div>') ;

  o.push([_("TAB_display"), t.join('\n')]) ;

  // COLUMN / Parameters

  t = [] ;
  t.push('<div class="one_line">') ;
  t.push(column_input_attr('course_dates',
			   'before=' + _("BEFORE_column_attr_course_dates")
			   + ' beforeclass=widthleft')) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(column_input_attr('url_base',
			   'before=' + _("BEFORE_column_attr_url_base")
			   + ' beforeclass=widthleft')) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(column_input_attr('url_title',
			   'before=' + _("BEFORE_column_attr_url_title")
			   + ' beforeclass=widthleft')) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(column_input_attr('url_import',
			   'before=' + _("BEFORE_column_attr_url_import")
			   + ' beforeclass=widthleft')) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(column_input_attr('locked',
			   [
			    [0, _("SELECT_column_locked_no")],
			    [1, _("SELECT_column_locked_yes")],
			   ]
			   )) ;
  t.push(column_input_attr('modifiable',
			   [[0, _("SELECT_column_modifiable_by_nobody")],
			    [1, _("SELECT_column_modifiable_by_teachers")],
			    [2, _("SELECT_column_modifiable_by_students")],
			   ])) ;
  t.push('</div>') ;


  o.push([_("TAB_column_param"), t.join('\n')]) ;

  // COLUMN / Action

  t = [] ;
  t.push('<div class="one_line">') ;
  t.push(column_input_attr('export')) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(column_input_attr('import')) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(column_input_attr('fill')) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(column_input_attr('delete')) ;
  t.push('</div>') ;
  t.push(one_line(_("LABEL_column_attr_author")
		  + '<span id="t_column_author"></span>',
		  _("TIP_column_attr_author"))) ;

  o.push([_("TAB_column_action"), t.join('\n')]) ;

  // COLUMN / Help

  t = [] ;
  t.push(doc_link) ;
  t.push('<div class="one_line">') ;
  t.push(hidden_txt(_("LABEL_help_autosave"), _("TIP_help_autosave"))) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(hidden_txt(_("LABEL_help_visibility"), _("TIP_help_visibility"))) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(hidden_txt('<a target="_blank" href="_URL_/doc_table.html#Calcul de moyenne">' +
		    _("LABEL_help_average"), _("TIP_help_average"))) ;
  t.push('</div>') ;

  o.push([_("TAB_?"), t.join('\n')]) ;

  // COLUMN

  w.push('</td><td class="tabbed_headers">') ;
  w.push( create_tabs('column', o) ) ;


  // Table / Table

  t = [] ;
 
  t.push('<div class="one_line">') ;
  t.push(hidden_txt('<span id="nr_filtered_lines"></span> ' +
		    _("LABEL_nr_filtered_lines") + ' ',
		    _("TIP_nr_filtered_lines"))) ;

  t.push(hidden_txt('<span id="nr_not_empty_lines"></span>',
		    _("TIP_nr_not_empty_lines"))) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(table_input_attr('nr_lines').replace('</select>', '</select> ' +
					      _("LABEL_select_nr_lines"))+', ');
  t.push(table_input_attr('nr_columns').replace('</select>', '</select> ' +
						_("LABEL_select_nr_cols"))) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(table_input_attr('facebook')) ;
  t.push(table_input_attr('print')) ;
  t.push(table_input_attr('abj')) ;
  t.push(table_input_attr('mail')) ;
  t.push(table_input_attr('statistics')) ;
  t.push('</div>') ;

  t.push(table_input_attr("comment", 'empty one_line')) ;

  t.push(hidden_txt(header_input('fullfilter', '',
				 'empty one_line onkey=full_filter_change(this)'),
		    _("TIP_table_filter"))) ;

  o = [[_("TAB_table"), t.join('\n')]] ;

  // Table / Paramétrage

  t = [] ;
  
  t.push('<div class="one_line">') ;
  t.push(table_input_attr('default_nr_columns',
			  'before='+_("BEFORE_table_attr_default_nr_columns")));
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(_("BEFORE_table_attr_private") +
	 table_input_attr('private', [[0,_("SELECT_table_private_public")],
				      [1,_("SELECT_table_private_private")]]));
  t.push(" " +
	 table_input_attr('modifiable',
			  [[0,_("SELECT_table_modifiable_false")],
			   [1,_("SELECT_table_modifiable_true")]])) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;

  if ( myindex(semesters, semester) != -1 )
      t.push(_("BEFORE_table_official_ue") +
	   table_input_attr('official_ue',
			    [[0, _("SELECT_table_official_ue_false")],
			     [1, _("SELECT_table_official_ue_true")]])) ;
  else
    t.push('&nbsp;') ;

  if ( table_attr.group && myindex(table_attr.masters, my_identity) != -1 )
      t.push(table_input_attr('group')) ;

  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(table_input_attr('dates', 'empty before=' + _("BEFORE_table_dates"))) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(table_input_attr('masters','empty before='
			  + _("BEFORE_table_masters"))) ;
  t.push('</div>') ;

  o.push([_("TAB_parameters"), t.join('\n')]) ;

  // Table / Action

  t = [] ;

  t.push('<div class="one_line">') ;
  t.push(table_input_attr('t_export')) ;
  t.push('/') ;
  t.push(table_input_attr('t_import')) ;
  t.push(' ' + _("LABEL_columns_definitions")) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(table_input_attr('t_copy')) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(table_input_attr('autosave')) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(table_input_attr('bookmark')) ;
  t.push('</div>') ;
  t.push('<div class="one_line">') ;
  t.push(table_input_attr('linear')) ;
  t.push('.') ;
  t.push(table_input_attr('forms')) ;
  t.push('.') ;

  t.push(table_input_attr('update_content')) ;
  t.push(hidden_txt('<a href="javascript:change_popup_on_red_line()">.</a>',
		    _("TIP_popup_on_red_line")
		    ,'','popup_on_red_line')) ;
  t.push('</div>') ;

  o.push([_("TAB_table_action"), t.join('\n')]) ;

  // Table / Info

  t = [] ;
  table_info.sort() ; // A table of [Priority, Function generating the HTML]
  for(var i in table_info)
  {
    var v = table_info[i][1]() ;
    if (v)
      t.push('<div class="one_line">' + v + '</div>') ;
  }

  o.push([_("TAB_table_info"), t.join('\n')]) ;

  // Table / Help

  o.push([_('TAB_?'),
	  '<div class="scroll_auto">'
	  + doc_link + _("LABEL_table_help")
	  ]) ;

  w.push('</td><td class="tabbed_headers">') ;
  w.push( create_tabs('table', o) ) ;

  w.push('</td></tr></table>') ;
  w.push('<script>select_tab("cellule", "' + _("TAB_cell") + '");</script>') ;
  w.push('<script>select_tab("column", "' + _("TAB_column") + '");</script>') ;
  w.push('<script>select_tab("table", "' + _("TAB_table") + '");</script>') ;

  return w.join('\n') ;
}

var popup_old_values = {} ;

function popup_close()
{
  element_focused = undefined ;
  var e = document.getElementById('popup_id') ;
  if ( e )
    {
      if ( e.getElementsByTagName('TEXTAREA')[0] )
	popup_old_values[e.className] = e.getElementsByTagName('TEXTAREA'
							       )[0].value ;
      e.parentNode.removeChild(e);
    }
}

function parse_lines(text)
{
  text = text.replace(/\r\n/g, '\n').replace(/\n\r/g, '\n').
              replace(/\r/g, '\n').replace(/ *\n */g, "\n").
              replace(/ *$/g, "").split('\n') ;

  while ( text.length > 1 && text.length && text[text.length-1] === '' )
    text.pop() ;

  return text ;
}

function popup_text_area()
{
  return document.getElementById('popup_id').getElementsByTagName('TEXTAREA')[0] ;
}

function popup_value()
{
  return parse_lines(popup_text_area().value) ;
}

function popup_set_value(value)
{
  var text_area = popup_text_area() ;
  text_area.value = value ;
  text_area.focus() ;
  text_area.select() ;
}

function popup_get_element()
{
  var popup = document.getElementById('popup') ;
  if ( ! popup )
    {
      popup = document.createElement('div') ;
      popup.id = 'popup' ;
      document.getElementsByTagName('BODY')[0].appendChild(popup) ;
    }
  return popup ;
}

function popup_is_open()
{
  return !! document.getElementById('popup_id') ;
}

function popup_column()
{
  return popup_get_element().column ;
}

function create_popup(html_class, title, before, after, default_answer)
{
  popup_close() ;
  hide_the_tip_real() ;

  var new_value ;

  if ( default_answer )
    {
      new_value = popup_old_values['import_export ' + html_class] ;
      if ( new_value === undefined )
	new_value = default_answer ;
      new_value = html(new_value) ;
    }
  else
    new_value = '' ;

  var s = '<div id="popup_id" class="import_export ' + html_class
           + '"><h2>' + title + '</h2>' + before ;
  if ( default_answer !== false )
    s += '<TEXTAREA WRAP="off" ROWS="10" class="popup_input" onfocus="element_focused=this;">'+ new_value + '</TEXTAREA>' ;

  s += '<BUTTON class="close" OnClick="popup_close()">&times;</BUTTON>'+after ;

  var popup = popup_get_element() ;
  popup.innerHTML = s ;
  if ( the_current_cell )
    popup.column = the_current_cell.column ;

  if ( default_answer !== false )
    popup.getElementsByTagName('TEXTAREA')[0].focus() ;
}



function tail_html()
{
  if ( preferences.interface == 'L' )
    return '<span id="server_feedback"></span><div id="authenticate"></div>';

  var a ;

  if ( false )
    {
    a = '<p class="copyright"><span id="server_feedback"></span></p>'
        + '<div id="log"></div>' ;
    }
  else
    a = '<p class="copyright"></p>';

  a += "<div id=\"saving\">" + _("MESSAGE_data_begin_sent") + "</div>" +
    '<div id="authenticate"></div>' +
    '<div id="current_input_div">' +
    '<input id="current_input" ' +
    'ondblclick="the_current_cell.toggle();" ' +
    'OnKeyDown="the_current_cell.keydown(event, true)" ' +
    'OnFocus="the_current_cell.focused=true;the_current_cell.input_div_focus()" ' +
    'OnBlur="the_current_cell.focused=false;the_current_cell.change()" ' +
    '>' +
    '</div>' ;
  if ( ue != 'VIRTUALUE' )
    {
        if ( navigator.appName == 'Microsoft Internet Explorer' )
	    window.XMLHttpRequest = false ;
	if ( window.XMLHttpRequest )
	    a += '<div id="server_answer" style="width:1px;height:1px;border:0px;position:absolute;top:0px;left:0px"></div>' ;
	else
	    a += '<iframe id="server_answer" style="width:1px;height:1px;border:0px;position:absolute;top:0px;left:0px" src="' + url + '/sort_up.png"></iframe>' ;
	a += '</body>' ;
    }
  return a ;
}

function insert_middle()
{
  if ( preferences.interface == 'L' )
    {
      return ;
    }
  i_am_root = myindex(root, my_identity) != -1 ;

  document.write(new_new_interface()) ;

/* onmouseout is here because it must contains the tip
    If you change the content, read 'table_init' in 'lib.js'
*/
  
  var hs = '<div class="horizontal_scrollbar"><img src="' + url
    + '/prev.gif" onclick="javascript:previous_page_horizontal();">'
    + '<div id="horizontal_scrollbar"></div><img src="' + url
    + '/next.gif" onclick="javascript:next_page_horizontal();"></div>' +
    '<div>' ;
  var w ;

  if ( true )
    w = '' ;
  else
    w = hs ;
  
  if ( ! scrollbar_right )
    w += '<div id="vertical_scrollbar"></div>' ;
  w += '<div id="divtable" class="colored"><div id="hover"></div></div>' ;
  if ( scrollbar_right )
    w += '<div id="vertical_scrollbar"></div>' ;
  if ( true )
    w += hs ;

  w += '</div></div><div id="loading_bar"><div></div></div>' ;
  document.write(w) ;
}


