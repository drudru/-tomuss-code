#!/bin/env python3
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2010-2012 Thierry EXCOFFIER, Universite Claude Bernard
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

import time
import html
import re
from .. import plugin
from .. import inscrits
from .. import utilities
from .. import configuration

def progress_bar(server):
    "DEPRECATED"
    server.the_file.write('''
<div style="border:2px solid black;">
<div id="loading_bar" style="background:green">&nbsp;</div>
</div>''')

def progress_bar_update(server, nb, nb_max):
    "DEPRECATED"
    server.the_file.write("""<script>
document.getElementById('loading_bar').style.width = '%f%%' ;
</script>""" % ((100.*nb)/nb_max))
    server.the_file.flush()

def get_mail(txt):
    mail = inscrits.L_slow.mail(txt)
    if mail:
        return [mail]
    if '@' in txt:
        return re.split(" +", txt)
    return

def send_mail(server):
    """Send personnalized mails"""
    if configuration.regtest:
        server.the_file.write(server._("MSG_evaluate"))
        return

    progress_bar = utilities.ProgressBar(
        server, message = '<h1>' + server._("MSG_abj_wait") + '</h1>')
    
    data = server.uploaded
    if data is None:
        server.the_file.write("BUG")
        return

    subject = data.getfirst('subject')
    message = data.getfirst('message')
    recipients = data.getfirst('recipients').split("\001")
    titles = data.getfirst('titles').split("\001")
    try:
        cc = data.getfirst('cc').split("\001")
    except AttributeError:
        cc = None
    frome = inscrits.L_slow.mail(server.ticket.user_name)
    if frome is None:
        server.the_file.write('<b style="color:#F00">'
                              + server._("MSG_send_mail_impossible")
                              + '</b>'
                              + '<pre><hr><b>' + html.escape(subject)
                              + '</b><hr>\n'
                              + html.escape(message) + '<hr>'
                              + '\n'.join(
                inscrits.L_slow.mail(recipient.split("\002")[0])
                for recipient in recipients)
                              + '</pre>')
        return
        
    progress_bar.append_to_message(server._("MSG_send_mail_start")
                                   % len(recipients))

    bad_mails = []
    good_mails = []
    for nb, recipient in enumerate(recipients):
        recipient = recipient.split("\002")
        m = get_mail(recipient[0])
        if m is None:
            bad_mails.append(recipient[0])
            continue
        content = message
        the_subject = subject
        for title, value in zip(titles, recipient[1:]):
            title = '[' + title + ']'
            content = content.replace(title, value)
            the_subject = the_subject.replace(title, value)

        # print( m, the_subject, content, frome)
        carbon_copy = ()
        if cc:
            cc[nb] = get_mail(cc[nb])
            if cc[nb]:
                carbon_copy = cc[nb]
        utilities.send_mail_in_background(m, the_subject, content, frome,
                                          show_to = True, cc = carbon_copy)
        good_mails.append(m)
        progress_bar.update(nb, len(recipients))
    progress_bar.hide()

    archive = message + '\n' + '='*79 + '\n'
    if bad_mails:
        archive += (server._("MSG_send_mail_error") + '\n'
                    + '\n'.join(bad_mails) + '\n'
                    )
    archive += (server._("MSG_send_mail_done") + '\n'
                + '\n'.join(' '.join(i) for i in good_mails) + '\n'
                )
    if cc:
        archive += (server._("CC:") + '\n'
                + '\n'.join(' '.join(i)
                            for i in cc
                            if i
                ) + '\n'
                )

    utilities.send_mail_in_background(frome,
                                      server._("MSG_mail_archive")
                                      + ' ' + subject,
                                      archive, frome, show_to=True)
    server.the_file.write('<p>')
    if bad_mails:
        server.the_file.write(server._("MSG_send_mail_error")
                              + ', '.join(bad_mails) + '\n')
    progress_bar = utilities.ProgressBar(
        server, '<p>' + server._("MSG_send_mail_close"), show_numbers=False)
    progress_bar.wait_mail_sent()

plugin.Plugin('send_mail', '/send_mail', function=send_mail,
              upload_max_size = 1000000,
              group='staff', launch_thread=True)
