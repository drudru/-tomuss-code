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

/******************************************************************************
Check the 'weight' of a column.
******************************************************************************/

function set_weight(value, column)
{
  value = value.replace(',', '.') ; // To send the good value to the server
  var v = a_float(value) ;

  column.real_weight_add = true ; // Pondered average

  if ( isNaN(v) )
    {
      v = 0 ;
      value = '0' ;
    }
  else if ( value === '' )
    {
      v = 1 ;
      value = '1' ;
    }
  else
    {
      if ( value.substr(0,1) == '+' || value.substr(0,1) == '-' )
	column.real_weight_add = false ;
    }

  column.real_weight = v ;
  column.need_update = true ;

  return value ;
}
