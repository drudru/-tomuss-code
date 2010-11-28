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

import plugin
import ticket
import time
import utilities
import configuration
import document

def tickets(server):
    """Display tickets"""
    filename = document.table_filename('0', 'Stats', 'tickets')
    
    f = open(filename, "w")
    f.write("""# -*- coding: utf8 -*-
from data import *
new_page('' ,'*', '', '')
column_change (0,'0_0','Login','Text','','','F',0,2)
column_change (0,'0_1','Date','Text','','','',0,2)
column_comment(0,'0_1','Date de première connexion')
column_change (0,'0_2','IP','Text','','','',0,2)
column_comment(0,'0_2','Adresse IP de connexion')
column_change (0,'0_3','ABJ','Bool','','','',0,1)
column_comment(0,'0_3','Est un gestionnaire des ABJ')
column_change (0,'0_4','Prof','Bool', '','','',0,1)
column_comment(0,'0_4','Est un enseignant')
column_change (0,'0_5','Navigateur','Text','[0;20]','','',0,6)
column_comment(0,'0_5','Navigateur Web utilisé')
table_comment(0, 'Les tickets actuellement valide')
default_nr_columns(6)
private_toggle(0)
add_master(%s,0)
""" % repr(server.ticket.user_name))
    for i, t in enumerate(ticket.tickets.values()):
        f.write("cell_change(0,'0_0','%d','%s','')\n" % (i, t.user_name))
        f.write("cell_change(0,'0_1','%d','%s','')\n" % (
            i, time.strftime('%Y-%m-%d %H:%M.%S', time.localtime(t.date))))
        f.write("cell_change(0,'0_2','%d','%s','')\n" % (i, t.user_ip))
        f.write("cell_change(0,'0_3','%d','%s','')\n" % (
            i, t.__dict__.get('is_an_abj_master', False)))
        f.write("cell_change(0,'0_4','%d','%s','')\n" % (i, t.__dict__.get('is_a_teacher','???')))
        f.write("cell_change(0,'0_5','%d',%s,'')\n" % (i, repr(t.user_browser)))
        
    f.close()

    t = document.table(0, 'Stats', 'tickets', create=False)
    if t:
        t.unload()


def headers(server):    
    return (
        ('Location','%s/=%s/0/Stats/tickets' % (
        configuration.server_url, server.ticket.ticket)), )

plugin.Plugin('tickets', '/tickets',
              function=tickets,
              root=True,
              response=307,
              headers = headers,
              link=plugin.Link(text='Tickets actifs',
                               help="Liste des tickets actuellement valides",
                               where='informations',
                               html_class="verysafe",
                               )
              )





