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

import time
import cgi
from .. import plugin
from .. import document
from .. import utilities
from .. import configuration

def infos(server, page):
    s = ('<a target="_blank" href="%s/%s">' % (
        configuration.suivi.url(ticket=server.ticket.ticket), page.user_name)
         + page.user_name + '</a>/' + page.user_ip
         )
    if not page.browser_file.closed:
        s = '<b>' + s + '</b>'
    return s

def stat_page(server):
    """Display the tables in memory and the user on them."""
    server.the_file.write(repr(utilities.current_jobs) + '\n')
    if utilities.send_mail_in_background_list:
        server.the_file.write(
            '<b>' + server._("MSG_send_mail_error") + '</b>' +
            ' '.join(zip(*utilities.send_mail_in_background_list)[0]))
        
    s = ['<title>'
         + server._("TITLE_statpage") + '</title><table border><tbody><tr><th>'
         + server._("TH_year"             ) +'</th><th>'
         + server._("TH_semester"         ) +'</th><th>'
         + server._("TH_table"            ) +'</th><th>'
         + server._("TH_statpage_nr_pages") +'</th><th>'
         + server._("TH_statpage_nr_lines") +'</th><th>'
         + server._("TH_statpage_nr_cols" ) +'</th><th>'
         + server._("TH_statpage_nr_cells") +'</th><th>'
         + server._("TH_statpage_who"     ) +'</th><th>'
         + server._("TH_statpage_when"    ) +'</th></tr>'
         ]
    tables = document.tables_values()
    tables.sort(key = lambda x: x.mtime)
    tables.reverse()
    for t in tables:
        nr_empty = 0
        for p in t.pages:
            if p.nr_cell_change == 0:
                nr_empty += 1
        nr_cells = 0
        for line in t.lines:
            for c in line:
                if c[0] != '':
                    nr_cells += 1
        s.append('<tr><td>%d</td><td>%s</td><td><a target="_blank" href="%s">%s</a></td><td>%d/%d<small>%s<a href="%s">%s</a>%s%s</td><td>%d</td><td>%d</td><td>%d</td><td>%s</td><td>%s</td></tr>' % (
            t.year,
            t.semester,
            "%s/=%s/%s/%s/%s" % (utilities.StaticFile._url_,
                               server.ticket.ticket, t.year, t.semester, t.ue),
            t.ue,
            len(t.pages)-nr_empty, len(t.pages), t.do_not_unload,
            "%s/=%s/tablebuffer/%s/%s/%s"%(utilities.StaticFile._url_,
                               server.ticket.ticket, t.year, t.semester, t.ue),
            sum(len(i) for i in t.sent_to_browsers),
            t.modifiable and "M" or "",
            getattr(t, "update_inscrits", None) and "U" or "",
            len(t.lines),
            len(t.columns),
            nr_cells,
            '<br>'.join([infos(server, u) for u in t.pages if u.browser_file]),
            time.ctime(t.mtime)
            )
                 )
    s.append('</tbody></table>')
    server.the_file.write('\n'.join(s))

plugin.Plugin('statpage', '/stat',
              function=stat_page, group='roots',
              link=plugin.Link(html_class="verysafe", where='informations',
                               priority=-10),
              )

def tablebuffer(server):
    """Display the tables in memory and the user on them."""
    table = document.table(server.the_year, server.the_semester,
                           server.the_ue, create=False)
    if table:
        server.the_file.write("""
<style>
TR { vertical-align:top ; }
TH, TD { border: 1px solid black ; }
</style>
<table>""")
        for i, v in enumerate(table.sent_to_browsers):
            server.the_file.write("<tr><th>%s<td>%s</tr>" % (
                    i, cgi.escape(v)))
        server.the_file.write("</table>")

plugin.Plugin('tablebuffer', '/tablebuffer/{Y}/{S}/{U}',
              function=tablebuffer, group='roots',
              )






