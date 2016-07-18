#!/bin/env python3
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2016 Thierry EXCOFFIER, Universite Claude Bernard
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
#    Contact: Thierry.EXCOFFIER@univ-lyon1.fr

from . import mail
from .. import utilities
from .. import configuration

class Can_Bring_A_Pc(mail.Mail):
    attributes_visible = ('columns',)

    def get_all_values(self, column, line_ids):
        for line_id, student in self.values(column, line_ids):
            prefs = utilities.display_preferences_get(
                utilities.the_login(student))
            if 'can_bring_a_pc' in prefs:
                yield (line_id,
                       configuration.yes if prefs.get('can_bring_a_pc', '')
                       else configuration.no)
