#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2016 Thierry EXCOFFIER, Universite Claude Bernard
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

import ast
from .. import configuration
from .. import utilities

def create(table):
    if table.year != 0 or table.semester != 'Dossiers':
        raise ValueError('Not allowed')
    
    _ = utilities._
    p = table.get_a_root_page()
    table.update_columns({
            'a' : {'title': _("COL_TITLE_messages_order"),
                   'comment': _("COL_COMMENT_messages_order"),
                   'type':'Note'},
            'b' : {'title': _("COL_TITLE_messages_group"),
                   'comment': _("COL_COMMENT_messages_group"),
                   'type':'Text', 'width': 10},
            'c' : {'title': _("COL_TITLE_messages"),
                   'comment': _("COMMENT_messages"),
                   'type':'Text', 'width': 20},
            })
    table.table_attr(p, 'masters', list(configuration.root))
    table.table_attr(p, 'default_sort_column', [1,0])
    table.table_attr(p, 'default_nr_columns', 3)
    table.table_attr(p, 'comment', _("COMMENT_messages"))

def get_messages(table, login):
    if table.messages_cache is None:
        messages = [(line[0].value,
                     ast.literal_eval(line[1].value),
                     line[2].value)
                    for line in table.lines.values()
                    if line[0].value != ''
                    and line[1].value != ''
                    and line[2].value != '']
        messages.sort()
        # Remove priority
        table.messages = [message[1:]  for message in messages]

    return [
        message
        for groupes, message in table.messages
        if configuration.is_member_of(login, groupes)
    ]
    
def init(table):
    table.do_not_unload_add('*config_messages')
    table.messages_cache = None
    configuration.get_messages = lambda login: get_messages(table, login)

def cell_change(table, dummy_page, dummy_col, dummy_lin, value, dummy_date):
    table.messages_cache = None
    configuration.tell_to_reload_config()
