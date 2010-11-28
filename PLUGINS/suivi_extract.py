#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet)
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
import document
import utilities
import inscrits

# http://pundit.univ-lyon1.fr:8891/2009/Automne/extract/UE-INF1001L:TD1:TD4/UE-MAT1001L:Test_rentrée:CC2



def display(f, year, semester, path):
    # Create dict of all tables
    tables = []
    students = {}
    nr_cols = 0
    for what in path:
        what = what.split(':')
        tables.append(
            (document.table(year, semester, what[0], ro=True, create=False),
             nr_cols,
             what[1:]))
        nr_cols += len(what)-1
  
    # Create dict of all students, with the good number of columns
    for table, position, columns in tables:
        for line in table.lines.values():
            if line[0].value == '':
                continue
            login = utilities.the_login(line[0].value)
            if login not in students:
                students[login] = ['' for i in range(nr_cols)]

    # fill the student data
    for table, position, columns in tables:
        coli = table.column_inscrit()
        if coli is None:
            continue
        i = position
        for column_title in columns:
            column = table.columns.from_title(column_title)
            if column is None:
                f.write('Je ne trouve pas la colonne ' + column_title
                        + ' dans la table ' + table.ue + '\n')
                f.close()
                return
            data_col = column.data_col
            for line in table.lines.values():
                s = utilities.the_login(line[0].value)
                students[s][i] = (
                    table.lines.line_compute_js(line) +
                    '<script>document.write(line[' +
                    str(data_col) + '].value_fixed());</script>')
            i += 1

    # display
    f.write(document.the_head)
    f.write('<body><table class="colored"><thead>')

    f.write('<tr><th rowspan="2">ID')
    for table, position, columns in tables:
        f.write('<th>' + '<th>'.join([table.ue for column in columns]))
    f.write('</tr>')


    f.write('<tr>')
    for table, position, columns in tables:
        f.write('<th>' + '<th>'.join(['%s' % column for column in columns]))
    f.write('</tr>')



    f.write('</thead>')
    f.write('<tbody>')
    for student, values in students.items():
        f.write('<tr><td>' + inscrits.login_to_student_id(student) + '<td>' +
                '<td>'.join(values) + '</tr>\n')
    f.write('</tbody>')
    f.write('</table>')
    f.close()


def page(server):
    """Extract named columns from tables, display as an HTML table
             /extract/UE-XXXXX:Column1:Column2/UE-YYYY:ColumnX:ColumnY...
    """
    display(server.the_file, server.year, server.semester,
            server.the_path)

plugin.Plugin('suivi_extract', '/extract/{*}', function=page, teacher=True,
              launch_thread = True,
              )






def display_fusion(f, year, semester, path,
                   with_inscrit=False, with_author=False, with_column=True):
    # Create dict of all tables
    tables = []
    students = {}
    nr_cols = 0
    for what in path:
        what = what.split(':')
        table = document.table(year, semester, what[0], ro=True, create=False)
        if table is None:
            f.write('Je ne trouve pas la table ' + what[0])
            f.close()
            return
        coli = table.column_inscrit()
        if coli is None:
            continue
        if len(what) == 1:
            what = [column.title for column in table.columns[coli+1:]]
         
        tables.append( (table, what[1:]))
  
    # Create dict of all students
    for table, columns in tables:
        for line in table.lines.values():
            if line[0].value == '':
                continue
            login = utilities.the_login(line[0].value)
            if login not in students:
                students[login] = []

    # fill the student data
    for table, columns in tables:
        column_inscrit = table.column_inscrit()
        
        for line in table.lines.values():
            if line[0].value == '':
                continue
            v = '<td>' + table.ue
            if with_inscrit:
                v += '<td>' + line[column_inscrit].value
            students[utilities.the_login(line[0].value)].append(v)

        for column_title in columns:
            column = table.columns.from_title(column_title)
            if column is None:
                f.write('Je ne trouve pas la colonne ' + column_title
                        + ' dans la table ' + table.ue + '\n')
                f.close()
                return
            data_col = column.data_col
            for line in table.lines.values():
                if line[0].value == '':
                    continue
                s = utilities.the_login(line[0].value)
                v = '<td>' + str(line[data_col].value)
                if with_column:
                    v += '<td>' + column_title
                if with_author:
                    v += '<td>' + line[data_col].author
                students[s].append(v)
    # display
    f.write(document.the_head)
    f.write('<body>')
    for table, columns in tables:
        f.write(table.ue + ' ' + repr(columns) + '<br>')
    f.write('<table class="colored">')
    f.write('<tbody>')
    for student, values in students.items():
        firstname, surname = inscrits.firstname_and_surname(student)
        f.write('<tr><td>' + inscrits.login_to_student_id(student)
                + '<td>' + firstname.encode('utf8')
                + '<td>' + surname.encode('utf8')
                + ''.join(values) + '</tr>\n')
    f.write('</tbody>')
    f.write('</table>')
    f.close()


def fusion(server):
    """Fusion of named columns from tables, display as an HTML table
             /fusion/UE-INF2011L:a/UE-INF2012L:
    """
    display_fusion(server.the_file, server.year, server.semester,
            server.the_path)
    
def fusion_inscrit_author(server):
    """Fusion of named columns from tables, display as an HTML table
             /fusion_inscrit_author/UE-INF2011L:a/UE-INF2012L:
    """
    display_fusion(server.the_file, server.year, server.semester,
                   server.the_path,
                   with_inscrit=True, with_author=True, with_column=False)

plugin.Plugin('suivi_fusion_inscrit_author', '/fusion_inscrit_author/{*}',
              function=fusion_inscrit_author, teacher=True,
              launch_thread = True,
              )





