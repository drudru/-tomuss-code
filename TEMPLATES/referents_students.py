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

from .. import data
from .. import inscrits
from .. import configuration
from ..utilities import _
from . import _ucbl_

def init(table):
    _ucbl_.init(table)
    if (table.year, table.semester) != configuration.year_semester:
        table.modifiable = table.update_inscrits = 0


def create(table):
    default_master = configuration.root[0]

    p = table.new_page('' , data.ro_user, '', '')
    table.table_attr(p, 'masters', default_master)
    table.column_change(p,'a',_("COL_TITLE_teacher")    ,'Login','','','F',0,8)
    table.column_change(p,'b',_("COL_TITLE_orientation"),'Text' ,'','','F',0,3)
    q = table.new_page('' , default_master, '', '')


def update_referents(the_ids, table, page):
    """Create referent list from LDAP"""
    
    table.with_inscrits = False
    for r in configuration.referents:
        r = inscrits.L_batch.query(base=configuration.ou_top,
                                   search='(memberOf=%s)'% r,
                                   attributes=(configuration.attr_login,))
        try:
            table.lock()
            for infos in r:
                if infos[0] is None:
                    continue
                login = infos[1][configuration.attr_login][0].lower()
                line = tuple(table.get_lines(login))
                if len(line) == 0:
                    table.cell_change(page, "a", str(len(table.lines)), login)
        finally:
            table.unlock()
    



# Get the mails
def check(table):
    _ucbl_.check(table, update_inscrits=update_referents)
