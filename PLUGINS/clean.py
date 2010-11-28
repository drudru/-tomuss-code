#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2008,2009 Thierry EXCOFFIER, Universite Claude Bernard
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
import tablestat

def clean(server):
    """Remove all the UE that where not modified and are not actives.
    Display the list of the tables and why they are not deleted."""
    
    for table in tablestat.les_ues(server.the_year, server.the_semester):
        empty, comment = table.empty()
        ue = '<a href="%s">%s</a> : %s' % (table.ue, table.ue, comment)
        if empty:
            ue = '<b>' + table.ue + '</b>'
            table.delete()
        else:
            # Not unloaded if there is active pages.
            table.unload()
            
        server.the_file.write(ue + '<br>\n')
        server.the_file.flush()

plugin.Plugin('clean', '/{Y}/{S}/clean', root=True, function=clean,
              link=plugin.Link(
                  text='Détruit les UE vides',
                  url="javascript:go(\'clean\')",
                  help="""Les UE détruites sont mises dans le répertoire Trash.
                  C'est LENT : il ne faut pas le faire en charge.
                  Il est préférable de ne pas le faire pour garder
                  un historique des étudiants inscrits.
                  Ceci n'est fait que pour les UE du semestre choisi.""",
                  where='root_rw',
                  html_class='veryunsafe',
                  )
              )


def clean_other(server):
    """Remove all the tables (not UE) that are completly empty."""
    
    for table in tablestat.all_the_tables():

        if len(table.columns):
            server.the_file.write(' .')
            server.the_file.flush()
            table.unload()
            continue

        ue = '%s : %d col. ' % (table.filename, len(table.columns))
        if len(table.pages) != 0:
            if len(table.active_pages) == 0:
                ue += 'DELETED'
                table.delete()
            else:
                ue += 'can not be delete because it is in use.'
        else:
            ue += 'not deleted, look the content it is a strange file.'

        server.the_file.write('<br>' + ue + '<br>\n')
        server.the_file.flush()

    server.the_file.write('<br>Cleaning done\n')
    server.the_file.flush()

plugin.Plugin('clean_other', '/clean_other', root=True, function=clean_other,
              link=plugin.Link(
                  text='Détruit les tables vides',
                  help="""Les tables détruites sont mises dans
                  le répertoire Trash.
                  C'est LENT : il ne faut pas le faire en charge.
                  Seul les tables complètement vides sont détruites.
                  Ceci ne détruit pas les UE.
                  """,
                  where='root_rw',
                  html_class='veryunsafe',
                  )
              )

