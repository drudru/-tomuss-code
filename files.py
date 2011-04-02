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

from utilities import StaticFile
import os
import configuration

files = {}
for name in (
    'style.css', 'hidden.css', 'suivi.css',
    'favicon.ico', 'top_tail.js', 'top_tail2.js', 
    'header.png',
    'charte.html',
    'verysafe.png', 'safe.png', 'unsafe.png', 'veryunsafe.png',
    'tip.png', 'feed.png', 'news.xml', 'eye.png', 
    'ok.png', 'bad.png', 'bug.png', 'feedback.png', 'abjus.png',
    'cross.png', 'leaves.png', 'weight.png', 'teacher.png',
    'close.png', 'cell_comment.png',
    'filtre.png','filtre2.png', 'comment.png', 'title.png',
    'up.gif', 'down.gif', 'next.gif', 'prev.gif',
    'sort_down.png', 'sort_up.png',
    'sort_down2.png', 'sort_up2.png',
    'tt.png',
    'lib.js', 'abj.js','types.js','utilities.js',
    'middle.js',
    'abj.html',
    'nat.html', 'nabjm.html', 'error.html', 'unauthorized.html',
    'robots.txt',
    'doc_table.html', 'doc_suivi.html', 'documentation.js', 'documentation.css',
    'stats.html', 'ticket.html',
    'live_status.js', 'bilan.js', 'bilan.css',
    ):
    files[name] = StaticFile(os.path.join('FILES', name))

for name in (
    'xxx.change.weeks.png', 'xxx.change.hours.png', 'xxx.change.days.png',
    'xxx.suivi.weeks.png', 'xxx.suivi.hours.png', 'xxx.suivi.days.png',
    'xxx.page_load_time.png',
    'xxx.page_load_time_1d.png',
    'xxx.page_load_time_1w.png',
    'xxx.page_load_time_evolution.png',
    'all_ues.js.gz','all_ues.js',
    'premier_cours.html',
    ):
    files[name] = StaticFile(os.path.join('TMP', name))

files['charte.html'].replace_on_load('<input', '<p')
files['style.css'].translate = lambda x:x.replace('_LOGO_', configuration.logo)
