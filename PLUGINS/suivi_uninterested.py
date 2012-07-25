#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet)
#    Copyright (C) 2008-2012 Thierry EXCOFFIER, Universite Claude Bernard
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
import collections
import plugin
import document
import utilities
import referent
import tablestat
import inscrits
import configuration

def uninterested(server):
    """Display information about student and their referents and
    how student interact with TOMUSS and referents."""
    f = server.the_file
    students = {}
    for s in referent.the_students(server.year, server.semester):
        students[s] = 0
    students_ue = collections.defaultdict(dict)
    students_notes = collections.defaultdict(int)
    students_in_blocnote = {}
    us = configuration.university_semesters
    for t in referent.les_blocsnotes(utilities.university_year(server.year,
                                                               server.semester)
                                     ):
        try:
            data_cols = [t.columns.from_id(title).data_col
                         for title in ('RDV1','RDV2','JUR1',
                                       'RDV3','RDV4','JUR2')
                         ]
        except AttributeError:
            continue
        for line in t.lines.values():            
            students_in_blocnote[utilities.the_login(line[0].value)] = [
                line[data_col].value
                for data_col in data_cols
                ]

    log = open(os.path.join('LOGS', 'SUIVI%s' % server.the_port,
                            str(time.localtime()[0]) + '.connections'), 'r')
        
    for line in log:
        s = line.split(' ', 1)[-1].strip() # Not [1] because some garbage line
        if s in students:
            students[s] += 1
    for t in tablestat.les_ues(server.year, server.semester):
        coli = t.column_inscrit()
        if coli is None:
            continue
        
        final = []
        for column in t.columns:
            title = column.title.upper()
            if 'NOTE' in title:
                final.append(column.data_col)
        for line in t.lines.values():
            s = utilities.the_login(line[0].value)
            if s not in students:
                continue
            for cell in line[coli+1:]:
                if (cell.value and cell.value != 'ABINJ'
                    and cell.value != '0' and cell.value != 0
                    and cell.value != configuration.yes
                    and cell.value != configuration.no):
                    students_notes[s] += 1
            try:
                ue = t.ue.split('-')[1]
                if final:
                    students_ue[s][ue] = t.lines.line_compute_js(line)
                    for data_col in final:
                        students_ue[s][ue] += (
                            '<br>' + t.columns[data_col].title + ' : ' +
                            '<script>document.write(line[' +
                            str(data_col) + '].value_fixed());</script>')
                else:
                    students_ue[s][ue] = '?'
            except IndexError:
                pass

    log.close()

    k = list(students.keys())

    def compare(x, y):
        r = cmp(students_notes[x], students_notes[y])
        if r:
            return r
        r = cmp(students[x], students[y])
        if r:
            return r
        r = cmp(int(x in students_in_blocnote), int(y in students_in_blocnote))
        if r:
            return r
        if x not in students_in_blocnote:
            return 0
        return cmp(students_in_blocnote[x], students_in_blocnote[y])
        
    k.sort(compare)

    f.write('<html><title>%s</title><body>\n' % server._("LINK_uninterested"))
    f.write('<script src="/utilities.js"></script>\n')
    f.write('<script src="/types.js"></script>\n')
    f.write('<script src="/lib.js"></script>\n')
    f.write('<style>TABLE { border-spacing: 0px ;}</style>\n')
    f.write("<p>%s %d" % (server.semester, server.year))
    f.write("<p>%s" % server._("MSG_uninterested"))
    f.write('<table border>')
    f.write('<tr><td>%s<td>%s<td>%s<td>%s\n'
            % (server._("TITLE_table_attr_mail"),
               server._("TH_student"),
               server._("TH_suivi_student_nr_grades"),
               server._("TH_nr_visits"),
               ))
    f.write('<td>RDV 1<td>RDV 2<td>%s ' % server._("COL_TITLE_JUR1") + us[0]
            + '<td>RDV 3<td>RDV 4<td>%s ' % server._("COL_TITLE_JUR2") + us[1]
            + '<td>%s<td>UE 1<td>UE 2<td>UE 3<td>UE 4<td>UE 5</tr>\n' %
                server._("MSG_suivi_student_referent"),
            )
    for s in k:
        student_mail = inscrits.L_batch.mail(s)
        if student_mail == None:
            student_mail = '???'
        x = '<tr><td>' + student_mail + '</td><td>' + s + '</td><td>' + str(students_notes[s]) \
            + '</td><td>' + str(students[s])
        # XXX And the second semester ?
        bn = students_in_blocnote.get(s, ('', '', '', '', '', ''))
        bn = [ i + '&nbsp;' for i in bn]
        if utilities.manage_key('LOGINS', utilities.charte(s, server.year,
                                                           server.semester)):
            bn[2] += server._("MSG_suivi_student_contract_checked")

        referent_mail = inscrits.L_batch.mail(
            referent.referent(server.year, server.semester, s))
        if referent_mail == None:
            referent_mail = ''
        else:
            referent_mail = referent_mail.encode('utf-8')
        x += '<td>' + '</td><td>'.join(bn) + '</td><td>' + referent_mail + '</td>'
        for ue, note in students_ue[s].items():
            x += '<td>' + ue + note + '</td>'
        x += '</tr>\n'
        f.write(x)
    f.write('</table></body></html>')

plugin.Plugin('uninterested', '/uninterested', function=uninterested,root=True,
              launch_thread = True,
              link=plugin.Link(where="informations", html_class="verysafe",
                               url="javascript:go_suivi('uninterested')",
                               priority = 1100,
                   ),
              )






