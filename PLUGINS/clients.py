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

import plugin
import ticket
import time
import utilities
import configuration
import document
import os

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
    BUG: The table displayed is the old version, not the new one
    because the redirect if too fast.
    A virtual table must be generated: see PLUGIN/resume.py
    """
    filename = document.table_filename(str(server.the_year),'Stats','clients')
    
    f = utilities.AtomicWrite(filename)
    f.write("""# -*- coding: utf8 -*-
from data import *
new_page('' ,'*', '', '')
column_change (0,'000','Type','Text','','','F',0,2)
column_change (0,'0_0','Item','Text','','','F',0,2)
column_change (0,'0_1','IP','Note','[0;NaN]','','',0,2)
column_comment(0,'0_1','Nombre d\\'adresses IPs utilisées')
column_change (0,'0_2','Login','Note','[0;NaN]','','',0,2)
column_comment(0,'0_2','Nombre de comptes utilisés')
column_change (0,'0_3','Browser','Note','[0;NaN]','','',0,2)
column_comment(0,'0_3','Nombre de navigateurs utilisés')
column_change (0,'0_4','OS','Note', '[0;NaN]','','',0,2)
column_comment(0,'0_4','Nombre de système d\\'exploitation utilisé')
column_change (0,'0_5','Pages','Note','[0;NaN]','','',0,2)
column_comment(0,'0_5','Nombre de pages affichées')
table_comment(0, 'Statistiques sur les utilisateurs')
table_attr('private', 0, 1)
add_master(%s,0)
table_attr('default_nr_columns', 0, 7)
""" % repr(server.ticket.user_name))
    oss, ips, clients, logins = new_page_stat(server.the_year)
    oss.update(ips)
    oss.update(clients)
    oss.update(logins)

    def txt(d):
        return repr(', '.join(['%s:%d' % (k,v) for k, v in d.items()]))
    
    for i, t in enumerate(oss):
        s = oss[t]
        f.write("cell_change(0,'000','%d','%s','')\n" % (i, s.what))
        f.write("cell_change(0,'0_0','%d','%s','')\n" % (i, t))
        f.write("cell_change(0,'0_1','%d',%d,'')\n" % (i, len(s.ip)))
        f.write("cell_change(0,'0_2','%d',%d,'')\n" % (i, len(s.login)))
        f.write("cell_change(0,'0_3','%d',%d,'')\n" % (i, len(s.browser)))
        f.write("cell_change(0,'0_4','%d',%d,'')\n" % (i, len(s.os)))
        f.write("cell_change(0,'0_5','%d',%d,'')\n" % (i, s.nr_pages))

        f.write("comment_change(0,'0_1','%d',%s)\n" % (i, txt(s.ip)))
        f.write("comment_change(0,'0_2','%d',%s)\n" % (i, txt(s.login)))
        f.write("comment_change(0,'0_3','%d',%s)\n" % (i, txt(s.browser)))
        f.write("comment_change(0,'0_4','%d',%s)\n" % (i, txt(s.os)))

    f.close()

    # XXX: Create __init__.py ???
    t = document.table(server.the_year, 'Stats', 'clients', create=False)
    if t:
        t.unload()


def headers(server):    
    return (
        ('Location','%s/=%s/%d/Stats/clients' % (
        configuration.server_url, server.ticket.ticket,
            server.the_year)), )


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
              response=307,
              headers = headers,
              )

if __name__ == "__main__":
    clients(None)




