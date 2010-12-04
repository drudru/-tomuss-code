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
import os
import time
import document
import utilities
import configuration

class Stat:
    def __init__(self):
        self.sum = 0
        self.nr = 0
        self.min = 1e9
        self.max = 0
        self.list = []
        self.sorted = False

    def add(self, duration):
        self.list.append(duration)
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
            self.list.sort()
            self.sorted = True
        if self.nr:
            return self.list[len(self.list)/2]
        else:
            return 1

    def problems(self):
        if self.nr:
            avg = self.avg()
            return len(list([i for i in self.list if i > 4*avg])) / float(self.nr)
        else:
            return 0
    
    def __str__(self):
        mediane = self.mediane()
        avg = self.avg()
        return 'Avg:%9.4f Avg/Med:%5.1f Min:%8.4f Max:%10.6f Sum:%11.6f [%5d] %2d%%>4*Avg' % (
            avg, avg/mediane, self.min, self.max, self.sum, self.nr,
            int(100*self.problems()))

def run(service_name, ft, index):
    try:
        f = open(os.path.join('LOGS', service_name), 'r')
    except IOError:
        utilities.warn(service_name + ' unreadable')
        return index
    service_name = service_name.split('.')[0]

    d = {}

    begin_time = None
    start_time = 0
    running = 0
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
            running += duration
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
        
    end_time = float(start_time)

    # output.write('%%time busy: %g, begin_time: %s\n' % (
    #    100 * running/(end_time - begin_time),
    #    time.ctime(begin_time)
    #    ))

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

        for when, dd in zip(('All','5 minutes', 'hour', 'day', 'week', 'month'),d[k]):
            if dd.nr == 0:
                continue
            ft.write("cell_change(0,'0_0','%d','%s','')\n" % (
                index, service_name))
            ft.write("cell_change(0,'0_1','%d','%s','')\n" % (
                index, k))
            ft.write("cell_change(0,'0_2','%d',%g,'')\n" % (
                index, dd.avg()*1000))
            ft.write("cell_change(0,'0_3','%d',%g,'')\n" % (
                index, dd.avg()/dd.mediane()))
            ft.write("cell_change(0,'0_4','%d',%g,'')\n" % (
                index, dd.min*1000))
            ft.write("cell_change(0,'0_5','%d',%g,'')\n" % (
                index, dd.max*1000))
            ft.write("cell_change(0,'0_6','%d',%g,'')\n" % (
                index, dd.sum))
            ft.write("cell_change(0,'0_7','%d',%d,'')\n" % (
                index, dd.nr))
            if launch_thread == '*':
                ft.write("cell_change(0,'0_8','%d','OUI','')\n" % (
                    index,))
            n = dd.problems()
            if n:
                ft.write("cell_change(0,'0_9','%d',%g,'')\n" % (
                    index, n*100))
            ft.write("cell_change(0,'0_a','%d','%s','')\n" % (
                index,when))
            index += 1
    return index


@utilities.add_a_lock
def profiling(server):
    """Display the statistics on the plugin usage, number of call and times."""

    filename = document.table_filename(str(server.the_year),
                                       'Stats', 'profile')
    utilities.mkpath( os.path.sep.join(filename.split(os.path.sep)[0:-1]))
    ft = open(filename, 'w')
    ft.write("""# -*- coding: utf8 -*-
from data import *
new_page('' ,'*', '', '')
column_change (0,'0_0','Service','Text','','','F',0,2)
column_change (0,'0_0','Service','Text','','','F',0,2)
column_change (0,'0_1','Plugin','Text','','','F',0,2)
column_change (0,'0_2','Moy','Note','[0;1000]','','',0,2)
column_comment(0,'0_2','Temps de réponse moyen du service en millisecondes')
column_change (0,'0_3','Moy/Méd','Note','[0;10]','','',0,2)
column_comment(0,'0_3','Moyenne divisée par la médiane')
column_change (0,'0_4','Min','Note','[0;1000]','','',0,2)
column_comment(0,'0_4','Temps de réponse minimal du service en millisecondes')
column_change (0,'0_5','Max','Note', '[0;1000]','','',0,2)
column_comment(0,'0_5','Temps de réponse maximal du service en millisecondes')
column_change (0,'0_6','Total','Note','[0;NaN]','','',0,2)
column_comment(0,'0_6','Temps de réponse cumulé pour le service en secondes')
column_change (0,'0_7','#Appel','Note','[0;NaN]','','',0,2)
column_comment(0,'0_7','Nombre d\\'utilisations du service')
column_change (0,'0_8','Batch','Text','','','',0,1)
column_comment(0,'0_8','Lancé en arrière plan.')
column_change (0,'0_9','Lenteurs','Note','[0;5]','','',0,1)
column_comment(0,'0_9','Pourcentage de requête prenant plus de 4 fois le temps moyen.')
column_change (0,'0_a','Quand','Text','[0;5]','','',0,1)
column_comment(0,'0_a','Statistiques calculées sur la durée indiquée')
table_comment(0, 'Profiling des services')
table_attr('default_nr_columns', 0, 11)
""")

    index = run(os.path.join('TOMUSS',
                             str(server.the_year) + '.times'
                             ), ft, 0)
    import configuration

    for url, port, year, semester, host in configuration.suivi.urls.values():
        server.the_file.write('\n')
        index = run(os.path.join('SUIVI%d' % port,
                                 str(server.the_year) + '.times'
                                 ), ft, index)

    ft.close()

    t = document.table(server.the_year, 'Stats', 'profile', create=False)
    if t:
        t.unload()

    server.the_file.write('<script>window.location="%s/=%s/%d/Stats/profile";</script>' % (
        configuration.server_url, server.ticket.ticket, server.the_year))
    server.the_file.close()

plugin.Plugin('profiling', '/profiling/{Y}',
              function=profiling,
              root = True,
              launch_thread = True,
              keep_open = True,
              link=plugin.Link(text='Profiling des plugins',
                               help='''Calcule des performances des différents
                               plugins TOMUSS''',
                               html_class="verysafe",
                               where='debug',
                               url="javascript:go_year_after('profiling')"
                               ),
              )

