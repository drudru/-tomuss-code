#!/usr/bin/env python
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

import re
from .. import configuration
from .. import utilities
from .. import sender

splitter = re.compile('[ \t\n]+')

def create(table):
    if table.year != 0 or table.semester != 'Dossiers':
        raise ValueError('Not allowed')
    
    p = table.get_a_root_page()

    _ = utilities._
    table.update_columns({
            'a' : {'title': _("COL_TITLE_login_major"),
                   'comment': _("COL_COMMENT_login_major"),
                   'type':'Text'},
            'b' : {'title': _("COL_TITLE_login_minor"),
                   'comment': _("COL_COMMENT_login_minor"),
                   'type':'Text'},
            'c' : {'title': _("COL_TITLE_acls_comment"),
                   'comment': _("COL_COMMENT_acls_comment"),
                   'type':'Text'},
            })
    table.table_attr(p, 'masters', list(configuration.root))
    table.table_attr(p, 'default_sort_column', [1,0])
    table.table_attr(p, 'default_nr_columns', 3)
    table.table_attr(p, 'private', 1)
    table.table_attr(p, 'comment', _("COL_COMMENT_config_login"))

def init(table):
    major_of.table = table
    configuration.major_of = major_of
    table.do_not_unload_add('*config_login')

@utilities.add_a_cache
def major_of(login):
    minors = set()
    for line in major_of.table.lines.values():
        if login in splitter.split(line[0].value):
            minors.update(splitter.split(line[1].value.strip()))
    minors.discard(login)
    return list(minors)

def cell_change(table, page, col, lin, value, dummy_date):
    if col not in 'ab':
        return
    for login in splitter.split(value):
        if not configuration.is_member_of(login, 'staff'):
            sender.append(page.browser_file,
                          '<script>alert(_("ALERT_bad_login")+%s);</script>'
                          % utilities.js(login))
    major_of.cache = {}
