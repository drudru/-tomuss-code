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

class ColumnColumns(ColumnAttr):
    name = 'columns'
    display_table = 1
    check_and_set = 'set_columns'
    visible_for = ['Moy', 'Nmbr', 'Mail', 'Code_Etape',
                   'COW', 'Firstname', 'Surname', 'Phone', 'Max']
    tip = {
        '': '<b>Colonnes utilisées pour faire le calcul',
        'Code_Etape':
        """<b>Extrait le code étape</b><br>
        Indiquez la colonne de numéro d'étudiants <b>ID</b><br>
        pour lesquels on veut extraire le code étape.""",
        'COW':
        """<b>Nom de la colonne dont on veut copier le contenu.</b><br>
        La copie ne se fera plus si vous saisissez une valeur<br>
        dans la cellule. Vous pouvez par exemple copier une colonne<br>
        contenant des moyennes pour en modifier certaines.""",
        'Firstname':
        """<b>Trouve le prénom</b><br>
        Indiquez la colonne de comptes (ID)<br>
        pour lesquels on veut trouver le prénom.""",
        'Mail':
        """<b>Trouve l'adresse mail</b><br>
        Indiquez la colonne de comptes (ID)<br>
        pour lesquels on veut trouver l'adresse mail.""",
        'Max':
        """<b>Noms des colonnes pour le calcul du maximum.</b><br>
        Le poids des colonnes n'intervient pas, par contre<br>
        les notes sont normalisées avant la comparaison""",
        'Moy':
        """<b>Noms des colonnes à moyenner</b><br>
        Par exemple : <b>td1 td2 td3</b>.<br>
        Le calcul de la note est la somme des<br>
        &nbsp;&nbsp;&nbsp;&nbsp;<em>td<sub>i</sub>.poids * (td<sub>i</sub>.note - td<sub>i</sub>.min) / (td<sub>i</sub>.max - td<sub>i</sub>.min)</em><br>
        divisée par la somme des poids ne commençant pas par <b>+</b> ou <b>-</b><br>
        Il est normalisé dans l'intervalle que vous avez indiqué.<br>
        Il est tenu compte des ABI, ABJ, PPN...""",
        'Nmbr':
        """<b>Noms des colonnes où il faut compter les cellules</b><br>
        qui correspondent au filtre""",
        'Phone':
        """<b>Trouve le numéro de téléphone</b><br>
        Indiquez la colonne de comptes (ID)<br>
        pour lesquels on veut trouver le téléphone.""",
        'Surname':
        """<b>Trouve le nom de famille</b><br>
        Indiquez la colonne de comptes (ID)<br>
        pour lesquels on veut trouver le nom de famille.""",
        }
    css = """
    #menutop #t_column_columns { width: 40% ; }
    #menutop DIV.tabs #t_column_columns { width: 73% ; }
    """
