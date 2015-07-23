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
    attributes_visible = ('rounding', 'weight', 'upload_max', 'upload_zip',
                          'groupcolumn', 'import_zip')
    ondoubleclick = 'upload_double_click'
    formatte_suivi = 'upload_format_suivi'
    human_priority = 20

def check_virus(data):
    try:
        import pyclamd
        pc = pyclamd.ClamdUnixSocket()
    except:
        return '' # Not installed or not running

    res = pc.scan_stream(data)
    del pc
    if res:
        return ', '.join(res.values())
    else:
        return ''

def save_file(server, page, column, lin_id, data, filename):
    err = check_virus(data)
    if err:
        server.the_file.write(
            '<span style="background:#F00;color:#FFF">%s %s</span>\n'
            % (server._("MSG_virus_found"), cgi.escape(err)))
        return
    server.the_file.write(server._("MSG_no_virus_found") + '\n')
    path = container_path(column)
    utilities.mkpath(path, create_init=False)
    file_path = os.path.join(path, lin_id)
    if os.path.exists(file_path):
        os.rename(file_path, file_path + '~')
    utilities.write_file(file_path, data)

    server.the_file.write('- <span>%s %s</span>\n' %
                          (server._("MSG_upload_size"), len(data)))

    magic = subprocess.check_output(["file", "--mime", file_path])
    magic = magic.split(": ", 1)[1].strip()
    server.the_file.write('- <span>%s %s<span>\n'
                          % (server._("MSG_upload_type"), cgi.escape(magic)))
    table = column.table
    table.lock()
    try:
        table.cell_change   (page, column.the_id, lin_id, len(data)/1000.)
        table.comment_change(page, column.the_id, lin_id, magic+' '+filename)
    finally:
        table.unlock()

def upload_post(server):
    err = document.get_cell_from_table(server, ('Upload',))
    if isinstance(err, basestring):
        server.the_file.write(err)
        raise ValueError(err)
    table, page, column, lin_id = err
    try:
        server.the_file.write(server._("MSG_abj_wait"))
        data = server.get_posted_data()
        if data is None or 'data' not in data:
            server.the_file.write("BUG")
            return
        filename = data["filename"][0].replace("\\", "/").split("/")[-1]
        data = data["data"][0]

        server.the_file.write('<p><b>' + cgi.escape(filename) + '</b>\n')

        if len(data) > float(column.upload_max) * 1000:
            server.the_file.write('<p style="color:red">%s %d &gt; %d\n'
                                  % (server._("MSG_upload_fail_max"),
                                     len(data), float(column.upload_max)*1000))
            return
        save_file(server, page, column, lin_id, data, filename)
        server.the_file.write('<p>' + server._("MSG_upload_stop"))
    finally:
        table.do_not_unload_remove('cell_change')
        server.close_connection_now()

def upload_get(server):
    err = document.get_cell_from_table_ro(server, ('Upload',))
    server.restore_connection()
    if isinstance(err, basestring):
        server.send_response(200)
        server.send_header('Content-Type', 'text/plain; charset=utf-8')
        server.end_headers()
        server.the_file.write(err)
        raise ValueError(err)
    table, column, lin_id = err
    path = container_path(column)
    line = table.lines[lin_id]
    for a_lin_id, a_line in ((lin_id, line),
                            ) + tuple(column.lines_of_the_group(line)):
        file_path = os.path.join(path, a_lin_id)
        try:
            data = utilities.read_file(file_path)
            mime = a_line[column.data_col].comment
            mime = mime.replace("; ", ";").split(' ')[0].strip()
            break
        except IOError:
            data = server._("MSG_upload_no_file")
            mime = "text/plain; charset=utf-8"
    server.send_response(200)
    server.send_header('Content-Type', mime)
    server.end_headers()
    server.the_file.write(data)

plugin.Plugin('upload_post', '/{Y}/{S}/{U}/upload_post/{*}',
              function=upload_post, launch_thread = True,
              priority = -10 # Before student_redirection
          )

plugin.Plugin('upload_get', '/{Y}/{S}/{U}/upload_get/{*}',
              function=upload_get, launch_thread = True,
              mimetype=None,
              priority = -10 # Before student_redirection
          )
