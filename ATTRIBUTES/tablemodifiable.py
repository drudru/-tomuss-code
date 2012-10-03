#!/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2008-2011 Thierry EXCOFFIER, Universite Claude Bernard
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

from ..column import TableAttr

class TableModifiable(TableAttr):
    name = 'modifiable'
    default_value = 1
    update_headers = 1
    gui_display = "GUI_select"
    formatter = "table_modifiable_toggle"
    css = "#tablemodifiableFB {color: #F00; border:0}"

    def encode(self, value):
        return int(value)
    def check(self, value):
        try:
            value = int(value)
        except ValueError:
            return self.check_error(value)
        if value == 0 or value == 1:
            return
        return self.check_error(value)
    def update(self, table, old_value, new_value, page):
        if not new_value:
            return # Not modifiable
        if old_value:
            return # Was yet modifiable : no change
        # Become modifiable
        if page.logged:
            return # Page defined on disc
        # Need to store the unlogged pages.
        for i, p in enumerate(table.pages):
            if p.logged:
                continue
            table.log('new_page(%s ,%s, %s, %s, %s) # %d' % (
                repr(p.ticket),
                repr(p.user_name),
                repr(p.user_ip),
                repr(p.user_browser),
                repr(p.date),
                i,
                ))
            p.logged = True
