#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet)
#    Copyright (C) 2008-2011 Thierry EXCOFFIER, Universite Claude Bernard
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

import sys
import time
from .. import plugin
from .. import configuration
from .. import utilities
from .. import referent
from .. import inscrits

def referents_table_real():
    done = {}
    d = {}
    for student in referent.student_list(sys.stderr,
                                         referent.port(),
                                         referent.not_in()).values():
        if student.key in done:
            continue
        done[student.key] = True
        p = ''
        # if student.key in a1:
        #     p += 'L1'
        # if student.key in a2:
        #     p += 'L2'
        r = referent.referent(configuration.year_semester[0],
                              configuration.year_semester[1],
                              student.key)
        if r == None:
            continue
        try:
            firstname, surname, mail = d[r]
        except KeyError:
            firstname, surname, mail = inscrits.L_batch.firstname_and_surname_and_mail(r)
            d[r] = firstname, surname, mail
        s_surname = student.surname
        s_firstname = student.firstname.title()
        yield (p, student.key, s_surname, s_firstname, surname, firstname.title(), mail)


@utilities.add_a_lock
def referents_table():
    if time.time() > referents_table.time + 3600:
        referents_table.cache = []
        for i in referents_table_real():
            referents_table.cache.append(i)
            yield i
        referents_table.time = time.time()
    else:
        for i in referents_table.cache:
            yield i
referents_table.time = 0


def referents_csv(server):
    """Generate the referent list in CSV"""
    import csv
    f = server.the_file
    w = csv.writer(f, delimiter=';')
    for r in referents_table():
        w.writerow(r)

def referents_html(server):
    """Generate the referent list in HTML"""
    f = server.the_file
    f.write(server._("MSG_wait_some_minutes"))
    f.flush()
    f.write('<table>\n')
    for r in referents_table():
        f.write('<tr><td>' + '</td><td>'.join(r) + '</td></tr>\n')
    f.write('</table>\n')


plugin.Plugin('referents.csv', '/referents.csv',
              function=referents_csv,
              authenticated=False,
              mimetype = 'text/csv; charset=utf-8',
              launch_thread=True,
              )

plugin.Plugin('referents.xls', '/referents.xls',
              function=referents_html, # Yes HTML not xls or csv
              authenticated=False,
              mimetype = 'application/excel; charset=utf-8',
              launch_thread=True,
              link=plugin.Link(
        url="javascript:go_suivi('referents.xls')",
        where='referents', html_class="verysafe", priority=100,
        group='roots',
        ),
              )

plugin.Plugin('referents.html', '/referents.html',
              function=referents_html, # Yes HTML not xls or csv
              mimetype = 'text/html; charset=utf-8',
              authenticated=False,
              launch_thread=True,
              link=plugin.Link(
        url="javascript:go_suivi('referents.html')",
        where='referents', html_class="verysafe", priority=100,
        group='roots',
        ),
              )
