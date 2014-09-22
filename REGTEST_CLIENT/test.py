#!/usr/bin/python

"""
Most Timing configurations are in 'display.py'
"""

# TODO : more tests

import sys
import os
import time
import socket
import tester

def run(name, t):
    module = __import__(name)
    t.output.write("<h2>" + name + '.py</h2>')
    module.run(t)

def do_tests(client, output, server, nb):
    output.write('<td style="vertical-align:top" width="%d%%">\n'
                 % int(100./nb))
    start = time.time()
    t = tester.Tester(client, output, server)
    m = '?BUG?'
    try:
        try:
            t.initialize()

            run('test_home', t)
            run('test_table', t)
            run('test_popup', t)
        except tester.Regtest:
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

def main():
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == '--tomuss_dir':
            i += 1
            tester.tomuss_dir = sys.argv[i]
        elif arg == '--trash':
            i += 1
            trash = sys.argv[i]
        elif arg == '--retry':
            i += 1
            retry = int(sys.argv[i])
        elif arg == '--continue-on-error':
            tester.continue_on_error = True
        else:
            raise ValueError("Unknown arg: " + arg)
        i += 1

    start = time.time()
    
    if not os.path.isdir(trash):
        os.mkdir(trash)
    try:
        os.symlink(os.path.join(os.getcwd(), trash),
                   os.path.join(tester.log_dir, 'Trash'))
    except OSError:
        pass
    name = os.path.join(tester.log_dir, 'xxx.html.new')
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

    os.rename(os.path.join(tester.log_dir, 'xxx.html.new'),
              os.path.join(tester.log_dir, 'xxx.html'))

    print 'Results are in %s/xxx.html' % tester.log_dir
    print s
    print '= Runtime: %.1f' % ((time.time() - start)/60), 'minutes'
    if ok:
        print 'REGTESTSOK'
        sys.exit(0)
    else:
        print 'REGTESTSBAD'
        sys.exit(1)


if __name__ == "__main__":
    main()
