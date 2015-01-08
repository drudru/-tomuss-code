#!/usr/bin/python
# -*- coding: latin-1 -*-

"""
Compute graphics for access statistics
"""

import tomuss_init
import os
import time
import glob
import math
import collections
from .. import utilities
from .. import configuration

_ = utilities.__

def plot(filename, commands):
    print 'Plotting', filename
    f = os.popen('gnuplot', 'w')
    f.write('set encoding iso_8859_1\n')
    f.write('set terminal png large font arial tiny\n')
    f.write("set output 'TMP/%s'\n" % filename)
    f.write(commands.encode('latin-1'))
    f.close()

def parse_date(date):
    year = int(date[0:4])
    if year < 2000:
        year += 1000 # An UCBL plugin remove 1000 year to highlight change
    t = int(time.mktime((
        year,
        int(date[4:6]),
        int(date[6:8]),
        int(date[8:10]),
        int(date[10:12]),
        int(date[12:14]),
        0,0,-1 # Guess DST
        )))
    return t

class Stats(object):
    def __init__(self):
        self.days = [0] * 7
        self.hours = [0] * 24
        self.dates = {}
        self.first = 1e50
        self.last = 0
        self.duration = 0

    def add_YYYYMMDDHHMMSS(self, date, seconds=None):
        if date == '':
            return
        if seconds:
            t = seconds
        else:
            t = parse_date(date)
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

    def plot_hours(self, name, visits='cell_change'):
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
             set xlabel '%s'
             set xtics 1
             set grid ytics
             plot [-0.5:23.5] 'xxx' with boxes fs solid 0.3 title "%s", %g with lines title "%s"
             """ % (
                _("LABEL_hours_of_the_day"),
                _("LABEL_cell_change_per_hours_of_the_day".replace(
                        'cell_change', visits)),
                a,
                _("B_Moy"),
                ))

    def plot_days(self, name, visits='cell_change'):
        d = self.duration / (7*86400.)
        if d < 1:
            d = 1
        f = open('xxx', 'w')
        f.write('\n'.join(['%d %g' % (v[0], v[1]/d)
                           for v in enumerate(self.days)]))
        f.close()
        a = sum(self.days) / float(len(self.days)) / d
        day_names = eval(_("MSG_days_full"))
        plot(name,
             """
             set grid ytics
             set xtics (%s)
             plot [-0.5:6.5] [0:] 'xxx' with boxes fs solid 0.3 title "%s", %g with lines title "%s"
             """ % (
                ','.join('"%s" %d' % (day_names[(i+1)%7], i)
                         for i in range(7)),
                _("LABEL_cell_change_per_day_of_the_week".replace(
                        'cell_change', visits)),
                a,
                _("B_Moy"),
                ))

    def plot_weeks(self, name, visits='cell_change'):
        a = self.date_number()
        if a:
            av = sum([v[1] for v in a]) / float(len(a))
        else:
            av = 0
        start_year, dummy_start_month = time.localtime(a[0][0])[0:2]

        year = start_year
        years = []
        while a:
            f = open('xxx.%d' % year, 'w')
            while a:
                local = time.localtime(a[0][0])
                if local[0] == year:
                    f.write("%d %d\n" % (local[7], a.pop(0)[1]))
                else:
                    break
            f.close()
            years.append("'xxx.%d' with lines lw 2 title \"%d\""
                         % (year, year))
            year += 1
                        
        
        s = []
        for month in range(1,13):
            tup = (2000, month, 1, 0, 0, 0, 0, 0, 0)
            i = time.mktime( tup )
            tup = time.localtime(i)
            label = time.strftime("%b", tup)
            s.append('"%s" %d' % (label, tup[7]))

        # years.reverse()
        plot(name, 'set xtics (%s)\n' % ','.join(s)
             + """
             set grid ytics
             set grid xtics
             set title '%s'
             plot %s, %g with lines title \"%s\"
             """ % (
                _("LABEL_cell_change_per_week".replace(
                        'cell_change', visits)),
                ','.join(years), av, _("B_Moy")))

def analyse_cellchange():
    d = configuration.db + '/Y*/S[!T]*/*.py'

    print 'Analyse:', d

    f = os.popen("grep -h '^cell_change' 2>/dev/null " + d, "r")
    stat = Stats()
    for line in f:
        if line == '':
            break
        if line.split('(')[1][0] == '0': # Do not count auto-filled cells
            continue
        t = line.replace("'",'"').split('"')[-2]
        stat.add_YYYYMMDDHHMMSS(t)
    f.close()

    stat.plot_weeks('xxx.change.weeks.png')
    stat.plot_days('xxx.change.days.png')
    stat.plot_hours('xxx.change.hours.png')

analyse_cellchange()

# Compute number of different students per day

power = 1.5

stats = Stats()
histogram_diff = [0] * 1000
student_diff = collections.defaultdict(list)
for filenam in glob.glob(os.path.join("LOGS", "SUIVI*/*.connections")):
    try:
        ff = open(filenam, "r")
    except IOError:
        continue
    last = ''
    histo = [''] * 10 # Not recount the same student before 10 other students
    last_access = {}
    for lin in ff:
        lin = lin.split(' ', 1)
        if len(lin) != 2:
            continue
        tt, login = lin
        if len(tt) != 14:
            print tt
            continue
        secondes = parse_date(tt)
        if configuration.is_a_student(login):
            if login in last_access:
                diff = secondes - last_access[login]
                student_diff[login].append(diff)
                if diff >= 2:
                    histogram_diff[int(math.log(diff)/math.log(power))] += 1
                else:
                    histogram_diff[0] += 1
            last_access[login] = secondes
        if login in histo:
            histo.remove(login)
            histo.append(login)
            continue
        histo.pop(0)
        histo.append(login)
        stats.add_YYYYMMDDHHMMSS(tt, seconds=secondes)
    ff.close()

stats.plot_hours('xxx.suivi.hours.png', 'visits')
stats.plot_days('xxx.suivi.days.png', 'visits')
stats.plot_weeks('xxx.suivi.weeks.png', 'visits')

while histogram_diff[-1] == 0:
    histogram_diff.pop()

def seconds_to_human(s):
    if s < 60:
        return "%ds" % s
    s /= 60.
    if s < 60:
        return "%dm" % s
    s /= 60.
    if s < 24:
        return "%dh" % s
    s /= 24.
    if s < 30:
        return "%dd" % s
    return "%dM" % (s/30)

ff = open("xxx.histogram_diff", "w")
for ii, nb in enumerate(histogram_diff):
    ff.write("%d %d\n" % (ii, nb))
ff.close()


tt =     [1, 2, 3, 5, 8, 15, 30]
for ii in [1, 2, 3, 5, 8, 15, 30]:
    tt.append( ii*60 )
for ii in [1, 2, 3, 5, 10]:
    tt.append( ii*60*60 )
for ii in [1, 2, 3, 5, 10, 15]:
    tt.append( ii*60*60*24 )
for ii in [1, 2, 3, 5, 10, 30]:
    tt.append( ii*60*60*24*30 )

tics = ['"%s" %f' % (seconds_to_human(ii), math.log(ii)/math.log(power))
        for ii in tt
        if ii < power**(len(histogram_diff)-1)
        ]

def plot_histogram_diff(filename, x_title, y_title, fig_title):
    plot('%s.png' % filename, """
    set xlabel "%s"
    set ylabel "%s"
    set xtics (%s)
    plot '%s' with boxes fs solid 0.3 title "%s"
    """ % (x_title, y_title, ','.join(tics), filename, fig_title))

plot_histogram_diff('xxx.histogram_diff',
                    _("LABEL_time_between_access"),
                    _("LABEL_number_of_access"),
                    _("LABEL_time_between_user_access"))

histogram_diff = [0] * 1000
for diffs in student_diff.values():
    diffs.sort()
    diff = diffs[len(diffs)//2]
    if diff == 0:
        histogram_diff[0] += 1
    else:
        histogram_diff[int(math.log(diff)/math.log(power))] += 1
while histogram_diff[-1] == 0:
    histogram_diff.pop()

ff = open("xxx.student_diff", "w")
for ii, nb in enumerate(histogram_diff):
    ff.write("%d %d\n" % (ii, nb))
ff.close()

plot_histogram_diff('xxx.student_diff',
                    _("LABEL_median_time_between_access"),
                    _("LABEL_number_of_users"),
                    _("LABEL_number_of_users_per_median_time"))

os.system('SCRIPTS/page_load_time')
