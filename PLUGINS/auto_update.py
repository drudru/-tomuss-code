#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2012 Thierry EXCOFFIER, Universite Claude Bernard
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

from .. import plugin
from .. import tablestat
from .. import configuration
from .. import document
from .. import utilities
import time

def auto_update(server):
    """Update the student list for each known table of the current semester.
    Or the tables in the path in the current semester.
    """

    server.the_file.write('<h1>' + server._("MSG_auto_update_start") + '</h1>')

    if server.the_path:
        tables = (
            document.table(configuration.year_semester[0],
                           configuration.year_semester[1],
                           utilities.safe(ue).replace('.','_'))
            for ue in server.the_path
            )
    else:
        tables = tablestat.les_ues(configuration.year_semester[0],
                               configuration.year_semester[1],
                               ro=False)

    to_unload = set()
    for t in tables:
        server.the_file.write("%s " % t.ue)
        server.the_file.flush()
        to_unload.add(t)
        while len(document.update_students) > 2:
            time.sleep(0.1)
        for tt in to_unload - set(document.update_students):
            if tt.do_not_unload:
                continue
            tt.unload()
            to_unload.remove(tt)
        
    server.the_file.write('<h1>' + server._("MSG_auto_update_done") + '</h1>')

plugin.Plugin('auto_update', '/auto_update', function=auto_update,
              group='roots', launch_thread = True,
              link=plugin.Link(where='root_rw', html_class='safe',
                               url = '/auto_update')
              )

plugin.Plugin('auto_update_one', '/auto_update/{*}', function=auto_update,
              group='staff', launch_thread = True,
              )
