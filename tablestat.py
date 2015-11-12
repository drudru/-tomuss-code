#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#    TOMUSS: The Online Multi User Simple Spreadsheet)
#    Copyright (C) 2008, 2009 Thierry EXCOFFIER, Universite Claude Bernard
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

import os
import time
from . import document
from . import configuration
from . import utilities

table_mtimes = {}

def les_ues(year, semester, true_file=False, all_files=False, ro=True):
    """true_file is for UE that link to another UE"""
    dirname = os.path.join(configuration.db,'Y'+ str(year),'S' + str(semester))
    for ue in utilities.python_files(dirname):
        if ue == 'abjs.py':
            continue
        if true_file and os.path.islink(os.path.join(dirname, ue)):
            continue
        if ue == 'undefined.py':
            continue
        filename = document.table_filename(str(year), str(semester), ue[:-3])
        mtime = os.path.getmtime(filename)
        last_mtime, official = table_mtimes.get(filename, (0, False))
        if not official and last_mtime == mtime:
            # The not official table has not be modified
            continue
        table = document.table(str(year), str(semester), ue[:-3], ro=ro)
        if not table:
            continue
        if all_files or table.official_ue:
            table_mtimes[filename] = (mtime, True)
            yield table
        else:
            table_mtimes[filename] = (mtime, False)
            table.unload()


def all_the_tables(directory=None):
    if directory == None:
        directory = configuration.db
    for ue in os.listdir(directory):
        name = os.path.join(directory, ue)
        if os.path.isdir(name):
            for i in all_the_tables(name):
                yield i
        else:
            if ue.endswith('.py'):
                if ue == '__init__.py' or ue == 'abjs.py':
                    continue
                if os.path.islink(os.path.join(directory, ue)):
                    continue
                name = directory.split(os.path.sep)
                year = name[-2]
                if year[0] != 'Y':
                    raise ValueError('Unexpected year directory name:' + year)
                year = year[1:]
                semester = name[-1]
                if semester[0] != 'S':
                    raise ValueError('Unexpected semester directory name:'
                                     + semester)
                semester = semester[1:]
                yield document.table(year, semester, ue[:-3], ro=True)

class TableStat(object):
    def __init__(self, name):
        self.name = name
        self.nr = 0
        self.nr_pages = 0
        self.nr_blocnote = 0
        self.nr_cols = 0
        self.nr_students = 0
        self.nr_comments = 0
        self.date_max = "0000MMJJDDHHMMSS"
        self.date_min = "9999MMJJDDHHMMSS"
        self.teachers = {}
        self.tables = {}
        self.nr_lines = 0
        self.nr_inscrits = 0
        self.nr_not_inscrits = 0
        self.group_and_seq = {}
        self.pages_per_table = {}

    def update(self, cell, blocnote=False, table=None):
        if cell.empty():
            return
        self.nr += 1
        self.teachers[cell.author] = True
        if table:
            try:
                self.tables[table] += 1
            except KeyError:
                self.tables[table] = 1
        if blocnote:
            self.nr_blocnote += 1
        if cell.date < self.date_min:
            self.date_min = cell.date
        if cell.date > self.date_max:
            self.date_max = cell.date
        if cell.comment:
            self.nr_comments += 1

    def date(self, d):
        return d[0:4] + '-' + d[4:6] + '-' + d[6:8] + ' ' + \
               d[8:10] + ':' + d[10:12] + '.' + d[12:]
      
        
    def __str__(self):
        return "<TR><TH>%s</TH><TD align=\"right\">%d</TD><TD>%s</TD><TD>%s</TD></TR>" % (
            self.name,
            self.nr,
            self.date(self.date_min),
            self.date(self.date_max),
            )

last_full_read_time = 0

def dir_mtime(year, semester):
    name = os.path.join(configuration.db, "Y%s" % year, "S" + semester)
    return os.path.getmtime(name)

def update_the_ues(year, semester):
    """Reread all thes ues"""
    global last_full_read_time
    if (tuple(configuration.year_semester) == (year, semester)
        or tuple(configuration.year_semester_next) == (year, semester)):
        dt = 60
    else:
        dt = 3600
    mtime = dir_mtime(year, semester)
    if configuration.regtest or mtime - last_full_read_time > dt:
        last_full_read_time = mtime
        # Force the generator to do its job to check new students or tables
        tuple(les_ues(year, semester, true_file=False))

def the_ues(year, semester, login):
    if not configuration.index_are_computed:
        update_the_ues(year, semester)
    login = utilities.the_login(login)
    tables = []
    if document.tables_of_student:
        student_tables = document.tables_of_student.get(login,[])
    else:
        table_list = document.update_index(login)
        if table_list is None:
            return ()
        student_tables = [document.table(*t, ro=True, create=False)
                          for t in set(table_list) # Remove duplicates
                          if t[0] == year and t[1] == semester
                          ]
        # Remove UE indexed but no more on disc
        student_tables = [t
                          for t in student_tables
                          if t
                          ]
        now = time.time()
        for t in student_tables:
            t.rtime = now
        return [t
                for t in student_tables
                if t.official_ue
                ]
    for ue in student_tables:
        tables.append(document.table(year, semester, ue, ro=True))
    return tables
