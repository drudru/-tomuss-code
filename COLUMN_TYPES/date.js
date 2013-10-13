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

function test_date(value, column)
{
  if ( value === '' )
    return value ;

  var v = value.split(' ',1)[0].split('/') ;
  if ( v.length < 1 || v.length > 3 )
    {
      alert_append(_('ALERT_date_format')) ;
      return ;
    }

  var day, month, year ;
  var today = new Date() ;
  if ( v.length < 3 )
    year = today.getFullYear() ;
  else
    {
      year = Number(v[2]) ;
      if ( year < 100 )
	if ( year <= (today.getFullYear()-2000) + 5 ) // 5 year in future
	  year += 2000 ;
	else
	  year += 1900 ;
    }

  if ( v.length < 2 )
    month = today.getMonth()+1 ;
  else
    month = Number(v[1]) ;

  day = Number(v[0]) ;

  var d = new Date(year, month-1, day) ;
  if ( d.getDate()!= day || d.getMonth() != month-1 || d.getFullYear() != year)
    {
      alert_append(_('ALERT_date_invalid') + value) ;
      return ;
    }
  day = two_digits(day) ;
  month = two_digits(month) ;

  var h = value.split(' ',2)[1] ;
  if ( h === undefined )
    h = '' ;
  else
    {
      if ( h.search(/^[0-9][h:]/) != -1 )
	h = '0' + h ;
      h = ' ' + h.replace(/h/g, ':') ;
    }

  return day + '/' + month + '/' + year + h ;
}
