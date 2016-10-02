// -*- coding: utf-8 -*-
/*
    TOMUSS: The Online Multi User Simple Spreadsheet
    Copyright (C) 2008-2015 Thierry EXCOFFIER, Universite Claude Bernard

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

function column_attr_try_replace(formula_column, attr, old_value, new_value,
				 job_to_do)
{
  var v = formula_column[attr] ;
  var w = v ;
  if ( attr == 'columns')
    w = ' ' + w.replace(/ /g, "  ") + ' ' ;
  w = w.replace(old_value, new_value) ;
  if ( attr == 'columns')
    w = w.replace(/  /g, " ").replace(/^ /, "").replace(/ $/, "") ;
  if ( w != v )
    {
      if ( ! column_change_allowed(formula_column) )
	return true ;
      job_to_do.push([formula_column, attr, w]) ;
    }
}

function protect_regexp(re)
{
  return re.replace(/([*\\[.$+?()])/g, '\\$1') ;
}

function protect_regexp_right(re)
{
  return re.replace(/\$/g, '\\$') ;
}

function set_title(value, column, xcolumn_attr)
{
  value = value.replace(/[[\] ]/g, '_') ;
  if ( value === '' )
    value = "." ;

  for(var data_col in columns)
    if ( data_col != column.data_col
	 && column.data_col // For display_suivi()
	 && !xcolumn_attr
	 && columns[data_col].title == value )
      {
	return column_attributes.title.check_and_set(value + '_bis', column,
                                                     xcolumn_attr) ;
      }

  if ( xcolumn_attr === false && column.title !== '' )
    {
      var job_to_do = [] ;
      var title = protect_regexp(column.title) ;

      for(var data_col in columns)
	{
	  var formula_column = columns[data_col] ;
	  var s1 = RegExp("\\[" + title + "\\]", "g") ;
	  var s2 = "[" + protect_regexp_right(value) + "]" ;
	  var changes = [
	    ['columns',
	     RegExp(" " + title + " ", "g"),
	     protect_regexp_right(" " + value + " ")],
            ['green'        , s1, s2],
            ['greentext'    , s1, s2],
            ['red'          , s1, s2],
            ['redtext'      , s1, s2],
            ['cell_writable', s1, s2]
	    ] ;
	  for(var i in changes)
	    {
	      i = changes[i] ;
	      if ( column_attr_try_replace(formula_column, i[0],
					   i[1], i[2], job_to_do) )
	      {
		alert_append(_("ALERT_columntitle_unchangeable")
			     + '\n\n' + column.title + ' ∈ '
			     + formula_column.title + '('
			     + formula_column.author + ')') ;
		return column.title ;
	      }
	    }
	}
      // Title change is possible
      column.title = value ; // Now to enable filter compilation
      for(var i in job_to_do)
	column_attr_set(job_to_do[i][0], job_to_do[i][1], job_to_do[i][2]) ;
    }
  column.title = value ;
  return column.title ;
}
