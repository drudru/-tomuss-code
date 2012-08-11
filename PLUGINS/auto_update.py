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

import plugin
import tablestat
import configuration
import document
import time

def auto_update(server):
    """Update the student list for each known table of the current semester"""

    to_unload = set()
    for t in tablestat.les_ues(*configuration.year_semester, ro=False):
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
        

plugin.Plugin('auto_update', '/auto_update', function=auto_update, root=True,
              launch_thread = True,
              link=plugin.Link(where='root_rw', html_class='safe')
              )
