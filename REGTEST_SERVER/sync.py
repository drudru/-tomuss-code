#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2013 Thierry EXCOFFIER, Universite Claude Bernard
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
#    Contact: Thierry.EXCOFFIER@univ-lyon1.fr

# If the test fails, try to take a longer timeout
timeout = 0.1

import sys
import time
import urllib.request, urllib.error, urllib.parse
import socket

sys.argv.append("real_regtest")
sys.argv.append("protect_do_not_display")
import tomuss_init
from .. import configuration
from .. import utilities
from . import server
sys.argv.remove("real_regtest")
sys.argv.remove("protect_do_not_display")

configuration.do_not_display = ('debug', 'auth', 'table', 'ldap', 'plugin',
                                'check', 'lang', 'DNU', 'info')

configuration.regtest = True

root     = configuration.root[0]
abj      = configuration.invited_abj_masters[1]
invited  = configuration.invited_teachers[0]
ok_png   = utilities.read_file('FILES/ok.png','bytes')

class Reader:
    
    def __init__(self, url):
        self.url = url
        self.buffer = b''
        hostname = socket.getfqdn() + ':' + str(server.Server.port)
        self.file = urllib.request.urlopen('http://' + hostname + '/' + url)

    def want_content(self, content):
        self.file.fp.raw._sock.settimeout(timeout)
        try:
            while True:
                self.buffer += self.file.read(1)
        except socket.timeout:
            self.must_contain(content)
            self.file.fp.raw._timeout_occurred = False

    def must_contain(self, content):
        if content.encode("utf-8") in self.buffer:
            return
        raise ValueError("%s Expected content not found: %s in\n%s" %
                         (self.url, content, self.buffer))    
    def must_not_contain(self, content):
        if content.encode("utf-8") not in self.buffer:
            return
        raise ValueError("%s unexpected content found: %s in\n%s" %
                         (self.url, content, self.buffer))    
    def close(self):
        print("Broke the link", self.url)
        try:
            # empty the socket input buffer
            self.file.read(10000)
        except OSError:
            pass
        # BEWARE the close do not really close the socket
        # Even the del does not make it.
        # So the 'send_alert' in the 'wait_nr_file' loop
        # Allow to wait the real close
        self.file.fp.raw._sock.shutdown(socket.SHUT_RDWR)
        self.file.fp.raw._sock.close()
        self.file.close()
        del self.file

def wait_nr_file(s, nb):
    print("Want %d files open on the server" % nb)
    while True:
        s.url("=" + root  + '/send_alert//a_message_to_close_connection')
        x = s.url("=" + root + '/stat')
        actives = x.count("<b><a")
        if actives == nb:
            break
        time.sleep(0.2)

def tests(s):
    print("Start first browser: A")
    a = s.url("=" + root + '/0/Public/sync')
    assert('page_id = "1"' in a)
    a_link = Reader("=" +root+ '/0/Public/sync/1/0')

    print("Start second browser: B")
    b = s.url("=" + root + '/0/Public/sync')
    assert('page_id = "2"' in b)
    b_link = Reader("=" +root+ '/0/Public/sync/2/0')
    wait_nr_file(s, 2)
    
    print("A create a column")
    assert(s.url("=" + root
                 + '/0/Public/sync/1/0/column_attr_title/col_0/SyncTitle')
           == ok_png)

    a_link.want_content('saved(0)')
    b_link.want_content('SyncTitle')

    print("B change a cell")
    assert(s.url("=" + root
                 + '/0/Public/sync/2/0/cell_change/col_0/line_0/SyncValue')
           == ok_png)
    a_link.want_content('SyncValue')
    b_link.want_content('window.page_index=3')
    b_link.close()
    wait_nr_file(s, 1)
    
    print("A change a cell 1")
    assert(s.url("=" + root
                 + '/0/Public/sync/1/1/cell_change/col_0/line_1/SyncBroken')
           == ok_png)

    print("B restore the link")
    b_link = Reader("=" +root+ '/0/Public/sync/2/1.4')

    b_link.want_content('Xcell_change("col_0","line_1","SyncBroken"')
    b_link.must_not_contain('Xcell_change("col_0","line_0","SyncValue"')
    b_link.must_not_contain('Xcolumn_attr(\'title\',"col_0","SyncTitle")')
    time.sleep(0.1)
    for n in range(14, 11, -1):
        try:
            b_link.want_content('window.page_index=%d' % n)
        except ValueError:
            pass
        break
    else:
        raise ValueError("Bad page index 1")

    b_link.close()
    wait_nr_file(s, 1)

    print("A change a cell 2. n=%d" % n)
    assert(s.url("=" + root
                 + '/0/Public/sync/1/2/cell_change/col_0/line_1/SyncLongBroke')
           == ok_png)


    print("B restore the link 2")
    b_link = Reader("=" +root+ '/0/Public/sync/2/1.%d' % n)
    b_link.want_content('SyncLongBroke')
    b_link.must_not_contain('Xcell_change("col_0","line_0","SyncValue"')
    b_link.must_not_contain('Xcolumn_attr(\'title\',"col_0","SyncTitle"')
    b_link.must_not_contain('Xcell_change("col_0","line_1","SyncBroken"')
    wait_nr_file(s, 2)
    for n in range(20, 18, -1):
        try:
            b_link.want_content('window.page_index=%d' % n)
        except ValueError:
            pass
        break
    else:
        raise ValueError("Bad page index")
    b_link.close()
    wait_nr_file(s, 1)
    
    print("B restore the link 3. n=%d" % n)
    b_link = Reader("=" +root+ '/0/Public/sync/2/1.%d' % n)
    b_link.want_content("</script>")
    b_link.must_not_contain('Xcell_change("col_0","line_1","SyncLongBroke')
    
    print("done")

try:
    s = server.Server()
    s.start(sync=False)
    tests(s)
    print('Sync tests are fine')
finally:
    time.sleep(0.1)
    s.stop()




