#!/usr/bin/python3
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
import os
import ast
from . import files
from . import utilities
from . import configuration
from . import document

display_dict = {}

def send_headers(server, css_file, js_file, init_function, more_js=""):
    server.the_file.write(
        str(document.the_head)
        + '''
<link rel="stylesheet" href="%s/display.css" type="text/css">
<link rel="stylesheet" href="%s/%s" type="text/css">
<script src="%s/display.js" onload="this.onloadDone=true;"></script>
<script src="%s/%s" onload="this.onloadDone=true;"></script>
''' % (configuration.url_files, configuration.url_files, css_file,
       configuration.url_files,
       configuration.url_files, js_file)
        + document.translations_init(server.ticket.language)
        )
    server.the_file.flush()
    server.the_file.write(
        '<noscript><h1>'+server._('MSG_need_javascript')+'</h1></noscript>\n'
        + "<script>"
        + "var ticket=%s;\n" % utilities.js(server.ticket.ticket)
        + "var username=%s;\n" % utilities.js(server.ticket.user_name )
        + "var admin=%s;\n" % utilities.js(configuration.maintainer)
        + "var url=%s;\n" % utilities.js(configuration.server_url)
        + "var url_suivi=%s;\n" % utilities.js(utilities.StaticFile._url_)
        + "var url_files=%s ;\n" % utilities.js(configuration.url_files)
        + "var root=%s ;\n" % utilities.js(list(configuration.root))
        + "var maintainer=%s;\n" % utilities.js(configuration.maintainer)
        + "var semester=%s;\n" % utilities.js(configuration.year_semester[1])
        + 'var tomuss_version="%s";\n' % configuration.version
        + 'var bilan_des_notes= %s ; \n' % utilities.js(
            configuration.bilan_des_notes)
        + more_js
        + """
</script>
</head>
<body>
<div id="top"></div>
<script>
        """
        + utilities.wait_scripts()
        + 'function initialize_display()'
        + '{ if ( ! wait_scripts("initialize_display()") ) return ;\n'
        + 'start_display() ;\n'
        + init_function + '() ; }\n'
        + 'initialize_display();\n'
        + '</script>\n'
        + '<div id="display_suivi"></div>'
        )

order_file = os.path.join("TMP", "xxx_display_{}".format(
    configuration.read_only))
try:
    order = ast.literal_eval(utilities.read_file(order_file))
except:
    order = {}

class Display:
    """The class name will be call as JavaScript function to generate HTML"""
    def __init__(self, name, containers, priority, data=None,
                 js=None):
        self.name = name
        if not isinstance(containers, (tuple, list)):
            containers = [containers]
        self.containers = containers
        self.priority = priority
        self.data = data
        self.js = js
        self.time = order.get(name, 0) / 10000000
        display_dict[name] = self
    def is_in(self, top):
        if self.name == top:
            return True
        for parent in self.containers:
            if parent in display_dict  and  display_dict[parent].is_in(top):
                return True

def init():
    """Update suivi_student.js with the display definition"""
    d = {}
    for display in display_dict.values():
        d[display.name] = [display.containers, display.priority]
        if display.js:
            d[display.name].append(display.js)
    files.files['display.js'].append(
        "display.py",
        '\nvar display_definition = ' + json.dumps(d)
        + ';\n')

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
    t = time.time()
    s = []
    profiling = {}
    for display in sorted(display_dict.values(), key=lambda x: x.time):
        if display.data:
            if display.is_in(top):
                if display.time > 0.2:
                    do_update(server, s, top)
                    s = []
                try:
                    s.append((display.name, display.data(server)))
                except:
                    utilities.send_backtrace('', 'Display: ' + display.name)
                    continue
                tt = time.time()
                display.time = max(display.time, tt - t)
                profiling[display.name] = int(display.time*1000000)
                t = tt
    s.append(("Profiling", profiling))
    do_update(server, s, top)
    data_to_display.nr_call += 1
    if data_to_display.nr_call % 10 == 0:
        utilities.write_file(order_file, repr(profiling))

data_to_display.nr_call = 0
