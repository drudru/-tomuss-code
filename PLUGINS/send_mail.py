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

    subject = server.the_path[0]
    message = server.the_path[1]
    n = 0
    while ('[' + str(n) + ']') in message + subject:
        n += 1

    n += 1 # For the student ID always here
    args = server.the_path[2:]
    if len(args) % n != 0:
        server.the_file.write(server._("TIP_violet_square"))
        utilities.send_backtrace('send_mail')
        return

    server.the_file.write(server._("MSG_send_mail_start") % (len(args)/n))
    server.the_file.flush()

    frome = inscrits.L_slow.mail(server.ticket.user_name)
    bad_mails = []
    for i in range(0, len(args), n):
        m = inscrits.L_slow.mail(args[i])
        if m is None:
            bad_mails.append(args[i])
            continue
        content = message
        the_subject = subject
        for j in range(i+1, i+n):
            old = '[' + str(j-i-1) + ']'
            new = args[j]
            content = content.replace(old, new)
            the_subject = the_subject.replace(old, new)

        the_subject = unicode(the_subject, 'utf-8').encode('utf-8')
        content = unicode(content, 'utf-8')
        # print m, the_subject, content, frome
        utilities.send_mail_in_background(m, the_subject, content, frome)
        
    if len(bad_mails) == 0:
        server.the_file.write(server._("MSG_send_mail_done") + '\n')
    else:
        server.the_file.write(server._("MSG_send_mail_error")
                              + repr(bad_mails) + '\n')
    

plugin.Plugin('send_mail', '/send_mail/{*}', function=send_mail,
              group='staff', launch_thread=True,
              mimetype='text/plain;charset=utf-8')
