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
RSSKEY creation
"""

from .. import plugin
from .. import utilities
import random
import os

def rsskey(server):
    """Create and return the RSS key of the connected user"""
    login = server.ticket.user_name

    key = utilities.manage_key('LOGINS', os.path.join(login, 'rsskey'))
    if key is False:
        random.seed()
        key = random.randint(0, 1000000000000000000)
        random.seed(id(login))
        key += random.randint(0, 1000000000000000000)
        key = "%x" % key
        utilities.manage_key('LOGINS', os.path.join(login, 'rsskey'),
                             content=key)
        utilities.manage_key('RSSLOGINS', key, content=login, separation=2)
    server.the_file.write(key)

plugin.Plugin('rsskey', '/rsskey', function=rsskey, mimetype='text/plain',
              priority=-10)





