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

from . import mail
from .. import utilities
from .. import inscrits

class Firstname(mail.Mail):
    attributes_visible = ('columns',)

    # copy/paste from Mail
    def get_all_values(self, column, line_ids):
        students = tuple(self.values(column, line_ids))
        infos = inscrits.L_batch.firstname_and_surname_and_mail_from_logins(
            tuple(utilities.the_login(i[1]) for i in students))
        for line_id, student in students:
            student = utilities.the_login(student).lower()
            if student in infos:
                yield line_id, infos[student][0].title().encode('utf-8')
