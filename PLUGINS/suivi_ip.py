#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet)
#    Copyright (C) 2009 Thierry EXCOFFIER, Universite Claude Bernard
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

from .. import plugin
from .. import tablestat
from .. import inscrits

def the_ip(server):
    """For each student, display the tables where he's present"""
    students = {}
    for t in tablestat.les_ues(server.year, server.semester, true_file=True):
        if not t.ue.startswith('UE-') and not t.ue.startswith('EC-'):
            if not hasattr(t, "rtime"):
                t.unload()
            continue
        ue = t.ue[3:]
        column_inscrit = t.column_inscrit()
        for line in t.lines.values():
            login = inscrits.login_to_student_id(line[0].value)
            if login == '':
                continue
            if login not in students:
                students[login] = []
            # Number of non empty cell
            i = 0
            if column_inscrit != None:
                if line[column_inscrit].value.startswith('ok'):
                    i = -1000
            
            nr = len([x for x in line[6:] if x.value != ''])
            students[login].append((nr+i,ue))
        if not hasattr(t, "rtime"):
            t.unload()

    for student in students:
        students[student].sort()
        students[student].reverse()
        # students[student] = [ue for nr, ue in students[student]]
        
        
    server.the_file.write(repr(students).replace('],', '],\n'))

plugin.Plugin('ip', '/ip', function=the_ip, group='roots',
              launch_thread = True,
              mimetype = "text/plain; charset=utf-8",
              link=plugin.Link(where="deprecated", html_class="verysafe",
                               url="javascript:go_suivi('ip')"),
              )
