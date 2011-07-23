#!/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2008,2010 Thierry EXCOFFIER, Universite Claude Bernard
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

import note
import text
import configuration

class Bool(note.Note):
    human_priority = 1
    full_title = 'Booléen'
    tip_cell = "Booléen, tapez O : oui, N : non"
    cell_test = 'test_bool'
    formatte = text.Text.formatte
    ondoubleclick = 'toggle_bool'
    tip_filter = "Vous pouvez indiquer <b>O</b> ou <b>N</b> comme filtre."
    should_be_a_float = 0

    def cell_indicator(self, column, value, cell, lines):
        return '', None

    def formatter(self, column, value, cell, lines, teacher, ticket, line_id):
        if column.is_modifiable(teacher):
            v = '<select class="hidden" onchange="_cell(this,\'%s/=%s/%d/%s/%s/cell/%s/%s\');">' % (
                configuration.server_url,
                ticket,
                column.table.year, column.table.semester,
                column.table.ue, column.the_id, line_id)
            for i in ('', 'OUI', 'NON'):
                if i == value:
                    sel = ' selected="1"'
                else:
                    sel = ""
                v += '<option value="%s" %s>%s</option>' % (i, sel, i)
            v += '</select>'
        else:
            v = value

        return (v, '', '')
