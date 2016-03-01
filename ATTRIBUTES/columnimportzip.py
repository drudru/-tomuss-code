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
#    Contact: Thierry.EXCOFFIER@bat710.univ-lyon1.fr

import re
import html
from .columnfill import ColumnFill
from .. import plugin
from .. import document
from ..COLUMN_TYPES import upload

class ColumnImportZip(ColumnFill):
    name = 'import_zip'
    action = 'import_zip'
    css = """
    #popup DIV.import_zip { border: 4px solid red ; overflow:scroll ;
                            left: 10%; right: 10%; bottom: 10% ; top: 10% ;
                          }
    DIV.import_zip IFRAME { position: absolute ; width: 95%; height: 90% }
    #t_column_import_zip { background: #FAA ; }
"""

def import_zip(server):
    """
    Upload many files at once.
    """
    import zipfile
    table = document.table(server.the_year, server.the_semester,
                           server.the_ue, create=False,
                           do_not_unload='import_zip')
    if not table:
        raise ValueError("Can't find table")
    try:
        column = table.columns.from_id(server.the_path[0])
        if column.type.name != 'Upload':
            raise ValueError('Not good type')
        server.the_file.write('<p>' + server._("MSG_abj_wait") + '\n')
        zf = zipfile.ZipFile(server.uploaded['data'].file, mode="r")
        page = table.get_a_page_for((server.ticket.user_name,))
        for filename in zf.namelist():
            server.the_file.write('<br>' + html.escape(filename) + '\n')
            for name in re.split("[#:@/\\\\]", filename):
                name = name.strip()
                if name == '':
                    continue
                lines = tuple(table.get_items(name))
                if lines:
                    break
            else:
                server.the_file.write(server._("MSG_importzip_no_login"))
                continue
            if not table.authorized(server.ticket.user_name,
                                    lines[0][1][column.data_col],
                                    column=column):
                server.the_file.write('<span style="color:red">'
                                      + server._("ALERT_not_authorized")
                                      + '</span>\n')
                continue

            f = zf.open(filename, "r")
            data = f.read()
            f.close()
            upload.save_file(
                server, page, column, lines[0][0], data,
                filename.split(name)[1][1:].strip(
                           ).replace('/','_').replace("\\", "_"))

        zf.close()
    except zipfile.BadZipFile:
        server.the_file.write('<p>' + server._("MSG_not_a_zip"))
    finally:
        server.the_file.write('<p>THE END')
        table.do_not_unload_remove('import_zip')


plugin.Plugin('import_zip', '/{Y}/{S}/{U}/import_zip/{*}',
              function=import_zip, launch_thread = True,
              upload_max_size = 2000000000,
          )
