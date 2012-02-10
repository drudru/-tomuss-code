#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2009-2011 Thierry EXCOFFIER, Universite Claude Bernard
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

import abj
import inscrits
import data
import time
from utilities import js, warn, start_new_thread_immortal
import utilities
import configuration
import os

update_student_information = """

function update_student_information(line)
{
update_student_information_default(line) ;
update_value_and_tip(t_student_id, line[0].value) ;
var n = line[1].value.toString() ;
update_value_and_tip(t_student_firstname,
                     n.substr(0,1) + n.substr(1).toLowerCase()) ;
update_value_and_tip(t_student_surname, line[2].value) ;
}
"""

def line_empty(line):
    for cell in line:
        if cell.value != '' and cell.author != data.ro_user:
            return False
    return True

def get_mails(table, the_ids):

    if not configuration.regtest:
        # Fast version
        for x in inscrits.L_batch.query_logins(list(table.logins())
                                               + table.authors(),
                                               (configuration.attr_login,
                                                configuration.attr_mail, )):
            if x[1]:
                login = inscrits.login_to_student_id(x[0].lower()).encode('utf-8')
                the_ids[login] = x[1].encode('utf-8')

    else:
        for login in list(table.logins()) + table.authors():
            if login not in the_ids:
                mail = inscrits.L_batch.mail(login)
                if mail:
                    print login, mail
                    the_ids[login] = mail
                else:
                    warn("No mail for " + login, what="check")



def create(table):
    p = table.new_page('',data.ro_user,'','')
    table.column_change (p, '0_0', 'ID'     , 'Text', '', '', 'F', 0, 4)
    table.column_comment(p, '0_0', "Numéro d'étudiant")
    table.column_change (p, '0_1', 'Prénom' , 'Text', '', '', 'F', 0, 8)
    table.column_change (p, '0_2', 'Nom'    , 'Text', '', '', 'F', 0, 8)
    table.column_change (p, '0_3', 'Grp'    , 'Text', '', '', '' , 0, 2)
    table.column_comment(p, '0_3', "Groupe de TD")
    table.column_change (p, '0_4', 'Seq'    , 'Text', '', '', '' , 0, 1)
    table.column_comment(p, '0_4', "Séquence de l'enseignement")
    table.column_change (p, '0_5', 'Inscrit', 'Text', '', '', 'C', 1, 1)
    table.column_comment(p, '0_5', "IP valide ?")
    if table.ue.startswith('SP-'):
        table.column_change (p, '0_6', 'UE', 'Text', '', '', '', 0, 4)
        table.column_comment(p, '0_6', "UE d'origine de l'étudiant")
        table.column_change (p, '0_7', 'Horaire', 'Text', '', '', '', 0, 5)
        table.column_comment(p, '0_7', "Horaire de l'enseignement")
        table.column_change (p, '0_8', 'Information', 'Text', '', '', '', 0, 6)
        table.column_comment(p, '0_8', "Informations complémentaires")
        table.column_change (p, '0_9', 'Note_Semestre_Avant_Jury',
                             'Note', '[0;20]','1','',0, 3)
        table.column_comment(p, '0_9', "Note de l'UE")
        table.column_change (p, '0_10', 'Remarques',
                             'Text', '[0;20]','1','',0, 8)
        table.column_comment(p, '0_10', "Commentaire de l'enseignant")

    if table.ue.startswith('TS-'):
        table.table_attr(p, 'default_nr_columns', 9)
        table.column_change (p, '0_6', 'UE', 'Text', '', '', '', 0, 4)
        table.column_comment(p, '0_6', "UE d'origine de l'étudiant")
        table.column_change (p, '0_7', 'Horaire', 'Text', '', '', '', 0, 5)
        table.column_comment(p, '0_7', "Horaire de l'enseignement")
        table.column_change (p, '0_8', 'Note_Semestre_Avant_Jury',
                             'Note', '[0;20]','1','',0, 3)
        table.column_comment(p, '0_8', "Note de l'UE")
        table.column_change (p, '0_9', 'Remarques',
                             'Text', '[0;20]','1','',0, 8)
        table.column_comment(p, '0_9', "Commentaire de l'enseignant")

        
    ts = configuration.semester_span(table.year, table.semester)
    if ts:
        table.date_change(p, ts)

