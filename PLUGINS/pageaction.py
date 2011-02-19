#!/usr/bin/env python
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

import plugin
import document
import abj
import utilities
import time

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
                                 server.ticket, do_not_unload=1)
    # the time is after the '.' in order to fully disable caching
    request = int(server.the_path[0].split('.')[0])
    action = server.the_path[1]
    path = server.the_path[2:]
    page.add_request(request, action, path, server.the_file)


def page_resume(server):
    """Display the list of ABJ, DA and TT for the students in the table.
    It is the same list being sended by mail."""
    lines, mails = abj.ue_resume(server.the_ue, server.the_year,
                                 server.the_semester, server.the_file)
    server.the_file.write(''.join(lines).encode('utf-8'))


plugin.Plugin('pagerewrite', '/{Y}/{S}/{U}/rewrite',
              function=page_rewrite, teacher=True,
              mimetype = "text/plain; charset=UTF-8",
              launch_thread = True)

plugin.Plugin('pageresume', '/{Y}/{S}/{U}/resume',
              function=page_resume, teacher=True,
              mimetype = "text/plain; charset=UTF-8",
              launch_thread = True)

plugin.Plugin('pageaction', '/{Y}/{S}/{U}/{P}/{*}', function=page_action,
              teacher=True, mimetype = "image/png",
              keep_open=True,
              cached = True, # We don't want browser reloading actions
              )

import os
import configuration

def extension(server):
    """Extend the table used in 'Automne' semester to be used
    in 'Printemps' semester.
    A symbolic link is created and the current table is accessible
    in the 2 semester but modifiable only in the 'Printemps' one.
    """
    if server.the_semester != "Printemps":
        server.the_file.write("Vous n'êtes pas autorisé à faire ceci car l'extension d'UE ce fait de l'automne vers le printemps.")
        return

    table = document.table(server.the_year, server.the_semester,
                           server.the_ue, None, None)

    if server.ticket.user_name not in table.masters and server.ticket.user_name not in table.teachers:
        server.the_file.write("Vous n'êtes pas autorisé à faire ceci car vous n'êtes pas responsable de l'UE.")
        return

    empty, message = table.empty(empty_even_if_used_page=True,
                                 empty_even_if_created_today=True,
                                 empty_even_if_column_created=True)
    if not empty:
        server.the_file.write("Vous n'êtes pas autorisé à faire ceci car la page %s n'est pas vide : " % table.location() + message)
        return

    old_filename = document.table_filename(server.the_year-1, 'Automne',
                                           server.the_ue)
    new_filename = table.filename

    if not os.path.exists(old_filename):
        server.the_file.write("Vous n'êtes pas autorisé à faire ceci car l'UE n'existait pas au semestre d'automne")
        return

    # The table in the previous semester should not be modified.
    t = document.table(server.the_year-1, 'Automne', server.the_ue, ro=True)
    t.modifiable = 0

    utilities.warn('Move %s to %s' % (old_filename, new_filename))
    utilities.rename_safe(old_filename, new_filename)

    # XXX: We hope that nobody will recreate the table at the instant.

    new_filename = os.path.join(*new_filename.split(os.path.sep)[1:])

    utilities.symlink_safe(os.path.join('..', '..', new_filename),
                           old_filename)

    pages = len(table.active_pages) + len(t.active_pages)

    table.unload(force=True)
    t.unload(force=True)

    server.the_file.write("Extension de l'automne vers le printemps réussie. L'UE n'est maintenant plus semestrialisée")
    return
        

plugin.Plugin('extension', '/{Y}/{S}/{U}/extension', teacher=True,
              function=extension,
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
              teacher=True, mimetype = None,
              )

def delete_this_table(server):
    """Delete the table."""
    table = document.table(server.the_year, server.the_semester,
                           server.the_ue, None, None)
    if not table.modifiable:
        server.the_file.write('On ne peut pas détruire des tables non modifiable')
        return
    if server.ticket.user_name not in (table.teachers + table.masters):
        server.the_file.write('Seul un responsable de l\'UE peut détruire la table')
        return

## Uncomment these lines in order to remove deleted tables from favorites.
##    d = utilities.manage_key('LOGINS',
##                             os.path.join(server.ticket.user_name, 'pages')
##                             )
##    if d:
##        d = eval(d)
##        if server.the_ue in d:
##            del d[server.the_ue]
##            utilities.manage_key('LOGINS',
##                                 os.path.join(server.ticket.user_name,
##                                              'pages'),
##                                 content = repr(d)
##                                 )
    
    table.delete()
    server.the_file.write('La destruction a été faite.')
    

plugin.Plugin('delete_this_table', '/{Y}/{S}/{U}/delete_this_table',
              teacher=True,
              function=delete_this_table,
              )

def end_of_load(server):
    """Keep track of the end of page loading to do stats.
    If the page takes too long to load, then 'newpage.py' assumes
    that something blocked TOMUSS because the page loading does not finish.
    """
    table, page = document.table(server.the_year, server.the_semester,
                                 server.the_ue, server.the_page, server.ticket)
    page.end_of_load = time.time()
    try:
        server.log_time('page_load_time', start_time=page.start_load)
        # server.the_file.write('OK\n')
    except AttributeError:
        pass

plugin.Plugin('end_of_load', '/{Y}/{S}/{U}/{P}/end_of_load',
              function=end_of_load,
              teacher=True,
              mimetype='image/png'
              )
