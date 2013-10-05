#!/usr/bin/env python
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

import sys
import urllib2
import threading
import time

sys.argv.append("real_regtest")
import tomuss_init
from .. import configuration
from .. import utilities
from . import server
sys.argv.remove("real_regtest")

configuration.regtest = True

root     = configuration.root[0]
abj      = configuration.invited_abj_masters[1]
invited  = configuration.invited_teachers[0]
ok_png   = utilities.read_file('FILES/ok.png')

class Reader(threading.Thread):
    def __init__(self, f):
        self.file = f
        self.buffer = ''
        threading.Thread.__init__(self)
    def run(self):
        try:
            while True:
                self.buffer += self.file.read(1)
        except TypeError:
            pass
    def wait_content(self, content):
        t = time.time()
        while time.time() - t < 5: # Wait 2 seconds
            if content in self.buffer:
                return True
        print self.buffer
        print 'TIMEOUT'
        return

def wait_nr_file(s, nb):
    print "Wait close"
    for dummy_i in range(10):
        x = s.url("=" + root + '/stat')
        if x.count("<b><a") == nb:
            break
        time.sleep(0.1)
    else:
        raise ValueError("Connection not closed")
    
def tests(s):
    print "Start first browser: A"
    a = s.url("=" + root + '/0/Public/sync')
    assert('page_id = "1"' in a)
    a_link = Reader(urllib2.urlopen(s.get_url("=" +root+ '/0/Public/sync/1')))
    a_link.setDaemon(True)
    a_link.start()


    print "Start second browser: B"
    b = s.url("=" + root + '/0/Public/sync')
    assert('page_id = "2"' in b)
    b_link = Reader(urllib2.urlopen(s.get_url("=" +root+ '/0/Public/sync/2')))
    b_link.setDaemon(True)
    b_link.start()

    print "A create a column"
    assert(s.url("=" + root
                 + '/0/Public/sync/1/0/column_attr_title/col_0/SyncTitle')
           == ok_png)
                
    assert( b_link.wait_content('SyncTitle') == True )

    print "B change a cell"
    assert(s.url("=" + root
                 + '/0/Public/sync/2/0/cell_change/col_0/line_0/SyncValue')
           == ok_png)
                
    assert( a_link.wait_content('SyncValue') == True )
    # Needed because there is some data sent after SyncValue
    # these data are in the same packet.
    # If the connection is close too quickly, the data
    # packet will be resent and the regtest will fail on line YYY_HERE_YYY
    time.sleep(1)
    print "B broke the link 1"
    b_link.file.close()
    
    print "A change a cell"
    assert(s.url("=" + root
                 + '/0/Public/sync/1/1/cell_change/col_0/line_1/SyncBroken')
           == ok_png)

    print "B restore the link"
    b_link = Reader(urllib2.urlopen(s.get_url("=" +root+ '/0/Public/sync/2')))
    b_link.setDaemon(True)
    b_link.start()

    assert( b_link.wait_content('SyncBroken') == True )
    assert('SyncValue' not in b_link.buffer) # YYY_HERE_YYY
    assert('SyncTitle' not in b_link.buffer)


    print "B broke the link 2"
    b_link.file.close()

    print "A change a cell"
    assert(s.url("=" + root
                 + '/0/Public/sync/1/2/cell_change/col_0/line_1/SyncLongBroke')
           == ok_png)

    wait_nr_file(s, 1)

    print "B restore the link 2"
    b_link = Reader(urllib2.urlopen(s.get_url("=" +root+ '/0/Public/sync/2')))
    b_link.setDaemon(True)
    b_link.start()

    assert( b_link.wait_content('SyncLongBroke') == True )
    assert('Xcell_change("col_0","line_0","SyncValue"' not in b_link.buffer)
    assert('Xcolumn_attr(\'title\',"col_0","SyncTitle"' not in b_link.buffer)
    assert('Xcell_change("col_0","line_1","SyncBroken"' not in b_link.buffer)

    print "B broke the link 3"
    b_link.file.close()
    s.url("=" + root  + '/send_alert/a_message_to_close_connection')
    # wait_nr_file(s, 1)
    
    print "B restore the link 3"
    b_link = Reader(urllib2.urlopen(s.get_url("=" +root+ '/0/Public/sync/2')))
    b_link.setDaemon(True)
    b_link.start()

    assert( b_link.wait_content("</script>") == True )
    assert('Xcell_change("col_0","line_1","SyncLongBroke' not in b_link.buffer)
    
    print "done"

try:
    s = server.Server()
    s.start(sync=False)
    tests(s)
    print 'Sync tests are fine'
finally:
    s.stop()




