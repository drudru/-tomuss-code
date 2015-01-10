#!/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2011 Thierry EXCOFFIER, Universite Claude Bernard
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

import sys
import collections
import os
from .. import plugin
from .. import utilities
from .. import document
from .. import column
from .. import plugins
from .. import files
from .. import display

def reload_plugins(server):
    """Reload all the plugins from PLUGINS, COLUMN_TYPES, ATTRIBUTES"""
    plugin_files = collections.defaultdict(list)
    for i in plugin.plugins:
        plugin_file = i.function.__module__
        if '.' not in plugin_file:
            continue
        plugin_files[plugin_file].append(i)
        
    server.the_file.write('<title>' + server._("TITLE_reload_plugins")
                          + '</title><table border>\n')
    server.the_file.write('<tr><th>' + server._("TH_reload_plugins_module")
                          + '<th>' + server._("TH_reload_plugins_number")
                          + '<th>' + server._("TH_reload_plugins_reloaded")
                          + '</tr>\n')
    for i in sorted(plugin_files.keys()):
        if __name__ == i:
            continue
        filename = i.replace('TOMUSS.','',1).replace('.', os.path.sep) + '.py'
        dummy_module, reimported = utilities.import_reload(filename)
        reimported = ('', server._("TH_reload_plugins_reloaded"))[reimported]
        server.the_file.write('<tr><td>%s<td>%d<td>%s</tr>\n' % (
            i, len(plugin_files[i]), reimported))
    server.the_file.write('</table>\n')
    server.the_file.write(server._("MSG_reload_plugins_js_reloaded"))
    server.the_file.write('<table border>\n')
    server.the_file.write('<tr><th>' + server._("TH_reload_plugins_attribute")
                          + '<th>' + server._("TH_reload_plugins_reloaded")
                          + '</tr>\n')
    server.the_file.write('\n'.join('<tr><td>%s<td>%s</tr>' % (
        name, reloaded) for name, reloaded in column.initialize()))
    server.the_file.write('</table>\n')
    server.the_file.write(server._("MSG_reload_plugins_class_tree") + '<br>')
    server.the_file.write(server._("MSG_reload_plugins_js_reloaded"))
    server.the_file.write('<table border>\n')
    server.the_file.write('<tr><th>' + server._("TH_reload_plugins_type")
                          + '<th>' + server._("TH_reload_plugins_reloaded")
                          + '</tr>\n')
    server.the_file.write('\n'.join('<tr><td>%s<td>%s</tr>' % (
        name, reloaded) for name, reloaded in plugins.load_types()))
    server.the_file.write('</table>\n')

    for a_file in files.files.values():
        a_file.clear_cache()

    # Recompute 'invited'
    t = document.table(0, 'Dossiers', 'config_plugin', None, None)
    t.template.onload(t)

    # Recompute display plugins
    display.init()

plugin.Plugin('reload_plugins', '/reload_plugins',
              function=reload_plugins, group='roots',
              link=plugin.Link(where='debug', html_class='safe',
                               priority=-5)
              )
