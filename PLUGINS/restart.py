#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2014 Thierry EXCOFFIER, Universite Claude Bernard
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
#    Contact: Thierry.EXCOFFIER@univ-lyon1.fr

import time
import sys
import os
import signal
import subprocess
from .. import plugin
from .. import utilities
from .. import document
from .. import sender

wait = 10 # In minutes

def restart_tomuss(server):
    "Restart TOMUSS when it is unused"
    _ = server._
    def w(txt):
        server.the_file.write(txt)
        if txt[-1] != ' ':
            server.the_file.write('<br>\n')
        server.the_file.flush()
    w(_("HELP_restart_tomuss"))
    while True:
        w(time.ctime() + ' ')
        if utilities.send_mail_in_background_list:
            w(_("MSG_restart_mailqueue")
              % len(utilities.send_mail_in_background_list))
        elif document.request_list:
            w(_("MSG_restart_request_list") % len(document.request_list))
        elif sender.File.to_send:
            w(_("MSG_restart_sender") % len(sender.File.to_send))
        else:
            for t in document.tables_values():
                if (time.time() - t.mtime < wait*60
                    or time.time() - t.atime < wait*60):
                    w(_("MSG_restart_access") % wait)
                    break
            else:
                # Restart TOMUSS
                w('GO '*10)
                subprocess.Popen(sys.argv, close_fds=True)
                os.kill(os.getpid(), signal.SIGINT)
                return # Never here
        time.sleep(60)

plugin.Plugin('restart_tomuss', '/restart_tomuss', group='roots',
              function=restart_tomuss, launch_thread=True,
              link=plugin.Link(where='debug', html_class='unsafe')
              )
