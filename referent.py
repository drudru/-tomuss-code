#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet)
#    Copyright (C) 2008-2011 Thierry EXCOFFIER, Universite Claude Bernard
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

import inscrits
import document
import utilities
import os
import teacher
import configuration

#REDEFINE
# List of LDAP OU of student to be affected to a 'referent'
def port():
    return configuration.the_portails['UFRFST'] 

#REDEFINE
# List of LDAP OU of student not to be affected to a 'referent'
def not_in():
    return ()
           
#REDEFINE
# Return True if the student need a referent teacher
def need_a_referent(login):
    """To be redefined"""
    return True

#REDEFINE
# Return True if the student must sign an interactive document
def need_a_charte(login):
    return False

#REDEFINE
# Compute the student list needing a referent
def student_list(f, pportails, not_in_list):
    f.write('<h1>' + utilities._("TITLE_referent_student_list") + '</h1>\n')
    students = {}
    print pportails
    for portail in pportails:
        f.write('<h2>' + portail + '</h2>')
        f.flush()
        for sstudent in inscrits.L_batch.member_of(portail):
            f.write(sstudent[0])
            for p in sstudent[4]:
                if p in not_in_list:
                    break
            else:
                # Not in any forbidden list
                f.write(' ')
                f.flush()
                s = Student(sstudent, portail=portail)
                if not s.licence:
                    f.write('(!L) ')
                    continue
                if len(s.ues) == 0: # Aucune IP !!!!
                    f.write('(!IP) ')
                    # XXX continue
                students[sstudent[0]] = s
                continue
            f.write('(L3) ')

    return students

def les_blocsnotes(year):
    dirname = os.path.join(configuration.db, 'Y' + str(year), 'SReferents')
    if not os.path.exists(dirname):
        return

    for ue in utilities.python_files(dirname):
        if ue == 'abjs.py':
            continue
        ue = utilities.login_to_module(ue[:-3])
        yield document.table(str(year), 'Referents', ue, ro=True)

#REDEFINE
# This function computes for the student some attributes needed to
# assign it a referent teacher.
# Attributes are :
# discipline (set), ues (list), licence, licence_first_year
def analyse_groups(student, groups):
    # Update list of the UE of the student
    for ue in groups:            
        if ue.startswith(configuration.ou_ue_starts):
            student.ues.append(ue[6:].split(' ')[0])

class Student(object):
    def __init__(self, v, portail):
        self.key = v[0]
        self.firstname = unicode(v[1], 'utf8')
        self.surname = unicode(v[2], 'utf8')
        self.mail = unicode(v[3], 'utf8')
        self.portail = portail
        self.primo_entrant = self.key[1:3] == '%2d' % (
            utilities.university_year() - 2000)

        # Get the portail of the student
        self.short_portail = ''
        for k, value in configuration.the_portails.items():
            if portail in value:
                self.short_portail = k
                break

        self.discipline = set()
        self.ues = []
        self.licence = False
        self.licence_first_year = False

        # This function compute exact values for discipline, ues, licence...
        analyse_groups(self, v[4])

    def __str__(self):
        return '%s %s %s %s %s %s' % (self.key, self.firstname, self.surname,
                                   self.mail, self.ues, self.discipline)

    def html(self):
        if self.mail is None:
            self.mail = inscrits.L_batch.mail(self.key)
        return '%s %s %s %s %s %s' % (self.key,
                                   self.firstname, self.surname,self.mail, 
                                   self.ues, self.discipline)

class Teacher(object):
    def __init__(self, name, discipline, line_key):
        self.name = name
        self.no_more_students = '*' in discipline
        discipline = discipline.replace('*', '')
        self.discipline = set(discipline.split(' '))
            
        self.line_key = line_key
        self.students = []
        self.nr = 0
        self.nr_weight = 0
        self.message = []

    def append(self, student):
        self.students.append(student)
        if student.startswith('111'): # XXX Primo entrant
            self.nr_weight += 4
        else:
            self.nr_weight += 1
        self.nr += 1
        if 'MATH' in self.discipline:
            self.nr_weight += 0.1


    def __str__(self):
        return '%s %s (%f) %s' % (self.name, ' '.join(self.discipline),
                                  self.nr, self.students)


def students_of_a_teacher(tteacher):
    for line in referents_students().lines.values():
        if line[0].value == tteacher:
            s = []
            for cell in line[2:]:
                if cell.value:
                    s.append(cell.value)
            return s
    return []

def portail_of_a_teacher(tteacher):
    for line in referents_students().get_lines(tteacher):
        return line[1].value
    return ''

def is_a_referent_master(name):
    # Get the referent table    
    try:
        table = referents_students()
    except ImportError:
        return False

    return name in table.masters


def referent(year, semester, login):
    """Returns the 'referent' of a student."""
    login = utilities.the_login(login)
    for line in referents_students(year, semester).lines.values():
        for cell in line[2:]:
            if utilities.the_login(cell.value) == login:
                return line[0].value
    return None
    
