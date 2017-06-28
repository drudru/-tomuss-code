#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet)
#    Copyright (C) 2009-2011 Thierry EXCOFFIER, Universite Claude Bernard
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

import os
import glob
import ast
from .. import plugin
from .. import utilities
from .. import tablestat
from .. import document
from .. import column
from .. import cell

def read():
    for filename in glob.glob(os.path.join("DB", "LOGINS", "*", "*",
                                           "preferences")):
        d = ast.literal_eval(utilities.read_file(filename)
                             .replace("OUI", "1")
                             .replace("NON", "0")
                             .replace("N", "0")
                         )
        yield (filename.split(os.path.sep)[-2], d)

def preferences(server):
    """Join of all the preferences table"""

    lines = []
    for login, d in read():
        for k, v in d.items():
            lines.append(cell.Line((cell.CellValue(login),
                                    cell.CellValue(k),
                                    cell.CellValue(v))))
    columns = [
        column.Column('0', '', freezed='F', width=6,
                      title=server._('COL_TITLE_ID')),
        column.Column('1', '', freezed='F', width=2,
                      title=server._('COL_TITLE_ATTRIBUTE')),
        column.Column('2', '', freezed='F', width=2,
                      title=server._('COL_TITLE_VALUE')),
        ]

    document.virtual_table(server, columns, lines,
                           table_attrs={
            'default_nr_columns': 3,
            'comment': server._('LINK_preferences'),
            })

plugin.Plugin('preferences', '/stat_preferences',
              function=preferences, group='roots',
              launch_thread = True,
              link=plugin.Link(where="informations", html_class="verysafe",
                               # Should be the last semester
                               url="javascript:go_suivi('stat_preferences')",
                               priority = 1000,
                   ),
              )






