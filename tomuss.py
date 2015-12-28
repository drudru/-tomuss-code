#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2008-2011 Thierry EXCOFFIER, Universite Claude Bernard
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

import tomuss_init
import time
import sys
import os
import glob
import BaseHTTPServer
from . import abj
from . import configuration
from . import utilities
from . import document
from .files import files
from . import ticket
from . import sender

if False:
    from . import deadlock
    deadlock.start_check_deadlock()

warn = utilities.warn

running = True
current_time = time.time()

class FileProxy(object):
    def __init__(self, f):
        self.file = f
        self.closed = False
    def close(self):
        warn(str(self.file), what="debug")
        self.file.close()
        self.closed = True
    def write(self, t):
        self.file.write(t)
    def flush(self):
        self.file.flush()
    def __str__(self):
        return str(self.file)

class MyRequestBroker(utilities.FakeRequestHandler):

    def send_file(self, name):
        # print self.headers
        if name not in files:
            return
        s = files[name]
        content = str(s)
        self.send_response(200)
        if len(content) > 1000:
            content = s.gzipped
            self.send_header('Content-Encoding', 'gzip')
        if s.name and len(content) != 0:
            self.send_header('Content-Length', len(content))
        self.send_header('Content-Type', s.mimetype)
        if 'UNCACHED' in name:
            self.send_header('Cache-Control', 'no-cache')
        else:
            self.send_header('Cache-Control',
                             'max-age=%d' % configuration.maxage)
        self.end_headers()
        sender.append(self.wfile, content, keep_open=False)
        self.do_not_close_connection()

    def log_time(self, action, start_time=None):
        if start_time is None:
            start_time = self.start_time
        now = time.time()
        logs.write('%f %g %s\n' % (start_time, now - start_time, action))
        logs.flush()
        if sender.live_status:
            try:
                t = self.ticket.ticket.split('-')
                if len(t) == 3:
                    t = t[1]
                else:
                    t = ''
                t += '/' + self.ticket.user_name
                tt = self.ticket.access_right()
            except:
                t = 'N'
                tt = ''
                    
            year = ''
            semester = ''
            if action in ('pageaction', 'pagenew', 'pageresume',
                          'page_load_time', 'pagerewrite', 'end_of_load',
                          'answer_page'
                          ):
                if action == 'pageaction':
                    action = '*' + self.path.split('/')[7] + '*'
                elif action == 'page_load_time':
                    action += '(%.1fs)' % (now - start_time)
                year = str(self.the_year)
                semester = self.the_semester
            elif action == 'abjaction':
                action = '+' + self.path.split('/')[7] + '+'
            elif action == 'static-file':
                action = '_' + self.path.split('/')[1] + '_'
            try:
                ue = self.the_ue
            except:
                ue = ''
            sender.send_live_status(
                 '<script>d(%s,"%s","%s",%6.4f,"%s","%s",%s,%s);</script>\n' %
                 (utilities.js(ticket.client_ip(self)),
                  t,
                  tt,
                  now - start_time,
                  action, year, utilities.js(semester),
                  utilities.js(ue)))

    def do_GET_real(self):
        if self.path.startswith('/PROFILE_THIS_URL/'):
            self.path = self.path.replace('/PROFILE_THIS_URL/', '/')
            self.do_profile = True
        else:
            self.do_profile = False

        # APACHE make a mess with %2F %3F and others
        # so we encode them with $2F $3F...
        self.path = self.path.replace("$", "%")

        if ticket.client_ip(self) in configuration.banned_ip:
            self.send_file('bad.png')
            self.log_time('static-file')
            return

        if (self.path.startswith('/files/' + configuration.version)
            or self.path != '/' and self.path[1:] in files
            ):
            name = self.path.split("/")[-1]
            if name in files:
                self.send_file(name)
                self.log_time('static-file')
            return

        if self.path.startswith('/status/'):
            # No authentication because it is the way to see if server works
            self.send_response(200)
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Type', 'image/png')
            self.end_headers()
            self.wfile.write(files['ok.png'])
            self.log_time('status')
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

        the_ticket, self.the_path = ticket.get_ticket_string(self)
        self.ticket = ticket.get_ticket_objet(the_ticket, self)
        warn('ticket=%s' % str(self.ticket)[:-1])
        warn('the_path=%s' % str(self.the_path))

        self.the_file = self.wfile

        if plugin.dispatch_request(self, manage_error=False) is None:
            # An unauthenticated dispatch was done
            return

        if not self.ticket:
            # XXX : If Answer is an image : no redirect
            if len(self.the_path) > 5:
                try:
                    int(self.the_path[3])     # Page number
                    float(self.the_path[4])   # Request number
                    self.log_time('ticket-not-fine-for-image')
                    warn('Ticket not fine for image', what="auth")
                    # DO NOT MAKE AN ANSWER.
                    # THe BROWSER MUST UNDERSTAND THAT CONNECTION IS BROKEN
                    return
                except:
                    # Not an image, may be a page option
                    warn('Ticket not fine for not an image', what="auth")

        # Don't want to be blocked by authentication
        authentication.ok(self)

    def do_GET_real_real_safe(self):
        """Called by  authentication.ok"""
        plugin.dispatch_request(self)
            
    def do_GET(self):
        global current_time
        self.start_time = time.time()
        utilities.important_job_add("do_GET")
        if self.start_time - current_time > configuration.unload_interval:
            current_time = self.start_time
            document.remove_unused_tables() # Not in a thread : avoid problems
        try:
            self.do_GET_real()
        except: # IOError
            if '/picture/' in self.path:
                return # To common error to be logged
            user_name = self.__dict__.get('ticket', '')
            if not user_name:
                user_name = ''
            if not isinstance(user_name, str):
                user_name = user_name.user_name

            utilities.send_backtrace('',
                                     subject = 'BUG TOMUSS ('
                                     + self.path + ') ' + user_name
                                     )
            try:
                if 'the_file' in self.__dict__:
                    self.wfile = self.the_file
                if 'plugin' in self.__dict__:
                    if self.plugin.mimetype == 'image/png':
                        self.wfile.write(files['bug.png'])
                    else:
                        self.wfile.write('There is a bug')
                else:
                    self.send_file('bug.png')
            except:
                pass
        utilities.important_job_remove("do_GET")