def referents_login(year, semester):
    """Returns the referent list"""
    return [t for t in referents_students(year, semester).logins() if t != '']

def the_students(year, semester):
    """The list of student WITH a 'referent'"""
    students = []
    for line in referents_students(year, semester).lines.values():
        if line[0].value == '':
            continue
        for cell in line[2:]:
            if cell.value != '':
                students.append(cell.value)
    return students

def nr_students(year, semester):
    """Number of student with of 'referent'"""
    return len(the_students(year, semester))

#REDEFINE
# Triggered when a student is removed from a teacher
def remove_student_from_referent_hook(referent, student_id):
    return

def remove_student_from_referent(referent, student):
    table = referents_students()
    line_key, line = tuple(table.get_items(referent))[0]
    student = inscrits.login_to_student_id(student)
    for cell, column in zip(line, table.columns):
        if cell.value == student:
            table.lock()
            try:
                table.cell_change(table.pages[0], column.the_id, line_key, '')
            finally:
                table.unlock()
                remove_student_from_referent_hook(referent, student)
            break

def add_column(table):
    table.lock()
    try:
        i = len(table.columns) - 2
        table.column_change(table.pages[1],'%d'%i,str(i+1),'Text','','','',0,4)
    finally:
        table.unlock()


#REDEFINE
# Triggered when a student is added to a teacher
def add_student_to_referent_hook(referent, student_id):
    return

def add_student_to_this_line(table, line_key, line, student):
    student = inscrits.login_to_student_id(student)
    for cell, column in zip(line, table.columns)[2:]:
        if cell.value == '':
            table.lock()
            try:
                table.cell_change(table.pages[1], column.the_id, line_key,
                                  student)
            finally:
                table.unlock()
                add_student_to_referent_hook(line[0].value, student)
            break
    else:
        add_column(table)
        add_student_to_this_line(table, line_key, line, student)


def add_student_to_referent(referent, student):
    table = referents_students()
    line_key, line = tuple(table.get_items(referent))[0]
    add_student_to_this_line(table, line_key, line, student)


#REDEFINE
# This function returns the teacher to assign to a student.
# It is only needed for special case of the generic algorithm.
def search_best_teacher_local(student, sorted_teachers, f, all_teachers):
    if 'INFO_L3' in student.discipline and student.primo_entrant:
        return all_teachers['elodie.desseree']

def search_best_teacher(student, sorted_teachers, f, all_teachers):        
    """Search the teacher of a student"""

    tteacher = search_best_teacher_local(student, sorted_teachers,
                                         f, all_teachers)
    if tteacher:
        return tteacher

    # If an old referent is possible.

    k = utilities.manage_key('LOGINS',
                             os.path.join(utilities.the_login(student.key),
                                          'old_referent'))
    if k:
        k = k.strip() # \n at the end if hand edited
    if k in all_teachers \
        and all_teachers[k].discipline.intersection(student.discipline):
        return all_teachers[k]

    # The teacher is in the same discipline with the less students.
    
    for tteacher in sorted_teachers:
        if not tteacher.discipline.intersection(student.discipline) :
            continue

        # No new students for this teacher
        if tteacher.no_more_students:
            continue
        # OK for this teacher.
        return tteacher
    return None

#REDEFINE
# Returns True if the student need a referent.
# This function can heavely modify 'all_cells' and other data
# to make some adjustement.
def student_need_a_referent(student, all_cells, debug_file):
    return True

def referents_students(year=None, semester=None):
    if year is None:
        year, semester = configuration.year_semester
    return document.table(year, semester, 'referents_students',
                          do_not_unload=1, ro=configuration.read_only)

