#!/usr/bin/python

"""
Most Timing configurations are in 'display.py'
"""

import os
import time
import socket
import display
from xnee import Xnee
import urllib2

Regtest = display.Regtest

tmp_dir = "/tmp/xxx-home"
log_dir = "/tmp/XXX"

class DiffError(ValueError):
    pass

nr_logs = 0

class Tester:
    """Launch a virtual display and an event simulator on the display.
    A web browser is launched on the display.

    The center of interest is the auto-detected BODY on the screen.
    """
    
    def __init__(self, client, output, server):
        print 'Creating tester'
        self.output = output
        self.output.write('<h1>' + client.split(' ')[0] + '</h1>\n')

        self.append_message = ''
        self.client = client
        self.display = display.Display(resolution='800x600',
                                       dump_dir = log_dir)
        self.xnee = Xnee(self.display.port)
        self.server = server
        self.start_tomuss()
        self.display.run(client % (self.display.width, self.display.height),
                         background=True, wait=True)
        # The window is now on the screen
        # self.xnee.goto(self.display.width/2,self.display.height/2)
        if 'opera' in client:
            # Accept licence
            self.check_image('opera', speed="slow", hide=True)
            self.xnee.key("Return")
            time.sleep(10)
        if 'chrom' in client:
            # Choose search engine
            self.xnee.goto(20,20)
            self.xnee.key("Tab")
            self.check_image('chrome', speed="slow", hide=True)
            self.xnee.key("Return")
            # self.wait_change()
            self.xnee.goto(10,10)
            time.sleep(1)
            self.xnee.button()
        if 'konqueror' in client:
            import collections
            self.display.no_change_interval = collections.defaultdict(
                lambda: 30)
        self.maximize_window()
        time.sleep(1)
        self.xnee.goto(1,1)
        self.goto_url('about:')
        self.check_image('start', speed='veryslow')
        print 'Tester started for', client.split(' ')[0]
        # self.display.run('export PATH="$PATH:/usr/games" ; oneko -speed 1000', background=True)

    def start_tomuss(self):
        os.system('rm -rf %s' % tmp_dir)
        os.system('rm -rf ../DBtest/Y9999')
        os.system('rm -rf ../DBtest/Y*/S*/referents.py')
        os.system('mkdir ../DBtest/Y9999 ; mkdir ../DBtest/Y9999/Sx')
        os.system('touch ../DBtest/Y9999/__init__.py ; touch ../DBtest/Y9999/Sx/__init__.py')
        os.mkdir(tmp_dir)
        
        create_write((tmp_dir, '.config', 'chromium', 'Default','Preferences'),
                     '''
                     {
                     "translate_language_blacklist": ["fr","en"],
                     "session": {
                                "restore_on_startup": 1,
                                "urls_to_restore_on_startup": [ "data:" ]
                                }
                     }

                     ''')
    

        # os.system('echo $HOME ; ls -lsa %s' % tmp_dir)
        os.system('(cd .. ; ./tomuss.py regtest >/dev/null 2>/dev/null &)')
        # Wait server start
        while True:
            try:
                time.sleep(1)
                f = urllib2.urlopen("http://%s:8888/=super.user/"%self.server)
                f.read()
                f.close()
                break
            except urllib2.URLError:
                continue

    def stop_tomuss(self):
        os.system('cd .. ; make stop')

    def maximize_window(self):
        self.xnee.goto(self.display.width/2,self.display.height/2)        
        self.xnee.key('F8')
        # self.xnee.key('F11') # don't work with chromium

    def goto_url(self, url):
        print 'goto', url
        self.display_message('URL: ' + url.replace('/', ' /'))
        self.xnee.key("l", control=True)
        time.sleep(0.1)
        self.xnee.string(url)
        # self.display.wait_end_of_change('fast')
        self.xnee.key("Return")

    def error(self, message):
        global nr_logs
        while True:
            filename = os.path.join(log_dir, '%d.ppm' % nr_logs)
            if os.path.exists(filename):
                nr_logs += 1
            else:
                break
        f = open(filename, 'w')
        f.write(self.display.last_dump)
        f.close()
        os.system('cd %s ; convert %d.ppm %d.png ; rm %d.ppm' % (
            log_dir, nr_logs,  nr_logs,  nr_logs))
        self.output.write('<a href="%d.png"><img src="%d.png" style="width:100%%">' % (nr_logs, nr_logs) +
                     '</a>\n'
                     )
        nr_logs += 1

    def display_message(self, message):
        if not message:
            return
        if message == '(C)':
            self.append_message += message
        else:
            if self.append_message:
                message = self.append_message + message
                self.append_message = ""
            self.output.write('<h3>' + message + '</h3>\n')
            self.output.flush()
    
    def is_identical(self, snapshot):
        f = open('xxx.ppm', 'w')
        f.write(self.display.last_dump)
        f.close()

        d = display.file_diff('xxx.ppm', snapshot)
        if d > display.pixel_diff_min:
            return d
        return True

    def check_image(self, filename, retry=True, speed="slow", message=None,
                    hide=False):
        print 'check_image', filename
        if message:
            self.display_message(message)
        self.image = filename # For the error message

        snapshot = os.path.join('Trash',
                                filename+'_'+self.client.split(' ')[0]+'.ppm')
        snap_png = snapshot.replace('.ppm','.png')

        if not hide:
            self.output.write(
                '<a href="%s"><img src="%s" style="width:100%%"></a>'
                % (snap_png, snap_png))

        if os.path.exists(snapshot):
            start = time.time()
            identical = True
            while self.is_identical(snapshot) is not True:
                self.display.dump()
                if time.time() - start > 30:
                    identical = self.is_identical(snapshot)
                    break               
                time.sleep(1)
        else:
            self.display.wait_end_of_change(speed)
            f = open('xxx.ppm', 'w')
            f.write(self.display.last_dump)
            f.close()
            os.system('convert xxx.ppm %s' % snap_png)
            os.rename('xxx.ppm', snapshot)
            print snapshot, 'created'
            return

        if identical is not True:
            self.error("Difference: %d" % identical)
            print snapshot, 'is not the same !!!!!!!!!!!!'
            raise DiffError('Difference')

    def stop(self):
        self.stop_tomuss()
        self.xnee.key("w", control=True)
        self.xnee.key("w", control=True)
        self.xnee.key("q", control=True)
        self.xnee.stop()
        time.sleep(5)
        self.display.stop()


