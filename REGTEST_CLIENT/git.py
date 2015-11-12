#!/usr/bin/python3

"""
Args :
 --force : to redo all the regtest on all the commits
           It is in case of regtest modification

"""       
                

import os
import shutil
import sys
import time

print('Cloning TOMUSS')
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
    f = open(filename, 'r', encoding = "utf-8")
    c = f.read()
    f.close()
    return c

def p(txt):
    print('==', txt.strip())
    sys.stdout.flush()

start = '2.14.7'
start = 'dec670be3288e6c91f639181e418e153b887c752'

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
        open('Trash/GIT/' + commit + '/resume', 'w', encoding = "utf-8").close()
        continue

    messages = []
    f = os.popen('./test.py --tomuss_dir /tmp/TOMUSS-REGTEST --trash '
                 + 'Trash/GIT/' + previous
                 + ' --retry 5 --continue-on-error', "r"
                 )
    while True:
        line = f.readline()
        if line == '':
            break
        if line.startswith('= '):
            p(line)
            messages.append(line)
        if 'REGTESTSOK' in line:
            success = True
            break
        if 'REGTESTSBAD' in line:
            success = False
            break
    f.close()

    if success:
        p('The regression tests are fine for ' + commit)
        os.symlink(previous, 'Trash/GIT/' + commit)
        continue

    p('The regression tests are NOT fine for ' + commit)
    os.mkdir('Trash/GIT/' + commit)
    g = open('Trash/GIT/' + commit + '/resume', 'a', encoding = "utf-8")
    g.write(time.ctime() + '\n')
    g.write(''.join(messages))
    g.close()

    for i in os.listdir('Trash/GIT/' + previous):
        os.mkdir('Trash/GIT/' + commit   + '/' + i)
        for j in os.listdir('Trash/GIT/' + previous + '/' + i):
            pr = 'Trash/GIT/' + previous + '/' + i + '/' + j
            co = 'Trash/GIT/' + commit   + '/' + i + '/' + j
            if j.endswith('.bug.png'):
                p('Files are different ' + i + ' ' + j)
                os.rename(pr, co.replace('.bug.png', '.png'))
            else:
                if not os.path.exists(co):
                    # Not created with .bug.png renaming
                    p('Create symbolic link for ' + i + ' ' + j)
                    os.symlink('../../' + previous + '/' + i + '/' + j, co)

shutil.rmtree('/tmp/TOMUSS-REGTEST')
