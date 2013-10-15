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

import time
import socket
from . import utilities
from . import inscrits
from . import ticket
from . import sender
from . import plugin
from . import configuration

warn = utilities.warn

# To synchronize with JavaScript encode_uri and decode_uri_option
def canonize(s):
    return (s.replace("$", "$24").replace('?','$3F').replace('#','$23')
            .replace("/", "$2F").replace("&", '$26').replace(".", '$2E')
            .replace("+", '$2B').replace(" ", "$20").replace("\n", "$0A")
            .replace("\r", "$0D")
            )

def redirect(server, url):
    server.send_response(307)
    server.send_header('Location', url)
    server.end_headers()
    if server.please_do_not_close:
        server.the_file.close()
    else:
        server.close_connection_now()

def ticket_login_name(ticket_key, service, server=None):
    return configuration.authenticator.login_from_ticket(ticket_key,
                                                         service, server)

def ticket_ask(server, dummy_server_url, service):
    redirect(server, configuration.authenticator.redirection(service, server))
    return None, None

def get_path(server, server_url):
    """
    If the user is connected, the function returns the ticket object
    and a clean path.
    If the user is not connected, it is redirected to the
    authentication service.
    """
    ticket_key, path = ticket.get_ticket_string(server)
    escaped_path = '/'.join(canonize(i) for i in path)
    ticket_object = ticket.get_ticket_objet(ticket_key, server)
        
    # Ticket OK
    if ticket_object:
        warn('fast ticket:%s' % str(ticket_object)[:-1], what='auth')
        path = server_url + '/=' + ticket_object.ticket +'/'+ escaped_path
        warn('fast path: %s' % str(path), what='auth')
        return ticket_object, path

    if ticket_object is not None:
        ticket_key = None # Because this ticket is not fine
    
    # 2.8.10
    service = server_url + '/' + escaped_path.split('?')[0] + '?unsafe=1'
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
                    redirect(server, utilities.StaticFile._url_
                             + '/auth_close.html')
                else:
                    redirect(server, utilities.StaticFile._url_
                             + '/allow_error.html')
                    utilities.send_backtrace('bad allow request',
                                             exception=False)
                return None, None

            return t, path

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
            redirect_loc = authentication_redirect
                    
            try:
                if not x.ticket:
                    x.ticket, dummy_the_path = get_path(x, redirect_loc)
                    if x.ticket == None:
                        x.log_time('redirection')
                        continue # Redirection done

                update_ticket(x.ticket)
                # The request can be executed
                try:
                    plugin.dispatch_request(x)
                except AttributeError:
                    utilities.send_backtrace(str(x.ticket)[:-1],
                                             subject = 'Authentication aborted:' + x.path)
                if not x.please_do_not_close:
                    x.close_connection_now()
                    
            except (AttributeError, IOError, socket.error):
                utilities.send_backtrace(
                    '', subject = 'AUTH '+ str(x.ticket)[:-1])

def run_authentication():
    utilities.start_new_thread_immortal(authentication_thread, ())

def ok(server):
    # Don't want to be blocked by authentication
    if server.ticket and hasattr(server.ticket, 'password_ok'):
        return True

    # Problem with the request with an ever changing IP
    if server.ticket is False:
        redirect(server, utilities.StaticFile._url_ + '/ip_error.html')
        return
    
    warn('Append to authentication queue', what="auth")
    # The Connection:close is sent by send_response to please HTTP/1.1
    server.do_not_close_connection()
    authentication_requests.append(server)

