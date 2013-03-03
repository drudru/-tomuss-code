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

from .. import plugin
from .. import utilities
from .. import configuration
import os

def private(server):
    """Set the private state of the student"""
    if not configuration.suivi_student_allow_private:
        return
    login = utilities.the_login(server.ticket.user_name)
    utilities.manage_key('LOGINS', os.path.join(login, 'private'),
                         content=str(int(server.the_path[0])))
    server.the_file.write(login + ' : ' + server._("MSG_saved"))

plugin.Plugin('private', '/private/{*}', priority=-11, function=private)

