#!/usr/bin/python3
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
import html
import cgi
import threading
import shutil
import imp
import ast
import urllib
import codecs
import email.utils
import email.header
import tomuss_init
from . import configuration

def read_file(filename, encoding="utf-8"):
    if encoding == "bytes":
        f = open(filename, "rb")
    else:
        f = open(filename, "r", encoding=encoding)
    c = f.read()
    f.close()
    return c

def write_file(filename, content, encoding="utf-8"):
    if content == None:
        warn('%s : 0' % (filename), what='debug')
        return
    warn('%s : %d' % (filename, len(content)), what='debug')
    opt = 'w'
    if encoding == "bytes":
        opt = opt + 'b'
        encoding = None
    f = open(filename + '~', opt, encoding = encoding)
    f.write(content)
    f.close()
    os.rename(filename + '~', filename)

def read_url(url):
    try:
        with urllib.request.urlopen(url) as f:
            c = f.read()
            encoding = f.headers.get_content_charset()
            if encoding:
                c = c.decode(encoding)
            else:
                try:
                    c = c.decode('utf-8')
                except UnicodeDecodeError:
                    c = c.decode('latin-1')
    except urllib.error.HTTPError as e:
        raise IOError(str(e))
    return c

def write_file_safe(filename, content):
    write_file(filename, content,"utf-8")
    if configuration.backup:
        write_file(configuration.backup + filename, content,"utf-8")

lock_list = []

def add_a_lock(fct):
    """Add a lock to a function to forbid simultaneous call"""
    def f(*arg, **keys):
        warn('[[[' + f.fct.__name__ + ']]]', what='debug')
        f.the_lock.acquire()
        try:
            r = f.fct(*arg, **keys)
        finally:
            f.the_lock.release()
        return r
    f.fct = fct
    f.the_lock = threading.Lock()
    f.__doc__ = fct.__doc__
    f.__name__ = fct.__name__
    f.__module__ = fct.__module__
    lock_list.append(f)
    return f

def append_file_unlocked(filename, content):
    """Paranoid : check file size before and after append"""
    try:
        before = os.path.getsize(filename)
    except OSError:
        before = 0
    f = open(filename, 'a', encoding = "utf-8")
    f.write(content)
    f.close()
    after = os.path.getsize(filename)
    if before + len(content.encode("utf-8")) != after:
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
    if isinstance(content,bytes):
        raise TypeError("1"*25," 128, utilities")
    if filename == filename_to_bufferize:
        filename_buffer.append(content)
    else:
        append_file_unlocked(filename, content)

def append_file_safe(filename, content):
    if isinstance(content, bytes):
        raise TypeError("1"*25," 134, utilities")
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
    return re.sub('[^0-9a-zA-Z-.@]', '_', txt)

def safe_quote(txt):
    return re.sub('[^\'0-9a-zA-Z-.@]', '_', txt)

def safe_space(txt):
    return re.sub('[^0-9a-zA-Z-. @]', '_', txt)

def safe_space_quote(txt):
    return re.sub('[^\'0-9a-zA-Z-. @]', '_', txt)

def flat(txt):
    return txt.translate("\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f ! #$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~?\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f?????Y|?????????????'u?.????????AAAAAA?CEEEEIIIIDNOOOOOXOUUUUY?Baaaaaa?ceeeeiiiionooooo??uuuuy?y")

def same(a, b):
    return flat(a).lower() == flat(b).lower()

def stable_repr(dic):
    if isinstance(dic, dict):
        t = []
        for k in sorted(dic):
            t.append("{}:{},\n".format(repr(k), repr(dic[k])))
        return '{\n' + ''.join(t) + '}'
    else:
        return '[\n' + ''.join(repr(i) + ',\n' for i in sorted(dic)) + ']'

