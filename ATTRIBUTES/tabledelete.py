#!/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2009-2013 Thierry EXCOFFIER, Universite Claude Bernard
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

from .. import plugin
from .. import document
from . import tabletabletitle

class TableDelete(tabletabletitle.TableTableTitle):
    name = 'table_delete'
    action = 'table_delete'
    gui_display = "GUI_a"

def delete_this_table(server):
    """Delete the table."""
    table = document.table(server.the_year, server.the_semester,
                           server.the_ue, None, None)
    if not table.modifiable:
        server.the_file.write(server._("MSG_delete_this_table_unmodifiable"))
        return
    if server.ticket.user_name not in table.masters:
        server.the_file.write(server._("MSG_extension_not_master"))
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
    server.the_file.write(server._("MSG_delete_this_table_done"))
    

plugin.Plugin('delete_this_table', '/{Y}/{S}/{U}/delete_this_table',
              group='staff',
              function=delete_this_table,
              )

