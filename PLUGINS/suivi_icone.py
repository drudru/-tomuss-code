#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet)
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

from .. import plugin
from .. import utilities
from .. import files
from .. import tablestat

try:
    import PIL.Image
    ok = True
except ImportError:
    utilities.warn("No Python module PIL")
    ok = False

def student_icone(server):
    """Generate an icon summarising the student information
    from all the tables."""
    if not ok:
        return
    
    login = server.the_student
    
    prst = []
    note = []
    ues = tablestat.the_ues(server.year, server.semester, login)
    if not ues:
        server.the_file.write(files.files['tip.png'].bytes())
        return
    for t in ues:
        for line in t.get_lines(login):
            prst += t.lines.line_indicator(line, what='Prst')
            note += t.lines.line_indicator(line, what='Note')

    prst.sort()
    prst = [v[1] for v in prst]
    
    note.sort()
    note = [v[1] for v in note]
                
    n = max(int(len(prst)**0.5), int(len(note)**0.5), 3) + 1
    s = [(238, 238, 238)] * ((2*n+1) * n)
    for i in range(n):
        s[n+i*(2*n+1)] = (255, 255, 255)

    for i, vv in enumerate(prst):
        vv = int(vv * 255)
        s[int(i/n)*(2*n+1) + i%n] = (255-vv, vv, 128)

    for i, vv in enumerate(note):
        vv = int(vv * 255)
        s[int(i/n)*(2*n+1) + i%n + n+1] = (255-vv, vv, 128)

    im = PIL.Image.new("RGB", (2*n+1, n))
    im.putdata(s)
    im.save(server.the_file, 'PNG')
    
plugin.Plugin('icone', '/{_I}',
              function=student_icone,
              priority=-20,
              # launch_thread=True,
              mimetype = 'image/png',
              unsafe=False,
              cached = True,
              )

