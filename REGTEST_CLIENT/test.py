#!/usr/bin/python

"""
Most Timing configurations are in 'display.py'
"""

# TODO : more tests

import sys
import os
import time
import socket
import dumper
from xnee import Xnee
import urllib2
import shutil
import glob

class Regtest(Exception):
    pass

tomuss_dir = '..'
trash = 'Trash'
tmp_dir = "/tmp/xxx-home"
log_dir = "/tmp/XXX"
retry = 1
continue_on_error = False

password = "your rdesktop password"

def rmdir(pattern):
    for i in glob.glob(pattern):
        try:
            shutil.rmtree(i)
        except OSError:
            pass
        if os.path.exists(i):
            print i + ' deletion failed, move it.'
            rmdir(i + '~')
            print 'rename', i, 'to', i + '~'
            os.rename(i, i + '~')
        if os.path.exists(i):
            print 'BUG'

class Tester:
    """Launch a virtual display and an event simulator on the display.
    A web browser is launched on the display.

    The center of interest is the auto-detected BODY on the screen.
    """
    
    def __init__(self, client, output, server):
        print 'Creating tester'
        self.client = client
        self.client_name = self.client.split(' ')[0]
        self.server = server
        self.output = output
        self.output.write('<h1>' + self.client_name + '</h1>\n')

        self.errors = []
        self.display = dumper.Display(resolution='800x600')
        self.xnee = Xnee(self.display.port)
        self.start_tomuss()
        self.display.run(client % (self.display.width, self.display.height),
                         background=True, wait=True)

    def initialize(self):
        # The window is now on the screen
        # self.xnee.goto(self.display.width/2,self.display.height/2)
        if 'epiphany' in self.client:
            time.sleep(1)
            self.xnee.key("Escape") # Recover window question
            time.sleep(1)
        if 'opera' in self.client:
            # Accept licence
            self.check_image('opera', hide=True)
            self.xnee.key("Return")
            time.sleep(12)
        if 'chrom' in self.client:
            # Choose search engine
            self.xnee.goto(20,20)
            self.xnee.key("Tab")
            self.check_image('chrome', hide=True)
            self.xnee.key("Return")
            time.sleep(4) # Wait tip
            self.xnee.button() # Make tip go away
            time.sleep(4) # Wait tip away
        if 'konqueror' in self.client:
            self.display.no_change_interval = 30
        if 'rdesktop' in self.client:
            time.sleep(1) # Login time...
            self.check_image('login', hide=True)
            self.xnee.string(password)
            self.xnee.key('Return')
            time.sleep(10) # Login time...
        time.sleep(1)
        self.maximize_window()
        self.xnee.goto(5,5)
        self.xnee.key("Escape") # Remove any visible popup
        self.goto_url('about:')
        time.sleep(10)
        self.xnee.key("Escape") # Remove any visible popup
        self.check_image('start')
        print 'Tester started for', self.client_name

    def start_tomuss(self):
        rmdir(tmp_dir)
        rmdir(tomuss_dir + '/DBregtest')
        for i in ('DBregtest', 'DBregtest/Y9999',
                  'DBregtest/Y9999/STest', 'LOGS', 'LOGS/TOMUSS'):
            try:
                os.mkdir(tomuss_dir + '/' + i)
            except OSError:
                pass
            open(tomuss_dir + '/' + i + '/__init__.py', 'w').close()

        try:
            os.mkdir(tmp_dir)
        except OSError:
            print 'BEWARE: a running program held a file in ', tmp_dir

        snapdir = os.path.join(trash, self.client_name)
        if not os.path.isdir(snapdir):
            os.mkdir(snapdir)
        
        create_write((tmp_dir, '.config', 'chromium', 'Default','Preferences'),
                     '''
                     {
                     "translate_language_blacklist": ["fr","en"],
                     "session": {
                                "restore_on_startup": 4,
                                "urls_to_restore_on_startup": [ "data:" ]
                                }
                     }

                     ''')

        os.system('gconftool-2 --set /apps/epiphany/general/show_toolbars '
                  + '--type bool "0"')

        # os.system('echo $HOME ; ls -lsa %s' % tmp_dir)
        os.system('(cd %s ; ./tomuss.py regtest >/dev/null 2>&1 &)' %
                  tomuss_dir)
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
        print 'Stop tomuss'
        f = urllib2.urlopen("http://%s:8888/stop" % self.server)
        assert('stopped' in f.read())
        f.close()

    def maximize_window(self):
        time.sleep(1)
        self.xnee.goto(self.display.width/2, self.display.height/2)        
        self.xnee.key('F8')
        time.sleep(1)
        # self.xnee.key('F11') # don't work with chromium

    def goto_url(self, url):
        print 'goto', url
        self.display_message('URL: <a href="' + url + '">'
                             + url.replace('/', ' /') + '</a>')
        self.xnee.key("l", control=True)
        time.sleep(0.1)
        self.xnee.string(url)
        # self.display.wait_end_of_change('fast')
        self.xnee.key("Return")

    def error(self, message, image):
        filename = os.path.join(log_dir,
                                '%s-%s-diff.png' % (self.client_name, message))
        self.display.store_diff(filename)

        imagename = os.path.join('Trash', self.client_name, image + '.bug.png')
        self.display.store_dump(imagename)
        
        self.output.write(
            '<span class="bad">'
            + message
            + '</span><br>'
            + '<a href="%s"><img src="%s"></a>' % (
                imagename, imagename)
            + '<a href="%s"><img src="%s"></a>' % (
                filename, filename)
            )

    def display_message(self, message):
        if not message:
            return
        self.output.write('<h3>' + message + '</h3>\n')
        self.output.flush()
    
    def is_identical(self, snapshot):
        d = self.display.diff(snapshot)
        if d > self.display.pixel_diff_min:
            return d
        return True

    def check_image(self, filename, retry=True, message=None,
                    hide=False, wait=None, timeout=40):
        print 'check_image', filename
        if message:
            self.display_message(message)

        snapshot = os.path.join(trash, self.client_name, filename + '.png')

        if os.path.exists(snapshot):
            start = time.time()
            identical = True
            escaped = False
            while self.is_identical(snapshot) is not True:
                self.display.dump()
                sys.stdout.flush()
                if not escaped and time.time() - start > timeout - 2:
                    print 'Escape !'
                    self.xnee.key('Escape') # Epiphany bug ?
                    escaped = True
                if time.time() - start > timeout:
                    identical = self.is_identical(snapshot)
                    break               
                time.sleep(1)
        else:
            if self.display.wait_end_of_change(wait=wait) is False:
                print 'Escape !'
                self.xnee.key('Escape') # Epiphany bug ?
                self.display.wait_end_of_change(wait=1)
            
            self.display.store_dump(snapshot)
            print snapshot, 'created'
            identical = True

        if not hide:
            self.output.write(
                '<a href="%s"><img src="%s" style="width:100%%"></a>'
                % (snapshot, snapshot))

        if identical is not True:
            self.error("%s{%d}" % (filename, identical), filename)
            print snapshot, 'is not the same !!!!!!!!!!!!'
            self.errors.append(filename)
            if not continue_on_error:
                raise Regtest('Difference')

    def stop(self):
        print 'Stop test for this browser'
        self.stop_tomuss()
        self.xnee.key("w", control=True)
        time.sleep(0.2)
        self.xnee.key("w", control=True)
        time.sleep(0.2)
        self.xnee.key("w", control=True)
        time.sleep(0.2)
        self.xnee.key("q", control=True)
        self.xnee.stop()
        time.sleep(5)
        self.display.stop()


