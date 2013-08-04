#!/usr/bin/python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2013 Thierry EXCOFFIER, Universite Claude Bernard
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
#    Contact: Thierry.EXCOFFIER@univ-lyon1.fr

"""
Management of student signatures.

The data is stored with manage_key in student directory.

The question added here are displayed on 'suivi' and MUST be answered.
It is a plain text question without HTML display with <pre>

The message text contains one or more {{{a possible answer}}} that
will become button. The answer is the button text.

When the student answer, a hook is called and the question will
no more be displayed.

After a number of day of timeout, the student answer will be True,
and the hook is called.

The full history is keeped.

Usage:

     add_question(login, message, hook_name, hook_data, timeout=1)

The hook_name is the name of a function in the 'configuration' module.

If the 'message' starts by 'file:FOO.html' the message will be
the content of the file files.files['FOO.html']
The message will be displayed in HTML.

"""

import os
import time
import cgi
import re
import tomuss_init
from . import utilities
from . import configuration
from . import files
from . import plugin
from . import inscrits

class Question(object):
    # If string : the student answer
    # If True : timeout on answer
    # If 0 : currently asked
    answer = 0
    answer_date = '19700101000000'
    
    def __init__(self, message, hook_name, hook_data, timeout,date,message_id):
        self.message = message
        self.hook_name = hook_name
        self.hook_data = hook_data
        self.timeout = timeout
        self.date = date
        self.message_id = message_id

    def html(self):
        if self.answer:
            button = 'disabled="true"'
        else:
            button = 'onclick="javascript:sign(this,%d)"' % self.message_id
        if self.message.startswith("file:"):
            try:
                message = str(files.files[self.message.split(':',1)[1]])
            except KeyError:
                message = self.message
        else:
            message = '<pre>' + cgi.escape(self.message) + '</pre>'
        t = (
            '<div id="message%s">' % self.message_id
            + re.sub("{{{([^}]*)}}}", '<button ' + button + '>\\1</button>',
                     message
                     )
            + '</div>')
        if self.answer:
            t = re.sub(">(" + cgi.escape(self.answer) + '<)',
                       ' style="background:#8F8">(%s)\\1' %
                       utilities.nice_date(self.answer_date),
                       t)
        return t

    def a_timeout(self):
        now = time.time()
        nb_days = (now
                   - time.mktime(time.strptime(self.date,"%Y%m%d%H%M%S"))
                   ) / 86400
        if nb_days >= self.timeout:
            return True

    def askable(self):
        return self.answer is 0 and not self.a_timeout()

    def __str__(self):
        return ''.join(repr(i)[0:12].ljust(13)
                       for i in (self.message, self.hook_name,
                                 self.hook_data, self.timeout, self.answer)
                       ).strip()

class Questions(object):
    def __init__(self, login):
        self.login = login
        self.questions = []

    def a_timeout(self):
        a_timeout = False
        for q in self.questions:
            if q.answer is 0 and q.a_timeout():
                if not configuration.read_only:
                    add_answer_unsafe(self.login, q.message_id, True)
                    a_timeout = True
        return a_timeout

    def get_by_content(self, needle):
        for q in self.questions:
            if needle in q.message:
                yield q

    def html_answered(self):
        t = []
        for q in self.questions:
            if q.answer and q.answer is not True:
                t.append('<hr>' + q.html())
        if len(t) == 0:
            return ''
        return ''.join(t)

    def html(self):
        t = []
        for q in self.questions:
            if q.askable():
                t.append('<hr>' + q.html())
        if len(t) == 0:
            return ''
        return unicode('''
<script>
function sign(t, message_id)
{
  if ( ! confirm(unescape(t.textContent)) )
     return ;
  t.parentNode.style.opacity = 0.5 ;
  var img = document.createElement('IMG') ;
  img.src = url + '/=' + ticket + '/signature/' + message_id
            + '/' + encode_uri(t.textContent) ;
  img.style.width = '20px' ;
  img.style.height = '20px' ;
  t.parentNode.insertBefore(img, t) ;
  var b = t.parentNode.getElementsByTagName('BUTTON') ;
  for(var i=0; i<b.length; i++)
     b[i].disabled = true ;

  var b = document.getElementsByTagName('BUTTON') ;
  for(var i=0; i<b.length; i++)
     if ( b[i].id != "signature_done" && ! b[i].disabled )
        return ;
  document.getElementById("signature_done").style.display = 'block' ; 
}
</script>
<h2><script>document.write(_('TITLE_signature'))</script></h2>
''' + ''.join(t) + '''<hr>
<button id="signature_done" style="display:none" onclick="location.reload()"><script>document.write(_('MSG_signature_done'))</script></button>
''', 'utf-8')
    
        
    def __str__(self):
        s = []
        for q in self.questions:
            s.append(str(q))
        return '\n'.join(s)

def add_question(login, message, hook_name, hook_data, timeout=1, now=None):
    """
    The message is only text : non HTML.
    The hook_name is the name of the function in 'configuration' module
    The hook_data will be in the hook parameter when the student answer
    After 'timeout' days, the hook is called with True answer
    """
    if now is None:
        now = time.strftime("%Y%m%d%H%M%S")
    qs = get_state(login)
    for q in qs.get_by_content(message):
        if  int(now) - int(q.date) < 1000:
            # Do not ask twice the same question in less than 1000 seconds
            return
    utilities.manage_key("LOGINS", os.path.join(login, "signatures"),
                         append = True,
                         content="ask(%s,%s,%s,%g,'%s')\n" % (
            repr(message), repr(hook_name), repr(hook_data), timeout, now))

