#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2010 Thierry EXCOFFIER, Universite Claude Bernard
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
from .. import utilities
from .. import files
import os

def favorite_student(server):
    """Toggle the favorite state of a student"""
    login = utilities.the_login(server.ticket.user_name)
    d = utilities.manage_key('LOGINS', os.path.join(login, 'favstu'))
    if d is False:
        d = []
    else:
        d = [utilities.the_login(i) for i in eval(d)]

    student = utilities.the_login(server.something)
    if student in d:
        d.remove(student)
        if student in d: # Remove duplicate (correct old bug)
            d.remove(student)
    else:
        d.append(student)
        
    utilities.manage_key('LOGINS', os.path.join(login, 'favstu'),
                         content = utilities.stable_repr(d))
    server.the_file.write(files.files['ok.png'].bytes())

plugin.Plugin('favorite_student', '/favorite_student/{?}',
              mimetype = 'image/png',
              function=favorite_student, group='staff')

