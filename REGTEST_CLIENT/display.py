#!/usr/bin/python

import os
import time
import subprocess
import collections

check_interval = 0.5       # Number of seconds between dumps
pixel_diff_min = 500       # Number of pixel that idicates a REAL screen change
no_change_interval = 7     # If no change in this time : the changes are done

class Regtest(ValueError):
    pass

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
        self.no_change_interval = no_change_interval
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

        print 'Start dumper'
        self.dumper = subprocess.Popen(
                ('./dumper', ':%d' % port),
                stdin = subprocess.PIPE,
                stdout = subprocess.PIPE,
                )
        self.dumper.stdin.write('diff\n')
        self.dumper.stdin.flush()
        self.dumper.stdout.readline()

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
        if self.dump_dir:
            self.dumper.stdin.write('save %s%sxxx.%03d.ppm\n' % (
                self.dump_dir, os.path.sep, self.nr_dumps) )
        self.dumper.stdin.write('diff\n')
        self.dumper.stdin.flush()
        d = self.dumper.stdout.readline()
        self.dumps_diff.append(int(d))
        print '\tdump[%d] diff=%d' % (self.nr_dumps,  self.dumps_diff[-1])

    def store_dump(self, filename):
        self.dumper.stdin.write('save %s\n' % filename)

    def store_diff(self, filename):
        self.dumper.stdin.write('subtract %s\n' % filename)

    def diff(self, filename):
        self.dumper.stdin.write('diff %s\n' % filename)
        return int(self.dumper.stdout.readline())

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

    def wait_end_of_change(self, wait=None, timeout=None):
        """Waits until here is no more change for 'wait' seconds
        Returns True is there is no change or False if there is timeout
        """
        if wait is None:
            wait = self.no_change_interval
        if timeout is None:
            timeout = 40
        print 'WAIT END OF CHANGE (%f seconds)' % wait

        start = t = time.time()
        while time.time() - t < wait:
            time.sleep(check_interval)
            self.dump()
            if self.dumps_diff[-1] > pixel_diff_min:
                t = time.time()
            if time.time() - start > timeout:
                return False # TIMEOUT
        return True

    def stop(self):
        self.dumper.stdin.write('quit\n')
        self.dumper.stdin.flush()
        os.kill(self.server.pid, 15)


if __name__ == "__main__":
    d = Display()
    d.display()
    
