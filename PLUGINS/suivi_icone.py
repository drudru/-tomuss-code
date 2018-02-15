#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet)
#    Copyright (C) 2008-2018 Thierry EXCOFFIER, Universite Claude Bernard
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
from .. import utilities
from .. import files
from .. import tablestat
from .. import configuration

try:
    import PIL.Image
    ok = True
except ImportError:
    utilities.warn("No Python module PIL")
    ok = False

def student_icone_no_index(server):
    """Generate an icon summarising the student information
    from all the tables."""
    
    login = server.the_student
    
    prst = []
    note = []
    ues = tablestat.the_ues(server.year, server.semester, login)
    if not ues:
        server.the_file.write(files.files['tip.png'].bytes())
        return prst, note
    for t in ues:
        for line in t.get_lines(login):
            prst += t.lines.line_indicator(line, what='Prst')
            note += t.lines.line_indicator(line, what='Note')

    prst.sort()
    prst = [(255 - v[1]*255, v[1]*255, 128) for v in prst]
    
    note.sort()
    note = [(int(255 - v[1]*255), int(v[1]*255), 128) for v in note]

    return prst, note

colors = {
        configuration.pre: (0  , 255,   0),
        configuration.abj: (0  ,   0, 255),
        configuration.abi: (255,   0,   0),
}

def student_icone_index(server):
    """Generate an icon summarising the student information
    from all the tables."""
    prst = []
    note = []
    content = utilities.manage_key('LOGINS',
                                   os.path.join(server.the_student, 'grades'))
    if content:
        content = content.split('\n')
    else:
        return  student_icone_no_index(server)
    y = str(server.year)
    for grade in content:
        date, year, semester, grade = grade.split(' ')
        if semester != server.semester or year != y:
            continue
        if grade in colors:
            prst.append(colors[grade])
        else:
            grade = float(grade)
            note.append((int((1 - grade) * 255),
                         int(grade * 255),
                         128))
    return prst, note


def student_icone(server):
    if not ok:
        return

    prst, note = student_icone_index(server)

    if not prst and not note:
        server.the_file.write(files.files['tip.png'].bytes())
        return

    n = max(int(len(prst)**0.5), int(len(note)**0.5), 3) + 1
    s = [(238, 238, 238)] * ((2*n+1) * n)
    for i in range(n):
        s[n+i*(2*n+1)] = (255, 255, 255)

    for i, vv in enumerate(prst):
        s[int(i/n)*(2*n+1) + i%n] = vv

    for i, vv in enumerate(note):
        s[int(i/n)*(2*n+1) + i%n + n+1] = vv

    im = PIL.Image.new("RGB", (2*n+1, n))
    im.putdata(s)
    im.save(server.the_file, 'PNG')

plugin.Plugin('icone', '/{_I}',
              function=student_icone,
              priority=-20,
              mimetype = 'image/png',
              unsafe=False,
              cached = True,
              )

