#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2011-2014 Thierry EXCOFFIER, Universite Claude Bernard
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
Use this plugin in order to make TOMUSS send student pictures.
"""

import os
import socket
from .. import plugin
from .. import utilities
from .. import inscrits

def picture(server):
    """Display the picture of a student"""
    # Remove .JPG and get the student number
    if '/' in server.something:
        return
    login = server.something.split('.')
    student_id = inscrits.login_to_student_id('.'.join(login[:-1]))
    extension = login[-1]
    try:
        server.the_file.write(
            utilities.read_file(os.path.join('PICTURES',
                                             student_id + '.' + extension)))
    except (IOError, socket.error):
        pass

plugin.Plugin('picture', '/picture/{?}',
              function=picture,
              mimetype='image/jpeg',
              group='staff',
              cached = True,
              unsafe=False,
              )

def my_picture(server):
    """Display the connected user picture"""
    server.something = inscrits.login_to_student_id(server.ticket.user_name) + '.JPG'
    picture(server)

plugin.Plugin('my_picture', '/picture/{?}',
              function=my_picture,
              mimetype='image/jpeg',
              group='!staff',
              cached = True,
              unsafe=False,
              )





