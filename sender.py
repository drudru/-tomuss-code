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

# All data structure are lock protected.

import time
import utilities
import socket

live_status = []

class File(object):
    nr_active_thread = 0
    to_send = {}

    def __init__(self, f, txt, keep_open):
        assert(append.the_lock.locked())
        self.file = f
        File.to_send[f] = self
        self.send = [txt]
        self.keep_open = keep_open
        self.in_processing = False
        
    def append(self, txt, keep_open):
        assert(append.the_lock.locked())
        if self.keep_open is False:
            raise ValueError('Append to a closed file')
        self.send.append(txt)
        self.keep_open = keep_open

    def send_text(self):
        """Return True if a text is sent"""
        assert(self.in_processing)
        append.the_lock.acquire()
        try:
            # Next line raise FireFox bug : (start buffering on many changes)
            # txt = ''.join(self.send).replace('</script><script>','')
            txt = ''.join(self.send)
            self.send = []
            keep_open = self.keep_open
            if txt == '':
                # Now another thread can take job for
                # this file because all write are done
                self.in_processing = False
                File.nr_active_thread -= 1
                return False
        finally:
            append.the_lock.release()

        try:
            self.file.write(txt)

            if keep_open:
                self.file.flush()
            else:
                self.file.close()
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
            self.in_processing = False
            File.nr_active_thread -= 1
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
                # Get a file to write into
                append.the_lock.acquire()
                try:
                    while True: # Stopped by Exception on pop
                        fil, f = File.to_send.popitem()
                        if not f.in_processing:
                            f.in_processing = True
                            File.nr_active_thread += 1
                            break
                        # If 'in_processing' is True
                        # IT MUST BE processed by its thread.
                        # So pop another one
                finally:
                    append.the_lock.release()
                # If here : no exception on pop
                # While the file must be wrote, continue
                while f.send_text():
                    pass
            except socket.error: # A write error on a socket
                utilities.warn('Write error on %s closed=%s' % (
                    f.file, f.file.closed))
            except KeyError: # To thread trying the popitem()
                utilities.warn('Bad pop')
                pass
@utilities.add_a_lock
def append(f, txt, keep_open=True):
    # if not txt.startswith('GIF'): utilities.warn('%s %s %s' % (f, txt[0:20], keep_open), what='sender')
    if f is None:
        utilities.warn('f is None: ' + txt)
        return
    try:
        File.to_send[f].append(txt, keep_open)
    except KeyError:
        File(f, txt, keep_open)

import re

def get_stats():
    f = open('/proc/loadavg', 'r')
    a = 100*float(f.read().split(' ')[0])
    f.close()

    f = open('/proc/diskstats', 'r')
    b = [ re.split('  *',' ' + i) for i in f.readlines() ]
    f.close()
    c = sum([ int(i[14]) for i in b if not i[3][-1].isdigit() ])
    b = c - get_stats.last_disk_usage
    get_stats.last_disk_usage = c

    f = open('/proc/net/dev', 'r')
    j = [i.replace(':',' ') for i in f.readlines() if 'eth0' in i][0]
    f.close()
    j = re.split('  *',' ' + j)
    j = int(j[-16]) + int(j[-8])
    c = j - get_stats.last_network_usage
    get_stats.last_network_usage = j
    if c < 0:
        c = 0
       
    return [a,b/10.,c/100000.]

get_stats.last_disk_usage = 0
get_stats.last_network_usage = 0


def live_status_send_thread():
    import authentication
    import ticket
    import document
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
