#!/bin/env python3
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
import html
from .. import utilities
from .. import plugin
from .. import document
from . import text

def container_path(column):
    return os.path.join('UPLOAD', str(column.table.year),
                        column.table.semester, column.table.ue,
                        column.the_id)

def length(stream):
    stream.seek(0, 2)
    size = stream.tell()
    stream.seek(0)
    return size

class Upload(text.Text):
    type_type = 'computed'
    attributes_visible = ('rounding', 'weight', 'upload_max', 'upload_zip',
                          'groupcolumn', 'import_zip')
    ondoubleclick = 'upload_double_click'
    formatte_suivi = 'upload_format_suivi'
    human_priority = 20


class HackClamd:
    """Pyclamd does not allow to use an open file"""
    def __init__(self, stream):
        self.stream = stream
        self.length = length(stream)
    def __getitem__(self, item):
        if self.length == 0:
            return ''
        if item.start == 0:
            x = self.stream.read(min(self.length, item.stop))
            self.length -= len(x)
            return x
        return self
    def __len__(self):
        return self.length

def check_virus(data):
    utilities.warn("SCAN: INIT")
    try:
        import pyclamd
        pc = pyclamd.ClamdUnixSocket()
    except:
        utilities.warn("SCAN: CAN'T CONNECT TO CLAMAV")
        return '' # Not installed or not running
    utilities.warn("SCAN: START")
    if isinstance(data, str):
        res = pc.scan_stream(data)
    else:
        res = pc.scan_stream(HackClamd(data))
    utilities.warn("SCAN: STOP %s" % res)
    if res:
        return repr(res)
    else:
        return ''

def copy_stream(instream, outstream):
    n = 0
    while True:
        a = instream.read(4096)
        if a == b"":
            break
        n += len(a)
        outstream.write(a)
    outstream.close()
    return n

def save_file(server, page, column, lin_id, data, filename):
    # Search a student with yet a downloaded file
    table = column.table
    line = table.lines[lin_id]
    path = container_path(column)
    for a_lin_id, a_line in column.lines_of_the_group(line):
        if (a_line[column.data_col].comment != ''
            and os.path.exists(os.path.join(path, a_lin_id))
        ):
            if table.authorized(page.user_name, line[column.data_col],
                                column, a_line):
                server.the_file.write("<p>→ %s %s<p>" % (
                    html.escape(a_line[1].value),
                    html.escape(a_line[2].value)))
                lin_id = a_lin_id
                break
            else:
                utilities.send_backtrace(
                    "{}<br>{}→{}".format(column, lin_id, a_lin_id),
                    "UPLOAD failed"
                )

    err = check_virus(data)
    if err:
        server.the_file.write(
            '<span style="background:#F00;color:#FFF">%s %s</span>\n'
            % (server._("MSG_virus_found"), html.escape(err)))
        return err
    server.the_file.write(server._("MSG_no_virus_found") + '\n')
    path = container_path(column)
    utilities.mkpath(path, create_init=False)
    file_path = os.path.join(path, lin_id)
    if os.path.exists(file_path):
        os.rename(file_path, file_path + '~')

    if isinstance(data, bytes):
        f = open(file_path, "wb")
        n = len(data)
        f.write(data)
        f.close()
    else:
        data.seek(0) # because check_virus read it
        f = open(file_path, "wb")
        n = copy_stream(data, f)
        data.close() # Free FieldStorage

    server.the_file.write('<br><span>%s %s</span>\n' %
                          (server._("MSG_upload_size"), n))

    magic = subprocess.check_output(["file", "--mime", file_path])
    magic = magic.decode("utf-8").split(": ", 1)[1].strip()
    server.the_file.write('<br><span>%s %s<span>\n'
                          % (server._("MSG_upload_type"), html.escape(magic)))
    table.lock()
    try:
        table.cell_change   (page, column.the_id, lin_id, n/1000.)
        table.comment_change(page, column.the_id, lin_id, magic+' '+filename)
    finally:
        table.unlock()

def upload_post(server):
    data = server.uploaded
    if data is None or 'data' not in data:
        server.the_file.write(server._('MSG_bad_ticket'))
        return

    err = document.get_cell_from_table(server, ('Upload',))
    if isinstance(err, str):
        server.the_file.write(err)
        server.close_connection_now()
        return
    table, page, column, lin_id = err
    try:
        filename = data.getfirst("filename").replace("\\", "/").split("/")[-1]
        stream = data["data"].file

        server.the_file.write('<p><b>' + html.escape(filename) + '</b>\n')
        size = length(stream)

        if size > float(column.upload_max) * 1000:
            server.the_file.write('<p style="color:red">%s %d &gt; %d\n'
                                  % (server._("MSG_upload_fail_max"),
                                     size, float(column.upload_max)*1000))
            return
        err = save_file(server, page, column, lin_id, stream, filename)
        if not err:
            server.the_file.write('<p>' + server._("MSG_upload_stop"))
    finally:
        table.do_not_unload_remove('cell_change')

def upload_get(server):
    err = document.get_cell_from_table_ro(server, ('Upload',))
    if isinstance(err, str):
        server.send_response(200)
        server.send_header('Content-Type', 'text/plain; charset=utf-8')
        server.end_headers()
        server.the_file.write(err.encode("utf-8"))
        raise ValueError(err)
    table, column, lin_id = err
    path = container_path(column)
    line = table.lines[lin_id]
    for a_lin_id, a_line in ((lin_id, line),
                            ) + tuple(column.lines_of_the_group(line)):
        file_path = os.path.join(path, a_lin_id)
        try:
            f = open(file_path, "rb")
            mime = a_line[column.data_col].comment
            mime = mime.replace("; ", ";").split(' ')[0].strip()
            server.send_response(200)
            server.send_header('Content-Type', mime)
            server.end_headers()
            copy_stream(f, server.the_file)
            f.close()
            return
        except IOError:
            data = server._("MSG_upload_no_file")
            mime = "text/plain; charset=utf-8"
    server.send_response(200)
    server.send_header('Content-Type', mime)
    server.end_headers()
    server.the_file.write(data.encode("utf-8"))

plugin.Plugin('upload_post', '/{Y}/{S}/{U}/upload_post/{*}',
              function=upload_post, launch_thread = True,
              upload_max_size = 40000000,
              priority = -10 # Before student_redirection
          )

plugin.Plugin('upload_get', '/{Y}/{S}/{U}/upload_get/{*}',
              function=upload_get, launch_thread = True,
              mimetype=None,
              priority = -10 # Before student_redirection
          )
