#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2010-2013 Thierry EXCOFFIER, Universite Claude Bernard
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

import os
import time
import ast
from .. import plugin
from .. import utilities

last = 0

def log(server):
    """Store a text in a log file"""
    global last
    if time.time() - last < 0.1:
        return
    last = time.time()
    
    if server.the_path[0] not in ('help', 'javascript_errors'):
        return
    text = '/'.join(server.the_path[1:]) + '\n'
    # XXX Not process safe
    f = open(os.path.join('LOGS', server.the_path[0]), 'a')
    f.write(text[:1000].strip() + '\n')
    f.close()
    

plugin.Plugin('log', '/log/{*}',
              function = log,
              authenticated = False,
              group='staff',
              )


def gui_record(server):
    """Store a text in a log file"""
    posted_data = server.get_posted_data()
    if posted_data is None:
        return

    table = posted_data['table'][0]
    start = posted_data['start'][0]
    data = posted_data['data'][0]
    try:
        ast.literal_eval(data)
        ast.literal_eval(start)
    except:
        utilities.send_backtrace(data, "GUI record")
        return
    
    utilities.manage_key('LOGINS', os.path.join(server.ticket.user_name, 'GUI_record'),
                         content='R(' + utilities.js(table) + ','
                         + utilities.js(start) + ','
                         + data + ')\n', append=True)

plugin.Plugin('gui_record', '/gui_record',
              function = gui_record,
              group='staff',
              launch_thread=True,
              )

