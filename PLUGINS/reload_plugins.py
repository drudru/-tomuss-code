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

import collections
import os
import plugin
import utilities
import document
import column
import plugins
import files

def reload_plugins(server):
    plugin_files = collections.defaultdict(list)
    for i in plugin.plugins:
        plugin_file = i.function.__module__
        if '.' not in plugin_file:
            continue
        plugin_files[plugin_file].append(i)
        
    server.the_file.write('<title>Reload Plugins</title><table border>\n')
    server.the_file.write('<tr><th>Module name<th>#Plugins in<br>the module<th>Reloaded?</tr>\n')
    for i in sorted(plugin_files.keys()):
        if __name__ == i:
            continue
        filename = i.replace('.', os.path.sep) + '.py'
        module, reimported = utilities.import_reload(filename)
        reimported = ('', 'Reloaded')[reimported]
        server.the_file.write('<tr><td>%s<td>%d<td>%s</tr>\n' % (
            i, len(plugin_files[i]), reimported))
        if reimported:
            for i in plugin_files[i]:
                plugin.plugins.remove(i)
    server.the_file.write('</table>\n')
    server.the_file.write('The attribute javascript is reloaded even if the Python module is not reloaded\n')
    server.the_file.write('<table border>\n')
    server.the_file.write('<tr><th>Attribute name<th>Reloaded?</tr>\n')
    server.the_file.write('\n'.join('<tr><td>%s<td>%s</tr>' % (
        name, reloaded) for name, reloaded in column.initialize()))
    server.the_file.write('</table>\n')
    server.the_file.write('BEWARE: subclasses are not recomputed.\n')
    server.the_file.write('The column type javascript is reloaded even if the Python module is not reloaded\n')
    server.the_file.write('<table border>\n')
    server.the_file.write('<tr><th>Type name<th>Reloaded?</tr>\n')
    server.the_file.write('\n'.join('<tr><td>%s<td>%s</tr>' % (
        name, reloaded) for name, reloaded in plugins.load_types()))
    server.the_file.write('</table>\n')

    for a_file in files.files.values():
        a_file.content = None
    
    document.table(0, 'Dossiers', 'config_plugin', None, None)

plugin.Plugin('reload_plugins', '/reload_plugins',
              function=reload_plugins,
              root=True,
              link=plugin.Link(
                  text='Recharge les plugins',
                  help="""Met à jours les plugins modifiés sur disque.
                  C'est-à-dire : le contenu des répertoires PLUGINS,
                  ATTRIBUTES et COLUMN_TYPES (y compris JavaScript).
                  Les plugins modifiant l'état de l'application
                  ou lançant des threads ne doivent pas être rechargés.""",
                  where='debug',
                  html_class='safe',
                  )
              )
