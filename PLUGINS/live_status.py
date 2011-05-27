#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2009 Thierry EXCOFFIER, Universite Claude Bernard
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
import utilities
import os
import sys
import sender
import files

files.files['live_status.js'] = utilities.StaticFile(
    os.path.join('PLUGINS', 'live_status.js'))

def live_status(server):
    """This page continuously display logs of the server."""
    server.the_file.write(utilities.read_file(os.path.join('PLUGINS',
                                                           'live_status.svg')
                                              ))
    sender.add_client(server.the_file)

plugin.Plugin('live_status_svg', '/live_status.svg',
              function=live_status, root=True,
              mimetype = "image/svg+xml",
              keep_open = True,
              link=plugin.Link(text='Live status',
                               html_class='verysafe',
                               where='debug',
                               help='Affichage graphique temps réel de TOMUSS',
                               priority=-1,
                               )
              )

