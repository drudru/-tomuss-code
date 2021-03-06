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

function set_visibility_date(value, column, xcolumn_attr)
{
  if ( value === '')
    return value ;
  v = get_date(value) ;
  if ( v == false )
    {
      Alert("ALERT_columnvisibility_date_invalid", value) ;
      return column.formatter(column.visibility_date) ;
    }
  if ( xcolumn_attr === false )
  {
    // Interactive
    if ( (v.getTime() - millisec())/(86400*1000) > max_visibility_date )
    {
      alert(_("ALERT_columnvisibility_date_far_futur") + ' '
	    + max_visibility_date + ' '
	    + _("ALERT_columnvisibility_date_far_futur2")
	   ) ;
      return column.formatter(column.visibility_date) ;
    }
    if ( v.getTime() + 86400*1000 - millisec() < 0 )
    {
      Alert("ALERT_columnvisibility_date_past") ;
      return column.formatter(column.visibility_date) ;
    }
  }
  v = ''+v.getFullYear()+two_digits(v.getMonth()+1)+two_digits(v.getDate()) ;
  return v ;
}
