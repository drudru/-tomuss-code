#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2008-2011 Thierry EXCOFFIER, Universite Claude Bernard
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
from .. import referent

def update_referents(server):
    """Dispatch students without referents to a referent."""
    referent.update_referents(server.ticket, server.the_file,
                              really_do_it=True)

plugin.Plugin('referents_update', '/referents',
              function=update_referents, group='referent_masters',
              launch_thread=True,
              link=plugin.Link(html_class='veryunsafe', where="referents",
                               priority=1000,
                               ),
              )

def update_referents_R(server):
    """Dispatch students without referents to a referent."""
    referent.update_referents(server.ticket, server.the_file,
                              really_do_it=True, add_students=False)

plugin.Plugin('referents_update_R', '/referents_R',
              function=update_referents_R, group='referent_masters',
              launch_thread=True,
              link=plugin.Link(html_class='veryunsafe', where="referents",
                               priority=1000,
                               ),
              )

def update_referents_safe(server):
    """Dispatch students without referents to a referent."""
    referent.update_referents(server.ticket, server.the_file,
                              really_do_it=False)

plugin.Plugin('referents_update_safe', '/referents_safe',
              function=update_referents_safe, group='referent_masters',
              launch_thread=True,
              link=plugin.Link(html_class='verysafe', where='referents',
                               priority=1000,
                               ),
              )

def update_referents_safe_R(server):
    """Dispatch students without referents to a referent."""
    referent.update_referents(server.ticket, server.the_file,
                              really_do_it=False, add_students=False)

plugin.Plugin('referents_update_safe_R', '/referents_safe_R',
              function=update_referents_safe_R, group='referent_masters',
              launch_thread=True,
              link=plugin.Link(html_class='verysafe', where='referents',
                               priority=1000,
                               ),
              )
