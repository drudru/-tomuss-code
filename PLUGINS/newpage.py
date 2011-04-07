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

import plugin
import document
from files import files
from utilities import warn
import configuration
import time
import sender
import utilities
import os

initial_content = '''
<script>
window.parent.server_answered() ;
var    Xcell_change  = window.parent.Xcell_change    ;
var Xcomment_change  = window.parent.Xcomment_change ;
var  Xcolumn_delete  = window.parent.Xcolumn_delete  ;
var  Xcolumn_attr    = window.parent.Xcolumn_attr    ;
var  Xtable_attr     = window.parent.Xtable_attr     ;
var  change_abjs     = window.parent.change_abjs     ;
var  saved           = window.parent.saved           ;
var  connected       = window.parent.connected       ;
var  update_mail     = window.parent.update_mail     ;
var  update_portail  = window.parent.update_portail  ;
var  login_list      = window.parent.login_list      ;
</script>
    '''

class StringFile(object):
    def __init__(self):
        self.closed = False
        self.real_file = None
        self.open_time = time.time()
        # XXX COPY/PASTE in the end of lib.js
        self.content = [initial_content]
    def write(self, txt):
        self.content.append(txt)
    def flush(self):
        if self.real_file:
            content = ''.join(self.content) 
            self.content = [] # no big memory leakage
            self.real_file.write(content)
            self.real_file.flush()
        else:
            if time.time() - self.open_time > 60:
                self.closed = True
    def set_real_file(self, f):
        if self.real_file is not None:
            self.content = [initial_content]
        self.real_file = f
    def close(self):
        self.flush()
        if self.real_file:
            self.real_file.close()
            self.closed = True
    def __str__(self):
        if self.real_file:
            rfc = self.real_file.closed
        else:
            rfc = '???'
        return 'closed=%s content=%d real_file=%s RF.closed=%s' % (
            self.closed, len(self.content), self.real_file, rfc
            ) + ''.join(self.content)

def new_page(server):
    """Create a new page and send the table editor to the client."""
    start_load = time.time()
    try:
        table, page = document.table(server.the_year, server.the_semester,
                                     server.the_ue, None, server.ticket,
                                     do_not_unload=1)
    except IOError:
        server.the_file.write(files["error.html"])
        server.the_file.close()
        utilities.send_backtrace(repr(server.the_path), 'Newpage IOError')
        return

    if table == None:
        server.the_file.write(files["unauthorized.html"])
        server.the_file.close()
        warn('No Table', what="error")
        return

    if table.is_extended:
        # Take the link destination (assuming ../..) and remove the .py
        link_to = os.readlink(table.filename)[:-3].split(os.path.sep)
        if len(link_to) == 3:
            assert(link_to[0] == '..')
            assert(link_to[1][0] == 'S')
            link_to[1] = link_to[1][1:]
        elif len(link_to) == 5:
            assert(link_to[0] == '..')
            assert(link_to[1] == '..')
            assert(link_to[2][0] == 'Y')
            assert(link_to[3][0] == 'S')
            link_to[2] = link_to[2][1:]
            link_to[3] = link_to[3][1:]
        else:
            assert(len(link_to) == 1)

        link_to = os.path.join(*link_to)
        
        server.the_file.write('<meta HTTP-EQUIV="REFRESH" content="0; url=%s">' % (link_to,))
        server.the_file.close()
        table.do_not_unload_add(-1)
        return
    
    warn('New page, do_not_unload=%d' % table.do_not_unload, what="table")

    if configuration.regtest_sync:
        document.check_new_students_real()
        time.sleep(0.1) # XXX Wait student list update

    # Update the number of access for the user
    # No lock because it is not important (there is a lock in manage_key)
    if server.the_semester in ('Printemps', 'Automne'):
        d = utilities.manage_key('LOGINS',
                                 os.path.join(server.ticket.user_name, 'pages')
                                 )
        if d is False:
            d = {}
        else:
            d = eval(d)
        if server.the_ue not in d:
            d[server.the_ue] = 1
        else:
            d[server.the_ue] += 1
        utilities.manage_key('LOGINS',
                             os.path.join(server.ticket.user_name, 'pages'),
                             content = repr(d)
                             )
    page.use_frame = True
    page.use_linear = '=linear=' in server.options
    if configuration.regtest_sync or page.use_linear:
        if not configuration.regtest_bug1:
            page.use_frame = False

    warn('New page, use_frame=%d' % page.use_frame, what="table")

    # With this lock cell modification can't be lost
    # between page content creation and the page activation
    table.lock()
    try:
        server.the_file.write(table.content(page))
        server.the_file.flush()

        if page.use_frame:
            table.active_page(page, StringFile())
        else:
            table.active_page(page, server.the_file)
    finally:
        # Can't be unloaded because it is active.
        table.do_not_unload_add(-1)
        table.unlock()
    if configuration.regtest_sync:
        # We want immediate update of navigator content
        while document.update_students or \
              sender.File.nr_active_thread or sender.File.to_send:
            time.sleep(0.01)
        if not configuration.regtest_bug1:
            server.the_file.close()
    warn('Actives=%s do_not_unload=%s' % (
        table.active_pages, table.do_not_unload), what="table")

    page.start_load = start_load # For end_of_load computation

    if page.use_frame:
        server.the_file.close()
    else:
        if page.use_linear:
            table.active_pages.remove(page) # Avoid 'Canceled load' message
            page.browser_file.close()
        else:
            if configuration.db == 'DBtest':
                time.sleep(2) # To not lose time when debugging
            else:
                time.sleep(8) # 5 seconds is too short


