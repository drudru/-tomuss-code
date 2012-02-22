#!/usr/bin/python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2008-2011 Thierry EXCOFFIER, Universite Claude Bernard
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

import time
import re
import os
import sys
import traceback
import configuration
import cgi
import threading
import shutil

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
        warn('acquired', what='debug')
        try:
            r = f.fct(*arg, **keys)
        finally:
            f.the_lock.release()
            warn('released', what='debug')
        return r
    f.fct = fct
    f.the_lock = threading.Lock()
    f.__doc__ = fct.__doc__
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
    append_file.the_lock.acquire()
    try:
        global filename_to_bufferize, filename_buffer
        if filename_to_bufferize:
            append_file_unlocked(filename_to_bufferize,
                                 ''.join(filename_buffer))
        filename_to_bufferize = filename
        filename_buffer = []
    finally:
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
    x = '%c %13.2f %s %s\n' % (what[0].upper(), time.time(), x, text)
    sys.stderr.write(x)
    global live_log
    if live_log:
        try:
            live_log.write(x)
        except:
            live_log = None

def send_mail(to, subject, message, frome=None, show_to=False):
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
    header += "Subject: " + subject + '\n'
    if len(to) == 1:
        header += "To: " + to[0] + '\n'
    elif show_to:
        for tto in to:
            header += "To: " + tto + '\n'
            
        
    if message.startswith('<html>'):
        header += 'Content-Type: text/html; charset=UTF-8\n'
    if isinstance(message, unicode):
        header += 'Content-Type: text/plain; charset=UTF-8\n'
        message = message.encode('utf-8')
    
    while True:
        try:
            smtpresult = send_mail.session.sendmail(frome, recipients,
                                                    header + '\n' + message)
            break
        except smtplib.SMTPRecipientsRefused:
            warn("Can't deliver mail to " + repr(recipients))
            break
        except:
            send_mail.session = smtplib.SMTP(configuration.smtpserver)

    try:
        if smtpresult:
            errstr = ""
            for recip in smtpresult.keys():
                errstr += """Ne peut pas envoyer le message a: %s
    Le serveur a répondu : %s
    %s""" % (recip, smtpresult[recip][0], smtpresult[recip][1])

            send_mail.session = None
            return errstr
    except:
        return 'BUG dans utilities.send_mail'

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
                    warn('strptime', what='error')
                    time.sleep(0.1)
            while True:
                warn('Call ' + self.fct.func_name)
                try:
                    self.fct(*self.args)
                except:
                    warn("Exception in " % self, what="Error")
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
    while True:
        time.sleep(0.25)
        if len(send_mail_in_background_list) == 0:
            continue
        send_mail(*send_mail_in_background_list.pop(0))


def send_mail_in_background(to, subject, message, frome=None):
    send_mail_in_background_list.append((to, subject, message, frome))



def js(t):
    if isinstance(t, basestring):
        # return repr(unicode(t,'utf8').encode('latin1'))
        return '"' + t.replace('\\','\\\\').replace('"','\\"').replace('>','\\x3E').replace('<','\\x3C').replace('&', '\\x26').replace('\r\n','\n').replace('\r','').replace('\n','\\n') + '"'
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