@utilities.add_a_lock
def add_answer(login, message_id, value, now=None):
    add_answer_unsafe(login, message_id, value, now)
    
def add_answer_unsafe(login, message_id, value, now=None):
    """Answer is stored even if the hook does not work"""
    if now is None:
        now = time.strftime("%Y%m%d%H%M%S")
    utilities.manage_key("LOGINS", os.path.join(login, "signatures"),
                                   append = True,
                                   content="answer(%d,%s,'%s')\n" % (
            message_id, repr(value), now))
    qs = get_state(login)
    hook = getattr(configuration, qs.questions[message_id].hook_name)
    hook(login, value, qs.questions[message_id].hook_data)

    
def get_state(login):
    qs = Questions(login)

    def ask(message, hook_name, hook_data, timeout, date):
        qs.questions.append(Question(message, hook_name, hook_data, timeout,
                                     date, len(qs.questions)))
    def answer(message_id, value, date):
        qs.questions[message_id].answer = value
        qs.questions[message_id].answer_date = date

    fct = {'ask': ask, 'answer': answer}
    content = utilities.manage_key("LOGINS", os.path.join(login,"signatures"))
    if content:
        for line in content.split('\n'):
            if line:
                eval(line, fct)
        if not configuration.read_only and qs.a_timeout():
            return get_state(login)
                
    return qs


def signature(server):
    if server.the_year == -1:
        # Because 'suivi' server can not write keys
        add_question(server.ticket.user_name, "file:suivi_student_charte.html",
                     "do_nothing", '', timeout=30)
    else:
        add_answer(server.ticket.user_name, int(server.the_year),
                   server.something)
    server.the_file.write(files.files['ok.png'])

plugin.Plugin('signature', '/signature/{Y}/{?}', function=signature,
              group="!staff",
              mimetype='image/png',
              priority = -10 # Before student_redirection
              )

def signatures(server):
    if server.ticket.is_a_teacher:
        login = server.the_student
    else:
        login = server.ticket.user_name
    qs = get_state(login)
    server.the_file.write(
        '<h1>' + login + ' '
        + ' '.join(inscrits.L_fast.firstname_and_surname(login)).encode('utf-8')
        + '<br>'
        + server._("TITLE_signatures") + '</h1>'
        + qs.html_answered()
        )

plugin.Plugin('signatures', '/signatures/{I}', function=signatures)


def test_hook(login, value, data):
    print '*'*99, login, value, data
    test_hook.login = login
    test_hook.value = value
    test_hook.data = data
configuration.test_hook = test_hook

def test():

    def check(expected):
        qs = str(get_state("p0000000"))
        if qs != expected:
            print 'Expected:', expected
            print 'Result:  ', qs
            raise ValueError("bug")
        
    utilities.manage_key("LOGINS", os.path.join("p0000000","signatures"),
                         content="")
    check('')
    add_question("p0000000", "bla bla<b>l&gt;dqf", 'test_hook', 'YYY')
    check("'bla bla<b>l 'test_hook'  'YYY'        1            0")
    add_question("p0000000", "question 2", 'test_hook', 'ZZZ', 0.)
    # Timeout on question 2
    check("'bla bla<b>l 'test_hook'  'YYY'        1            0\n'question 2' 'test_hook'  'ZZZ'        0            True")
    assert(test_hook.login == "p0000000")
    assert(test_hook.value == True)
    assert(test_hook.data == "ZZZ")
    add_answer("p0000000", 0, "YES")
    check("'bla bla<b>l 'test_hook'  'YYY'        1            'YES'\n'question 2' 'test_hook'  'ZZZ'        0            True")
    assert(test_hook.login == "p0000000")
    assert(test_hook.value == "YES")
    assert(test_hook.data == "YYY")
    add_question("p0000000", "file:ok.png", 'test_hook', 'TTT', 1.)
    add_answer("p0000000", 2, "OUI")
    assert(str(files.files['ok.png']) in get_state("p0000000").html_answered())
    print 'Tests are fine'

def translate_chartes_to_signatures():
    import glob
    print "WAIT, IT'S LONG..."
    message = "file:suivi_student_charte.html"
    content = utilities.read_file(os.path.join('PLUGINS',
                                               'suivi_student_charte.html'))
    answer = content.split('{{{')[1].split("}}}")[0]
    todo = []
    for filename in sorted(glob.glob(
            os.path.join(configuration.db, 'LOGINS', '*', '*', 'charte_*_*')
            )):
        parts = filename.split(os.path.sep)
        login = parts[3]
        now = os.path.getmtime(filename)
        now = time.strftime("%Y%m%d%H%M%S", time.localtime(now))
        print login,
        todo.append((now, login, filename))

    for now, login, filename in sorted(todo):
        add_question(login, message, "do_nothing", '', timeout=99999, now=now)
        q = tuple(get_state(login).get_by_content(message))[-1]
        add_answer(login, q.message_id, answer, now)
        utilities.unlink_safe(filename)
        print login, now

   
if __name__ == "__main__":
    tomuss_init.terminate_init()
    import sys
    if len(sys.argv) == 1:
        test()
    elif sys.argv[1] == 'translate':
        translate_chartes_to_signatures()
