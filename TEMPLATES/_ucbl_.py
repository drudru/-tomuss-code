#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2009-2013 Thierry EXCOFFIER, Universite Claude Bernard
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

import re
from .. import inscrits
from .. import data
from ..utilities import warn
from .. import utilities
from .. import configuration

removal_allowed = 0.15

update_student_information = """

function update_student_information(line)
{
update_student_information_default(line) ;
update_value_and_tip(t_student_id, line[0].value) ;
var n = line[1].value.toString() ;
update_value_and_tip(t_student_firstname, title_case(n)) ;
update_value_and_tip(t_student_surname, line[2].value) ;
}
"""

def line_empty(line):
    for cell in line:
        if (cell.value != ''
            and cell.author != data.ro_user
            and cell.author != data.no_user
            and cell.author != data.rw_user
            ):
            return False
    return True

columns = {
    '0_0': {'type': 'Text', 'freezed': 'F', 'width': 4, 'repetition': 1}, # ID
    '0_1': {'type': 'Text', 'freezed': 'F', 'width': 8}, # Firstname
    '0_2': {'type': 'Text', 'freezed': 'F', 'width': 8}, # Surname
    '0_3': {'type': 'Text', 'width': 2},                 # Group
    '0_4': {'type': 'Text', 'width': 1},                 # Sequence
    '0_5': {'type': 'Text', 'freezed': 'C', 'hidden': 1, 'title': 'Inscrit',
            'comment': "IP valid ?"}, # Invisible column : line HTML class
    }

def create(table):
    p = table.get_ro_page()
    cols = dict(columns) # Copy the standard columns
    cols.update(configuration.local_columns(table)) # Append your local columns

    # Translate titles and comments using columns keys and prefixes COL_TITLE…
    _ = utilities._
    for k, v in cols.items():
        if 'title' not in v:
            key = "COL_TITLE_" + k
            title = _(key)
            if key != title:
                v['title'] = title
        if 'comment' not in v:
            key = "COL_COMMENT_" + k
            comment = _(key)
            if key != comment:
                v['comment'] = comment
    table.update_columns(cols)
    ts = configuration.semester_span(table.year, table.semester)
    if ts:
        if re.search(configuration.ue_not_per_semester, table.ue_code):
            # XXX Assume there only one semester extension
            # So we take the start of the first semester and the end of the
            # second one
            year, semester = utilities.university_year_semester(
                year=table.year, semester=table.semester)
            ts = configuration.semester_span(year, semester)
            year2, semester2 = utilities.next_year_semester(year, semester)
            ts2 = configuration.semester_span(year2, semester2)
            table.date_change(p, ts.split(' ')[0] + ' ' + ts2.split(' ')[1])
        else:
            table.date_change(p, ts)

def student_add_allowed(table):
    """Returns the new student list or False if there is to many
    students to remove"""
    
    warn('%s allow_student_removal %s' % (
        table.ue, configuration.allow_student_removal), what="table")

    # Check if it is an old 'students' method
    new_list = list(table.retrieve_student_list())
    
    old_list = set(table.logins_valid())
    nr_to_delete = len( old_list
                        - set(x[0] for x in new_list) )
    if nr_to_delete == 0:
        return new_list
    if nr_to_delete / float(len(old_list)) > removal_allowed:
        if (configuration.year_semester == (table.year, table.semester)
            and configuration.year_semester != configuration.year_semester_next
            ):
            utilities.manage_key('CLOSED', table.ue, separation=5,
                                 content='%d/%s' % (table.year,
                                                    table.semester)
                                 )
        return False
    return new_list


def update_inscrits_ue(the_ids, table, page):
    if len(table.columns) < 6: # Stat table
        return
    
    table.with_inscrits = table.columns[5].title == 'Inscrit' and not table.is_extended

    warn("Update inscrit list of " + table.ue, what="check")

    new_list = student_add_allowed(table)

    warn("Update inscrit list of " + table.ue + ' DONE', what="check")

    if new_list:
        warn("Update inscrit students", what="check")
        for infos in new_list:
            update_student(table, page, the_ids, infos)
    if table.with_inscrits:
        warn("Update info list for student without name", what="check")
        for line_id, line in table.lines.items():
            if (line[1].value == '' or line[2].value == '') and line[0].value.strip():
                get_info.append( (table, line_id, table.pages[0],
                                  line[0].value) )
    terminate_update(table, the_ids)