def run(name, t):
    module = __import__(name)
    t.output.write("<h2>" + name + '.py</h2>')
    module.run(t)

def do_tests(client, output, server, nb):
    output.write('<td style="vertical-align:top" width="%d%%">\n'
                 % int(100./nb))
    start = time.time()
    t = Tester(client, output, server)
    m = '?BUG?'
    try:
        try:
            t.initialize()

            run('test_home', t)
            run('test_table', t)
            run('test_popup', t)
        except Regtest:
            pass
        if t.errors:
            m = '***bad[' + ' '.join(t.errors) + ']***'
        else:
            m = 'ok'
    finally:
        if t:
            t.stop()

    m = t.client_name + ':' + m + '(%ds) ' % (time.time() - start)
    output.write(m + '</td>\n')
    
    return m

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
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == '--tomuss_dir':
            i += 1
            tomuss_dir = sys.argv[i]
        elif arg == '--trash':
            i += 1
            trash = sys.argv[i]
        elif arg == '--retry':
            i += 1
            retry = int(sys.argv[i])
        elif arg == '--continue-on-error':
            continue_on_error = True
        else:
            raise ValueError("Unknown arg: " + arg)
        i += 1

    start = time.time()
    
    for i in ('http_proxy', 'https_proxy', 'MAIL', 'MAILCHECK'):
        if os.environ.has_key(i):
            del os.environ[i]

    os.environ["HOME"] = tmp_dir

    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)
    if not os.path.isdir(trash):
        os.mkdir(trash)
    try:
        os.symlink(os.path.join(os.getcwd(), trash),
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
    H1 { text-align: center ; font-size: 70% ; }
    H2 { margin-bottom: 0px ; font-size: 70% ;
         border: 1px solid black; background: #8F8; text-align: center }
    H3 { margin-bottom: 0px ; margin-top: 0.3em ; font-size: 70% ; }
    IMG { border: 0px; width: 100% }
    </style>
    <table><tr>
    ''')
    print 'The log file:', name

    server = socket.getfqdn()
    if server == 'pundit.univ-lyon1.fr':
        server = '192.168.0.1'

    firefox3 = "firefox"
    iceape = None
    epiphany = "epiphany"
    chromium = 'chromium-browser'
    konqueror = "konqueror"
    konqueror = None
    opera = "opera"
    ie6 = None
    vnc = None
    ie = None

    ## epiphany = firefox3 = opera = None ##

    if password != "your rdesktop password":
        ie = "rdesktop sa1cs.univ-lyon1.fr -u thierry.excoffier -d UNIV-LYON1  -f -s 'C:/Program Files/Internet Explorer/iexplore.exe http://www.univ-lyon1.fr'"

    t = []
    if epiphany:
        t.append((epiphany, "$(echo %dx%d >/dev/null)"))
    if ie:
        t.append((ie, "$(echo %dx%d >/dev/null)"))
    if konqueror:
        t.append((konqueror, "--geometry %dx%d-0-0"))
    if chromium:
        t.append((chromium, "-width %d -height %d"))
    if opera:
        t.append((opera, "--geometry %dx%d-0-0 -nosession -nomail"))
    if firefox3:
        t.append((firefox3, "-width %d -height %d about:"))
    if ie6:
        t.append((ie6, "$(echo %dx%d >/dev/null)"))
    if vnc:
        t.append((vnc, "$(echo %dx%d >/dev/null)"))
    if iceape:
        t.append((iceape, "-width %d -height %d"))

    s = '= ' # Filtered by 'forever Makefile goal
    ok = True
    for name, args in t:
        for i in range(retry):
            print '*'*79
            print '= Start testing', name
            print '*'*79
            m = do_tests(name+' >/dev/null 2>&1 ' + args,
                         output, server, len(t))
            print 'Testing done for', name
            print '=', m
            s += m
            if ':ok' in m:
                break
        else:
            ok = False
    output.write('</tr></table>\n')

    os.rename(os.path.join(log_dir, 'xxx.html.new'),
              os.path.join(log_dir, 'xxx.html'))

    print 'Results are in %s/xxx.html' % log_dir
    print s
    print '= Runtime: %.1f' % ((time.time() - start)/60), 'minutes'
    if ok:
        print 'REGTESTSOK'
        sys.exit(0)
    else:
        print 'REGTESTSBAD'
        sys.exit(1)
