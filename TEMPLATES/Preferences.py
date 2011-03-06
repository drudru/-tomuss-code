#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2009,2011 Thierry EXCOFFIER, Universite Claude Bernard
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

prefs = {
'display_tips'   :("Affiche les bulles d'aides"                       ,"OUI"),
'nr_favorites'   :("Page d'accueil : nombre d'UE favorites affichées" ,"6"  ),
'nr_lines'       :("Nombre de lignes affichées par défaut"            ,"0"  ),
'nr_cols'        :("Nombre de colonnes affichées par défaut"          ,"0"  ),
'zebra_step'     :("Nombre de lignes entre les traits épais"          ,"5"  ),
'page_step'      :("Avec 0,5 «page suivante» décale d'½ page"         ,"1"  ),
'invert_name'    :("Inverse les colonnes NOM et PRÉNOM"               ,"OUI"),
'scrollbar_right':("Affiche l'ascenseur vertical à droite"            ,"OUI"),
'favoris_sort'   :("Page d'accueil : trie les favoris par code"       ,"NON"),
'v_scrollbar'    :("Affiche l'ascenseur vertical"                     ,"OUI"),
'v_scrollbar_nr' :("Nombre de caractères affichés dans l'ascenseur vertical","1"  ),
'interface'      :("Interface utilisateur : N:normal L:lineaire (pour malvoyant)"   ,"N"),
'current_suivi'  :("Page d'accueil : on fait le suivi du semestre courant au lieu du semestre choisi","NON"),
}

def create(table):
    p = table.new_page('' ,data.ro_user, '', '')
    table.table_attr(p, 'masters', [utilities.module_to_login(table.ue)])
    table.column_change(p,'0_0','Explications'       ,'Text','','','F',0,20)
    table.column_change(p,'0_1','Valeur recommandée' ,'Text','','','F',0,4 )
    table.column_change(p,'0_2','Ordre'              ,'Text','','','F',1,2 )
    table.column_change(p,'0_3','Votre choix'        ,'Text','','','F',0,4 )
    table.table_attr(p, 'default_nr_columns', 3)
    table.table_attr(p, 'default_sort_column', 0)
    table.new_page('' ,utilities.module_to_login(table.ue), '', '')

def init(table):
    table.default_sort_column = 0 # compatibility with old Preferences files
    table.private = 1

def check(table):
    p_ro = table.pages[0]
    p_rw = table.pages[1]

    table.lock()
    try:
        # Remove old attribute            
        for lin in table.lines:
            if lin not in prefs:
                if table.lines[lin][0].value:
                    table.cell_change(p_ro, '0_0', lin, '')
                    table.cell_change(p_ro, '0_1', lin, '')
                    table.cell_change(p_ro, '0_2', lin, '')
                    table.cell_change(p_ro, '0_3', lin, '')

        # Add/update new attributes
        for lin, value in prefs.items():
            table.cell_change(p_ro, '0_0', lin, value[0])
            table.cell_change(p_ro, '0_1', lin, value[1])
            if lin not in table.lines:
                table.cell_change(p_rw, '0_3', lin, value[1])
    finally:
        table.unlock()

def preferences(table):
    p = {}
    for lin in prefs:
        if lin in table.lines:
            p[lin] = table.lines[lin][3].value
        else:
            p[lin] = prefs[lin][1]
    return p
        
