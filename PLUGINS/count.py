#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2009-2012 Thierry EXCOFFIER, Universite Claude Bernard
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

import collections
import time
from .. import plugin
from .. import document
from .. import column
from .. import plugins
from .. import cell

class Stat(object):
    def __init__(self, login):
        self.login = login
        self.nb = collections.defaultdict(int)

def count(server):
    """count the number of cells with the given value
    used in the given tables per weeks.
    The week date must be indicated in the column course date.
    It may be used to compute the number of ABINJ per week for a set of UE.

    http://127.0.0.1:SUIVI_PORT_NUMBER/count/ABINJ/UE-INF1001L/UE-INF1002L

    """
    logins = {}
    columns = [
        column.Column('c0', '', freezed='F', position=0, title='ID'),
        column.Column('c1', '', freezed='F', position=1, title='Prénom'),
        column.Column('c2', '', freezed='F', position=2, title='Nom'),
        ]
    weeks = collections.defaultdict(int)
    parse =  column.ColumnAttr.attrs['course_dates'].parse
    what = server.the_path[0]
    for table in server.the_path[1:]:
        t = document.table(server.year, server.semester, table, None, None,
                           create=False, ro=True)
        if t == None:
            continue
        for data_col, a_column in enumerate(t.columns):
            try:
                dates = parse(a_column.course_dates)
            except AttributeError:
                dates = ()

            if dates:
                # XXX Assumes that all the dates are on the same week
                date = dates[0]

                # Monday date
                date = time.localtime(time.mktime(date) - date[6] * 86400)
                date = time.strftime('%Y-%m-%d_%B', date)
            else:
                date = '??/??/????'
                
            for line in t.lines.values():
                login = line[0].value
                if not login:
                    continue
                if login not in logins:
                    logins[login] = s = Stat(login)
                    s.surname = line[1].value
                    s.name = line[2].value
                value = line[data_col].value
                if value == '':
                    value = a_column.empty_is
                if value == what:
                    logins[login].nb[date] += 1
                    if logins[login].nb[date] > weeks[date]:
                        weeks[date] += 1

    i = 4

    for title in sorted(weeks):
        columns.append(column.Column('c%d' % i, '',
                                     position=i,
                                     title=title,
                                     weight='+1',
                                     type="Note",
                                     minmax='[0;%d]' % weeks[title],
                                     empty_is='0',
                                     rounding='1',
                                     comment=server._("B_Nmbr")
                                     + ' ' + what,
                                     ))
        i += 1
        
    columns.append(
        column.Column('c3', '', position=2, title=server._("COL_TITLE_TOTAL"),
                      type="Moy",                      
                      weight='1',
                      columns=' '.join([c.title for c in columns[3:]]),
                      rounding='1',
                      minmax='[0;NaN]',
                      )
        )
    # XXX Really not nice.
    # Why the 'type' attribute does not work like the others ?
    columns[-1].type = plugins.types['Moy']

    lines = []
    for stat in logins.values():
        lines.append(cell.Line(
                [
                    cell.CellValue(stat.login),
                    cell.CellValue(stat.surname),
                    cell.CellValue(stat.name)
                    ] +
                [cell.CellValue(stat.nb[col.title])
                 for col in columns[3:]])
                     )
    document.virtual_table(server, columns, lines,
                           { 'default_sort_column': 2 }
                           )


plugin.Plugin('count', '/count/{*}',
              function=count, group='staff',
              launch_thread = True, unsafe=False)

