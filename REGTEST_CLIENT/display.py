#!/usr/bin/python

import os
import time
import subprocess
import collections

check_interval = 1         # Number of seconds between dumps
pixel_diff_min = 500       # Number of pixel that idicates a REAL screen change
no_change_interval = 7     # If no change in this time : the changes are done

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
                 dump_dir = None,
                 ):
        self.dumps_diff = []
        self.nr_dumps = 0
        self.last_dump = None
        self.dump_dir = dump_dir
        self.no_change_interval = collections.defaultdict(
            lambda: no_change_interval)
        if server == '': # Real display
            self.port = 0
            self.width = 1280
            self.height = 1024
            self.last_dump = ''
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

    def dump(self):
        self.nr_dumps += 1
        old_dump = self.last_dump
        if self.dump_dir:
            dump_dir =  '| tee %s%sxxx.%03d.ppm' % (
                self.dump_dir, os.path.sep, self.nr_dumps)
        else:
            dump_dir = ''
        self.last_dump = self.run(
            """(xwd -silent -root -screen || (sleep 1 ; xwd -silent -root -screen) ) |
            convert xwd:- ppm:- 2>/dev/null""" + dump_dir,
            return_stdout=True)
        if old_dump is None:
            self.dumps_diff.append(0)
        else:
            self.dumps_diff.append(diff(old_dump, self.last_dump))
        print '\tdump[%d] diff=%d' % (self.nr_dumps,  self.dumps_diff[-1])
        
        return self.last_dump

    def display(self):
        display(self.dump())

    def wait_change(self, comment="", timeout=60):
        t = time.time()
        print 'WAIT CHANGE', comment
        while True:
            self.dump()
            if self.dumps_diff[-1] > pixel_diff_min: # Small changes
                break
            if time.time() - t > timeout:
                raise Regtest('Timeout')
            time.sleep(check_interval)
        print '\tCHANGED !'

    def wait_end_of_change(self, speed):
        """Returns the number of seconds of changes"""
        print 'WAIT END OF CHANGE (%f seconds) "%s"' % (
            self.no_change_interval[speed], speed)

        t = start = time.time()        
        while time.time() - start < self.no_change_interval[speed]:
            time.sleep(check_interval)
            self.dump()
            if self.dumps_diff[-1] > pixel_diff_min:
                t = time.time()
        print 'Last change:', t - start
        self.no_change_interval[speed] = check_interval + 1.5*(t - start)

    def stop(self):
        os.kill(self.server.pid, 15)


if __name__ == "__main__":
    d = Display()
    d.display()
    
