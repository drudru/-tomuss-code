#!/usr/bin/python

import os
import time
import subprocess
import cgi
import sys

class Rects:
    def __init__(self, *rects):
        self.rects = rects

    def number(self, color, **k):
        return len(self.filter(color, **k))

    def __getitem__(self, n):
        return self.rects[n]

    def __str__(self):
        return str(self.rects)

    def items(self):
        return self.rects.items()

    def filter(self, x_min=None, x_max=None, y_min=None, y_max=None,
               text=None, x_left_max=None, uniq=False, sentence=None):
        t = []
        if isinstance(text, str):
            text = (text,)
        for r in self.rects:
            if x_min != None and r[0] < x_min:
                continue
            if y_min != None and r[1] < y_min:
                continue
            if x_max != None and r[0] + r[2] > x_max:
                continue
            if x_left_max != None and r[0] > x_left_max:
                continue
            if y_max != None and r[1] + r[3] > y_max:
                continue
            if text and r[4] not in text:
                continue
            if sentence != None:
                if r[4] not in sentence:
                    continue
            t.append(r)
        if sentence:
            print sentence
            print t
            if len(sentence) != len(t):
                return None
            for rect, word in zip(t, sentence):
                if rect[4] != word:
                    return None
            for i in range(len(t)-1):
                # Test if word are to spaced.
                if t[i+1][0] - (t[i][0] + t[i][2]) > 16:
                    return None
            return [t[0][0],t[0][1], t[-1][0] + t[-1][2] - t[0][0], t[0][3]]

            
        if uniq is not False:
            if uniq is None and len(t) == 0:
                return None
            if len(t) != 1:
                raise ValueError("Devrait trouver un unique <<%s>>" % text)
            return t[0]
        return t

class Display:
    check_interval = 0.2    # Number of seconds between dumps
    pixel_diff_min = 500    # Number of pixels that indicates a REAL change
    no_change_interval = 20 # If no change in this time : the changes are done
    nr_dumps = 0            # current number of dumps
    dump_dir = ''

    def __init__(self,
                 resolution="860x780", # To allow Xnest full screen
                 port=0,
                 server=("/usr/bin/Xvfb", "", "/usr/bin/Xnest")[0],
                 title=None,
                 catalogue="D",
                 ):
        self.catalogue = catalogue
        if server == '': # Real display
            self.port = port
            self.width = resolution.split('x')[0]
            self.height = resolution.split('x')[1]
            self.last_dump = ''
            self.title = title
            self.start_dumper()
            print 'Dumper created'
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
            print output
            if "Fatal server error" not in output:
                break
            port += 1

        import time ; time.sleep(1)
        print "X server runs on display :%d" % port
        self.port = port
        self.width = int(resolution.split('x')[0])
        self.height = int(resolution.split('x')[1])
        os.system("xmodmap -pke | (DISPLAY=:%d;xmodmap -)" % port)
        self.run('fvwm -f $(pwd)/fvwm.rc 2>&1 | grep -v WARNING',
                 background=True)
        self.start_dumper()

    def start_dumper(self):
        print 'Start dumper', self.port, self.catalogue
        self.dumper = subprocess.Popen(
                ('nice', './dumper', ':%d' % self.port,
                 self.catalogue),
                stdin = subprocess.PIPE,
                stdout = subprocess.PIPE,
                )
        self.dump()
        self.dump()
        self.diff()

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
        self.dumper.stdin.write('snapshot\n')
        self.dumper.stdin.flush()
        if self.dump_dir:
            self.dumper.stdin.write('save %s%sxxx.%03d.ppm\n' % (
                self.dump_dir, os.path.sep, self.nr_dumps) )

    def save(self, filename):
        self.dumper.stdin.write('save %s\n' % filename)
        self.dumper.stdin.flush()

    def diff(self, filename=None):
        if filename:
            self.dumper.stdin.write('diff %s\n' % filename)
        else:
            self.dumper.stdin.write('diff\n')
        self.dumper.stdin.flush()
        return int(self.dumper.stdout.readline())

    def store_dump(self, filename):
        self.dumper.stdin.write('save %s\n' % filename)

    def store_diff(self, filename):
        self.dumper.stdin.write('subtract %s\n' % filename)

    def rects(self):
        self.dumper.stdin.write('analyse\n')
        self.dumper.stdin.flush()
        line = self.dumper.stdout.readline()
        if False:
            f = open('xxx.analyses', 'a')
            f.write(line)
            f.close()
        try:
            return eval(line)
        except SyntaxError: # Le dumper a planter :-( XXX Pourquoi
            print 'line=(%s)' % line
            self.start_dumper()
            self.dump()
            return self.rects()

    def wait_change(self, comment="", timeout=60):
        t = time.time()
        print 'WAIT CHANGE', comment
        print '\t',
        self.dump()
        while self.diff() <= self.pixel_diff_min:
            if time.time() - t > timeout:
                return False
            sys.stdout.write('*')
            sys.stdout.flush()
            self.dump()
        print ' CHANGED !'
        return True

    def wait_end_of_change(self, wait=None, timeout=None):
        """Waits until here is no more change for 'wait' seconds
        Returns True is there is no change or False if there is timeout
        """
        if wait is None:
            wait = self.no_change_interval
        if timeout is None:
            timeout = 40
        print 'WAIT END OF CHANGE (%f seconds) ' % wait,

        start = t = time.time()
        while time.time() - t < wait:
            time.sleep(self.check_interval)
            self.dump()
            if self.diff() > self.pixel_diff_min:
                t = time.time()
            sys.stdout.write('*')
            sys.stdout.flush()
            if time.time() - start > timeout:
                sys.stdout.write('\n')
                return False # TIMEOUT
        sys.stdout.write('\n')
        return True

    def stop(self):
        self.dumper.stdin.write('quit\n')
        self.dumper.stdin.flush()
        os.kill(self.server.pid, 15)

    def html(self, zoom=1):
        s = ''
        for x, y, dx, dy, txt in self.rects():
            s += '<div style="position:absolute;background:#0F0;left:%d;top:%d;width:%d;height:%d">%s</div>\n' % (
                x*zoom, y*zoom, dx*zoom, dy*zoom, cgi.escape(txt))
        return s
    

if __name__ == "__main__":
    d = Display(server='', port=1)
    print d.rects()
    for i in d.rects().filter(x_min=382, y_min=320, x_max=500):
        print i
