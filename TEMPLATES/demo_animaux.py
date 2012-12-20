#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2009-2011 Thierry EXCOFFIER, Universite Claude Bernard
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

import random
from .. import inscrits
from .. import abj
from . import _ucbl_
from ._ucbl_ import update_student, terminate_update, cell_change
from .. import configuration

# Do not edit this first line (see SCRIPTS/install_demo)
update_student_information = _ucbl_.update_student_information + """
function student_picture_url(login)
{
  if ( login )
    return '/' + login_to_id(login) + '.png' ;
  return '' ;
}
"""

def create(table):
    _ucbl_.create(table)
    try:
        master = table.ue.split('-')[1].lower().replace('-','') + '.master'
    except IndexError:
        master = table.user
    table.table_attr(table.pages[0], 'masters', master)
    table.table_attr(table.pages[0], 'default_sort_column', 2)
    table.new_page('', master, '', '')

def init(table):
    _ucbl_.init(table)
    table.table_title = 'Techniques de base'
    table.modifiable = 1
    table.comment = "Pictures from wiki commons"
    table.default_sort_column = 2 # compatibility with old files

def content(table):
    tt = abj.get_table_tt(table.year, table.semester)
    tt.loading = True # Do not save next change in database
    tt.cell_change(tt.pages[0], '0_0', 'x', 'k07')
    tt.cell_change(tt.pages[0], '0_3', 'x', '1')
    tt.loading = False

    return  table.the_abjs() + update_student_information

def update_inscrits_ue(the_ids, table, page):
    table.with_inscrits = table.columns[5].title == 'Inscrit'
    if not table.with_inscrits:
        return

    for infos in inscrits.demo_animaux.values()[:-1]:
        t = []
        for i in infos:
            if isinstance(i, unicode):
                i = i.encode('utf8')
            t.append(i)
        
        update_student(table, page, the_ids, t)
    terminate_update(table, the_ids)

def create_column(table, title, content_type, average=10., delta=5.):
    p = table.pages[1]
    table.column_attr(p, title, 'type', content_type)
    table.column_attr(p, title, 'title', title)
    table.column_attr(p, title, 'comment',
                      'Column auto generated for demo purpose')
    data_col = table.columns.data_col_from_title(title)
    for key, line in table.lines.items():
        if line[data_col].value != '':
            continue
        if content_type == 'Prst':
            value = (configuration.pre,
                     configuration.abi,
                     configuration.abj)[random.randint(0,2)]
        elif content_type == 'Note':
            if random.randint(0,4) == 0:
                value = (configuration.abi, configuration.abj
                         )[random.randint(0,1)]
            else:
                value = '%4.1f' % random.gauss(average, delta)
        else:
            value = ''
        table.cell_change(p, title, key, value, "20090509213856")
        if random.randint(0,10) == 0:
            table.comment_change(p, title, key,
                                 "A cell comment / un commentaire sur la case")

def check(table):
    _ucbl_.check(table, update_inscrits_ue)

    if table.columns.from_id('#ABINJ') is not None:
        return

    table.lock()
    try:
        p = table.pages[1]
        create_column(table, 'CM1', 'Prst')
        create_column(table, 'CM2', 'Prst')
        create_column(table, 'CM3', 'Prst')
        table.column_attr(p, configuration.abi, 'type', 'Nmbr')
        table.column_attr(p, configuration.abi, 'title',
                          '#' + configuration.abi)
        table.column_attr(p, configuration.abi, 'columns', "CM1 CM2 CM3")
        create_column(table, 'TP1', 'Note', 10, 3)
        create_column(table, 'TP2', 'Note', 8, 2)
        create_column(table, 'TP3', 'Note', 14, 1)
        table.column_attr(p, 'Avg.TP', 'type', 'Moy')
        table.column_attr(p, 'Avg.TP', 'title', 'Avg.TP')
        table.column_attr(p, 'Avg.TP', 'columns', "TP1 TP2 TP3")
    finally:
        table.unlock()
