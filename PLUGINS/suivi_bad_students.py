#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2008 Thierry EXCOFFIER, Universite Claude Bernard
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
from tablestat import les_ues
import utilities
import configuration

def bad_student_with_notes(f, year, semester, _):
    f.write('<title>' + _("TITLE_suivi_bad_student") + '</title>\n')
    f.write('<h1>' + _("TITLE_suivi_bad_student") + '</h1>\n')
    f.write('<table><tr><th>'
            + _("TH_table"           )         + '<th>'
            + _("COL_TITLE_ID"       )         + '<th>'
            + _("COL_TITLE_firstname")         + '<th>'
            + _("COL_TITLE_surname"  )         + '<th>'
            + _("TH_suivi_bad_student_values") + '</tr>\n')
    nr = 0
    for t in les_ues(year, semester, true_file=True):
        coli = t.column_inscrit()
        if coli is None:
            continue
        for line in t.lines.values():
            nr += 1
            if line[coli].value != 'non':
                continue
            s = []
            for cell in line[coli+1:]:
                if (cell.value
                    and cell.value != configuration.abi
                    and cell.value != '0'
                    and cell.value != 0
                    and cell.value != configuration.yes
                    and cell.value != configuration.no):
                    s.append(cell.value)
            if len(s) == 0:
                continue
                
            f.write('<tr><th>' + t.ue + '<td>'
                    + utilities.the_login(line[0].value) + '<td>'
                    + line[1].value + '<td>' + line[2].value + '<td>'
                    + repr(s) + '</tr>\n')
    f.write('</table>')

def bad(server):
    """Display the list of student attending courses
    but not officialy registered"""
    bad_student_with_notes(server.the_file, server.year, server.semester,
                           server._)

plugin.Plugin('bad_ip', '/*1', abj_master=True,
              function = bad,
              launch_thread = True,
              link=plugin.Link(url="javascript:go_suivi('*1')",
                               where="abj_master", html_class="verysafe",
                               priority=100),
              )