def check(table, update_inscrits=update_inscrits_ue):
    the_ids = {}

    warn("Update student list", what="check")
    if (configuration.allow_student_list_update
        or update_inscrits != update_inscrits_ue
        ) and table.modifiable and table.update_inscrits:
        page = table.pages[0]
        warn("Update inscrits", what="check")
        update_inscrits(the_ids, table, page)
        
    # PORTAILS
    warn("Update portail list", what="check")
    if False:
        # The old slow method
        portails = {}
        for login in list(the_ids.keys()):
            portails[login] = [i.encode('latin1')
                               for i in inscrits.L_batch.portail(login)]
    else:
        portails = {}
        for login, p in inscrits.L_batch.portails(the_ids.keys()).items():
            portails[inscrits.login_to_student_id(login)] = [
                i.encode("latin-1")
                for i in p]
    warn("Change portails", what="check")
    table.change_portails(portails)
    # Take mails from student list and not the user database
    mails = dict(table.mails)
    mails.update(the_ids)
    table.change_mails(mails)
    warn("Update done", what="check")

def update_student(table, page, the_ids, infos):
    the_id, firstname, surname, mail, grp, seq = infos[:6]
    if the_id in the_ids:
        return
    if mail:
        the_ids[the_id] = mail
    else:
        the_ids[the_id] = the_id
    table.lock()
    try:
        for i in range(len(table.columns), len(infos)):
            # Should be in LOCAL directory
            if i == 6:
                title = 'Quoi'
            elif i == 7:
                title = 'Quand'
            else:
                title = ''
            table.column_change (table.pages[0],
                                 "0_%d" % i,
                                 title, 'Text', '', '', '', 0, 6)
        if configuration.grp_modifiable:
            grp_page = table.get_nobody_page()
        else:
            grp_page = page

        for key, x in table.get_items(the_id):
            # do not erase user provided information
            if ((grp != '' or x[3].author == data.ro_user)
                and configuration.allow_student_removal
                and (x[3].value == '' or x[3].author == data.ro_user)):
                if x[3].value == '':
                    table.cell_change(grp_page, "0_3", key, grp)
                else:
                    table.cell_change(page, "0_3", key, grp)
            if ((seq != '' or x[4].author == data.ro_user)
                and configuration.allow_student_removal
                and (x[4].value == '' or x[4].author == data.ro_user)):
                table.cell_change(page, "0_4", key, seq)
            for col, val in enumerate(infos[6:]):
                if ((val != '' or x[col+6].author == data.ro_user)
                    and (configuration.allow_student_removal
                         or x[col+6].value == '')):
                    table.cell_change(page,
                                      table.columns[col+6].the_id, key, val)
            if table.with_inscrits:
                if firstname:
                    table.cell_change(page, "0_1", key, firstname)
                if surname:
                    table.cell_change(page, "0_2", key, surname)
            break
        else: # The FOR does not found the student
            lin = '0_' + str(len(table.lines))
            table.cell_change(page, "0_0", lin, the_id)
            if firstname:
                table.cell_change(page, "0_1", lin, firstname)
            if surname:
                table.cell_change(page, "0_2", lin, surname)
            if grp != '':
                table.cell_change(grp_page, "0_3", lin, grp)
            if seq != '':
                table.cell_change(page, "0_4", lin, seq)
            for col, val in enumerate(infos[6:]):
                if val != '':
                    table.cell_change(page,
                                      table.columns[col+6].the_id, lin, val)
                    
    finally:
        table.unlock()

