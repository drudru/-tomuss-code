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
import tablestat

def clean(server):
    """Remove all the UE that where not modified and are not actives.
    Display the list of the tables and why they are not deleted.
    Tables with lines are not deleted even if empty.
    """
    
    for table in tablestat.les_ues(server.the_year, server.the_semester):
        empty, comment = table.empty()
        ue = '<a href="%s">%s</a> : %s' % (table.ue, table.ue, comment)
        if empty and len(table.lines) == 0:
            ue = '<b>' + table.ue + '</b>'
            table.delete()
        else:
            # Not unloaded if there is active pages.
            table.unload()
            
        server.the_file.write(ue + '<br>\n')
        server.the_file.flush()

plugin.Plugin('clean', '/{Y}/{S}/clean', group='roots', function=clean,
              launch_thread=True,
              link=plugin.Link(
                  url="javascript:go(\'clean\')",
                  where='root_rw', html_class='veryunsafe',
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
                ue += server._("MSG_clean_other_deleted")
                table.delete()
            else:
                ue += server._("MSG_clean_other_in_use")
        else:
            ue += server._("MSG_clean_other_strange")

        server.the_file.write('<br>' + ue + '<br>\n')
        server.the_file.flush()

    server.the_file.write('<br>' + server._("MSG_clean_other_done"))
    server.the_file.flush()

plugin.Plugin('clean_other', '/clean_other', group='roots',
              function=clean_other, launch_thread=True,
              link=plugin.Link(
                  where='root_rw', html_class='veryunsafe',
                  )
              )

