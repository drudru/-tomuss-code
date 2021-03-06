#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2008-2014 Thierry EXCOFFIER, Universite Claude Bernard
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
import collections
import gc
import html
import math
import sys
from .. import objgraph
from .. import plugin
from .. import utilities
from .. import configuration
from .. import document

def gc_top(server):
    "Display a clickable list of Python classes and their number of instance."
    if configuration.regtest:
        server.the_file.write(server._("MSG_evaluate"))
        return
    
    server.the_file.write('<META NAME="ROBOTS" CONTENT="NOINDEX, NOFOLLOW">\n')
    server.the_file.write('<pre>')
    server.the_file.write('gc.garbage=%s\n' % gc.garbage)
    # leaking = objgraph.get_leaking_objects()
    # server.the_file.write('leaking=%s\n' % len(leaking))
    server.the_file.write('\n')
    gc.collect()
    for name, nr in objgraph.most_common_types(limit=100):
        server.the_file.write('%6d <a href="%s/=%s/type/%s">%s</a>\n' % (
            nr, utilities.StaticFile._url_, server.ticket.ticket, name, name))
    server.the_file.write('</pre>')
    # server.the_file.write('Leak :<pre>')
    # t = ['%s\n' % html.escape(repr(o)[:80])
    #      for o in leaking
    #      ]
    # t.sort()
    # server.the_file.write(''.join(t) + '</pre>')

def check(path, o):
    s = []
    first = path[0]
    rest = path[1:]
    for child in gc.get_referents(o):
        if type(child).__name__ == first:
            if len(path) == 1:
                s.append(child)
            else:
                s += check(rest, child)
    return s

last = None
    
def gc_type(server):
    """Display a clickable list of the instance of the classes specified"""
    global last
    if configuration.regtest:
        server.the_file.write(server._("MSG_evaluate"))
        return
    gc.collect()
    objects = gc.get_objects()
    server.the_file.write('<h1> ? → ' + '→'.join(server.the_path) + '</h1>')
    server.the_file.write('<pre>')
    what = collections.defaultdict(dict)
    for i in objects:
        for j in check(server.the_path, i):
            what[type(i).__name__][id(j)] = j
    s = sorted(what, key=lambda x: len(what[x]))
    s.reverse()
    for k in s:
        server.the_file.write('%s(<a href="%s/=%s/type/%s">%s</a>)\n' % (
                k,
                utilities.StaticFile._url_,
                server.ticket.ticket,
                k + '/' + '/'.join(server.the_path),
                len(what[k])))
        if last:
            for i in what[k]:
                if i in last:
                    continue
                server.the_file.write('        <b><a href="%s/=%s/object/%s">%s</a></b>\n' % (
                        utilities.StaticFile._url_,
                        server.ticket.ticket,
                        i,
                        html.escape(repr(what[k][i])[:100])))

        for n, i in enumerate(what[k]):
            server.the_file.write('        <a href="%s/=%s/object/%s">%s</a>\n' % (
                utilities.StaticFile._url_,
                server.ticket.ticket,
                i,
                html.escape(repr(what[k][i])[:100])))
            if n == 50:
                break
        server.the_file.write('\n')
                    
    server.the_file.write('</pre>')
    last = set(id(i) for i in objects)

def gc_object(server):
    """Display the graph of instances using or used by the object"""
    if configuration.regtest:
        server.the_file.write(server._("MSG_evaluate"))
        return
    i = objgraph.at(int(server.the_path[0], 0))
    gc.collect()
    filename = os.path.join('TMP', 'objects.png')
    objgraph.show_backrefs(i, max_depth=5, too_many=10, filename=filename)
    server.the_file.write(utilities.read_file(filename, "bytes"))

plugin.Plugin('gctop'   , '/gc'        , group='roots', function=gc_top,
              launch_thread=True,
              link=plugin.Link(where='debug', html_class='verysafe')
              )
plugin.Plugin('gctype'  , '/type/{*}'  , group='roots',
              function=gc_type,
              launch_thread=True,
              )
plugin.Plugin('gcobject', '/object/{*}', group='roots', function=gc_object,
              launch_thread=True,
              mimetype = 'image/png')

