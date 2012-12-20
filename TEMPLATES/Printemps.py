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

import re
from .. import utilities
from .. import abj
from .. import configuration
from ._ucbl_ import check, update_student_information, create, update_student, cell_change
from . import _ucbl_

def init(table):
    _ucbl_.init(table)
    table.default_sort_column = 2
    table.modifiable = 0
    if table.is_extended:
        # Never modify via a symbolic link
        pass
    elif (table.year, table.semester) == configuration.year_semester:
        # Normal case : current semester modifications are allowed
        table.modifiable = 1
    elif table.semester == 'Test':
        table.modifiable = 1
    elif (table.year, table.semester) == configuration.year_semester_next:
        # No more useful because users can destroy table with bad students.
        #if utilities.manage_key('CLOSED', table.ue, separation=5
        #                        ) == '%s/%s' % configuration.year_semester:
        #    # Closed on the previous semester
        #    table.modifiable = 1
        table.modifiable = 1
    elif (re.search(configuration.ue_not_per_semester, table.ue)
          and table.semester == configuration.university_semesters[0]
          and table.year == utilities.university_year()):
        # Not an UE per semester : all the semesters points on the first
        table.modifiable = 1
        
    table.update_inscrits = table.modifiable

def content(table):
    c = table.the_abjs()
    if table.ue == 'tables':
        c += """
function update_student_information(line)
{
t_student_picture.parentNode.href = '%s/=' + ticket + '/' + year + '/' + semester + '/' + line[0].value ;
}
""" % utilities.StaticFile._url_
    else:
        c += update_student_information

    return c











