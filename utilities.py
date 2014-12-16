#!/usr/bin/python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2008-2012 Thierry EXCOFFIER, Universite Claude Bernard
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#    Contact: Thierry.EXCOFFIER@bat710.univ-lyon1.fr

import resource
import time
import re
import os
import sys
import traceback
import gettext
import cgi
import threading
import shutil
import gc
import ast
from . import configuration

def read_file(filename):
    f = open(filename, 'r')
    c = f.read()
    f.close()
    return c

def write_file(filename, content):
    warn('%s : %d' % (filename, len(content)), what='debug')
    f = open(filename, 'w')
    f.write(content)
    f.close()

def write_file_safe(filename, content):
    write_file(filename, content)
    if configuration.backup:
        write_file(configuration.backup + filename, content)

lock_list = []

def add_a_lock(fct):
    """Add a lock to a function to forbid simultaneous call"""
    def f(*arg, **keys):
        warn('[[[' + f.fct.func_name + ']]]', what='debug')
        f.the_lock.acquire()
        try:
            r = f.fct(*arg, **keys)
        finally:
            f.the_lock.release()
        return r
    f.fct = fct
    f.the_lock = threading.Lock()
    f.__doc__ = fct.__doc__
    f.func_name = fct.func_name
    f.__module__ = fct.__module__
    lock_list.append(f)
    return f

def append_file_unlocked(filename, content):
    """Paranoid : check file size before and after append"""
    try:
        before = os.path.getsize(filename)
    except OSError:
        before = 0
    f = open(filename, 'a')
    f.write(content)
    f.close()
    after = os.path.getsize(filename)
    if before + len(content) != after:
        raise IOError("Append file failed %s before=%d + %d ==> %d" % (
            filename, before, len(content), after))
    if filename.endswith('.py'):
        try:
            os.unlink(filename + 'c')
        except OSError:
            pass


filename_to_bufferize = None
filename_buffer = []

def bufferize_this_file(filename):
    """Should be called with None to flush the buffered content"""
    global filename_to_bufferize, filename_buffer
    if filename == filename_to_bufferize:
        return
    append_file.the_lock.acquire()
    try:
        if filename_to_bufferize:
            append_file_unlocked(filename_to_bufferize,
                                 ''.join(filename_buffer))
    finally:
        filename_to_bufferize = filename
        filename_buffer = []
        append_file.the_lock.release()
    
@add_a_lock
def append_file(filename, content):
    if filename == filename_to_bufferize:
        filename_buffer.append(content)
    else:
        append_file_unlocked(filename, content)

def append_file_safe(filename, content):
    append_file(filename, content)
    if configuration.backup:
        append_file(configuration.backup + filename, content)

def unlink_safe(filename, do_backup=True):
    if do_backup and os.path.exists(filename):
        dirname = os.path.join('Trash', time.strftime('%Y%m%d'))
        mkpath(dirname)

        shutil.move(filename,
                    os.path.join(dirname,
                                 filename.replace(os.path.sep, '___'))
                    )
    try:
        os.unlink(filename)
    except OSError:
        pass
    if configuration.backup:
        try:
            os.unlink(configuration.backup + filename)
        except OSError:
            pass

def rename_safe(old_filename, new_filename):
    unlink_safe(new_filename)
    os.rename(old_filename, new_filename)
    if configuration.backup:
        os.rename(configuration.backup + old_filename,
                  configuration.backup + new_filename)

def symlink_safe(old_filename, new_filename):
    os.symlink(old_filename, new_filename)
    if configuration.backup:
        os.symlink(old_filename, configuration.backup + new_filename)
    
def safe(txt):
    return re.sub('[^0-9a-zA-Z-.]', '_', txt)

def safe_quote(txt):
    return re.sub('[^\'0-9a-zA-Z-.]', '_', txt)

def safe_space(txt):
    return re.sub('[^0-9a-zA-Z-. ]', '_', txt)

def safe_space_quote(txt):
    return re.sub('[^\'0-9a-zA-Z-. ]', '_', txt)

def flat(txt):
    return txt.translate(u"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f ! #$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~?\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f?????Y|?????????????'u?.????????AAAAAA?CEEEEIIIIDNOOOOOXOUUUUY?Baaaaaa?ceeeeiiiionooooo??uuuuy?y")

def same(a, b):
    return flat(a).lower() == flat(b).lower()

def university_year(year=None, semester=None):
    if semester is None:
        semester = configuration.year_semester[1]
    if year is None:
        year = configuration.year_semester[0]
    try:
        i = configuration.semesters.index(semester)
    except ValueError:
        return year
    return year + configuration.semesters_year[i]

def university_year_semester(year=None, semester=None):
    "Return the first year+semester of the university"
    if semester is None:
        semester = configuration.year_semester[1]
    if year is None:
        year = configuration.year_semester[0]
    try:
        i = configuration.semesters.index(semester)
    except ValueError:
        return year, semester
    
    return (year + configuration.semesters_year[i],
            configuration.university_semesters[0])


def next_year_semester(year, semester):
    try:
        i = (configuration.semesters.index(semester) + 1) % len(
            configuration.semesters)
    except ValueError:
        return year + 1, semester
    if i != 0:
        return year, configuration.semesters[i]
    else:
        return year + 1, configuration.semesters[i]

