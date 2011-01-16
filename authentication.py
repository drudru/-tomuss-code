#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2008,2009 Thierry EXCOFFIER, Universite Claude Bernard
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

import cgi
import time
import utilities
import inscrits
import sys
import ticket
import socket
import sender
import configuration
import urllib2

warn = utilities.warn

def canonize(s):
    return s.replace('%','%25')
    # ? is very special
    return urllib2.quote(s)

last_mail_sended = 0

#REDEFINE
# From the CAS ticket and the service required by client,
# returns the login name of the user.
def ticket_login_name(ticket_key, service):

    service = canonize(service)
    checkparams = "?service=" + service + "&ticket=" + ticket_key
    warn('Ask CAS: %s' % service, what="auth")
    i = 0
    while True:
        try:
            casdata = urllib2.urlopen("%s/validate?service=%s&ticket=%s" % (
                configuration.cas, service, ticket_key))
            break
        except urllib2.URLError:
            warn('CAS : %s' % sys.exc_info()[0], what="auth")
            if i == 1: # Retry only once
                global last_mail_sended
                # No more than one mail per minute.
                if time.time() - last_mail_sended > 60:
                    utilities.send_backtrace('CAS Error', exception=False)
                    last_mail_sended = time.time()
                return False
            time.sleep(i)
            i += 1

    warn('CAS opened', what="auth")
    test = casdata.readline().strip()
    warn('CAS answer: %s' % test, what="auth")

    if test == 'yes':
        login_name = casdata.readlines()[0].strip().lower()
    else:
        casdata.read()
        login_name = False
        
    casdata.close()
    return login_name

#REDEFINE
# This function is called when the browser does not give a valid ticket.
# The browser is redirected on the CAS authentification service.
def ticket_ask(server, server_url, service):
    service = canonize(service)
    server.send_response(307)
    server.send_header('Location',
                       '%s/login?service=%s' % (
                           configuration.cas,
                           service))
    server.end_headers()
    return None, None

#REDEFINE
# If the user is connected, the function returns the ticket object
# and a clean path.
# If the user is not connected, it is redirected to the
# authentication service.
def get_path(server, server_url):
    
    ticket_key, path = ticket.get_ticket_string(server)
    ticket_object = ticket.get_ticket_objet(ticket_key)
    # Ticket OK
    if ticket_object != None:
        warn('fast ticket:%s' % str(ticket_object)[:-1], what='auth')
        warn('fast path: %s' % str(path), what='auth')
        return ticket_object, path

    # 2.8.10
    service = server_url.replace('/=TICKET','') + '/' + '/'.join(path)
    service = service.split('?ticket=')[0].split('&ticket')[0]
    service = service.replace('?','%3F')
    service = canonize(service)
    warn('SERVICE: %s TICKET: %s' % (service, ticket_key), what="auth")

    if ticket_key != None:
        sender.send_live_status('<script>b("/CAS");</script>\n')
        s = time.time()
        user_name = ticket_login_name(ticket_key, service)
        s = time.time() - s
        sender.send_live_status(
            '<script>d("%s","/CAS","",%6.4f,"%6.4fs","","","");</script>\n' %
            (configuration.cas, s, s))

        warn('username: %s' % user_name, what="auth")
        if user_name:
            t = ticket.add_ticket(ticket_key, user_name,
                                  ticket.client_ip(server),
                                  server.headers["User-Agent"])

            if path and path[0] == 'allow':
                warn('allow request for ticket : ' + path[1], what="auth")
                if path[1] not in ticket.tickets \
                       or ( ticket.tickets[path[1]].user_name == user_name
                            and ticket.tickets[path[1]].user_browser == server.headers["User-Agent"]
                            ):
                    ticket.tickets[path[1]] = ticket.tickets[ticket_key]
                    ticket.tickets[path[1]].ticket = path[1]
                    del ticket.tickets[ticket_key] # DO NOT CALL REMOVE METHOD
                    server.send_response(200)
                    server.send_header('Content-Type', 'text/html')
                    server.end_headers()
                    server.wfile.write('Vous pouvez <a href="javascript:window.close()">fermer</a> cette page.<script>window.close();</script>')
                else:
                    server.send_response(200)
                    server.send_header('Content-Type', 'text/html')
                    server.end_headers()
                    server.wfile.write('There is a problem...')
                    utilities.send_backtrace('bad allow request',
                                             exception=False)
                return None, None

            # If it is a student, no need to redirect it to the good URL
            if len(user_name) > 2 and user_name[1].isdigit():
                return t, path

            # We want the client to see the "good" url
            try:
                server.send_response(307)
            except AttributeError:
                warn("Can't redirect", what='error')
                return None, None
            if '=TICKET' in server_url:
                location = '%s/%s' % (
                    server_url.replace('=TICKET', '=' + ticket_key),
                    '/'.join(path))
            else:
                location = '%s/=%s/%s' % (
                    server_url, ticket_key, '/'.join(path))

            server.send_header('Location', location.strip('/'))
            server.end_headers()
            return None, None

    warn("No or bad ticket: Redirect the browser", what="auth")
    ticket_ask(server, server_url, service)
    return None, None

import referent
import document

authentication_requests = []

authentication_redirect = None

def authentication_thread():
    ticket.remove_old_files()
    while True:
        time.sleep(0.1)
        while len(authentication_requests):
            x = authentication_requests.pop()
            while not x.wfile.closed:
                time.sleep(0.01)
            # now it is safe because the Handler has closed the file
            x.wfile = x.the_file
            tick = x.ticket
            try:
                what = 'init'
                if tick == None:
                    what = 'no-ticket'
                    x.ticket, x.the_path = get_path(x, authentication_redirect)
                    tick = x.ticket
                    if tick == None:
                        x.wfile.close()
                        x.log_time('redirection')
                        continue # Redirection done
                
                what = 'is-teacher?'
                tick.is_a_teacher = inscrits.is_a_teacher(tick.user_name)
                
                if tick.is_a_teacher:
                    what = 'is-administrative?'
                    tick.is_an_administrative = inscrits.is_an_administrative(tick.user_name)
                    what = 'is-abj-master?'
                    tick.is_an_abj_master = inscrits.is_an_abj_master(
                        tick.user_name)
                    what = 'is-referent-master?'
                    tick.is_a_referent_master = referent.is_a_referent_master(tick.user_name)
                    what = 'password-ok?'
                    tick.password_ok = inscrits.password_ok(tick.user_name)
                    what = 'is-referent?'
                    tick.is_a_referent = inscrits.is_a_referent(tick.user_name)
                        
                else:
                    tick.is_an_abj_master     = False
                    tick.is_a_referent_master = False
                    tick.is_a_referent        = False
                    tick.is_an_administrative = False
                    tick.password_ok          = True

                x.log_time('authentication')
                x.start_time = time.time()

                what = 'send-answer'
                x.do_GET_real_real_safe()
                what = 'close'
                x.wfile.close()
            except (IOError, socket.error):
                utilities.send_backtrace(
                    '', subject = 'AUTH '+ what + ' ' + str(tick)[:-1])


def run_authentication():
    utilities.start_new_thread_immortal(authentication_thread, ())
