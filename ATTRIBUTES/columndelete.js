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

function column_delete()
{
  var column = the_current_cell.column ;
  var empty = column_empty_of_cells(column.data_col) ;
  if ( column.real_type.cell_is_modifiable && ! empty )
    {
      alert('On peut seulement détruire des colonnes vides.\n\nVous devez donc d\'abord vider la colonne en cliquant sur "Remp."') ;
      return ;
    }
  if ( column.author == '*' && column.data_col < 6 )
    {
      alert("Il est interdit d'enlever cette colonne") ;
      return ;
    }
  if ( ! column_change_allowed(column) )
    {
      alert("La colonne n'a pas été créée par vous mais par " + column.author +
	    " et vous n'êtes pas responsable de l'UE : " + teachers) ;
      return ;
    }
  var c = column_used_in_average(column.title) ;
  if ( c )
    {
      alert("Cette colonne est utilisée par la colonne «" + c + '»') ;
      return ;
    }
  if ( column.the_local_id !== undefined )
    {
      alert("Cette colonne n'existe pas encore.\nPour afficher moins de colonnes sur l'écran, changez le nombre de colonnes à afficher dans le menu en haut de la case «Tableau».") ;
      return ;
    }
  if ( ! empty )
    if (!confirm("Voulez-vous vraiment détruire la colonne : " + column.title))
      return ;

  append_image(undefined, 'column_delete/' + column.the_id) ;
  Xcolumn_delete(' ', column.the_id) ;
  the_current_cell.update_headers() ;
}
