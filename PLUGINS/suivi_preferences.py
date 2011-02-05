#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet)
#    Copyright (C) 2009-2011 Thierry EXCOFFIER, Universite Claude Bernard
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
import utilities
import tablestat
import configuration
import document

def preferences(server):
    """Join of all the preferences table"""
    filename = document.table_filename('0', 'Stats', 'stat_preferences')

    f = open(filename, "w")
    f.write("""# -*- coding: utf8 -*-
from data import *
new_page('' ,'*', '', '')
column_change (0,'0_0','Enseignant','Text','','','F',0,6)
column_comment(0,'0_0','Identifiant (login) de l\\'enseignant')
column_change (0,'0_1','Attribut','Text','','','F',0,2)
column_change (0,'0_2','Valeur','Text','','','F',0,2)
table_comment (0,'Toutes les préférences')
table_attr('default_nr_columns', 0, 3)
""")

    i = 0
    for t in tablestat.les_ues('0', 'Preferences', all_files=True):
        login = utilities.module_to_login(t.ue)
        for key, line in t.lines.items():
            if line[3].value.lower() != line[1].value.lower():
                f.write("""cell_change(0,'0_0','%d',%s,'')
cell_change(0,'0_1','%d',%s,'')
cell_change(0,'0_2','%d',%s,'')
""" % (i, repr(login), i, repr(key), i, repr(line[3].value)))
                i += 1

    f.close()

def headers(server):
    return (
        ('Location','%s/=%s/0/Stats/stat_preferences' % (
        configuration.server_url, server.ticket.ticket), ),)


plugin.Plugin('preferences', '/stat_preferences',
              function=preferences, root=True,
              launch_thread = True,
              response=307,
              headers = headers,
              link=plugin.Link(text='Fusion des préférences',
                               where="informations",
                               html_class="verysafe",
                               # Should be the last semester
                               url="javascript:go_suivi('stat_preferences')",
                               help="""Pour voir globalement ce que les
                               utilisateurs modifient dans leurs
                               préférences TOMUSS""",
                               priority = 1000,
                   ),
              )






