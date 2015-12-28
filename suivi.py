#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet)
#    Copyright (C) 2008-2013 Thierry EXCOFFIER, Universite Claude Bernard
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

# import locale
# locale.setlocale(locale.LC_ALL, 'fr_FR.utf8')

import tomuss_init
import os
import sys
import time
import re
import BaseHTTPServer
from . import configuration
from . import utilities
from . import authentication
from . import plugin
from . import ticket

if False:
    from . import deadlock
    deadlock.start_check_deadlock()

warn = utilities.warn

StaticFile = utilities.StaticFile

running = True

class MyRequestBroker(utilities.FakeRequestHandler):
    def log_time(self, action):
        time_logs.write('%f %g %s\n' % (self.start_time, time.time()
                                   - self.start_time, action))
        time_logs.flush()

    def do_GET(self):
        try:
            self.do_GET_real()
        except:
            utilities.send_backtrace('',
                                     subject='GET path = ' + self.path)

    def do_GET_real(self):
        if ticket.client_ip(self) in configuration.banned_ip:
            return
        self.start_time = time.time()
        self.the_port = server_port
        self.ticket = None

        if self.path.startswith('/PROFILE_THIS_URL/'):
            self.path = self.path.replace('/PROFILE_THIS_URL/', '/')
            self.do_profile = True
        else:
            self.do_profile = False

        # APACHE make a mess with %2F %3F and others
        # so we encode them with $2F $3F...
        self.path = self.path.replace("$", "%")
        self.the_path = self.path.split('/')[1:]

        # Remove year/semester if present
        # They are only useful to use an Apache dispatch on the good port
        ip = 0
        if self.the_path[0].startswith('='):
            ip += 1
        try:
            self.year = int(self.the_path[ip])
            self.semester = self.the_path[ip+1]
            # The 'rss2' plugin need year/semesters not in configuration.semesters
            # if self.semester not in configuration.semesters:
            #    raise ValueError('')
            del self.the_path[ip:ip+2]
        except (ValueError, IndexError):
            self.year, self.semester = configuration.year_semester
        path = '/' + '/'.join(self.the_path)

        if path.startswith('/load_config/'):
            i = utilities.read_file(os.path.join('TMP', 'xxx.load_config'))
            if path == '/load_config/' + i:
                to_reload = ('config_table', 'config_plugin', 'config_acls',
                             'config_cache')
                for tt in to_reload:
                    conf = document.table(0, 'Dossiers',tt, None, None,ro=True)
                    conf.do_not_unload = []
                    conf.unload()
                for tt in to_reload:
                    document.table(0, 'Dossiers', tt, None, None, ro=True)
                configuration.config_acls_clear_cache()
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write('ok')
            return

        if path[1:] == 'robots.txt':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(utilities.read_file(os.path.join("FILES",
                                                              "robots.txt")))
            return

        if configuration.regtest and path == '/stop':
            global running
            self.send_response(200)
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write('stopped')
            running = False
            return
        
        self.the_file = self.wfile
        self.the_rfile = self.rfile
        # self.do_not_close_connection()
        if plugin.dispatch_request(self, manage_error=False) is None:
            # XXX Assumes that a thread is not launched
            return # Unauthenticated dispatch is done

        self.path = path
        the_ticket, self.the_path = ticket.get_ticket_string(self)
        self.ticket = ticket.get_ticket_objet(the_ticket, self)
        warn('ticket=%s' % str(self.ticket)[:-1])
        warn('the_path=%s' % str(self.the_path))

        if path.startswith('/='):
            # For RegTest authenticator
            self.old_ticket = path.split("/")[1][1:]
        # Restore year/semester in order to have a good redirection
        if configuration.regtest:
            self.path = '/%d/%s' % (self.year, self.semester) + path
        else:
            # Remove old ticket.
            self.path = '/%d/%s' % (
                self.year, self.semester) + re.sub("^/=[^/]*/?", "/", path)
        # Don't want to be blocked by authentication
        authentication.ok(self)

        # Free some memory
        now = time.time()
        if now - server.last_unload > 60:
            nb = 0
            nb_unloaded = 0
            for t in document.tables_values():
                nb += 1
                if now - getattr(t,"rtime",0) > configuration.unload_interval:
                    t.unload()
                    nb_unloaded += 1
            server.last_unload = now
            warn("%d table unloaded on %d" % (nb_unloaded, nb), what="info")

    def do_GET_real_real_safe(self):
        """Called by  authentication.ok"""
        logs.write(time.strftime('%Y%m%d%H%M%S ')+self.ticket.user_name + '\n')
        plugin.dispatch_request(self)

if __name__ == "__main__":
    try:
        if sys.argv[1] == 'any' and sys.argv[2] == 'any':
            year = semester = year_semester = None
        else:
            year = int(sys.argv[1])
            semester = sys.argv[2]
            year_semester = "%d/%s" % (year, semester)
        server_port = int(sys.argv[3])
    except:
        sys.stderr.write("%s yearYYYY|any semester|any TCPport\n"% sys.argv[0])
        sys.exit(1)

    for i in sys.argv:
        if i == 'regtest':
            configuration.regtest = True
    configuration.blur = 'blur' in sys.argv
    from . import regtestpatch
    regtestpatch.do_patch()
    configuration.read_only = True
    from . import document
    from . import plugins
    plugins.load_types()
    document.table(0, 'Dossiers', 'config_table', None, None,
                   ro=True, create=False)
    document.table(0, 'Dossiers', 'config_acls', None, None,
                   ro=True, create=False)
    warn("Configuration table loaded, do_not_display=%s" % repr(configuration.do_not_display))
    utilities.init()


    utilities.mkpath(os.path.join("LOGS", "SUIVI%d" % server_port))
    logs = open(os.path.join("LOGS", "SUIVI%d" % server_port,
                             str(time.localtime()[0]) + '.connections'), "a")
    time_logs = open(os.path.join("LOGS", "SUIVI%d" % server_port,
                                  str(time.localtime()[0]) + '.times'), "a")

    plugins.plugins_suivi()
    document.table(0, 'Dossiers', 'config_plugin', None, None,
                   ro=True, create=False)
    document.table(0, 'Dossiers', 'config_cache', None, None,
                   ro=True, create=False)

    authentication.run_authentication()

    server = BaseHTTPServer.HTTPServer(("0.0.0.0", server_port),
                                       MyRequestBroker)
    server.last_unload = 0

    StaticFile._url_ = configuration.suivi.url(year, semester, ticket='')
    authentication.authentication_redirect = '/'.join(StaticFile._url_.split('/')[:-2])
    
    plugins.generate_data_files(suivi=True)

    if configuration.regtest:
        # 'Suivi' regtest fail because list of modified UE
        # is not displayed for teachers
        configuration.index_are_computed = False

    if not configuration.index_are_computed:
        from . import tablestat

        # Load all the tables, in order to allow fast access
        for t in tablestat.les_ues(year, semester):
            if False:
                warn("%s grpcol=%s seqcol=%s" % (t.ue, t.columns.get_grp(),
                                                 t.columns.get_seq()))

    warn("Server Ready on: " + authentication.authentication_redirect)
    while running:
        server.handle_request()
    utilities.stop_threads()




