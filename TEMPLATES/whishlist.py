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
    table.new_page('' ,'*', '', '')
    p = table.new_page("",'thierry.excoffier',"","")
    table.table_attr(p, 'masters', list(configuration.root))
    table.column_change(p,'1_0','Num\xc3\xa9ro','Text','','','',0,1)
    table.column_change(p,'1_1','Votre_remarque_ou_voeu','Text','','','',0,10)
    table.column_change(p,'1_2','R\xc3\xa9ponse_du_programmeur','Text','','','',0,10)
    table.cell_change(p,'1_0','1_0','0','20081113222630')
    table.cell_change(p,'1_1','1_0','Je veux pouvoir choisir les couleurs des pages !','20081113222836')
    table.cell_change(p,'1_2','1_0','OK mais quand ce qui est vraiment important aura \xc3\xa9t\xc3\xa9 fait.','20081113222805')
    table.table_attr(p, 'default_nr_columns', 3)

