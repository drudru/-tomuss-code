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

import plugin
import os
import time

last = 0

def log(server):
    """Store a text in a log file"""
    global last
    if time.time() - last < 0.1:
        return
    last = time.time()
    
    if server.the_path[0] not in ('help',):
        return
    text = '/'.join(server.the_path[1:]) + '\n'
    # Not process safe
    f = open(os.path.join('LOGS','help'), 'a')
    f.write(text[:100])
    f.close()
    

plugin.Plugin('log', '/log/{*}',
              function = log,
              teacher=True,
              )

