#!/usr/bin/python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2014 Thierry EXCOFFIER, Universite Claude Bernard
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
#    Contact: Thierry.EXCOFFIER@univ-lyon1.fr

import json
import time
from . import files
from . import utilities
from . import configuration

display_dict = {}

class Display:
    """The class name will be call as JavaScript function to generate HTML"""
    time = 0
    def __init__(self, name, containers, priority, data=None,
                 js=None):
        self.name = name
        if not isinstance(containers, (tuple, list)):
            containers = [containers]
        self.containers = containers
        self.priority = priority
        self.data = data
        self.js = js
        display_dict[name] = self
    def is_in(self, top):
        if self.name == top:
            return True
        for parent in self.containers:
            if display_dict[parent].is_in(top):
                return True

def init():
    """Update suivi_student.js with the display definition"""
    d = {}
    for display in display_dict.values():
        d[display.name] = [display.containers, display.priority]
        if display.js:
            d[display.name].append(display.js)
    files.files['suivi_student.js'].append(
        "display.py",
        '\nvar display_definition = ' + json.dumps(d)
        + '\n;display_create_tree();\n')

def do_update(server, s, top):
    server.the_file.write(
        '<script><!--\ndisplay_update(%s,"%s");\n--></script>' %
        (json.dumps(s,
                    indent=server.ticket.user_name in configuration.root
                    and 1
                    or None
                    ).replace('>','\\x3E'), top))
    server.the_file.flush()
    
    
def data_to_display(server, top):
    """Create the page by updating it every 0.2 seconds or more"""
    server.the_file.write('<script>start_display();</script>')
    start = t = time.time()
    s = []
    profiling = {}
    for display in sorted(display_dict.values(), key=lambda x: x.time):
        if display.data:
            if display.is_in(top):
                try:
                    s.append((display.name, display.data(server)))
                except:
                    utilities.send_backtrace('', 'Display: ' + display.name)
                    continue
                tt = time.time()
                display.time = (4*display.time + (tt - t)) / 5
                profiling[display.name] = int(display.time*1000000)
                t = tt
                if t - start > 0.02:
                    do_update(server, s, top)
                    s = []
                    start = t
                    
    s.append(("Profiling", profiling))
    do_update(server, s, top)

