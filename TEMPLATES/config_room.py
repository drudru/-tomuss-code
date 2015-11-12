#!/usr/bin/env python3
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
from .. import configuration
from .. import utilities
from .. import files
from .. import sender
from ..PYTHON_JS import tomuss_python
from ..PYTHON_JS import places

class Room(object):
    def __init__(self, key, line):
        self.key     = key
        self.name    = line[0].value
        self.places  = line[1].value
        self.url     = line[2].value
        self.comment = line[3].value
        self.Places  = places.Places(self.places)

def create(table):
    if table.year != 0 or table.semester != 'Dossiers':
        raise ValueError('Not allowed')
    
    p = table.get_a_root_page()

    _ = utilities._
    table.update_columns({
            'a' : {'title': _("COL_TITLE_room_name"),
                   'comment': _("COL_COMMENT_room_name"),
                   'type':'Text'},
            'b' : {'title': _("COL_TITLE_room_places"),
                   'comment': _("COL_COMMENT_room_places"),
                   'type':'Text'},
            'c' : {'title': _("COL_TITLE_room_url"),
                   'comment': _("COL_COMMENT_room_url"),
                   'type':'URL'},
            'd' : {'title': _("COL_TITLE_room_comment"),
                   'comment': _("COL_COMMENT_room_comment"),
                   'type':'Text'},
            })
    table.table_attr(p, 'masters', list(configuration.root))
    table.table_attr(p, 'default_sort_column', [1,0])
    table.table_attr(p, 'default_nr_columns', 4)
    table.table_attr(p, 'comment', _("COL_COMMENT_config_room"))

def rooms_list(table):
    return [Room(key, line)
            for key, line in table.lines.items()
            if line[0].value != ""
        ]

def init(table):
    table.do_not_unload_add('*config_room')
    table.rooms_list = rooms_list


def onload(table):
    make_json(table)

def make_json(table):
    s = []
    for line in table.lines.values():
        if line[0].value:
            s.append((line[0].value, line[1].value,
                      line[2].value, line[3].value))
    files.files['types.js'].append("config_room",
                                   'var rooms = ' + json.dumps(s) + ';\n')

def cell_change(table, page, col, dummy_lin, value, dummy_date):
    if (col == 'c'
        and value != ''
        and not value.startswith(('http:', 'https:'))):
        sender.append(page.browser_file,
        '''<script>alert("http: " + _("or") + " https:\\n\\n" + _("ALERT_column_not_saved"));</script>''')
        raise ValueError("URL")
    # Not now because the cell value is not yet stored
    utilities.start_job(lambda: make_json(table), 1)
