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
import files

def referent_get(server):
    """Add a student to its refered students"""
    login = utilities.the_login(server.ticket.user_name)
    student = inscrits.login_to_student_id(server.something)

    students = referent.students_of_a_teacher(login)
    if student not in students:
        old_referent = referent.referent(configuration.year_semester[0],
                                         configuration.year_semester[1],
                                         utilities.the_login(student))
        if old_referent:
            referent.remove_student_from_referent(old_referent, student)

        referent.add_student_to_referent(login, student)

    server.the_file.write("Vous êtes maintenant le référent pédagogique de cet étudiant.")


plugin.Plugin('referent_get', '/referent_get/{?}',
              mimetype = 'text/plain',
              function=referent_get, referent=True)