def is_an_int(txt):
    try:
        int(txt)
        return True
    except ValueError:
        return False

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
              error_to=None, cc=()):
    "Not safe with user given subject"
    import smtplib

    if configuration.regtest :
        # XXX
        to = "marianne.tery@univ-lyon1.fr"
        frome = "marianne.tery@univ-lyon1.fr"
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
        new_to.append(addr)
    to = new_to
    if len(to) == 0:
        return
    
    header = "From: {}\n".format(frome)

    s = subject.replace('\n',' ').replace('\r',' ')
    header += "Subject: " + email.header.Header(s).encode() + '\n'
    if len(to) == 1:
        header += "To: {}\n".format(to[0])
    elif show_to:
        for tto in to:
            header += "To: {}\n".format(tto)
    for tto in cc:
        header += "CC: {}\n".format(tto)
    if reply_to:
        header += 'Reply-To: {}\n'.format(reply_to)
    if error_to:
        header += 'Error-To: {}\n'.format(error_to)
        
    if message.startswith('<html>') or message.startswith('<!DOCTYPE html>') :
        header += 'Content-Type: text/html; charset="utf-8"\n'
    else:
        if isinstance(message, str):
            header += 'Content-Type: text/plain; charset="utf-8"\n'

    header += "Date: " + email.utils.formatdate(localtime=True) + '\n'
    header += "Content-Transfer-Encoding: 8bit\n"
    header += "MIME-Version: 1.0\n"
    header += '\n'
    header = header.replace("\n", "\r\n")

    use_backup_smtp = False
    while True: # Stop only if the mail is sent
        try:
            smtpresult = send_mail.session.sendmail(
                frome, tuple(recipients) + tuple(cc),
                (header + message).encode('utf-8'))
            break
        except smtplib.SMTPRecipientsRefused:
            send_backtrace('from=%s\nrecipients=%s\nheaders=%s\nmessage=%s' %
                           (repr(frome), repr(recipients), repr(header),
                            repr(message)))
            try:
                if use_backup_smtp:
                    warn("Lost mail from %s to %s" % (
                        repr(frome), repr(recipients)), what="error")
                    break
                use_backup_smtp = True
                send_mail.session = smtplib.SMTP(configuration.smtpserver.split(' ')[1])
            except IndexError:
                warn("Lost mail (no backup SMTP server) from %s to %s" % (
                    repr(frome), repr(recipients)), what="error")
                break
            continue
        except (smtplib.SMTPServerDisconnected, smtplib.SMTPSenderRefused):
            # It is normal: connection is closed by SMTP if unused
            pass
        except:
            if send_mail.session is not None:
                send_backtrace('from=%s\nrecipients=%s\nheaders=%s' %
                               (repr(frome), repr(recipients), repr(header)))
        # Reconnect
        send_mail.session = smtplib.SMTP(configuration.smtpserver.split(' ')[0])
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
                warn('Call ' + self.fct.__name__)
                try:
                    self.fct(*self.args)
                except:
                    try:
                        warn("Exception in %s" % self, what="error")
                        if self.send_mail:
                            send_backtrace("Exception in %s" % self)
                    except:
                        pass
                if not self.immortal:
                    break
            thread_list.remove(self)
        def backtrace_html(self):
            return str(self)
        def __str__(self):
            return 'Thread immortal=%-5s send_mail=%-5s %s' % (
                   self.immortal, self.send_mail, fct.__name__)

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
    while send_mail_in_background_list:
        time.sleep(configuration.time_between_mails)
        send_mail(*send_mail_in_background_list.pop(0))
        t = time.time()
    return t

def send_mail_in_background(to, subject, message, frome=None, show_to=False,
                            reply_to=None, error_to=None, cc=()):
    send_mail_in_background_list.append((to, subject, message, frome,
                                         show_to, reply_to, error_to, cc))
    start_job(sendmail_thread, 1, important='send_mail_in_background')

def js(t):
    if isinstance(t, str):
        return '"' + t.replace('\\','\\\\').replace('"','\\"').replace('>','\\x3E').replace('<','\\x3C').replace('&', '\\x26').replace('\r','').replace('\n','\\n') + '"'
    elif isinstance(t, float):
        return '%s' % t # DO NOT USE %g: 4.9999998 => 5
    elif isinstance(t, dict):
        return '{' + ','.join("%s:%s" % (js(k), js(v))
                              for k, v in t.items()) + '}'
    elif isinstance(t, tuple):
        return str(list(t))
    elif isinstance(t, set):
        raise TypeError("not sets here")
    elif isinstance(t, bytes):
        raise TypeError("not bytes here")
    else:
        return str(t)

def js2(t):
    return '"' + t.replace('\\','\\\\').replace('"','\\"').replace('\n','\\n') + '"'

