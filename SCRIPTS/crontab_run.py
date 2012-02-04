#!/usr/bin/python
# Test is TOMUSS is running and starts it if not.
# If called with argument 'crontab' it does not run
# tomuss if it was stoped with 'make stop'
# It runs it only if the host was rebooted or the processes killed

import sys
import os
import signal
import time

sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), '..'))

for i in ('http_proxy', 'https_proxy'):
    if os.environ.has_key(i):
        del os.environ[i]

import utilities
import configuration
configuration.terminate()
import plugins
plugins.load_types()
import document
document.table(0, 'Dossiers', 'config_table', None, None)

import urllib2

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
    try:
        start_time = time.time()
        f = urllib2.urlopen(url + '/style.css')
        c = f.read()
        f.close()
    except IOError:
        c = ''

    if 'thetable' not in c:
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
        os.system('. LOCAL/profile ; ulimit -s 1024 ; nohup %s ./%s >%s/%s 2>&1 & echo $! >%s/pid' %
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
    try:
        os.kill(pid, 15)
        utilities.write_file(os.path.join('LOGS', name.upper(), 'pid'), '')
        print name, 'stopped'
    except OSError:
        pass

def stop_suivi():
    for url, port, year, semester, host in configuration.suivi.urls.values():
        stop("suivi%d" % port)


if 'stop' in sys.argv:
    stop_suivi()
    stop('tomuss')
    sys.exit(0)

if 'stoptomuss' in sys.argv:
    stop('tomuss')
    sys.exit(0)

if 'stopsuivi' in sys.argv:
    stop_suivi()
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
    run_only_if_not_properly_stopped = 'crontab' in sys.argv

    run(configuration.server_url, 'tomuss.py',
        run_only_if_not_properly_stopped, strace="")

    for url, port, year, semester, host in configuration.suivi.urls.values():
        run(url, 'suivi.py %d %s %d' % (year, semester, port),
            run_only_if_not_properly_stopped, name="suivi%d" % port)
    try:
        import LOCAL.crontab_run
        LOCAL.crontab_run.run()
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
    

