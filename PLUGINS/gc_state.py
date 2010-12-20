#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2008-2010 Thierry EXCOFFIER, Universite Claude Bernard
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
import gc
import objgraph
import cgi
import utilities
import os
import configuration
import time

def gc_top(server):
    "Display a clickable list of Python classes and their number of instance."
    if configuration.regtest:
        server.the_file.write('Disabled functionnality on demo server')
        return
    
    server.the_file.write('<META NAME="ROBOTS" CONTENT="NOINDEX, NOFOLLOW">\n')
    server.the_file.write('<pre>')
    gc.collect()
    for name, nr in objgraph.types_sorted():
        server.the_file.write('%6d <a href="%s/=%s/type/%s">%s</a>\n' % (
            nr, utilities.StaticFile._url_, server.ticket.ticket, name, name))
    server.the_file.write('</pre>')


def gc_type(server):
    """Display a clickable list of the instance of the classes specified"""
    if configuration.regtest:
        server.the_file.write('Disabled functionnality on demo server')
        return
    server.the_file.write('<pre>')
    for i in objgraph.by_type(server.the_path[0]):
        if hasattr(i, 'closed'):
            closed = 'closed=%s' % i.closed
        else:
            closed = ''
        if isinstance(i, utilities.StaticFile):
            value = i.name
        else:
            value = str(i)
        server.the_file.write('<a href="%s/=%s/object/%s">' % (
            utilities.StaticFile._url_, server.ticket.ticket,
                                               id(i)) +
                cgi.escape(value) + '</a> %s\n' % closed)
    server.the_file.write('</pre>')

def gc_object(server):
    """Display the graph of instances using or used by the object"""
    if configuration.regtest:
        server.the_file.write('Disabled functionnality on demo server')
        return
    o = int(server.the_path[0], 0)
    for i in gc.get_objects():
        if id(i) == o:
            gc.collect()
            objgraph.show_backrefs(i, max_depth=5)
            server.the_file.write(utilities.read_file(
                os.path.join('TMP', 'objects.png')))
            break

plugin.Plugin('gctop'   , '/gc'        , root=True, function=gc_top,
              link=plugin.Link(text='Affiche les objets python en mémoire',
                               help="Utile pour trouver les fuites mémoire",
                               where='debug',
                               html_class='verysafe',
                          )
              )
plugin.Plugin('gctype'  , '/type/{*}'  , root=True, function=gc_type)
plugin.Plugin('gcobject', '/object/{*}', root=True, function=gc_object,
              mimetype = 'image/png')


def caches(server):
    s = ['<table><tr><th>Name<th>What<th>Type<th>Age<th>Max Age<th>Content']
    now = int(time.time())
    for cache in utilities.caches:
        if  cache.the_type == 'add_a_cache0':
            nr_items = 1
            size = 'of size %d' % len(cache.cache[0])
            since = now - int(cache.cache[1])
        else:
            nr_items = len(cache.cache)
            size = ''
            sinces = list([now - int(c[1]) for c in cache.cache.values()])
            sinces.sort()
            
            since = ' '.join('%d*%d' % (nb, v)
                             for nb,v in utilities.count(sinces))
        if cache.__doc__ is None:
            doc = '???'
        else:
            doc = cache.__doc__
        
        s.append('<tr><td>%s<td>%s<td>%s<td>%s<td>%s<td>%s items %s' % (
            cache.fct.func_name, cgi.escape(doc), cache.the_type,
            since, cache.timeout, nr_items, size))
    s.append('</table>')
    server.the_file.write('\n'.join(s))

plugin.Plugin('caches'   , '/caches'   , root=True, function=caches,
              link=plugin.Link(text='Affiche les caches',
                               help="Utile pour trouver les fuites mémoire",
                               where='debug',
                               html_class='verysafe',
                          )
              )

def locks(server):
    server.the_file.write('<pre>' + utilities.lock_state() + '</pre>')

plugin.Plugin('locks'   , '/locks'   , root=True, function=locks,
              link=plugin.Link(text='Affiche les verrous',
                               help="Utile pour trouver ce qui bloque",
                               where='debug',
                               html_class='verysafe',
                          )
              )

