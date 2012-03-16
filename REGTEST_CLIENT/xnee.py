#!/usr/bin/python

import os
import time
import modmap
import subprocess

class Xnee:
    def __init__(self, port=0):
        """The port is the X11 port (0 by default)"""
        print 'xnee start on display', port
        for xnee in ('cnee', 'xnee'):
            f = os.popen('%s --help 2>&1 ; %s --version 2>&1' % (xnee,xnee),
                         'r')
            c = f.read()
            f.close()
            if 'OPTIONS' in c:
                break

        o = []
        if '--no-resolution-adjustment' in c:
            o.append('--no-resolution-adjustment')

        print 'xnee version:', xnee
            
        self.keys = modmap.init(port)
        print 'modmap read'

        if 'Alt_L' not in self.keys:
            os.system('''xmodmap -display :%d -e "keycode 64 = Alt_L" \
                                              -e "clear mod1" \
                                              -e "add mod1 = Alt_L"
                      ''' % port)
            self.keys = modmap.init(port)

        if 'BackSpace' not in self.keys:
            os.system('''xmodmap -display :%d -e "keycode 22 = BackSpace"
                      ''' % port)
            self.keys = modmap.init(port)

        if 'a' not in self.keys:
            c = 'xmodmap -display :%d' % port
            for a in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                c += ' -e "keycode %d = %s %s"' % (
                    self.keys[a][0], a, a.lower())
            os.system(c)
            self.keys = modmap.init(port)


        print 'run xnee'
        self.process = subprocess.Popen([xnee,
                                         '--display',
                                         '127.0.0.1:%d' % port,
                                         '--replay'] + o,
                                        stdin = subprocess.PIPE,
         # env = { 'DISPLAY': '127.0.0.1:%d' % port },
                                        )
        self.counter = 1000
        self.x = 501
        self.y = 502

        if xnee == 'xnee':
            self.key('a') # To turn around an old xnee bug (unbutu 6.10)

        print xnee, 'is running'

        # self.file.write("# Xnee version:           1.08\n")
        # os.system('export DISPLAY=:%d ; xmodmap -pk ; xmodmap -pm' % port)
        
    def send(self, data):
        v = "%s,0,%d\n" % (data, self.counter)
        self.process.stdin.write(v)
        self.process.stdin.flush()
        self.counter += 10

    def goto(self, x, y):
        self.x = x
        self.y = y
        self.send("0,6,%d,%d,0,0" %(x+5,y+5))
        self.send("0,6,%d,%d,0,0" %(x-5,y-5))
        self.send("0,6,%d,%d,0,0" %(x,y))

    def keypress(self, key):
        k = self.keys[key]
        if k[1]:
            self.keypress("Shift_L")
        self.send("0,2,0,0,0,%d" % k[0])
        time.sleep(0.05) # To avoid buffer overflow

    def keyrelease(self, key):
        k = self.keys[key]
        self.send("0,3,0,0,0,%d" % k[0])
        if k[1]:
            self.keyrelease("Shift_L")

    def key(self, key, control=False, alt=False):
        if control:
            self.keypress("Control_L")
        if alt:
            self.keypress("Alt_L")
        self.keypress(key)
        self.keyrelease(key)
        if alt:
            self.keyrelease("Alt_L")
        if control:
            self.keyrelease("Control_L")

    def button_press(self, button=1):
        self.send("0,4,0,0,%d,0" % button)

    def button_release(self, button=1):
        self.send("0,5,0,0,%d,0" % button)

    def button(self, button=1):
        time.sleep(0.1)
        self.button_press(button)
        self.button_release(button)
        time.sleep(0.1)

    def double_button(self, button=1):
        self.button_press(button)
        self.button_release(button)
        self.button_press(button)
        self.button_release(button)

    def string(self, string):
        for s in string:
            self.key(s)

    def stop(self):
        os.kill(self.process.pid, 15)

if __name__ == "__main__":
    import sys

    if '1' in sys.argv:
        x = Xnee(1)
    elif '2' in sys.argv:
        x = Xnee(2)
    else:
        x = Xnee(0)

    if 'g50' in sys.argv:
        x.goto(50,50)
    if 'g500' in sys.argv:
        x.goto(500,500)
    if 'g100' in sys.argv:
        x.goto(100,100)
    if 'g200' in sys.argv:
        x.goto(200,200)

    if 'b1' in sys.argv:
        x.button(1)
    if 'b1p' in sys.argv:
        x.button_press(1)
    if 'b1r' in sys.argv:
        x.button_release(1)
    if 'b2' in sys.argv:
        x.button(2)
    if 'b3' in sys.argv:
        x.button(3)

    if 'f1' in sys.argv:
        x.key("F1")
    if 'l' in sys.argv:
        x.key("l", control=True)
    if 'r' in sys.argv:
        x.key("Return")

    time.sleep(1)
    x.stop()
    
