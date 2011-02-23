#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2009-2010 Thierry EXCOFFIER, Universite Claude Bernard
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
import inscrits
import utilities
import configuration
import _ucbl_
import abj
import os

def init(table):
    _ucbl_.init(table)
    table.default_sort_column = 2 # Compatibility with old files
    table.abjs = abj.get_abjs(table.year, table.semester)
    table.abjs_mtime = 0
    table.private = 1

def check_columns(table):
    page = table.pages[0]
    # Don't change line order.
    # The line content is used in other plugins and the order must be unchanged
    # To change display order, use the number in the first column.
    for pos,col_id, col_title, col_type, col_fixed, col_width, col_comment in (
(0 ,'0_0' ,'ID'                      ,'Text','F',4 ,"Numéro étudiant"),
(1 ,'0_1' ,'Prénom'                  ,'Text','F',8 ,""),
(2 ,'0_2' ,'Nom'                     ,'Text','F',8 ,""),
(90,'0_3' ,'Contacté'                ,'Bool','' ,4 ,""),
(6 ,'0_4' ,'RDV_1'                   ,'Prst','' ,4 ,"Premier rendez-vous"),
(4 ,'0_5' ,'TOMUSS_Automne'          ,'Bool','' ,4 ,"L'étudiant s'est connecté"),
(7 ,'0_6' ,'RDV_2'                   ,'Prst','' ,4 ,"Deuxième rendez-vous"),
(91,'0_7' ,'ContratRespecté'         ,'Bool','' ,4 ,""),
(5 ,'0_8' ,'Remarques IP automne'    ,'Text','' ,16,'Remarques à usage privé'),
(92,'0_9' ,'Contacté_2'              ,'Bool','' ,4 ,""),
(11,'0_10','RDV_3'                   ,'Prst','' ,4 ,""),
(9 ,'0_11','TOMUSS_Printemps'        ,'Bool','' ,4 ,"L'étudiant s'est connecté"),
(12,'0_12','RDV_4'                   ,'Prst','' ,4 ,""),
(93,'0_13','ContratRespecté_2'       ,'Bool','' ,4 ,""),
(10,'0_14','Remarques IP Printemps'  ,'Text','' ,16,'Remarques à usage privé'),
(94,'0_15','.Réussite'               ,'Bool','' ,4 ,"Étudiant en situation de réussite"),
(8 ,'0_16','Commentaire Jury Automne','Text','' ,16,"Transmis aux membres des jurys"),
(95,'0_17','Inscrit'                 ,'Text','C',1 ,""),
(3 ,'0_18','Primo Entrant'           ,'Bool','F',4 ,"Première inscription en licence."),
(13,'0_19','Commentaire Jury Printemps','Text','',16,"Transmis aux membres des jurys"),
):
        for col in table.columns:
            # do not create the column if it exists.
            if ( col.the_id == col_id
                 and col.title == col_title
                 and col.comment == col_comment
                 and col.width == col_width
                 and col.position == pos
                 ):
                break
        else:
            if pos >= 90:
                hidden = 1
            else:
                hidden = 0
                
            table.column_change(page, col_id, col_title, col_type, '', '',
                                col_fixed , hidden, col_width)
            if not hidden:
                if col_comment:
                    table.column_comment(page, col_id, col_comment)
                if hasattr(table, 'column_attr'):
                    table.column_attr(page, col_id, 'position', pos)
                else:
                    table.column_position(page, col_id, pos)

        if table.default_nr_columns != 9:
            table.table_attr(page, 'default_nr_columns', 9)


def content(table):
    return _ucbl_.update_student_information

def onload(table):
    """This function is only here to correct a bug on old referent files"""
    user = utilities.module_to_login(table.ue)
    if user not in table.masters:
        utilities.warn('Missing master for ' + table.ue, what='warning')
        table.masters.append(user)

def create(table):
    p = table.new_page('' ,data.ro_user, '', '')
    table.table_attr(p, 'masters', [utilities.module_to_login(table.ue)])
    check_columns(table)
    table.table_attr(p, 'default_nr_columns', 9)
    table.table_attr(p, 'default_sort_column', 2)

def update_inscrits_referents(the_ids, table, page):
    import referent
    table.lock()
    try:
        check_columns(table)
    finally:
        table.unlock()
    if configuration.year_semester[1] == 'Automne':
        contrat = '0_5'
    else:
        contrat = '0_11'

    done = {}
    current_year = str(utilities.university_year())[-2:]
    for the_id in referent.students_of_a_teacher(utilities.module_to_login(table.ue)):
        login = utilities.the_login(the_id)
        done[login] = True
        firstname,surname,mail = inscrits.L_batch.firstname_and_surname_and_mail(login)
        the_ids[the_id] = mail.encode('utf-8')
        # COpy/Paste with Favoris.py
        if referent.need_a_charte(login):
            if utilities.manage_key('LOGINS', utilities.charte(login)):
                s = 'OUI'
            else:
                s = 'NON'
        else:
            if utilities.manage_key('LOGINS', os.path.join(login, 'rsskey')):
                s = 'OUI'
            else:
                s = 'NON'
        if login[1:3] == current_year:
            for group in inscrits.L_batch.member_of_list(login):
                if '1A,OU=' in group:
                    pe = 'OUI'
                    break
            else:
                pe = 'NON'
        else:
            pe = 'NON'
        table.lock()
        try:
            lines = list(table.get_items(login))
            if len(lines) == 0:
                line = "0_" + str(len(table.lines))
            else:
                line = lines[0][0]
            table.cell_change(page, "0_0"  ,line, the_id)
            table.cell_change(page, "0_1"  ,line, firstname.encode('utf-8'))
            table.cell_change(page, "0_2"  ,line, surname.encode('utf-8'))
            table.cell_change(page, "0_18" ,line, pe)
            table.cell_change(page, contrat,line, s)

        finally:
            table.unlock()

    students_to_remove = [the_id
                          for the_id in table.logins()
                          if utilities.the_login(the_id) not in done]
    _ucbl_.remove_students_from_table(table, students_to_remove)

def check(table, update_inscrits=update_inscrits_referents):
    _ucbl_.check(table, update_inscrits)
    
cell_change = _ucbl_.cell_change
