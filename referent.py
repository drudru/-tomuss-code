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
    f.write('<h1>Get the student list for UEs</h1>\n')
    students = {}
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
# discipline (dict or set), ues (list), licence, licence_first_year
def analyse_groups(student, groups):
    # Update list of the UE of the student
    for ue in groups:            
        if ue.startswith(configuration.ou_ue_starts):
            student.ues.append(ue[6:].split(' ')[0])

class Student(object):
    def __init__(self, v, portail):
        self.key = v[0]
        self.firstname = v[1]
        self.surname = v[2]
        self.mail = v[3]
        self.portail = portail
        self.primo_entrant = self.key[1:3] == '%2d' % (
            utilities.university_year() - 2000)

        # Get the portail of the student
        self.short_portail = ''
        for k, value in configuration.the_portails.items():
            if portail in value:
                self.short_portail = k
                break

        self.discipline = {}
        self.ues = []
        self.licence = False
        self.licence_first_year = False

        # This function compute exact values for discipline, ues, licence...
        analyse_groups(self, v[4])

    def __str__(self):
        return '%s %s %s %s %s %s' % (self.key, self.firstname, self.surname,
                                   self.mail, self.ues, self.discipline.keys())

    def html(self):
        if self.mail is None:
            self.mail = inscrits.L_batch.mail(self.key)
        return '%s %s %s %s %s %s' % (self.key,
                                   self.firstname, self.surname,self.mail, 
                                   self.ues, self.discipline.keys())

class Teacher(object):
    def __init__(self, name, discipline, line_key):
        self.name = name
        self.no_more_students = discipline.endswith('*')
        discipline = discipline.replace('*', '')
        self.discipline = discipline
            
        self.line_key = line_key
        self.students = []
        self.nr = 0
        self.message = []

    def append(self, student):
        self.students.append(student)
        self.nr += 1

    def __str__(self):
        return '%s %s (%f) %s' % (self.name, self.discipline, self.nr,
                                  self.students)


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

def nr_students(year, semester):
    """Number of student of a 'referent'"""
    n = 0
    for line in referents_students(year, semester).lines.values():
        if line[0].value == '':
            continue
        n -= 1
        for cell in line:
            if cell.value != '':
                n += 1
    return n

def remove_student_from_referent(referent, student):
    table = referents_students()
    line_key, line = tuple(table.get_items(referent))[0]
    student = inscrits.login_to_student_id(student)
    for cell, column in zip(line, table.columns):
        if cell.value == student:
            table.lock()
            try:
                table.cell_change(table.pages[1], column.the_id, line_key, '')
            finally:
                table.unlock()
            break

def add_column(table):
    table.lock()
    try:
        i = len(table.columns) - 2
        table.column_change(table.pages[1],'%d'%i,str(i+1),'Text','','','',0,4)
    finally:
        table.unlock()


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
    if 'INFL3' in student.discipline and student.primo_entrant:
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
        and all_teachers[k].discipline in student.discipline:
        return all_teachers[k]

    # The teacher is in the same discipline with the less students.
    
    for tteacher in sorted_teachers:
        if tteacher.discipline not in student.discipline :
            if False:
                f.write('<li> %s[%d] et %s pas la bonne discipline\n' % (
                    tteacher.name, tteacher.nr, student.key))
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

