// -*- coding: utf-8 -*-
/*
    TOMUSS: The Online Multi User Simple Spreadsheet
    Copyright (C) 2008-2011 Thierry EXCOFFIER, Universite Claude Bernard

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

/*
 * Set the column title and change formula if necessary.
 * Returns the new title.
 */

function set_title(value, column, xcolumn_attr)
{
  value = value.replace(/ /g, '_') ;

  for(var data_col in columns)
    if ( data_col != column.data_col
	 && column.data_col // For display_suivi()
	 && !xcolumn_attr
	 && columns[data_col].title == value )
      {
	return set_title(value + '_bis', column, xcolumn_attr) ;
      }

  // XXX does not replace multiple occurrence because
  // Regex can not be used easely with special characters
  // that may appear in titles.

  if ( ! xcolumn_attr && column.title !== '' )
    {
      var job_to_do = [] ;

      for(var data_col in columns)
	{
	  var formula_column = columns[data_col] ;
	  var w = (' ' + formula_column.columns + ' ')
	    .replace(' ' + column.title + ' ',
		     ' ' + value + ' ') ;
	  w = w.substr(1, w.length-2) ; // Remove appended space
	  
	  if ( w == formula_column.columns )
	    continue ;
	  if ( ! column_change_allowed(formula_column) )
	    {
	      alert_append("Cette colonne est utilisée dans une formule qui ne peut être mise à jour car vous n'avez pas le droit.\nLe changement de ce titre est donc interdit.\nSeul le responsable de la table peut faire ce changement.") ;
	      return column.title ;
	    }
	  job_to_do.push([formula_column, 'columns', w]) ;
	}
      // Title change is possible
      for(var i in job_to_do)
	column_attr_set(job_to_do[i][0], job_to_do[i][1], job_to_do[i][2]) ;
    }
  column.title = value ;
  return column.title ;
}

/* Check of the 'type' cell in the header. */

function type_title_to_type(title)
{
  for(var v in types)
    if ( types[v].title == title )
      return types[v] ;
  // alert_append('bug type_title_to_type : ' + title);
}

function set_type(value, column)
{
  var checked = type_title_to_type(value) ;

  if ( column.real_type
       && column.real_type.cell_compute !== undefined
       && checked.cell_compute === undefined
       && lines[0][column.data_col]._save !== undefined
       )
	{
	  // Restore uncomputed values. XXX some may missing if never in client
	  for(var line in lines)
	    lines[line][column.data_col].restore() ;
	  table_fill(false, false, true) ;
	}
  if ( column.real_type
       && column.real_type.cell_compute === undefined
       && checked.cell_compute !== undefined )
    {
      /* Save values */
      for(var line in lines)
	lines[line][column.data_col].save() ;
    }

  column.real_type = checked ;
  column.need_update = true ;

  return value ;
}

function set_empty_is(value, column)
{
  column.need_update = true ;
  return value ;
}

function returns_false()
{
  return false ;
}

function unmodifiable(value, column)
{
  // It was "return '' ;" before the 2010-09-13
  // It was modified in order to make the 'import_columns' function work.
  return value ;
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
	      + compile_filter_generic_(value) + ';} ; f' + tmp_index_filter) ;
}

function set_filter_generic(value, column)
{
  column.real_filter = compile_filter_generic(value) ;
  return value ;
}

function test_nothing(value, column)
{
  return value ;
}

