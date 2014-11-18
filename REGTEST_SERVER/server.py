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
import sys
import subprocess
import shutil
import glob
import time
import urllib2
import socket
from .. import configuration
from .. import utilities

# To make casauth work we should not use a proxy
for ii in ('http_proxy', 'https_proxy'):
    if os.environ.has_key(ii):
        del os.environ[ii]

class Server(object):
    port = 8888
    name = "tomuss"
    started = False
    start_time = 0
    
    def start(self, cleaning=True, sync=True):
        if Server.start_time == 0:
            Server.start_time = time.time()
        for dirname in ['DBregtest', 'BACKUP_DBregtest',
                        '/tmp/DBregtest', '/tmp/BACKUP_DBregtest', 
                        ] + glob.glob('TMP/TICKETS/*'):
            print 'delete:', dirname
            try:
                os.unlink(dirname)
            except OSError:
                shutil.rmtree(dirname, ignore_errors=True)
        for i in ('DBregtest', 'BACKUP_DBregtest'):
            name = '/tmp/%s/Y%d/SAutomne'%(i, configuration.year_semester[0]-1)
            utilities.mkpath_safe(name)
            os.symlink(name, i)
        self.restart('w', sync=sync)

    def log_files(self, mode):
        if True:
            return (open('xxx.' + self.name + '.stdout', mode),
                    open('xxx.' + self.name + '.stderr', mode))
        else:
            return sys.stdout, sys.stderr

    def wait_start(self):
        i = 0
        while True:
            try:
                self.url('=super.user/evaluate/1', stop_if_error=False,
                         display_log_if_error=False, silent=i)
                self.started = True
                break
            except (urllib2.HTTPError, urllib2.URLError):
                i += 1
                sys.stdout.write('*')
                sys.stdout.flush()
                time.sleep(0.1)


    def restart(self, mode='a', more=[], sync=True):
        stdout, stderr = self.log_files(mode)
        args = ['./tomuss.py', 'regtest', 'real_regtest']
        if sync:
            args.append('regtest_sync')
        self.process = subprocess.Popen(args + more,
                                        stdout = stdout.fileno(),
                                        stderr = stderr.fileno(),
                                        )
        self.wait_start()

    def get_url(self, url):
        return 'http://' + socket.getfqdn() + ':' + str(self.port) + '/' + url

    def url(self, url, stop_if_error=True, display_log_if_error=True,
            returns_file=False, timeout=0, silent=False):
        full_url = self.get_url(url)
        if not silent:
            print ' %6.2f ' % (time.time() - Server.start_time) + url,
        sys.stdout.flush()
        try:
            if timeout:
                f = urllib2.urlopen(full_url, timeout=timeout)
            else:
                f = urllib2.urlopen(full_url)
            if returns_file:
                c = f
            else:
                if timeout:
                    c = ''
                    try:
                        while True:
                            c += f.read(1)
                    except socket.timeout:
                        c += '***TIMEOUT***'
                else:
                    c = f.read()
            print '*'
        except:
            if stop_if_error:
                self.stop()
            if display_log_if_error:
                print self.stdout()
                print self.stderr()
            raise
        if not returns_file:
            f.close()
        # os.system('diff -u -r *DBregtest/')
        url = url.split('/')
        if (self.name == 'tomuss'
            and len(url) == 4
            and url[-2] in ('Automne', 'Printemps', 'Test')
            and url[-1] not in ('abj', 'UE-pastue')
            ):
            name = os.path.join('DBregtest',
                                'Y'+url[-3], 'S'+url[-2], url[-1]+'.py')
            if os.path.exists(name):
                f = open(name, "r")
                x = f.read()
                f.close()
                assert("# 0" in x)
        return c
        
    def stop(self):
        self.url('stop', stop_if_error=False, display_log_if_error=False)
        self.process.wait()

    def stdout(self):
        return utilities.read_file('xxx.' + self.name + '.stdout')

    def stderr(self):
        return utilities.read_file('xxx.' + self.name + '.stderr')

    def errors(self):
        if 'Traceback' in self.stdout() + self.stderr():
            raise ValueError('Traceback in logs')

