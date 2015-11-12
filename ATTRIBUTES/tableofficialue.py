#!/bin/env python3
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
#    Contact: Thierry.EXCOFFIER@bat710.univ-lyon1.fr

from . import tablemodifiable
from .. import document

class TableOfficialUE(tablemodifiable.TableModifiable):
    name = 'official_ue'
    # This value is set to True by the TEMPLATE/_ucbl_.py
    # Only the official UEs are displayed in the 'suivi'
    default_value = 0
    formatter = "function(v){return v;}"
    gui_display = "GUI_select"

    def update(self, table, old_value, new_value, page):
        """Change student table indexes."""
        for login in table.the_keys():
            if new_value:
                document.indexes_to_update.append((table, '', login))
            else:
                document.indexes_to_update.append((table, login, ''))
