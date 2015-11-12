#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2008 Thierry EXCOFFIER, Universite Claude Bernard
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
import os
from .. import plugin
from .. import document
from .. import abj
from .. import utilities
from .. import files

def page_rewrite(server):
    """Generate the minimal python module defining the current
    table state. So there is no more history."""
    # do_not_unload : not import because it is readonly
    table = document.table(server.the_year, server.the_semester,
                           server.the_ue, None, None)
    server.the_file.write(table.rewrite())

def page_action(server):
    """An editing action on the table is queued.
    The client may not send the action in the good order."""
    table, page = document.table(server.the_year, server.the_semester,
                                 server.the_ue, server.the_page,
                                 server.ticket, do_not_unload='page_action')
    # the time is after the '.' in order to fully disable caching
    try:
        request = int(server.the_path[0].split('.')[0])
        action = server.the_path[1]
        path = server.the_path[2:]
    except:
        table.do_not_unload_remove('page_action')
        utilities.send_backtrace(repr(server.the_path), 'Page Action')
        return
    page.add_request(request, action, path, server.the_file)


def page_resume(server):
    """Display the list of ABJ, DA and TT for the students in the table.
    It is the same list being sended by mail."""
    lines, dummy_mails = abj.ue_resume(server.the_ue, server.the_year,
                                       server.the_semester, server.the_file)
    server.the_file.write(''.join(lines))


plugin.Plugin('pagerewrite', '/{Y}/{S}/{U}/rewrite',
              function=page_rewrite, group='staff',
              mimetype = "text/plain; charset=UTF-8",
              launch_thread = True)

plugin.Plugin('pageresume', '/{Y}/{S}/{U}/resume',
              function=page_resume, group='staff',
              mimetype = "text/plain; charset=UTF-8",
              launch_thread = True)

plugin.Plugin('pageaction', '/{Y}/{S}/{U}/{P}/{*}', function=page_action,
              group='staff', mimetype = "image/png",
              keep_open=True,
              cached = True, # We don't want browser reloading actions
              priority = -1, # The most frequent plugin call
              )

def page_unload(server):
    """Unload page from memory"""
    table = document.table(server.the_year, server.the_semester,
                           server.the_ue, None, None)
    if table:
        server.the_file.write(server._("MSG_page_unload_before") + '<br>\n')
        table.unload(force=True)
        server.the_file.write(server._("MSG_page_unload_after") + '<br>\n')
    else:
        server.the_file.write(server._("MSG_page_unload_no_table") + "<br>\n")

plugin.Plugin('page_unload', '/{Y}/{S}/{U}/page_unload',
              function=page_unload, group='roots')

def extension(server):
    """Extend the current table to the next semester.
    A symbolic link is created and the current table is accessible
    in the 2 semesters but modifiable only in the 'next' semester.
    """

    next_year, next_semester = utilities.next_year_semester(
        server.the_year, server.the_semester)

    table = document.table(next_year, next_semester, server.the_ue, None, None)

    empty, message = table.empty(empty_even_if_used_page=True,
                                 empty_even_if_created_today=True,
                                 empty_even_if_column_created=True)
    if not empty:
        server.the_file.write(server._("MSG_extension_not_empty")
                              % table.location() + message)
        return

    old_filename = document.table_filename(server.the_year,
                                           server.the_semester,
                                           server.the_ue)
    new_filename = table.filename

    if not os.path.exists(old_filename):
        server.the_file.write(server._("MSG_extension_no_table")
                              % (server.the_year, server.the_semester))
        return

    if os.path.islink(old_filename):
        server.the_file.write(server._("MSG_extension_yet_done"))
        return

    # The table in the previous semester should not be modified.
    t = document.table(server.the_year, server.the_semester, server.the_ue,
                       ro=True)
    if server.ticket.user_name not in t.masters:
        server.the_file.write(server._("MSG_extension_not_master"))
        return

    t.modifiable = 0

    utilities.warn('Move %s to %s' % (old_filename, new_filename))
    utilities.rename_safe(old_filename, new_filename)

    # XXX: We hope that nobody will recreate the table at the instant.
    # Must be moved into document.py/table_manage

    new_filename = os.path.join(*new_filename.split(os.path.sep)[1:])

    utilities.symlink_safe(os.path.join('..', '..', new_filename),
                           old_filename)
    table.unload(force=True)
    t.unload(force=True)

    server.the_file.write(server._("MSG_extension_ok")
                          % (server.the_semester, next_semester))

    utilities.start_new_thread(document.update_indexes,
                               (next_year, next_semester, server.the_ue))

plugin.Plugin('extension', '/{Y}/{S}/{U}/extension', group='staff',
              function=extension,
              )

def bookmark(server):
    """Toggle the bookmarked state of a table"""
    key = os.path.join(server.ticket.user_name, 'bookmarked')
    bookmarked = utilities.manage_key('LOGINS', key)
    if bookmarked is False:
        bookmarked = []
    else:
        bookmarked = eval(bookmarked)

    bookmark = (server.the_year, server.the_semester, server.the_ue)
    if bookmark in bookmarked:
        bookmarked.remove(bookmark)
    else:
        bookmarked.append(bookmark)
    utilities.manage_key('LOGINS', key, content = repr(bookmarked))
    server.the_file.write(files.files['ok.png'].bytes())

plugin.Plugin('bookmark', '/{Y}/{S}/{U}/bookmark', group='staff',
              function=bookmark, mimetype = 'image/png'
              )


def key_history(server):
    """Store the received data in the key history.
    It is used in 'linear' interface to analyse how it is used."""
    utilities.append_file(os.path.join('LOGS', 'key_history'),
                          '%s %d/%s/%s %s\n' % (
        server.ticket, server.the_year, server.the_semester, server.the_ue,
        server.the_path[0]))

plugin.Plugin('key_history', '/{Y}/{S}/{U}/{P}/key_history/{*}',
              function=key_history,
              group='staff', mimetype = None,
              priority=-2
              )

def end_of_load(server):
    """Keep track of the end of page loading to do stats.
    If the page takes too long to load, then 'newpage.py' assumes
    that something blocked TOMUSS because the page loading does not finish.
    """
    dummy_table, page = document.table(server.the_year, server.the_semester,
                                       server.the_ue, server.the_page,
                                       server.ticket)
    page.end_of_load = time.time()
    try:
        server.log_time('page_load_time', start_time=page.start_load)
        # server.the_file.write('OK\n')
    except AttributeError:
        pass

plugin.Plugin('end_of_load', '/{Y}/{S}/{U}/{P}/end_of_load',
              function=end_of_load,
              group='staff',
              mimetype='image/png',
              priority=-2
              )