def mkpath(path, create_init=True, mode=configuration.umask):
    s = ''
    for i in path.split(os.path.sep):
        s += i + os.path.sep
        try:
            os.mkdir(s, mode)
            if create_init:
                write_file(os.path.join(s, '__init__.py'), '',"utf-8")
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
    return safe(str(student))

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
            if hasattr(v, 'backtrace_html'):
                try:
                    s += ("<p><b>" + html.escape(k) + "</b>:<br>"
                          + v.backtrace_html() + "\n")
                except TypeError:
                    pass
            displayed[id(v)] = True
    s += '</tr>'
    return s

import socket


def send_backtrace(txt, subject='Backtrace', exception=True):
    s = configuration.version
    if exception and sys.exc_info()[0] != None \
       and sys.exc_info()[0] == BrokenPipeError:
        s += '*'
    else:
        s += ' '
    s += ' '.join(sys.argv) + ' ' + subject
    subject = s
    displayed = {}
    s = ''
    if txt:
        s += ('<h1>Information reported by the exception catcher</h1><pre>' +
               html.escape(txt) + '</pre>\n')
    if exception and sys.exc_info()[0] != None:
        s += '<h1>Exception stack</h1>\n'
        s += '<p>Exception class: ' + html.escape(str(sys.exc_info()[0])) + '\n'
        s += '<p>Exception value: ' + html.escape(str(sys.exc_info()[1])) + '\n'
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
    
    f = open(filename, "a", encoding = "utf-8")
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
    import io
    zbuf = io.BytesIO()
    zfile = gzip.GzipFile(None, 'wb', 9, zbuf)
    if isinstance(buf, str):
        buf = buf.encode("utf-8")
    zfile.write(buf)
    zfile.close()
    return zbuf.getvalue()

