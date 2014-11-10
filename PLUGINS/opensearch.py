#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2014 Thierry EXCOFFIER, Universite Claude Bernard
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
from .. import plugin
from .. import configuration
from .. import utilities
from .. import inscrits
from .. import teacher

def opensearch_desc(server):
    server.the_file.write(u"""<?xml version="1.0" encoding="UTF-8"?>
<OpenSearchDescription xmlns="http://a9.com/-/spec/opensearch/1.1/"
                       xmlns:moz="http://www.mozilla.org/2006/browser/search/">
  <ShortName>TOMUSS</ShortName>
  <Description>Etudiant/UE</Description>
  <InputEncoding>UTF-8</InputEncoding>
  <Url type="text/html" method="GET" template="%s/search/{searchTerms}">
  </Url>
</OpenSearchDescription>
""" % (configuration.server_url,))

def link(server, info):
    return '<a href="%s/%s">%s %s</a><br>\n' % (
        configuration.suivi.url(ticket=server.ticket.ticket),
        info[0], cgi.escape(info[1]),
        cgi.escape(info[2].title()))

def display(server, name, who, where):
    infos = inscrits.L_slow.firstname_or_surname_to_logins(
        name,
        attributes=[configuration.attr_login,
                    configuration.attr_surname,
                    configuration.attr_firstname,
                    configuration.attr_mail,
                ],
        base = where
    )
    infos = sorted(infos, key=lambda x: (x[1], x[2]))
    if infos:
        server.the_file.write(
            "<h2>%s</h2>\n" % who
            + ''.join(link(server, x) for x in infos).encode('utf-8')
        )
    return len(infos)


def code(txt):
    if '-' in txt:
        return txt
    else:
        return 'UE-' + txt

def display_ue(server, name):
    ues = []
    for ue in teacher.all_ues().values():
        if (name in ue.intitule().lower()
            or name in ue.name.lower()
            or name in ''.join(ue.responsables()).lower()
            ):
            ues.append(ue)
    if ues:
        ues.sort(key=lambda x: x.name)
        server.the_file.write(
            "<h2>" + server._("TH_home_ue") + "</h2>"
            + ''.join('<a href="%s/=%s/%s/%s/%s"><tt>%s</tt> %s</a><br>\n' %
                      (configuration.server_url,
                       server.ticket.ticket,
                       configuration.year_semester[0],
                       configuration.year_semester[1],
                       code(x.name),
                       code(x.name),
                       x.intitule().encode('utf-8'))
                      for x in ues)
        )
    return len(ues)

def search(server):
    if server.ticket is None:
        class Debug:
            ticket = "thierry.excoffier"
            language = "fr"
        server.ticket = Debug()
    q = utilities.flat(unicode('/'.join(server.the_path),
                               'utf-8')).replace('+', ' ').encode('utf-8')
    if len(q) < 2:
        server.the_file.write("?")
        return
        
    server.the_file.write('''<html>
<style>
TABLE TR { vertical-align: top }
TABLE { table-layout: fixed }
H1 { text-align: center }
</style>
<h1>«%s»</h1>
<table style="vertical-align:top"><tr><td>
    ''' % cgi.escape(q).encode("utf-8"))
    n = display(server, q, server._("MSG_mail_students"),
                configuration.cn_students)
    server.the_file.write("<td>")
    n += display(server, q, server._("MSG_mail_teachers"),
                 configuration.cn_teachers)
    server.the_file.write("<td>")
    n += display_ue(server, q)
    server.the_file.write("</tr></table>")
    if n == 0:
        server.the_file.write("?")

plugin.Plugin('opensearch_desc', '/opensearch_desc',
              function=opensearch_desc,
              authenticated=False,
              documentation = "Opensearch description",
              mimetype="application/opensearchdescription+xml",
              cached = True,
              )

plugin.Plugin('search', '/search/{*}',
              function=search,
              documentation = "Opensearch results",
              launch_thread=True,
              unsafe=False,
              )






