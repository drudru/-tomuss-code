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

function date_formatter(value)
{
  if ( value.join )
    {
       first_day = new Date() ;
       first_day.setTime(value[0]*1000) ;

       last_day = new Date() ;
       last_day.setTime(value[1]*1000) ;
       var s = formatte_date(last_day) ;
       
       last_day.setTime(value[1]*1000 + 1000*86400) ;

       return formatte_date(first_day) + ' ' + s ;
    }

  var v = value.replace(/[ ,][ ,]*/g, ' ') ;
  var vs = v.split(' ') ;
  if ( vs.length != 2 )
    {
      Alert("ALERT_tabledates_2") ;
      return ;
    }
  var d1 = parse_date(vs[0]).getTime() ;
  var d2 = parse_date(vs[1], true).getTime() ;
  if ( isNaN(d1) || isNaN(d2) )
    {
      Alert("ALERT_tabledates_bad") ;
      return ;
    }
  if ( d1 > d2 )
    {
      Alert("ALERT_tabledates_invert") ;
      return ;
    }
  v = date_to_store(vs[0]).replace(/..$/,'') + ' '
    + date_to_store(vs[1], true).replace(/..$/,'') ;
  
  return v ;
}
