#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#    Copyright (C) 2017 Thierry EXCOFFIER, Universite Claude Bernard
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
#    Contact: Thierry.EXCOFFIER@univ-lyon1.fr

"""
The argument is the list of referent logins.

The mails about the 7 last day ABINJ are sent to these referents.

"""


import time
import locale
import sys
import tomuss_init
from .. import referent
from .. import document
from .. import utilities
from .. import configuration
from .. import inscrits

def students(teachers):
    s = set()
    for login in teachers:
        s.update(referent.students_of_a_teacher(login))
    return s

def ues(students):
    s = set()
    for login in students:
        for year, semester, ue in document.update_index(
                utilities.the_login(login)):
            if (year, semester) == configuration.year_semester:
                s.add(ue)
    return s

def nice_date(txt):
    return time.strftime("%c", time.strptime(txt, "%Y%m%d%H%M%S"))

def message(teacher, all_students, since):
    messages = []
    for login in referent.students_of_a_teacher(teacher):
        if len(all_students[login]) == 0:
            continue
        fn, sn, mail = inscrits.L_batch.firstname_and_surname_and_mail(login)
        messages.append(login + ' ' + fn.title() + ' ' + sn + ' ' + mail)
        for col, cell in all_students[login]:
            messages.append('    ' + col.table.ue + ' ' + col.table.table_title)
            if len(messages) >= 3 and messages[-1] == messages[-3]:
                messages.pop()
            t = ('        ' + nice_date(cell.date)
                 + '«' + col.title + '» «' + cell.author)
            if cell.comment:
                t += '» «' + cell.comment
            t += '»'
            messages.append(t)
        messages.append('')
    if messages:
        mail = [inscrits.L_batch.mail(teacher), configuration.maintainer]
        utilities.send_mail(to = mail,
                            subject = "TOMUSS " + configuration.abi
                            + '(' + teacher + ')',
                            message =
                            nice_date(since) + ' >>>> ' + time.strftime("%c")
                            + '\n\n\n' + '\n'.join(messages),
                            frome = configuration.maintainer,
                            show_to = True)
    
class Stat:
    students = {}
    def __init__(self, teachers, since):
        self.teachers = teachers
        self.students = {login: [] for login in students(teachers)}
        self.since = since
    def analyse(self, ue):
        ue = document.table(configuration.year_semester[0],
                            configuration.year_semester[1],
                            ue)
        for line in ue.lines.values():
            if line[0].value not in self.students:
                continue
            for col, cell in zip(ue.columns, line):
                if cell.value == configuration.abi and cell.date > self.since:
                    self.students[line[0].value].append((col, cell))
    def analyse_all(self):
        for ue in ues(self.students):
            self.analyse(ue)
        locale.setlocale(locale.LC_TIME,
                         configuration.language + '_'
                         + configuration.language.upper() + '.utf8')
        for teacher in self.teachers:
            message(teacher, self.students, self.since)

last_week = time.strftime("%Y%m%d%H%M%S",
                          time.localtime(time.time() - 7 * 86400))

Stat(sys.argv[1:], last_week).analyse_all()
