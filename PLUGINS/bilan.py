#!/usr/bin/env python
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

import plugin
import utilities
import os
import inscrits
import configuration
from referent import students_of_a_teacher
import files

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
        server.the_file.write('Étudiant inconnu de TOMUSS')
        return

    if server.ticket.is_a_referent \
       and server.the_student not in students_of_a_teacher(server.ticket.user_name):
        i_can_refer = '1'
    else:
        i_can_refer = '0'

    firstname,surname,mail = inscrits.L_fast.firstname_and_surname_and_mail(server.the_student)
    server.the_file.write('''<META HTTP-EQUIV="Content-Type" CONTENT="text/html;charset=UTF-8">
<SCRIPT src="%s/bilan.js"></SCRIPT>
<SCRIPT src="%s/lib.js"></SCRIPT>
<SCRIPT src="%s/utilities.js"></SCRIPT>
<SCRIPT><!--
ticket = "%s" ;
bilan("%s","%s",%s,%s,%s,%s,%s,%s,%s) ;
--></SCRIPT>''' % (
                              configuration.server_url,
                              configuration.server_url,
                              configuration.server_url,
                              server.ticket.ticket,
                             server.ticket.ticket, server.the_student, v,
                   utilities.js(firstname.encode('utf8')),
                   utilities.js(surname.title().encode('utf8')),
                   utilities.js(mail.encode('utf8')),
                   configuration.suivi.all(server.ticket.ticket),
                   i_can_refer,
                   configuration.external_bilan(server.the_student)
                   ))


plugin.Plugin('bilan', '/bilan/{I}',
              function=bilan,
              referent=True,
              )