def previous_year_semester(year, semester):
    try:
        i = (configuration.semesters.index(semester)
             + len(configuration.semesters) - 1) % len(
                 configuration.semesters)
    except ValueError:
        return year - 1, semester
    if i != len(configuration.semesters) - 1:
        return year, configuration.semesters[i]
    else:
        return year - 1, configuration.semesters[i]

def semester_key(year, semester):
    try:
        return year, configuration.semesters.index(semester)
    except ValueError:
        return year, semester

def year_semester_from_date(yyyymm):
    """The time can be longer"""
    month = int(yyyymm[4:6])
    year = int(yyyymm[:4])

    for s, m in zip(configuration.semesters,configuration.semesters_months): 
        if m[0] <= month <= m[1]:
            return year, s
        if m[0] <= 12+month <= m[1]:
            return year-1, s

def semester_span(year, semester):
    """Semester span in seconds"""
    sem_span = configuration.semester_span(year, semester)
    if sem_span:
        first_day, last_day = sem_span.split(' ')
        return (configuration.date_to_time(first_day),
                configuration.date_to_time(last_day))
    else:
        return (0, 8000000000)

def date_to_time(date, if_exception=None):
    try:
        return configuration.date_to_time(date)
    except:
        if if_exception is None:
            raise
        else:
            return if_exception
        
live_log = None

def warn(text, what='info'):
    if what in configuration.do_not_display:
        return
    x = []
    try:
        for i in range(1, 4):
            x.append(sys._getframe(i).f_code.co_name)
    except ValueError:
        pass
    x.reverse()
    x = '/'.join(x).rjust(50)[-50:]
    x = '%c %13.2f %4d %s %s\n' % (
        what[0].upper(),
        time.time(),
        resource.getrusage(resource.RUSAGE_SELF)[2]//1000,
        x, text)
    sys.stderr.write(x)
    global live_log
    if live_log:
        try:
            live_log.write(x)
        except:
            live_log = None

@add_a_lock
def send_mail(to, subject, message, frome=None, show_to=False, reply_to=None,
              error_to=None):
    "Not safe with user given subject"
    import smtplib

    if isinstance(to, list) or isinstance(to, tuple):
        recipients = to
    else:
        recipients = [to]
    if frome == None:
        frome = configuration.maintainer

    new_to = []
    for addr in recipients:
        if not addr:
            continue
        if '@' not in addr or '.' not in addr:
            continue
        try:
            new_to.append(addr.encode('ascii'))
        except UnicodeEncodeError:
            warn('bad email address: ' + repr(addr), what='error')
    to = new_to
    if len(to) == 0:
        return
    
    header = "From: " + frome + '\n'
    if isinstance(subject, unicode):
        s = subject.encode("utf-8")
    else:
        s = subject
    header += "Subject: " + s.replace('\n',' ').replace('\r',' ') + '\n'
    if len(to) == 1:
        header += "To: " + to[0] + '\n'
    elif show_to:
        for tto in to:
            header += "To: " + tto + '\n'
    if reply_to:
        header += 'Reply-To: ' + reply_to + '\n'
    if error_to:
        header += 'Error-To: ' + error_to + '\n'
        
    if message.startswith('<html>'):
        header += 'Content-Type: text/html; charset=UTF-8\n'
    else:
        if isinstance(message, unicode):
            header += 'Content-Type: text/plain; charset=UTF-8\n'

    if isinstance(message, unicode):            
        message = message.encode('utf-8')
    
    while True: # Stop only if the mail is sent
        try:
            smtpresult = send_mail.session.sendmail(frome, recipients,
                                                    header + '\n' + message)
            break
        except smtplib.SMTPRecipientsRefused:
            warn("Can't deliver mail to " + repr(recipients))
            break
        except smtplib.SMTPServerDisconnected:
            # It is normal: connection is closed by SMTP if unused
            send_mail.session = smtplib.SMTP(configuration.smtpserver)
            continue
        except:
            if send_mail.session is not None:
                send_backtrace('from=%s\nrecipients=%s\nheaders=%s' %
                               (repr(frome), repr(recipients), repr(header)))
            send_mail.session = smtplib.SMTP(configuration.smtpserver)

    try:
        if smtpresult:
            errstr = ""
            for recip in smtpresult.keys():
                errstr += _("MSG_utilities_smtp_error") % recip \
                    + smtpresult[recip][0] + ' ' + smtpresult[recip][1]

            send_mail.session = None
            return errstr
    except:
        return 'BUG in utilities.send_mail'

send_mail.session = None

thread_list = []

def start_new_thread_immortal(fct, args, send_mail=True):
    start_new_thread(fct, args, send_mail=send_mail, immortal=True)

