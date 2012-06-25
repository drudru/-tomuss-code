#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2009 Thierry EXCOFFIER, Universite Claude Bernard
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
import plugin
import ticket
import configuration
import document
import column
import cell

def the_new_pages(the_year):
    d = configuration.db + '/Y%d/S*/*.py' % the_year

    f = os.popen("grep -h '^new_page' " + d, "r")
    for i in f:
        yield i
    f.close()

class Stat(object):
    def __init__(self, what):
        self.ip = {}
        self.browser = {}
        self.os = {}
        self.login = {}
        self.nr_pages = 0
        self.what = what

    def add(self, ip, browser, oss, login):
        self.ip     [ip     ] =      self.ip.get(ip     , 0) + 1
        self.browser[browser] = self.browser.get(browser, 0) + 1
        self.os     [oss    ] =      self.os.get(oss    , 0) + 1
        self.login  [login  ] =   self.login.get(login  , 0) + 1
        self.nr_pages += 1
        

def new_page_stat(the_year):
    clients = {}
    oss = {}
    ips = {}
    logins = {}

    def new_page(ticket, login, ip, client, date=None):
        if 'MSIE 7' in client:
            nav = 'IE7'
        elif 'MSIE 6' in client:
            nav = 'IE6'
        elif 'MSIE' in client:
            nav = 'IE'
        elif 'Firefox/1' in client:
            nav = 'Gecko Firefox1'
        elif 'Firefox/2' in client:
            nav = 'Gecko Firefox2'
        elif 'Firefox/3' in client:
            nav = 'Gecko Firefox3'
        elif 'Firefox/4' in client:
            nav = 'Gecko Firefox4'
        elif 'Iceape' in client:
            nav = 'Gecko Iceape'
        elif 'Iceweasel' in client:
            nav = 'Gecko Iceweasel'
        elif 'SeaMonkey' in client:
            nav = 'Gecko SeaMonkey'
        elif 'Netscape/7' in client:
            nav = 'Gecko Netscape'
        elif 'Epiphany' in client:
            nav = 'Gecko Epiphany'
        elif 'Galeon' in client:
            nav = 'Gecko Galeon'
        elif 'Camino' in client:
            nav = 'Gecko Camino'
        elif 'Chrome/' in client:
            nav = 'Chrome'
        elif 'Safari' in client:
            nav = 'Safari (KHTML)'
        elif 'KHTML' in client:
            nav = 'KHTML'
        elif 'Opera' in client:
            nav = 'Opera'
        elif 'Gecko' in client:
            nav = 'Gecko'
        else:
            nav = client

        if 'Windows NT 5' in client:
            os = 'Windows 5'
        elif 'WinNT4' in client:
            os = 'Windows 4'
        elif 'Windows NT 4' in client:
            os = 'Windows 4'
        elif 'Windows NT 6' in client:
            os = 'Windows 6'
        elif 'Windows 98' in client:
            os = 'Windows 98'
        elif 'Windows' in client:
            print 'os', client
            os = 'Windows'
        elif 'Linux' in client:
            os = 'Linux'
        elif 'Mac OS' in client:
            os = 'Macintosh'
        else:
            os = client

        if os not in oss:
            oss[os] = Stat('OS')
        oss[os].add(ip, nav, os, login)

        if ip not in ips:
            ips[ip] = Stat('IP')
        ips[ip].add(ip, nav, os, login)

        if nav not in clients:
            clients[nav] = Stat('Browser')
        clients[nav].add(ip, nav, os, login)

        if login not in logins:
            logins[login] = Stat('Login')
        logins[login].add(ip, nav, os, login)


    for line in the_new_pages(the_year):
        eval(line)

    return oss, ips, clients, logins


def clients(server):
    """Display client statistics.
    """

    columns = [
        column.Column('0', '', freezed='F', width=2, type='Text',
                      title=server._('COL_TITLE_type')),
        column.Column('1', '', freezed='F', width=2, type='Text',
                      title=server._('COL_TITLE_item')),
        column.Column('2', '', width=2, type='Note', title='IP',
                      comment=server._('COL_COMMENT_IP')),
        column.Column('3', '', width=2, type='Note',
                      title=server._("COL_TITLE_ID"),
                      comment=server._('COL_COMMENT_ID')),
        column.Column('4', '', width=2, type='Note',
                      title=server._("COL_TITLE_browser"),
                      comment=server._('COL_COMMENT_browser')),
        column.Column('5', '', width=2, type='Note',
                      title=server._("COL_TITLE_OS"),
                      comment=server._('COL_COMMENT_OS')),
        column.Column('6', '', width=2, type='Note',
                      title=server._("COL_TITLE_page"),
                      comment=server._('COL_COMMENT_page')),
         ]
    table_attrs = { 'comment': server._("TABLE_COMMENT_client"),
                    'default_nr_columns': 7,
                    }
    oss, ips, browsers, logins = new_page_stat(server.the_year)
    oss.update(ips)
    oss.update(browsers)
    oss.update(logins)

    def txt(d):
        return repr(', '.join(['%s:%d' % (k,v) for k, v in d.items()]))

    lines = []
    for i, t in enumerate(oss):
        s = oss[t]
        lines.append(cell.Line((
                cell.CellValue(s.what),
                cell.CellValue(t),
                cell.Cell(len(s.ip), '', '', txt(s.ip)),
                cell.Cell(len(s.login), '', '', txt(s.login)),
                cell.Cell(len(s.browser), '', '', txt(s.browser)),
                cell.Cell(len(s.os), '', '', txt(s.os)),
                cell.CellValue(s.nr_pages),
                )))
    document.virtual_table(server, columns, lines, table_attrs)

plugin.Plugin('clients', '/clients/{Y}',
              function=clients,
              root=True,
              link=plugin.Link(text="Statistiques clients",
                               help="""Sur les navigateurs,
                               les systèmes d'exploitation et les adresses IP.
                               C'est pas très bien pour la vie privée.""",
                               html_class="verysafe",
                               where="informations",
                               url="javascript:go_year_after('clients')"
                               ),
              launch_thread = True,
              )

if __name__ == "__main__":
    clients(None)




