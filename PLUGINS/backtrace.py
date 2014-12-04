#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2012 Thierry EXCOFFIER, Universite Claude Bernard
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

import cgi
import datetime
import os
import collections
from .. import plugin
from .. import utilities
from .. import configuration

tf = "%Y%m%d"

def date_range(from_date, to_date):
    """Generator of dates.
    from_date and to_date are in YYYYMMDD format,
    They are include in the range.
    BEWARE: returns YYYY-MM-DD
    """
    day = datetime.datetime(int(from_date[:4]), int(from_date[4:6]),
                            int(from_date[6:]))
    last = datetime.datetime(int(to_date[:4]), int(to_date[4:6]),
                             int(to_date[6:]))
    one_day = datetime.timedelta(days=1)
    while True:
        yield (day.strftime("%Y-%m-%d"), day.timetuple())
        if day == last:
            return
        day += one_day

def date_by_reversed_weeks(from_date, to_date):
    day = datetime.datetime(int(from_date[:4]), int(from_date[4:6]),
                            int(from_date[6:]))
    last = datetime.datetime(int(to_date[:4]), int(to_date[4:6]),
                             int(to_date[6:]))
    one_day = datetime.timedelta(days=1)
    two_week = datetime.timedelta(days=14)
    last -= datetime.timedelta(days = last.isoweekday()) # Sunday
    while True:
        for dummy_i in range(7):
            last += one_day
            yield (last.strftime("%Y-%m-%d"), last.timetuple())
            if last == day:
                return
        last -= two_week

def backtrace_list(server, from_date, to_date, what):
    for dirname, dummy_time in date_range(from_date, to_date):
        full_dirname = os.path.join("LOGS", "BACKTRACES", dirname)
        if not os.path.isdir(full_dirname):
            continue
        files = sorted(os.listdir(full_dirname), reverse=True)
        server.the_file.write('<h2>' + dirname + '</h2>')
        t = []
        d = collections.defaultdict(int)
        for filename in files:
            w, content = classifier(filename=os.path.join(full_dirname,
                                                          filename))
            if what == 'any' or w == what:
                d[filename[:2]] += 1
                t.append(
                    '<a target="backtrace" onclick="dofocus(event)" class="%s" href="%s">%s %s</a>' %
                         (
                        w,
                        dirname + '/' + filename,
                        filename.replace(".html", ""),
                        cgi.escape(content)))
        maxi = float(max(d.values()))
        def cell(hour):
            v = d['%02d' % hour]
            if v:
                return '<div style="height:%.2fem">%d</div>' % (v/maxi, v)
            else:
                return '&nbsp;'
            
        server.the_file.write('<table class="hour"><tr>'
                              + ''.join('<th>%02d' % i for i in range(24))
                              + '</tr><tr>'
                              + ''.join('<td>%s' % cell(i) for i in range(24))
                              + '</tr></table><p>')
        server.the_file.write('<br>\n'.join(t))

def classifier(filename=None, subject=None):
    if filename:
        f = open(filename, "r")
        subject = f.readline()
        f.close()
    if './' not in subject:
        return 'important', subject
    if subject.split("./")[0][-1] == '*':
        # Closed Pipe
        return 'informative', subject
    if 'Backtrace' in subject:
        return 'important', subject
    if 'Plugin login_list' in subject:
        return 'warning', subject
    if ' Plugin ' in subject:
        return 'important', subject
    if 'ALERT' in subject:
        return 'important', subject
    if 'BUG TOMUSS' in subject:
        return 'important', subject
    return 'warning', subject
    