def start_new_thread(fct, args, send_mail=True, immortal=False):
    class T(threading.Thread):
        def __init__(self):
            self.send_mail = send_mail
            self.immortal = immortal
            self.fct = fct
            self.args = args
            threading.Thread.__init__(self)
        def run(self):
            thread_list.append(self)
            warn("Start %s" % self)
            # turn around a locking problem BUG in python threads
            while True:
                try:
                    time.strptime('2010', '%Y')
                    break
                except:
                    warn('strptime' + str(self), what='error')
                    time.sleep(0.1)
            while True:
                warn('Call ' + self.fct.func_name)
                try:
                    self.fct(*self.args)
                except:
                    warn("Exception in %s" % self, what="Error")
                    if self.send_mail:
                        send_backtrace("Exception in %s" % self)
                if not self.immortal:
                    break
            thread_list.remove(self)
        def backtrace_html(self):
            return str(self)
        def __str__(self):
            return 'Thread immortal=%-5s send_mail=%-5s %s' % (
                   self.immortal, self.send_mail, fct.func_name)

        def stack(self):
            return (str(self) + '\n'
                    + ''.join(traceback.format_stack(
                        sys._current_frames()[self.ident])[3:]))

    t = T()
    t.setDaemon(True)
    t.start()    

def stop_threads():
    sys.exit(0)
    for t in threading.enumerate():
        t.join()



send_mail_in_background_list = []
def sendmail_thread():
    """Send the mail in background with a minimal time between mails"""
    sendmail_thread.safe_to_check = False
    while send_mail_in_background_list:
        sendmail_thread.safe_to_check = True
        time.sleep(configuration.time_between_mails)
        send_mail(*send_mail_in_background_list.pop(0))
        sendmail_thread.safe_to_check = False

def send_mail_in_background(to, subject, message, frome=None, show_to=False,
                            reply_to=None, error_to=None):
    send_mail_in_background_list.append((to, subject, message, frome,
                                         show_to, reply_to, error_to))
    start_job(sendmail_thread, 1)

def js(t):
    if isinstance(t, basestring):
        # return repr(unicode(t,'utf8').encode('latin1'))
        return '"' + t.replace('\\','\\\\').replace('"','\\"').replace('>','\\x3E').replace('<','\\x3C').replace('&', '\\x26').replace('\r','').replace('\n','\\n') + '"'
    elif isinstance(t, float):
        return '%g' % t
    elif isinstance(t, dict):
        return '{' + ','.join("'%s':%s" % (k, js(v))
                              for k, v in t.items()) + '}'
    elif isinstance(t, tuple):
        return str(list(t))
    else:
        return str(t)

def js2(t):
    return '"' + t.replace('\\','\\\\').replace('"','\\"').replace('\n','\\n') + '"'

def mkpath(path, create_init=True, mode=0777):
    s = ''
    for i in path.split(os.path.sep):
        s += i + os.path.sep
        try:
            os.mkdir(s, mode)
            if create_init:
                write_file(os.path.join(s, '__init__.py'), '')
        except OSError:
            pass

def mkpath_safe(path):
    mkpath(path)
    if configuration.backup:
        mkpath(configuration.backup + path)


#REDEFINE
# If the student login in LDAP is not the same as the student ID.
# This function translate student ID to student login.
# The returned value must be usable safely.
def the_login(student):
    if isinstance(student, basestring):
        return safe(student)
    return ''

def tipped(html, tip, classname="", url=''):
    """Do not use this function, use 'hidden' javascript utility"""

    if url == '':
        html = html.split('<script>')
        if len(html) == 2:
            if html[0] == '':
                html = html[1].replace('</script>','')
            else:
                html = js2(html[0]) + '+' + html[1].replace('</script>','')
        else:
            html = js2(html[0])
        return '<script>hidden(%s,%s,%s);</script>' % (html, js2(tip),
			 js2(classname))
    return '<script>hidden(%s,%s,%s);</script>' % (
	js2('<a target="_blank" href="%s">%s</a>' % (url, html)), js2(tip), js2(classname))


def newline():
    return '<br>'

def frame_info(frame, displayed):
    s = '<tr><td class="name"><small><small>%s</small></small>/<b>%s</b><br><td class="line">%s<td>\n' % (
        frame.f_code.co_filename.replace(os.getcwd(), '').strip('/'),
        frame.f_code.co_name,
        frame.f_lineno)
    for k, v in frame.f_locals.items():
        if id(v) not in displayed:
            try:
                s += "<p><b>" + cgi.escape(k) + "</b>:<br>" + v.backtrace_html() + "\n"
            except AttributeError:
                pass
            except TypeError:
                pass
            displayed[id(v)] = True
    s += '</tr>'
    return s

import socket


