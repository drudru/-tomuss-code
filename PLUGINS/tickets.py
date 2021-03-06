#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2009 Thierry EXCOFFIER, Universite Claude Bernard
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
from .. import plugin
from .. import ticket
from .. import document
from .. import cell
from .. import column

def tickets(server):
    """Display tickets"""
    lines = []
    for t in ticket.get_values():
        lines.append(cell.Line((
                    cell.CellValue(t.user_name),
                    cell.CellValue(time.strftime('%Y-%m-%d %H:%M.%S',
                                                 time.localtime(t.date))),
                    cell.CellValue(t.user_ip),
                    cell.CellValue(str(t.access_right())),
                    cell.CellValue(repr(t.user_browser)))))

    columns = [
        column.Column('0', '', freezed='F', width=2,
                      title=server._('COL_TITLE_ID')),
        column.Column('1', '', width=2,
                      title=server._('COL_TITLE_ticket_date'),
                      comment=server._('COL_COMMENT_ticket_date'),
                      ),
        column.Column('2', '', width=2,
                      title=server._('COL_TITLE_ticket_IP'),
                      comment=server._('COL_COMMENT_ticket_IP'),
                      ),
        column.Column('3', '', width=2, type="Text",
                      title=server._('COL_TITLE_ticket_access_rights'),
                      comment=server._('COL_COMMENT_ticket_access_rights'),
                      ),
        column.Column('4', '', width=6,
                      title=server._('COL_TITLE_ticket_browser'),
                      comment=server._('COL_COMMENT_ticket_browser'),
                      ),
        ]
    document.virtual_table(server, columns, lines,
                           table_attrs={
            'default_nr_columns': 6,
            'comment': server._('LINK_tickets'),
            })

plugin.Plugin('tickets', '/tickets', function=tickets, group='roots',
              launch_thread=True,
              link=plugin.Link(where='informations', html_class="verysafe")
              )





