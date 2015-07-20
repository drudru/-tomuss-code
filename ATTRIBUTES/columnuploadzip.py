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
#    Contact: Thierry.EXCOFFIER@bat710.univ-lyon1.fr

from .columnfill import ColumnFill
from .. import plugin
from .. import document
from .. import utilities
from ..COLUMN_TYPES import upload


class ColumnUploadZip(ColumnFill):
    name = 'upload_zip'
    action = 'upload_zip'


def upload_zip(server):
    import zipfile
    import os
    import tempfile
    table = document.table(server.the_year, server.the_semester,
                           server.the_ue, create=False)
    if not table:
        raise ValueError("Can't find table")
    column = table.columns.from_id(server.the_path[0])
    dirname = upload.container_path(column)
    f, name = tempfile.mkstemp()
    zf = zipfile.ZipFile(os.fdopen(f, "w"),
                         mode="w", compression=zipfile.ZIP_DEFLATED)
    for lin_id in server.the_path[1:-1]:
        if lin_id not in table.lines:
            continue
        line = table.lines[lin_id]
        filename = os.path.join(dirname, lin_id)
        if os.path.exists(filename):
            zf.write(
                filename,
                "%d_%s_%s_%s" % (table.year, table.semester, table.ue,
                                 column.title.replace('/','_'))
                + '/' + line[0].value + "_" + line[1].value + '_' + line[2].value
                + '_' + line[column.data_col].comment.replace("; ", ";"
                                                          ).split(' ',1)[1]
            )
    zf.close()
    f = open(name, "r")
    while True:
        c = f.read(1000000)
        if c == '':
            break
        else:
            server.the_file.write(c)
    f.close()
    os.unlink(name)

plugin.Plugin('upload_zip', '/{Y}/{S}/{U}/upload_zip/{*}',
              function=upload_zip, launch_thread = True,
              mimetype="application/zip",
          )