def send_backtrace(txt, subject='Backtrace', exception=True):
    s = configuration.version
    if exception and sys.exc_info()[0] != None \
       and sys.exc_info()[0] == socket.error:
        s += '*'
    else:
        s += ' '
    s += ' '.join(sys.argv) + ' ' + subject
    subject = s
    displayed = {}
    s = ''
    if txt:
        s += ('<h1>Information reported by the exception catcher</h1><pre>' +
               cgi.escape(txt) + '</pre>\n')
    if exception and sys.exc_info()[0] != None:
        s += '<h1>Exception stack</h1>\n'
        s += '<p>Exception class: ' + cgi.escape(str(sys.exc_info()[0])) + '\n'
        s += '<p>Exception value: ' + cgi.escape(str(sys.exc_info()[1])) + '\n'
        f = sys.exc_info()[2]
        s += '<p>Exception Stack:<table>\n'
        x = ''
        while f:
            ss = frame_info(f.tb_frame, displayed)
            x = ss + x
            f = f.tb_next
        s += x + '</table>'

    s += '<h1>Current Stack:</h1>\n<table>\n'
    try:
        for i in range(1, 20):
            ss = frame_info(sys._getframe(i), displayed)
            s += ss
    except ValueError:
        pass
    s += '</table>'
    filename = os.path.join("LOGS", "BACKTRACES",
                            time.strftime('%Y-%m-%d'
                                          + os.path.sep + "%H:%M:%S")
                            )
    mkpath(os.path.join(*filename.split(os.path.sep)[:-1]), create_init=False)

    s = '<html><style>TABLE TD { border: 1px solid black;} .name { text-align:right } PRE { background: white ; border: 2px solid red ;}</style><body>' + s + '</body></html>'
    
    f = open(filename, "a")
    f.write(subject + '\n' + s)
    f.close()
    warn(subject + '\n' + s, what="error")

    if send_backtrace.last_subject != subject and '*./' not in subject:
        # Not send twice the same mail subject.
        # Do not send closed connection traceback.
        send_mail_in_background(configuration.maintainer, subject, s)
        send_backtrace.last_subject = subject

send_backtrace.last_subject = ''

def compressBuf(buf):
    import gzip
    import StringIO
    zbuf = StringIO.StringIO()
    zfile = gzip.GzipFile(None, 'wb', 9, zbuf)
    zfile.write(buf)
    zfile.close()
    return zbuf.getvalue()

class StaticFile(object):
    """Emulate a string, but it is a file content"""
    mimetypes = {'html': 'text/html;charset=utf8',
                'css': 'text/css;charset=utf8',
                'png': 'image/png',
                'ico': 'image/png',
                'jpg': 'image/jpeg',
                'gif': 'image/gif',
                'js': 'application/x-javascript;charset=utf8',
                'txt': 'text/plain',
                'xml': 'application/rss+xml;charset=utf8',
                }
    _url_ = 'http://???/' # The current server (TOMUSS or 'suivi')
                
    def __init__(self, name, mimetype=None, content=None):
        self.name = name
        if mimetype == None:
            if '.' in name:
                n = name.split('.')[-1]
                mimetype = self.mimetypes[n]
        self.mimetype = mimetype
        self.content = content
        if self.content:
            # Not a file, so NEVER reload it
            self.time = -1
            self.copy_on_disc()
        else:
            self.time = 0
        self.append_text = {}
        self.replace_text = {}

    def need_update(self):
        if self.time != -1 and (self.content == None
                                or self.time != os.path.getmtime(self.name)):
            return True

        for i in self.append_text.values():
            if isinstance(i, StaticFile):
                if i.need_update():
                    return True

    def copy_on_disc(self):
        dirname = os.path.join("TMP", configuration.version)
        mkpath(dirname)
        filename = os.path.join(dirname, self.name.split(os.path.sep)[-1])
        write_file(filename, self.content)

    def __str__(self):
        if self.need_update():
            self.time = os.path.getmtime(self.name)
            content = read_file(self.name)
            for old, new in self.replace_text.values():
                content = content.replace(old, new)
            content += ''.join(str(i) for i in self.append_text.values())
            if self.name.endswith('.js') or self.name.endswith('.html'):
                content = content.replace('_FILES_', configuration.url_files)
            self.content = content
            self.gzipped = compressBuf(self.content)
            self.copy_on_disc()

        return self.content

    def clear_cache(self):
        if self.time != -1:
            self.content = None

    def __len__(self):
        return len(str(self))

    def replace(self, key, old, new):
        """The replacement is done each time the file is reloaded"""
        self.replace_text[key] = (old, new)
        self.clear_cache()

    def append(self, key, content):
        """The append is done each time the file is reloaded"""
        self.append_text[key] = content
        self.clear_cache()

caches = []

def register_cache(f, fct, timeout, the_type):
    f.__doc__ = fct.__doc__
    f.fct = fct
    f.timeout = timeout
    f.the_type = the_type
    caches.append(f)

def clean_cache0(f):
    if f.cache[1] and time.time() - f.cache[1] > f.timeout:
        f.cache = ('', 0)


def add_a_cache0(fct, timeout=None):
    """Add a cache to a function without parameters"""
    if timeout is None:
        timeout = 3600
    def f():
        cache = f.cache
        if time.time() - cache[1] > f.timeout:
            cache = (f.fct(), time.time())
            f.cache = cache
        return cache[0]
    f.cache = ('', 0)
    register_cache(f, fct, timeout, 'add_a_cache0')
    f.clean = clean_cache0
    return f

def clean_cache(f):
    if getattr(f, 'last_value_on_exception', 0):
        return # Do not erase in order to reuse if there is an exception
    for key, value in f.cache.items():
        if time.time() - value[1] > f.timeout:
            del f.cache[key]

