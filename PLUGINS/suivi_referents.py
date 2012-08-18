#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet)
#    Copyright (C) 2008,2010 Thierry EXCOFFIER, Universite Claude Bernard
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
import referent
import utilities
import configuration

class StatCol(object):
    def __init__(self, titles, increment=lambda x: True):
        self.titles = titles
        self.counter = 0
        self.increment = increment
        self.data_col = None

    def get_data_col(self, table):
        col = table.columns.from_id(self.titles[0])
        if col:
            self.data_col = col.data_col
            self.titles = (col.title,)
            return
        # It is an old file
        for title in self.titles:
            self.data_col = table.columns.data_col_from_title(title)
            if self.data_col:
                return

    def count(self, line):
        if self.data_col is None:
            return
        value = line[self.data_col].value
        if value == '':
            return
        if self.increment(value):
            self.counter += 1

    def html(self):
        # if self.counter == 0:
        #    return ''
        if self.data_col is None:
            return ''
        else:
            return self.titles[0] + ' : ' + str(self.counter) + '\n'
        

def stat_referent(f, year, semester, server):
    import TEMPLATES.Referents
    us = configuration.university_semesters
    # Do not translate remaining french please. It's to read old files
    prst = configuration.pre
    yes = configuration.yes
    no = configuration.no
    columns = (
        StatCol( ('RDV1', 'RDV_1',), increment=lambda x: x == prst),
        StatCol( ('RDV2', 'RDV_2',), increment=lambda x: x == prst),
        StatCol( ('RDV3', 'RDV_3',), increment=lambda x: x == prst),
        StatCol( ('RDV4', 'RDV_4',), increment=lambda x: x == prst),
        StatCol( ('REM1', 'Remarques', 'Remarques IP ' + us[0])),
        StatCol( ('REM2', 'Remarques_2', 'Remarques IP ' + us[1])),
        StatCol( ('CON1', 'TOMUSS_'+us[0], us[0])),
        StatCol( ('CON2', 'TOMUSS_'+us[1], us[1])),
        StatCol( ('JUR1', 'Commentaire Jury ' + us[0],)),
        StatCol( ('JUR2', 'Commentaire Jury ' + us[1],)),
        StatCol( ('FiRe', 'Primo Entrant',)),
        # For old files
        StatCol( ('ContratSigné',)),
        StatCol( ('Contacté',)),
        StatCol( ('Contacté_2',)),
        StatCol( ('ContratSigné 2',)),
        StatCol( ('ContratRespecté',)     , increment=lambda x: x == yes),
        StatCol( ('ContratNonRespecté',)  , increment=lambda x: x == no),
        StatCol( ('ContratRespecté_2',)   , increment=lambda x: x == yes),
        StatCol( ('ContratNonRespecté_2',), increment=lambda x: x == no),
    )

    nr_students = 0
    nr_teachers = 0

    year_blocnote = utilities.university_year(year, semester)

    for t in referent.les_blocsnotes(year_blocnote):
        for statcol in columns:
            statcol.get_data_col(t)

        for line in t.lines.values():
            if line[0].value == '':
                continue
            if len(line) < 8:
                continue
            nr_students += 1
            for statcol in columns:
                statcol.count(line)

        nr_teachers += 1

    f.write('<title>%s</title>\n' % server._("LINK_referents"))
    f.write('<h1>%s</h1>\n' % server._("LINK_referents"))
    f.write('<pre>')
    f.write('%s%d\n' % (server._("MSG_suivi_referents_nr_students"),
                        referent.nr_students(year, semester)))
    f.write('%s%d\n' % (server._("MSG_suivi_referents_nr_referents"),
                        len(referent.referents_login(year, semester))))
    f.write('%s%d\n' % (server._("MSG_suivi_referents_nr_notepads"),
                        nr_teachers))
    f.write("%s%d\n" % (server._("MSG_suivi_referents_nr_students_in_notepads"),
                        nr_students))
    for statcol in columns:
        f.write(statcol.html())
    
    f.write('</pre>')

def referents(server):
    """Display statistics about referents."""
    stat_referent(server.the_file, server.year, server.semester, server)

plugin.Plugin('referents', '/*3', function=referents,
              group='roots',
              launch_thread = True,
              link=plugin.Link(url="javascript:go_suivi('*3')",
                               where='referents', html_class="verysafe",
                               ),
              )




