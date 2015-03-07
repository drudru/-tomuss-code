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
import time
from .. import plugin
from .. import utilities
from .. import inscrits
from .. import configuration

try:
    import PIL.Image
    has_pil = True
except ImportError:
    utilities.warn("No Python module PIL")
    has_pil = False

#REDEFINE
# Read/compute the student picture from a database.
# Store it in the filename indicated if it needs to be cached.
# Returns the filename containing the picture to display
def get_the_picture(student_id, filename):
    return filename
configuration.get_the_picture = get_the_picture
configuration.icon_picture_width = 30
configuration.picture_ttl = 24*3600

def load_picture(student_id, extension, icon=''):
    """Update the file on disk if it is needed
    icon may be '_'
    Return the image filename or another one
    """
    name = os.path.join('PICTURES', student_id + icon + '.' + extension)
    if (os.path.exists(name)
        and time.time() - os.path.getmtime(name) < configuration.picture_ttl):
        # Returns the data from cache
        return name
    if not icon:
        # Get the full size image from elsewhere and store it if it exists
        return configuration.get_the_picture(student_id, name)
    full_size = load_picture(student_id, extension)
    full_name = os.path.join('PICTURES', student_id + '.' + extension)
    if os.path.exists(full_name):
        if has_pil:
            i = PIL.Image.open(full_name)
            width = configuration.icon_picture_width
            j = i.resize((width, (i.size[1] * width) // i.size[0]))
            j.save(name)
            return name
        return full_name
    if os.path.exists(full_size):
        return full_size
    return os.path.join('FILES', 'bug.png')

def picture(server, icon=''):
    """Display the picture of a student"""
    # Remove .JPG and get the student number
    if '/' in server.something:
        return
    login = server.something.split('.')
    student_id = inscrits.login_to_student_id('.'.join(login[:-1]))
    extension = login[-1]
    data = utilities.read_file(load_picture(student_id, extension, icon))
    try:
        server.the_file.write(data)
    except socket.error:
        pass

plugin.Plugin('picture', '/picture/{?}',
              function=picture,
              mimetype='image/jpeg',
              group='staff',
              cached = True,
              unsafe=False,
              )

plugin.Plugin('picture_icon', '/picture-icon/{?}',
              function=lambda server: picture(server, icon='-'),
              mimetype='image/jpeg',
              group='staff',
              cached = True,
              unsafe=False,
              )

def my_picture(server, icon=False):
    """Display the connected user picture"""
    server.something = inscrits.login_to_student_id(server.ticket.user_name) + '.JPG'
    picture(server, icon)

plugin.Plugin('my_picture', '/picture/{?}',
              function=my_picture,
              mimetype='image/jpeg',
              group='!staff',
              cached = True,
              unsafe=False,
              priority = -10 # Before student_redirection
              )

plugin.Plugin('my_picture_icon', '/picture-icon/{?}',
              function=lambda server: my_picture(server, icon='-'),
              mimetype='image/jpeg',
              group='!staff',
              cached = True,
              unsafe=False,
              priority = -10 # Before student_redirection
             )





