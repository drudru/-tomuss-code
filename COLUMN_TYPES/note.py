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

import text
import cgi
import configuration
import math

if not hasattr(math, 'isnan'):
    math.isnan = lambda x: not x<0 and not x>=0

class Note(text.Text):
    attributes_visible = ('minmax', 'weight', 'rounding')
    human_priority = -10
    tip_filter = "TIP_filter_Note"
    tip_cell = "TIP_cell_Note"
    cell_test = "test_note"
    formatte = 'note_format'

    should_be_a_float = 1

    message = """<script>Write("MSG_Note_ABINJ");</script>"""

    def cell_indicator_prst(self, column, value, cell, lines):
        if value == configuration.abi or value == configuration.abi_short:
            return 'abinj', 0
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

    def test_ok(self, test):
        if not test.startswith('['):
            return False
        if not test.endswith(']'):
            return False
        test = test[1:-1].split(';')
        if len(test) != 2:
            return False
        for t in test:
            try:
                float(t)
            except ValueError:
                if t != '?':
                    return False
        return True

    def formatter(self,column, value, cell, lines, teacher, ticket, line_id):
        if column.is_modifiable(teacher):
            return super(Note, self).formatter(column, value, cell, lines,
                                               teacher, ticket, line_id)

        classname = self.cell_indicator(column, value, cell, lines)[0]
        if classname == 'abinj2':
            return (configuration.abi + '???', classname, self.message)
        if classname in ('prst', 'abinj', 'abjus'):
            return (cgi.escape(str(value)), classname, '')
        if value == '':
            return '', '', ''

        v_min, v_max = column.min_max()
        v = '%s%s' % (value, self.value_range(v_min, v_max))

        if column.weight.startswith('+') or column.weight.startswith('-'):
            return (v, '', '')

        all_floats, floats = column.cell_values(lines)
        floats.sort()
        floats.reverse()
        all_floats.sort()
        all_floats.reverse()
        rank = ''

        def message(text, the_rank, nr):
            return (u'''<script>
Write("MSG_Note_rank_before","<b>%d</b>");
Write("MSG_Note_rank_middle","<b>%d</b>");
Write("%s");</script><br>''' % (the_rank, nr, text)).encode('utf8')
        
        try:
            rank += message("MSG_Note_rank_after_1",
                            floats.index(value)+1, len(floats))
        except ValueError:
            pass
        try:
            if len(floats) != len(all_floats) :
                rank +=  message("MSG_Note_rank_after_2",
                                 all_floats.index(value)+1, len(all_floats))
        except ValueError:
            pass

        return (v, classname, rank)

    def value_range(self, v_min, v_max):
        if v_min == 0:
            return '/%g' % v_max
        else:
            return '[%g;%g]' % (v_min, v_max)