def add_a_cache(fct, timeout=3600, not_cached='neverreturnedvalue',
                last_value_on_exception=False):
    """Add a cache to a function with one parameter.
    If the returned value is 'not_cached' then it is not cached.
    If the cached function may sometime raise an exception,
    it may be interesting to set last_value_on_exception=True in order
    to return the previously cached value and hide the exception.
    """
    def f(x):
        cache = f.cache.get(x, ('',0))
        if time.time() - cache[1] > f.timeout:
            try:
                cache = (f.fct(x), time.time())
            except:
                if f.last_value_on_exception and cache[1] != 0:
                    cache = (cache[0], time.time())
                    send_backtrace(str(f.fct), "Cache update failed",
                                   exception=False)
                else:
                    raise
            
        if cache[0] == f.not_cached:
            return f.not_cached
        else:
            f.cache[x] = cache
            return cache[0]
    f.cache = {}
    register_cache(f, fct, timeout, 'add_a_cache')
    f.clean = clean_cache
    f.not_cached = not_cached
    f.last_value_on_exception = last_value_on_exception
    return f

def add_a_method_cache(fct, timeout=None, not_cached='neverreturnedvalue'):
    """Add a cache to a method with one parameter.
    If the returned value is 'not_cached' then it is not cached.
    The CACHE IS COMMON TO EVERY INSTANCE of the class"""
    if timeout == None:
        timeout = 3600
    def f(self, x):
        cache = f.cache.get(x, ('',0))
        if time.time() - cache[1] > f.timeout:
            cache = (f.fct(self, x), time.time())
            
        if cache[0] == f.not_cached:
            return f.not_cached
        else:
            f.cache[x] = cache
            return cache[0]
    f.cache = {}
    register_cache(f, fct, timeout, 'add_a_method_cache')
    f.clean = clean_cache
    f.not_cached = not_cached
    return f


def unload_module(m):
    if m not in sys.modules:
        return
    # print "unload", m
    del(sys.modules[m])
    # print "UNLOAD", '.'.join(m.split('.')[:-1]), '====', m.split('.')[-1]
    try:
        del(sys.modules['.'.join(m.split('.')[:-1])].__dict__[m.split('.')[-1]])
    except KeyError:
        pass

def import_reload(filename):
    mtime = os.path.getmtime(filename)
    name = filename.split(os.path.sep)
    name[-1] = name[-1].replace('.py','')
    name.insert(0, 'TOMUSS')
    module_name = '.'.join(name)
    __import__(module_name) # force the .pyc creation
    old_module = sys.modules[module_name]
    mtime_pyc =  os.path.getmtime(filename + 'c')
    to_reload = mtime > mtime_pyc
    if to_reload:
        unload_module(module_name)
        __import__(module_name)
        module = sys.modules[module_name]
        # replace the old by the new one
        for o in gc.get_referrers(old_module):
            if isinstance(o, dict):
                for k, v in o.items():
                    if v is old_module and k != 'old_module':
                        o[k] = module
                        break
    else:
        module = old_module
    return module, to_reload

def nice_date(x):
    year = x[0:4]
    month = x[4:6]
    day = x[6:8]
    hours = x[8:10]
    minutes = x[10:12]
    seconds = x[12:14]
    return hours + 'h' + minutes + '.' + seconds + ' le ' + \
           day + '/' + month + '/' + year 

def wait_scripts():
    # Returns 'true' if the script are loaded and so processing must continue.
    # If it returns 'false' then the calling function must stop processing.
    # It will be recalled with a 'setTimeOut'
    
    # The parameter is a string evaluated if the loading is not fine,
    # It must be a function recalling 'wait_scripts'
    # By the way :
    #    * this function can not be stored in a script.
    #    * It must not be in a loop
    return """
    function wait_scripts(recall)
    {
    if ( navigator.userAgent.indexOf('Konqueror') == -1 )
        {
            var d = document.getElementsByTagName('SCRIPT'), e ;            
            for(var i=0; i<d.length; i++)
               {
               e = d[i] ;
               if ( e.src === undefined )
                   continue ;
               if ( e.src === '' )
                   continue ;
               if ( e.onloadDone )
                   continue ;
            /*   if ( e.readyState === "loaded" )
                   continue ; */
               if ( e.readyState === "complete" )
                   continue ;
               setTimeout(recall, 1000) ;
               return ;
               }
         }
    return true ;
    }
         """



#REDEFINE
# This function returns True if the user uses a stupid password.
# Potential stupid passwords are in the 'passwords' list.
# Each of the passwords should be tried to login,
# if the login is a success, the password is bad.
def stupid_password(login, passwords):
    return False


def module_to_login(module):
    return module.replace('__','.').replace('_','-')

def login_to_module(login):
    return login.replace('.','__').replace('-','_')

class AtomicWrite(object):
    """Act as 'open' function but rename file once it is closed."""
    def __init__(self, filename, reduce_ok=True, display_diff=False):
        self.real_filename = filename
        self.filename = filename + '.new'
        self.file = open(self.filename, 'w')
        self.reduce_ok = reduce_ok
        self.display_diff = display_diff
    def write(self, v):
        self.file.write(v)
    def close(self):
        self.file.close()
        if not self.reduce_ok \
           and os.path.exists(self.real_filename) \
           and os.path.getsize(self.filename) \
                   < 0.5 * os.path.getsize(self.real_filename):
            send_mail(configuration.maintainer,
                      'BUG TOMUSS : AtomicWrite Reduce' +
                      self.real_filename, self.real_filename)   
            return
        if self.display_diff:
            os.system("diff -u '%s' '%s'" % (
                self.real_filename.replace("'","'\"'\"'"),
                self.filename.replace("'","'\"'\"'")))
        os.rename(self.filename, self.real_filename)