class ServerSuivi(Server):
    port = 8889
    name = 'suivi'
    
    def start(self):
        if self.started:
            return
        self.restart('w')

    def restart(self, mode='a'):
        stdout, stderr = self.log_files(mode)
        self.process = subprocess.Popen(['./suivi.py',
                                         str(configuration.year_semester[0]),
                                         configuration.year_semester[1],
                                         str(self.port),
                                         'regtest', 'real_regtest'],
                                        stdout = stdout.fileno(),
                                        stderr = stderr.fileno(),
                                        )
        self.wait_start()

def check(filename,
          masters_expected=None,
          nr_pages=None,
          nr_columns=None,
          lines_id=None,
          nr_cells=None,
          cell_required=None,
          one_cell_required=None,
          column_required=None,
          dump=False,
          exists=None):

    if exists is False:
        return not os.path.exists('DBregtest/' + filename) \
               and not os.path.exists('BACKUP_DBregtest/' + filename)

    masters = []
    pages = []
    columns = []
    nr_columns_default = []
    cells = []
    column_dict = {}
    
#    def add_master(master,page_id=None):
#        masters.append(master)
    def new_page(page_ticket, page_author, page_ip, page_browser,date=None):
        pages.append((page_ticket, page_author, page_ip, page_browser,date))
    def cell_change(page_id, col_id, line_id, value, date):
        cells.append((page_id, col_id, line_id, value))
    def comment_change(page_id, col_id, line_id, comment):
        cells.append((page_id, col_id, line_id, comment))
    def column_attr(attr, page_id, col_id, value):
        columns.append((attr, page_id, col_id, value))
        column_dict[col_id] = True
    def table_attr(attr, page_id, value):
        if attr == 'masters':
            while masters:
                masters.pop()
            while value:
                masters.append(value.pop(0))
        elif attr == 'comment':
            columns.append((page_id, value))
        elif attr == 'default_nr_columns':
            nr_columns_default.append(value)

    c = utilities.read_file('DBregtest/' + filename)
    if utilities.read_file('BACKUP_DBregtest/' + filename) != c:
        time.sleep(1)
        if utilities.read_file('BACKUP_DBregtest/' + filename) != c:
            os.system('diff -u ' + 'DBregtest/' + filename + ' BACKUP_DBregtest/' + filename)
            raise ValueError(filename + '\nBad Backup')
    
    for line in c.split('\n')[2:]:
        if line != '':
            eval(line)

    the_lines_id = {}
    if cells:
        for line_id in zip(*cells)[2]:
            the_lines_id[line_id] = True
        the_lines_id = list(the_lines_id.keys())
        the_lines_id.sort()
    else:
        the_lines_id = []
        
    if masters_expected != None and masters_expected != masters:
        print 'Masters =', masters
        print 'Masters Expected =', masters_expected
        raise ValueError(filename + '\nBad masters')
    if nr_pages != None and nr_pages != len(pages):
        print '#pages =', len(pages)
        print '#pages Expected =', nr_pages
        raise ValueError(filename + '\nBad #pages')
    if nr_columns != None and nr_columns != len(column_dict):
        print '#columns =', len(column_dict)
        print '#columns Expected =', nr_columns
        for col in columns:
            print '\t',col
        raise ValueError(filename + '\nBad #columns')
    if lines_id != None and lines_id != the_lines_id:
        print '#lines_id =', the_lines_id
        print '#lines_id Expected =', lines_id
        raise ValueError(filename + '\nBad lines_id')
    if nr_cells != None and nr_cells != len(cells):
        print '#cells =', len(cells)
        print '#cells Expected =', nr_cells
        raise ValueError(filename + '\nBad #cells')
    if cell_required != None:
        one_cell_required = [cell_required]
        
    if one_cell_required != None:
        for cr in one_cell_required:
            for i in cells:
                if i[0:4] == cr:
                    break
            else:
                continue
            break
        else:
            print 'cells ='
            for cell in cells:
                print '\t',cell
            print 'one_cell required =', one_cell_required
            raise ValueError(filename + '\nCell required')
    if column_required != None:
        for i in columns:
            if i == column_required:
                break
        else:
            print 'columns =', columns
            print 'column required =', column_required
            raise ValueError(filename + '\nColumn required')
            

    if dump:
        print masters
        print pages
        print columns
        print nr_columns
        print cells
        print the_lines_id