def histogram(values):
    if len(values) == 0:
        return ''
    bin_size = 300 # 5 minute
    value_max = max(values)
    nr_bins = value_max // bin_size
    counters = [0] * (nr_bins+1)
    for v in values:
        counters[v//bin_size] += 1

    while counters and counters[-1] == 0:
        del counters[-1]

    if len(counters) == 0:
        return ''

    counter_max = math.log(max(counters)+1)

    s = '<table width="100%" style="table-layout:fixed"><colgroup>'
    s += '<col with="*">' * len(counters) + '</colgroup>'
    s += '<tr style="vertical-align:bottom">'
    for v in counters:
        s += '<td><img src="../ok.png" style="width:100%%" height="%dpx">' % int(50*math.log(v+1)/counter_max)
    s += '</tr><tr>'
    i = 0
    for v in counters:
        s += '<td style="text-align:center">%d<br><small><small>%s' % (int(i), v)
        i += bin_size / 60.
    s += '</tr></table>'
    return s

def caches(server):
    """Display the caches statistics"""
    s = ['<title>' + server._("MSG_cache_title")
         + '</title><table border="1"><tr><th>' + server._("TH_cache_name")
         + '<th>' + server._("TH_cache_what")
         + '<th>' + server._("TH_cache_type")
         + '<th>' + server._("TH_cache_age")
         + '<th>' + server._("TH_cache_maxage")
         + '<th>' + server._("TH_cache_content")]
    now = int(time.time())
    for cache in utilities.caches:
        if  cache.the_type == 'add_a_cache0':
            nr_items = 1
            size = server._("MSG_cache_size") % sys.getsizeof(cache.cache[0])
            since = now - int(cache.cache[1])
        else:
            nr_items = len(cache.cache)
            size = ''
            sinces = list([now - int(c[1]) for c in cache.cache.values()])
            since = histogram(sinces)
        if cache.__doc__ is None:
            doc = '???'
        else:
            doc = cache.__doc__
        
        s.append('<tr><td>%s<br><span style="font-size:60%%">%s</span><td>%s<td>%s<td width="50%%">%s<td>%s<td>%s items %s' % (
            cache.fct.__name__.replace('_',' '),
            cache.fct.__module__.replace('.', ' '),
            html.escape(doc),
            cache.the_type.replace('_',' '),
            since, cache.timeout, nr_items, size))
    s.append('</table>')
    server.the_file.write('\n'.join(s))

plugin.Plugin('caches'   , '/caches'   , group='roots', function=caches,
              link=plugin.Link(where='debug', html_class='verysafe')
              )

def locks(server):
    """Displays all the lock states"""
    server.the_file.write('<title>' + server._("MSG_locks_title")
                          + '</title><pre>'+ utilities.lock_state() + '</pre>')
    for t in document.tables_values():
        if t.the_lock.locked():
            server.the_file.write('<br>LOCKED: ' + str(t) + '<br>')

plugin.Plugin('locks'   , '/locks'   , group='roots', function=locks,
              link=plugin.Link(where='debug', html_class='verysafe')
              )

def threads(server):
    """Displays the running thread"""
    server.the_file.write('<title>' + server._("MSG_threads_title")
                          + '</title><pre>'
                          + html.escape(utilities.all_the_stacks())
                          + '</pre>')

plugin.Plugin('threads'   , '/threads'   , group='roots', function=threads,
              link=plugin.Link(where='debug', html_class='verysafe')
              )

def gcbig(server):
    "Display big Python objects"
    if configuration.regtest:
        server.the_file.write(server._("MSG_evaluate"))
        return
    
    server.the_file.write('<META NAME="ROBOTS" CONTENT="NOINDEX, NOFOLLOW">\n')
    server.the_file.write('<pre>')
    gc.collect()
    sizes = [[] for dummy in range(32)]
    log2 = math.log(2)
    for o in gc.get_objects():
        try:
            sizes[ int(math.log(sys.getsizeof(o)+1)/log2) ].append(o)
        except:
            pass
    total = 0
    for n, objects in enumerate(sizes):
        size = sum(sys.getsizeof(o) for o in objects)
        total += size
        server.the_file.write('%d-%d: %d objects (%d bytes)\n' % (
                2**n, 2**(n+1)-1, len(objects), size))
        if len(objects) < 10:
            for o in objects:
                server.the_file.write('   <a href="object/%d">%s</a>\n' % (
                        id(o),
                        html.escape(repr(o)[:200])))
        
        
    server.the_file.write('</pre>')
    server.the_file.write('Total: %d bytes\n' % total)
    


plugin.Plugin('gcbig'   , '/gcbig'   , group='roots', function=gcbig,
              launch_thread=True,
              link=plugin.Link(where='debug', html_class='verysafe')
              )


def requests(server):
    """Displays the requests queue"""

    server.the_file.write(
        '<head><title>LOST REQUESTS</title></head>'
        '<table>'
        '<tr><th>Request<th>Page<th>Action<th>Path<th>Current Cell Value</tr>')
    for request in sorted(document.request_list,
                          key = lambda x: (x[2], x[1])):
        request = list(request[1:-1])
        if request[2] == 'cell_change':
            column = request[1].table.columns.from_id(request[3][0])
            if column:
                line_id = request[3][1]
                line = request[1].table.lines[line_id]
                v = line[column.data_col].value
                t = html.escape(
                    line[0].value + ' ' + line[1].value + ' ' + line[2].value
                    + ' ' + column.title + '='
                    + str(v)
                    )
                
            else:
                v = '???' + request[3][0] + '???'
                t = '???????'
            if str(v).rstrip('.0') != str(request[3][2]).rstrip('.0'):
                t = '<span style="background:#F88">' + t + '(!=' + html.escape(request[3][2]) + ')'
        else:
            t = ''
        request[0] = '%s(%s)' % (request[0], request[1].request)
        server.the_file.write('<tr>'
                              + ''.join("<td>" + html.escape(str(v))
                                        for v in request)
                              + '<td>' + t + '</tr>')
    server.the_file.write('</table>')

plugin.Plugin('requests'   , '/requests'   , group='roots', function=requests,
              link=plugin.Link(where='debug', html_class='verysafe')
              )

def memory_size_checker(server):
    """Display thread list each time the memory footprint change"""
    import resource
    mem = resource.getrusage(resource.RUSAGE_SELF)[2]
    server.the_file.write('<pre>')
    i = 0
    while True:
        i += 1
        if i % 100 == 0:
            # Keep browser connection open
            server.the_file.write(' ')
            server.the_file.flush()
        time.sleep(0.01)
        current = resource.getrusage(resource.RUSAGE_SELF)[2]
        if current == mem:
            continue
        try:
            server.the_file.write(
                '\n\n%d → %d\n\n' % (mem, current)
                + '\n'.join(t.stack()
                          for t in utilities.thread_list
                      )
                + '\n'*2 + '<hr>\n'
            )
            server.the_file.flush()
        except:
            break
        mem = current

plugin.Plugin('memory_size_checker', '/memory_size_checker',
              group='roots', function=memory_size_checker, launch_thread=True,
              link=plugin.Link(where='debug', html_class='verysafe'),
              unsafe=False
              )

def atomic_checker(server):
    """Compute the size of atomic Python type : integer, string"""
    atomic_types = (str, int, int, float)
    gc.collect()
    objs = gc.get_objects()
    atomics = set()
    for o in objs:
        # Do not iterate over files...
        if isinstance(o, (dict, list, tuple, set)):
            for a in o:
                if isinstance(a, atomic_types):
                    atomics.add(a)
        if isinstance(o, dict):
            for a in o.values():
                if isinstance(a, atomic_types):
                    atomics.add(a)
    t = collections.defaultdict(lambda: [0,0])
    for a in atomics:
        stat = t[type(a)]
        stat[0] += 1
        stat[1] += sys.getsizeof(a)

    for a_type, stat in t.items():
        server.the_file.write("%d %s %d bytes<br>\n" %(stat[0],
                                                       html.escape(str(a_type)),
                                                       stat[1]))

plugin.Plugin('atomic_checker', '/atomic_checker',
              group='roots', function=atomic_checker, launch_thread=True,
              link=plugin.Link(where='debug', html_class='verysafe')
              )

