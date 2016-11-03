#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2009-2012 Thierry EXCOFFIER, Universite Claude Bernard
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


"""This TEMPLATE can be modified and it will update table in usage
to match the modification. For example, the columns order.
"""

import os
import html
from .. import inscrits
from .. import utilities
from .. import configuration
from . import _ucbl_

prototype = "_ucbl_"

def referent_resume(table, login):
    s = []
    first = True
    for line in table.get_lines(login):
        for i, col in enumerate(table.columns):
            if i >= 3 and line[i].value:
                if first:
                    s.append('<div class="blocnote">'
                             + utilities._("MSG_Referents_suivi")
                             % (table.year, table.year+1) + '<br>')
                    first = False
                s.append('%s&nbsp;:&nbsp;<b>%s</b>,'
                         % ( col.title,
                             html.escape(str(line[i].value)) ))
    if first == False:
        s.append('</div>')
    return '\n'.join(s)

# The ID starting by 0_ are here for compatibility with _ucbl template
referent_columns = {
    '0_0' : {'position': 0,'type':'Text', "width":4, "freezed":'F',
             'repetition': 1},
    '0_1' : {'position': 1,'type':'Text', "width":6, "freezed":'F'},
    '0_2' : {'position': 2,'type':'Text', "width":6, "freezed":'F'},
    '0_3' : {'hidden':1},
    '0_4' : {'hidden':1},
    '0_5' : {'position': 3,'type':'Text', "width":1, "freezed":'C',
             "hidden":1, 'title':'Inscrit'},
    'FiRe': {'position': 4,'type':'Bool', "width":1, "freezed":'F'},
    'CON1': {'position': 5,'type':'Bool', "width":2},
    'REM1': {'position': 6,'type':'Text', "width":6},
    'RDV1': {'position': 7,'type':'Prst', "width":2},
    'RDV2': {'position': 8,'type':'Prst', "width":2},
    'JUR1': {'position': 9,'type':'Text', "width":6},
    'CON2': {'position':10,'type':'Bool', "width":2},
    'REM2': {'position':11,'type':'Text', "width":6},
    'RDV3': {'position':12,'type':'Prst', "width":2},
    'RDV4': {'position':13,'type':'Prst', "width":2},
    'JUR2': {'position':14,'type':'Text', "width":6},
    }

def init(table):
    _ucbl_.init(table)
    table.default_sort_column = 2 # Compatibility with old files
    table.private = 1
    table.modifiable = int(utilities.university_year() == table.year)
    table.referent_resume = referent_resume
    table.referent_columns = referent_columns

def check_columns(table):
    if len(table.columns) != 0 and table.columns.from_id('FiRe') is None:
        table.modifiable = 0
        return # Old table : no more columns update
    cols = dict(list(referent_columns.items()))
    cols.update(configuration.local_columns(table))
    for k, v in cols.items():
        x = utilities._('COL_TITLE_' + k)
        if x != 'COL_TITLE_' + k:
            v['title'] = x
        x = utilities._('COL_COMMENT_' + k)
        if x != 'COL_COMMENT_' + k:
            v['comment'] = x
    table.update_columns(cols)

def content(dummy_table):
    return _ucbl_.update_student_information

def onload(table):
    """This function is only here to correct a bug on old referent files"""
    user = utilities.module_to_login(table.ue)
    if user not in table.masters:
        utilities.warn('Missing master for ' + table.ue, what='warning')
        table.masters.append(user)

def create(table):
    p = table.get_ro_page()
    table.table_attr(p, 'masters', [utilities.module_to_login(table.ue)])
    table.table_attr(p, 'default_nr_columns', 9)
    table.table_attr(p, 'default_sort_column', 2)
    check_columns(table)

def update_inscrits_referents(the_ids, table, page):
    from .. import referent
    table.lock()
    try:
        check_columns(table)
    finally:
        table.unlock()
    if configuration.year_semester[1] == configuration.university_semesters[0]:
        contrat = 'CON1'
    else:
        contrat = 'CON2'

    fire = table.columns.from_id('FiRe').data_col
    done = {}
    for the_id in referent.students_of_a_teacher(utilities.module_to_login(table.ue)):
        login = utilities.the_login(the_id)
        done[login] = True
        firstname,surname,mail = inscrits.L_batch.firstname_and_surname_and_mail(login)
        the_ids[the_id] = mail
        # COpy/Paste with Favoris.py
        if referent.need_a_charte(login):
            if utilities.charte_signed(login, year=table.year,
                                       semester=table.semester):
                s = configuration.yes
            else:
                s = configuration.no
        else:
            if utilities.manage_key('LOGINS', os.path.join(login, 'rsskey')):
                s = configuration.yes
            else:
                s = configuration.no
        pe = configuration.student_in_first_year(login)
        table.lock()
        try:
            line = table.get_line_id_or_create(login)
            lines = tuple(table.get_items(login))
            if len(lines) == 0:
                #  FiRe only setted if empty, it must never change
                if pe is True:
                    table.cell_change(page, "FiRe", line, configuration.yes)
                elif pe is False:
                    table.cell_change(page, "FiRe", line, configuration.no)
            table.cell_change(page, "0_0"   ,line, the_id)
            table.cell_change(page, "0_1"   ,line, firstname)
            table.cell_change(page, "0_2"   ,line, surname)
            table.cell_change(page, contrat ,line, s)

        finally:
            table.unlock()

    students_to_remove = [the_id
                          for the_id in table.logins()
                          if utilities.the_login(the_id) not in done]
    _ucbl_.remove_students_from_table(table, students_to_remove)

def check(table, update_inscrits=update_inscrits_referents):
    _ucbl_.check(table, update_inscrits)
