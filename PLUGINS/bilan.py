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

import os
from .. import plugin
from .. import utilities
from .. import inscrits
from .. import configuration
from ..referent import students_of_a_teacher
from .. import files
from .. import document

files.add('PLUGINS', 'bilan.js')
files.add('PLUGINS', 'bilan.css')

# The bilan is computed by SCRIPTS/bilan.py once per night
def bilan(server):
    """Displays all the informations about a student in TOMUSS for
    all the semesters.
    These information can be augmented with other data"""
    
    v = utilities.manage_key('LOGINS',
                             os.path.join(server.the_student, 'resume'))
    if v is False:
        server.the_file.write(server._("MSG_bilan_unknown"))
        return

    if server.ticket.is_a_referent \
       and server.the_student not in students_of_a_teacher(server.ticket.user_name):
        i_can_refer = '1'
    else:
        i_can_refer = '0'

    firstname,surname,mail = inscrits.L_fast.firstname_and_surname_and_mail(server.the_student)
    prefs_table = document.get_preferences(server.ticket.user_name,
                                           create_pref=False,
                                           the_ticket=server.ticket)
    server.the_file.write(
        str(document.the_head)
        + document.translations_init(prefs_table['language'])
        + '''
<SCRIPT src="%s/bilan.js"></SCRIPT>
<SCRIPT><!--
var ticket = "%s" ;
var url = "%s" ;
bilan("%s","%s",%s,%s,%s,%s,%s,%s,%s) ;
--></SCRIPT>''' % (
               configuration.url_files,
               server.ticket.ticket,
               configuration.server_url,
               server.ticket.ticket, server.the_student, v,
               utilities.js(firstname.title()),
               utilities.js(surname.upper()),
               utilities.js(mail),
               configuration.suivi.all(server.ticket.ticket),
               i_can_refer,
               configuration.external_bilan(server.the_student)
               ))


plugin.Plugin('bilan', '/bilan/{I}',
              function=bilan, unsafe=False,
              group='referents',
              )





