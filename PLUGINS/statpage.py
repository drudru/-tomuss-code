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
import document
import time
import utilities

def infos(page):
    s = page.user_name + '/' + page.user_ip
    if not page.browser_file.closed:
        s = '<b>' + s + '</b>'
    return s

def stat_page(server):
    """Display the table in memory and the user on them."""
    s = ['<title>Who\'s connected</title><table border><tbody><tr><th>Year</th><th>Semester</th><th>UE</th><th>#pages</th><th>#lines</th><th>#cols</th><th>#cells</th><th>Users on the page</th><th>Last User Interaction</th></tr>']
    tables = document.tables_values()
    tables.sort(key = lambda x: x.mtime)
    tables.reverse()
    for t in tables:
        nr_empty = 0
        for p in t.pages:
            if p.request == 0:
                nr_empty += 1
        nr_cells = 0
        for line in t.lines:
            for c in line:
                if c[0] != '':
                    nr_cells += 1
        s.append('<tr><td>%d</td><td>%s</td><td><a href="%s">%s</a></td><td>%d/%d[%d]</td><td>%d</td><td>%d</td><td>%d</td><td>%s</td><td>%s</td></tr>' % (
            t.year,
            t.semester,
            "%s/=%s/%s/%s/%s" % (utilities.StaticFile._url_,
                               server.ticket.ticket, t.year, t.semester, t.ue),
            t.ue,
            len(t.pages)-nr_empty, len(t.pages), t.do_not_unload,
            len(t.lines),
            len(t.columns),
            nr_cells,
            '<br>'.join([infos(u) for u in t.pages if u.browser_file]),
            time.ctime(t.mtime)
            )
                 )
    s.append('</tbody></table>')
    server.the_file.write('\n'.join(s))

plugin.Plugin('statpage', '/stat',
              function=stat_page, root=True,
              link=plugin.Link(text='Qui fait quoi',
                               help='Liste les tables TOMUSS en mémoire',
                               html_class="verysafe",
                               where='informations',
                               ),
              )






