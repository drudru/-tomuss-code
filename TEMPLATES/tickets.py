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

import _ucbl_
import abj

def init(table):
    _ucbl_.init(table)
    table.default_sort_column = 1
    table.table_title = 'Statistiques sur les tickets valides'
    table.modifiable = 0
    table.abjs = abj.get_abjs(table.year, table.semester)
    table.abjs_mtime = 0

def content(table):
    return _ucbl_.update_student_suivi + """
<script>
function update_student_information(line)
{
update_student_suivi(line) ;
}
</script>"""

check = _ucbl_.check









