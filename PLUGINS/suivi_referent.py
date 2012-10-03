#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet)
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
from .. import inscrits
from .. import utilities
from .. import referent
from .. import configuration

def get_referent(server):
    """Display the referent of the named student"""
    student = inscrits.login_to_student_id(utilities.safe(server.something))
    year, semester = configuration.year_semester
    ref = referent.referent(year, semester, student)
    if ref:
        ref = server._("MSG_suivi_referent_is") + ref
    else:
        ref = server._("MSG_suivi_referent_none")
    ref = utilities.js(ref)
    server.the_file.write('<script>window.parent.set_the_referent(%s);</script>'
                          % ref)

plugin.Plugin('referent', '/referent/{?}', function=get_referent, group='staff',
              )
