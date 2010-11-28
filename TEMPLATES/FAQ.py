#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2009 Thierry EXCOFFIER, Universite Claude Bernard
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

def create(table):
    table.add_master('thierry.excoffier')
    p = table.new_page('' ,'thierry.excoffier', '', '')
    table.column_change(p,'0_0','Numéro','Text','','','F',0,1)
    table.column_change(p,'0_1','Question','Text','','','F',0,10)
    table.column_change(p,'0_2','Réponse','Text','','','F',0,20)
    table.cell_change(p,'0_0','2_0','0','20081113165156')
    table.cell_change(p,'0_1','2_0','Comment poser des questions dans cette FAQ ?','20081113165210')
    table.cell_change(p,'0_2','2_0','Vous écrivez votre question dans la colonne question :-)','20081113165247')
    table.cell_change(p,'0_0','2_1','0.1','20081113165250')
    table.cell_change(p,'0_1','2_1','Qui donne les réponses et quand ?','20081113165320')
    table.cell_change(p,'0_2','2_1','Tous ceux qui veulent participer, et quand on a le temps...','20081113165406')
    table.cell_change(p,'0_0','2_2','0.2','20081113165409')
    table.cell_change(p,'0_1','2_2','Comment exprimer son avis sur une réponse ?','20081113165443')
    table.cell_change(p,'0_2','2_2','En mettant un commentaire sur la réponse','20081113165452')
    table.cell_change(p,'0_0','2_3','0.3','20081113165456')
    table.cell_change(p,'0_1','2_3','Comment chercher un mot clef dans la FAQ ?','20081113165515')
    table.cell_change(p,'0_2','2_3','Vous tapez dans le filtre de ligne un caractère tilde suivi de votre mot clef.','20081113165550')
    table.cell_change(p,'0_0','2_4','0.4','20081113165456')
    table.cell_change(p,'0_1','2_4','Comment retrouver les questions que j\'ai posés ?','20081113165515')
    table.cell_change(p,'0_2','2_4','Vous tapez dans le filtre de ligne un caractère arobase : @','20081113165550')
    table.default_nr_columns_change(3)

def init(table):
    table.default_sort_column = 0

