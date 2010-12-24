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

import utilities
import abj
import configuration
import os
import document

from _ucbl_ import check, update_student_information, create, the_abjs, update_student, terminate_update, cell_change, column_change
import _ucbl_

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
        if utilities.manage_key('CLOSED', table.ue, separation=5
                                ) == '%s/%s' % configuration.year_semester:
            # Closed on the previous semester
            table.modifiable = 1
    table.update_inscrits = table.modifiable
    table.abjs = abj.get_abjs(table.year, table.semester)
    table.abjs_mtime = 0

def content(table):
    table.abjs_mtime = table.abjs.mtime
    c = the_abjs(table)
    if table.ue == 'tables':
        c += """
<script>
function update_student_information(line)
{
if ( line[0].value == '' )
        t_student_picture.src = '/tip.png' ;
      else
        t_student_picture.src = student_picture_url(line[0].value) ;
t_student_picture.parentNode.href =  '%s/=' + ticket + '/' + year + '/' + semester + '/' + line[0].value ;
}
</script>""" % utilities.StaticFile._url_ 
    else:
        c += update_student_information

    return c











