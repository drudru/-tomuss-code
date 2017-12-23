#!/usr/bin/python3
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2008-2011 Thierry EXCOFFIER, Universite Claude Bernard
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

class Suivi(object):
    def __init__(self, https=False):
        self.urls = {}
        if https:
            self.http = 'https'
        else:
            self.http = 'http'
    def urls_sorted(self):
        from . import utilities
        urls = list(self.urls.items())
        urls.sort(key=lambda x: utilities.semester_key(x[0][0], x[0][1]))
        if urls:
            return tuple(zip(*urls))[1]
        else:
            return ()
    def servers(self):
        done = set()
        servers = list(self.urls_sorted())
        servers.reverse() # most recent servers first
        for url, port, year, semester, host in servers:
            if port in done:
                continue
            done.add(port)
            yield url, port, year, semester, host
    def add(self, year, semester, host, port):
        if '%' in host:
            host = host % port
        self.urls[str(year), semester] = (
            '%s://%s/%s/%s' % (self.http, host, year, semester),
            port, year, semester, host)
    def url(self, year=None, semester=None, ticket=None):
        from . import configuration
        if year == None:
            year, semester = configuration.year_semester
        try:
            url, port, year, semester, host = self.urls[str(year), semester]
        except KeyError:
            if ticket and (year, semester) != configuration.year_semester:
                return self.url(configuration.year_semester[0],
                                configuration.year_semester[1],
                                ticket,
                                )
            return 'http://not_running_suivi_server/'
        if ticket:
            u = '%s://%s/=%s/%s/%s' % (self.http, host, ticket, year, semester)
        else:
            u = '%s://%s/%s/%s' % (self.http, host, year, semester)
        return u
    def url_with_ticket(self, ticket):
        for url, port, year, semester, host in self.urls_sorted():
            yield  ('%s://%s/=%s/%s/%s'%(self.http,host,ticket,year,semester),
                    port, year, semester, host)
    def all(self, ticket=None):
        if ticket:
            return '{' + ','.join([
                '"%d/%s": "%s://%s/=%s/%s/%s"' % (
                year, semester, self.http, host, ticket, year, semester)
                for url, port, year, semester, host in self.urls.values()])+'}'
        else:
            return '{' + ','.join([
                '"%d/%s": "%s"' % (year, semester, url)
                for url, port, year, semester, host in self.urls.values()])+'}'
    def domains(self):
        return set("{}://{}".format(self.http, host)
                   for url, port, year, semester, host in self.urls.values()
                   )
