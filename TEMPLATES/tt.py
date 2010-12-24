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
import configuration
import utilities

def create(table):
    
    p = table.new_page('' ,data.ro_user, '', '')
    table.table_attr(p, 'default_nr_columns', 11)

    if configuration.regtest:
        masters = [configuration.invited_abj_masters[-1]]
    else:
        masters = ['sandrine.gourdine', 'corinne.tourvieille',
                   'nathalie.piovesan', 'thierry.excoffier']

    table.table_attr(p, 'masters', masters)
    table.column_change(p,'0_0','Numéro_étudiant'                 ,'Text','','' ,'',0,4 )
    table.column_change(p,'0_1','Prénom'                          ,'Text','','' ,'',0,8 )
    table.column_change(p,'0_2','Nom'                             ,'Text','','' ,'',0,8 )
    table.column_change(p,'0_3','+Ecrit'                          ,'Text','','1','',0,3 )
    table.column_comment(p,'0_3', '1 = +33% ou pourcentage de temps en plus')
    table.column_change(p,'0_4','+Oral'                           ,'Text','','1','',0,3 )
    table.column_comment(p,'0_4', '1 = +33% ou pourcentage de temps en plus')
    table.column_change(p,'0_5','+TP'                             ,'Text','','1','',0,3 )
    table.column_comment(p,'0_5', '1 = +33% ou pourcentage de temps en plus')
    table.column_change(p,'0_6','Secrétaire'                      ,'Bool','','1','',0,2 )
    table.column_comment(p,'0_6', "Il dispose d'un assistant")
    table.column_change(p,'0_7','Salle_Particulière'              ,'Bool','','1','',0,2 )
    table.column_comment(p,'0_7', "Il dispose d'une salle")
    table.column_change(p,'0_8','Début'                           ,'Date','','' ,'',0,6 )
    table.column_comment(p,'0_8', "Indiquer la durée si elle n'est pas indéfinie")
    table.column_change(p,'0_9','Fin'                             ,'Date','','' ,'',0,6 )
    table.column_comment(p,'0_9', "Indiquer la durée si elle n'est pas indéfinie")
    table.column_change(p,'0_10','Remarques_Et_Autres_Dispositions','Text','','' ,'',0,13)
    table.table_attr(p, 'default_sort_column', 2)


import _ucbl_

def init(table):
    _ucbl_.init(table)
    table.default_sort_column = 2 # compatibility with old files
    table.do_not_unload = 1
    table.modifiable = int(table.modifiable
                           and utilities.university_year() == table.year)
    table.update_inscrits = table.modifiable

def content(table):
    return _ucbl_.update_student_information

cell_change = _ucbl_.cell_change

def check(table):
    # Get mails and portails
    _ucbl_.check(table, update_inscrits=lambda x,y,z: None)
