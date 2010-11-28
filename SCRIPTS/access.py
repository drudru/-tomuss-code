#!/usr/bin/python
# -*- coding: latin1 -*-

"""
Compute graphics for access statistics
"""

import os
import time
import sys

sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), '..'))
import configuration
configuration.terminate()

def plot(filename, commands):
    print 'Plotting', filename
    f = os.popen('gnuplot', 'w')
    f.write('set terminal png large font arial tiny\n')
    f.write("set output 'TMP/%s'\n" % filename)
    f.write(commands)
    f.close()

class Stats:
    def __init__(self):
        self.days = [0] * 7
        self.hours = [0] * 24
        self.dates = {}
        self.first = 1e50
        self.last = 0
        self.duration = 0

    def add_YYYYMMDDHHMMSS(self, date):
        t = int(time.mktime((
            int(date[0:4]),
            int(date[4:6]),
            int(date[6:8]),
            int(date[8:10]),
            0,0,0,0,-1 # Guess DST
            )))
        if t < self.first:
            self.first = t
        if t > self.last:
            self.last = t
        self.duration = self.last - self.first

        self.hours[ int(date[8:10]) ] += 1
        self.days[ time.localtime(t)[6] ] += 1

        t /= 86400 * 7
        t *= 86400 * 7

        if t in self.dates:
            self.dates[t] += 1
        else:
            self.dates[t] = 1


    def date_number(self):
        a = self.dates.items()
        a.sort()
        return a

    def plot_hours(self, name):
        d = self.duration / 86400.
        if d < 1:
            d = 1
        f = open("xxx", 'w')
        f.write('\n'.join(['%d %g' % (v[0], v[1]/d)
                           for v in enumerate(self.hours)]))
        f.close()
        a = sum(self.hours) / float(len(self.hours)) / d
        plot(name,
             """
             set xlabel 'Heures de la journée'
             set xtics 1
             set grid ytics
             plot [-0.5:23.5] 'xxx' with boxes fs solid 0.3 title "Par heure de la journée", %g with lines title "Moyenne"
             """ % a)

    def plot_days(self, name):
        d = self.duration / (7*86400.)
        if d < 1:
            d = 1
        f = open('xxx', 'w')
        f.write('\n'.join(['%d %g' % (v[0], v[1]/d)
                           for v in enumerate(self.days)]))
        f.close()
        a = sum(self.days) / float(len(self.days)) / d
        plot(name,
             """
             set grid ytics
             set xtics ("Lundi" 0, "Mardi" 1, "Mercredi" 2, "Jeudi" 3, "Vendredi" 4, "Samedi" 5, "Dimanche" 6)
             plot [-0.5:6.5] [0:] 'xxx' with boxes fs solid 0.3 title "Par jour de la semaine", %g with lines title "Moyenne"
             """ % a)

    def plot_weeks(self, name):
        a = self.date_number()
        s = []
        for v in a:
            s.append("%d %d" % v)
        s = '\n'.join(s)
        f = open('xxx', 'w')
        f.write(s)
        f.close()
        av = sum([v[1] for v in a]) / float(len(a))
        
        s = []
        start_year, start_month = time.localtime(a[0][0])[0:2]

        while True:
            tup = (start_year, start_month, 1, 0, 0, 0, 0, 0, 0)
            i = time.mktime( tup )
            if i > a[-1][0]:
                break
            tup = time.localtime(i)
            label = time.strftime("%m/%y", tup)
            start_month += 1
            if start_month == 13:
                start_month = 1
                start_year += 1        
            s.append('"%s" %d' % (label, i))

        plot(name, 'set xtics (%s)\n' % ','.join(s)
             + """
             set grid ytics
             set grid xtics
             set xtics rotate 
             plot 'xxx' with boxes fs solid 0.3 title \"Par semaine\", %g with lines title \"Moyenne\"
             """ % av)


d = configuration.db + '/Y*/S*/*.py'

print 'Analyse:', d

f = os.popen("grep -h '^cell_change' 2>/dev/null " + d, "r")
stats = Stats()
for line in f:
    if line == '':
        break
    if line.split('(')[1][0] == '0': # Do not count auto-filled cells
        continue
    tt = line.replace("'",'"').split('"')[-2]
    stats.add_YYYYMMDDHHMMSS(tt)
f.close()
    
stats.plot_weeks('xxx.change.weeks.png')
stats.plot_days('xxx.change.days.png')
stats.plot_hours('xxx.change.hours.png')

# Compute number of different students per day

stats = Stats()
import glob
for filename in glob.glob(os.path.join("LOGS", "SUIVI*/*.connections")):
    try:
        f = open(filename, "r")
    except IOError:
        continue
    last = ''
    histo = [''] * 10 # Not recount the same student before 10 other students
    for line in f:
        line = line.split(' ', 1)
        if len(line) != 2:
            continue
        if line[1] in histo:
            histo.remove(line[1])
            histo.append(line[1])
            continue
        if len(line[0]) != 14:
            print line[0]
            continue
        histo.pop(0)
        histo.append(line[1])
        stats.add_YYYYMMDDHHMMSS(line[0])
    f.close()

stats.plot_hours('xxx.suivi.hours.png')
stats.plot_days('xxx.suivi.days.png')
stats.plot_weeks('xxx.suivi.weeks.png')

os.system('SCRIPTS/page_load_time')       
