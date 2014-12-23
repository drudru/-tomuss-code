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

"""
Defines the authentication methods. One per class
Currently :
   * CAS authenticator
   * OpenID authenticator
   * Unix password authenticator (With Apache and BasicAuth in .htaccess)
   * FaceBook Connect

Beware, ticket_from_url method must be fast and never freeze.

login_from_ticket can call other web services and lag a couple of seconds.
"""

import httplib
import urllib2
import time
import random
import cgi
import sys

real_regtest = 'real_regtest' in sys.argv

last_mail_sended = 0

class Authenticator(object):
    ticket_name = 'ticket' # Parameter name in the come back URL
    
    def __init__(self, provider, realm):
        self.provider = provider
        self.realm = realm

    def ticket_from_url(self, server):
        """The ticket or None"""
        try:
            form = cgi.parse_qs(server.path.split('?')[-1])
            return form[self.ticket_name][0]
        except (KeyError, IndexError):
            return

    def logout(self, dummy_server):
        """Logout only from TOMUSS, not other services"""
        return

class CAS(Authenticator):
    def login_from_ticket(self, ticket_key, service, dummy_server):
        """Return False on bad ticket.
        The login if it is ok
        """
        i = 0
        while True:
            try:
                casdata = urllib2.urlopen("%s/validate?service=%s&ticket=%s" %(
                    self.provider, service, ticket_key))
                break
            except urllib2.URLError:
                from . import utilities
                if i == 1: # Retry only once
                    global last_mail_sended
                    # No more than one mail per minute.
                    if time.time() - last_mail_sended > 60:
                        utilities.send_backtrace('CAS Error', exception=False)
                        last_mail_sended = time.time()
                    return False
                time.sleep(i)
                i += 1

        test = casdata.readline().strip()

        if test == 'yes':
            login_name = casdata.readlines()[0].strip().lower()
            if login_name[0].isdigit():
                login_name = "an_hacker_is_here"
        else:
            casdata.read()
            login_name = False

        casdata.close()
        return login_name

    def redirection(self, service, dummy_server):
        return '%s/login?service=%s' % (self.provider, service)

    def logout(self, dummy_server):
        return self.provider + '/logout'

class OpenID(Authenticator):
    """For example:
    configuration.cas = 'https://www.google.com/accounts/o8/id'
    """
    connector = None

    def init(self):
        if self.connector:
            return
        from openid.consumer import consumer
        from openid.extensions import ax
        # from openid.store import memstore
        self.cons = consumer.Consumer({}, None) # memstore.MemoryStore())
        self.connector = self.cons.begin(self.provider)
        ax_request = ax.FetchRequest()
        # 'http://axschema.org/contact/email',
        ax_request.add(ax.AttrInfo('http://axschema.org/contact/email',
                                   required = True))
        self.connector.addExtension(ax_request)
    
    def login_from_ticket(self, dummy_ticket_key, service, server):
        self.init()
        from openid.consumer import consumer
        # path = configuration.server_url + server.path.split('?')[0]
        d = {}
        for k, v in cgi.parse_qs(server.path.split('?')[-1]).items():
            d[k] = v[0]
        s = self.cons.complete(d, service)
        if s.status == consumer.SUCCESS:
            try:
                return d['openid.ext1.value.ext0']
            except KeyError:
                return d['openid.ax.value.email']
        else:
            return False
        
    def redirection(self, service, dummy_server):
        self.init()
        return self.connector.redirectURL(self.realm, service)

    def ticket_from_url(self, server):
        try:
            form = cgi.parse_qs(server.path.split('?')[-1])
            handle = form['openid.assoc_handle'][0]
            return '%x' % (hash(handle)*hash(handle[::-1]))
        except KeyError:
            return

try:
    import PAM
except ImportError:
    PAM = None

def password_is_good_su(login, password):
    """Check clear text password"""
    import pexpect
    from . import utilities
    p = pexpect.spawn('/bin/su -c "echo OK" %s' % utilities.safe(login))
    p.expect(':')
    p.sendline(password)
    r = p.read()
    p.close()
    return 'OK' in r

