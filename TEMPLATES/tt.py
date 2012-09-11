#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2009,2012 Thierry EXCOFFIER, Universite Claude Bernard
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

import data
import configuration
import utilities
import _ucbl_

def create(table):
    
    p = table.new_page('' ,data.ro_user, '', '')
    table.table_attr(p, 'default_nr_columns', 11)

    if configuration.regtest:
        masters = [configuration.invited_abj_masters[-1]]
    else:
        masters = configuration.tt_masters
    _ = utilities._
    table.table_attr(p, 'masters', list(masters))
    table.column_change(p,'0_0',_("COL_TITLE_0_0")       ,'Login','','','',0,4)
    table.column_change(p,'0_1',_("COL_TITLE_0_1")    ,'Firstname','','','',0,8)
    table.column_attr(p, '0_1', 'columns', _("COL_TITLE_0_0"))
    table.column_change(p,'0_2',_("COL_TITLE_0_2")    ,'Surname','','' ,'',0,8)
    table.column_attr(p, '0_2', 'columns', _("COL_TITLE_0_0"))
    table.column_change(p,'0_3',_("COL_TITLE_+write")    ,'Text','','1','',0,3)
    table.column_comment(p,'0_3', _("COL_COMMENT_+write"))
    table.column_change(p,'0_4',_("COL_TITLE_+speech")   ,'Text','','1','',0,3)
    table.column_comment(p,'0_4',_("COL_COMMENT_+speech"))
    table.column_change(p,'0_5',_("COL_TITLE_+practical"),'Text','','1','',0,3)
    table.column_comment(p,'0_5',_("COL_COMMENT_+practical"))
    table.column_change(p,'0_6',_("COL_TITLE_+assistant"),'Bool','','1','',0,2)
    table.column_comment(p,'0_6',_("COL_COMMENT_+assistant"))
    table.column_change(p,'0_7',_("COL_TITLE_+room")     ,'Bool','','1','',0,2)
    table.column_comment(p,'0_7',_("COL_COMMENT_+room"))
    table.column_change(p,'0_8',_("TH_begin")            ,'Date','','' ,'',0,6)
    table.column_comment(p,'0_8', _("COL_COMMENT_tt_duration"))
    table.column_change(p,'0_9',_("TH_end")              ,'Date','','' ,'',0,6)
    table.column_comment(p,'0_9', _("COL_COMMENT_tt_duration"))
    table.column_change(p,'0_10',_("COL_TITLE_tt_remarks"),'Text','','','',0,13)
    table.table_attr(p, 'default_sort_column', 2)

def init(table):
    _ucbl_.init(table)
    table.default_sort_column = 2 # compatibility with old files
    table.do_not_unload_add(1)
    table.modifiable = int(table.modifiable
                           and utilities.university_year() == table.year)
    table.update_inscrits = table.modifiable

def content(dummy_table):
    return _ucbl_.update_student_information

cell_change = _ucbl_.cell_change

def check(table):
    # Get mails and portails
    _ucbl_.check(table, update_inscrits=lambda x,y,z: None)