def run(name, t):
    module = __import__(name)
    t.output.write("<h2>" + name + '.py</h2>')
    try:
        module.run(t)
    except Regtest:
        t.error("Unexpected Timeout: stop testing")

def do_tests(client, output, server, nb):
    output.write('<td style="vertical-align:top" width="%d%%">\n'
                 % int(100./nb))
    t = None
    try:
        t = Tester(client, output, server)
        
        run('test_home', t)
        run('test_table', t)
        
        t.stop()
        output.write('</td>\n')
        return 'ok'
    except Regtest:
        if t:
            t.stop()
        output.write('</td>\n')
        return 'bad[' + t.image + ']'
    except DiffError:
        if t:
            t.stop()
        return 'bad'

def create_open(path):
    for i in range(1, len(path)):
        try:
            os.mkdir(os.path.sep.join(path[:i]))
        except OSError:
            pass
    return open(os.path.sep.join(path), 'w')

def create_write(path, content):
    f = create_open(path)
    f.write(content)
    f.close()


if __name__ == "__main__":
    for i in ('http_proxy', 'https_proxy', 'MAIL', 'MAILCHECK'):
        if os.environ.has_key(i):
            del os.environ[i]

    os.putenv("HOME", tmp_dir)
    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)
    if not os.path.isdir('Trash'):
        os.mkdir('Trash')
    try:
        os.symlink(os.path.join(os.getcwd(), 'Trash'),
                   os.path.join(log_dir, 'Trash'))
    except OSError:
        pass
    name = os.path.join(log_dir, 'xxx.html.new')
    output = open(name, 'w')
    output.write('''
    <style>
    TABLE { background: black; border-spacing: 1 }
    TABLE TD { background: white }
    .bad { background: #F88 ; }
    H1 { text-align: center ; font-size: 150% ; }
    H2 { margin-bottom: 0px ; font-size: 100% ;
         border: 1px solid black; background: #8F8; text-align: center }
    H3 { margin-bottom: 0px ; margin-top: 0.3em ; font-size: 70% ; }
    IMG { border: 0px }
    </style>
    <table><tr>
    ''')
    print 'The log file:', name

    server = socket.getfqdn()
    if server == 'pundit.univ-lyon1.fr':
        server = '192.168.0.1'

    firefox3 = "firefox"
    iceape = None
    galeon = None
    chromium = 'chromium-browser'
    konqueror = "konqueror"
    opera = "opera"
    ie6 = None
    vnc = None

    if server == "192.168.0.*1":
        ie6 = "/home/exco/bin/ie6"
        vnc = "xtightvncviewer 192.168.0.132::3389 -encodings Raw -compresslevel 1 -nojpeg -x11cursor"

    t = []
    if chromium:
        t.append((chromium, "-width %d -height %d about:"))
    if opera:
        t.append((opera, "--geometry %dx%d-0-0 -nosession -nomail"))
    if konqueror:
        t.append((konqueror, "--geometry %dx%d-0-0"))
    if firefox3:
        t.append((firefox3, "-width %d -height %d about:"))
    if galeon:
        t.append((galeon, "-f about: about: $(echo %dx%d >/dev/null)"))
    if ie6:
        t.append((ie6, "$(echo %dx%d >/dev/null)"))
    if vnc:
        t.append((vnc, "$(echo %dx%d >/dev/null)"))
    if iceape:
        t.append((iceape, "-width %d -height %d"))

    s = '= ' # Filtered by 'forever Makefile goal
    for name, args in t:
        print '*'*79
        print '= Start testing', name
        print '*'*79
        s += name + ':' + do_tests(name + ' >/dev/null 2>&1 ' + args,
                                   output, server, len(t)) + ' '
        print 'Testing done for', name
    output.write('</tr></table>\n')

    os.rename(os.path.join(log_dir, 'xxx.html.new'),
              os.path.join(log_dir, 'xxx.html'))

    print 'Results are in %s/xxx.html' % log_dir
    print s
    import sys
    if 'bad' in s:
        sys.exit(0)
    else:
        sys.exit(0)
