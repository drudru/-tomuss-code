// -*- coding: utf-8 -*-
/*
    TOMUSS: The Online Multi User Simple Spreadsheet
    Copyright (C) 2008-2013 Thierry EXCOFFIER, Universite Claude Bernard

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


/* Check of the 'type' cell in the header. */

function type_title_to_type(title)
{
  for(var v in types)
    if ( types[v].title == title )
      return types[v] ;
  // alert_append('bug type_title_to_type : ' + title);
}

/******************************************************************************
Check the 'filter' cell in the header
******************************************************************************/

/******************************************************************************   Beware : the value is [value, author, date, comment]
   The test update the information in the column object.
   It returns the new value.
******************************************************************************/

/**************** Generic filter **********************/

function compile_filter_generic_(value)
{
  var negate, val, oper, data ;
  var test, end, v, number ;

  /*
   * Negate part
   */
  value = value.replace(/ */, '') ; // Remove Spaces at the left
  if ( value.substr(0,1) == '!' )
    {
      negate = true ;
      value = value.substr(1) ;
    }
  else
    negate = false ;

  /*
   * Value part (allow white space here)
   */
  value = value.replace(/ */, '') ;
  if ( value.substr(0,1) == '#' )
    {
      val = 'value_.comment' ;
      value = value.substr(1) ;
    }
  else if ( value.substr(0,1) == '@' )
    {
      val = 'value_.author' ;
      value = value.substr(1) ;
    }
  else if ( value.substr(0,1) == ':' )
    {
      val = 'value_.history' ;
      value = value.substr(1) ;
    }
  else if ( value.substr(0,1) == '?' )
    {
      val = '(value_.date.substr(6,2)+"/"+value_.date.substr(4,2)+"/"+value_.date.substr(0,4)+"/"+value_.date.substr(8,2))' ; /* The date and hour */
      value = value.substr(1) ;
    }
  else
    val = 'value_.value' ; /* The value */

  /*
   * Operator part (do not allow white space because : '@ a' for example)
   */
  // value = value.replace(/ */, '') ;
  if ( value.substr(0,1) == '=' )
    { oper = '==' ; value = ' ' + value ; }
  else if ( value.substr(0,2) == '<=' )
    oper = '<=' ;
  else if ( value.substr(0,2) == '>=' )
    oper = '>=' ;
  else if ( value.substr(0,1) == '<' )
    oper = '<' ;
  else if ( value.substr(0,1) == '>' )
    oper = '>' ;
  else if ( value.substr(0,1) == '~' )
    oper = "~" ;
  else
    oper = "" ;
  value = value.substr(oper.length) ;

  /*
   * Constant part
   */
  // value = value.replace(/ */, '') ;
  if ( val === 'value_.value' && oper === '' )
    end = value.search(/[<>&|=!]| [<>&|=!:#?@~]| ou/) ;
  else
    end = value.search(/[ <>&|=!]/) ;
  if ( end == -1 )
    {
      data = value ;
      value = '' ;
    }
  else
    {
      data = value.substr(0, end) ;
      value = value.substr(end) ;
      value = value.replace(/ */, '') ;
    }

  /*
   * Special constant cases
   */
  if ( val === 'value_.author' && data === '' && oper === '')
    {
      data = my_identity ;
      oper = '==' ;
    }
  else if ( val === 'value_.comment' && data === '' && oper === '')
    {
      oper = '!=' ;
    }
  else if ( val.length > 20 && data === '' && oper === '')
    {
      oper = '>=' ;
      data = today.substr(6,2) + '/' + today.substr(4,2) + '/' + today.substr(0,4) ;
    }
  else if ( val == 'value_.history' && data === '' && oper === '')
    {
      oper = '!=' ;
    }

  /*
   * code generation
   */
  if ( replaceDiacritics(data) === data )
    {
      // No diacritics in data, so don't test them
      if ( value.substr(0,1) != '(' ) // Not a Date
	val = 'replaceDiacritics(' + val + '.toString())' ;
    }


  /*
   * Constant type : true: number, false:string, other: date
   */
  if ( ! isNaN(data.replace(',', '.')) )
    data = data.replace(',', '.') ;

  if ( isNaN(data) )
    {
      number = get_date(data) ;
      if ( number.reverse )
	{
	  if ( oper === '>' || oper === '>=' )
	    oper = '<' ;
	  else if ( oper === '<' || oper === '<=' )
	    oper = '>' ;
	}
    }
  else
    number = data !== '' ;


  /*
   * Create formula, depends on constant type AND operator
   */
  if ( oper === '~' || oper === '' || number === false )
    {
      dataorig = data ;
      data =  "'" + data.replace(/\\/g,"\\\\").replace(/[\']/g,"\\'").toUpperCase() + "'" ;
      number = false ;
    }

  /* Use regex to speedup process with /i option if the searched
     text does not contains dangerous symbols */

  if ( oper === '' )
    {
      if ( dataorig === '' || dataorig.search(/[^a-zA-Z0-9_-]/) != -1 )
	test = val + '.toString().toUpperCase().indexOf(' + data + ') == 0' ;
      else
	test = val + '.toString().search(/^' + dataorig + '/i) != -1' ;
    }
  else if ( oper === '~' )
    {
      if (  dataorig === '' || dataorig.search(/[^a-zA-Z0-9_-]/) != -1 )
	test = val + '.toString().toUpperCase().indexOf(' + data + ') != -1' ;
      else
	test = val + '.toString().search(/' + dataorig + '/i) != -1' ;
    }
  else
    switch(number)
      {
      case true:
	switch(oper)
	  {
	  case '<':
	  case '>':
	  case '<=':
	  case '>=':
	    test = 'a_float(' + val + ')' + oper + data ;
	    break ;
	  default:
	    test = val + oper + data ;
	    break ;
	  }
	break ;
      case false:
	test = val + '.toString().toUpperCase()' + oper + data ;
	break ;
      default:

	switch(oper)
	  {
	  case '<':
	    test = 'get_date_sup(' + val + ') < ' + number.getTime() ;
	    break ;
	  case '<=':
	    test = 'get_date_sup('+ val+ ') <= ' + number.sup.getTime() ;
	    break ;
	  case '>':
	    test = 'get_date_inf(' + val + ') > ' + number.sup.getTime() ;
	    break ;
	  case '>=':
	    test = 'get_date_inf(' + val + ') >= ' + number.getTime() ;
	    break ;
	  default:
	    break ;
	  }
      }

  if ( negate )
    test = '!(' + test + ')' ;

  if ( value !== '' )
    {
      if ( value.substr(0,1) == '&' )
	test += ' && ('
	  + compile_filter_generic_(value.substr(1)) + ')' ;
      else if ( value.substr(0,1) == '|' )
	test = '(' + test + ') || ('
	  + compile_filter_generic_(value.substr(1)) + ')' ;
      else if ( value.substr(0,2) == 'ou' )
	test = '(' + test + ') || ('
	  + compile_filter_generic_(value.substr(2)) + ')' ;
      else
	test += ' && ('
	  + compile_filter_generic_(value) + ')' ;
    }

  _d('\n' + test + '\n') ;
  return test ;
}

var tmp_index_filter = 0 ;

function compile_filter_generic(value)
{
  if ( value === '' || value === '~' )
    return function() { return true ; } ;
  tmp_index_filter++ ;

  return eval('function f' + tmp_index_filter + '(value_){return '
	      + compile_filter_generic_(value
					.replace(/\\\\/g, '\001')
					.replace(/\\[ ]/g, '\002')
					.replace(/\\[!]/g, '\003')
					.replace(/\\[~]/g, '\004')
					.replace(/\\[|]/g, '\005')
					.replace(/\\[=]/g, '\006')
					.replace(/\\[<]/g, '\007')
					.replace(/\\[>]/g, '\010')
					.replace(/\\[@]/g, '\011')
					.replace(/\\[:]/g, '\013')
					.replace(/\\[#]/g, '\014')
					.replace(/\\[?]/g, '\016')
				       )
	      .replace(/\001/g, '\\\\')
	      .replace(/\002/g, ' ')
	      .replace(/\003/g, '!')
	      .replace(/\004/g, '~')
	      .replace(/\005/g, '|')
	      .replace(/\006/g, '=')
	      .replace(/\007/g, '<')
	      .replace(/\010/g, '>')
	      .replace(/\011/g, '@')
	      .replace(/\013/g, ':')
	      .replace(/\014/g, '#')
	      .replace(/\016/g, '?')
	      + ';} ; f' + tmp_index_filter) ;
}

function set_filter_generic(value, column)
{
  column.real_filter = compile_filter_generic(value) ;
  column_update_option('filter', value) ;
  return value ;
}

function cell_select(event)
{
  event = the_event(event) ;
  stop_event(event) ;
  the_current_cell.change() ;
  _d('cell select');
  cell_goto(the_td(event), false) ;
}

function text_format(c)
{
  return c ;
}

function student_input(column)
{
  return '_cell(this,\'' + url + '/=' + ticket + '/' + year + '/' + semester
    + '/' + DisplayGrades.ue.ue + '/cell/' + column.the_id
    + '/' + DisplayGrades.ue.line_id + "','" + column.type
    + "','" + column.minmax + '\');' ;
}

function text_format_suivi()
{
  if ( cell_modifiable_on_suivi() )
  {
    return '<input class="hidden" onkeypress="if ( the_event(event).keyCode == 13 ) '
      + student_input(DisplayGrades.column)
      + '" value="'
      + (DisplayGrades.value.toString().replace("%","&#37").replace("'", "&#39;")
	 .replace('"', '&#34;'))
      + '"></input> <small style="font-size:80%">' + _("MSG_enter") + '</small>' ;
  }
  else
    return html(DisplayGrades.value.toString()).replace(/\n/g,'<br>') ;
}

function ___NAME__()
{
  types.push({title: '__NAME__',
		 default_filter: __DEFAULT_FILTER__,
		 tip_column_title: __TIP_COLUMN_TITLE__,
		 tip_filter: __TIP_FILTER__,
		 tip_cell: __TIP_CELL__,
		 cell_test: __CELL_TEST__,
		 cell_completions: __CELL_COMPLETIONS__,
		 cell_compute: __CELL_COMPUTE__,   
		 cell_is_modifiable: __CELL_IS_MODIFIABLE__,   
		 onmousedown: __ONMOUSEDOWN__,
		 formatte: __FORMATTE__,
		 formatte_suivi: __FORMATTE_SUIVI__,
                 should_be_a_float: __SHOULD_BE_A_FLOAT__,
	         type_type: __TYPE_TYPE__,
	         human_priority: __HUMAN_PRIORITY__
		 }) ;
  types[types.length-1].index = types.length - 1 ;
  return types[types.length-1] ;
}

