#!/usr/bin/env python
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

from .. import data
from .. import configuration
from .. import utilities

prefs = {'display_tips'   : configuration.yes,
         'nr_favorites'   : "6"  ,
         'nr_lines'       : "0"  ,
         'nr_cols'        : "0"  ,
         'zebra_step'     : "5"  ,
         'page_step'      : "1"  ,
         'invert_name'    : configuration.yes,
         'scrollbar_right': configuration.yes,
         'favoris_sort'   : configuration.no,
         'v_scrollbar'    : configuration.yes,
         'v_scrollbar_nr' : "1"  ,
         'interface'      : "N"  ,
         'current_suivi'  : configuration.no,
         'language'       : ""   ,
         'home_3scrollbar': configuration.yes,
         }

def create(table):
    p = table.get_ro_page()
    _ = utilities._
    table.table_attr(p, 'masters', [utilities.module_to_login(table.ue)])
    table.column_change(p,'0_0',_("COL_TITLE_explanations"),'Text','','','F',0,20)
    table.column_change(p,'0_1',_("COL_TITLE_recommended") ,'Text','','','F',0,4 )
    # To read old files, now unused
    table.column_change(p,'0_2',_("COL_TITLE_order")       ,'Text','','','F',1,2 )
    table.column_change(p,'0_3',_("COL_TITLE_your_choice") ,'Text','','','F',0,4 )
    table.table_attr(p, 'default_nr_columns', 3)
    table.table_attr(p, 'default_sort_column', 0)
    table.new_page('' ,utilities.module_to_login(table.ue), '', '')

def init(table):
    table.default_sort_column = 0 # compatibility with old Preferences files
    table.private = 1

def check(table):
    p_ro = table.pages[0]
    p_rw = table.pages[1]

    table.lock()
    try:
        # Remove old attribute            
        for lin in table.lines:
            if lin not in prefs:
                if table.lines[lin][0].value:
                    table.cell_change(p_ro, '0_0', lin, '')
                    table.cell_change(p_ro, '0_1', lin, '')
                    table.cell_change(p_ro, '0_2', lin, '')
                    table.cell_change(p_ro, '0_3', lin, '')

        # Add/update new attributes
        for lin, value in prefs.items():
            if lin not in table.lines:
                table.cell_change(p_rw, '0_3', lin, value)
            table.cell_change(p_ro, '0_0', lin, utilities._('Preferences_' + lin))
            table.cell_change(p_ro, '0_1', lin, value)

    finally:
        table.unlock()

def preferences(table):
    p = {}
    for lin in prefs:
        if lin in table.lines:
            p[lin] = table.lines[lin][3].value
        else:
            p[lin] = prefs[lin]
    return p
        
