#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2010 Thierry EXCOFFIER, Universite Claude Bernard
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

import plugin
import utilities
import referent
import configuration
import inscrits
import os

import files
files.files['types.js'].append(
    'referent_get',
    utilities.read_file(os.path.join('PLUGINS', 'referent_get.js')))

def referent_get_a_student(server, login, students, student,
                           allow_referent_change=True):
    year, semester = configuration.year_semester
    student = inscrits.login_to_student_id(student)
    firstname, surname = inscrits.L_fast.firstname_and_surname(student)

    if firstname == 'Inconnu' and surname == 'Inconnu':
        server.the_file.write("%s%s\n" % (
                student, server._("MSG_referent_get_not_a_student")))
    elif student in students:
        server.the_file.write("%s%s\n" % (
                    student, server._("MSG_referent_get_yet_yours")))
    else:
        old_referent = referent.referent(year, semester,
                                         utilities.the_login(student))
        if old_referent:
            if allow_referent_change:
                referent.remove_student_from_referent(old_referent, student)
            else:
                server.the_file.write('%s%s\n' % (
                        student, server._("MSG_referent_get_yet_referent")))
                return
        referent.add_student_to_referent(login, student)

        server.the_file.write('%s : %s %s\n' % (
            student, firstname.encode('utf8'), surname.encode('utf8')))

def referent_get(server):
    """Add a student to its refered students"""
    login = utilities.the_login(server.ticket.user_name)
    students = referent.students_of_a_teacher(login)

    server.the_file.write("%s\n" % server._("MSG_referent_get_done"))

    for student in server.the_path:
        if student == '':
            continue
        referent_get_a_student(server, login, students, student)

plugin.Plugin('referent_get', '/referent_get/{*}',
              mimetype = 'text/plain; charset=UTF-8',
              function=referent_get, referent=True)


def referent_set(server):
    """Add a student to a referent :
            ...../referent_set/user.name/student1/student2/...
    """
    login = utilities.the_login(server.the_path[0])
    students = referent.students_of_a_teacher(login)

    server.the_file.write(server._("MSG_referent_get_set_done") %
                          login + "\n")

    for student in server.the_path[1:]:
        if student == '':
            continue
        referent_get_a_student(server, login, students, student,
                               allow_referent_change=False)


plugin.Plugin('referent_set', '/referent_set/{*}',
              mimetype = 'text/plain; charset=UTF-8',
              link=plugin.Link(html_class="verysafe", where="referents",
                               url="javascript:go_referent_set()",
                               ),
              function=referent_set, root=True
              )


def orphan_students(server):
    """Remove the teacher of students"""

    year, semester = configuration.year_semester

    for student in server.the_path:
        if student == '':
            continue
        teacher = referent.referent(year, semester, student)
        if teacher is None:
            server.the_file.write(server._("MSG_referent_get_orphan_none") % student
                                  + "\n")
            continue
        referent.remove_student_from_referent(teacher, student)
        server.the_file.write(student + server._("MSG_referent_get_orphan_quit")
                              + teacher + '\n')

plugin.Plugin('orphan_students', '/orphan_students/{*}',
              mimetype = 'text/plain; charset=UTF-8',
              link=plugin.Link(html_class="safe", where="referents",
                               url="javascript:go_orphan_students()",
                               ),
              function=orphan_students, root=True
              )


