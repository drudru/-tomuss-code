#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2008-2014 Thierry EXCOFFIER, Universite Claude Bernard
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

import os
import time
import html
import urllib.request, urllib.parse, urllib.error
from . import utilities
from . import configuration

warn = utilities.warn

def client_ip(server):
    try:
        # In case of proxy
        ip = server.headers["x-forwarded-for"]
        try:
            # Take the first IP
            return utilities.safe(ip.split(",")[0])
        except IndexError:
            return utilities.safe(ip)
    except AttributeError:
        return utilities.safe(server.client_address[0])

class Ticket(object):
    def __init__(self, ticket, user_name=None, user_ip=None,
                 user_browser=None, date=None, language=''):
        self.ticket = ticket
        self.user_name = user_name
        self.user_ip = user_ip
        self.user_browser = user_browser
        if date == None:
            self.date = time.time()
        else:
            self.date = date
        self.set_language(language)

    def set_language(self, lang):
        self.language = lang.lower().replace(';',',').replace('-','_')

    def is_member_of(self, group):
        return configuration.is_member_of(self.user_name, group)

    # Compatibility with old code
    is_a_teacher         = property(lambda x:x.is_member_of('staff'))
    is_an_abj_master     = property(lambda x:x.is_member_of('abj_masters'))
    is_a_referent_master = property(lambda x:x.is_member_of('referent_masters'))
    is_a_referent        = property(lambda x:x.is_member_of('referents'))
    is_an_administrative = property(lambda x:x.is_member_of('administratives'))
        
    def is_fine(self, server):
        # print self.user_name, (time.time() - self.date) , configuration.ticket_time_to_live, self.user_ip, client_ip(server), self.user_browser, server.headers["user-agent"]
        if (configuration.regtest
            and self.user_name == self.ticket
            and self.user_ip == client_ip(server)
            ):
            return True
        user_browser = server.headers.get("user-agent", '')
        if user_browser == '':
            utilities.send_mail_in_background(
                configuration.maintainer,
                'BUG TOMUSS: No user Agent !',
                'user_ip = %s, client_ip = %s, user_name = %s' % (
                self.user_ip,
                client_ip(server),
                self.user_name))

        return (self.user_name != None
                and (time.time() - self.date) < configuration.ticket_time_to_live
                and self.user_ip == client_ip(server)
                and self.user_browser == user_browser
                )

    def log(self):
        return 'add(' + \
               repr(self.ticket) + ',' + repr(self.user_name) + \
               ',' + repr(self.user_ip) + ',' + repr(self.user_browser) + \
               ',' + repr(self.date) + ')\n'

    def remove_file(self):
        try:
            os.unlink(os.path.join(configuration.ticket_directory, self.ticket))
        except IOError:
            pass
        except OSError:
            pass

    def remove(self):
        """Remove all the tickets of the user to avoid problems"""
        warn('Remove ticket : %s' % self, what="auth")
        user = self.user_name
        for key, value in get_items():
            if value.user_name == user:
                tickets[key].remove_this_ticket()

    def remove_this_ticket(self):
        """Expired ticket"""
        warn('Remove this ticket : %s' % self, what="auth")
        self.date = 0
        self.remove_file()

    def access_right(self):
        if not hasattr(self,'is_a_teacher'):
            return '?????'
        s = ''
        if self.is_a_teacher:
            s += 'T'
        if self.is_an_abj_master:
            s += 'J'
        if self.is_a_referent_master:
            s += 'R'
        if self.is_a_referent:
            s += 'r'
        if self.is_an_administrative:
            s += 'A'
        if getattr(self, 'password_ok', False):
            s += 'P'
        return s

    def __str__(self):
        return self.log()

    def backtrace_html(self):
        return html.escape(self.log())

class Anonymous:
    language = configuration.language
    ticket = "none"
    user_name = "anonymous"

# A class is better....
tickets = {}

def add(ticket, user_name, user_ip, user_browser, date=None, language=''):
    t = Ticket(ticket, user_name, user_ip, user_browser, date, language)
    tickets[ticket] = t
    return t

def add_ticket(ticket, user_name, user_ip, user_browser, language=''):
    get_ticket_objet.the_lock.acquire()
    t = add(ticket, user_name, user_ip, user_browser, language=language)
    get_ticket_objet.the_lock.release()
    utilities.write_file(os.path.join(configuration.ticket_directory, t.ticket), t.log())
    return t

def get_items():
    with get_ticket_objet.the_lock:
        return tuple(tickets.items())

def get_values():
    with get_ticket_objet.the_lock:
        return tuple(tickets.values())

def get_ticket_string(server):
    """Extract from the path the ticket as a string (or None) and the path"""
    warn('PATH: %s' % server.path, what='auth')
    if server.path.startswith("/="):
        path = server.path.split("/")
        ticket = path[1][1:]
        path = path[2:]
    else:
        ticket = configuration.authenticator.ticket_from_url(server)
        path = server.path.split("?")[0].lstrip('/').split('/')

    if ticket:
        ticket = ticket.replace("/", "_").replace("&", "_").replace("?", "_").replace("%", "_")
    return ticket, [urllib.parse.unquote(x)
                    for x in path]

def clone(ticket_key, ticket):
    return Ticket(ticket_key,
                  ticket.user_name, ticket.user_ip, ticket.user_browser,
                  ticket.date, ticket.language)

def remove_old_tickets():
    """Remove old tickets from memory"""
    if time.time() - remove_old_tickets.time < configuration.ticket_time_to_live/10:
        return
    remove_old_tickets.time = time.time()

    assert(get_ticket_objet.the_lock.locked)
    global tickets
    t = {}
    for ticket in tickets.values():
        if (time.time() - ticket.date) > configuration.ticket_time_to_live \
               or ticket.user_name == '':
            ticket.remove_file()
        else:
            t[ticket.ticket] = ticket

    tickets = t
    
remove_old_tickets.time = time.time()

def remove_old_files():
    """Remove old tickets from disc.
    It should be done because TOMUSS may crash without cleaning
    """
    for filename in os.listdir(configuration.ticket_directory):
        filename = os.path.join(configuration.ticket_directory, filename)
        try:
            if time.time() - os.path.getmtime(filename) \
                   > configuration.ticket_time_to_live:
                os.unlink(filename)
        except OSError:
            pass

@utilities.add_a_lock
def get_ticket_objet(ticket, server, check_ticket=True):
    """Get the ticket object from the ticket string
       * None if no ticket
       * False if ticket invalid to quickly
       * 0 if ticket not fine
    """
    
    if ticket == None:
        warn('No ticket', what='auth')
        return None
    if ticket not in tickets:
        warn('Unknown ticket: ' + ticket, what='auth')
        ticket_file = os.path.join(configuration.ticket_directory, ticket)
        try:
            # Update 'tickets' table with 'add' function
            eval( utilities.read_file(ticket_file))
            warn('Found in file', what='auth')
        except OSError:
            pass
        except IOError:
            pass

    remove_old_tickets()

    ticket_object = tickets.get(ticket, None)

    if ticket_object  and check_ticket and not ticket_object.is_fine(server):
        warn('TICKET NOT FINE : %.3f secs, %s %s %s' % (
                time.time() - ticket_object.date,
                str(ticket_object).strip(),
                client_ip(server), server.headers.get("user-agent", ''))
             )
        for k, v in server.headers.items():
            warn('%s : %s' % (k, v))
        
        if time.time() - ticket_object.date < 2:
            return False
        return 0
    if ticket_object and ticket_object.language == '':
        ticket_object.set_language(server.headers.get('accept-language',''))
    return ticket_object 