class StaticFile(object):
    """Emulate a string, but it is a file content"""
    mimetypes = {'html': 'text/html;charset=utf-8',
                'css': 'text/css;charset=utf-8',
                'png': 'image/png',
                'ico': 'image/png',
                'jpg': 'image/jpeg',
                'gif': 'image/gif',
                'js': 'application/x-javascript;charset=utf-8',
                'txt': 'text/plain;charset=utf-8',
                'xml': 'application/rss+xml;charset=utf-8',
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
        if 'image' in self.mimetype :
            self.encoding = "bytes"
        else:
            self.encoding = "utf-8"
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
        if configuration.read_only is not None:
            return # Only TOMUSS server write on disc
        dirname = os.path.join("TMP", configuration.version)
        mkpath(dirname, mode=0o755) # The static web server needs access
        filename = os.path.join(dirname, self.name.split(os.path.sep)[-1])
        write_file(filename, self.content, self.encoding)

    def get_zipped(self):
        if self.encoding == "bytes":
            self.bytes()
        else :
            str(self)
        if self.gzipped is None:
            self.gzipped = compressBuf(self.content)
        return self.gzipped

    def bytes(self):
        assert self.encoding == 'bytes'
        if self.need_update():
            self.time = os.path.getmtime(self.name)
            self.content = read_file(self.name, self.encoding)
            self.gzipped = None
            self.copy_on_disc()
        return self.content

    def __str__(self):
        assert self.encoding != 'bytes'
        if self.need_update():
            self.time = os.path.getmtime(self.name)
            content = read_file(self.name, self.encoding)
            for old, new in self.replace_text.values():
                content = content.replace(old, new)
            content += ''.join(str(i) for i in self.append_text.values())
            if self.name.endswith('.js') or self.name.endswith('.html'):
                content = content.replace('_FILES_', configuration.url_files)
            self.content = content
            self.gzipped = None
            self.copy_on_disc()
        return self.content

    def clear_cache(self):
        if self.time != -1:
            self.content = None

    def __len__(self):
        if self.encoding == "bytes":
            return len(self.bytes())
        else:
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
    try:
        for key, value in list(f.cache.items()):
            if time.time() - value[1] > f.timeout:
                del f.cache[key]
    except RuntimeError: # dictionary changed size during iteration
        pass

def add_a_cache(fct, timeout=3600, not_cached='neverreturnedvalue',
                last_value_on_exception=False):
    """Add a cache to a function with one parameter.

    If the returned value is 'not_cached' then it is not cached.

    If the cached function may raise an exception,
    it may be interesting to set 'last_value_on_exception=True' in order
    to return the previously cached value and hide the exception.

    If 'last_value_on_exception="disk"' then the cache is stored on disk.
    So, if there is an exception on the first call,
    the last value is restored from disk.
    """
    def f(x):
        cache = f.cache.get(x, ('',0))
        # XXX The lock protect only the cache update, not the cache test.
        # So the cache may be updated twice in a row.
        if (time.time() - cache[1] > f.timeout
            and f.lock.acquire(blocking = cache[1]==0 )):
            on_disk = f.last_value_on_exception == 'disk'
            try:
                cache = (f.fct(x), time.time())
            except:
                if f.last_value_on_exception and cache[1] != 0:
                    # Do not retry immediatly
                    cache = (cache[0], time.time())
                    send_backtrace(str(f.fct), "Cache update failed")
                else:
                    if on_disk:
                        c = read_file(os.path.join(f.dirname, safe(repr(x))))
                        cache = (ast.literal_eval(c), time.time())
                        send_backtrace(str(f.fct), "Restore cache from disk")
                    else:
                        raise
                on_disk = False
            finally:
                f.cache[x] = cache
                if on_disk:
                    write_file(os.path.join(f.dirname, safe(repr(x))),
                               repr(cache[0]))
                f.lock.release()
        return cache[0]
    f.cache = {}
    register_cache(f, fct, timeout, 'add_a_cache')
    f.clean = clean_cache
    f.not_cached = not_cached
    f.last_value_on_exception = last_value_on_exception
    if last_value_on_exception == 'disk':
        f.dirname = os.path.join('TMP', 'CACHE', f.fct.__name__)
        mkpath(f.dirname)
    f.lock = threading.Lock()
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

def import_reload(filename):
    mtime = os.path.getmtime(filename)
    name = filename.split(os.path.sep)
    name[-1] = name[-1].replace('.py','')
    name.insert(0, 'TOMUSS')
    module_name = '.'.join(name)
    __import__(module_name) # force the .pyc creation
    old_module = sys.modules[module_name]
    mtime_pyc =  os.path.getmtime(old_module.__spec__._cached)
    to_reload = mtime > mtime_pyc
    if to_reload:
        imp.reload(old_module)
    return old_module, to_reload

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
    t = list(time.localtime()[:6])
    t[1] -= 1 # Month starts et 0 in JavaScript
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
               if ( e.readyState === "complete" )
                   continue ;
               setTimeout(recall, 1000) ;
               return ;
               }
         }
    var d = new Date%s ;
    millisec.delta = d.getTime() - millisec() + 1000 ; // 1s to load page
    return true ;
    }
         """ % str(tuple(t))



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
        self.file = open(self.filename, 'w', encoding = "utf-8")
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
    last = next(t)
    i = 1
    try:
        while True:
            a = next(t)
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
    return list(zip( * ( [iter(an_iterable)]*size ) ))

    
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
        os.mkdir(f1, configuration.umask)
    except OSError:
        pass

    if os.path.sep in key:
        if content is None and not os.path.isdir(os.path.join(f1, key_dir)):
            return False
        try:
            os.mkdir(os.path.join(f1, key_dir), configuration.umask)
        except OSError:
            pass

    f1 = os.path.join(f1, key)

    if append:
        f = open(f1, 'a', encoding = "utf-8")
        f.write(content)
        f.close()
        # Do not return content because it may be large
        return

    if os.path.exists(f1):
        if delete:
            os.unlink(f1)
            return
        f = open(f1, 'r', encoding = "utf-8")
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
        if not reduce_ok and len(content) < len(c)*0.5:
            warn("Size not reduced for " + f1)
            return c
        if content != c: # Write if modified (non-existant files are empty)
            f = open(f1, 'w', encoding = "utf-8")
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
                            key, separation, content, reduce_ok, append,
                            delete)
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

def display_preferences_get(login):
    prefs = manage_key('LOGINS', os.path.join(login, 'preferences'))
    if prefs:
        return eval(prefs)
    else:
        return {}

def lock_state():
    s = 'Global Python import locked: %s\n' % imp.lock_held()
    for f in lock_list:
        if f.the_lock.locked():
            s += 'Locked   '
        else:
            s += 'Unlocked '
        s += '%s [%s]\n' % (f.fct.__name__, f.fct.__module__)
    return s

main_thread =  threading.current_thread()

def all_the_stacks():
    me = threading.current_thread()
    frames = sys._current_frames()
    s = []
    for t in threading.enumerate():
        if t is not me:
            try:
                s.append(''.join(traceback.format_stack(frames[t.ident])))
            except KeyError:
                pass
    return '\n'.join(s)

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
                     all_the_stacks() +
                     '=' * 79 + '\n'
                     )
    traceback.print_stack()
    sys.exit(0)

def print_lock_state_clean_cache():
    while True:
        f = open(os.path.join('LOGS', 'xxx.locks.%d' % os.getpid()), 'w', encoding = "utf-8")
        f.write(lock_state() + '\n\n')
        f.write(all_the_stacks())
        f.close()

        for cache in caches:
            cache.clean(cache)

        time.sleep(60)

class Variables(object):
    """Map variables to a TOMUSS configuration table stored in 0/Variables/group

    The default group is the name of the module using Variables.

    Usage Example :

    V = Variables({'foo': ('foo comment', 'default_value'),
                   'bar': ('bar comment', 5),
                   })
    print(V.foo)

    Beware :
       * There is no overhead on V.foo access (except on value change)
       * The V.foo value will change if the user modify
         the table 0/Variables/group
       * The user may only enter values of the same type.
         With the example, only integer values are allowed for 'bar'
       * The table is filled only when it is used (V.foo will do it)
    """
    def __init__(self, variables, group=None):
        self.__dict__['_variables'] = variables
        if group is None:
            group = sys._getframe(1).f_code.co_filename
            group = group.split(os.path.sep)[-1].replace('.py', '')
        
        self.__dict__['_group'] = group
        # Can't create the table here: catch 22

    def __iter__(self):
        return (key
                for key in self.__dict__
                if not key.startswith('_')
                )

    def _clean_(self):
        for k in tuple(iter(self)):
            self.__dict__.pop(k)

    def __getattr__(self, name):
        from . import document
        # '_' to remove ambiguity between 'Variables' template
        # and the table template.
        t = document.table(0, "Variables", '_' + self._group)
        if t and t.modifiable:
            rw = t.pages[1]
            t.lock()
            try:
                for k, v in self._variables.items():
                    new_line = k not in t.lines
                    t.cell_change(rw, '0', k, v[0], force_update=True)
                    t.cell_change(rw, '1', k, v[1].__class__.__name__,
                                  force_update=True)
                    if new_line:
                        t.cell_change(rw, '2', k, repr(v[1]))
            finally:
                t.unlock()
            t.variables.add(self)
        for k, v in t.lines.items():
            try:
                self.__dict__[k] = ast.literal_eval(v[2].value)
            except SyntaxError:
                self.__dict__[k] = None
        return self.__dict__[name]

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

import http.server

class HTTPServer(http.server.HTTPServer):
    old_shutdown_request = http.server.HTTPServer.shutdown_request

    def shutdown_request(self, request):
        return

class FakeRequestHandler(http.server.BaseHTTPRequestHandler):
    """
    """
    please_do_not_close = False
    # 0.3 is too short for tablets
    timeout = 0.5 # For Opera that does not send GET on HTTP request
    it_is_a_post = False
    do_profile = False

    def test(self, depth=3, node=None):
        if node is None:
            node = self
        if depth == 0:
            return
        if not hasattr(node, "__dict__"):
            return
        for k, v in node.__dict__.items():
            if isinstance(v, socket.SocketIO):
                print(k, v)
        for k, v in node.__dict__.items():
            self.test(depth-1, v)

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()

    def do_POST(self):
        self.wfile.write = self.wfile._sock.sendall
        self.it_is_a_post = True
        self.do_GET()

    def get_field_storage(self, size=50000000):
        if not self.it_is_a_post:
            return None
        return cgi.FieldStorage(fp=self.rfile, headers=self.headers,
                                environ={'REQUEST_METHOD' : 'POST'})

    def get_posted_data(self, size=50000000):
        """Provide compatibility for the old usage.
        Do not use: it takes a lot of memory.
        """
        fs = self.get_field_storage(size)
        if fs is None:
            return None
        d = {}
        for k in fs.keys():
            d[k] = [fs.getfirst(k, '')]
        return d

    #def send_response(self, i, comment=None):
        #if comment:
            ## To answer HEAD request no handled
            #http.server.BaseHTTPRequestHandler.send_response(self,i,comment)
            #return
        #http.server.BaseHTTPRequestHandler.send_response(self, i)
        ## Needed for HTTP/1.1 requests
        #self.send_header('Connection', 'close')
        ## self.wfile.flush()

    def backtrace_html(self):
        s = repr(self) + '\nRequest started %f seconds before\n' % (
            time.time() - self.start_time, )
        if hasattr(self, 'start_time_old'):
            s+= 'Authentication started %f seconds before\n' % (
            time.time() - self.start_time, )
        s += '<h2>SERVER HEADERS</h2>\n'
        for k,v in self.headers.items():
            if k != 'authorization':
                s += '<b>' + k + '</b>:' + html.escape(str(v)) + '<br>\n'
        s += '<h2>SERVER DICT</h2>\n'
        for k,v in self.__dict__.items():
            if k != 'headers' and k != 'uploaded':
                s += '<b>' + k + '</b>:' + html.escape(str(v)) + '<br>\n'
        return s

    def address_string(self):
        """Override to avoid DNS lookups"""
        return "%s:%d" % self.client_address

    def log_time(self, action, **keys):
        try:
            self.__class__.log_time.__func__(self, action, **keys)
        except TypeError:
            self.__class__.log_time.__func__(self, action, **keys)

    def do_not_close_connection(self):
        self.please_do_not_close = True
        def close(file=self.wfile, old_close=self.wfile.close):
            # If the thread run the job before the request is handled
            # The flush is called by the Python library on a closed file.
            setattr(file, 'flush', lambda:True)
            if file._sock:
                file._sock.close()
            old_close()
        self.wfile.close = close

    def close_connection_now(self):
        sock = self.wfile._sock
        if sock:
            self.server.old_shutdown_request(sock)
        http.server.BaseHTTPRequestHandler.finish(self)
        self.please_do_not_close = True

    old_finish = http.server.BaseHTTPRequestHandler.finish
    def finish(self):
       if not self.please_do_not_close:
            self.old_finish()

    def unsafe(self):
        if 'unsafe=1' in self.path:
            return True
        else:
            return False

    def _(self, msgid):
        return _(msgid, self.ticket.language.split(','))

#    def __(self, msgid):
#        return str(self._(msgid), "utf-8")

def start_threads():
    start_new_thread_immortal(print_lock_state_clean_cache, ())

@add_a_lock
def start_job(fct, seconds, important=None):
    """
    If needed: run 'fct' in 'seconds' in a new thread.

    'fct' returns its completion time (the time just before the last work checking)
    or None if it is assumed that completion time is: now - 0.01 second

    A new thread is started only if the current job is completed.
    So the number of 'fct' call can be less than the number of 'start_job' call.

    'fct' may take more than 'seconds' to execute.

    The minimum time between 'fct' end and next start is 'seconds'
    """
    fct.last_request = time.time()
    if getattr(fct, 'processing', False):
        return

    def wait():
        while fct.processing:
            time.sleep(seconds)
            t = None
            try:
                t = fct()
            finally:
                if t is None:
                    # -0.01 to be sure the function was not on its way out
                    t = time.time() - 0.01
                start_job.the_lock.acquire()
                if fct.last_request < t:
                    fct.processing = False
                    if important:
                        important_job_remove(important)
                start_job.the_lock.release()
    if fct.__doc__:
        wait.__doc__ = ('Wait %d before running:\n\n' % seconds) + fct.__doc__
    fct.processing = True
    if important:
        important_job_add(important)
    start_new_thread(wait, ())


current_jobs = set()
no_more_important_job = False

def important_job_add(job_name):
    current_jobs.add(job_name)
    while no_more_important_job:
        time.sleep(0.1)

def important_job_remove(job_name):
    current_jobs.remove(job_name)

def important_job_running():
    """If it returns None, no more important job are allowed and
    it is safe to stop TOMUSS"""
    global no_more_important_job
    no_more_important_job = True
    if current_jobs:
        no_more_important_job = False
        return True



def display_stack_on_kill():
    import signal
    signal.signal(signal.SIGTERM, on_kill)

def init(launch_threads=True):
    if launch_threads:
        start_threads()
    display_stack_on_kill()
    configuration.ampms_full = [
        ampm for ampm in eval(_("MSG_ampms_full"))]
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
    configuration.or_keyword = _('or')
    s += "function or_keyword() { return %s; }" % js(_('or'))
    s += "var COL_TITLE_0_2 = %s;\n" % js(_("COL_TITLE_0_2"))
    s += "var server_language = %s ;\n" % js(configuration.language)
    s += "var special_days = %s ;\n" % js(configuration.special_days)
    s += "var allowed_grades = %s ;\n" % js(configuration.allowed_grades)
    from . import files # Here to avoid circular import
    files.files['types.js'].append("utilities.py", s)
    files.files['allow_error.html'] = StaticFile(
        'allow_error.html',
        content=_("TIP_violet_square"))
    files.files['ip_error.html'] = StaticFile(
        'ip_error.html',
        content=_("ip_error.html"))
    files.add('PLUGINS', 'suivi_student_charte.html')

def start_as_daemon(logdir):
    mkpath(logdir)
    logname = time.strftime('%Y-%m-%d_%H:%M:%S')
    start_as_daemon.log = open(os.path.join(logdir, logname), "w")
    os.dup2(start_as_daemon.log.fileno() ,1)
    sys.stderr = sys.stdout
    loglink = os.path.join(logdir, 'log')
    if os.path.islink(loglink):
        os.unlink(loglink)
    os.symlink(logname, loglink)

    pid = os.path.join(logdir, 'pid')
    write_file(pid, str(os.getpid()))

    # atexit can be called and the process can fail to exit.
    # In this case, the PID must remain in order to allow crontab_run.py
    # to kill the process.
    # So the next lines are commented.
    # import atexit
    # atexit.register(os.unlink, pid)

class ProgressBar:
    """Insert a progress bar in the generated HTML.

    pb = utilities.ProgressBar(server, message="<h1>Title</h1>")
    pb.update(n, n_max)
    pb.hide()
    """
    nr = 0
    last_update = 0

    def __init__(self, server, message = "", auto_hide = False,
                 show_numbers = True):
        self.server = server
        self.html_id = "progressbar{}".format(self.nr)
        self.auto_hide = auto_hide
        self.show_numbers = show_numbers
        ProgressBar.nr += 1
        server.the_file.write('''
<div><div>{}</div>
<div style="border:2px solid black;">
<div id="{}" style="background:#8F8; border-right: 2px solid #080">&nbsp;</div>
</div></div>'''.format(message, self.html_id))

    def update(self, nb, nb_max):
        now = time.time()
        if now - self.last_update > 1 or nb == nb_max:
            if self.show_numbers:
                more = "x.innerHTML = '{}/{}' ;".format(nb, nb_max)
            else:
                more = ""
            self.server.the_file.write("""<script>
            var x = document.getElementById('{}') ;
            x.style.width = '{}%' ;
            {}
            </script>""".format(self.html_id, 100 * nb / nb_max, more))
            self.server.the_file.flush()
            self.last_update = now
        if self.auto_hide and nb >= nb_max:
            self.hide()

    def append_to_message(self, text):
        self.server.the_file.write("""<script>
        var x = document.getElementById('{}').parentNode.parentNode.firstChild;
        x.innerHTML += {} ;
        </script>""".format(self.html_id, js(text)))
        self.server.the_file.flush()

    def hide(self):
        self.server.the_file.write("""<script>
        var x = document.getElementById('{}').parentNode.parentNode ;
        x.parentNode.removeChild(x) ;
        </script>""".format(self.html_id))
        self.server.the_file.flush()

    def wait_mail_sent(self):
        try:
            last = send_mail_in_background_list[-1]
        except IndexError:
            last = None
        nb_mails = len(send_mail_in_background_list)

        while True:
            try:
                pos = send_mail_in_background_list.index(last)
            except ValueError:
                pos = 0
            try:
                self.update(nb_mails - pos, nb_mails)
            except:
                break
            if pos == 0:
                break
            time.sleep(1)

# Remove files and directories in background

_cleanup_list = []
def _cleanup():
    while _cleanup_list:
        try:
            name = _cleanup_list.pop()
            if name.startswith('/') or '..' in name:
                send_backtrace("Bad filename cleanup: " + name)
                continue
            if os.path.isdir(name):
                shutil.rmtree(name)
            else:
                os.unlink(name)
        except IOError:
            pass
        except OSError:
            pass

def remove_this(filename):
    _cleanup_list.append(filename)
    start_job(_cleanup, 1)
