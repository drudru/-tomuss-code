#!/bin/env python3
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2017 Thierry EXCOFFIER, Universite Claude Bernard
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

import subprocess
from ..column import ColumnAttr
from .. import plugin
from .. import document
from .. import configuration

class ColumnSpeak(ColumnAttr):
    name = "speak"
    action = "column_speak"
    always_visible = 1
    check_and_set = "function(value, column) { return Number(value) ;}"
    need_authorization = 0

    def encode(self, value):
        try:
            return int(value)
        except ValueError:
            return 0
    def check(self, value):
        if value in (0, 1, 2, 3, '0', '1', '2', '3'):
            return ''
        return self.check_error(value)

    gui_display = "GUI_select"
    css = '#menutop DIV.tabs #t_column_speak { width: 8em }'


    javascript = """
function column_speak(select)
{
  var action = select.selectedIndex ;
  var a = document.getElementsByTagName("AUDIO") ;
  if ( a.length )
    {
    a[0].parentNode.removeChild(a[0]) ;
    if ( action == 0 )
        return ;
    }
  a = document.createElement("AUDIO") ;
  var t = '<source src="' + url + '/=' + ticket + '/' + year + '/'
          + semester + '/' + ue + '/column_speak/'
          + the_current_cell.column.data_col + '/' + action ;
  for(var line in filtered_lines)
     t += '/' + filtered_lines[line][0].value ;
  a.controls = true ;
  a.autoplay = true ;
  a.onended = function() { a.parentNode.removeChild(a) ; } ;
  a.innerHTML = t + '" type="audio/x-wav"/>' ;
  the_body.appendChild(a) ;
}
"""

def column_speak(server):
    table = document.table(server.the_year, server.the_semester,
                           server.the_ue, create=False)
    if table is None:
        return
    col = int(server.the_path[0])
    speed = int(server.the_path[1])
    s = []
    for student in server.the_path[2:]:
        for line_id, line in table.get_items(student):
            s.append("{}. {}. . {} .".format(line[2].value.title(),
                                           line[1].value.title(),
                                           line[col].value))
    p = subprocess.Popen("espeak -v {} -s {} -b 1 --stdin --stdout".format(
        configuration.language, int(120 * 1.2**speed)).split(' '),
                         stdin = subprocess.PIPE,
                         stdout = server.the_file,
                         stderr = subprocess.STDOUT)
    p.stdin.write('\n'.join(s).encode("utf-8"))
    p.stdin.close()
    p.wait()

plugin.Plugin('column_speak', '/{Y}/{S}/{U}/column_speak/{*}',
              function=column_speak, launch_thread = True,
              mimetype="audio/x-wav", cached=False

          )
