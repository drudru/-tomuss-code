#!/bin/env python
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

import time
import plugin
import inscrits
from files import files
import utilities
import configuration

def send_mail(server):
    """Send personnalized mails"""
    if configuration.regtest:
        server.the_file.write(server._("MSG_evaluate"))
        return

    data = server.get_posted_data()
    if data is None:
        return

    subject = data['subject'][0]
    message = data['message'][0]
    recipients = data['recipients'][0].split("\001")
    titles = data['titles'][0].split("\001")
    
    server.the_file.write(server._("MSG_send_mail_start") % len(recipients))
    server.the_file.write("<p>")
    frome = inscrits.L_slow.mail(server.ticket.user_name)
    bad_mails = []
    good_mails = []
    for recipient in recipients:
        recipient = recipient.split("\002")
        m = inscrits.L_slow.mail(recipient[0])
        if m is None:
            bad_mails.append(recipient[0])
            continue
        content = message
        the_subject = subject
        for title, value in zip(titles, recipient[1:]):
            title = '[' + title + ']'
            content = content.replace(title, value)
            the_subject = the_subject.replace(title, value)

        the_subject = unicode(the_subject, 'utf-8').encode('utf-8')
        content = unicode(content, 'utf-8')
        # print m, the_subject, content, frome
        utilities.send_mail_in_background(m, the_subject, content, frome)
        good_mails.append(m)
        server.the_file.write('%d ' % len(good_mails))

    archive = unicode(message, 'utf-8') + '\n' + '='*79 + '\n'
    if bad_mails:
        archive += (server._("MSG_send_mail_error") + '\n'
                    + '\n'.join(bad_mails) + '\n'
                    )
    archive += (server._("MSG_send_mail_done") + '\n'
                + '\n'.join(good_mails) + '\n'
                )

    utilities.send_mail_in_background(frome,
                                      server._("MSG_mail_archive")
                                      + ' ' + subject,
                                      archive, frome, show_to=True)
    server.the_file.write('<p>')
    if bad_mails:
        server.the_file.write(server._("MSG_send_mail_error")
                              + repr(bad_mails) + '\n')
    server.the_file.write('<p>' + server._("MSG_send_mail_close") + '<p>')
    while utilities.send_mail_in_background_list:
        server.the_file.write(server._("MSG_send_mail_left")
                              % len(utilities.send_mail_in_background_list)
                              + '\n')
        time.sleep(1)
    server.the_file.write(server._("MSG_send_mail_left") % 0)

plugin.Plugin('send_mail', '/send_mail', function=send_mail,
              group='staff', launch_thread=True)
