#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2009-2010 Thierry EXCOFFIER, Universite Claude Bernard
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
import inscrits
import configuration
import _ucbl_

default_master = 'thierry.excoffier'

def create(table):
    table.add_master(default_master)
    p = table.new_page('' , data.ro_user, '', '')
    table.column_change(p,'a','Enseignant','Login','','','F',0,8)
    table.column_change(p,'b','Orientation','Text','','','F',0,3)
    table.column_comment(p, 'b',
                         "{MAT|INF}[gerland][*] *:ne veut plus d'étudiants")
    q = table.new_page('' , default_master, '', '')



def update_referents(the_ids, table, page):
    """Create referent list from LDAP"""
    
    table.with_inscrits = False
    for r in configuration.referents:
        r = inscrits.L.query(base="DC=univ-lyon1,DC=fr",
                             search='(memberOf=%s)'% r,
                             attributes=(configuration.attr_login,))
        try:
            table.lock()
            for infos in r:
                if infos[0] is None:
                    continue
                login = infos[1][configuration.attr_login][0].lower()
                line_key = tuple(table.get_lines(login))
                if len(line_key) == 0:
                    table.cell_change(page, "a", str(len(table.lines)), login)
                    line_key = table.get_lines(login)
        finally:
            table.unlock()
    



# Get the mails
def check(table):
    _ucbl_.check(table, update_inscrits=update_referents)
