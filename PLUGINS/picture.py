#!/usr/bin/env python3
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
configuration.picture_extension = '.JPG'

def find_size(i, max_width):
    height = (max_width * i.size[1]) // i.size[0]
    if height > 2 * max_width:
        height = 2 * max_width
        width = (height * i.size[0]) // i.size[1]
    if max_width > i.size[0] and height > i.size[1]:
        return i.size[0], i.size[1]
    return max_width, height

def load_picture_(student_id, extension, icon=''):
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
    full_size = load_picture_(student_id, extension)
    full_name = os.path.join('PICTURES', student_id + '.' + extension)
    if os.path.exists(full_name):
        if has_pil:
            i = PIL.Image.open(full_name)
            i = i.resize(find_size(i, configuration.icon_picture_width))
            j.save(name)
            return name
        return full_name
    if os.path.exists(full_size):
        return full_size
    return os.path.join('FILES', 'bug.png')

@utilities.add_a_lock
def load_picture(student_id, extension, icon=''):
    return load_picture_(student_id, extension, icon)

def picture(server, icon=''):
    """Display the picture of a student"""
    # Remove .JPG and get the student number
    if '/' in server.something:
        return
    login = server.something.split('.')
    student_id = inscrits.login_to_student_id('.'.join(login[:-1]))
    extension = login[-1]
    data = utilities.read_file(load_picture(student_id, extension, icon),"bytes")
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
              priority = -10, # Before student_redirection
              launch_thread = True,
              )

plugin.Plugin('picture_icon', '/picture-icon/{?}',
              function=lambda server: picture(server, icon='-'),
              mimetype='image/jpeg',
              group='staff',
              cached = True,
              unsafe=False,
              launch_thread = True,
              )

def my_picture(server, icon=''):
    """Display the connected user picture"""
    if configuration.is_a_student_login(server.something):
        server.something = (inscrits.login_to_student_id(
            server.ticket.user_name) + configuration.picture_extension)
    picture(server, icon)

plugin.Plugin('my_picture', '/picture/{?}',
              function=my_picture,
              mimetype='image/jpeg',
              group='!staff',
              cached = True,
              unsafe=False,
              launch_thread = True,
              priority = -10 # Before student_redirection
              )

plugin.Plugin('my_picture_icon', '/picture-icon/{?}',
              function=lambda server: my_picture(server, icon='-'),
              mimetype='image/jpeg',
              group='!staff',
              cached = True,
              unsafe=False,
              launch_thread = True,
              priority = -10 # Before student_redirection
             )

# Picture uploading

def uploadable(server):
    return has_pil and (configuration.allow_picture_upload
                        or (configuration.allow_teacher_picture_upload
                            and getattr(server, 'teacher_as_a_student', True)))

from .. import display
display.Display("PictureUpload", "LinksTable", 20,
                lambda server: (server.is_a_student
                                or (server.the_path[0].startswith(' ')
                                    and configuration.allow_picture_upload)
                ) and uploadable(server))

from .. import files
files.files["display.js"].append("picture.py", """
function DisplayPictureUpload(node)
{
  if ( ! node.data )
    return ;
  return hidden_txt(
       '<a href="javascript:picture_upload()">' + _("MSG_picture_upload")
        + '</a>',_("TIP_picture_upload")) ;
}
function picture_upload()
{
   create_popup("picture_upload", '<h1>' + _("MSG_picture_upload") + '</h1>',
                _("MSG_picture_upload_choose") + ' ' + username
                + '<p>' + _("TIP_picture_upload")
                + '<form action="' + url + '/=' + ticket + '/my_picture_upload"'
                + ' onchange="this.submit()"'
                + ' target="_blank"'
                + ' enctype="multipart/form-data" method="post">'
                + '<input type="file" name="datafile" size="40"></form>',
                '', false) ;
}
""")

def my_picture_upload(server):
    if not uploadable(server):
        server.the_file.write(
            server._("config_table_allow_picture_upload")
            + ' : ' + str(configuration.allow_picture_upload)
            + '<p>' + server._("config_table_allow_teacher_picture_upload")
            + ' : ' + str(configuration.allow_teacher_picture_upload)
        )
        return
    posted_data = server.get_posted_data(size=10000000)
    image = posted_data['datafile'][0]
    import io
    f = io.BytesIO(image)
    i = PIL.Image.open(f).convert('RGB')

    student_id = inscrits.login_to_student_id(server.ticket.user_name)
    j = i.resize(find_size(i, configuration.icon_picture_width))
    j.save(os.path.join('PICTURES', student_id + '-.JPG'))

    j = i.resize(find_size(i, 8 * configuration.icon_picture_width))
    j.save(os.path.join('PICTURES', student_id + '.JPG'))

    url = configuration.server_url + '/=' + server.ticket.ticket + '/picture'
    server.the_file.write(
        '{}<p><img src="{}.JPG"><p>{}<p><img src="{}.JPG">'.format(
            server._("MSG_picture_upload_icon"),
            url + '-icon/' + server.ticket.user_name,
            server._("MSG_picture_upload_large"),
            url + '/' + server.ticket.user_name,
        ))

plugin.Plugin('my_picture_upload', '/my_picture_upload',
              function=my_picture_upload,
              launch_thread = True,
              priority = -10, # Before student_redirection
              link=plugin.Link(html_class="verysafe",
                               where="root_rw",
                               url="javascript:picture_upload()"
                               ),
             )





