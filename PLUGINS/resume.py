#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
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

import plugin
import utilities
import configuration
import document
import column
import TEMPLATES._ucbl_

class Stat(object):
    def __init__(self, login):
        self.login = login
        self.tables = {}

def resume(server):
    """Resume"""
    server.the_file.write(document.table_head(server.year,
                                              server.semester,
                                              server.ticket.ticket,
                                              create_pref = False,
#                                              comment=repr(server.the_path),
                                              default_sort_column=2,
                                              user_name=server.ticket.user_name
                                              ) +
                          TEMPLATES._ucbl_.update_student_information +
         "<script>document.write(head_html()); insert_middle();</script>")
                          
    logins = {}
    columns = [
        column.Column('c0', '', freezed='F', position=0, title='ID'),
        column.Column('c1', '', freezed='F', position=1, title='Prénom'),
        column.Column('c2', '', freezed='F', position=2, title='Nom'),
        ]
    i = 4
    for table in server.the_path:
        t = document.table(server.year, server.semester, table, None, None,
                           create=False, ro=True)
        if t == None:
            continue
        columns.append(column.Column('c%d' % i, '',
                                     position=i,
                                     title=table,
                                     weight='+1',
                                     ttype="Note",
                                     test='[0;NaN]',
                                     empty_is=0,
                                     comment='Nombre de cellules saisies',
                                     ))
        i += 1
        for line in t.lines.values():
            login = line[0].value
            if login == '':
                continue
            if login not in logins:
                logins[login] = s = Stat(login)
                s.surname = line[1].value
                s.name = line[2].value
            logins[login].tables[table] = (
                len([cell for cell in line[6:]
                     if cell.value != '' and cell.value != 'ABINJ']),
                )
    columns.append(
        column.Column('c3', '', position=2, title='TOTAL',
                      weight='1 ' + ' '.join([c.title for c in columns[3:]]),
                      ttype="Moy",
                      test='[0;NaN]',
                      )
        )


    lines_id = '[' + ','.join(['"l%d"' % i for i in range(len(logins))]) + ']'

    lines = []
    for stat in logins.values():
        lines.append('[C(' + utilities.js(stat.login)
                     + '),C(' + utilities.js(stat.surname)
                     + '),C(' + utilities.js(stat.name)
                     + '),' +
                     ','.join(['C(%s)' % stat.tables.get(col.title,('',))[0]
                      for col in columns[3:]])
                     + ',C()]')
    lines = '[' + ',\n'.join(lines) + ']'
    

    columns = '[' + ',\n'.join([col.js(hide=False) for col in columns]) + ']'
    
    server.the_file.write("""
    <script>
    lines_id = %s ;
    columns = %s ;
    lines = %s ;
    document.write(tail_html()) ;

    change_teachers([]) ;
    change_title(%s,2) ;
    change_mails({}) ;
    change_portails({}) ;
    runlog(columns, lines) ;
    </script>
    """ % (lines_id, columns, lines, utilities.js(repr(server.the_path)) ))
    server.the_file.close()


plugin.Plugin('resume', '/resume/{*}',
              function=resume, teacher=True,
              keep_open = True,
              launch_thread = True)

