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

from . import note
from . import text

class Bool(note.Note):
    human_priority = 1
    tip_cell = "TIP_cell_Bool"
    cell_test = 'test_bool'
    formatte = text.Text.formatte
    formatte_suivi = 'bool_format_suivi'
    ondoubleclick = 'toggle_bool'
    tip_filter = "TIP_filter_Bool"
    should_be_a_float = 0
    attributes_visible = ('url_import',)
    cell_completions = "bool_completions"

    def cell_indicator(self, column, value, cell, lines):
        return '', None

    def stat(self, column, value, cell, lines):
        return {}