def backtrace_day(server, from_date, to_date, dummy_what):
    first_time = True
    a = ' <a target="list" class="%s" onfocus="dofocus(event)" href="list/%s/%s/%s">%d</a><br>'
    days = eval(server._("MSG_days"))
    days = days[1:] + days[0:1]
    server.the_file.write('<table class="day">'
                          + "<tr>"
                          + ''.join('<th>%s' % d for d in days) 
                          + '</tr>')

    for dirname, time_tuple in date_by_reversed_weeks(from_date, to_date):
        weekday = time_tuple[6]
        if weekday <= 0 or first_time:
            t = "<tr>"
            if first_time:
                t += time_tuple[6] * "<td>&nbsp;"
            first_time = False
        t += "<td>"
        full_dirname = os.path.join("LOGS", "BACKTRACES", dirname)
        if os.path.isdir(full_dirname):
            files = os.listdir(full_dirname)
            d = collections.defaultdict(int)
            for filename in files:
                d[classifier(filename=os.path.join(full_dirname,
                                                   filename))[0]] += 1
            dn = dirname.replace("-", "")
            if len(d):
                any = sum(d.values())
                t += a % ('any', 'any', dn, dn, any)
            else:
                t += '&nbsp;<br>'
            for c in ("important", "warning", "informative"):
                if d[c]:
                    t += a % (c, c, dn, dn, d[c])
                else:
                    t += '&nbsp;<br>'
        if time_tuple[6] == 6:
            t += "</tr>"
        server.the_file.write(t)
        t = ''
    if time_tuple[6] != 6:
        t += "</tr>"
        server.the_file.write(t)

    server.the_file.write("</table>")

def backtrace_home(server):
    dates = sorted(os.listdir(os.path.join("LOGS", "BACKTRACES")))
    traces = sorted(os.listdir(os.path.join("LOGS", "BACKTRACES", dates[-1])))
    traces.insert(0,"NONE")
    from_date = dates[0].replace("-", "")
    to_date = dates[-1].replace("-", "")

    server.the_file.write("""<table width="100%%" height="100%%">
<tr>
<td style="width:15em"><iframe width="100%%" height="100%%" src="day/any/%s/%s"></iframe>
<td><iframe width="100%%" name="list" height="100%%" src="list/any/%s/%s"></iframe>
<td><iframe width="100%%" name="backtrace" height="100%%" src="%s/%s"></iframe>
</tr>
</table>
""" % (from_date, to_date, to_date, to_date, dates[-1], traces[-1]))
    
def backtrace(server):
    """
    Display backtraces.
    Arguments are: {list|day}/{any|important|warning|informative}/fromYYYYMMDD/until
    """
    server.the_file.write('''
<head>
<title>BackTraces</title>
<base href="%s/=%s/backtrace/">
<style>
BODY { white-space: nowrap;
       font-family: sans-serif;
       text-decoration: none ;
       margin: 0px ;
     }
TABLE { border-spacing: 0 }
.important { color: #F00 }
.warning { color: #A40 }
.informative { color: #000 }
.any { color: #000; font-size: 80%% ; font-weight: bold }
A { padding: 0px ; }
TABLE.day th { font-size: 70%%; width: 3em }
TABLE.day td, TABLE.day th { border: 1px solid black }
TABLE.day td { text-align: right }
TABLE.hour td, TABLE.hour th { border: 1px solid black;
                               text-align: right;
                               vertical-align: top;
                               padding: 0px ;
                             }
TABLE.hour TD DIV { background: #F88; }
</style>
<script>
var oldfocus ;
function dofocus(event)
{
  var e = event || window.event ;
  var t = e.target || e.srcElement ;
  while ( t.tagName != 'A' )
     t = t.parentNode ;
  if ( oldfocus )
     oldfocus.style.background = "" ;
  t.style.background = "#FF0" ;
  oldfocus = t ;
}
</script>
</head>
''' % (configuration.server_url, server.ticket.ticket))
    if len(server.the_path) == 2:
        dirname = server.the_path[0].replace('.','').replace('/','')
        filename = server.the_path[1].replace('.','').replace('/','')
        f = utilities.read_file(os.path.join("LOGS", "BACKTRACES",
                                             dirname, filename))
        server.the_file.write('<h2>' + server.the_path[0] + ' '
                              + server.the_path[1].replace(".html", "")
                              + '</h2>')
        server.the_file.write(f)
        return
    if len(server.the_path) == 0:
        backtrace_home(server)
        return
    precision, what, from_date, to_date = server.the_path
    if precision == 'list':
        backtrace_list(server, from_date, to_date, what)
    elif precision == 'day':
        backtrace_day(server, from_date, to_date, what)
        
    

plugin.Plugin('backtrace', '/backtrace/{*}', group='roots',
              function=backtrace, launch_thread=True,
              link=plugin.Link(
                  where='debug', html_class='verysafe', url='/backtrace',
                  )
              )

