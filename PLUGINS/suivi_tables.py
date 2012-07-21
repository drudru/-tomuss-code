#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet)
#    Copyright (C) 2008-2012 Thierry EXCOFFIER, Universite Claude Bernard
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

import plugin
import column
import document
from tablestat import TableStat, les_ues
from cell import CellEmpty, CellValue, Line

def table_statistics(server):
    """Create a table of statistics about all the tables."""
    
    tables = {'': TableStat('')}
    for t in les_ues(server.year, server.semester):
        tables[t.ue] = table = TableStat(t.ue)
        table.nr_cols = len(t.columns)
        table.nr_pages = len(t.pages)
        table.nr_lines = len(t.lines)
        table.t = t
        col_inscrit = t.column_inscrit()
        for line in t.lines.values():
            if col_inscrit != None:
                if line[col_inscrit].value == 'ok':
                    table.nr_inscrits += 1
                elif line[col_inscrit].value == 'non':
                    table.nr_not_inscrits += 1
                group_and_seq = line[3].value + '/' + line[4].value
                table.group_and_seq[group_and_seq] = True
                
            for v in line:
                table.update(v)

    max_cels = max([t.nr for t in tables.values()])
    max_cols = max([t.nr_cols for t in tables.values()])
    max_lines = max([t.nr_lines for t in tables.values()])
    max_pages = max([t.nr_pages for t in tables.values()])
    # max_students = max([t.nr_students for t in tables.values()])
    max_comment = max([t.nr_comments for t in tables.values()])
    max_teachers = max([len(t.teachers) for t in tables.values()])

    columns = [
        column.Column('c0', '', freezed='F', type='Text', width=4,
                      title=server._('COL_TITLE_table'),
                      comment=server._('COL_COMMENT_table'),
                      ),
        column.Column('c1', '', type='Note', width=2,
                      title=server._('COL_TITLE_nb_cells_entered'),
                      comment=server._('COL_COMMENT_nb_cells_entered'),
                      minmax="[0;%s]" % max_cels,
                      ),
        column.Column('c2', '', type='Note', width=2,
                      title=server._('COL_TITLE_nb_teachers'),
                      comment=server._('COL_COMMENT_nb_teachers'),
                      minmax="[0;%s]" % max_teachers,
                      ),
        column.Column('c3', '', type='Note', width=2,
                      title=server._('COL_TITLE_nb_lines'),
                      comment=server._('COL_COMMENT_nb_lines'),
                      minmax="[0;%s]" % max_lines,
                      ),
        column.Column('c4', '', type='Note', width=2,
                      title=server._('COL_TITLE_nb_columns'),
                      comment=server._('COL_COMMENT_nb_columns'),
                      minmax="[0;%s]" % max_cols,
                      ),
        column.Column('c5', '', type='Note', width=2,
                      title=server._('COL_TITLE_nb_pages'),
                      comment=server._('COL_COMMENT_nb_pages'),
                      minmax="[0;%s]" % max_pages,
                      ),
        column.Column('c6', '', type='Note', width=2,
                      title=server._('COL_TITLE_nb_comments'),
                      comment=server._('COL_COMMENT_nb_comments'),
                      minmax="[0;%s]" % max_comment,
                      ),
        column.Column('c7', '', type='Date', width=4,
                      title=server._('COL_TITLE_first_change'),
                      ),
        column.Column('c8', '', type='Date', width=4,
                      title=server._('COL_TITLE_last_change'),
                      ),
        column.Column('c9', '', type='Note', width=2,
                      title=server._('COL_TITLE_nb_registered'),
                      comment=server._('COL_COMMENT_nb_registered'),
                      ),
        column.Column('ca', '', type='Note', width=2,
                      title=server._('COL_TITLE_nb_unregistered'),
                      comment=server._('COL_COMMENT_nb_unregistered'),
                      ),
        column.Column('cb', '', type='Bool', width=1,
                      title=server._('COL_TITLE_extended'),
                      comment=server._('COL_COMMENT_extended'),
                      ),
        column.Column('cc', '', type='Text', width=4,
                      title=server._('COL_TITLE_empty'),
                      comment=server._('COL_COMMENT_empty'),
                      ),
        column.Column('cd', '', type='Bool', width=2,
                      title=server._('COL_TITLE_nb_grp'),
                      comment=server._('COL_COMMENT_nb_grp'),
                      ),
        column.Column('ce', '', type='Bool', width=2,
                      title=server._('COL_TITLE_formula'),
                      comment=server._('COL_COMMENT_formula'),
                      ),
        ]
    table_attrs = {
        'comment': server._('LINK_tables'),
        'default_nr_columns': 14
        }

    lines = []
    for t in tables.values():
        if t.name == '':
            continue
        s = t.name.split('.')
        if len(s) == 1:
            s = ('', s[0])
        lines.append(Line((
                CellValue(t.name),
                CellValue(t.nr),
                CellValue(len(t.teachers)),
                CellValue(t.nr_lines),
                CellValue(t.nr_cols),
                CellValue(t.nr_pages),
                CellValue(t.nr_comments),
                CellValue(t.date_min),
                CellValue(t.date_max),
                CellValue(t.nr_inscrits),
                CellValue(t.nr_not_inscrits),
                CellValue(t.t.is_extended and 'OUI' or 'NON'),
                CellValue(t.t.empty()[1]),
                CellValue(len([g for g in t.group_and_seq if g != ''])),
                CellValue(t.t.problem_in_column_name()),
                )))

    document.virtual_table(server, columns, lines, table_attrs=table_attrs)

plugin.Plugin('tables', '/*2', function=table_statistics,
              teacher=True, launch_thread = True,
              link=plugin.Link(url="javascript:go_suivi('*2')",
                               where="informations", html_class="verysafe",
                               ),
              )

