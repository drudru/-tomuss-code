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

from .. import plugin
from .. import document
from .. import utilities
from .. import referent
from .. import data
from ..tablestat import TableStat, les_ues
from ..cell import CellValue, Line
from .. import column

def teachers_statistics(server):
    """Create a table of statistics about all the teachers"""
    teachers = {'': TableStat('')}
    for t in les_ues(server.year, server.semester):
        for c in t.columns:
            user_name = c.author
            if user_name not in teachers:
                teachers[user_name] = TableStat(user_name)
            teachers[user_name].nr_cols += 1
        for p in t.pages:
            if p.user_name not in teachers:
                teachers[p.user_name] = TableStat(p.user_name)
            teachers[p.user_name].nr_pages += 1
            try:
                teachers[p.user_name].pages_per_table[t.ue] += 1
            except:
                teachers[p.user_name].pages_per_table[t.ue] = 1
        for line in t.lines.values():
            for v in line[6:]:
                teachers[v.author].update(v)
        if not hasattr(t, "rtime"):
            t.unload()

    year = utilities.university_year(server.year, server.semester)
    for t in referent.les_blocsnotes(year):
        for p in t.pages:
            if p.user_name not in teachers:
                teachers[p.user_name] = TableStat(p.user_name)
            teachers[p.user_name].nr_pages += 1
        user_name = utilities.module_to_login(t.ue)
        if user_name not in teachers:
            teachers[user_name] = TableStat(user_name)
        # teachers[user_name].nr_students = len([x for x in t.logins() if x])
        teachers[user_name].nr_students = len(
            referent.students_of_a_teacher(user_name))
        for line in t.lines.values():
            for v in line[3:]:
                teachers[v.author].update(v, blocnote=True)
        t.unload()

    teachers.pop(data.ro_user, None)
    teachers.pop(data.rw_user, None)
    teachers.pop(data.no_user, None)

    if len(teachers):
        max_cels = max([t.nr for t in teachers.values()])
        max_cols = max([t.nr_cols for t in teachers.values()])
        max_pages = max([t.nr_pages for t in teachers.values()])
        max_students = max([t.nr_students for t in teachers.values()])
        max_blocnote = max([t.nr_blocnote for t in teachers.values()])
        max_comment = max([t.nr_comments for t in teachers.values()])
    else:
        max_cels = max_cols = max_pages = max_students = max_blocnote = max_comment = 1


    columns = [
        column.Column('c0', '', freezed='F', type='Text', width=6,
                      title=server._('COL_TITLE_teacher'),
                      comment=server._('COL_COMMENT_teacher'),
                      ),
        column.Column('cfn', '', freezed='F', type='Text', width=4,
                      title=server._('COL_TITLE_firstname'),
                      ),
        column.Column('csn', '', freezed='F', type='Text', width=4,
                      title=server._('COL_TITLE_surname'),
                      ),        
        column.Column('c1', '', type='Note', width=2,
                      title=server._('COL_TITLE_nb_cells_entered'),
                      comment=server._('COL_COMMENT_nb_cells_entered'),
                      minmax="[0;%s]" % max_cels,
                      ),
        column.Column('c2', '', type='Note', width=2,
                      title=server._('COL_TITLE_nb_columns'),
                      comment=server._('COL_COMMENT_nb_columns'),
                      minmax="[0;%s]" % max_cols,
                      ),        
        column.Column('c3', '', type='Note', width=2,
                      title=server._('COL_TITLE_nb_pages'),
                      comment=server._('COL_COMMENT_nb_pages'),
                      minmax="[0;%s]" % max_pages,
                      ),        
        column.Column('c4', '', type='Note', width=2,
                      title=server._('COL_TITLE_nb_comments'),
                      comment=server._('COL_COMMENT_nb_comments'),
                      minmax="[0;%s]" % max_comment,
                      ),
        column.Column('c5', '', type='Note', width=2,
                      title=server._('COL_TITLE_nb_suivi_students'),
                      comment=server._('COL_COMMENT_nb_suivi_students'),
                      minmax="[0;%s]" % max_students,
                      ),
        column.Column('c6', '', type='Note', width=2,
                      title=server._('COL_TITLE_nb_notepad_cells'),
                      comment=server._('COL_COMMENT_nb_notepad_cells'),
                      minmax="[0;%s]" % max_blocnote,
                      ),        
        column.Column('c7', '', type='Date', width=4,
                      title=server._('COL_TITLE_first_change'),
                      ),
        column.Column('c8', '', type='Date', width=4,
                      title=server._('COL_TITLE_last_change'),
                      ),        
        ]
    table_attrs = {
        'comment': server._('LINK_teachers'),
        'default_nr_columns': 11
        }

    lines = []

    for t in teachers.values():
        s = t.name.split('.')
        if len(s) == 1:
            s = ('', s[0])
        lines.append(Line((
                    CellValue(t.name),
                    CellValue(s[0]),
                    CellValue(s[1]),
                    CellValue(t.nr),
                    CellValue(t.nr_cols),
                    CellValue(t.nr_pages),
                    CellValue(t.nr_comments),
                    CellValue(t.nr_students),
                    CellValue(t.nr_blocnote),
                    CellValue(t.date_min),
                    CellValue(t.date_max),
                    )))
    document.virtual_table(server, columns, lines, table_attrs=table_attrs)

plugin.Plugin('teachers', '/*', function=teachers_statistics,
              group='staff', launch_thread = True,
              link=plugin.Link(url="javascript:go_suivi('*')",
                               where="informations", html_class="verysafe",
                               ),
              )
