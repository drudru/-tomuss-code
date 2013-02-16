#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2008-2013 Thierry EXCOFFIER, Universite Claude Bernard
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

import sys
import time
import socket
import urllib2
from . import utilities
from . import inscrits
from . import ticket
from . import sender
from . import configuration

warn = utilities.warn

# To synchronize with JavaScript encode_uri and decode_uri_option
def canonize(s):
    return (s.replace("$", "$24").replace('?','$3F').replace('#','$23')
            .replace("/", "$2F").replace("&", '$26').replace(".", '$2E')
            .replace("+", '$2B').replace(" ", "$20")
            )

last_mail_sended = 0

#REDEFINE
# Return True if the user password is good
def password_is_good(login, password):
    """Check clear text password"""
    import pexpect
    p = pexpect.spawn('/bin/su -c "echo OK" %s' % utilities.safe(login))
    p.expect(':')
    p.sendline(password)
    r = p.read()
    p.close()
    return 'OK' in r

#REDEFINE
# From the CAS ticket and the service required by client,
# returns the login name of the user.
def ticket_login_name(ticket_key, service, server=None):
    if not configuration.cas:
        # Not CAS: assume Apache and .htaccess
        auth = server.headers['authorization'].split(' ')[1].decode('base64')
        login, password = auth.split(':', 1)
        if password_is_good(login, password):
            return login
        else:
            return False

#    service = canonize(service)
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
def ticket_ask(server, dummy_server_url, service):
#    service = canonize(service)
    if not configuration.cas:
        # Assume you are using .htaccess and Apache
        import random
        server.send_header('Location', service + '?ticket='
                           + str(random.randrange(1000000000000,
                                                  10000000000000)) )
    else:
        server.send_header('Location',
                           '%s/login?service=%s' % (
                configuration.cas,
                service))
    server.end_headers()
    server.close_connection_now()
    return None, None

#REDEFINE
# If the user is connected, the function returns the ticket object
# and a clean path.
# If the user is not connected, it is redirected to the
# authentication service.
def get_path(server, server_url):
    
    ticket_key, path = ticket.get_ticket_string(server)
    escaped_path = '/'.join(canonize(i) for i in path)
    ticket_object = ticket.get_ticket_objet(ticket_key, server)
        
    # Ticket OK
    if ticket_object != None:
        warn('fast ticket:%s' % str(ticket_object)[:-1], what='auth')
        if '/=TICKET' in server_url:
            path = server_url.replace('TICKET',
                                      ticket_object.ticket
                                      ) + '/' + escaped_path
        else:
            path = server_url + '/=' + ticket_object.ticket +'/'+ escaped_path
        warn('fast path: %s' % str(path), what='auth')
        return ticket_object, path

    # 2.8.10
    service = server_url.replace('/=TICKET','') + '/' + escaped_path
    service = service.split('?ticket=')[0].split('&ticket')[0]
    warn('SERVICE: %s TICKET: %s' % (service, ticket_key), what="auth")

    if ticket_key != None:
        sender.send_live_status('<script>b("/CAS");</script>\n')
        s = time.time()
        user_name = ticket_login_name(ticket_key, service, server)
        s = time.time() - s
        sender.send_live_status(
            '<script>d("%s","/CAS","",%6.4f,"%6.4fs","","","");</script>\n' %
            (configuration.cas, s, s))

        warn('username: %s' % user_name, what="auth")
        if user_name:
            t = ticket.add_ticket(
                ticket_key, user_name, ticket.client_ip(server),
                server.headers["user-agent"],
                language=server.headers.get('accept-language',''))

            if path and path[0] == 'allow':
                warn('allow request for ticket : ' + path[1], what="auth")
                if path[1] not in ticket.tickets \
                       or ( ticket.tickets[path[1]].user_name == user_name
                            and ticket.tickets[path[1]].user_browser
                                == server.headers["user-agent"]
                            ):
                    # Update the old ticket
                    ticket.tickets[path[1]] = ticket.clone(path[1], t)
                    server.send_header('Location', utilities.StaticFile._url_
                                       + '/auth_close.html'
                                       )
                    server.end_headers()
                    server.close_connection_now()
                else:
                    server.send_header('Location', utilities.StaticFile._url_
                                       + '/allow_error.html'
                                       )
                    server.end_headers()
                    server.close_connection_now()
                    utilities.send_backtrace('bad allow request',
                                             exception=False)
                return None, None

            # XXX
            # If it is a student, no need to redirect it to the good URL
            # if len(user_name) > 2 and user_name[1].isdigit():
            #     return t, path

            # We want the client to see the "good" url
            if '=TICKET' in server_url:
                location = '%s/%s' % (
                    server_url.replace('=TICKET', '=' + ticket_key),
                    escaped_path)
            else:
                location = '%s/=%s/%s' % (server_url, ticket_key, escaped_path)

            server.send_header('Location', location.strip('/'))
            server.end_headers()
            server.close_connection_now()
            return None, None

    warn("No or bad ticket: Redirect the browser", what="auth")
    ticket_ask(server, server_url, service)
    return None, None

authentication_requests = []

authentication_redirect = None

def update_ticket(tick):
    if tick.is_member_of('staff'):
        tick.password_ok = inscrits.L_fast.password_ok(tick.user_name)
    else:
        tick.password_ok = True
        
def authentication_thread():
    """The send_response 307 (redirection) is yet done"""
    ticket.remove_old_files()
    while True:
        time.sleep(0.1)
        while len(authentication_requests):
            x = authentication_requests.pop()
            while not x.wfile.closed or not x.rfile.closed:
                time.sleep(0.01)
            # now it is safe because the Handler has closed the file
            x.restore_connection()
            try:
                if not x.ticket:
                    x.ticket, x.the_path = get_path(x, authentication_redirect)
                    if x.ticket == None:
                        x.log_time('redirection')
                        continue # Redirection done
                x.send_header('Location',
                              get_path(x,authentication_redirect)[1])
                x.end_headers()
                x.close_connection_now()
                # After redirection to not delay it
                update_ticket(x.ticket)

            except (AttributeError, IOError, socket.error):
                utilities.send_backtrace(
                    '', subject = 'AUTH '+ str(x.ticket)[:-1])

def run_authentication():
    utilities.start_new_thread_immortal(authentication_thread, ())

def ok(server):
    # Don't want to be blocked by authentication
    if server.ticket and hasattr(server.ticket, 'password_ok'):
        return True

    # Redirect the client to not block the others
    server.send_response(307)

    # Problem with the request with an ever changing IP
    if server.ticket is False:
        server.send_header('Location', utilities.StaticFile._url_
                           + '/ip_error.html'
                           )
        server.end_headers()
        return
    
    warn('Append to authentication queue', what="auth")
    # The Connection:close is sent by send_response to please HTTP/1.1
    server.do_not_close_connection()
    authentication_requests.append(server)

