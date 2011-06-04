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

goto_url_time = 5 # Number of seconds to load an URL

class DiffError(ValueError):
    pass

nr_logs = 0

class Tester:
    """Launch a virtual display and an event simulator on the display.
    A web browser is launched on the display.

    The center of interest is the auto-detected BODY on the screen.
    """
    
    def __init__(self, client, output, server, no_change_interval=0.55):
        print 'Creating tester'
        self.output = output
        self.output.write('<h1>' + client.split(' ')[0] + '</h1>\n')

        self.append_message = ''
        self.client = client
        self.display = display.Display(resolution='800x600')
        self.xnee = Xnee(self.display.port)
        self.server = server
        self.start_tomuss()
        self.display.no_change_interval = no_change_interval
        self.display.run(client % (self.display.width, self.display.height),
                         background=True, wait=True)
        # The window is now on the screen
        # self.xnee.goto(self.display.width/2,self.display.height/2)
        if 'opera' in client:
            # Accept licence
            self.xnee.key("Return")
            self.wait_change('Licence')
        if 'chrom' in client:
            # Choose search engine
            self.xnee.goto(20,20)
            self.xnee.key("Tab")
            self.xnee.key("Return")
            self.wait_change('Search engine choice')
            self.xnee.goto(10,10)
            time.sleep(1)
            self.xnee.button()

        self.maximize_window()
        print 'Tester started for', client.split(' ')[0]
        # self.display.run('export PATH="$PATH:/usr/games" ; oneko -speed 1000', background=True)

    def start_tomuss(self):
        os.system('rm -rf %s' % tmp_dir)
        os.system('rm -rf ../DBtest/Y9999')
        os.system('rm -rf ../DBtest/Y*/S*/referents.py')
        os.system('mkdir ../DBtest/Y9999 ; mkdir ../DBtest/Y9999/Sx')
        os.system('touch ../DBtest/Y9999/__init__.py ; touch ../DBtest/Y9999/Sx/__init__.py')
        os.mkdir(tmp_dir)
        # os.system('echo $HOME ; ls -lsa %s' % tmp_dir)
        os.system('(cd .. ; ./tomuss.py regtest >/dev/null 2>/dev/null &)')
        # Wait server start
        time.sleep(1)
        f = urllib2.urlopen("http://%s:8888/=super.user/" % self.server)
        f.read()
        f.close()

    def stop_tomuss(self):
        os.system('cd .. ; make stop')

    def maximize_window(self):
        self.xnee.goto(self.display.width/2,self.display.height/2)        
        self.xnee.key('F8')
        # self.xnee.key('F11') # don't work with chromium
        self.display.wait_end_of_change()

    def goto_url(self, url):
        print 'goto', url
        self.xnee.goto(10,10)
        self.xnee.key("l", control=True)
        self.xnee.string(url)
        self.display.wait_end_of_change()
        self.xnee.key("Return")
        time.sleep(goto_url_time) # Assumes that most the page is on screen
        self.display.dump() # Get the screen with 'loading' message

        self.display.wait_end_of_change()
        print 'goto', url, 'done'
        self.display_message('URL: ' + url.replace('/', ' /'))

    def error(self, message):
        global nr_logs
        f = open(os.path.join(log_dir, '%d.ppm' % nr_logs), 'w')
        f.write(self.display.last_dump)
        f.close()
        os.system('cd %s ; convert %d.ppm %d.png ; rm %d.ppm' % (
            log_dir, nr_logs,  nr_logs,  nr_logs))
        self.output.write('<span class="bad">BAD: ' + message + '</span><br>'
                     '<a href="%d.png"><img src="%d.png" style="width:100%%">' % (nr_logs, nr_logs) +
                     '</a>]\n'
                     )
        nr_logs += 1

    def good(self, a, message):
        if a:
            self.output.write('OK: ' + message + '<br>\n')
        else:
            print 'BAD', message
            self.error(message)
        self.output.flush()
        return a

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
    
    def wait_change(self, message):
        self.display_message(message)
        self.display.wait_change(message)
        return self.display.wait_end_of_change()

    def check_image(self, filename):
        f = open('xxx.ppm', 'w')
        f.write(self.display.last_dump)
        f.close()
        snapshot = os.path.join('Trash',
                                filename+'_'+self.client.split(' ')[0]+'.ppm')
        if os.path.exists(snapshot):
            d = display.file_diff('xxx.ppm', snapshot)
            if d > display.pixel_diff_min:
                os.rename('xxx.ppm', snapshot.replace('.ppm','.bug.ppm'))
                self.error("Difference: %d" % d)
                print snapshot, 'is not the same !!!!!!!!!!!!'
                raise DiffError('Difference')
            print snapshot, 'is identical'
            return

        os.rename('xxx.ppm', snapshot)
        print snapshot, 'created'
            

    def stop(self):
        self.stop_tomuss()
        self.xnee.key("w", control=True)
        self.xnee.key("w", control=True)
        self.xnee.key("q", control=True)
        self.xnee.stop()
        time.sleep(1)
        os.system('ps -l')
        self.display.stop()


def run(name, t):
    module = __import__(name)
    t.output.write("<h2>" + name + '.py</h2>')
    try:
        module.run(t)
    except Regtest:
        t.error("Unexpected Timeout: stop testing")

def do_tests(client, output, server):
    output.write('<td style="vertical-align:top">\n')
    t = None
    try:
        t = Tester(client, output, server,
                   no_change_interval = display.no_change_interval)
        
        run('test_home', t)
        t.stop()
        output.write('</td>\n')
        return 'ok'
    except Regtest:
        if t:
            t.stop()
        output.write('</td>\n')
        return 'bad'
    except DiffError:
        if t:
            t.stop()
        return 'bad'

if __name__ == "__main__":
    for i in ('http_proxy', 'https_proxy', 'MAIL', 'MAILCHECK'):
        if os.environ.has_key(i):
            del os.environ[i]

    os.putenv("HOME", tmp_dir)
    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)
    if not os.path.isdir('Trash'):
        os.mkdir('Trash')
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
    if firefox3:
        t.append((firefox3, "-width %d -height %d about:"))
    if konqueror:
        t.append((konqueror, "--geometry %dx%d-0-0"))
    if chromium:
        t.append((chromium, "-width %d -height %d about:"))
    if opera:
        t.append((opera, "--geometry %dx%d-0-0 -nosession -nomail"))
    if galeon:
        t.append((galeon, "-f about: about: $(echo %dx%d >/dev/null)"))
    if ie6:
        t.append((ie6, "$(echo %dx%d >/dev/null)"))
    if vnc:
        t.append((vnc, "$(echo %dx%d >/dev/null)"))
    if iceape:
        t.append((iceape, "-width %d -height %d"))

    s = ''
    for name, args in t:
        print '*'*79
        print 'Start testing', name
        print '*'*79
        s += name + ':' + do_tests(name + ' >/dev/null 2>&1 ' + args, output, server) + ' '
        print 'Testing done for', name
    output.write('</tr></table>\n')

    os.rename(os.path.join(log_dir, 'xxx.html.new'),
              os.path.join(log_dir, 'xxx.html'))

    print 'Results are in %s/xxx.html' % log_dir
    print s
    import sys
    if 'bad' in s:
        sys.exit(1)
    else:
        sys.exit(0)
