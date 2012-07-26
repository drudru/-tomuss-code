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

// DO NOT TRANSLATE THESE STRING
// IT IS DEPRECATED and only here to read old data files

function set_comment(value, column)
{
  var round_by = value.replace(/.*arrondi[es]* *[aà] *([0-9.,]*).*/i,'$1') ;
  column.round_by = a_float(round_by) ;
  if ( !isNaN(value) || isNaN(column.round_by) )
  {
    column.round_by = undefined ;
  }

  var best_of = value.replace(/.*oyenne *des *([0-9]*) *meilleur.*/i,'$1') ;
  if ( best_of === '' )
    {
      if ( value.search('la meilleure note') == -1 )
	column.best_of = undefined ;
      else
	column.best_of = 1 ;
    }
  else
  {
    column.best_of = a_float(best_of) ;
    if ( isNaN(column.best_of) )
      column.best_of = undefined ;
  }

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

  column.historical_comment = column.best_of || column.mean_of
    || column.round_by ;

  return value ;
}
