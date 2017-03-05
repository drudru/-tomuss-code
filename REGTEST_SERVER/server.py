#!/usr/bin/env python3
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
import time
import urllib.request, urllib.error, urllib.parse
import socket
import tests_config
from .. import configuration
from .. import utilities

# To make casauth work we should not use a proxy
for ii in ('http_proxy', 'https_proxy'):
    if ii in os.environ:
        del os.environ[ii]

def get_content_type(filename):
    import mimetypes
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = b'----------ThIs_Is_tHe_bouNdaRY_$'
    CRLF = b'\r\n'
    L = []
    for (key, value) in fields:
        L.append(b'--' + BOUNDARY)
        L.append(b'Content-Disposition: form-data; name="'
                 + key.encode("utf-8") + b'"')
        L.append(b'')
        L.append(value.encode("utf-8"))
    for (key, filename, value) in files:
        L.append(b'--' + BOUNDARY)
        L.append(b'Content-Disposition: form-data; name="'
                 + key.encode("utf-8")
                 + b'"; filename="'
                 + filename.encode("utf-8")
                 + b'"')
        L.append(b'Content-Type: '
                 + get_content_type(filename).encode("utf-8"))
        L.append(b'')
        L.append(value)
    L.append(b'--' + BOUNDARY + b'--')
    L.append(b'')
    body = CRLF.join(L)
    content_type = b'multipart/form-data; boundary=' + BOUNDARY
    return content_type, body

def post_multipart(url, fields, files, cj):
    """
    Post fields and files to an http host as multipart/form-data.
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return the server's response page.
    """
    import http.client
    host = url.split('/')[2]
    selector = '/' + url.split('/', 3)[-1]
    content_type, body = encode_multipart_formdata(fields, files)
    h = http.client.HTTPConnection(host)
    h.putrequest('POST', selector)
    h.putheader('content-type', content_type)
    h.putheader('content-length', str(len(body)))
    h.putheader('user-agent', "tomuss POST regtest")
    h.putheader('host', host)
    h.putheader('cookie', '; '.join('%s=%s' % (c.name, c.value)
                                    for c in cj
                                    if c.name.startswith("PHP")
                                    ))
    h.endheaders()
    h.send(body)
    return h.getresponse().read().decode("utf-8")
    # errcode, errmsg, headers = h.getresponse()
    # # XXX All these test should not be necessary.
    # # But the file uploading fail sometime without these
    # if h.file:
    #     h.file._sock.settimeout(None)
    #     return h.file.read() or post_multipart(url, fields, files, cj)
    # else:
    #     return post_multipart(url, fields, files, cj)

class Server(object):
    port = 8888
    name = "tomuss"
    started = False
    start_time = 0
    
    def start(self, cleaning=True, sync=True, load_local=False):
        if Server.start_time == 0:
            Server.start_time = time.time()
        tests_config.init(configuration.year_semester[0])
        self.restart('w', sync=sync, load_local=load_local)

    def log_files(self, mode):
        if True:
            return (open('xxx.' + self.name + '.stdout', mode, encoding = "utf-8"),
                    open('xxx.' + self.name + '.stderr', mode, encoding = "utf-8"))
        else:
            return sys.stdout, sys.stderr

    def wait_start(self):
        i = 0
        while True:
            try:
                self.url('=' + configuration.root[0] + '/evaluate/1', stop_if_error=False,
                         display_log_if_error=False, silent=i)
                self.started = True
                break
            except (urllib.error.HTTPError, urllib.error.URLError):
                i += 1
                sys.stdout.write('*')
                sys.stdout.flush()
                time.sleep(0.1)


    def restart(self, mode='a', more=[], sync=True, load_local=False):
        stdout, stderr = self.log_files(mode)
        args = ['./tomuss.py', 'regtest', 'real_regtest']
        if sync:
            args.append('regtest_sync')
        if load_local:
            args.append('regtest_load_local')
        self.process = subprocess.Popen(args + more,
                                        stdout = stdout.fileno(),
                                        stderr = stderr.fileno(),
                                        )
        self.wait_start()

    def get_url(self, url):
        return 'http://' + socket.getfqdn() + ':' + str(self.port) + '/' + url

    def url(self, url, stop_if_error=True, display_log_if_error=True,
            returns_file=False, timeout=0, silent=False, read_bytes=False):
        full_url = self.get_url(url)
        if not silent:
            print(' %6.2f ' % (time.time() - Server.start_time) + url, end=' ')
        sys.stdout.flush()
        try:
            if timeout:
                f = urllib.request.urlopen(full_url, timeout=timeout)
            else:
                f = urllib.request.urlopen(full_url)
            if returns_file:
                c = f
            else:
                c = b""
                if timeout:
                    try:
                        while True:
                            x = f.read(1)
                            if x == b'':
                                c += b'!***TIMEOUT***!'
                                break
                            c += x
                    except socket.timeout:
                        c += b'***TIMEOUT***'
                else:
                    c = f.read()
                if not read_bytes and b"PNG" not in c :
                    # if b"utf-8" not in c:
                    #     print(c)
                    c = c.decode(encoding="utf-8", errors="replace")
            print('*')
        except:
            if stop_if_error:
                self.stop()
            if display_log_if_error:
                print(self.stdout())
                print(self.stderr())
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
                f = open(name, "r", encoding = "utf-8")
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

    def post(self, url, fields=(), files=()):
        full_url = self.get_url(url)
        print(' %6.2f ' % (time.time() - Server.start_time) + url, end=' ')
        c = post_multipart(full_url, fields, files, {})
        print("*")
        return c

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
    def column_attr(attr, page_id, col_id, value, dummy_date):
        columns.append((attr, page_id, col_id, value))
        column_dict[col_id] = True
    def table_attr(attr, page_id, value, dummy_date):
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
        for line_id in list(zip(*cells))[2]:
            the_lines_id[line_id] = True
        the_lines_id = list(the_lines_id.keys())
        the_lines_id.sort()
    else:
        the_lines_id = []
        
    if masters_expected != None and masters_expected != masters:
        print('Masters =', masters)
        print('Masters Expected =', masters_expected)
        raise ValueError(filename + '\nBad masters')
    if nr_pages != None and nr_pages != len(pages):
        print('#pages =', len(pages))
        print('#pages Expected =', nr_pages)
        raise ValueError(filename + '\nBad #pages')
    if nr_columns != None and nr_columns != len(column_dict):
        print('#columns =', len(column_dict))
        print('#columns Expected =', nr_columns)
        for col in columns:
            print('\t',col)
        raise ValueError(filename + '\nBad #columns')
    if lines_id != None and lines_id != the_lines_id:
        print('#lines_id =', the_lines_id)
        print('#lines_id Expected =', lines_id)
        raise ValueError(filename + '\nBad lines_id')
    if nr_cells != None and nr_cells != len(cells):
        print('#cells =', len(cells))
        print('#cells Expected =', nr_cells)
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
            print('cells =')
            for cell in cells:
                print('\t',cell)
            print('one_cell required =', one_cell_required)
            raise ValueError(filename + '\nCell required')
    if column_required != None:
        for i in columns:
            if i == column_required:
                break
        else:
            print('columns =', columns)
            print('column required =', column_required)
            raise ValueError(filename + '\nColumn required')
            

    if dump:
        print(masters)
        print(pages)
        print(columns)
        print(nr_columns)
        print(cells)
        print(the_lines_id)
