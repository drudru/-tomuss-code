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

import math
from . import text
from .. import configuration

if not hasattr(math, 'isnan'):
    math.isnan = lambda x: not x<0 and not x>=0

class Note(text.Text):
    attributes_visible = ('minmax', 'weight', 'rounding', 'repetition',
                          'url_import')
    human_priority = -10
    tip_filter = "TIP_filter_Note"
    tip_cell = "TIP_cell_Note"
    cell_test = "test_note"
    formatte = 'note_format'
    formatte_suivi = 'note_format_suivi'
 
    should_be_a_float = 1

    message = """<script>Write("MSG_Note_ABINJ");</script>"""

    def cell_indicator_prst(self, column, value, cell, lines):
        if value == configuration.abi or value == configuration.abi_short:
            return 'abinj', 0
        if value == configuration.tnr or value == configuration.tnr_short:
            return 'tnr', 0
        if value == configuration.abj or value == configuration.abj_short:
            return 'abjus', None
        if value == configuration.pre or value == configuration.pre_short:
            return 'prst', 1
        if value == '' and lines:
            nr_abinj = len([c for c in lines if c[column.data_col].value ==''])
            if nr_abinj / float(len(lines)) < configuration.abinj:
                return 'abinj2', 0

        return '', None

    def cell_indicator(self, column, value, cell, lines):
        if column.weight.startswith('+') or column.weight.startswith('-'):
            return '', None

        classname = self.cell_indicator_prst(column, value, cell, lines)
        if classname[0]:
            return classname

        try:
            value = float(value)
        except ValueError:
            return '', None

        if math.isnan(value):
            return '', None

        v_min, v_max = column.min_max()
        ci = (value - v_min) / (v_max - v_min)
        if   ci > 0.8: return 'verygood', ci
        elif ci > 0.6: return 'good', ci
        elif ci > 0.4: return 'mean', ci
        elif ci > 0.2: return 'bad', ci
        else: return 'verybad', ci

    def stat(self, column, value, cell, lines):
        """Returns a dict of various values, currently:
        'rank', 'rank_grp', 'average'
        """

        all_floats, floats = column.cell_values(lines)
        floats.sort()
        floats.reverse()
        all_floats.sort()
        all_floats.reverse()

        d = {"nr": len(all_floats),
             "nr_in_grp": len(floats),
             }
        try:
            d["rank"] = all_floats.index(value)
        except ValueError:
            pass
        try:
            d["rank_grp"] = floats.index(value)
        except ValueError:
            pass
        if all_floats:
            d["average"] = sum(all_floats) / len(all_floats)
            d["mediane"] = all_floats[len(all_floats)//2]
        return d

    def value_range(self, v_min, v_max):
        if v_min == 0:
            return '/%g' % v_max
        else:
            return '[%g;%g]' % (v_min, v_max)
