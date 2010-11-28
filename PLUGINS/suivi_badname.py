#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet)
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
import tablestat
import inscrits
import utilities

def normalize(txt):
    return utilities.flat(txt).lower().replace('  ', ' ')

def the_badname(server):
    """Display the names not matching the student ID."""
    for t in tablestat.les_ues(server.year, server.semester, true_file=True):
        for line in t.lines.values():
            login = inscrits.login_to_student_id(line[0].value)
            if login.strip() == '':
                continue
            first_name, surname = inscrits.firstname_and_surname(login)
            if (normalize(first_name) != normalize(unicode(line[1].value,'utf8'))
                or normalize(surname) != normalize(unicode(line[2].value, 'utf8'))):
                server.the_file.write('%s\t%s\t%s %s != %s %s\n' % (
                t.ue, login,
                first_name.encode('utf8'), surname.encode('utf8'),
                unicode(line[1].value, 'utf8').encode('utf8'),
                unicode(line[2].value, 'utf8').encode('utf8')))


plugin.Plugin('badname', '/badname', function=the_badname, root=True,
              launch_thread = True,
              mimetype = "text/plain; charset=utf8",
              link=plugin.Link(text="Mauvais noms",
                               where="deprecated",
                               html_class="verysafe",
                               url="javascript:go_suivi('badname')",
                               help="""Liste les noms d'étudiants qui sont
                               dans TOMUSS avec un nom qui ne correspond
                               pas au numéro d'étudiant.""",
                               ),
              )
