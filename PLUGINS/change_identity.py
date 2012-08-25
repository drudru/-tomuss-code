#!/usr/bin/env python
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

import plugin
import authentication
import utilities

def change_identity(server):
    "Change of identity for this ticket"
    server.the_file.write(server._("MSG_change_identity_start") + "<br>")
    server.ticket.__init__(server.ticket.ticket,
                           server.the_path[0],
                           server.ticket.user_ip,
                           server.ticket.user_browser,
                           server.ticket.date)
    authentication.update_ticket(server.ticket)
    server.the_file.write(server._("MSG_change_identity_done"))
    server.close_connection_now()
    

plugin.Plugin('change_identity', '/change_identity/{*}',
              group='roots', function=change_identity,
              keep_open = True,
              launch_thread = True,
              link=plugin.Link(text=utilities._("LINK_change_identity") +
                               '<form style="margin:0" action="javascript:var m = document.getElementById(\'new_identity\').value ; window.location=\'/=\'+ticket+\'/change_identity/\' + m"><input id="new_identity" class="search_field" name="x" class="keyword" value="john.doe"></form>',
                               url='', where='debug', html_class='safe',
                          )
              )
