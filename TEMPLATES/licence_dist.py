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
    new_page = table.new_page
    column_change = table.column_change
    cell_change = table.cell_change

    p = new_page('' ,data.ro_user, '', '')
    table.table_attr(p, 'masters', ['helene.paquien', 'saida.aissa',
                                    'saida.aissa',   'stephanie.pouchot',
                                    'thierry.lafouge', 'isabelle.buisson'])

    column_change(p,'0_0','Prenom','Text','','','F',0,4)
    column_change(p,'0_1','Nom','Text','','','F',0,4)
    column_change(p,'0_2','Date Réception','Date','','','',0,2)
    column_change(p,'0_3','Date de Naissance','Date','','','',0,2)
    column_change(p,'0_4','Nationalité','Text','','','',0,2)
    column_change(p,'0_6','Année dernier diplôme','Text','','','',0,2)
    column_change(p,'0_7','Diplôme (Dernier)','Text','','','',0,4)
    column_change(p,'0_8','Ecole (Dernière)','Text','','','',0,4)
    column_change(p,'0_9','Ville (de l\'école)','Text','','','',0,4)
    column_change(p,'0_14','On prend','Bool','','','',0,1)
    column_change(p,'0_15','Accepte','Bool','','','',0,1)
    table.table_attr(p, 'default_nr_columns', 11)
