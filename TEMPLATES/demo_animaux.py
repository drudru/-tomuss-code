#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2009 Thierry EXCOFFIER, Universite Claude Bernard
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

import inscrits
import utilities
import abj
import time
import _ucbl_
from _ucbl_ import the_abjs, update_student, terminate_update, cell_change

# Do not edit this first line (SCRIPTS/install_demo)
update_student_information = _ucbl_.update_student_information + """
<script>
function student_picture_url(login)
{
  if ( login )
    return '/' + login_to_id(login) + '.png' ;
  return '' ;
}
</script>
"""

def create(table):
    _ucbl_.create(table)
    table.table_attr(table.pages[0], 'masters',
                     [table.ue.lower().replace('-','') + '.master']
                     )
    table.table_attr(table.pages[0], 'default_sort_column', 2)

def init(table):
    _ucbl_.init(table)
    table.full_title = 'Techniques de base'
    table.modifiable = 1
    table.abjs = abj.get_abjs(table.year, table.semester)
    table.abjs_mtime = 0
    table.comment = "Pictures from wiki commons"
    table.default_sort_column = 2 # compatibility with old files

def content(table):
    if False: # Next lines are DANGEROUS (abj.abjs = ...)
        abj.abjs = True # Do not save next change in database
        abj.get_abjs(table.year, table.semester).add_da('k01','demo_animaux',
                                                        date='01/01/2009') 
        abj.get_abjs(table.year, table.semester).add('k01',
                                                     '02/02/2009M', '03/03/2009A')
        abj.abjs = None

    tt = abj.get_table_tt(table.year, table.semester)
    tt.loading = True # Do not save next change in database
    tt.cell_change(tt.pages[0], '0_0', 'x', 'k07')
    tt.cell_change(tt.pages[0], '0_3', 'x', '1')
    tt.loading = False

    table.abjs_mtime = table.abjs.mtime
    c = the_abjs(table)
    c += update_student_information
    return c

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
    terminate_update(table, the_ids, page)

def check(table):
    if table.ue.startswith('UE') and len(table.lines) == 0:
        prefill = True
    else:
        prefill = False

    _ucbl_.check(table, update_inscrits_ue)

    if prefill:
        import random
        table.lock()
        try:
            table.new_page('', '', '', '')
            p = table.pages[-1]
            table.column_change(p, '0_6', 'CM1', 'Prst', '[0;20]', '1', '','','4')
            table.column_change(p, '0_7', 'TP1', 'Note', '[0;20]', '1', '','','4')
            for lin in range(len(table.lines)):
                table.cell_change(p, '0_6', '0_%d' % lin,
                                  ('PRST','ABINJ','ABJUS','')[random.randint(0,3)],
                                  "20090509213856")
                table.cell_change(p, '0_7', '0_%d' % lin,
                                  '%4.1f' % random.gauss(10,3),
                                  "20090509213856")
        finally:
            table.unlock()





