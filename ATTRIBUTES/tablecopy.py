#!/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2011-2013 Thierry EXCOFFIER, Universite Claude Bernard
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

from .tableexport import TableExport
from .. import utilities
from .. import document
from .. import plugin
from .. import configuration

class TableCopy(TableExport):
    default_value = 1
    name = 't_copy'
    action = 'table_copy'
    gui_display = "GUI_a"
    css = """
DIV.import_export TABLE.table_copy_diagram {
 width: 10%; border-spacing:0.4em; margin: auto; background: #CCC }
TABLE.table_copy_diagram TD { text-align: center; vertical-align: middle; }
TABLE.table_copy_diagram TH { background: white ; border: 1px solid #888; }
    """

##################################### PLUGIN ################################

def tablecopy(server):
    """Copy the table in another EMPTY one"""
    _ = utilities._

    server.the_file.write(_("MSG_tablecopy_start") + "\n")
    table = document.table(server.the_year, server.the_semester,
                           server.the_ue, None, None)
    server.the_file.write(_("MSG_tablecopy_read") + "\n")

    dest_year = int(server.the_path[0])
    dest_semester = utilities.safe(server.the_path[1]).replace('.','_')
    option = server.the_path[2]
    if len(server.the_path) == 4 and len(server.the_path[3]):
        newname = utilities.safe(server.the_path[3])
    else:
        newname = server.the_ue
        if dest_year == server.the_year and dest_semester==server.the_semester:
            server.the_file.write(_("MSG_tablecopy_cant") + "\n")
            return

    dest_table = document.table(dest_year,dest_semester, newname, create=False)
    if dest_table:
        if not dest_table.empty(empty_even_if_used_page=True,
                                empty_even_if_created_today=True,
                                empty_even_if_column_created=True)[0]:
            server.the_file.write(_("MSG_tablecopy_not_empty") + "\n")
            return
        dest_table.delete()

    if option == 'history':
        c = utilities.read_file(table.filename)
    elif option == 'content':
        c = table.rewrite()
    elif option == 'columns':
        c = table.rewrite(only_columns=True)
    else:
        server.the_file.write("\nBUG: '%s'." % option)
        return

    filename = document.table_filename(dest_year, dest_semester, newname)
    try:
        utilities.write_file_safe(filename, c)
    except IOError:
        server.the_file.write(_("MSG_tablecopy_cant") + "\n")
        return
        
    server.the_file.write(_("MSG_tablecopy_check") % (len(c)/1024.) + "\n")
    dest_table = document.table(dest_year,dest_semester, newname, create=False)

    for name in dest_table.masters:
        dest_table.master_of_update('+', name)

    server.the_file.write("\n" + _("MSG_tablecopy_done") + "\n")
    url = "%s/%s/%s/%s" % (configuration.server_url,
                             dest_year, dest_semester, newname)
    server.the_file.write(url + '\n')

plugin.Plugin('tablecopy', '/{Y}/{S}/{U}/tablecopy/{*}',
              function=tablecopy, group='staff',
              mimetype = "text/plain; charset=UTF-8",
              )
