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
import document
import glob
import os
import configuration
import utilities

def master_of(server):
    """Update the preferences to add the list of UE where the user is master.
    This function is only used in case of bug in the algorithm updating
    the master list incrementaly"""

    users = {}
    f = glob.glob(os.path.join(configuration.db,'Y[0-9]*','S*','[!_]*.py'))
    for filename in f:
        filename = filename.split(os.path.sep)
        year, semester, ue = filename[-3:]
        year = year[1:]
        semester = semester[1:]
        if semester in configuration.master_of_exceptions:
            continue
        ue = ue[:-3]
        utilities.warn(str((year, semester, ue)))
        try:
            table = document.table(year, semester, ue, None, None)
        except:
            print 'Problem with ', year, semester, ue
            continue
        for user in table.masters:
            if user not in users:
                users[user] = []
            users[user].append((year, semester, ue))
        table.unload()
        server.the_file.write('%s: %s<br>' % (table.filename, table.masters))
        
    for user, tables in users.items():
        utilities.manage_key('LOGINS',
                             os.path.join(user, 'master_of'),
                             content = repr(tables)
                             )

def message(pplugin, server):
    """Display the link to the master_of initialisation"""
    return '<a target="_blank" href="=%s/%s"><b>NE PAS UTILISER</b> : réinitialise complètement la liste des UE dont on est responsable</a>. A utiliser seulement en cas de bugs.' % (
        server.ticket.ticket, pplugin.url[0])


plugin.Plugin('master_of', '/master_of',
              function=master_of,
              root=True,
              launch_thread = True,
              link=plugin.Link(text='Réinitialise responsables',
                               help="""À utiliser seulement en cas de bug.
                               Ceci recalcule pour chaque utilisateur la
                               liste des tables dont il est responsable.
                               Ceci est normalement inutile.""",
                               html_class="veryunsafe",
                               priority=100,
                               where='root_rw',
                               ),
              )


