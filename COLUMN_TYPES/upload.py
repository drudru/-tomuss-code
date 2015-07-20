#!/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2015 Thierry EXCOFFIER, Universite Claude Bernard
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

"""
Charger plusieurs fichiers
Effacer les fichiers
doc
"""

import os
import subprocess
import cgi
from .. import utilities
from .. import plugin
from .. import document
from . import text

def container_path(column):
    return os.path.join('UPLOAD', str(column.table.year),
                        column.table.semester, column.table.ue,
                        column.the_id)

class Upload(text.Text):
    type_type = 'computed'
    attributes_visible = ('rounding', 'weight', 'upload_max', 'upload_zip')
    ondoubleclick = 'upload_double_click'
    formatte_suivi = 'upload_format_suivi'
    human_priority = 20

def get_cell_from_table(server, allowed_types, ro=False):
    """server.the_path must starts by 'col_id/lin_id'
    Return an error string or the tuple (table, page, column, lin_id)
    Once the cell value is modified, call:
         table.do_not_unload_remove('cell_change')
    """
    table = document.table(server.the_year, server.the_semester,
                           server.the_ue, create=False)
    if not table:
        return "Can't find table"
    col_id = server.the_path[0]
    lin = server.the_path[1]
    column = table.columns.from_id(col_id)
    if not column:
        return "Can't find column"
    if column.type.name not in allowed_types:
        return "Not an %s column type" % allowed_types
    if (not server.ticket.is_a_teacher
        and table.the_keys()[server.ticket.user_name][0] != lin):
        return 'Your are not allowed to read/modify this value'
    if ro:
        return table, column, lin
    if not column.is_modifiable(server.ticket.is_a_teacher,
                                server.ticket,
                                table.lines[lin][column.data_col]):
        return "Not modifiable value"

    table, page = document.table(server.the_year, server.the_semester,
                                 server.the_ue, None, server.ticket,
                                 do_not_unload='cell_change')
    return table, page, column, lin

def upload_post(server):
    err = get_cell_from_table(server, ('Upload',))
    if isinstance(err, basestring):
        server.the_file.write(err)
        raise ValueError(err)
    table, page, column, lin_id = err
    try:
        server.the_file.write('<h1>%s</h1>' % server._("MSG_upload_start"))
        data = server.get_posted_data()
        if data is None or 'data' not in data:
            server.the_file.write("BUG")
            return
        filename = data["filename"][0]
        data = data["data"][0]

        server.the_file.write('<b>' + cgi.escape(filename) + '</b>')

        if len(data) > float(column.upload_max) * 1000:
            server.the_file.write('<p style="color:red">%s %d &gt; %d'
                                  % (server._("MSG_upload_fail_max"),
                                     len(data), float(column.upload_max) * 1000))
            return

        path = container_path(column)
        utilities.mkpath(path, create_init=False)
        file_path = os.path.join(path, lin_id)
        utilities.write_file(file_path, data)

        server.the_file.write('<p>%s %s' % (server._("MSG_upload_size"),
                                            len(data)))

        magic = subprocess.check_output(["file", "--mime", file_path])
        magic = magic.split(": ", 1)[1]
        server.the_file.write('<p>%s %s' % (server._("MSG_upload_type"),
                                            cgi.escape(magic)))
        
        table.lock()
        try:
            table.cell_change(page, column.the_id, lin_id, len(data)/1000.)
            table.comment_change(page, column.the_id, lin_id, magic + ' ' + filename)
        finally:
            table.unlock()
    finally:
        table.do_not_unload_remove('cell_change')
        server.close_connection_now()


def upload_get(server):
    err = get_cell_from_table(server, ('Upload',), ro=True)
    server.restore_connection()
    if isinstance(err, basestring):
        server.send_response(200)
        server.send_header('Content-Type', 'text/plain; charset=utf-8')
        server.end_headers()
        server.the_file.write(err)
        raise ValueError(err)
    table, column, lin_id = err
    path = container_path(column)
    file_path = os.path.join(path, lin_id)

    server.send_response(200)
    server.send_header('Content-Type',
                       table.lines[lin_id][column.data_col].comment
                       .replace("; ", ";").split(' ')[0])
    server.end_headers()
    server.the_file.write(utilities.read_file(file_path))

plugin.Plugin('upload_post', '/{Y}/{S}/{U}/upload_post/{*}',
              function=upload_post, launch_thread = True,
              priority = -10 # Before student_redirection
          )

plugin.Plugin('upload_get', '/{Y}/{S}/{U}/upload_get/{*}',
              function=upload_get, launch_thread = True,
              mimetype=None,
              priority = -10 # Before student_redirection
          )
