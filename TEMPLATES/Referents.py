#!/usr/bin/env python
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
import cgi
from .. import data
from .. import inscrits
from .. import utilities
from .. import configuration
from . import _ucbl_

def referent_resume(table, login):
    s = []
    first = True
    for line in table.get_lines(login):
        for i, col in enumerate(table.columns):
            if i >= 3 and line[i].value:
                if first:
                    s.append('<div class="blocnote">'
                             + unicode(utilities._("MSG_Referents_suivi"),
                                       'utf8')
                             % (table.year, table.year+1) + '<br>')
                    first = False
                s.append(u'%s&nbsp;:&nbsp;<b>%s</b>,'
                         % ( unicode(col.title, 'utf8'),
                             unicode(cgi.escape(str(line[i].value)), 'utf8') ))
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
    '0_5' : {'position': 3,'type':'Text', "width":1, "freezed":'F',
             "hidden":1, 'title':'Inscrit'},
    'FiRe': {'position': 4,'type':'Bool', "width":2, "freezed":'F'},
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
    'Insc': {'type':'Text', "hidden":1, "freezed": 'C', 'title': 'Inscrit'},
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
    for k, v in referent_columns.items():
        x = utilities._('COL_TITLE_' + k)
        if x != 'COL_TITLE_' + k:
            v['title'] = x
        x = utilities._('COL_COMMENT_' + k)
        if x != 'COL_COMMENT_' + k:
            v['comment'] = x
    table.update_columns(referent_columns)

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
    check_columns(table)
    table.table_attr(p, 'default_nr_columns', 9)
    table.table_attr(p, 'default_sort_column', 2)

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
        the_ids[the_id] = mail.encode('utf-8')
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
        if configuration.student_in_first_year(login):
            pe = configuration.yes
        else:
            pe = configuration.no
        table.lock()
        try:
            lines = list(table.get_items(login))
            if len(lines) == 0:
                line = "0_" + str(len(table.lines))
            else:
                line = lines[0][0] # Never 2 lines with one student
            table.cell_change(page, "0_0"   ,line, the_id)
            table.cell_change(page, "0_1"   ,line, firstname.encode('utf-8'))
            table.cell_change(page, "0_2"   ,line, surname.encode('utf-8'))

            if lines and lines[0][1][fire].value == '':
                #  FiRe only setted if empty, it must never change
                table.cell_change(page, "FiRe"  ,line, pe)
            table.cell_change(page, contrat ,line, s)

        finally:
            table.unlock()

    students_to_remove = [the_id
                          for the_id in table.logins()
                          if utilities.the_login(the_id) not in done]
    _ucbl_.remove_students_from_table(table, students_to_remove)

def check(table, update_inscrits=update_inscrits_referents):
    _ucbl_.check(table, update_inscrits)
    
cell_change = _ucbl_.cell_change
