#!/bin/env python3
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2017 Thierry EXCOFFIER, Universite Claude Bernard
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
from ..column import ColumnAttr
from .. import configuration
from .. import utilities

class ColumnPrivate(ColumnAttr):
    name = 'private'
    update_table_headers = 1
    check_and_set = 'test_nothing'

    def encode(self, value):
        if isinstance(value, str):
            value = value.strip()
            if value == '':
                return []
            return re.split(' +', value.strip().lower())
        else:
            return value

    def check(self, value):
        value = self.encode(value)
        if hasattr(configuration, 'is_member_of'):
            for login in value:
                if not configuration.is_member_of(login, 'staff'):
                    return '_("ALERT_bad_login") + ' + utilities.js(login)


    css = """#menutop DIV.tabs #t_column_private { width: 75% }
#t_column_private.empty {
  background-image: url('private.png');
}
"""
