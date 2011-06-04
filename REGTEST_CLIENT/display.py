#!/usr/bin/python

import os
import time
import subprocess

check_interval = 3         # Number of seconds between to wait_change check
pixel_diff_min = 500       # Number of pixel that idicates a REAL screen change
no_change_interval = 3   # Number of seconds to wait for a modification

class Regtest(ValueError):
    pass

def display(image):
    f = os.popen("display -", 'w')
    f.write(image)
    f.close()

def diff(a, b):
    if a == b:
        return 0
    i = len(a) // 2
    if i:
        nb = diff(a[:i], b[:i])
        if nb > 1000:
            return 1000
        return nb + diff(a[i:], b[i:])
    return 1

def file_diff(a, b):
    f = open(a, 'r')
    a = f.read()
    f.close()
    f = open(b, 'r')
    b = f.read()
    f.close()
    return diff(a, b)

class Display:
    def __init__(self,
                 resolution="1200x1000", # To allow Xnest full screen
                 port=0,
                 server=("/usr/bin/Xvfb", "", "/usr/bin/Xnest")[0],
                 ):
        self.nr_dumps = 0
        if server == '': # Real display
            self.port = 0
            self.width = 1280
            self.height = 1024
            self.last_dump = ''
            self.clip = (0, 0, self.width-1, self.height-1)
            return
        
        while True:
            if 'Xvfb' in server:
                options = (server, ':%d' % port, '-ac', '-noreset',
                           '-screen', '0', '%sx24' % resolution)
            else:
                options = (server, ':%d' % port, '-ac', '-noreset',
                           '-geometry', '%s' % resolution)
            self.server = subprocess.Popen(
                options,
                stdin = None,
                stdout = subprocess.PIPE,
                stderr = subprocess.STDOUT,
                )

            output = self.server.stdout.read(80)
            # print output
            if "Fatal server error" not in output:
                break
            port += 1

        # import time ; time.sleep(10)
        print "X server runs on display :%d" % port
        self.port = port
        self.width = int(resolution.split('x')[0])
        self.height = int(resolution.split('x')[1])
        self.clip = (0, 0, self.width-1, self.height-1)
        self.clips = []
        self.run('fvwm -f $(pwd)/fvwm.rc 2>&1 | grep -v WARNING',
                 background=True)
        self.dump()

    def run(self, command, return_stdout=False, background=False, wait=False):
        c = "export DISPLAY=:%d ; %s" % (self.port, command)
        if background:
            c += ' &'
        if return_stdout:
            f = os.popen(c, 'r')
            image = f.read()
            f.close()
            return image
        os.system(c)
        if wait:
            self.wait_change("command: " + command)

    def set_clip(self, t):
        self.clips.append(self.clip)
        self.clip = (t[0], t[1], t[0]+t[2]-1, t[1]+t[3]-1)

    def pop_clip(self):
        self.clip = self.clips.pop()

    def dump(self):
        self.nr_dumps += 1
        self.last_dump = self.run(
            """(xwd -silent -root -screen || (sleep 1 ; xwd -silent -root -screen) ) |
            convert xwd:- ppm:- 2>/dev/null |
            pnmcut -left %d -top %d -right %d -bottom %d""" % self.clip,
            return_stdout=True)
        return self.last_dump

    def display(self):
        display(self.dump())

    def wait_change(self, comment="", timeout=60):
        last_dump = self.last_dump
        t = time.time()
        print 'WAIT CHANGE'
        while True:
            d = diff(last_dump, self.dump())
            if d > pixel_diff_min: # Small changes
                break
            if time.time() - t > timeout:
                raise Regtest('Timeout')
            print '\twait dump=', self.nr_dumps, comment
            time.sleep(check_interval)
        print '\tdump', self.nr_dumps, 'changed ! nr bytes changed:', d
            

    def wait_end_of_change(self):
        v = self.last_dump
        t = time.time()
        time.sleep(self.no_change_interval)
        print 'WAIT END OF CHANGE'
        while True:
            d = diff(self.dump(), v)
            if d <= pixel_diff_min:
                break
            print '\tA display change :', d, 'bytes, dump=', self.nr_dumps, time.time() - t
            time.sleep(self.no_change_interval)
            v = self.last_dump
            if time.time() - t > 60:
                self.error('TIMEOUT end of change')
                raise Regtest('Timeout')
        print '\tdump', self.nr_dumps, 'unchanged'
        return self.last_dump

    def stop(self):
        os.kill(self.server.pid, 15)


if __name__ == "__main__":
    d = Display()
    d.display()
    
