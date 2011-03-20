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

from column import ColumnAttr
import plugins

class ColumnType(ColumnAttr):
    name = 'type'
    priority = -1 # because 'real_type' must be computed before
    update_headers = 1
    display_table = 1
    default_value = 'Note'
    check_and_set = 'set_type'
    gui_display = 'GUI_select'
    def encode(self, value):
        return plugins.types[value]
    def decode(self, value):
        return value.name
    tip = """<b>Type de la colonne</b>, il indique le contenu des cellules :
<ul>
<li> 'Text' : du texte libre
<li> 'Note' : une note, ou un indicateur de présence
<li> 'Moy' : calcul de la moyenne pondérée de plusieurs colonnes
<li> 'Prst' : Cellules cliquables pour indiquer la présence
<li> 'Nmbr' : Compte le nombre de cellules contenant une valeur
<li> 'Date' : Des dates de la forme JJ/MM/AAAA
<li> 'Bool' : Oui ou Non
<li> 'Max' : Maximum sur plusieurs colonnes
</ul>"""