def student_add_allowed(table, new_list=None):
    warn('%s allow_student_removal %s' % (
        table.ue, configuration.allow_student_removal), what="table")
    if not configuration.allow_student_removal:
        # We don't allow to add students if there is too many
        # to remove.
        if new_list is None:
            new_list = list(inscrits.L_batch.students(table.ue_code))
        
        nr_yet = 0
        for student in new_list:
            if list(table.get_lines(student[0])):
                nr_yet += 1
        nr_to_delete = len(table.the_keys()) - nr_yet
        warn("%s: %d delete on %d, %d new" % (
            table.ue, nr_to_delete, len(table.the_keys()),
            len(new_list) - nr_yet),what="table")
        if nr_to_delete == 0:
            return True
        if nr_to_delete / float(len(table.the_keys())) > 0.15: # XXX : constant
            if configuration.year_semester == (table.year, table.semester):
                utilities.manage_key('CLOSED', table.ue, separation=5,
                                     content='%d/%s' % (table.year,
                                                        table.semester)
                                     )
            return False
    return True


def update_inscrits_ue(the_ids, table, page):
    if len(table.columns) < 6: # Stat table
        return
    
    table.with_inscrits = table.columns[5].title == 'Inscrit' and not table.is_extended

    warn("Update inscrit list of " + table.ue, what="check")

    new_list = list(inscrits.L_batch.students(table.ue_code))

    warn("Update inscrit list of " + table.ue + ' DONE', what="check")

    if student_add_allowed(table, new_list):
        warn("Update inscrit students", what="check")
        for infos in new_list:
            update_student(table, page, the_ids, infos)
    if table.with_inscrits:
        warn("Update info list for student without name", what="check")
        for line_id, line in table.lines.items():
            if (line[1].value == '' or line[2].value == '') and line[0].value.strip():
                get_info.append( (table, line_id, table.pages[0],
                                  line[0].value) )
    terminate_update(table, the_ids, page)

def check(table, update_inscrits=update_inscrits_ue):
    the_ids = {}

    warn("Update student list", what="check")
    if (configuration.allow_student_list_update
        or update_inscrits != update_inscrits_ue
        ) and table.modifiable and table.update_inscrits:
        page = table.pages[0]
        warn("Update inscrits", what="check")
        update_inscrits(the_ids, table, page)
        
    warn("Update mail list", what="check")
    get_mails(table, the_ids)
    warn("Change mail list", what="check")
    table.change_mails(the_ids)

    # PORTAILS
    warn("Update portail list", what="check")
    portails = {}
    for login in list(the_ids.keys()):
        portails[login] = [i.encode('latin1')
                           for i in inscrits.L_batch.portail(login)]
    warn("Change portails", what="check")
    table.change_portails(portails)
    warn("Update done", what="check")
    
def the_abjs(table):
    students = table.abjs.students
    grp_col = table.columns.get_grp()
    seq_col = table.columns.get_seq()
    t = []
    for login in table.logins():
        tt = abj.tierstemps(login)
        if login in students:
            student = students[login]
            line = list(table.get_lines(login))
            if line:
                line = line[0]
                the_abjs= abj.do_prune(student.abjs,
                                       table.dates[0], table.dates[1]+86400,
                                       line[grp_col].value,line[seq_col].value,
                                       table.ue)
            else:
                the_abjs = ()
            da = student.da
        else:
            the_abjs = []
            da = []
        if tt or the_abjs or da:
            t.append("%s:[[%s],[%s],%s]" % (
                js(login),
                ','.join(['[%s,%s,%s]'
                          %(js(a),js(b),js(d)) for a,b,c,d in the_abjs]),
                ','.join(['[%s,%s,%s]'
                          %(js(a),js(b),js(d)) for a,b,c,d in da]),
                js(tt.encode('utf-8'))))

    return 'change_abjs({%s});\n' % ',\n'.join(t)

