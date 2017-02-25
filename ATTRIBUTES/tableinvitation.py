#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2017 Thierry EXCOFFIER, Universite Claude Bernard
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
#    Contact: Thierry.EXCOFFIERuniv-lyon1.fr

import hashlib
import time
import random
from .. import utilities
from .. import plugin
from .. import document
from .. import configuration
from .. import inscrits
from ..TEMPLATES import config_table

config_table.variable_list.append("random_seed")
# Only used on the first TOMUSS launch, after it is editable in config_table
configuration.random_seed = str(random.randrange(0, 1000000000000))

from ..column import TableAttr

class TableInvitation(TableAttr):
    name = 'invitation'
    default_value = 1
    gui_display = "GUI_a"
    action = "send_invitation"

def checksum(link):
    return hashlib.md5((link + configuration.random_seed
    ).encode("utf-8")).hexdigest()
        
def invitation(server):
    if configuration.regtest:
        server.the_file.write(server._("MSG_evaluate"))
        return

    progress_bar = utilities.ProgressBar(server,
                                         message=server._("MSG_abj_wait"))
    
    data = server.uploaded
    if data is None:
        server.the_file.write("BUG")
        return

    subject = data.getfirst('subject')
    message = data.getfirst('message')
    days = data.getfirst('days')
    invitation_type = data.getfirst('type')
    recipients = data.getfirst('recipients').split("\001")
    frome = inscrits.L_slow.mail(server.ticket.user_name)

    for nb, recipient in enumerate(recipients):
        link = "{}/{}/{}/{}/{}/{}".format(
            server.the_year, server.the_semester, server.the_ue,
            recipient, invitation_type, int(time.time() + float(days)*86400))
        link = (configuration.server_url + "/invitation_accept/"
                + link + '/' + checksum(link))

        utilities.send_mail_in_background(recipient, subject,
                                          message + '\n' + link,
                                          frome,
                                          show_to = True)
        progress_bar.update(nb, len(recipients))
    progress_bar.hide()

    utilities.send_mail_in_background(frome,
                                      server._("MSG_mail_archive")
                                      + ' ' + subject,
                                      message + '\n\n'
                                      + '\n'.join(recipients),
                                      frome,
                                      show_to = True)
    
    progress_bar = utilities.ProgressBar(
        server, '<p>' + server._("MSG_send_mail_close"), show_numbers=False)
    progress_bar.wait_mail_sent()


plugin.Plugin('invitation', '/{Y}/{S}/{U}/invitation',
              launch_thread=True,
              function=invitation, upload_max_size = 1000000,
              )

def invitation_accept(server):
    if configuration.regtest:
        server.the_file.write(server._("MSG_evaluate"))
        return

    year, semester, ue, recipient, typ, max_time, the_checksum = server.the_path
    link = '/'.join(server.the_path[:-1])
    if checksum(link) != the_checksum:
        server.the_file.write(server._("MSG_invitation_bad"))
        return
    if time.time() > int(max_time):
        server.the_file.write(server._("MSG_invitation_expired"))
        return

    table = document.table(year, semester, ue, create=False)

    if server.ticket.user_name in table.the_key_dict:
        server.the_file.write(server._("MSG_invitation_yet_in"))
        return

    if typ == 'one_shot':
        for line in table.lines.values():
            if line[0].comment == recipient:
                server.the_file.write(server._("MSG_invitation_yet_used"))
                return

    try:
        table.lock()
        page = table.get_nobody_page()
        col_id = table.columns[0].the_id
        lin_id = table.create_line_id()
        table.cell_change(page, col_id, lin_id, server.ticket.user_name)
        table.comment_change(page, col_id, lin_id, recipient)
    finally:
        table.unlock()
        
    server.the_file.write(
        server._("MSG_invitation_accepted")
        + '<p><a href="{}">{}</a>'.format(
            configuration.suivi.url(ticket=server.ticket.ticket),
            server._("MSG_home_title")))
    
plugin.Plugin('invitation_accept', '/invitation_accept/{*}',
              function=invitation_accept, unsafe=False,
              priority = -10 # Before student_redirection
              )
