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

function set_visibility_date(value, column, interactive_modification)
{
  if ( value === '')
    return value ;
  v = get_date(value) ;
  if ( v == false )
    {
      alert("La date que vous donnez n'est pas valide : " + value) ;
      return column.visibility_date ;
    }
  if ( (v.getTime() - millisec())/(86400*1000) > 31 )
    {
      alert("La date de visibilité doit être dans moins d'un mois") ;
      return column.visibility_date ;
    }
  if ( interactive_modification && v.getTime() - millisec() < 0 )
    {
      alert("La date de visibilité ne doit pas être dans le passé") ;
      return column.visibility_date ;
    }
  v = ''+v.getFullYear()+two_digits(v.getMonth()+1)+two_digits(v.getDate()) ;
  return v ;
}