def update_referents(ticket, f, really_do_it = False):

    if not is_a_referent_master(ticket.user_name):
        f.write("You are not allowed to do this")
        f.close()
        return

    # Get the referent table
    table = referents_students()
    table.lock()
    try:
        page = table.new_page(ticket.ticket, ticket.user_name, ticket.user_ip,
                      ticket.user_browser)
    finally:
        table.unlock()

    f.write('''
    <link rel="stylesheet" href="../hidden.css" type="text/css">
    <script src="../utilities.js"></script>
    <script>display_tips = true;</script>
    ''')

    f.write('<h1>' + configuration.year_semester[1] + ' '
            + str(configuration.year_semester[0]) + '</h1>\n')
    f.write(table.filename + '\n')

    if not table.modifiable:
        f.write('<p>Modification interdite (problème de date ?)\n')
        return

    students = student_list(f, port(), not_in())

    f.write('<h1>%d students</h1>\n' % len(students))

    f.write('<h1>Remove multiple instances of students or teachers</h1>\n')
    all_cells = {}
    all_teachers = {}

    table.lock()
    try:
        for line_key, line in table.lines.items():
            if line[0].value and line[0].value not in all_teachers:
                tteacher = Teacher(line[0].value, line[1].value, line_key)
                if tteacher.discipline != '' and tteacher.discipline[-1]!= '*':
                    all_teachers[line[0].value] = tteacher
            else:
                if line[0].value:
                    f.write('Remove teacher: %s<br>\n' % line[0].value)
                    if really_do_it:
                        table.cell_change(page, 'a', line_key, '')
                        table.cell_change(page, 'b', line_key, '')
                tteacher = None

            for cell_key, cell in zip(table.columns, line)[2:]:
                if cell.value == '':
                    continue
                cell_key = cell_key.the_id
                if tteacher == None:
                    f.write('Student without teacher: %s<br>\n' % cell.value)
                    if really_do_it:
                        table.cell_change(page, cell_key , line_key, '')
                    continue
                if cell.value not in all_cells:
                    all_cells[cell.value] = tteacher
                    if cell.value not in students:
                        f.write('%s not in the student list (%s) ' % (
                        cell.value, line[0].value))
                        f.write('REMOVED')
                        the_student = utilities.the_login(cell.value)
                        if really_do_it:
                            table.cell_change(page, cell_key, line_key, '')
                            utilities.manage_key('LOGINS',
                                                 os.path.join(the_student,
                                                              'old_referent'),
                                                 content=line[0].value)
                        tteacher.message.append(u'Enlève étudiant : %s %s' %
                                                (the_student,
                                                ' '.join(inscrits.L_slow.firstname_and_surname_and_mail(the_student))))
                        f.write('<br>\n')
                    else:
                        tteacher.append(cell.value)
                else:
                    f.write('Remove duplicate student: %s<br>\n' % cell.value)
                    if really_do_it:
                        table.cell_change(page, cell_key, line_key, '')
    finally:
        table.unlock()

    f.write('<h1>Students in need of a teacher</h1>\n')
    missing = []
    i = 0
    for student in students.values():
        if student_need_a_referent(student, all_cells, f):
            missing.append(student.key)
            f.write(student.html() + '<br>\n')


    f.write('<h1>Teacher list sorted by number of student</h1>\n')
    sorted_teachers = list(all_teachers.values())
    sorted_teachers.sort(key=lambda x: x.nr)
    for tteacher in sorted_teachers:
        f.write('<li>' + str(tteacher))


    f.write('<h1>Affectations</h1>\n')
    while missing:
        sorted_teachers.sort(key=lambda x: x.nr)
        s = missing[0]

        tteacher = search_best_teacher(students[s], sorted_teachers, f, all_teachers)
        if tteacher == None:
            f.write('<li> MANQUE ENSEIGNANT!!!!!!!!!! pour %s\n' %
                    students[s])
            missing.remove(s)
            continue
        ss = s
        ss += ' ' + repr(students[s].discipline.keys())

        f.write('<li><b>' + tteacher.name + '[' + str(tteacher.nr) + ']</b> (%s): '
                % (tteacher.discipline,) + ss)
        tteacher.append(s)
        tteacher.message.append(u'Ajoute étudiant : %s' % students[s].html())
        if really_do_it:
            add_student_to_this_line(table,
                                     tteacher.line_key,
                                     table.lines[tteacher.line_key],
                                     s)

        # Remove student from lists
        missing.remove(s)

    f.write('<h1>Résume</h1>\n')
    for tteacher in sorted_teachers:
        if not tteacher.message:
            continue
        f.write('<li> %s<br>\n' % tteacher.name
                + '<br>\n'.join(tteacher.message).encode('utf8'))

        if really_do_it:
            utilities.send_mail(inscrits.L_batch.mail(tteacher.name),
                                "Changements d'etudiants referes",
                                (u"""Bonjour

La liste de vos étudiants référés vient de changer automatiquement.

* Un étudiant est considéré comme faisant la licence FST
  s'il suit une UE de la licence FST.
  C'est le seul critère permettant de ne pas oublier les étudiants
  qui viennent de Médecine, IUT...

* Un étudiant n'ayant pas fait son IP n'as de référent.

* Quand un étudiant revient, son ancien référent lui est affecté si possible.

Voici la liste des changements :

%s

La liste à jour est celle indiquée sur http://TOMUSS.univ-lyon1.fr

Amicalement.

""" % '\n'.join(tteacher.message)).encode('latin1'), frome=configuration.root[0])

        
        
