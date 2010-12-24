#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2009,2010 Thierry EXCOFFIER, Universite Claude Bernard
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

import data
import utilities

# DO NOT CHANGE THE ORDER IN THIS LIST TO CHANGE ORDER ON SCREEN.
# If you want to do so, give a correct number
# in the second column because the display is sorted with this column
prefs = (
('display_tips'   ,0  ,"Affiche les bulles d'aides"                    ,"OUI"),
('display_picture',9.9  ,""                     ,""),
('unmodifiable'   ,9.9  ,"", ""),
('tipfixed'       ,9.9  ,""     ,""),
('nr_favorites'   ,2.5,"Nombre d'UE favorites affichées"               ,"6"  ),
('nr_lines'       ,3  ,"Nombre de lignes affichées par défaut"         ,"0"  ),
('nr_cols'        ,4  ,"Nombre de colonnes affichées par défaut"       ,"0"  ),
('zebra_step'     ,4.5,"Nombres de lignes entre les traits épais"      ,"5"  ),
('page_step'      ,4.6,"Avec 0,5 «page suivante» décale d'½ page"      ,"1"  ),
('invert_name'    ,5  ,"Inverse les colonnes NOM et PRÉNOM"            ,"OUI"),
('v_scrollbar'    ,6  ,"Affiche l'ascenseur vertical"                  ,"OUI"),
('v_scrollbar_nr' ,7  ,"Nombre de caractères affichés dans l'ascenseur vertical","1"  ),
('scrollbar_right',7.05,"Affiche l'ascenseur vertical à droite"        ,"OUI"),
('interface'      ,7.1,"Interface utilisateur : N:normal L:lineaire (pour malvoyant)"   ,"N"),
('favoris'        ,9.9  ,""   ,""),
('master_of'      ,9.9  ,""   ,"[]"),
('current_suivi'  ,10   ,"Page d'accueil : on fait le suivi du semestre courant","NON"),
)

def create(table):
    p = table.new_page('' ,data.ro_user, '', '')
    table.table_attr(p, 'masters', [utilities.module_to_login(table.ue)])
    table.column_change(p,'0_0','Explications'       ,'Text','','','F',0,20)
    table.column_change(p,'0_1','Valeur recommandée' ,'Text','','','F',0,4 )
    table.column_change(p,'0_2','Ordre'              ,'Text','','','F',1,2 )
    table.column_change(p,'0_3','Votre choix'        ,'Text','','','F',0,4 )
    table.table_attr(p, 'default_nr_columns', 3)
    table.table_attr(p, 'default_sort_column', 2)
    table.new_page('' ,utilities.module_to_login(table.ue), '', '')

def init(table):
    table.default_sort_column = 2 # compatibility with old Preferences files
    table.private = 1

def check(table):
    p_ro = table.pages[0]
    p_rw = table.pages[1]

    table.lock()

    try:
        for line, order, text, value in prefs:
            if line not in table.lines:
                if text == '':
                    continue # Don't add obsolete preferences
                # Do not change user entered value
                table.cell_change(p_rw, '0_3', line, value)
            # Create or update other values
            table.cell_change(p_ro, '0_0', line, text)
            table.cell_change(p_ro, '0_1', line, value)
            table.cell_change(p_ro, '0_2', line, str(order))
            if text == '':
                # Remove obsolet values
                table.cell_change(p_rw, '0_3', line, '')
    finally:
        table.unlock()

def preferences(table):
    p = {}
    for line, order, text, value in prefs:
        if line != '':
            if line in table.lines:
                p[line] = table.lines[line][3].value
            else:
                p[line] = value
    return p
        