def update_student(table, page, the_ids, infos):
    the_id, firstname, surname, mail, grp, seq = infos[:6]
    if the_id in the_ids:
        return
    # time.sleep(1) # XXX
    if mail:
        the_ids[the_id] = mail
    else:
        the_ids[the_id] = the_id
    table.lock()
    try:
        for i in range(len(table.columns), len(infos)):
            if i == 6:
                title = 'Quoi'
            elif i == 7:
                title = 'Quand'
            else:
                title = ''
            table.column_change (table.pages[0],
                                 '0_%d'%i, title, 'Text', '', '', '', 0, 6)
        
        for key, x in table.get_items(the_id):
            # do not erase user provided information
            if ((grp != '' or x[3].author == data.ro_user)
                and (configuration.allow_student_removal
                     or x[3].value == '')):
                table.cell_change(page, "0_3", key, grp)
            if ((seq != '' or x[4].author == data.ro_user)
                and (configuration.allow_student_removal
                     or x[4].value == '')):
                table.cell_change(page, "0_4", key, seq)
            for col, val in enumerate(infos[6:]):
                if ((val != '' or x[col+6].author == data.ro_user)
                    and (configuration.allow_student_removal
                         or x[col+6].value == '')):
                    table.cell_change(page, "0_%d" % (col+6), key, val)
            if table.with_inscrits:
                table.cell_change(page, "0_1", key, firstname)
                table.cell_change(page, "0_2", key, surname)
            break
        else: # The FOR does not found the student
            lin = '0_' + str(len(table.lines))
            table.cell_change(page, "0_0", lin, the_id)
            table.cell_change(page, "0_1", lin, firstname)
            table.cell_change(page, "0_2", lin, surname)
            if grp != '':
                table.cell_change(page, "0_3", lin, grp)
            if seq != '':
                table.cell_change(page, "0_4", lin, seq)
            for col, val in enumerate(infos[6:]):
                if val != '':
                    table.cell_change(page, "0_%d" % (col+6), lin, val)
                    
    finally:
        table.unlock()

def rw_page(table):
    """Not thread safe"""
    for page in table.pages:
        if page.user_name == data.rw_user:
            return page        
    return table.new_page('',data.rw_user,'','')

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
                and utilities.the_login(line[0].value) not in students):
                if inscrit_column:
                    table.cell_change(table.pages[0], inscrit_column, line_id,
                                      'ok')
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
                                      'non')
                for i, column in enumerate(table.columns):
                    if (line[i].value and line[i].author == data.ro_user
                        and i != inscrit_column):
                        if p == None:
                            p = rw_page(table)
                        table.cell_change(p, column.the_id, line_id)
    finally:
        table.unlock()

def terminate_update(table, the_ids, page):
    if table.with_inscrits:
        allow_student_removal = configuration.allow_student_removal
        grp_col = table.columns.get_grp()
        to_remove = [line_id
                     for line_id, line in table.lines.items()
                     if line[0].value not in the_ids
                         and line[grp_col].value != 'FERMEE'
                     ]
        # Do not remove if there is more than :
        #     10% removal (>=20 lines)
        #     50% removal (<20 lines)
        # Or if there is less than 12 students
        if len(table.lines) >= 20:
            if len(to_remove) > 1+len(table.lines)/10:
                allow_student_removal = False
        else:
            if len(to_remove) >= 1+len(table.lines)/2:
                allow_student_removal = False
        
        p = None
        warn("Lock", what="check")
        table.lock()
        warn("Locked", what="check")
        try:
            students_to_remove = set()
            for line_id, line in table.lines.items():
                if line[0].value in the_ids \
                       or not table.official_ue \
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

    if table.abjs.mtime != table.abjs_mtime:
        table.abjs_mtime = table.abjs.mtime
        table.send_update(None, '<script>' + the_abjs(table) + '</script>')

    warn("Done", what="check")

# Get Firstname and surname when id is given.

get_info = []
thread_started = False

def cell_change(table, page, col, lin, value, date):
    if page.page_id == 0:
        return
    if col != '0_0':
        return
    get_info.append((table, lin, page, value))

def init(table):
    # Hack to not initialize table in a locked state : We use a thread.
    global thread_started
    if not thread_started:
        thread_started = True
        start_new_thread_immortal(check_get_info, ())
        
    table.official_ue = configuration.is_an_official_ue(table.ue_code)
    table.update_inscrits = table.modifiable

def check_get_info():
    """Update the name, surname, mail, portail from ID"""
    import configuration
    if configuration.regtest:
        time.sleep(999999)
    while True:
        time.sleep(0.1)
        while len(get_info):
            table, lin, page, value = get_info.pop()
            line = table.lines[lin]
            if value == '':
                firstname, surname, mail = '', '', ''
            else:
                firstname, surname, mail = inscrits.L_batch.firstname_and_surname_and_mail(
                value)
                
            firstname = firstname.encode('utf8')
            line = table.lines[lin]
            # DO NOT USE the user page (use pages[0])
            # BECAUSE IT BREAKS THE NUMBER OF REQUESTS
            # It loose value on tomuss reboot.

            table.lock()
            try:
                if value or line[1].author == data.ro_user:
                    table.cell_change(table.pages[0], '0_1', lin, firstname,
                                      force_update=True)
                if value or line[2].author == data.ro_user:
                    surname = surname.encode('utf8')
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
            table.update_mail(line[0].value, mail.encode('utf8'))

            portails = [i.encode('latin1') for i in inscrits.L_batch.portail(value)]
            table.update_portail(line[0].value, portails)
