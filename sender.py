#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2009-2013 Thierry EXCOFFIER, Universite Claude Bernard
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

# All data structure are lock protected.

import time
import socket
from . import utilities

live_status = []

# xxx = open('xxx', 'w')

class File(object):
    nr_active_thread = 0
    to_send = {}

    def __init__(self, f, txt, keep_open, index):
        assert(append.the_lock.locked())
        self.file = f
        File.to_send[f] = self
        self.send = [txt]
        self.keep_open = keep_open
        self.in_processing = False
        self.index = index
        
    def append(self, txt, keep_open, index):
        assert(append.the_lock.locked())
        if self.keep_open is False:
            raise ValueError('Append to a closed file')
        self.send.append(txt)
        if index is not None:
            self.index = index
        self.keep_open = keep_open

    def delete(self):
        del File.to_send[self.file]
        File.nr_active_thread -= 1

    def send_text(self):
        """Return True if a text is sent"""
        assert(self.in_processing)
        append.the_lock.acquire()
        try:
            # The mergin of <script> may a raise a FireFox bug.
            txt = ''.join(self.send).replace('</script>\n<script>','')
            self.send = []
            keep_open = self.keep_open
            index = self.index
            if txt == '':
                # Remove this sender object, no more useful
                self.delete()
                return False
        finally:
            append.the_lock.release()

        try:
            # xxx.write('+' + txt + '\n')
            self.file.write(txt)

            if keep_open:
                self.file.flush()
            else:
                self.file.close()

            if index is not None:
                self.file.index = index # Successfuly wrote
        except:
            # Close on error
            try:
                if not self.file.closed:
                    self.file.close()
            except socket.error:
                try:
                    self.file.closed = True
                except AttributeError:
                    pass
            
            append.the_lock.acquire()            
            self.delete()
            append.the_lock.release()
            return False

        return True

def send_live_status(txt):
    for f in live_status:
        append(f, txt)

def add_client(f):
    global live_status
    live_status = [fi for fi in live_status if not fi.closed]
    live_status.append(f)

def send_thread(verbose=False):
    while True:
        time.sleep(0.1)
        while File.to_send:
            try:
                try:
                    # Get a file to write into
                    append.the_lock.acquire()
                    for f in File.to_send.values():
                        if not f.in_processing:
                                f.in_processing = True
                                File.nr_active_thread += 1
                                break
                    else:
                        continue # No work to do
                finally:
                    append.the_lock.release()

                # While there is content to send: continue
                while f.send_text():
                    pass
                # Now the File queue is empty, it self destroyed
            except socket.error: # A write error on a socket
                utilities.warn('Write error on %s closed=%s' % (
                    f.file, f.file.closed))

@utilities.add_a_lock
def append(f, txt, keep_open=True, index=None):
    # if not txt.startswith('GIF'): utilities.warn('%s %s %s' % (f, txt[0:20], keep_open), what='sender')
    if f is None:
        utilities.warn('f is None: ' + txt)
        return
    # xxx.write('*' + txt + '\n')
    try:
        File.to_send[f].append(txt, keep_open, index)
    except KeyError:
        File(f, txt, keep_open, index)

import re
import os

def get_stats():
    a = 100 * os.getloadavg()[0]

    try:
        f = open('/proc/diskstats', 'r')
        b = [ re.split('  *',' ' + i) for i in f.readlines() ]
        f.close()
        c = sum([ int(i[14]) for i in b if not i[3][-1].isdigit() ])
        b = c - get_stats.last_disk_usage
        get_stats.last_disk_usage = c
    except IOError:
        b = 0

    try:
        f = open('/proc/net/dev', 'r')
        j = [i.replace(':',' ') for i in f.readlines() if 'eth0' in i][0]
        f.close()
        j = re.split('  *',' ' + j)
        j = int(j[-16]) + int(j[-8])
        c = j - get_stats.last_network_usage
        get_stats.last_network_usage = j
        if c < 0:
            c = 0
    except IOError:
        c = 0
       
    return [a,b/10.,c/100000.]

get_stats.last_disk_usage = 0
get_stats.last_network_usage = 0


def live_status_send_thread():
    from . import authentication
    from . import ticket
    from . import document
    while True:
        time.sleep(2)
        send_live_status('<script>g(%s);</script>\n'% repr(get_stats()))
        send_live_status('<script>d("","N","",0.4,"%dT %dt %sr %ds %da %du", "","","");</script>\n'%(
            len(document.tables),
            len(ticket.tickets),
            len(document.request_list),
            File.nr_active_thread,
            len(authentication.authentication_requests),
            len(document.update_students),
            ))
