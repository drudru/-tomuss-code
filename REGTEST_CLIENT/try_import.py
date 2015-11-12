#!/usr/bin/python3

"""
Try importing cell in an infinite loop in a browser in a virtual X11

If the values are not stored, the program stop with an error,
the screenshot is in xxx......png

"""

import sys
import tester
import time
import socket
import os
import pdb

year = time.localtime()[0]

# Some tweaking maybe needed to point cursor to the good place
if False:
    delta_y = 18
    delta_x = 10
else:
    delta_y = 0
    delta_x = 0

# X11
x11 = "/usr/bin/Xnest" # Interactive display on screen
x11 = "/usr/bin/Xvfb"  # X11 only in memory: not visible

t = tester.Tester("firefox -width %d -height %d", sys.stdout, socket.getfqdn(),
                  x11=x11)
t.display.pixel_diff_min = 50
try:
    print('\n=========initialize',  socket.getfqdn())
    t.initialize()
    print('\n=========goto')
    t.goto_url("http://%s:8888/=super.user/%d/Automne/demo_animaux-99" % (
        t.server, year))
    print('\n=========wait')
    t.display.wait_end_of_change(wait=1)
    print('\n=========load table database')
    f = open("/tmp/DBregtest/Y%d/SAutomne/demo_animaux-99.py" % year, "r", encoding = "utf-8")
    c = f.read()
    print('First column: CM1')
    t.xnee.goto(500, 400)
    t.xnee.button()
    print('Action TAB')
    t.xnee.goto(500, 140 - delta_y)
    t.xnee.button()
    # pdb.set_trace()
    i = 0
    while True:
        i += 1
        what = ("PRST", "INJLEAVE")[i % 2]
        print('Click on fill values in column')
        t.xnee.goto(400, 190 - delta_y)
        t.xnee.button()
        t.display.wait_end_of_change(wait=0.1)
        print('Click on input field')
        t.xnee.goto(500, 400 - delta_y)
        t.xnee.button()
        print('Enter value')
        t.xnee.string(what[0])
        print('Fill values')
        t.xnee.goto(380 - delta_x,520 - delta_y)
        t.xnee.button()
        nb_ok = 0
        for j in range(100):
            for line in f.readlines():
                if what in line:
                    nb_ok += 1
            if nb_ok == 112:
                break
            time.sleep(0.1)
        else:
            print('Store')
            t.display.dump()
            t.display.store_dump('xxx-%04d-1.png' % i)
            t.xnee.key('j', shift=True, control=True)
            time.sleep(1)
            t.display.dump()
            t.display.store_dump('xxx-%04d-2.png' % i)
            os.system("ps -fle | grep python")
            os.system("ps -fle | grep firefox")
            print('check problems with the running server.')
            print('Type ^C to stop it')
            time.sleep(1000000)

        print('OK')
        
finally:
    t.stop()