def python_files(dirname):
    a = os.listdir(dirname)
    for ue in a:
        if not ue.endswith('.py'):
            continue
        if ue.startswith('__'):
            continue
        yield ue

def count(t):
    """Generator : given an iterable it returns tuples :
    (nr_identical_items, item_value)
    """
    t = t.__iter__()
    last = t.next()
    i = 1
    try:
        while True:
            a = t.next()
            if a == last:
                i += 1
            else:
                yield (i, last)
                i = 1
                last = a
    except StopIteration:
        yield (i, last)

def get_tuples(an_iterable, size):
    """
    >>> for i in get_tuple([1,2,3,4,5,6,7], 3): print i
    (1, 2, 3)
    (4, 5, 6)
    """
    return zip( * ( [iter(an_iterable)]*size ) )

    
def manage_key_real(dirname, key, separation=3, content=None, reduce_ok=True,
                    append=False, delete=False):
    """
    Do not use this function
    """
    if content is None and not os.path.isdir(dirname):
        return False
    try:
        mkpath(dirname)
    except OSError:
        pass
    
    key_dir = key.split(os.path.sep)[0]
    f1 = os.path.join(dirname, key_dir[:separation])
    if content is None and not os.path.isdir(f1):
        return False
    try:
        os.mkdir(f1, 0750)
    except OSError:
        pass

    if os.path.sep in key:
        if content is None and not os.path.isdir(os.path.join(f1, key_dir)):
            return False
        try:
            os.mkdir(os.path.join(f1, key_dir), 0750)
        except OSError:
            pass

    f1 = os.path.join(f1, key)
    if os.path.exists(f1):
        if delete:
            os.unlink(f1)
            return
        f = open(f1, 'r')
        c = f.read()
        f.close()
    else:
        c = False

    if content is not None:
        if configuration.read_only:
            send_backtrace("Manage key with content in 'suivi' server",
                           exception=False)
            return

        if c is False:
            c = ''
        if append:
            content = c + content
        else:
            if not reduce_ok and len(content) < len(c)*0.5:
                warn("Size not reduced for " + f1)
                return c
        if content != c: # Write if modified (non-existant files are empty)
            f = open(f1, 'w')
            f.write(content)
            f.close()
    return c

@add_a_lock
def manage_key(dirname, key, separation=3, content=None, reduce_ok=True,
               append=False, delete=False):
    """
    Store the content in the key and return the old content or False

    The write is not *process* safe.
    """
    key = key.replace('/.', '/_')
    if key is '':
        return False
    c = manage_key_real(os.path.join(configuration.db, dirname),
                        key, separation, content, reduce_ok, append, delete)
    if configuration.backup:
        d = manage_key_real(os.path.join(configuration.backup
                                         + configuration.db, dirname),
                            key, separation, content, reduce_ok, append)
        if c != d:
            send_backtrace('normal=%s\nbackup=%s\n' % (repr(c), repr(d)),
                           'manage key backup' + key, exception=False)
    return c

def key_mtime(dirname, key, separation=3):
    """Return the modification time of the key"""
    try:
        return os.path.getmtime(os.path.join(configuration.db, dirname,
                                             key[:separation], key))
    except OSError:
        return 0

        
def charte(login, year=None, semester=None):
    if year == None:
        year, semester = configuration.year_semester
    return os.path.join(login, 'charte_%s_%s' % (str(year), semester))

def charte_signed(login, server=None, year=None, semester=None):
    from . import signature
    if server:
        year = server.year
        semester = server.semester
    # For the old files
    if manage_key('LOGINS', charte(login, str(year), semester)):
        return True
    year = int(year)
    qs = signature.get_state(login)
    for q in qs.get_by_content('suivi_student_charte'):
        if year_semester_from_date(q.date) == (year, semester):
            return q.answer
    # Not found : add the question only for the current semester
    if year_semester_from_date(time.strftime("%Y%m")) == (year, semester):
        server.the_file.write('<img src="%s/=%s/signature/-1/x">'
                              % (configuration.server_url,
                                 server.ticket.ticket) )
        time.sleep(1)

def lock_state():
    import imp
    s = 'Global Python import locked: %s\n' % imp.lock_held()
    for f in lock_list:
        if f.the_lock.locked():
            s += 'Locked   '
        else:
            s += 'Unlocked '
        s += '%s [%s]\n' % (f.fct.func_name, f.fct.__module__)
    return s

def on_kill(dummy_x, dummy_y):
    sys.stderr.write('=' * 79 + '\n' +
                     'KILLED\n' +
                     '=' * 79 + '\n' +
                     'LOCKS\n' +
                     '-' * 79 + '\n' +
                     lock_state() +
                     '=' * 79 + '\n'
                     'THREADS\n' +
                     '-' * 79 + '\n' +
                     '\n'.join(t.stack() for t in thread_list) +
                     '=' * 79 + '\n'
                     )
    traceback.print_stack()
    sys.exit(0)

