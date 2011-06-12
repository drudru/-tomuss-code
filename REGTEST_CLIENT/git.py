#!/usr/bin/python

"""
Args :
 --force : to redo all the regtest on all the commits
           It is in case of regtest modification

"""       
                

import os
import shutil
import sys
import time

print 'Cloning TOMUSS'
os.system('git clone .. /tmp/TOMUSS-REGTEST')

if not os.path.isdir('Trash'):
    os.mkdir('Trash')
if not os.path.isdir('Trash/GIT'):
    os.mkdir('Trash/GIT')

try:
    os.symlink('LOCAL.template', '/tmp/TOMUSS-REGTEST/LOCAL')
except OSError:
    pass

def read_file(filename):
    f = open(filename, 'r')
    c = f.read()
    f.close()
    return c

def p(txt):
    print '==', txt.strip()
    sys.stdout.flush()

start = '2.14.7'

f = os.popen("git log --pretty=oneline --reverse %s.." % start, "r")
lines = f.readlines()
f.close()

commit = None
for line in lines:
    previous = commit
    commit, comment = line.split(' ', 1)
    p('-'*70)
    p(comment)
    p('.'*70)

    if ('--force' not in sys.argv
        and os.path.isdir('Trash/GIT/' + commit)
        and os.path.isfile('Trash/GIT/' + commit + '/resume')):
        p('Regression tests yet done on ' + commit)
        continue

    p('Checkout ' + commit)
    os.system('cd /tmp/TOMUSS-REGTEST ; git checkout %s' % commit)

    if previous is None:
        p("Take the snapshots of the first commit")
        os.system('./test.py --tomuss_dir /tmp/TOMUSS-REGTEST --trash '
                  + 'Trash/GIT/' + commit)
        open('Trash/GIT/' + commit + '/resume', 'w').close()
        continue

    messages = []
    success = False
    for retry in range(5):
        f = os.popen('./test.py --tomuss_dir /tmp/TOMUSS-REGTEST --trash '
                     + 'Trash/GIT/' + previous, "r"
                     )
        while True:
            line = f.readline()
            if line == '':
                break
            print line,
            if line.startswith('= ') and (':ok' in line or 'bad' in line):
                p(line)
                messages.append(line)
                if 'bad' not in line:
                    p('Regtest success on all the browser !')
                    success = True
                    break
        if success:
            break
        f.close()

    if success:
        p('The regression tests are fine for ' + commit)
        os.symlink(previous, 'Trash/GIT/' + commit)
        continue

    p('The regression tests are NOT fine for ' + commit)
    os.mkdir('Trash/GIT/' + commit)
    g = open('Trash/GIT/' + commit + '/resume', 'a')
    g.write(time.ctime() + '\n')
    g.write(''.join(messages))
    g.close()

    os.system('./test.py --tomuss_dir /tmp/TOMUSS-REGTEST --trash '
              + 'Trash/GIT/' + commit)
    for i in os.listdir('Trash/GIT/' + commit):
        for j in os.listdir('Trash/GIT/' + commit + '/' + i):
            p = 'Trash/GIT/' + previous + '/' + i + '/' + j
            c = 'Trash/GIT/' + commit   + '/' + i + '/' + j
            if read_file(p) == read_file(c):
                p('Create symbolic link for ' + i + ' ' + j)
                os.remove(c)
                os.symlink('../../' + previous + '/' + i + '/' + j, c)
            else:
                p('Files are different ' + i + ' ' + j)


shutil.rmtree('/tmp/TOMUSS-REGTEST')
