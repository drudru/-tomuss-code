#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2010 Thierry EXCOFFIER, Universite Claude Bernard
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

import plugin
import tablestat
import data
import itertools

def page_groupe(server):
    """List all the students groups defined by the teacher
    and not by TOMUSS"""
    
    for t in tablestat.les_ues(server.year, server.semester):
        col_inscrit = t.column_inscrit()
        if col_inscrit is None:
            continue
        if t.ue_code != t.ue or not t.official_ue:
            continue

        g = []
        for line in t.lines.values():
            if line[col_inscrit].value != 'ok':
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
                s += '\t%s %s %s\n' % (j[2], j[3], j[4])
            server.the_file.write('%s(%s)\n' % key + s)




plugin.Plugin('groupe', '/groupe', teacher=True, password_ok = None,
              mimetype = 'text/plain',
              function = page_groupe,
              launch_thread=True,
              link=plugin.Link(text="Tous les groupes saisis dans TOMUSS",
                               where="informations",
                               html_class="verysafe",
                               url="javascript:go_suivi('groupe')",
                               help="""Extrait pour toutes les UE la liste
                               des affectations de groupes faites par
                               les enseignants.""",
                               ),

              )
