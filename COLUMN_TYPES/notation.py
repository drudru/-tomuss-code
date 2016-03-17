#!/bin/env python3
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2016 Thierry EXCOFFIER, Universite Claude Bernard
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
#    Contact: Thierry.EXCOFFIER@univ-lyon1.fr

from . import note

class Notation(note.Note):
    tip_cell = "TIP_cell_Notation"
    cell_is_modifiable = 0
    human_priority = 0
    ondoubleclick = 'notation_open'
    attributes_visible = ('minmax', 'weight', 'rounding', 'repetition',
                          "groupcolumn")
    formatte_suivi = "notation_format_suivi"

    def update_for_suivi(self, column):
        data_col = column.data_col
        for dummy_group, lines in column.get_the_groups().items():
            if len(lines) == 1:
                continue
            comments = []
            for line in lines:
                cell = line[data_col]
                if cell.comment:
                    comments.append(cell.comment)
            if len(comments) == 1:
                comment = comments[0]
                for line in lines:
                    line[data_col] = line[data_col].set_comment(comment)