def remove_students_from_table(table, students):
    """If the line is 'empty' then it is erased.
    If it contains user information, ro_user cells are given to rw_user
    so any user can erase the line manualy"""

    data_col = table.column_inscrit()
    if data_col:
        inscrit_column = table.columns[data_col].the_id
    else:
        inscrit_column = None
    p = None

    table.lock()
    try:
        for line_id, line in table.lines.items():
            if (inscrits.login_to_student_id(line[0].value) not in students
                and utilities.the_login(line[0].value) not in students
                and line[0].value != ''
                ):
                if inscrit_column:
                    v = configuration.student_inscrit_value(table, line)
                    if v:
                        v = ' ' + v
                    table.cell_change(table.pages[0], inscrit_column, line_id,
                                      'ok' + v)
                continue
            if line_empty(line):
                # Clear the line
                for i, column in enumerate(table.columns):
                    if line[i].value:
                        table.cell_change(table.pages[0],
                                          column.the_id, line_id, '')
            else:
                if inscrit_column:
                    table.cell_change(table.pages[0], inscrit_column, line_id,
                                      'non', change_author=False)
                for i, column in enumerate(table.columns):
                    if (line[i].value and line[i].author == data.ro_user
                        and i != data_col):
                        if p == None:
                            p = table.get_rw_page()
                        table.cell_change(p, column.the_id, line_id)
    finally:
        table.unlock()

def terminate_update(table, the_ids):
    if table.with_inscrits:
        allow_student_removal = configuration.allow_student_removal
        grp_col = table.columns.get_grp()
        if grp_col is None:
            grp_col = 0
        to_remove = [line_id
                     for line_id, line in table.lines.items()
                     if line[0].value not in the_ids
                         and line[grp_col].value != 'FERMEE'
                     ]
        # Do not remove if there is more than :
        #     15% removal (>=20 lines)
        #     50% removal (<20 lines)
        # Or if there is less than 12 students
        if len(table.lines) >= 20:
            if len(to_remove) > 1+len(table.lines)*removal_allowed:
                allow_student_removal = False
        else:
            if len(to_remove) >= 1+len(table.lines)/2:
                allow_student_removal = False
        
        table.lock()
        try:
            students_to_remove = set()
            for line_id, line in table.lines.items():
                if line[0].value in the_ids \
                       or inscrits.login_to_student_id(line[0].value) in the_ids:
                    # Student is fine
                    continue
                if not allow_student_removal:
                    continue
                if line[0].value:
                    students_to_remove.add(line[0].value)
        finally:
            table.unlock()

        if allow_student_removal:
            remove_students_from_table(table, students_to_remove)

    warn("Done", what="check")

# Get Firstname and surname when id is given.

get_info = []

def cell_change(table, page, col, lin, value, date):
    if page.page_id == 0:
        return
    # Call a locally defined cell update hook.
    configuration.cell_change(table, page, col, lin, value, date)
    if col != '0_0':
        return
    get_info.append((table, lin, page, value))
    # In 1 seconds update name and surname in a new thread.
    # Only one thread do this job.
    utilities.start_job(check_get_info, 1)

def init(table):
    table.official_ue = configuration.is_an_official_ue(table.ue_code)
    table.update_inscrits = table.modifiable

def check_get_info():
    """Update the name, surname, portail from ID"""
    if configuration.regtest:
        return

    check_get_info.safe_to_check = False
    while get_info:
        check_get_info.safe_to_check = True
        table, lin, dummy_page, value = get_info.pop()
        line = table.lines[lin]
        if value == '':
            firstname, surname = '', ''
        else:
            firstname, surname = inscrits.L_batch.firstname_and_surname(
                value)

        firstname = firstname.encode('utf-8')
        line = table.lines[lin]

        if table.unloaded:
            # The information took so long to get that the table
            # was unloaded, so it can't be stored.
            # To not pollute the backtrace logs, we do not
            # try to store the value.
            check_get_info.safe_to_check = False
            continue

        # DO NOT USE the user page (use pages[0])
        # BECAUSE IT BREAKS THE NUMBER OF REQUESTS
        # It loose value on tomuss reboot.

        table.lock()
        try:
            if value or line[1].author == data.ro_user:
                table.cell_change(table.pages[0], '0_1', lin, firstname,
                                  force_update=True)
            if value or line[2].author == data.ro_user:
                surname = surname.encode('utf-8')
                table.cell_change(table.pages[0], '0_2', lin, surname,
                                  force_update=True)

            if value or line[3].author == data.ro_user:
                table.cell_change(table.pages[0], '0_3', lin, '',
                                  force_update=True)
            if value or line[4].author == data.ro_user:
                table.cell_change(table.pages[0], '0_4', lin, '',
                                  force_update=True)
        finally:
            table.unlock()

        portails = [i.encode('latin-1') for i in inscrits.L_batch.portail(value)]
        table.update_portail(line[0].value, portails)
        check_get_info.safe_to_check = False
