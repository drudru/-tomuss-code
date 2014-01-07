#!/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2011 Thierry EXCOFFIER, Universite Claude Bernard
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

from . import code_etape
from .. import utilities
from .. import inscrits

class Mail(code_etape.Code_Etape):
    cell_is_modifiable = 1
    attributes_visible = ('columns',)
    def get_one_value(self, student_id, column, line_id):
        return inscrits.L_fast.mail(student_id)

    def get_all_values(self, column):
        if self.__class__.__name__ != 'Mail':
            # Subclass need this generic function.
            # XXX It is not nice, a clean hierarchy must be done
            for line_id, login in self.values(column):
                yield line_id, self.get_one_value(login, column, line_id)
            return
        
        students = tuple(self.values(column))
        infos = inscrits.L_batch.firstname_and_surname_and_mail_from_logins(
            tuple(utilities.the_login(i[1]) for i in students))
        for line_id, student in students:
            student = utilities.the_login(student).lower()
            if student in infos:
                yield line_id, infos[student][2].encode('utf-8')
            else:
                yield line_id, None