def password_is_good_PAM(login, password):
    def pam_conv(dummy_auth, dummy_query_list, dummy_userData):
        return [(password,0)]

    auth = PAM.pam()
    auth.start('passwd')
    auth.set_item(PAM.PAM_USER, login)
    auth.set_item(PAM.PAM_CONV, pam_conv)
    try:
        auth.authenticate()
        auth.acct_mgmt()
    except:
        return False
    return True

#REDEFINE
# Return True if the user password is good
def password_is_good(login, password):
    """Check clear text password"""
    if PAM:
        return password_is_good_PAM(login, password)
    else:
        return password_is_good_su(login, password)


class Password(Authenticator):
    """
    Assume Apache and .htaccess
    Check the access right using a password.
    """
    def login_from_ticket(self, dummy_ticket_key, dummy_service, server):
        auth = server.headers['authorization'].split(' ')[1].decode('base64')
        login, password = auth.split(':', 1)
        if password_is_good(login, password):
            return login
        else:
            return False

    def redirection(self, service, dummy_server):
        return service + '&ticket=%x' % random.randrange(10000000000000,
                                                         100000000000000)

class RegTest(Authenticator):
    """
    To allow /=user.name/ tickets without any testing.
    For the demo server, create a fake ticket for each IP address,
    so the interface user language is associated to the IP.

    It try to emulate a CAS answering always yes.

    Really dirty programming.
    Nothing is safe here.
    Do not use as a start point.
    """
    good_tickets = set()
    
    def login_from_ticket(self, ticket_key, dummy_service, server):
        code = ticket_key.split('-')
        if real_regtest:
            return code[0]
        from . import ticket
        if ticket_key in ticket.tickets:
            if not ticket.tickets[ticket_key].is_fine(server):
                self.good_tickets.remove(ticket_key)
                return False
        else:
            if ticket_key not in self.good_tickets:
                return False
        if len(code) == 1:
            return False
        return code[0]

    def redirection(self, service, server):
        if '?' not in service:
            service += '?auth=regtest'
        service = service.replace('$2E', '.')
        tickt = 'user.name'
        if server.path.startswith('/='):
            tickt = server.path.split('/')[1].strip('=')
        elif '?' in server.path:
            item = server.path.split('?')[1]
            if 'ticket=' in item:
                tickt = item.split("ticket=")[1]
        elif '/allow/' in server.path:
            tickt = server.path.split('/allow/')[1]
        elif hasattr(server, 'old_ticket'): # suivi.py case
            tickt = server.old_ticket
        username = tickt.split('-')[0]

        if "&create_ticket=" in server.path:
            tickt = server.path.split("&create_ticket=")[1]
            self.good_tickets.add(tickt)
            return '%s&ticket=%s' % (service, tickt)

        tickt = username + '-' + str(random.randrange(1000000000000))
        return '%s&create_ticket=%s' % (service, tickt)


class FaceBook(Authenticator):
    """
    A new app is needed with its API public and private number :
    
    configuration.cas = ('public key', 'private key')

    """
    ticket_name = 'state'

    def login_from_ticket(self, dummy_ticket_key, service, server):
        form = cgi.parse_qs(server.path.split('?')[-1])
        try:
            code = form['code'][0]
        except KeyError:
            return
        f = urllib2.urlopen(
            "https://graph.facebook.com/oauth/access_token?"
            "client_id=%s&redirect_uri=%s&client_secret=%s&code=%s" %
            (self.provider[0], service, self.provider[1], code,
            ))
        access_token = f.read()
        f.close()
        if not access_token.startswith("access_token="):
            return
        
        f = urllib2.urlopen("https://graph.facebook.com/me?" + access_token)
        user_data = f.read()
        f.close()

        conn = httplib.HTTPSConnection('graph.facebook.com')
        conn.request('DELETE', '/me/permissions?' + access_token)
        conn.getresponse()
        conn.close()
        
        return user_data.split('"username":"')[1].split('"')[0]

    def redirection(self, service, dummy_server):
        return (
            'https://www.facebook.com/dialog/oauth?client_id=%s&redirect_uri=%s&state=%x'%
            (self.provider[0], service, random.randrange(2**64))
            )
