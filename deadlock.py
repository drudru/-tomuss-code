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

"""
To activate deadlock check, call before any lock creation :

         start_check_deadlock()
"""


import threading

origLock = None

class Lock(object):
    my_lock = threading.Lock()
    lock_stacks = {}                    # Key : Thread, Item : heap of Lock
    all_the_locks = []

    def __init__(self, name=''):
        self.lock = origLock()
        self.locked_after = {}
        self.all_the_locks.append(self)
        self.name = name
        
    def acquire(self, *args):
        # print('ACQUIRE', self)
        self.my_lock.acquire()
        t = threading.currentThread()
        if t in self.lock_stacks:
            lock_stack = self.lock_stacks[t]
        else:
            lock_stack = self.lock_stacks[t] = []
            
        for lock in lock_stack:
            if self is not lock:
                self.locked_after[lock] = True
                if self in lock.locked_after:
                    print('SELF:', self)
                    print('LOCK:', lock)
                    self.debug()
                    raise ValueError("Possible deadlock")
            
        lock_stack.append(self)
        self.my_lock.release()
        return self.lock.acquire(*args)

    def release(self):
        # print('RELEASE', self)
        self.my_lock.acquire()
        self.lock_stacks[threading.currentThread()].pop()
        self.my_lock.release()
        self.lock.release()

    def locked(self):
        return self.lock.locked()

    def debug(self):
        import pprint
        print('=============================== lock stacks:')
        print(pprint.pformat(self.lock_stacks))
        print('=============================== the locks:')
        for i in self.all_the_locks:
            print('LOCK:', i, 'IS LOCKED AFTER:')
            print(pprint.pformat(i.locked_after))

    def __repr__(self):
        if self.name:
            return self.name
        else:
            return repr(self.lock)


def start_check_deadlock():
    global origLock
    origLock = threading.Lock
    threading.Lock = Lock


if __name__ == "__main__":
    start_check_deadlock()
    l1 = threading.Lock('L1')
    l2 = threading.Lock('L2')

    class T1(threading.Thread):
        def run(self):
            l1.acquire()
            l1.release()
            l2.acquire()
            l2.release()

    class T2(threading.Thread):
        def run(self):
            l2.acquire()
            l2.release()
            l1.acquire()
            l1.release()

    class T3(threading.Thread):
        def run(self):
            l1.acquire()
            l2.acquire()
            l2.release()
            l1.release()

    class T4(threading.Thread):
        def run(self):
            try:
                l2.acquire()
                l1.acquire()
                l1.release()
                l2.release()
                print('Test3 is BAD: No exception launched')
            except ValueError:
                print('Test3 is fine: exception launched')
                raise

    t1 = T1()
    t1.start()
    t2 = T2()
    t2.start()
    t1.join()
    t2.join()
    print('Test1 is fine: No exception launched')
    t3 = T3()
    t3.start()
    t3.join()
    print('Test2 is fine: No exception launched')
    assert(len(l1.locked_after) == 0)
    assert(len(l2.locked_after) == 1)
    t4 = T4()
    t4.start()
    t4.join()
            
        
