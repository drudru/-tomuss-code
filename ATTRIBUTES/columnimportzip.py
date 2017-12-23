#!/bin/env python3
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2015-2017 Thierry EXCOFFIER, Universite Claude Bernard
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
import re
import html
import glob
import subprocess
import PyPDF2
from .columnfill import ColumnFill
from .. import sender
from .. import plugin
from .. import document
from .. import configuration
from .. import utilities
from ..COLUMN_TYPES import upload

class ColumnImportZip(ColumnFill):
    name = 'import_zip'
    action = 'import_zip'
    css = """
    #popup DIV.import_zip { border: 4px solid red ; overflow:scroll ;
                            left: 10%; right: 10%; bottom: 10% ; top: 10% ;
                          }
    #popup DIV.import_zip H2 { margin-top: 0.5em ; }
    #t_column_import_zip { background: #FAA ; }
"""

def name(column):
    return "{}_{}_{}_{}".format(column.table.year,
                                column.table.semester,
                                column.table.ue,
                                column.the_id)

def upload_pdf(server):
    table = document.table(server.the_year, server.the_semester,
                           server.the_ue, create=False)
    column = table.columns.from_id(server.the_path[0])
    tmp = server.ticket.temporary_directory_get(name(column))
    page = table.pages[server.the_page]
    assert(server.ticket.user_name == page.user_name)
    
    for line_id in server.uploaded:
        line = table.lines[line_id]
        first, nb = server.uploaded.getfirst(line_id).split('\001')
        first = int(first)
        nb = int(nb)
        server.the_file.write("{} : {}-{}<br>".format(line[0].value,
                                                      first, first+nb-1))
        joiner = ["pdfunite"]
        for i in range(first, first+nb):
            joiner.append(os.path.join(tmp, "p{:06d}.pdf".format(i)))
        output = os.path.join(tmp, line_id + '.pdf')
        joiner.append(output)
        process = subprocess.Popen(joiner)
        process.wait()
        with open(output, "rb") as f:
            upload.save_file(server, page, column, line_id, f, column.title)
        server.the_file.write('<hr>')
    server.the_file.write('THE END')

def import_pdf(server, table, column):
    full_pdf = PyPDF2.PdfFileReader(server.uploaded['data'].file)
    server.the_file.write(
    "window.importPDF = new window.parent.ImportPDF({},{}) ;"
                .format(utilities.js(name(column)), full_pdf.getNumPages()))
    dirname = server.ticket.temporary_directory_get(name(column), erase=True)
    for page_number in range(full_pdf.getNumPages()):
        pdf = os.path.join(dirname, "p{:06d}.pdf".format(page_number+1))
        page = full_pdf.getPage(page_number)
        output = PyPDF2.PdfFileWriter()
        output.addPage(page)
        with open(pdf, "wb") as f:
            output.write(f)
        print(pdf)
        process = subprocess.Popen(['pdftoppm', '-png',
                                      '-singlefile',
                                      '-r', '100',
                                      pdf, pdf.replace(".pdf", "")
                         ]).wait()
        server.the_file.write('window.importPDF.add();')
    
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
        if server.uploaded['data'].filename.lower().endswith(".pdf"):
            import_pdf(server, table, column)
            return
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
        server.the_file.write('<p>THE END')
    except zipfile.BadZipFile:
        server.the_file.write('<p>' + server._("MSG_not_a_zip"))
    finally:
        table.do_not_unload_remove('import_zip')


plugin.Plugin('import_zip', '/{Y}/{S}/{U}/import_zip/{*}',
              function=import_zip, launch_thread = True,
              upload_max_size = 2000000000,
          )

plugin.Plugin('upload_pdf', '/{Y}/{S}/{U}/upload_pdf/{P}/{*}',
              function=upload_pdf, launch_thread = True,
              upload_max_size = 200000,
          )

def tmp(server):
    n = server.ticket.temporary_directory_name(os.path.join(*server.the_path))
    server.do_not_close_connection()
    with open(n, "rb") as f:
        c = f.read()
        sender.append(server.the_file, c, keep_open=False)

plugin.Plugin('tmp', '/tmp/{*}',
              function=tmp, mimetype="image/png"
          )
