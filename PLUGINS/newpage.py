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

import os
import re
import time

from .. import plugin
from .. import document
from ..utilities import warn
from .. import configuration
from .. import sender
from .. import utilities
from .. import column

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
var  set_updating    = window.parent.set_updating    ;
</script>
    '''

class StringFile(object):
    """This class allows to store content before the browser asks it.
    """
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
            try:
                self.real_file.write(content)
                self.real_file.flush()
            except AttributeError:
                self.closed = True
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


def extented(year, semester, ue):
    table = document.table(year, semester, ue, create=False)
    if not table:
        return
    if not table.modifiable:
        return
    ts = configuration.semester_span(table.year, table.semester)
    if not ts:
        return
    
    if column.TableAttr.attrs['dates'].encode(ts) != table.dates:
        # The user has changed table dates
        # Do not change the user value
        return
    
    # Need to indicate new dates
    year2, semester2 = utilities.next_year_semester(table.year, table.semester)
    # XXX Assume there only one semester extension
    ts2 = configuration.semester_span(year2, semester2)
    ts = ts.split(' ')[0] + ' ' + ts2.split(' ')[1]
    table.lock()
    try:
        table.date_change(table.pages[0], ts)
    finally:
        table.unlock()

def new_page(server):
    """Create a new page and send the table editor to the client."""

    filename = document.table_filename(server.the_year, server.the_semester,
                                       server.the_ue)
    first_semester = configuration.university_semesters[0]
    first_table = document.table_filename(utilities.university_year(),
                                          first_semester,
                                          server.the_ue)
    # XXX Not working if UE ends with -1 -2...
    if (server.the_semester != first_semester
        and not os.path.exists(filename)
        and os.path.exists(first_table)
        and re.search(configuration.ue_not_per_semester, server.the_ue)
        ):
        # Create a symbolic link from current semester to first semester
        utilities.symlink_safe(
            os.path.join('..', '..',
                         os.path.sep.join(first_table.split(os.path.sep)[-3:])
                         ),
            filename)
    start_load = time.time()
    try:
        table, page = document.table(server.the_year, server.the_semester,
                                     server.the_ue, None, server.ticket,
                                     do_not_unload='new_page')
    except IOError:
        server.the_file.write(server._("TIP_violet_square"))
        server.close_connection_now()
        utilities.send_backtrace(repr(server.the_path), 'Newpage IOError')
        return

    if table == None:
        utilities.send_backtrace(repr(server.the_path), 'Newpage Unauthorized',
                                 exception=False)
        server.the_file.write(server._("MSG_new_page_unauthorized"))
        server.close_connection_now()
        warn('No Table', what="error")
        return

    if not table.on_disc:
        table.do_not_unload_remove('new_page')
        server.the_file.write("%s/%s/%s" % (
                server.the_year, server.the_semester, server.the_ue))
        server.the_file.write(server._("MSG_new_page_in_past"))
        server.close_connection_now()
        return

    if table.is_extended:
        table.do_not_unload_remove('new_page')
        # Take the link destination (assuming ../..) and remove the .py
        year, semester, ue = table.link_to()
        link_to = '../../%s/%s/%s' % (year, semester, ue)
        # Check table dates
        # XXX It is done here in order to fix old files
        extented(year, semester, ue)
        server.the_file.write(
            '<meta HTTP-EQUIV="REFRESH" content="0; url=%s">' % (link_to,))
        server.close_connection_now()
        return
    
    warn('New page, do_not_unload=%s' % table.do_not_unload, what="table")

    if configuration.regtest_sync:
        # We want immediate update of the table content (abjs for example)
        document.update_students.append(table)
        document.check_new_students_real()

    # Update the number of access for the user
    # No lock because it is not important (there is a lock in manage_key)
    if server.the_semester in configuration.semesters:
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
        if True:
            server.the_file.write(table.content(page))
        else:
            # simulation slow connection
            for i in table.content(page).split('\n'):
                server.the_file.write(i + '\n')
                if 'P(' in i:
                    time.sleep(0.01)
        server.the_file.flush()

        if page.use_frame:
            table.active_page(page, StringFile())
        else:
            table.active_page(page, server.the_file)
    finally:
        # Can't be unloaded because it is active.
        table.do_not_unload_remove('new_page')
        table.unlock()
    if configuration.regtest_sync:
        # We want immediate update of navigator content
        while sender.File.nr_active_thread or sender.File.to_send:
            time.sleep(0.01)
        if not configuration.regtest_bug1:
            server.close_connection_now()
    warn('Actives=%s do_not_unload=%s' % (
        table.active_pages, table.do_not_unload), what="table")

    page.start_load = start_load # For end_of_load computation

    if page.use_frame:
        server.close_connection_now()
    else:
        if page.use_linear:
            table.active_pages.remove(page) # Avoid 'Canceled load' message
            server.close_connection_now()
            # page.browser_file.close()
        else:
            # XXX: I can't remember why it is here
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
        if server.the_student:
            # Do not revert request sent
            # It is possible to go in the future because page.request
            # may forgot incrementation.
            page.request = max(int(server.the_student), page.request)
    except ValueError:
        server.the_file.write(
            '''
<script>
if (window.parent.click_to_revalidate_ticket)
      window.parent.click_to_revalidate_ticket() ;
else
      Alert("ALERT_new_page_too_old") ;
</script>''')
        server.close_connection_now()
        return
    except:
        # Reconnection of an old non modifiable page on: a stopped server
        # or with an old ticket after a connection lost.
        # See REGTEST_SERVER/tests.py 'lostpage'
        server.the_file.write('<script>window.parent.location = "%s/%s/%s/%s";</script>' % (configuration.server_url, server.the_year, server.the_semester, server.the_ue))
        server.close_connection_now()
        utilities.send_backtrace('', 'Page not found')
        return

    if not hasattr(page, 'use_frame'):
        warn('Browser reconnection', what="error")
        page.use_frame = True

    if not page.use_frame:
        warn('Page not using frame (LINEAR?)', what="error")
        server.close_connection_now()
        return

    if page.browser_file:
        table.lock()
        try:
            if page.browser_file.closed:
                # The page was not closed by the document thread
                table.remove_active_page(page)
        finally:
            table.unlock()
    
    if isinstance(page.browser_file, StringFile):
        warn('ok', what="info")
        page.browser_file.set_real_file(server.the_file)
        sender.append(page.browser_file, str(page.page_id) ) # Flush data
    else:
        warn('Browser reconnection index=%s' % page.index, what='Info')
        if page.browser_file is None:
             page.browser_file = StringFile()
        if page.index is not None:
            page.browser_file.write(
                ''.join(table.sent_to_browsers[page.index-1:]))
        page.browser_file.set_real_file(server.the_file)
        page.browser_file.flush()
        page.end_of_load = 0 # end_of_load will not be called
        if configuration.regtest_sync:
            server.close_connection_now()
        else:
            table.active_page(page, page.browser_file)

plugin.Plugin('answer_page', '/{Y}/{S}/{U}/{P}/{I}',
              function=answer_page, group='staff',
              keep_open = True,
              priority = -2, # Before other actions
              )

plugin.Plugin('pagenew', '/{Y}/{S}/{U}/{=}', function=new_page, group='staff',
              keep_open = True,
              launch_thread = True, unsafe=False)

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

plugin.Plugin('set_page', '/set_page/{U}/{P}', function=set_page,
              group='staff')

