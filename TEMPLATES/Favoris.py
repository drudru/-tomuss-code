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

from Referents import init, content

def check_columns(table):
    page = table.pages[0]
    for col_id, col_title, col_type, col_fixed, col_width, col_comment in (
        ('0_0' ,'ID'               ,'Text','F', 4,"Numéro étudiant"),
        ('0_1' ,'Prénom'           ,'Text','F', 8,""),
        ('0_2' ,'Nom'              ,'Text','F', 8,""),
        ('0_3' ,'TOMUSS_Automne'   ,'Bool','' , 4,"l'étudiant s'est connecté"),
        ('0_4' ,'TOMUSS_Printemps' ,'Bool','' , 4,"l'étudiant s'est connecté"),
        ('0_5' ,'Inscrit'          ,'Text','C' ,1,""),
        ):
        for col in table.columns:
            # do not create the column if it exists.
            if ( col.the_id == col_id
                 and col.title == col_title ):
                break
        else:
            if col_title == 'Inscrit':
                hidden = 1
            else:
                hidden = 0
            table.column_change(page, col_id, col_title, col_type, '', '',
                                col_fixed , hidden, col_width)
            if col_comment:
                table.column_comment(page, col_id, col_comment)

def create(table):
    table.new_page('' ,data.ro_user, '', '')
    table.add_master(utilities.module_to_login(table.ue))
    check_columns(table)

def update_inscrits_favoris(the_ids, table, page):
    import referent
    import PLUGINS.suivi_student
    table.lock()
    try:
        check_columns(table)
    finally:
        table.unlock()
    if configuration.year_semester[1] == 'Automne':
        contrat = '0_3'
    else:
        contrat = '0_4'

    login = utilities.the_login(utilities.module_to_login(table.ue))
    d = utilities.manage_key('LOGINS', os.path.join(login, 'favstu'))
    if d is False:
        d = []
    else:
        d = eval(d)

    done = {}
    for the_id in d:
        login = utilities.the_login(the_id)
        done[login] = True
        firstname,surname,mail = inscrits.firstname_and_surname_and_mail(login)
        the_ids[the_id] = mail.encode('utf-8')
        # COpy/Paste with Referents.py
        if PLUGINS.suivi_student.need_a_charte(login):
            if utilities.manage_key('LOGINS', utilities.charte(login)):
                s = 'OUI'
            else:
                s = 'NON'
        else:
            if utilities.manage_key('LOGINS', os.path.join(login, 'rsskey')):
                s = 'OUI'
            else:
                s = 'NON'
        table.lock()
        try:
            lines = list(table.get_items(login))
            if len(lines) == 0:
                line = "0_" + str(len(table.lines))
            else:
                line = lines[0][0]
            table.cell_change(page, "0_0", line, the_id)
            table.cell_change(page, "0_1", line, firstname.encode('utf-8'))
            table.cell_change(page, "0_2", line, surname.encode('utf-8'))
            table.cell_change(page, contrat, line, s)
        finally:
            table.unlock()

    students_to_remove = [the_id
                          for the_id in table.logins()
                          if utilities.the_login(the_id) not in done]
    _ucbl_.remove_students_from_table(table, students_to_remove)

    
def check(table, update_inscrits=update_inscrits_favoris):
    _ucbl_.check(table, update_inscrits)