def mkpath(path):
    s = ''
    for i in path.split(os.path.sep):
        s += i + os.path.sep
        try:
            os.mkdir(s)
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
    return safe(student)

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
    s = '<tr><td class="name"><A href="file:/%s">%s</A><td class="line">%s<td>\n' % (
        frame.f_code.co_filename,
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
    warn(subject + '\n' + s, what='error')

    send_mail_in_background(configuration.maintainer, subject,
                            '<html><style>TABLE TD { border: 1px solid black;} .name { text-align:right } PRE { background: white ; border: 2px solid red ;}</style><body>' + s + '</body></html>')


class StaticFile(object):
    """Emulate a string, but it is a file content"""
    mimetypes = {'html': 'text/html;charset=utf8',
                'css': 'text/css;charset=utf8',
                'png': 'image/png',
                'ico': 'image/png',
                'gif': 'image/gif',
                'js': 'application/x-javascript;charset=utf8',
                'txt': 'text/plain',
                'xml': 'application/rss+xml;charset=utf8',
                }
    _url_ = 'http://???/'
                
    def __init__(self, name, mimetype=None, translate=None):
        self.name = name
        if mimetype == None:
            if '.' in name:
                n = name.split('.')[-1]
                if n == 'gz':
                    n = name.split('.')[-2]
                mimetype = self.mimetypes[n]
        self.mimetype = mimetype
        self.content = None
        self.time = 0
        self.append_text = {}
        self.replace_text = {}
        if translate is None:
            if name.endswith('.js') or name.endswith('.html'):
                # It is stupid to replace every time
                # But configuration order is tricky.
                translate = lambda x: x.replace('_URL_', StaticFile._url_)
            else:
                translate = lambda x: x

        self.translate = translate

    def __str__(self):
        if self.content == None or self.time != os.path.getmtime(self.name):
            self.time = os.path.getmtime(self.name)
            content = read_file(self.name)
            for old, new in self.replace_text.values():
                content = content.replace(old, new)
            content += ''.join(self.append_text.values())
            self.content = content

        return self.translate(self.content)

    def __len__(self):            
        return len(str(self))

    def replace(self, key, old, new):
        """The replacement is done each time the file is reloaded"""
        self.replace_text[key] = (old, new)

    def append(self, key, content):
        """The append is done each time the file is reloaded"""
        self.append_text[key] = content

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
    def f(fct=fct, timeout=timeout):
        cache = f.cache
        if time.time() - cache[1] > f.timeout:
            cache = (fct(), time.time())
            f.cache = cache
        return cache[0]
    f.cache = ('', 0)
    register_cache(f, fct, timeout, 'add_a_cache0')
    f.clean = clean_cache0
    return f

def clean_cache(f):
    for key, value in f.cache.items():
        if time.time() - value[1] > f.timeout:
            del f.cache[key]

def add_a_cache(fct, timeout=None, not_cached='neverreturnedvalue'):
    """Add a cache to a function with one parameter.
    If the returned value is 'not_cached' then it is not cached."""
    if timeout is None:
        timeout = 3600
    def f(x, fct=fct, timeout=timeout, not_cached=not_cached):
        cache = f.cache.get(x, ('',0))
        if time.time() - cache[1] > timeout:
            cache = (fct(x), time.time())
            
        if cache[0] == not_cached:
            return not_cached
        else:
            f.cache[x] = cache
            return cache[0]
    f.cache = {}
    register_cache(f, fct, timeout, 'add_a_cache')
    f.clean = clean_cache
    return f

def add_a_method_cache(fct, timeout=None, not_cached='neverreturnedvalue'):
    """Add a cache to a method with one parameter.
    If the returned value is 'not_cached' then it is not cached.
    The CACHE IS COMMON TO EVERY INSTANCE of the class"""
    if timeout == None:
        timeout = 3600
    def f(self, x, fct=fct, timeout=timeout, not_cached=not_cached):
        cache = f.cache.get(x, ('',0))
        if time.time() - cache[1] > timeout:
            cache = (fct(self, x), time.time())
            
        if cache[0] == not_cached:
            return not_cached
        else:
            f.cache[x] = cache
            return cache[0]
    f.cache = {}
    register_cache(f, fct, timeout, 'add_a_method_cache')
    f.clean = clean_cache
    return f


def unload_module(m):
    if m not in sys.modules:
        return
    del(sys.modules[m])
    del(sys.modules['.'.join(m.split('.')[:-1])].__dict__[m.split('.')[-1]])

def import_reload(filename):
    mtime = os.path.getmtime(filename)
    name = filename.split(os.path.sep)
    name[-1] = name[-1].replace('.py','')
    module_name = '.'.join(name)
    module = __import__(module_name)
    mtime_pyc =  os.path.getmtime(filename + 'c')
    to_reload = mtime > mtime_pyc
    if to_reload:
        unload_module(module_name)
        module = __import__(module_name)
    for item in name[1:]:
        module = module.__dict__[item]
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
               if ( e.readyState === "loaded" )
                   continue ;
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

def manage_key_real(dirname, key, separation=3, content=None, reduce_ok=True):
    """
    Do not use this function
    """
    if content is None and not os.path.isdir(dirname):
        return False
    try:
        mkpath(dirname)
    except OSError:
        pass
    
    f1 = os.path.join(dirname, key[:separation])
    if content is None and not os.path.isdir(f1):
        return False
    try:
        os.mkdir(f1, 0750)
    except OSError:
        pass

    if os.path.sep in key:
        key_dir = key.split(os.path.sep)[0]
        if content is None and not os.path.isdir(os.path.join(f1, key_dir)):
            return False
        try:
            os.mkdir(os.path.join(f1, key_dir), 0750)
        except OSError:
            pass

    f1 = os.path.join(f1, key)
    if os.path.exists(f1):
        f = open(f1, 'r')
        c = f.read()
        f.close()
    else:
        c = False

    if content is not None:
        if not reduce_ok and c and len(content) < len(c)*0.5:
            warn("Size not reduced for " + f1)
            return c
        
        f = open(f1, 'w')
        f.write(content)
        f.close()
    return c

@add_a_lock
def manage_key(dirname, key, separation=3, content=None, reduce_ok=True):
    """
    Store the content in the key and return the old content or False

    The write is not *process* safe.
    """
    key = key.replace('/.', '/_')
    if key is '':
        return False
    c = manage_key_real(os.path.join(configuration.db, dirname),
                        key, separation, content, reduce_ok)
    if configuration.backup:
        d = manage_key_real(os.path.join(configuration.backup
                                         + configuration.db, dirname),
                            key, separation, content, reduce_ok)
        if c != d:
            send_backtrace('normal=%s\nbackup=%s\n' % (repr(c), repr(d)),
                           'manage key backup' + key)
    return c

def charte(login, year=None, semester=None):
    if year == None:
        year, semester = configuration.year_semester
    return os.path.join(login, 'charte_%s_%s' % (str(year), semester))

def charte_server(login, server):
    return charte(login, str(server.year), server.semester)

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

def on_kill(x, y):
    sys.stderr.write('=' * 79 + '\n' +
                     'KILLED\n' +
                     '=' * 79 + '\n' +
                     lock_state() +
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

import BaseHTTPServer

class FakeRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """Used because there is only only one request handler for every request.
    And the initial TOMUSS version was not assuming this.
    A clean program must not store information in the request handler object
    """
    posted_data = None
    
    def __init__(self, *args, **keys):
        if len(args) != 1:
            BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, *args)
            return
        server = args[0]
        if 'full' in keys:
            self.__dict__.update(server.__dict__)
        else:
            self.path = server.path
            self.client_address = server.client_address
            
        self.the_path = server.the_path
        self.headers = server.headers
        self.ticket = server.ticket
        self.the_file = server.the_file
        self.start_time = server.start_time
        self.posted_data = server.posted_data
        if hasattr(server, 'start_time_old'):
            self.start_time_old = server.start_time_old
        self.server = server
        

        try:
            self.year = server.year
            self.semester = server.semester
            self.the_port = server.the_port
        except AttributeError:
            pass

    def backtrace_html(self):
        s = repr(self) + '\nRequest started %f seconds before\n' % (
            time.time() - self.start_time, )
        if hasattr(self, 'start_time_old'):
            s+= 'Authentication started %f seconds before\n' % (
            time.time() - self.start_time, )
        s += '<h2>SERVER HEADERS</h2>\n'
        for k,v in self.headers.items():
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
            self.server.__class__.log_time.im_func(self, action, **keys)
        except TypeError:
            self.server.__class__.log_time.__func__(self, action, **keys)

def start_threads():
    start_new_thread_immortal(print_lock_state_clean_cache, ())

def display_stack_on_kill():
    import signal
    import traceback
    signal.signal(signal.SIGTERM, on_kill)

def init():
    start_threads()
    display_stack_on_kill()
    start_new_thread_immortal(sendmail_thread, (), send_mail=False)

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
    x = X()
    x.square(10)
    x.square(10)
    x.square(20)
            

    def xxx(g):
        if g <= 1:
            return 1
        return g * xxx(g-1)

    print xxx(1)
    print xxx(2)
    xxx = add_a_lock(xxx)
    print xxx(1)
    print xxx(2)

    

        
