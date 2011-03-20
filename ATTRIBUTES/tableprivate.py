#!/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2008-2011 Thierry EXCOFFIER, Universite Claude Bernard
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#    Contact: Thierry.EXCOFFIER@bat710.univ-lyon1.fr

from tablemodifiable import TableModifiable

class TablePrivate(TableModifiable):
    formatter = r'''
function(value)
{
  if ( (table_attr.masters.length == 0 || ! i_am_the_teacher) && value == 1)
    {
      alert('Vous ne pouvez pas rendre cette table privée car\nvous ne pourriez plus la voir.\nCommencez par vous ajouter comme étant\nun des responsable de cette table') ;
      return ;
    }
  return value ;
}'''

    name = 'private'
    default_value = 0
    gui_display = "GUI_select"
    
    tip = """Une table publiques est visible/modifiable par TOUS les <b>enseignants</b>.<br>
Une table privée est seulement visible/modifiable par les responsables,<br>
les étudiants pourront néanmoins voir leur suivi."""