function test_float(value, column)
{
  return Number(value) ;
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

function set_visibility_date(value, column, interactive_modification)
{
  if ( value === '')
    return value ;
  v = get_date(value) ;
  if ( v == false )
    {
      alert_append("La date que vous donnez n'est pas valide : " + value) ;
      return column.visibility_date ;
    }
  if ( (v.getTime() - millisec())/(86400*1000) > 31 )
    {
      alert_append("La date de visibilité doit être dans moins d'un mois") ;
      return column.visibility_date ;
    }
  if ( interactive_modification && v.getTime() - millisec() < 0 )
    {
      alert_append("La date de visibilité ne doit pas être dans le passé") ;
      return column.visibility_date ;
    }
  v = ''+v.getFullYear()+two_digits(v.getMonth()+1)+two_digits(v.getDate()) ;
  return v ;
}

function set_comment(value, column)
{
  var round_by = value.replace(/.*arrondi[es]* *[aà] *([0-9.,]*).*/i,'$1') ; 
  if ( round_by === '' )
    column.round_by = undefined ;
  else
    column.round_by = a_float(round_by) ;

  var best_of = value.replace(/.*oyenne *des *([0-9]*) *meilleur.*/i,'$1') ; 
  if ( best_of === '' )
    {
      if ( value.search('la meilleure note') == -1 )
	column.best_of = undefined ;
      else
	column.best_of = 1 ;
    }
  else
    column.best_of = a_float(best_of) ;

  var best_of = value.replace(/.*]([0-9]*),([0-9]*)\[.*/,'][ $1 $2').split(/ /) ;

  if ( best_of.length == 3 && best_of[0] == '][' )
    {
      column.best_of = - a_float(best_of[2]) ;
      if ( isNaN(column.best_of) )
	column.best_of = undefined ;

      column.mean_of = - a_float(best_of[1]) ;
      if ( isNaN(column.mean_of) )
	column.mean_of = undefined ;
    }
  else
    column.mean_of = undefined ;

  column.need_update = true ;

  return value ;
}

function returns_false() { return false ; } ;

function the_green_filter(c, column)
{
  return c.value > column.color_green ;
}

function set_green(value, column)
{
  if ( value === undefined )
    value = '' ;
  if ( value === '' )
    {
      column.color_green_filter = returns_false ;
    }
  else if ( value === 'NaN' )
    {
      column.color_green_filter = the_green_filter ;
      var stats = compute_histogram(column.data_col) ;
      column.color_green = stats.average() + stats.standard_deviation() ;
    }
  else if ( isNaN(value) )
    {
      column.color_green_filter = compile_filter_generic(value) ;
    }
  else
    {
      value = Number(value) ;
      column.color_green_filter = the_green_filter ;
      column.color_green = value ;
    }

  return value ;
}

function the_red_filter(c, column)
{
  return c.value < column.color_red ;
}


function set_red(value, column)
{
  if ( value === undefined )
    value = '' ;
  if ( value === '' )
    {
      column.color_red_filter = returns_false ;
    }
  else if ( value === 'NaN' )
    {
      column.color_red_filter = the_red_filter ;
      var stats = compute_histogram(column.data_col) ;
      column.color_red = stats.average() - stats.standard_deviation() ;
    }
  else if ( isNaN(value) )
    {
      column.color_red_filter = compile_filter_generic(value) ;
    }
  else
    {
      value = Number(value) ;
      column.color_red_filter = the_red_filter ;
      column.color_red = value ;
    }

  return value ;
}




function ___NAME__()
{
  types.push({title: '__NAME__',
      full_title: __FULL_TITLE__,

      set_title: __SET_TITLE__,
      set_type: __SET_TYPE__,
      set_test_filter: __SET_TEST_FILTER__,
      set_minmax: __SET_MINMAX__,
      set_weight: __SET_WEIGHT__,
      set_green: __SET_GREEN__,
      set_red: __SET_RED__,
      set_empty_is: __SET_EMPTY_IS__,
      set_columns: __SET_COLUMNS__,
      set_visibility_date : __SET_VISIBILITY_DATE__,
      set_comment: __SET_COMMENT__,
      set_freezed: __SET_FREEZED__,
      set_width: __SET_WIDTH__,
      set_position: __SET_POSITION__,
      set_hidden: __SET_HIDDEN__,
      set_author: __SET_AUTHOR__,

      default_filter: __DEFAULT_FILTER__,

      tip_column_title: __TIP_COLUMN_TITLE__,
      tip_title: __TIP_TITLE__,
      tip_type: __TIP_TYPE__,
      tip_filter: __TIP_FILTER__,
      tip_weight: __TIP_WEIGHT__,
      tip_test_filter: __TIP_TEST_FILTER__,
      tip_minmax: __TIP_MINMAX__,
      tip_cell: __TIP_CELL__,
      tip_columns: __TIP_COLUMNS__,
      tip_red: __TIP_RED__,
      tip_green: __TIP_GREEN__,
      tip_visibility_date: __TIP_VISIBILITY_DATE__,
      tip_empty_is: __TIP_EMPTY_IS__,
      tip_comment: __TIP_COMMENT__,
		 //      tip_author: __TIP_AUTHOR__,  XXX Problems with IE

      cell_test: __CELL_TEST__,   
      cell_compute: __CELL_COMPUTE__,   
      cell_is_modifiable: __CELL_IS_MODIFIABLE__,   
      onmousedown: __ONMOUSEDOWN__,
      formatte: __FORMATTE__,

      should_be_a_float: __SHOULD_BE_A_FLOAT__

		 }) ;
  types[types.length-1].index = types.length - 1 ;
  return types[types.length-1] ;
}

