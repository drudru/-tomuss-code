#!/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2011-2014 Thierry EXCOFFIER, Universite Claude Bernard
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

import inspect
from . import text
from .. import inscrits
from .. import data
from .. import utilities

class Code_Etape(text.Text):
    human_priority = 12
    tip_cell = ""
    set_columns = 'set_columns'
    attributes_visible = ('columns',)
    type_type = 'people'

    def data_col(self, the_table, column):
        """Returns the data_col of the first column in columns"""
        try:
            id_column_title = column.depends_on()[0]
        except IndexError:
            return None
        return the_table.columns.data_col_from_title(id_column_title)

    def values(self, column, line_ids=None):
        data_col = self.data_col(column.table, column)
        if data_col is None:
            return []
        if line_ids is None:
            line_ids = column.table.lines.keys()
        return [(line_id, column.table.lines[line_id][data_col].value)
                for line_id in line_ids
                ]

    def get_all_values(self, column, line_ids=None):
        """Redefine this method to get the [line_id, value] list"""
        # Get the line_id + input value
        students = self.values(column, line_ids)
        # Get the data from all the input values
        students_etapes = inscrits.L_slow.etapes_of_students(tuple(
            inscrits.login_to_student_id(i[1]) for i in students))
        # Merge line_id and returned value
        for line_id, student in students:
            student = inscrits.login_to_student_id(student)
            yield line_id, ' '.join(students_etapes.get(student,[]))

    def get_one_value(self, student_id, column, line_id):
        """Deprecated, Define get_all_values"""
        pass

    def update_one(self, the_table, line_id, column):
        self.update_all(the_table, column, line_ids=(line_id,))

    def simulate_get_all_values(self, the_table, column, line_ids):
        data_col = self.data_col(the_table, column)
        if data_col is None:
            return ()
        return (
            (line_id, self.get_one_value(
                    the_table.lines[line_id][data_col].value,
                    column, line_id)
             )
            for line_id in (line_ids or the_table.lines)
            )
        
    def update_all(self, the_table, column, attr=None, line_ids=None):
        if attr is not None and attr.name != 'columns' and attr.name != 'type':
            return
        if line_ids is None:
            line_ids = column.table.lines.keys()

        if 'get_all_values' in self.__class__.__dict__:
            if 'line_ids' in inspect.getargspec(self.get_all_values).args:
                values = self.get_all_values(column, line_ids)
            else:
                if (line_ids is None
                    or 'get_one_value' not in self.__class__.__dict__):
                    values = self.get_all_values(column)
                else:
                    values = self.simulate_get_all_values(the_table, column,
                                                          line_ids)
        elif 'get_one_value' in self.__class__.__dict__:
            values = self.simulate_get_all_values(the_table, column, line_ids)
        else:
            raise ValueError("Missing method: get_all_values or get_one_value")


        line_id_done = set()
        data_col = the_table.column_inscrit()
        rw_page = None
        for line_id, value in values:
            line_id_done.add(line_id)
            if isinstance(value, str):
                v = unicode(value, "utf-8", "replace").encode("utf-8")
                if v != value:
                    utilities.send_backtrace(
                        "%s %s %s" % (the_table, column.title, v),
                        'Bad value encoding')
                    value = v
            the_table.lock()
            try:
                if (data_col
                    and the_table.lines[line_id][data_col].value) == 'non':
                    if rw_page is None:
                        rw_page = the_table.get_rw_page()
                    page = rw_page
                else:
                    page = the_table.pages[0]
                the_table.cell_change(page, column.the_id, line_id, value)
            finally:
                the_table.unlock()

        # Erase system defined cells without value
        for line_id in line_id_done - set(line_ids):
            if (the_table.lines[line_id][column.data_col].author
                in (data.ro_user, data.rw_user, data.no_user)):
                try:
                    the_table.cell_change(the_table.pages[0], column.the_id,
                                          line_id, '')
                finally:
                    the_table.unlock()
