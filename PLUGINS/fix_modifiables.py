#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet)
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
from .. import plugin
from .. import column
from .. import document
from .. import tablestat
from ..cell import CellValue, Line
from .. import configuration
from .. import files

def fix_modifiables(server):
    """List of the modifiable OLD table"""

    last_week = time.time() - 7*86400
    lines = []
    server.the_file.write('''<html>
<pre id="fix_modifiable" style="font-size:200%"></pre>
<script>
var fix_modifiable_element = document.getElementById("fix_modifiable") ;
var fix_modifiable_nb = 0 ;
function x(t)
{
    fix_modifiable_nb++ ;
    if ( t === undefined )
        fix_modifiable_element.parentNode.removeChild(fix_modifiable_element);
    else
        fix_modifiable_element.innerHTML = fix_modifiable_nb + ' ' + t ;
}
function on_cell_change(data_lin, data_col, value)
{
    if ( value != no )
       return false ; // Allow only to switch to NO

    var line = lines[data_lin] ;
    var cell = line[data_col] ;
    // Localy update the cell in data and on the screen
    cell.set_value_local(value) ;
    var td = td_from_line_id_data_col(data_lin, data_col) ;
    if ( td !== undefined )
         update_cell(td, cell, columns[data_col]) ;

    // Do the action on the server
    var img = document.createElement('IMG') ;
    img.src = '/=' + ticket + '/fix_modifiable/' + line[0].value
              + '/' + line[1].value + '/' + line[2].value ;
    img.className = "server" ;
    if ( td )
        td.insertBefore(img, td.childNodes[0]) ;
    else
    {
        img.onload = function() { this.parentNode.removeChild(this) ; } ;
        document.getElementById('log').appendChild(img) ;
    }
    return false ; // Do not send the normal cell change to the server
}
</script>''')

    start = time.time()
    for t in tablestat.all_the_tables():
        server.the_file.write('<script>x("%s")</script>' % t)
        if (not t.modifiable
            or t.mtime > last_week
            or (t.year, t.semester) == configuration.year_semester
            or (t.year, t.semester) == configuration.year_semester_next
            or (t.year, t.semester) == configuration.year_semester_modifiable
            or t.semester in configuration.master_of_exceptions
            ):
            pass
        else:
            lines.append(
                Line((CellValue(t.year),
                      CellValue(t.semester),
                      CellValue(t.ue),
                      CellValue(time.strftime('%Y-%m-%d',
                                              time.localtime(t.mtime))),
                      CellValue(t.modifiable
                                and configuration.yes
                                or configuration.no),
                  )))
        t.unload()
    print 'RUNTIME %.1f minutes' % ((time.time() - start)/60)
    server.the_file.write('<script>x()</script>')

    columns = [
        column.Column('c0', '', freezed='F', type='Note', width=1,
                      rounding=1, minmax="[2008;2028]", title=server._('year'),
                  ),
        column.Column('c2', '', freezed='F', type='Text', width=2,
                      title=server._('semester'),
                  ),
        column.Column('c4', '', freezed='F', type='Text', width=8,
                      title=server._('COL_TITLE_table'),
                  ),
        column.Column('c6', '', type='Text', width=2,
                      title=server._('B_Date'),
                      comment=server._('MSG_table_modification_date'),
                  ),
        column.Column('c8', '', type='Bool', width=1,
                      cell_writable="",
                      title=server._('SELECT_table_modifiable_true'),
                  ),
        ]
    table_attrs = {
        'comment': server._('Basculer en non modifiable les tables'),
        'default_nr_columns': 5,
        'default_sort_columns': [0,1,2],
        }
    server.the_file.write("""<script>setTimeout("var modification_allowed_on_this_line = on_cell_change;", 1000) ;</script>""")
    document.virtual_table(server, columns, lines, table_attrs=table_attrs)

plugin.Plugin('fix_modifiables', '/fix_modifiables', function=fix_modifiables,
              group='roots', launch_thread = True,
              link=plugin.Link(where="root_rw", html_class="safe"),
              )

def fix_modifiable(server):
    t = document.table(server.the_year, server.the_semester, server.the_ue)
    if t is None:
        server.the_file.write(files.files["bug.png"])
        return
    try:
        t.lock()
        t.table_attr(t.pages[0], 'modifiable', 0)
    finally:
        t.unlock()
    t.unload()
    server.the_file.write(files.files["ok.png"])

plugin.Plugin('fix_modifiable',
              '/fix_modifiable/{Y}/{S}/{U}', function=fix_modifiable,
              group='roots',
              mimetype = 'image/png'
              )