if __name__ == "__main__":
    utilities.display_stack_on_kill()
    
    if 'regtest' in sys.argv:
        configuration.regtest = True
    if 'regtest_sync' in sys.argv:
        configuration.regtest_sync = True
    configuration.blur = 'blur' in sys.argv
    configuration.regtest_bug1 = 'regtest-bug1' in sys.argv
    from . import regtestpatch
    regtestpatch.do_patch()
    from . import plugin # AFTER from . import regtestpatch???
    from . import plugins
    plugins.load_types()
    document.table(0, 'Dossiers', 'config_table', None, None)
    document.table(0, 'Dossiers', 'config_acls', None, None)

    if 'checker' in sys.argv:
        from . import tablestat
        from .TEMPLATES import _ucbl_
        configuration.do_not_display = ()
        for table in tablestat.les_ues(2009,'Automne', true_file=True):
            warn(table.ue)
            _ucbl_.student_add_allowed(table)
        sys.exit(0)

    utilities.init()
        
    if 'recompute_the_ue_list' in sys.argv:
        from . import teacher
        print teacher.all_ues(compute=True)
        sys.exit(0)

    from . import authentication
    authentication.run_authentication()

    import socket
    for i in range(5):
        try:
            server = BaseHTTPServer.HTTPServer(("0.0.0.0",
                                                configuration.server_port),
                                               MyRequestBroker)
            break
        except socket.error:
            warn('Socket port used: %s' % configuration.server_port)
            time.sleep(1)
    else:
        raise IOError("Can not start TOMUSS")
    warn('Database:' + configuration.db)
    warn('Backup Database:' + configuration.backup + configuration.db)
    warn("Server Ready on:" + configuration.server_url)

    utilities.mkpath(os.path.join("LOGS", "TOMUSS"))
    logs = open(os.path.join("LOGS", "TOMUSS",
                             str(time.localtime()[0]) +".times"), "a")

    plugins.plugins_tomuss()
    document.table(0, 'Dossiers', 'config_plugin', None, None)
    plugins.generate_data_files()
    document.start_threads()

    authentication.authentication_redirect = configuration.server_url
    utilities.StaticFile._url_ = authentication.authentication_redirect

    utilities.start_new_thread_immortal(sender.send_thread, (True,))

    for i in range(3):
        utilities.start_new_thread_immortal(sender.send_thread, ())

    utilities.start_new_thread_immortal(sender.live_status_send_thread, ())

    document.table(0, 'Dossiers', 'config_home', None, None)
    document.table(0, 'Dossiers', 'config_cache', None, None)
    document.table(0, 'Dossiers', 'config_login', None, None)
    document.table(0, 'Dossiers', 'config_room', None, None)

    from . import display
    display.init()

    # While there is an updating table, there is many messages
    # Wait the end of the flow
    while utilities.filename_to_bufferize is not None:
        time.sleep(0.1)
    print '\n\n\n' +'*'*78
    print utilities._("MSG_tomuss_start"
                      ) % (configuration.server_url + '/=super.user')
    if configuration.regtest:
        regtest = 'regtest'
    else:
        regtest = ''
    for url, port, year, semester, host in configuration.suivi.servers():
        print '\t./suivi.py %d %s %d' % (year, semester, port), regtest
    print '*'*78 + '\n\n'

    # Translation of old files to new format
    for filename in glob.glob(os.path.join(configuration.db,
                                           'Y*', 'S*', 'abjs.py')):
        conv_year, conv_semester = filename.split(os.path.sep)[-3:-1]
        print 'Start translation of', filename
        abj.Abjs(int(conv_year[1:]), conv_semester[1:])

    if 'profile' in sys.argv:
        # To profile a single URL and not the full server.
        # Put PROFILE_THIS_URL just before the ticket:
        #    http://192.168.0.1:8888/PROFILE_THIS_URL/=ticket/stats
        import cProfile
        try:
            cProfile.run("while running: server.handle_request()", "xxx.prof")
        except KeyboardInterrupt:
            import pstats
            ps = pstats.Stats('xxx.prof')
            ps.strip_dirs().sort_stats('cumulative').print_stats()
    else:
        while running:
            server.handle_request()
        
    utilities.stop_threads()
