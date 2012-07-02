#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet)
#    Copyright (C) 2008-2012 Thierry EXCOFFIER, Universite Claude Bernard
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
import time
import plugin
import document
import utilities
import configuration
import column
import cell

class Stat:
    sum = 0
    nr = 0
    min = 1e9
    max = 0
    sorted = False
    values = None
    
    def __init__(self):
        self.values = []

    def add(self, duration):
        self.values.append(duration)
        self.sum += duration
        self.nr += 1
        if duration < self.min:
            self.min = duration
        if duration > self.max:
            self.max = duration
        self.sorted = False

    def avg(self):
        if self.nr:
            return self.sum / self.nr
        return 1
    
    def mediane(self):
        if not self.sorted:
            self.values.sort()
            self.sorted = True
        if self.nr:
            return self.values[len(self.values)/2]
        else:
            return 1

    def problems(self):
        if self.nr:
            avg = self.avg()
            return len(list([i
                             for i in self.values
                             if i > 4*avg])
                       ) / float(self.nr)
        else:
            return 0
    
    def __str__(self):
        mediane = self.mediane()
        avg = self.avg()
        return 'Avg:%9.4f Avg/Med:%5.1f Min:%8.4f Max:%10.6f Sum:%11.6f [%5d] %2d%%>4*Avg' % (
            avg, avg/mediane, self.min, self.max, self.sum, self.nr,
            int(100*self.problems()))

def run(service_name, lines):
    try:
        f = open(os.path.join('LOGS', service_name), 'r')
    except IOError:
        utilities.warn(service_name + ' unreadable')
        return
    service_name = service_name.split('.')[0]

    d = {}

    begin_time = None
    start_time = 0
    five_minute = time.time() - 5*60
    one_hour = time.time() - 60*60
    one_day = time.time() - 60*60*24
    one_week = time.time() - 60*60*24*7
    one_month = time.time() - 60*60*24*30
    for line in f:
        try:
            start_time, duration, name = line.strip().split(' ')
            if begin_time == None:
                begin_time = float(start_time)
            duration = float(duration)
            start_time = float(start_time)
        except ValueError:
            continue
        if name not in d:
            d[name] = (Stat(), Stat(), Stat(), Stat(), Stat(), Stat())
        d[name][0].add(duration)
        if start_time > five_minute:
            d[name][1].add(duration)
        if start_time > one_hour:
            d[name][2].add(duration)
        if start_time > one_day:
            d[name][3].add(duration)
        if start_time > one_week:
            d[name][4].add(duration)
        if start_time > one_month:
            d[name][5].add(duration)
        
    keys = list(d.keys())
    keys.sort(lambda x, y: cmp(d[x][0].sum/(d[x][0].nr+1),
                               d[y][0].sum/(d[y][0].nr+1)) )
    keys.reverse()
    for k in keys:
        launch_thread = ' '
        for p in plugin.plugins:
            if p.name == k:
                if p.launch_thread:
                    launch_thread = '*' # XXX Miss many
                    break

        for when, dd in zip(('All', '5 minutes', 'hour',
                             'day', 'week', 'month'), d[k]):
            if dd.nr == 0:
                continue
            lines.append(cell.Line((
                        cell.CellValue(service_name),
                        cell.CellValue(k),
                        cell.CellValue(dd.avg()*1000),
                        cell.CellValue(dd.avg()/dd.mediane()),
                        cell.CellValue(dd.min*1000),
                        cell.CellValue(dd.max*1000),
                        cell.CellValue(dd.sum),
                        cell.CellValue(dd.nr),
                        cell.CellValue(launch_thread == '*'
                                       and 'OUI' or ''),
                        cell.CellValue(dd.problems()
                                       and dd.problems()*100 or ''),
                        cell.CellValue(when),
                        )))


@utilities.add_a_lock
def profiling(server):
    """Display the statistics on the plugin usage, number of call and times."""

    columns = (
        column.Column('0', '', freezed='F', width=2, type='Text',
                      title=server._('COL_TITLE_service')),
        column.Column('1', '', freezed='F', width=2, type='Text',
                      title=server._('COL_TITLE_plugin')),
        column.Column('2', '', width=2, type='Note', minmax='[0;1000]',
                      title=server._('COL_TITLE_avg'),
                      comment=server._('COL_COMMENT_avg'),
                      ),
        column.Column('3', '', width=2, type='Note', minmax='[0;10]',
                      title=server._('COL_TITLE_avg/med'),
                      comment=server._('COL_COMMENT_avg/med'),
                      ),
        column.Column('4', '', width=2, type='Note', minmax='[0;1000]',
                      title=server._('COL_TITLE_min'),
                      comment=server._('COL_COMMENT_min'),
                      ),
        column.Column('5', '', width=2, type='Note', minmax='[0;1000]',
                      title=server._('COL_TITLE_max'),
                      comment=server._('COL_COMMENT_max'),
                      ),
        column.Column('6', '', width=2, type='Note', minmax='[0;NaN]',
                      title=server._('COL_TITLE_total'),
                      comment=server._('COL_COMMENT_total'),
                      ),
        column.Column('7', '', width=2, type='Note', minmax='[0;NaN]',
                      title=server._('COL_TITLE_call'),
                      comment=server._('COL_COMMENT_call'),
                      ),
        column.Column('8', '', width=2, type='Text',
                      title=server._('COL_TITLE_batch'),
                      comment=server._('COL_COMMENT_batch'),
                      ),
        column.Column('9', '', width=2, type='Note', minmax='[0;5]',
                      title=server._('COL_TITLE_slow'),
                      comment=server._('COL_COMMENT_slow'),
                      ),
        column.Column('10', '', width=2, type='Text',
                      title=server._('COL_TITLE_when'),
                      comment=server._('COL_COMMENT_when'),
                      ),
        )
    lines = []                     
    run(os.path.join('TOMUSS', str(server.the_year) + '.times'), lines)

    for url, port, year, semester, host in configuration.suivi.urls.values():
        server.the_file.write('\n')
        run(os.path.join('SUIVI%d' % port, str(server.the_year) + '.times'
                         ), lines)

    document.virtual_table(server, columns, lines,
                           {
            'comment': server._("TABLE_COMMENT_profiling"),
            'default_nr_columns': 11,
            })

plugin.Plugin('profiling', '/profiling/{Y}',
              function=profiling,
              root = True,
              launch_thread = True,
              keep_open = True,
              link=plugin.Link(html_class="verysafe", where='debug',
                               url="javascript:go_year_after('profiling')"
                               ),
              )