plugin.Plugin('emptyname', '/{Y}/{S}/', response=307,
              headers = lambda x: (('Location', '%s/=%s' %
                                    (configuration.server_url,
                                     x.ticket.ticket)),
                                   ),
              documentation = "Bad url, redirect user to the home page")

def answer_page(server):
    """Connect the browser IFRAME to the page"""
    try:
        table, page = document.table(server.the_year, server.the_semester,
                                     server.the_ue, server.the_page,
                                     server.ticket)
    except ValueError, e:
        server.the_file.write(
            '''
<script>
if (window.parent.click_to_revalidate_ticket)
      window.parent.click_to_revalidate_ticket() ;
else
      alert("Votre page est trop vieille, réactualisez la. Si votre navigateur est récent vous ne perdrez aucune donnée si 'AutoSauve' est bien activé.") ;
</script>''')
        server.the_file.close()
        return
    except:
        # Reconnection of an old non modifiable page on: a stopped server
        # or with an old ticket after a connection lost.
        # See REGTEST_SERVER/tests.py 'lostpage'
        server.the_file.write('<script>window.parent.location = "%s/%s/%s/%s"</script>' % (configuration.server_url, server.the_year, server.the_semester, server.the_ue))
        server.the_file.close()
        utilities.send_backtrace('', 'Page not found')
        return

    if not hasattr(page, 'use_frame'):
        warn('Browser reconnection', what="error")
        page.use_frame = True
        # server.the_file.close()
        # return

    if not page.use_frame:
        warn('Page not using frame (LINEAR?)', what="error")
        server.the_file.close()
        return

    if isinstance(page.browser_file, StringFile):
        warn('ok', what="info")
        page.browser_file.set_real_file(server.the_file)
        sender.append(page.browser_file, str(page.page_id) ) # Flush data
    else:
        warn('Browser reconnection', what='Info')
        if page.browser_file is None:
             page.browser_file = StringFile()
            
        page.browser_file.set_real_file(server.the_file)
        table.active_page(page, page.browser_file)
        # server.the_file.close()


plugin.Plugin('answer_page', '/{Y}/{S}/{U}/{P}',
              function=answer_page, teacher=True,
              keep_open = True,
              administrative = None,
              )



plugin.Plugin('pagenew', '/{Y}/{S}/{U}/{=}', function=new_page, teacher=True,
              keep_open = True,
              administrative = None,
              launch_thread = True)

def set_page(server):
    """Set the number of page load (for favorites management by users)"""
    d = utilities.manage_key('LOGINS',
                             os.path.join(server.ticket.user_name, 'pages')
                             )
    if d is False:
        d = {}
    else:
        d = eval(d)
    if server.the_page:
        d[server.the_ue] = server.the_page # Safe because {P} is integer
    else:
        if server.the_ue in d:
            del d[server.the_ue]
    utilities.manage_key('LOGINS',
                         os.path.join(server.ticket.user_name, 'pages'),
                         content = repr(d)
                         )
    return 'ok'

plugin.Plugin('set_page', '/set_page/{U}/{P}', function=set_page, teacher=True)

