#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2012 Thierry EXCOFFIER, Universite Claude Bernard
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

import ast
import sys
from .. import data
from .. import configuration
from .. import utilities
from .. import sender

def create(table):
    p = table.new_page('' ,data.ro_user, '', '')
    table.new_page('' ,configuration.root[0], '', '')
    _ = utilities._
    table.table_attr(p, 'masters', list(configuration.root))

    table.update_columns(
        {
            '0': {'type':'Text', 'width':10, 'title': _("COL_TITLE_ct_what")},
            '1': {'type':'Text', 'width': 1, 'title': _("COL_TITLE_ct_type")},
            '2': {'type':'Text', 'width': 9, 'title': _("COL_TITLE_ct_value")},
            })

    table.table_attr(p, 'default_nr_columns', 3)
    table.table_attr(p, 'default_sort_column', 0)

def cell_change(table, page, col, lin, value, dummy_date):
    if page.page_id == 0:
        return
    line = table.lines[lin]
    if line[0].author != data.ro_user or col != '2':
        sender.append(page.browser_file,
                      '<script>Alert("ERROR_value_not_modifiable");</script>')
        raise ValueError(utilities._("ERROR_value_not_modifiable"))
    t = line[1].value
    try:
        v = ast.literal_eval(value)
    except:
        sender.append(page.browser_file, '<script>Alert(%s);</script>'
                      % utilities.js(str(sys.exc_info()[0])))
        raise
    if t != v.__class__.__name__:
        sender.append(page.browser_file,
                      '<script>Alert("ALERT_unexpected_type");</script>')
        raise ValueError(utilities._("ALERT_unexpected_type"))
