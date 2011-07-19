#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet)
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
import utilities
import subprocess
from tablestat import les_ues
import os

def student_icone(server):
    """Generate an icone summarising the student information
    from all the tables."""
    login = server.the_student
    
    prst = []
    note = []
    for t in les_ues(server.year, server.semester):
        for line in t.get_lines(login):
            prst += t.lines.line_indicator(line, what='Prst')
            note += t.lines.line_indicator(line, what='Note')

    prst.sort()
    prst = [v[1] for v in prst]
    
    note.sort()
    note = [v[1] for v in note]
                
    n = max(int(len(prst)**0.5), int(len(note)**0.5), 3) + 1
    s = ["\356\356\356"] * ((2*n+1) * n)
    for i in range(n): s[n+i*(2*n+1)] = '\377\377\377'

    for i, vv in enumerate(prst):
        vv = int(vv * 255)
        s[int(i/n)*(2*n+1) + i%n] = chr(255-vv) + chr(vv) + chr(128)

    for i, vv in enumerate(note):
        vv = int(vv * 255)
        s[int(i/n)*(2*n+1) + i%n + n+1] = chr(255-vv) + chr(vv) + chr(128)

    process = subprocess.Popen("pnmtopng",
                               stdin = subprocess.PIPE,
                               stdout = server.the_file,
                               )

    process.stdin.write("P6\n%d %d\n255\n" % (2*n+1, n) + ''.join(s))
    process.stdin.close()
    # os.waitpid(process.pid, 0)


plugin.Plugin('icone', '/{_I}',
              function=student_icone,
              # launch_thread=True,
              authenticated=False,
              mimetype = 'image/png',
              )

plugin.Plugin('icone_withticket', '/{?}/{_I}',
              function=student_icone,
              authenticated=False,
              # launch_thread=True,
              mimetype = 'image/png',
              )

