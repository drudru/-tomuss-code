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

from .. import plugin
from .. import document
from .. import configuration
from .. import utilities
from . import abj_change

def send_alert(server):
    """Send an alert popup to the TABLE clients or all clients ."""
    message = server.the_path[0].replace('+', ' ')
    if message.startswith('?x='):
        message = message[3:]
    if server.the_ue != '':
        document.table(configuration.year_semester[0],
                       configuration.year_semester[1],
                       server.the_ue).send_alert(message)
    else:
        document.send_alert(message)
        for page in abj_change.pages:
            try:
                page.the_file.write(
                    '<script>Alert("ALERT_send_alert","\\n\\n"+%s);</script>\n'
                    % utilities.js(message))
                page.the_file.flush()
            except:
                pass

    server.the_file.write(server._("MSG_send_alert") + message)

plugin.Plugin('send_alert', '/send_alert/{U}/{*}',
              function=send_alert,
              group='roots',
              link=plugin.Link(text=utilities._("LINK_send_alert_before")
                               + '''<br><form style="margin:0" action="javascript:var m = document.getElementById('message').value ; if(confirm(_('LINK_send_alert_before') + '\\n\\n' + m)) window.location='/='+ticket+'/send_alert//' + m"><input id="message" class="search_field" name="x" class="keyword" value="'''
                               + utilities._("LINK_send_alert_default")
                               .replace('\n', ' ')
                               + '"></form>',
                   url='', where="root_rw", html_class="safe", priority = -100,
                   ),
              )

