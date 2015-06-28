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

import json
import collections
from .. import plugin
from .. import document

def get_columns(server):
    """Return the column definition of the table"""
    t = document.table(server.the_year, server.the_semester, server.the_ue,
                       create=False)
    if t:
        grp_seq = collections.defaultdict(int)
        grp_col = t.columns.get_grp()
        seq_col = t.columns.get_seq()
        if grp_col and seq_col:
            for line in t.lines.values():
                if line[0].value:
                    grp_seq[line[seq_col].value + '/' + line[grp_col].value
                    ] += 1
        server.the_file.write(t.columns.js(hide=False)
                              + 'the_columns(columns,%s);'
                              % json.dumps(grp_seq))
    else:
        server.the_file.write('the_columns([], []);')

plugin.Plugin('get_columns', '/{Y}/{S}/{U}/get_columns',
              function=get_columns,
              group='staff',
              mimetype = 'application/x-javascript',
              unsafe=False,
              )
