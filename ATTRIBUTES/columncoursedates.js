// -*- coding: utf-8 -*-
/*
    TOMUSS: The Online Multi User Simple Spreadsheet
    Copyright (C) 2011 Thierry EXCOFFIER, Universite Claude Bernard

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


function course_dates_formatter(column, value)
{
  if ( value === '' ) return '' ;
  var dates = value.split(/ +/) ;
  var v = [] ;
  for(var date in dates)
     {
     date = dates[date] ;
     v.push(date.substr(6,2)+'/'+date.substr(4,2)+'/'+date.substr(0,4)
	    +date.substr(8)) ;
     }
  return v.join(' ') ;
}


function set_course_dates(value, column, interactive_modification)
{
  if ( value === '')
  {
    column.parsed_course_dates = undefined ;
    return value ;
  }
  var dates = value.split(/[ ,;]+/) ;
  var t = [] ;
  column.parsed_course_dates = [] ;
  for(var date in dates)
    {
      date = dates[date] ;
      if ( date.substr(date.length-1).toUpperCase() == 'M')
	ma = 'M' ;
      else if ( date.substr(date.length-1).toUpperCase() == 'A')
	ma = 'A' ;
      else
	ma = '' ;
      date = date.replace(/[MAma]/, '') ;

      v = get_date(date) ;
      if ( v == false )
	{
          alert_append(date + _("ALERT_coursedates_invalid")) ;
	  return column.course_dates ;
	}
      if ( ma != 'A' )
	column.parsed_course_dates.push(v.getTime()) ;
      if ( ma != 'M' )
	column.parsed_course_dates.push(v.getTime()+86400*1000/2) ;
      t.push(''+v.getFullYear()+two_digits(v.getMonth()+1)
	     +two_digits(v.getDate()) + ma) ;
    }
  return t.join(' ') ;
}
