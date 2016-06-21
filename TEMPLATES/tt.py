#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2009-2013 Thierry EXCOFFIER, Universite Claude Bernard
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

import time
from .. import configuration
from .. import utilities
from . import _ucbl_

def create(table):
    p = table.get_ro_page()
    table.table_attr(p, 'default_nr_columns', 11)

    if configuration.regtest:
        masters = [configuration.invited_abj_masters[-1]]
    else:
        masters = configuration.tt_masters
    _ = utilities._
    table.table_attr(p, 'masters', list(masters))
    table.update_columns({
        '0_0':{'type':'Login'    , 'title':_("COL_TITLE_0_0"), "width":4,
               "freezed":'F'},
        '0_1':{'type':'Surname'  , 'title':_("COL_TITLE_0_1"), "width":8,
               "freezed":'F', 'columns': _("COL_TITLE_0_0")},
        '0_2':{'type':'Firstname', 'title':_("COL_TITLE_0_2"), "width":8,
               "freezed":'F', 'columns': _("COL_TITLE_0_0")},
        '0_8':{'type':'Date' , 'title':_("TH_begin")     , "width":6,
               'comment': _("COL_COMMENT_tt_duration")},
        '0_9':{'type':'Date' , 'title':_("TH_end")       , "width":6,
               'comment': _("COL_COMMENT_tt_duration")},
    })
    table.table_attr(p, 'default_sort_column', 2)

def translate_tt(tt_value):
    """Translate some TT values to more informative values"""
    if (tt_value.strip() == '1'
        or tt_value.upper() == utilities._('yes')[0]
        or tt_value.upper() == utilities._('yes')
        ):
        return '1/3'
    if tt_value.upper() == utilities._('no')[0]:
        return utilities._('no')
    return tt_value

class SpecialExaminationCondition(object):
    begin = ""
    begin_seconds = 0
    end = ""
    end_seconds = 8000000000
    predefined = set(('0_0', '0_1', '0_2', '0_8', '0_9'))
    
    def __init__(self, line, table):
        self.table = table
        self.line = line
        if line[table.col_begin].value:
            self.begin = line[table.col_begin].value
            self.begin_seconds = configuration.date_to_time(self.begin)
        if line[table.col_end].value:
            self.end = line[table.col_end].value
            self.end_seconds = configuration.date_to_time(self.end)

    def current(self):
        return self.begin_seconds < time.time() < self.end_seconds

    def text(self):
        s = []
        if self.begin:
            s.append(utilities._("MSG_abj_tt_from") + ' ' + self.begin)
        if self.end:
            s.append(utilities._('TH_until') + ' ' + self.end)
        if s:
            s = [' '.join(s)]

        for column in self.table.columns.left_to_right():
            if column.the_id in self.predefined:
                continue
            value = self.line[column.data_col].value
            comment = self.line[column.data_col].comment
            if value == '' and comment == '':
                continue
            if column.the_id.startswith("0_"):
                # Historical table
                if value.upper().startswith('N') or value == 0:
                    continue
                if column.type.name == "Text":
                    value = translate_tt(value)
            if comment == '' or value == '':
                value = value + comment
            else:
                value += ' (' + comment + ')'
            value = value.replace('_', ' ') # For enumeration
            if column.comment:
                s.append('{}: {}.'.format(column.comment.split("///")[0],
                                          value))
            else:
                s.append(value + '.')
        return '\n'.join(s)

@utilities.add_a_lock
def the_current_tt(table):
    if table.the_current_tt_time == table.mtime:
        return table.the_current_tt_cache
    table.the_current_tt_time = table.mtime
    table.col_begin = table.columns.from_id("0_8").data_col
    table.col_end = table.columns.from_id("0_9").data_col
    d = {}
    for line in table.lines.values():
        if len(line[0].value) < 2:
            continue
        d[line[0].value] = SpecialExaminationCondition(line, table)
    table.the_current_tt_cache = d
    return d
    
def init(table):
    _ucbl_.init(table)
    table.default_sort_column = 2 # compatibility with old files
    table.modifiable = int(table.modifiable
                           and utilities.university_year() == table.year)
    table.update_inscrits = table.modifiable
    if table.modifiable:
        table.do_not_unload_add('*tt')
    table.the_current_tt_time = -1
    table.the_current_tt = the_current_tt

def content(dummy_table):
    return _ucbl_.update_student_information

def cell_change(table, dummy_page,dummy_col,dummy_lin,dummy_value,dummy_date):
    table.the_current_tt_time = -1
