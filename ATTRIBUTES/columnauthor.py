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

class ColumnAuthor(ColumnAttr):
    computed = 1
    update_headers = 1
    name = 'author'
    check_and_set = 'test_nothing'
    formatter = 'get_author2'
    tip = "Personne qui a modifié la définition<br>de la colonne pour la dernière fois :"
    gui_display = "GUI_none"
    css = '''
    #menutop #t_column_author { font-size: 80% ; }
    #menutop DIV.tabs #t_column_author { font-size: 100% ; }
    '''