def print_lock_state_clean_cache():
    while True:
        
        f = open(os.path.join('LOGS', 'xxx.locks.%d' % os.getpid()), 'w')
        f.write(lock_state())
        f.close()

        for cache in caches:
            cache.clean(cache)
            
        time.sleep(60)

class Useles(object):
    closed = False
    def close(self):
        self.closed = True
    def flush(self):
        pass
    def write(self, dummy_txt):
        raise ValueError('write on Useles')

    # For socket replacement
    def sendall(self, dummy=None):
        pass
    def shutdown(self,dummy=None):
        pass

Useles = Useles()


class Variables(object):
    """Map variables to a TOMUSS configuration table stored in 0/Variables/group

    The default group is the name of the module using Variables.

    Usage Example :

    V = Variables({'foo': ('foo comment', 'default_value'),
                   'bar': ('bar comment', 5),
                   })
    print V.foo

    Beware :
       * The V.foo access time is long.
       * The V.foo value will change if the user modify
         the table 0/Variables/group
       * The user may only enter values of the same type.
         With the example, only integer values are allowed
       * The table is filled only when it is used (V.foo will do it)

    """
    _initialized = False
    
    def __init__(self, variables, group=None):
        self.__dict__['_variables'] = variables
        if group is None:
            group = sys._getframe(1).f_code.co_filename
            group = group.split(os.path.sep)[-1].replace('.py', '')
        
        self.__dict__['_group'] = group
        # Can't create the table here: catch 22

    def __iter__(self):
        return self._variables.keys()

    def items(self):
        for k in self._variables:
            yield k, getattr(self, k)

    def __getattr__(self, name):
        from . import document
        # '_' to remove ambiguity between 'Variables' template
        # and the table template.
        t = document.table(0, "Variables", '_' + self._group)
        if t and t.modifiable and not self._initialized:
            ro = t.pages[0]
            rw = t.pages[1]
            t.lock()
            try:
                for k, v in self._variables.items():
                    new_line = k not in t.lines
                    t.cell_change(ro, '0', k, v[0])
                    t.cell_change(ro, '1', k, v[1].__class__.__name__)
                    if new_line:
                        t.cell_change(rw, '2', k, repr(v[1]))
            finally:
                t.unlock()
            self.__dict__["_initialized"] = True
        if t is None  or   name not in t.lines:
            try:
                return self._variables[name][1]
            except KeyError:
                raise AttributeError(name)
        return ast.literal_eval(t.lines[name][2].value)

    def __setattr__(self, name, value):
        raise AttributeError("Edit the Variable table to change parameters")

@add_a_lock
def _(msgid, language=None):
    "Translate the message (local then global dictionary)"
    if language is None:
        language = (configuration.language, 'en', 'fr')
    else:
        language = tuple(language) + (configuration.language, 'en', 'fr')
    if _.language != language:
        _.language = language
        try:
            _.loc_tr = gettext.translation('tomuss',
                                           os.path.join('LOCAL',
                                                        'LOCAL_TRANSLATIONS'),
                                           language)
        except IOError:
            _.loc_tr = None
        _.glo_tr = gettext.translation('tomuss', 'TRANSLATIONS', language)

    if _.loc_tr:
        tr = _.loc_tr.gettext(msgid)
        if tr != msgid:
            return tr
    return _.glo_tr.gettext(msgid)

_.language = None

def __(txt):
    return unicode(_(txt), 'utf-8')

import BaseHTTPServer


class FakeRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """
    """
    please_do_not_close = False
    # 0.3 is too short for tablets
    timeout = 0.5 # For Opera that does not send GET on HTTP request
    it_is_a_post = False
    do_profile = False

    def do_POST(self):
        self.it_is_a_post = True
        self.do_GET()

    def get_posted_data(self):
        if not self.it_is_a_post:
            return None
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        if ctype != 'multipart/form-data':
            warn("ctype=%s" % ctype)
            return None
        return cgi.parse_multipart(self.the_rfile, pdict)
            
    def send_response(self, i, comment=None):
        if comment:
            # To answer HEAD request no handled
            BaseHTTPServer.BaseHTTPRequestHandler.send_response(self,i,comment)
            return
        BaseHTTPServer.BaseHTTPRequestHandler.send_response(self, i)
        # Needed for HTTP/1.1 requests
        self.send_header('Connection', 'close')
        self.wfile.flush()

    def backtrace_html(self):
        s = repr(self) + '\nRequest started %f seconds before\n' % (
            time.time() - self.start_time, )
        if hasattr(self, 'start_time_old'):
            s+= 'Authentication started %f seconds before\n' % (
            time.time() - self.start_time, )
        s += '<h2>SERVER HEADERS</h2>\n'
        for k,v in self.headers.items():
            if k != 'authorization':
                s += '<b>' + k + '</b>:' + cgi.escape(str(v)) + '<br>\n'
        s += '<h2>SERVER DICT</h2>\n'
        for k,v in self.__dict__.items():
            if k != 'headers':
                s += '<b>' + k + '</b>:' + cgi.escape(str(v)) + '<br>\n'
        return s

    def address_string(self):
        """Override to avoid DNS lookups"""
        return "%s:%d" % self.client_address

    def log_time(self, action, **keys):
        try:
            self.__class__.log_time.im_func(self, action, **keys)
        except TypeError:
            self.__class__.log_time.__func__(self, action, **keys)

    def do_not_close_connection(self):
        self.wfile = Useles
        self.the_rfile = self.rfile
        self.rfile = Useles
        self.please_do_not_close = True
        try:
            # self.request is self.connection
            # self.rfile is self.wfile
            self.the_sock = self.request._sock
            self.connection._sock = Useles
            self.request._sock = Useles
            self.the_fp = self.headers.__dict__['fp']
            self.headers.__dict__['fp'] = Useles
        except AttributeError:
            # Before Python 2.7
            pass

    def restore_connection(self):
        self.wfile = self.the_file
        self.rfile = self.the_rfile
        self.please_do_not_close = False
        try:
            self.request._sock = self.the_sock
            self.headers.__dict__['fp'] = self.the_fp
        except ValueError:
            # Before Python 2.7
            pass

    def close_connection_now(self):
        self.the_file.close()
        try:
            self.the_rfile.close()
            self.the_fp.close()
            self.the_sock.close()
        except AttributeError:
            pass

    def unsafe(self):
        if 'unsafe=1' in self.path:
            return True
        else:
            return False

    def _(self, msgid):
        return _(msgid, self.ticket.language.split(','))

    def __(self, msgid):
        return unicode(self._(msgid), "utf-8")

def start_threads():
    start_new_thread_immortal(print_lock_state_clean_cache, ())


def start_job(fct, seconds):
    """In a new thread 'fct' will be called in 'seconds'.
    If the same 'fct' is started multiple times, only the first one
    is taken into account.
    
    This function is NOT SAFE, because if a job is started while the function
    is on its way out, it will not be restarted.
    To be safe, protect the test ending the function as in:
    
        my_fct.safe_to_check = False
        while list_of_thing_to_do:
             my_fct.safe_to_check = True
             work
             my_fct.safe_to_check = False
    """
    if getattr(fct, 'job_in_file', False):
        for dummy_i in range(100):
            if fct.safe_to_check:
                return
        send_backtrace(repr(fct), "start job never safe_to_check")
        return

    def wait():
        time.sleep(seconds)
        try:
            fct()
        finally:
            fct.job_in_file = False
            fct.safe_to_check = True
    if fct.__doc__:
        wait.__doc__ = ('Wait %d before running:\n\n' % seconds) + fct.__doc__
    fct.safe_to_check = True
    fct.job_in_file = True
    start_new_thread(wait, ())

    
def display_stack_on_kill():
    import signal
    signal.signal(signal.SIGTERM, on_kill)

def init(launch_threads=True):
    if launch_threads:
        start_threads()
    display_stack_on_kill()
    configuration.ampms_full = [
        unicode(ampm, 'utf-8') for ampm in eval(_("MSG_ampms_full"))]
    s = ""
    for k in ("yes", "no", "abi", "abj", "pre", "tnr", "ppn"):
        configuration.__dict__[k] = _(k)
        s += "var %s = %s, " % (k, js(_(k)))
        k_short = k + '_short'
        if _(k_short) != k_short:
            s += "%s = %s, " % (k_short, js(_(k_short)))
            configuration.__dict__[k_short] = _(k_short)
        k += "_char"
        configuration.__dict__[k] = _(k)
        s += "%s = %s;\n" % (k, js(_(k)))
    s += "var COL_TITLE_0_2 = %s;\n" % js(_("COL_TITLE_0_2"))
    s += "var server_language = %s ;\n" % js(configuration.language)
    from . import files # Here to avoid circular import
    files.files['types.js'].append("utilities.py", s)
    files.files['auth_close.html'] = StaticFile(
        'auth_close.html',
        content=_("MSG_authentication_close")
        + '<script>window.close();</script>')
    files.files['allow_error.html'] = StaticFile(
        'allow_error.html',
        content=_("TIP_violet_square"))
    files.files['ip_error.html'] = StaticFile(
        'ip_error.html',
        content=_("ip_error.html"))
    files.add('PLUGINS', 'suivi_student_charte.html')

if __name__ == "__main__":
    def square(g):
        print 'square', g
        return g*g
    square = add_a_cache(square)
    print square(6)
    print square(7)
    print square(8)
    print square(7)
    print square(6)

    def square(g):
        print 'square', g
        return g*g
    square = add_a_cache(square, not_cached=64)
    print square(7)
    print square(7)
    print square(8)
    print square(8)

    class X:
        @add_a_method_cache
        def square(self, g):
            print 'square', g
            return g*g
    xx = X()
    xx.square(10)
    xx.square(10)
    xx.square(20)
            

    def xxx(g):
        if g <= 1:
            return 1
        return g * xxx(g-1)

    print xxx(1)
    print xxx(2)
    xxx = add_a_lock(xxx)
    print xxx(1)
    print xxx(2)

    

        
