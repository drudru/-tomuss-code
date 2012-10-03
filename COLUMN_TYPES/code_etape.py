#!/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2011 Thierry EXCOFFIER, Universite Claude Bernard
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

from . import text
from .. import inscrits
from .. import data

def etapes_text(etapes):
    return ' '.join(sorted(etapes))

class Code_Etape(text.Text):
    human_priority = 12
    cell_is_modifiable = 0
    tip_cell = ""
    set_columns = 'set_columns'
    attributes_visible = ('columns',)
    type_type = 'people'

    def data_col(self, the_table, column):
        try:
            id_column_title = column.depends_on()[0]
        except IndexError:
            return None
        return the_table.columns.data_col_from_title(id_column_title)

    def get_one_value(self, student_id, column, line_id):
        student_id = inscrits.login_to_student_id(student_id)
        return etapes_text(inscrits.L_slow.etapes_of_student(student_id))

    def update_one(self, the_table, line_id, column):
        data_col = self.data_col(the_table, column)
        if data_col is None:
            return
        student_id = the_table.lines[line_id][data_col].value
        etape = self.get_one_value(student_id, column, line_id)
        the_table.lock()
        try:
            if etape is None:
                if the_table.lines[line_id][column.data_col].author == data.ro_user:
                    etape = ''
                else:
                    return
            the_table.cell_change(the_table.pages[0], column.the_id, line_id,
                                  etape)
        finally:
            the_table.unlock()

    def values(self, column):
        data_col = self.data_col(column.table, column)
        if data_col is None:
            return
        for line_id, line in column.table.lines.items():
            yield line_id, line[data_col].value

    def get_all_values(self, column):
        students = self.values(column)
        students_etapes = inscrits.L_batch.etapes_of_students(tuple(
            inscrits.login_to_student_id(i[1]) for i in students))
        for line_id, student in self.values(column):
            student = inscrits.login_to_student_id(student)
            yield line_id, etapes_text(students_etapes.get(student,[]))

    def update_all(self, the_table, column, attr=None):
        if attr is not None and attr.name != 'columns' and attr.name != 'type':
            return
        if not getattr(the_table, 'update_inscrits', True):
            return
        
        for line_id, value in self.get_all_values(column):
            the_table.lock()
            try:
                if value is None:
                    if the_table.lines[line_id][column.data_col].author != data.ro_user:
                        # Do not replace user defined input with nothing
                        continue
                    value = ''
                the_table.cell_change(the_table.pages[0], column.the_id,
                                      line_id, value)
            finally:
                the_table.unlock()
