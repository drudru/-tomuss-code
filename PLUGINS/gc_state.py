#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
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
import collections
import gc
import cgi
import objgraph
import plugin
import utilities
import configuration

def gc_top(server):
    "Display a clickable list of Python classes and their number of instance."
    if configuration.regtest:
        server.the_file.write(server._("MSG_evaluate"))
        return
    
    server.the_file.write('<META NAME="ROBOTS" CONTENT="NOINDEX, NOFOLLOW">\n')
    server.the_file.write('gc.garbage=%s\n' % gc.garbage)
    server.the_file.write('<pre>')
    gc.collect()
    for name, nr in objgraph.types_sorted():
        server.the_file.write('%6d <a href="%s/=%s/type/%s">%s</a>\n' % (
            nr, utilities.StaticFile._url_, server.ticket.ticket, name, name))
    server.the_file.write('</pre>')


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

    
def gc_type(server):
    """Display a clickable list of the instance of the classes specified"""
    if configuration.regtest:
        server.the_file.write(server._("MSG_evaluate"))
        return
    gc.collect()
    objects = gc.get_objects()
    server.the_file.write('<h1> ? → ' + '→'.join(server.the_path) + '</h1>')
    server.the_file.write('<pre>')
    what = collections.defaultdict(list)
    for i in objects:
        for j in check(server.the_path, i):
            what[type(i).__name__].append(j)
    s = sorted(what, key=lambda x: len(what[x]))
    s.reverse()
    for k in s:
        server.the_file.write('%s(<a href="%s/=%s/type/%s">%s</a>)' % (
                k,
                utilities.StaticFile._url_,
                server.ticket.ticket,
                k + '/' + '/'.join(server.the_path),
                len(what[k])))
        for i in what[k][:10]:
            server.the_file.write(' <a href="%s/=%s/object/%s">%x</a>' % (
                utilities.StaticFile._url_,
                server.ticket.ticket,
                id(i),
                id(i)))
        server.the_file.write('\n')
                    
    server.the_file.write('</pre>')

def gc_object(server):
    """Display the graph of instances using or used by the object"""
    if configuration.regtest:
        server.the_file.write(server._("MSG_evaluate"))
        return
    i = objgraph.at(int(server.the_path[0], 0))
    gc.collect()
    objgraph.show_backrefs(i, max_depth=5)
    server.the_file.write(utilities.read_file(os.path.join('TMP',
                                                           'objects.png')))

plugin.Plugin('gctop'   , '/gc'        , group='roots', function=gc_top,
              link=plugin.Link(where='debug', html_class='verysafe')
              )
plugin.Plugin('gctype'  , '/type/{*}'  , group='roots', function=gc_type)
plugin.Plugin('gcobject', '/object/{*}', group='roots', function=gc_object,
              mimetype = 'image/png')

import math
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
            size = server._("MSG_cache_size") % len(cache.cache[0])
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
        
        s.append('<tr><td>%s<td>%s<td>%s<td width="50%%">%s<td>%s<td>%s items %s' % (
            cache.fct.func_name.replace('_',' '), cgi.escape(doc),
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

plugin.Plugin('locks'   , '/locks'   , group='roots', function=locks,
              link=plugin.Link(where='debug', html_class='verysafe')
              )

def threads(server):
    """Displays the running thread"""
    server.the_file.write('<title>' + server._("MSG_threads_title")
                          + '</title><pre>' +
                          '\n'.join(cgi.escape(t.stack())
                                    for t in utilities.thread_list) +
                          '</pre>')

plugin.Plugin('threads'   , '/threads'   , group='roots', function=threads,
              link=plugin.Link(where='debug', html_class='verysafe')
              )

