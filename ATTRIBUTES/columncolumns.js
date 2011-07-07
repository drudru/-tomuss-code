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

function set_columns(value, column, xcolumn_attr)
{
  var cols = [] ;
  var weight = 0 ;
  var ok ;

  value = value.replace(/ *$/,'').replace(/^ */,'') ;

  if ( value === '' )
    {
      column.average_from = [] ;
      column.average_columns = [] ;
      column.need_update = true ;
      return value ;
    }


  column.average_from = value.split(/ +/) ;

  for(var i=0; i<column.average_from.length; i++)
    {
      ok = false ;
      for(var c in columns)
	if ( columns[c].title == column.average_from[i] )
	  {
	    cols.push(c) ;
	    weight += columns[c].real_weight ;
	    ok = true ;
	    break ;
	  }
      if ( ! ok )
	{
	  if ( xcolumn_attr === true )
	    // Wait the good value
	    // Nezt time 'xcolumn_attr' will be '1' in place of 'true'
	    setTimeout(function() {set_columns(value, column, 1)},
		       1000) ;
	  else
	    {
	      alert_append("Je ne connais pas le titre de colonne '"
			   + column.average_from[i]
			   + "' qui est utilisé dans la moyenne de la colonne "
			   + column.title + "\n"
			   + "LA LISTE DES COLONNES N'A PAS ÉTÉ SAUVEGARDÉE"
			   ) ;
	      column.average_columns = [] ;
	      return null ; // Do not save, but leaves user input unchanged
	    }
	}
    }
  column.average_columns = cols ;
  column.average_weight = weight ;
  column.need_update = true ;
  if ( column.type == 'Nmbr' )
    {
      column.minmax = '[0;' + column.average_columns.length + ']' ;
      column.max = column.average_columns.length ;
    }

  return value ;
}
