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
import document
import configuration
import abj_change
import utilities

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
                page.the_file.write("<script>alert(%s);</script>\n" %
                                    utilities.js("Message de TOMUSS :\n\n" +
                                                 message))
                page.the_file.flush()
            except:
                pass

    server.the_file.write("Message envoyé : " + message)

plugin.Plugin('send_alert', '/send_alert/{U}/{*}',
              function=send_alert,
              root=True,
              link=plugin.Link(text="""Envoyer le message suivant :<br><form style="margin:0" action="javascript:var m = document.getElementById('message').value ; if(confirm('Vous allez envoyer le message :\\n\\n' + m)) window.location='/='+ticket+'/send_alert//' + m"><input id="message" class="search_field" name="x" class="keyword" value="Le serveur va être redémarré dans quelques secondes, il est conseillé (mais non obligatoire) de réactualiser la page après le redémarrage."></form>""",
                   url='',
                   where="root_rw",
                   html_class="safe",         
                   help="""Vous pouvez éditer le champ texte afin d'envoyer un
                   message (fenêtre popup) à tous les utilisateurs actuellement
                   connectés à TOMUSS.
                   Taper 'return' pour envoyer le message.""",
                   priority = -100,
                   ),
              )

