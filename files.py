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
from . import utilities
from . import configuration

files = {}

def add(*args):
    filename = args[-1]
    old = files.get(filename, None)
    files[filename] = utilities.StaticFile(os.path.join(*args))
    if old:
        files[filename].append_text = old.append_text
        files[filename].replace_text = old.replace_text
        files[filename].clear_cache()
        str(files[filename]) # XXX It does not work without this !
    return files[filename]

def append(filename, key, content):
    """'append' can by called before 'add'"""
    if filename not in files:
        files[filename] = utilities.StaticFile(os.path.join("FILES",
                                                            "bad.png"))
    files[filename].append(key, content)

for name in (
    'style.css',
    'favicon.ico',
    'header.png',
    'verysafe.png', 'safe.png', 'unsafe.png', 'veryunsafe.png',
    'tip.png', 'feed.png', 'news.xml', 'eye.png', 'butterflynet.png',
    'ok.png', 'bad.png', 'bug.png', 'feedback.png', 'abjus.png',
    'weight.png', 'teacher.png',
    'close.png', 'cell_comment.png',
    'filtre.png','filtre2.png', 'comment.png', 'title.png', 'columns.png',
    'visible.png', 'empty.png', 'rounding.png', 'course_dates.png',
    "import.png",
    'up.gif', 'down.gif', 'next.gif', 'prev.gif',
    'sort_down.png', 'sort_up.png',
    'sort_down2.png', 'sort_up2.png',
    'tt.png',
    'lib.js', 'abj.js','types.js','utilities.js',
    'middle.js',
    'abj.html',
    'robots.txt',
    'doc_table.html', 'documentation.js', 'documentation.css',
    'stats.html',
    'howto.html',
    'printemps.png', 'automne.png'
    ):
    add('FILES', name)

for name in (
    'xxx.change.weeks.png', 'xxx.change.hours.png', 'xxx.change.days.png',
    'xxx.suivi.weeks.png', 'xxx.suivi.hours.png', 'xxx.suivi.days.png',
    'xxx.page_load_time.png',
    'xxx.page_load_time_1d.png',
    'xxx.page_load_time_1w.png',
    'xxx.page_load_time_evolution.png',
    'xxx.page_load_time_evolutionW.png',
    'xxx.preferences.png',
    'all_ues.js.gz','all_ues.js',
    'premier_cours.html',
    ):
    add('TMP', name)

files['lib.js'].append('files.py',
                       utilities.wait_scripts()
                       + '\nvar semesters = '
                       + utilities.js(configuration.semesters) + ';\n'
                       + '\nvar semesters_year = '
                       + utilities.js(configuration.semesters_year) + ';\n'
                       + '\nvar semesters_months = '
                       + utilities.js(configuration.semesters_months) + ';\n'
                       + '\nvar semesters_color = '
                       + utilities.js(configuration.semesters_color) + ';\n'
                       )

