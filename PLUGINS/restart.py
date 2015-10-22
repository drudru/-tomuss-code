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

wait = 1 # Tables must be unused for this time in minutes

def restart_tomuss(server, start=True):
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
        for t in document.tables_values():
            mtime = time.time() - t.mtime
            if  mtime < wait*60:
                w(_("MSG_restart_access") % wait
                  + ' <small>(%s mtime=%d seconds)</small>' % (t, mtime))
                break
        else:
            if utilities.important_job_running():
                w(str(utilities.current_jobs))
            else:
                # Restart TOMUSS
                w('GO '*10)
                utilities.warn(repr(sys.argv))
                if start:
                    subprocess.Popen(sys.argv, close_fds=True)
                os.kill(os.getpid(), signal.SIGINT)
                time.sleep(1)
                os.kill(os.getpid(), signal.SIGTERM)
                time.sleep(1)
                os.kill(os.getpid(), signal.SIGKILL)
                return # Never here
        time.sleep(wait*6)

plugin.Plugin('restart_tomuss', '/restart_tomuss', group='roots',
              function=restart_tomuss, launch_thread=True,
              link=plugin.Link(where='debug', html_class='unsafe')
              )

plugin.Plugin('stop_tomuss', '/stop_tomuss', group='roots',
              function=lambda server: restart_tomuss(server, start=False),
              launch_thread=True,
              link=plugin.Link(where='debug', html_class='veryunsafe')
              )