def update_referents(ticket, f, really_do_it = False, add_students=True):

    if not is_a_referent_master(ticket.user_name):
        f.write("You are not allowed to do this")
        f.close()
        return

    # Get the referent table
    table = referents_students()
    page = table.pages[0]
    # table.lock()
    # try:
    #    page = table.new_page(ticket.ticket, ticket.user_name, ticket.user_ip,
    #                          ticket.user_browser)
    # finally:
    #    table.unlock()
    f.write('''
    <link rel="stylesheet" href="../style.css" type="text/css">
    <script src="../utilities.js"></script>
    <script>display_tips = true;</script>
    ''')

    f.write('<h1>' + configuration.year_semester[1] + ' '
            + str(configuration.year_semester[0]) + '</h1>\n')
    f.write(table.filename + '\n')

    if not table.modifiable:
        f.write('<p>%s\n' % utilities._("MSG_referent_unmodifiable"))
        return

    students = student_list(f, port(), not_in())

    f.write('<h1>' + utilities._("TITLE_referent_nr_students") % len(students)
            + '</h1>\n')

    f.write('<h1>%s</h1>\n' % utilities._("TITLE_referent_remove_duplicates"))
    all_cells = {}
    all_teachers = {}

    table.lock()
    try:
        etapes_of_students = inscrits.L_batch.etapes_of_students(
            table.logins())
        for line_key, line in table.lines.items():
            if line[0].value and line[0].value not in all_teachers:
                tteacher = Teacher(line[0].value, line[1].value, line_key)
                if tteacher.discipline and not tteacher.no_more_students:
                    all_teachers[line[0].value] = tteacher
            else:
                if line[0].value:
                    f.write('%s%s<br>\n' % (
                            utilities._("MSG_referent_remove_teacher"),
                            line[0].value))
                    if really_do_it:
                        table.cell_change(page, 'a', line_key, '')
                        table.cell_change(page, 'b', line_key, '')
                tteacher = None

            for cell_key, cell in zip(table.columns, line)[2:]:
                if cell.value == '':
                    continue
                cell_key = cell_key.the_id
                if tteacher == None:
                    f.write('%s%s<br>\n' % (
                            utilities._("MSG_referent_orphan_student"),
                            cell.value))
                    if really_do_it:
                        table.cell_change(page, cell_key , line_key, '')
                    continue
                if cell.value not in all_cells:
                    all_cells[cell.value] = tteacher
                    if cell.value not in students:
                        f.write(utilities._("MSG_referent_student_not_in_list")
                                % (cell.value, line[0].value,
                                   etapes_of_students.get(cell.value, ())
                                   ))
                        f.write(utilities._("MSG_referent_student_removed"))
                        the_student = utilities.the_login(cell.value)
                        if really_do_it:
                            remove_student_from_referent_hook(line[0].value,
                                                              cell.value)
                            table.cell_change(page, cell_key, line_key, '')
                            utilities.manage_key('LOGINS',
                                                 os.path.join(the_student,
                                                              'old_referent'),
                                                 content=line[0].value)
                        tteacher.message.append(
                            utilities.__("MSG_referent_remove_student") +
                            '%s %s' % (the_student,
                                       ' '.join(inscrits.L_slow.firstname_and_surname_and_mail(the_student))))
                        f.write('<br>\n')
                    else:
                        tteacher.append(cell.value)
                else:
                    f.write(utilities._("MSG_referent_remove_duplicate_student")
                            + '%s<br>\n' % cell.value)
                    if really_do_it:
                        remove_student_from_referent_hook(line[0].value,
                                                          cell.value)
                        table.cell_change(page, cell_key, line_key, '')

    finally:
        table.unlock()

    f.write('<h1>%s</h1>\n' % utilities._("TITLE_referent_students_in_need"))
    missing = []
    if add_students:
        for student in students.values():
            if student_need_a_referent(student, all_cells, f):
                missing.append(student.key)
                f.write(student.html().encode('utf8') + '<br>\n')

    f.write('<h1>%s</h1>\n' % utilities._("TITLE_referent_teacher_list"))
    sorted_teachers = list(all_teachers.values())
    sorted_teachers.sort(key=lambda x: x.nr_weight)
    for tteacher in sorted_teachers:
        f.write('<li>' + str(tteacher))


    f.write('<h1>%s</h1>\n' % utilities._("TITLE_referent_affectations"))
    while missing:
        sorted_teachers.sort(key=lambda x: x.nr_weight)
        s = missing[0]

        tteacher = search_best_teacher(students[s], sorted_teachers, f, all_teachers)
        if tteacher == None:
            f.write('<li> ' + utilities._("MSG_referent_no_teacher") %
                    students[s].html().encode('utf8') + '\n')
            missing.remove(s)
            continue
        ss = s
        ss += ' ' + repr(students[s].discipline)

        f.write('<li><b>' + tteacher.name + '[' + str(tteacher.nr) + ']</b> (%s): '
                % (tteacher.discipline,) + ss)
        tteacher.append(s)
        tteacher.message.append(utilities.__("MSG_referent_add_student")
                                % students[s].html())
        if really_do_it:
            add_student_to_this_line(table,
                                     tteacher.line_key,
                                     table.lines[tteacher.line_key],
                                     s)

        # Remove student from lists
        missing.remove(s)

    f.write('<h1>%s</h1>\n' % utilities._("TITLE_referent_resume"))
    my_mail = inscrits.L_slow.mail(ticket.user_name)
    for tteacher in sorted_teachers:
        if not tteacher.message:
            continue
        f.write('<li> %s<br>\n' % tteacher.name
                + '<br>\n'.join(tteacher.message).encode('utf8'))

        if really_do_it:
            utilities.send_mail(inscrits.L_batch.mail(tteacher.name),
                                utilities.__("MSG_referent_mail_subject"),
                                utilities.__("MSG_referent_mail_body") %
                                ('\n'.join(tteacher.message),
                                 configuration.configuration.server_url),
                                frome=my_mail)

        
        
