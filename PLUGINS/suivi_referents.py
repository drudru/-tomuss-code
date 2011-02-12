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

class StatCol(object):
    def __init__(self, titles, increment=lambda x: True):
        self.titles = titles
        self.counter = 0
        self.increment = increment
        self.data_col = None

    def get_data_col(self, table):
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
            return '[???NO TABLE WITH %s???]\n' % self.titles[0]
        else:
            return '[' + str(self.data_col) + '] ' + self.titles[0] + ' : ' + str(self.counter) + '\n'
        

def stat_referent(f, year, semester):

    columns = (
        StatCol( ('RDV_1',), increment=lambda x: x == 'PRST'),
        StatCol( ('RDV_2',), increment=lambda x: x == 'PRST'),
        StatCol( ('RDV_3',), increment=lambda x: x == 'PRST'),
        StatCol( ('RDV_4',), increment=lambda x: x == 'PRST'),
        StatCol( ('Remarques', 'Remarques IP automne')),
        StatCol( ('Remarques_2', 'Remarques IP Printemps')),
        StatCol( ('Contacté',)),
        StatCol( ('Contacté_2',)),
        StatCol( ('ContratSigné',)),
        StatCol( ('TOMUSS_Automne',)),
        StatCol( ('TOMUSS_Printemps',)),
        StatCol( ('ContratSigné 2',)),
        StatCol( ('ContratRespecté',), increment=lambda x: x == 'OUI'),
        StatCol( ('ContratNonRespecté',), increment=lambda x: x == 'NON'),
        StatCol( ('ContratRespecté_2',), increment=lambda x: x == 'OUI'),
        StatCol( ('ContratNonRespecté_2',), increment=lambda x: x == 'NON'),
        StatCol( ('Commentaire Jury Automne',)),
        StatCol( ('Commentaire Jury Printemps',)),
        StatCol( ('Primo Entrant',)),
    )

    nr_students = 0
    nr_teachers = 0

    year_blocnote = utilities.university_year(year, semester)

    for t in referent.les_blocsnotes(year_blocnote):
        empty = True

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

    f.write('<title>Statistiques Référents</title>\n')
    f.write('<h1>Statistiques sur les référents pédagogiques</h1>\n')
    f.write('<pre>')
    f.write('#étudiants suivis : %d\n' %
            referent.nr_students(year, semester))
    f.write('#référents pédagogiques : %d\n' %
            len(referent.referents_login(year, semester)))
    f.write('#référents pédagogiques avec blocnote : %d\n' % nr_teachers)
    f.write("#Étudiants suivis dans les blocnotes : %d\n"% nr_students)
    for statcol in columns:
        f.write(statcol.html())
    
    f.write('</pre>')

def referents(server):
    """Display statistics about referents."""
    stat_referent(server.the_file, server.year, server.semester)

plugin.Plugin('referents', '/*3', function=referents, teacher=True,
              launch_thread = True,
              link=plugin.Link(text='Statistiques référents pédagogiques',
                               url="javascript:go_suivi('*3')",
                               where="informations",
                               html_class="verysafe",
                               help="""Affiche des statistiques sur
                               les enseignants référents pédagogiques""",
                               ),
              )




