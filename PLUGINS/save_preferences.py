#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2013 Thierry EXCOFFIER, Universite Claude Bernard
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

"""
Save user preferences for suivi
"""

import os
from .. import plugin
from .. import utilities
from .. import configuration
from .. import files

def save_preferences(server):
    """Set the private state of the student"""
    login = utilities.the_login(server.ticket.user_name)
    d = {}
    for item in server.the_path:
        item = item.split('=')
        assert(len(item) == 2)
        assert(utilities.safe(item[0]) == item[0])
        d[item[0]] = int(item[1])
        assert(d[item[0]] in (0,1))
    utilities.manage_key('LOGINS', os.path.join(login, 'preferences'),
                         content = repr(d))
    server.the_file.write(str(files.files['ok.png']))

    # XXX For old files from TOMUSS before 5.3.2
    utilities.manage_key('LOGINS', os.path.join(login, 'private'),
                         delete=True)


plugin.Plugin('save_preferences', '/save_preferences/{*}', priority=-11,
              mimetype="image/png", group="",
              function=save_preferences)

