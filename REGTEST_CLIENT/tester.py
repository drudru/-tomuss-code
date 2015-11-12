"""

"""

import shutil
import glob
import time
import os
import sys
import dumper
from xnee import Xnee
import urllib.request, urllib.error, urllib.parse

tomuss_dir = '..'
trash = 'Trash'
tmp_dir = "/tmp/xxx-home"
log_dir = "/tmp/XXX"
retry = 1
continue_on_error = False

for i in ('http_proxy', 'https_proxy', 'MAIL', 'MAILCHECK'):
    if i in os.environ:
        del os.environ[i]

os.environ["HOME"] = tmp_dir

if not os.path.isdir(log_dir):
    os.mkdir(log_dir)


class Regtest(Exception):
    pass

def rmdir(pattern):
    for i in glob.glob(pattern):
        try:
            shutil.rmtree(i)
        except OSError:
            os.unlink(i)
        if os.path.exists(i):
            print(i + ' deletion failed, move it.')
            rmdir(i + '~')
            print('rename', i, 'to', i + '~')
            os.rename(i, i + '~')
        if os.path.exists(i):
            print('BUG')

def create_open(path):
    for i in range(1, len(path)):
        try:
            os.mkdir(os.path.sep.join(path[:i]))
        except OSError:
            pass
    return open(os.path.sep.join(path), 'w', encoding = "utf-8")

def create_write(path, content):
    f = create_open(path)
    f.write(content)
    f.close()


class Tester(object):
    """Launch a virtual display and an event simulator on the display.
    A web browser is launched on the display.

    The center of interest is the auto-detected BODY on the screen.
    """
    
    def __init__(self, client, output, server, x11="/usr/bin/Xvfb"):
        print('Creating tester')
        self.client = client
        self.client_name = self.client.split(' ')[0]
        self.server = server
        self.output = output
        self.output.write('<h1>' + self.client_name + '</h1>\n')

        self.errors = []
        self.display = dumper.Display(resolution='800x600', server=x11)
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
        time.sleep(1)
        self.maximize_window()
        self.xnee.goto(50,50)
        self.xnee.key("Escape") # Remove any visible popup
        self.goto_url('about:')
        # time.sleep(10)
        self.xnee.key("Escape") # Remove any visible popup
        # self.check_image('start')
        print('Tester started for', self.client_name)

    def start_tomuss(self):
        print("Start TOMUSS")
        rmdir(tmp_dir)
        rmdir('/tmp/DBregtest')
        rmdir('/tmp/BACKUP_DBregtest')
        rmdir(tomuss_dir + '/BACKUP_DBregtest')
        rmdir(tomuss_dir + '/DBregtest')
        os.mkdir('/tmp/DBregtest')
        os.mkdir('/tmp/BACKUP_DBregtest')
        os.symlink('/tmp/DBregtest', tomuss_dir + '/DBregtest')
        os.symlink('/tmp/BACKUP_DBregtest', tomuss_dir + '/BACKUP_DBregtest')
        for i in ('DBregtest', 'DBregtest/Y9999',
                  'DBregtest/Y9999/STest', 'LOGS', 'LOGS/TOMUSS'):
            try:
                os.mkdir(tomuss_dir + '/' + i)
            except OSError:
                pass
            open(tomuss_dir + '/' + i + '/__init__.py', 'w', encoding = "utf-8").close()

        try:
            os.mkdir(tmp_dir)
        except OSError:
            print('BEWARE: a running program held a file in ', tmp_dir)

        snapdir = os.path.join(trash, self.client_name)
        if not os.path.isdir(snapdir):
            os.mkdir(snapdir)
        
        print("Configure account")
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
        print("Run server")
        os.system('(cd %s ; ./tomuss.py regtest real_regtest >/dev/null 2>&1 &)' %
                  tomuss_dir)
        print("Wait server start")
        while True:
            try:
                time.sleep(1)
                f = urllib.request.urlopen("http://%s:8888/=super.user/"%self.server)
                f.read()
                f.close()
                break
            except urllib.error.URLError:
                continue

    def stop_tomuss(self):
        print('Stop tomuss')
        f = urllib.request.urlopen("http://%s:8888/stop" % self.server)
        assert('stopped' in f.read())
        f.close()

    def maximize_window(self):
        time.sleep(1)
        self.xnee.goto(self.display.width/2, self.display.height/2)        
        self.xnee.key('F8')
        time.sleep(1)
        # self.xnee.key('F11') # don't work with chromium

    def goto_url(self, url):
        print('goto', url)
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
        print('check_image', filename)
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
                    print('Escape !')
                    self.xnee.key('Escape') # Epiphany bug ?
                    escaped = True
                if time.time() - start > timeout:
                    identical = self.is_identical(snapshot)
                    break               
                time.sleep(1)
        else:
            if self.display.wait_end_of_change(wait=wait) is False:
                print('Escape !')
                self.xnee.key('Escape') # Epiphany bug ?
                self.display.wait_end_of_change(wait=1)
            
            self.display.store_dump(snapshot)
            print(snapshot, 'created')
            identical = True

        if not hide:
            self.output.write(
                '<a href="%s"><img src="%s" style="width:100%%"></a>'
                % (snapshot, snapshot))

        if identical is not True:
            self.error("%s{%d}" % (filename, identical), filename)
            print(snapshot, 'is not the same !!!!!!!!!!!!')
            self.errors.append(filename)
            if not continue_on_error:
                raise Regtest('Difference')

    def stop(self):
        print('Stop test for this browser')
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
