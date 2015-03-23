#!/usr/bin/python
# Tests if TOMUSS is running and starts it if it is not.
# If called with argument 'crontab' it does not run
# tomuss if it was stoped with 'make stop'
# It runs it only if the host was rebooted or the processes killed

import sys
import os
import signal
import time
import urllib2
import tomuss_init

for i in ('http_proxy', 'https_proxy'):
    if os.environ.has_key(i):
        del os.environ[i]

from .. import utilities
from .. import configuration

def is_running1(url):
    if url != is_running1.last_url:
        print 'Check if running:', url
        is_running1.last_url = url
    else:
        print '*',
    sys.stdout.flush()
    try:
        f = urllib2.urlopen(url + '/robots.txt')
        c = f.read()
        f.close()
        return 'User-agent:' in c
    except IOError:
        return False
is_running1.last_url = ''

def is_running(url):
    return is_running1(url) or is_running1(url)

def run(url, command, run_only_if_not_properly_stopped, name=None,strace=""):
    if name == None:
        name = command.split('.')[0]
    logdir = os.path.join('LOGS', name.upper())
    pid = ''
    try:
        pid = int(utilities.read_file( os.path.join(logdir, 'pid')))
    except IOError:
        pass
    except ValueError:
        pass
    print url + ', PID=' + str(pid),
    sys.stdout.flush()
    if run_only_if_not_properly_stopped:
        if pid == '':
            # The pid file does not exists, so it was properly stopped.
            # Do not start it, the stop is intended.
            return
    start_time = time.time()
    if not is_running(url):
        if pid != '':
            try:
                os.system('''(
date
echo '====================================================================='
ps -felL
echo '====================================================================='
# lsof
echo '====================================================================='
netstat -ave
echo '====================================================================='
cd /proc/%d/task &&
for I in * ; do echo "$I: wchan=$(cat $I/wchan) sleepavg=$(grep SleepAVG $I/status | (read A B ; echo $B))" ; done
) >LOGS/xxx_state.%d 2>&1''' % (pid, pid))

                os.kill(pid, signal.SIGKILL)
                # Synchonous mail send
                utilities.send_mail(configuration.maintainer,
                                    'TOMUSS : Unresponding server',
                                    'Query at : %g' % start_time +
                                    url + ' relaunched')
                time.sleep(1) # Let server some time to write logs
            except OSError:
                print ', No Process',
                sys.stdout.flush()
                pass # Normal case : there is no process (reboot or core-dump)
        print ', start'
        utilities.mkpath(logdir)
        logname = time.strftime('%Y-%m-%d_%H:%M:%S')
        loglink = os.path.join(logdir, 'log')
        if os.path.islink(loglink):
            os.unlink(loglink)
        os.symlink(logname, loglink)
        os.system('''. LOCAL/profile
ulimit -s 1024
nohup %s ./%s >%s/%s 2>&1 &
P=$!
sleep 1 # Wait server start
if [ -d /proc/$P ]
then
echo $P >%s/pid
fi
''' %
                  (strace, command, logdir, logname, logdir))
    else:
        print ', yet running'

def stop(name):
    pid = None
    try:
        f = open(os.path.join('LOGS', name.upper(), 'pid'))
    except IOError:
        print '%s : there is no "pid" file to stop it' % name
        return
    try:
        try:
            pid = int(f.read().strip())
        except ValueError:
            return
    finally:
        f.close()
    print '%s : PID = %d' % (name, pid)
    try:
        os.kill(pid, 15)
        utilities.write_file(os.path.join('LOGS', name.upper(), 'pid'), '')
        print name, 'stopped'
        return pid
    except OSError:
        pass

def stop_suivi():
    for infos in configuration.suivi.servers():
        stop("suivi%d" % infos[1])

def stop_safe():
    if not is_running(configuration.server_url):
        return
    print '\a'
    print "Goto on TOMUSS home page, and choose 'stop tomuss'"
    print "The new version will be started automaticaly"
    print "If you want to stop TOMUSS right NOW, type '^C' once"
    try:
        while is_running(configuration.server_url):
            time.sleep(1)
    except KeyboardInterrupt:
        print "\nStopping TOMUSS not nicely"
        stop('tomuss')
            
def restart_suivi():
    """Linux only function"""
    for url,port,year,semester,dummy_host in configuration.suivi.servers():
        pid = stop("suivi%d" % port)
        # Wait death
        if pid:
            while os.path.exists("/proc/%d" % pid):
                time.sleep(1)
        run(url, 'suivi.py %d %s %d' % (year, semester, port),
            run_only_if_not_properly_stopped=False, name="suivi%d" % port)
        # Wait end of load
        while not is_running(url):
            time.sleep(1)

def restart_tomuss():
    """Linux only function"""
    pid = stop("tomuss")
    if pid:
        while os.path.exists("/proc/%d" % pid):
            time.sleep(1)
    run(configuration.server_url, 'tomuss.py',
        run_only_if_not_properly_stopped=False, strace="")

if 'stop' in sys.argv:
    stop_suivi()
    stop('tomuss')
    sys.exit(0)

if 'stop' in sys.argv:
    stop_suivi()
    stop('tomuss')
    sys.exit(0)

if 'stopsafe' in sys.argv:
    stop_suivi()
    stop_safe()
    sys.exit(0)

if 'stoptomusssafe' in sys.argv:
    stop_safe()
    sys.exit(0)

if 'stopsuivi' in sys.argv:
    stop_suivi()
    sys.exit(0)

if 'restartsuivi' in sys.argv:
    restart_suivi()
    sys.exit(0)

if 'restarttomuss' in sys.argv:
    restart_tomuss()
    sys.exit(0)

# Running suivi.

lock = os.path.join('TMP','crontab_run.running')

if os.path.exists(lock):
    if time.time() - os.path.getmtime(lock) < 3600:
        print 'The crontab is yet running'
        sys.exit(0)
    print "Assume the lock is really too old (host reboot?)"
    os.remove(lock)

try:
    utilities.write_file(lock, time.ctime())
    only_if_not_properly_stopped = 'crontab' in sys.argv

    run(configuration.server_url, 'tomuss.py',
        only_if_not_properly_stopped, strace="")

    for surl,sport,syear,ssemester,shost in configuration.suivi.servers():
        run(surl, 'suivi.py %d %s %d' % (syear, ssemester, sport),
            only_if_not_properly_stopped, name="suivi%d" % sport)
    try:
        from ..LOCAL import crontab_run
        crontab_run.run()
    except ImportError:
        pass

    # Collect Virtual Memory Usage for TOMUSS servers
    os.system('''
J=""
for I in $(cat LOGS/*/pid)
    do
         J="$J $I:$(cat /proc/$I/status | grep VmPeak)"
    done
echo $(date) $J | sed -e 's/VmPeak: //g' -e 's/... kB//g' >>LOGS/VM_usage
''')
finally:
    os.unlink(lock)
    

