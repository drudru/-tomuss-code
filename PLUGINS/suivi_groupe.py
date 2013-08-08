#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2010-2013 Thierry EXCOFFIER, Universite Claude Bernard
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
from .. import configuration
from .. import utilities

debug = False

def get_lines(table, col_inscrit, seq=None):
    for line in table.lines.values():
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
        if seq is not None and line[4].value != seq:
            continue
        yield line

def page_groupe(server):
    """List all the students groups defined by the teacher and not by TOMUSS"""
    server.the_file.write(
        str(document.the_head)
        + '''
<script>
function display(s)
{
document.getElementById('x').innerHTML = s ;
}
</script>
<div id="x" style="position:fixed;right:0;top:0;border:1px solid black;background:white;font-size:70%%"></div>
<table class="colored">
<tr><th>%s<th>TOMUSS<th>%s<th><th>%s</tr>
''' % (
            server._("LABEL_tablelinear_value_date"),
            server._('COL_TITLE_0_4'),
            server._('COL_TITLE_0_3'),
       ) )
    lines = []
    for t in tablestat.les_ues(server.year, server.semester):
        col_inscrit = t.column_inscrit()
        if col_inscrit is None:
            if not hasattr(t, "rtime"):
                t.unload()
            continue
        if t.ue_code != t.ue or not t.official_ue:
            if not hasattr(t, "rtime"):
                t.unload()
            continue

        g = []
        newest_date = '0'
        for line in get_lines(t, col_inscrit):
            g.append((t.ue, line[4].value, line[0].value,
                      line[3].value, line[3].author))
            s = line[3].date
            if s > newest_date:
                newest_date = s
        newest_date = (newest_date[:4] + '-'
                       + newest_date[4:6] + '-'
                       +  newest_date[6:8] )

        # SPlit by UE/Sequence
        g.sort()
        for key, i in itertools.groupby(g, lambda x: x[:2]):
            s = ''
            groups = set()
            for j in i:
                s += '\t%s %s %s<br>\n' % (j[2], j[3], j[4])
                groups.add(j[3])
                
            lines.append(
                '<tr><td>%s<td><a href="%s/=%s/%s/%s/%s">%s</a><td>%s<td><a href="groupe/%s(%s).csv" onmouseover="display(%s)">CSV</script></a><td>%s' % (
                    newest_date,
                    configuration.server_url,
                    server.ticket.ticket,
                    server.year, server.semester, t.ue,
                    key[0], key[1],
                    t.ue, j[1], utilities.js(s).replace('"',"'"),
                    ' '.join(groups)
                    ))
        if not hasattr(t, "rtime"):
            t.unload()
    server.the_file.write('\n'.join(sorted(lines, reverse=True)) + '</table>')


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
    date = configuration.tuple_to_date(time.localtime())

    w.writerow((server._("MSG_suivi_group_date")    , '', date         , ''))
    w.writerow((server._("MSG_suivi_group_table")   , '', t.ue[3:]     , ''))
    w.writerow((server._("MSG_suivi_group_title")   , '', t.table_title, ''))
    w.writerow((server._("MSG_suivi_group_sequence"), '', seq          , ''))
    w.writerow((server._("MSG_suivi_group_id"),
                server._("MSG_suivi_group_surname"),
                server._("MSG_suivi_group_firstname"),
                server._("MSG_suivi_group_group")))

    for line in get_lines(t, col_inscrit, seq=seq):
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
