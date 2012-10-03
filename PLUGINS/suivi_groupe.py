#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2010-2011 Thierry EXCOFFIER, Universite Claude Bernard
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

"""
"""

import itertools
import time
import csv
from .. import plugin
from .. import tablestat
from .. import data
from .. import document

debug = False

def page_groupe(server):
    """List all the students groups defined by the teacher and not by TOMUSS"""
    
    for t in tablestat.les_ues(server.year, server.semester):
        col_inscrit = t.column_inscrit()
        if col_inscrit is None:
            continue
        if t.ue_code != t.ue or not t.official_ue:
            continue

        g = []
        for line in t.lines.values():
            if line[col_inscrit].value != 'ok' and not debug:
                continue
            if line[3].author == data.ro_user:
                # This is an official group affectation
                continue
            if line[3].value == '':
                continue
            if line[4].value == '':
                # Not an official : there is no sequence
                continue
            g.append((t.ue, line[4].value, line[0].value,
                      line[3].value, line[3].author))

        # SPlit by UE/Sequence
        g.sort()
        for key, i in itertools.groupby(g, lambda x: x[:2]):
            s = ''
            for j in i:
                s += '\t%s %s %s<br>\n' % (j[2], j[3], j[4])
            server.the_file.write(
                '%s(%s) ' % key
                + '<a href="groupe/%s(%s).csv">CSV</a><br>\n' % (t.ue, j[1])
                + s)


def page_one_groupe(server):
    """Group affectation for one table"""

    ue = server.the_path[0].split('(')[0]
    seq = server.the_path[0].split('(')[1].split(')')[0]

    t = document.table(server.year, server.semester, ue, ro=True)

    col_inscrit = t.column_inscrit()
    if col_inscrit is None:
        return
    if t.ue_code != t.ue or not t.official_ue:
        return

    w = csv.writer(server.the_file, delimiter=';')
    date = time.strftime('%d/%m/%Y', time.localtime())

    w.writerow((server._("MSG_suivi_group_date")    , '', date         , ''))
    w.writerow((server._("MSG_suivi_group_table")   , '', t.ue[3:]     , ''))
    w.writerow((server._("MSG_suivi_group_title")   , '', t.table_title, ''))
    w.writerow((server._("MSG_suivi_group_sequence"), '', seq          , ''))
    w.writerow((server._("MSG_suivi_group_id"),
                server._("MSG_suivi_group_surname"),
                server._("MSG_suivi_group_firstname"),
                server._("MSG_suivi_group_group")))
          
    for line in t.lines.values():
        if line[col_inscrit].value != 'ok' and not debug:
            continue
        if line[3].author == data.ro_user:
            # This is an official group affectation
            continue
        if line[3].value == '':
            continue
        if line[4].value == '':
            # Not an official : there is no sequence
            continue
        if line[4].value != seq:
            continue

        w.writerow((line[0].value, '', '', line[3].value))
    w.writerow((line[0].value, '', '', line[3].value))

plugin.Plugin('groupe', '/groupe', group='abj_masters',
              mimetype = 'text/html',
              function = page_groupe,
              launch_thread=True,
              link=plugin.Link(where="grouping", html_class="verysafe",
                               url="javascript:go_suivi('groupe')",
                               ),
              )

plugin.Plugin('one_groupe', '/groupe/{*}',
              group='staff',
              mimetype = 'text/csv',
              function = page_one_groupe,
              launch_thread=True
              )
