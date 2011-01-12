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

import text
import inscrits
import utilities

def etapes_text(etapes):
    return ' '.join(sorted(etapes))

class Code_Etape(text.Text):
    human_priority = 12
    full_title = 'Code Etape'
    cell_is_modifiable = 0
    tip_cell = ""
    set_columns = 'set_columns'
    tip_columns = """<b>Extrait le code étape</b><br>
    Indiquez la colonne de numéro d'étudiants <b>ID</b><br>
    pour lesquels on veut extraire le code étape."""

    def data_col(self, the_table, column):
        try:
            id_column_title = column.depends_on()[0]
        except IndexError:
            return None
        return the_table.columns.data_col_from_title(id_column_title)

    def update_one(self, the_table, line_id, column):
        data_col = self.data_col(the_table, column)
        if data_col is None:
            return
        student_id = the_table.lines[line_id][data_col].value
        etape = etapes_text(inscrits.L.etapes_of_student(student_id))
        the_table.lock()
        try:
            the_table.cell_change(the_table.pages[0], column.the_id, line_id,
                                  etape)
        finally:
            the_table.unlock()

    def update_all(self, the_table, column, attr=None):
        if attr is not None and attr.name != 'columns':
            return
        if not getattr(the_table, 'update_inscrits', True):
            return
        
        data_col = self.data_col(the_table, column)
        if data_col is None:
            return
        students = set(inscrits.login_to_student_id(line[data_col].value)
                       for line in the_table.lines.values()
                       )
        etapes = inscrits.L.etapes_of_students(tuple(students))
        for line_key, line in the_table.lines.items():
            try:
                student_id = inscrits.login_to_student_id(line[data_col].value)
                etape = etapes_text(etapes[student_id])
            except KeyError:
                continue
            the_table.lock()
            try:
                the_table.cell_change(the_table.pages[0], column.the_id,
                                      line_key, etape)
            finally:
                the_table.unlock()
