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
import time
import os
import collections
import plugin
import utilities
import configuration

tf = "%Y%m%d"

def date_range(from_date, to_date):
    """Generator of dates.
    from_date and to_date are in YYYYMMDD format,
    They are include in the range.
    BEWARE: returns YYYY-MM-DD
    """
    time_tuple = list(time.strptime(from_date, tf))
    while True:
        yield (from_date[:4] + '-' + from_date[4:6] + '-' + from_date[6:],
               time_tuple)
        if from_date == to_date:
            return
        time_tuple[2] += 1
        from_date = time.strftime(tf, time_tuple)


def backtrace_list(server, from_date, to_date, what):
    for dirname, dummy_time in date_range(from_date, to_date):
        full_dirname = os.path.join("LOGS", "BACKTRACES", dirname)
        if not os.path.isdir(full_dirname):
            continue
        files = sorted(os.listdir(full_dirname), reverse=True)
        server.the_file.write('<h2>' + dirname + '</h2>')
        for filename in files:
            w, content = classifier(filename=os.path.join(full_dirname,
                                                          filename))
            if what == 'any' or w == what:
                server.the_file.write('<a target="backtrace" onfocus="dofocus(event)" href="%s">%s <small><small>%s</small></small></a><br>' %
                                      (dirname + '/' + filename,
                                       filename.replace(".html", ""),
                                       cgi.escape(content)))

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
    return 'warning', subject
    
def backtrace_day(server, from_date, to_date, dummy_what):
    s = []
    weekday = -1
    for dirname, time_tuple in date_range(from_date, to_date):
        if weekday <= 0:
            t = "<tr>"
        if weekday == -1:
            t += time_tuple[6] * "<td>&nbsp;"
            weekday = time_tuple[6]
        t += "<td>"
        full_dirname = os.path.join("LOGS", "BACKTRACES", dirname)
        if os.path.isdir(full_dirname):
            files = os.listdir(full_dirname)
            d = collections.defaultdict(int)
            for filename in files:
                d[classifier(filename=os.path.join(full_dirname,
                                                   filename))[0]] += 1
            dn = dirname.replace("-", "")
            for c in d.keys():
                t += (' <a target="list" class="%s" onfocus="dofocus(event)" href="list/%s/%s/%s">%d</a>' % (
                    c, c, dn, dn, d[c]))
        if time_tuple[6] == 6:
            t += "</tr>"
            s.append(t)
    if time_tuple[6] != 6:
        t += "</tr>"
        s.append(t)
        

    s.reverse()
    server.the_file.write('<table border>' + ''.join(s) + "</table>")

def backtrace_home(server):
    dates = sorted(os.listdir(os.path.join("LOGS", "BACKTRACES")))
    traces = sorted(os.listdir(os.path.join("LOGS", "BACKTRACES", dates[-1])))
    traces.insert(0,"NONE")
    from_date = dates[0].replace("-", "")
    to_date = dates[-1].replace("-", "")

    server.the_file.write("""<table width="100%%" height="100%%">
<tr>
<td width="10%%"><iframe width="100%%" height="100%%" src="day/any/%s/%s"></iframe>
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
<base href="%s/=%s/backtrace/">
<style>
BODY { white-space: nowrap; font-family: sans-serif }
.important { color: red }
.warning { color: orange }
</style>
<script>
var oldfocus ;
function dofocus(event)
{
  var e = event || window.event ;
  e.target.style.background = "#FF0" ;
  if ( oldfocus )
     oldfocus.style.background = "" ;
  oldfocus = e.target ;
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
              function=backtrace,
              link=plugin.Link(
                  where='debug', html_class='verysafe', url='/backtrace',
                  )
              )

