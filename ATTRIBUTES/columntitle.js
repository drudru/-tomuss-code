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
	return column_attributes.title.check_and_set(value + '_bis', column,
                                                     xcolumn_attr) ;
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
	      alert_append(_("ALERT_columntitle_unchangeable")) ;
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
