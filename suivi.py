#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet)
#    Copyright (C) 2008,2009 Thierry EXCOFFIER, Universite Claude Bernard
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

if False:
    import deadlock
    deadlock.start_check_deadlock()

import configuration
import utilities
import BaseHTTPServer
import os
import authentication
import sys
import time
import plugin
import ticket
import inscrits

warn = utilities.warn

StaticFile = utilities.StaticFile

running = True

from files import files

class MyRequestBroker(BaseHTTPServer.BaseHTTPRequestHandler):
    def log_time(self, action):
        time_logs.write('%f %g %s\n' % (self.start_time, time.time()
                                   - self.start_time, action))
        time_logs.flush()
    def do_GET(self):
        # self.rfile.close()
        try:
            self.do_GET_real()
        except:            
            utilities.send_backtrace(repr(self.header),
                                     subject='GET path = ' + self.path)

    def do_GET_real(self):
        if ticket.client_ip(self) in configuration.banned_ip:
            return
        self.start_time = time.time()
        self.year = year
        self.semester = semester
        self.the_port = server_port
        self.ticket = None
        self.the_path = self.path.split('/')[1:]

        # Remove year/semester if present
        # They are only useful to use an Apache dispatch on the good port
        if '/'.join(self.the_path[0:2]) == year_semester:
            del self.the_path[0:2]
        elif '/'.join(self.the_path[1:3]) == year_semester:
            del self.the_path[1:3]
        self.path = '/' + '/'.join(self.the_path)

        if self.path[1:] == 'load_config':
            import document
            t = document.table(0, 'Dossiers', 'config_table',
                           None, None, ro=True)
            t.unload()
            t = document.table(0, 'Dossiers', 'config_plugin',
                           None, None, ro=True)
            t.unload()
            t = document.table(0, 'Dossiers', 'config_table',
                           None, None, ro=True)
            t = document.table(0, 'Dossiers', 'config_plugin',
                           None, None, ro=True)
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write('ok')
            return

        if self.path[1:] in files and self.path[1:] != '':
            warn('PATH=(%s)' % self.path[1:])
            self.send_response(200)
            f = files[self.path[1:]]
            self.send_header('Content-Type', f.mimetype)
            self.send_header('Content-Length', len(f))
            self.end_headers()
            self.wfile.write( f )
            self.log_time('static_file')
            return

        if configuration.regtest and self.path == '/stop':
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
        self.wfile = plugin.Useles
        if plugin.dispatch_request(self, manage_error=False) == None:
            return # Unauthenticated dispatch is done

        self.ticket, self.the_path = ticket.get_ticket_string(self)
        self.ticket = ticket.get_ticket_objet(self.ticket)
        warn('ticket=%s' % str(self.ticket)[:-1])
        warn('the_path=%s' % str(self.the_path))

        if self.ticket and not self.ticket.is_fine(self):
            warn('Ticket not fine!', what="auth")
            old_ticket = self.ticket
            self.ticket = None
            if old_ticket != None:
                self.the_path = self.path.split('/')[2:]
                self.path = '/' + '/'.join(self.the_path)

            authentication.authentication_requests.append(self)
            return


        # Don't want to be blocked by 'is_an_abj_master' test
        if self.ticket == None or not hasattr(self.ticket, 'password_ok'):
            warn('Append to authentication queue', what="auth")
            authentication.authentication_requests.append(self)
        else:
            self.do_GET_real_real_safe()
        warn('the_file=%s(%s) wfile=%s' % (self.the_file,
                                           self.the_file.closed, self.wfile),
             what="debug")

    def do_GET_real_real_safe(self):
        tick = self.ticket
        logs.write(time.strftime('%Y%m%d%H%M%S ') + tick.user_name + '\n')
        plugin.dispatch_request(self)

    def address_string(self):
        """Override to avoid DNS lookups"""
        return "%s:%d" % self.client_address

if __name__ == "__main__":
    utilities.display_stack_on_kill()

    utilities.start_new_thread_immortal(utilities.sendmail_thread, (),
                                        send_mail=False)
    try:
        year = int(sys.argv[1])
        semester = sys.argv[2]
        year_semester = "%d/%s" % (year, semester)
        server_port = int(sys.argv[3])
    except:
        sys.stderr.write("""%s AnneeYYYY semestre TCPport\n""" % sys.argv[0])
        sys.exit(1)

    for i in sys.argv:
        if i == 'regtest':
            configuration.regtest = True
    import regtestpatch
    regtestpatch.do_patch()
    configuration.read_only = True
    import document
    import plugins
    plugins.load_types()
    document.table(0, 'Dossiers', 'config_table', None, None,
                   ro=True, create=False)
    warn("Configuration table loaded, do_not_display=%s" % repr(configuration.do_not_display))

    logs = open(os.path.join("LOGS", "SUIVI%d" % server_port,
                             str(time.localtime()[0]) + '.connections'), "a")
    time_logs = open(os.path.join("LOGS", "SUIVI%d" % server_port,
                                  str(time.localtime()[0]) + '.times'), "a")

    plugins.plugins_suivi()
    document.table(0, 'Dossiers', 'config_plugin', None, None,
                   ro=True, create=False)

    authentication.run_authentication()

    server = BaseHTTPServer.HTTPServer(("0.0.0.0", server_port),
                                       MyRequestBroker)
    
    authentication.authentication_redirect = configuration.suivi.url(year, semester, ticket='TICKET')
    StaticFile._url_ = '/'.join(authentication.authentication_redirect.split('/')[0:-3])

    import tablestat

    # Load all the tables, in order to allow fast acces
    for t in tablestat.les_ues(year, semester):
        if False:
            warn("%s grpcol=%s seqcol=%s" % (t.ue, t.columns.get_grp(),
                                             t.columns.get_seq()))

    warn("Server Ready on: " + authentication.authentication_redirect)
    while running:
        server.handle_request()
    utilities.stop_threads()




