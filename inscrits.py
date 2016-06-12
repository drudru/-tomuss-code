#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet)
#    Copyright (C) 2008-2016 Thierry EXCOFFIER, Universite Claude Bernard
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

import tomuss_init
import ldap3
import ssl
import re
import time
import threading
from . import configuration
from . import utilities
from . import sender

ldap3.LDAPTimeLimitExceededResult = 5

warn = utilities.warn

safe_re = re.compile('[^0-9a-zA-Z-. _]')
def safe(txt):
    """Values safe in an LDAP request"""
    if not isinstance(txt, str):
        return ''
    return safe_re.sub('_', txt)

class LDAP_Logic(object):
    def member_of(self, groupe, base=configuration.ou_students):
        """Iterator over the members of a group"""
        alls = self.query(base=base,
                          search='(memberOf=%s)' % groupe,
                          attributes=(configuration.attr_login,
                                      configuration.attr_firstname,
                                      configuration.attr_surname,
                                      configuration.attr_mail,
                                      configuration.attr_login_alt,
                                      'memberOf')
                          )
        for i in alls:
            i = i[1]
            login = login_from_ldap(i)

            if configuration.attr_mail not in i:
                i[configuration.attr_mail] = (login,)     

            yield (login_to_student_id(login),
                   i[configuration.attr_firstname][0],
                   i[configuration.attr_surname][0],
                   i[configuration.attr_mail][0],
                   i['memberOf']
                   )
    def get_ldap_ues(self):
        """Full list of UE"""
        dues = {}
        ues = self.query('(|(%s*)(%s*))' % (configuration.ou_ue_starts,
                                            configuration.ou_ue_starts2),
                         base=configuration.ou_groups)
        for i in [i[0] for i in ues]:
            dues[i[3:].split(' ')[0]] = True

        dues = list(dues.keys())
        dues.sort()
        return dues

    def ues_of_a_student(self, name):
        """List of UEs where the student is registered."""
        a = tuple(self.member_of_list(name))
        if len(a) == 0:
            return []
        return [aa
                for aa in a
                if (configuration.ou_ue_contains in aa)
                and (aa.startswith(configuration.ou_ue_starts)
                     or aa.startswith(configuration.ou_ue_starts2))
                ]

    def ues_of_a_student_short(self, name):
        """Extract from the OU the UE short name (code)"""
        t = [ x.replace(' ',',').split(',')[0].split('=')[1]
                 for x in self.ues_of_a_student(name)]
        t.sort()
        return t

    def ues_of_a_student_with_groups(self, name):
        """List of UEs where the student as triplets (ue, group, sequence)."""
        groups = tuple(self.member_of_list(name))
        if len(groups) == 0:
            return []
        ues = set()
        result = []
        for group in groups:
            if 'GRP-GRP' in group:
                group = group.split(',')[0].split('-')
                ue = group[-2]
                grp_seq = group[-1].split('_')
                try:
                    result.append((ue, grp_seq[0], grp_seq[1][1:]))
                except IndexError:
                    result.append((ue, grp_seq[0], ''))
                ues.add(ue)
                
        for group in groups:
            if group.startswith(configuration.ou_ue_starts) or group.startswith(configuration.ou_ue_starts2):
                ue = group.split(' ')[0][6:]
                if ue not in ues: # Do not erase existing group
                    result.append((ue, '', ''))

        return result

    def get_attributes(self, login, attributes):
        """From the login of the person, retrieve the attributes"""
        if login in demo_animaux:
            a = dict(list(zip((configuration.attr_firstname,
                          configuration.attr_surname,
                          configuration.attr_mail),
                         [(i,)
                          for i in demo_animaux[login][1:4]])))
        else:
            a = self.query_login(login, attributes)
        if not a:
            a = {}
        if a.get(configuration.attr_mail) == None:
            a[configuration.attr_mail] = [str(login)] # No unicode please

        return [a.get(i, ('Inconnu',))[0] for i in attributes]
        

    def firstname_and_surname(self, login):
        """From the login of the person, retrieve the name"""
        return self.firstname_and_surname_and_mail(login)[:2]
    
    def mail(self, login):
        """From the login of the person, retrieve the mail"""
        a = self.firstname_and_surname_and_mail(login)[2]
        if a == login:
            return None
        else:
            return a

    def mails(self, logins):
        the_mails = {}
        for x in self.query_logins(
            logins,
            (configuration.attr_login, configuration.attr_mail)):
            if x[1]:
                login = login_to_student_id(x[0].lower())
                the_mails[login] = x[1]
        return the_mails

    def phone(self, login):
        "Retrieve the phone linked to the login"
        return self.get_attributes(login, (configuration.attr_phone,))[0]

    def phone_from_logins(self, logins):
        "Retrieve the phones linked to the logins"
        d = {}
        for login,phone in self.query_logins(logins,(configuration.attr_login,
                                                     configuration.attr_phone,
                                                     )):
            d[login.lower()] = phone
        return d

    @utilities.add_a_method_cache
    def firstname_and_surname_and_mail(self, login):
        """From the login of the person, retrieve the name and mail"""
        x = self.get_attributes(login, (configuration.attr_firstname,
                                        configuration.attr_surname,
                                        configuration.attr_mail,
                                        ))
        return [x[0], x[1], x[2]]

    get_student_info = firstname_and_surname_and_mail

    def firstname_and_surname_and_mail_from_logins(self, logins):
        """From a set of logins, retrieve the name and the mail"""
        d = {}
        for l,f,s,m in self.query_logins(logins, (configuration.attr_login,
                                                  configuration.attr_firstname,
                                                  configuration.attr_surname,
                                                  configuration.attr_mail,
                                                  )):
            d[l.lower()] = (f, s, m)
        return d
            
    # To not remake the query for firstname, surname and mails
    firstname_and_surname_and_mail_from_logins = utilities.add_a_method_cache(
        firstname_and_surname_and_mail_from_logins, timeout=10)
    
    @utilities.add_a_method_cache
    def portail(self, login):
        """From the login of the person, retrieve the portails"""
        a = self.member_of_list(login)
        return [configuration.is_a_portail(aa)
                for aa in a
                if configuration.is_a_portail(aa)]

    def portails(self, logins):
        """From the login of the person, retrieve the portails"""
        a = self.query_logins(logins,
                              attributes=('memberOf', configuration.attr_login),
                              only_first_value = False
                              )
        p = {}
        for attrs in a:
            p[attrs[configuration.attr_login][0]] = [
                configuration.is_a_portail(aa)
                for aa in attrs.get('memberOf', ())
                if configuration.is_a_portail(aa)]
        return p

    def firstname_and_surname_to_login(self, firstname, surname):
        firstname = safe(utilities.flat(firstname))
        surname = safe(utilities.flat(surname))
        aa = self.query(
            search='(|(&('+configuration.attr_surname +'='
            + surname.replace('-','*')
            + ')(' +configuration.attr_firstname + '='
            + firstname.replace('-','*')
            + '))(' + configuration.attr_login + '=' +
            firstname.replace(' ','-') + '.' + surname.replace(' ','-') +
            '))',
            attributes = (configuration.attr_login, configuration.attr_mail,
                          'lastLogonTimestamp',),
            base=configuration.ou_top)
        a = []
        for x in aa: # For all the answers
            if x[0] == None:
                continue
            if configuration.attr_login not in x[1]:
                continue
            i = 0
            n = x[1][configuration.attr_login][0]
            if '.' in n:
                i += 10000
            if not n[-1].isdigit():
                i += 10001
            if ' ' not in n:
                i += 10010
            if 'lastLogonTimestamp' in x[1]:
                i += 10100
            if configuration.attr_mail in x[1]:
                i += 11000
            a.append( (i,n) )
        a.sort()
        if len(a):
            return a[-1][1].lower()

        aa = self.query_login(surname.replace(' ','-') + '.'
                             + firstname.replace(' ','-'))
        if aa:
            return aa[configuration.attr_login][0].lower()
        return None

    @utilities.add_a_method_cache
    def firstname_surname_to_login(self, firstname_surname):
        """Give a login from a firstname and a surname"""
        firstname_surname = firstname_surname.split(' ')
        for i in range(1, len(firstname_surname)):
            login = self.firstname_and_surname_to_login(' '.join(firstname_surname[:i]),
                                                   ' '.join(firstname_surname[i:]))
            if login:
                return login
        return None

    def firstname_or_surname_to_logins(self, name, base=None, attributes=None):
        """Retrieve possible logins from a surname, a firstname
        or an incomplete login (with a dot inside).
        Returns the attributes needed."""
        name = name.strip()
        if len(name) == 1:
            return
        q = []
        if ' ' in name and len(name) >= 3:
            both = '(%s=%s*)' % (configuration.attr_surname,
                                 utilities.safe_space_quote(name))
        else:
            both = ''
        for start in name.split(' '):
            start = utilities.safe_quote(start.strip())
            if start == '':
                continue
            q.append('(|(%s=%s*)(%s=%s*)(%s=%s*)%s)' % (
                configuration.attr_surname, start,
                configuration.attr_firstname, start,
                configuration.attr_login, start,
                both))
        if len(q) == 0:
            return
        q = '(&' + ''.join(q) + ')'

        if base:
            if base.startswith("CN="):
                q = '(&(memberof=' + base + ')' + q + ')'
                base = configuration.ou_top
        else:
            base = configuration.ou_top
                
        q = '(&(objectClass=person)' + q + ')' # To accelerate query

        if attributes == None:
            attributes = [configuration.attr_login,
                          configuration.attr_surname,
                          configuration.attr_firstname]
        aa = self.query(q, base=base, attributes=attributes)
        i = attributes.index(configuration.attr_login)
        if type(aa) != list : print("i"*50, " inscrit 337 aa",type(aa))
        for xx in aa :
            if type(xx) != list : print("i"*50, " inscrit 337 xx",type(xx))
            x = xx[1]
            if x.get(configuration.attr_login) == None:
                continue
            r = [x.get(attr,('',))[0]
                 for attr in attributes
                 ]
            r[i] = r[i].lower() # login must be in lower case
            yield r

    def query_logins(self, logins, attributes, only_first_value=True):
        if not logins:
            return ()
        chunk_size = 1000
        if len(logins) > chunk_size:
            r = []
            chunk = logins[:]
            n = 1 + len(logins) // int(1 + len(logins)//chunk_size)
            while chunk:
                r += self.query_logins(chunk[:n], attributes, only_first_value)
                chunk = chunk[n:]
            return r
        
        logins = ''.join(['(%s=%s)' % (configuration.attr_login,
                                      utilities.the_login(login))
                                        for login in logins
                         ])
        
        a = self.query(search='(|' + logins + ')',
                       base=configuration.ou_top, attributes=attributes
                       )
        r = []
        for i in a:
            if i[0] != None:
                i = i[1]
                if only_first_value:
                    r.append([i.get(attr,('',))[0]
                              for attr in attributes])
                else:
                    r.append(i)
        return r

    def member_of_list(self, login):
        """List of the LDAP groups containing the login"""
        r = self.query_login(login, ('memberOf',))
        if len(r) == 0:
            return ()
        return r.get('memberOf', ())
    member_of_list = utilities.add_a_method_cache(member_of_list)


    def etapes_of_student(self, login):
        """Assumes that LDAP contains OU with ' etape-XXXX' inside"""
        a = self.member_of_list(utilities.the_login(login))
        return sorted(aa.split(' etape-')[1].split(',')[0]
                for aa in a if ' etape-' in aa)

    def etapes_of_students(self, logins):
        """If possible, optimize this function"""
        d = {}
        for login in logins:
            d[login] = self.etapes_of_student(login)
        return d

    def is_in_one_of_the_groups(self, login, groups):
        """Returns true if the login is one of the groups or sub group"""
        r = self.member_of_list(login)
        for group in groups:
            for rr in r:
                if rr.endswith(group):
                    return True
        return False

    def password_ok(self, login):
        """Create a list of stupid passwords and check them"""
        # if login in configuration.root:
        #    return True

        passwords = [login] + login.split('.')
        passwords = []

        password = self.query_login(login,
                                    (configuration.attr_default_password,))
        if password:
            try:
                passwords.append(password[configuration.attr_default_password]
                                 [0])
            except KeyError:
                pass

        return not utilities.stupid_password(login, passwords)
    password_ok = utilities.add_a_method_cache(password_ok, not_cached=False)

    @utilities.add_a_method_cache
    def students(self, ue, year=None, semester=None, table=None):
        """Iterator giving the student list for an UE"""
        alls = self.query(base=configuration.ou_students,
                          search='(memberOf=*%s*)' % ue,
                          attributes=(configuration.attr_login,
                                      configuration.attr_firstname,
                                      configuration.attr_surname,
                                      configuration.attr_mail,
                                      configuration.attr_login_alt))
        for i in alls:
            i = i[1]
            yield (login_to_student_id(i[configuration.attr_login][0]),
                   i[configuration.attr_firstname][0],
                   i[configuration.attr_surname][0],
                   i[configuration.attr_mail][0],
                   '', # Group
                   '', # Sequence
                   )

class Empty(LDAP_Logic):
    """Fake LDAP handler"""
    def __init__(self, name='LDAP'):
        self.nr = 0
    def query(self, search='', attributes=None, base=''):
        self.nr += 1
        if attributes == None:
            attributes = (configuration.attr_login,)
        d = {}
        for i in attributes:
            d[i] = (i, configuration.teachers[1])
        d['base'] = base
        d['search'] = search
        return (('ldapdisabled', d),)
    def query_login(self, login, attributes=(configuration.attr_login,)):
        self.nr += 1
        if login in demo_animaux:
            d = demo_animaux[login]
            d = {configuration.attr_login: login,
                 configuration.attr_mail: [d[3]],
                 configuration.attr_surname: [d[2]],
                 configuration.attr_firstname: [d[1]],
                 'memberOf': ['CN=UE-%d,' % i + configuration.ou_ue_contains
                              for i in range(10)],
                 }
        else:
            d = {configuration.attr_login: login,
                 configuration.attr_mail: ['???@???.???'],
                 configuration.attr_surname: [login + 'surname'],
                 configuration.attr_firstname: [login + 'firstname'],
                 'memberOf': (),
                 }
        for k in attributes:
            if k not in d:
                d[k] = [k]
        return d

#REDEFINE
# This class can be replaced by a subclass of itself in order to replace
# the 'students' method returning the student list for an UE.
# The student list may be computed without using LDAP.
class LDAP(LDAP_Logic):
    """An LDAP connection."""
    connection = True
    def __init__(self):
        self.time_last_mail = 0
        self.connect()

    def connect(self):
        if ( len(configuration.ldap_server) == 0
             or configuration.ldap_server[0].endswith('.domain.org')):
            # Fake LDAP server, do not use it
            return

        servers = [
            ldap3.Server(host, configuration.ldap_server_port,
                         use_ssl = configuration.ldap_server_port in (636, 6360)
                     )
            for host in configuration.ldap_server
            ]
        # configuration.ldap_reconnect
        server_pool = ldap3.ServerPool(servers,
                                       ldap3.POOLING_STRATEGY_ROUND_ROBIN,
                                       active=True, exhaust=600)
        self.connection = ldap3.Connection(
            server_pool,
            user = configuration.ldap_server_login,
            password = configuration.ldap_server_password,
            authentication = ldap3.AUTH_SIMPLE,
            raise_exceptions = True,
            client_strategy = ldap3.STRATEGY_REUSABLE_THREADED,
            pool_size = 4,
        )
        self.connection.tls = ldap3.Tls()
        self.connection.tls.validate = ssl.CERT_NONE
        self.connection.open()
        self.connection.start_tls()
        self.connection.bind()

    def query(self, search, attributes=(configuration.attr_login,),
              base=configuration.ou_groups):
        """Returns a list of answers.
        A answer is a pair : (CN, dictionnary)
        """
        t = time.time()
        # warn('search=%s base=%s attr=%s' % (search, base, attributes) )
        if self.connection is True:
            # Fake connection
            t = {}
            for a in attributes:
                t[a] = [a + '?']
            return (('cn?',t),)
        nr_none_return = 0
        while True:
            try:
                start_time = time.time()
                sender.send_live_status('<script>b("/LDAP");</script>\n')
                msg_id = self.connection.search(
                    base, search, ldap3.SEARCH_SCOPE_WHOLE_SUBTREE,
                    time_limit = ldap3.LDAPTimeLimitExceededResult,
                    attributes=attributes)
                s = self.connection.get_response(msg_id)[0]
                t = []
                if s is None:
                    self.connect() # Assume temporary network problem
                    time.sleep(1)
                    nr_none_return += 1
                    if nr_none_return == 10:
                        utilities.send_backtrace(
                            "Attributes = %s\nRequest = %s" % (attributes,
                                                               search),
                            subject = "LDAP returns None")
                        return t
                else:
                    for line in s:
                        if 'attributes' in line:
                            t.append([line['dn'], line['attributes']])
                    sender.send_live_status(
                        '<script>d("LDAP","/LDAP","",%6.4f,%s,"","","");</script>\n' %
                        (time.time() - start_time,
                         utilities.js(search + ':' + repr(attributes))))
                    return t
            except ldap3.LDAPException as e:
                sender.send_live_status(
                    '<script>d("LDAP","/LDAP","",1,"","%s","LDAP","%s");</script>\n' %
                    (time.ctime(start_time), e.__class__.__name__))
                warn('Uncatched: %s QUERY=%s ATTRIBUTES=%s' % (
                    e.__class__.__name__,
                    search, repr(attributes)
                    ), what='error')
                if time.time() > self.time_last_mail + 10:
                    self.time_last_mail = time.time()
                    # utilities.send_backtrace(
                    #     configuration.ldap_server[self.server] + '\n'
                    #     + 'QUERY=' + search + '\n'
                    #     + 'ATTRIBUTES=' + repr(attributes) + '\n'
                    #     + 'BASE=' + base + '\n'
                    #     , subject = 'LDAP Error', exception = False)
                if isinstance(e, (
                        ldap3.core.exceptions.LDAPSizeLimitExceededResult,
                        ldap3.core.exceptions.LDAPNoSuchObjectResult)):
                    return ()
                time.sleep(1)
                self.connect() # Assume temporary network problem

    def query_login(self, login, attributes=(configuration.attr_login,),
                    star_is_safe=False):
        if ('*' in login) and not star_is_safe:
            return {}
        if not star_is_safe:
            login = utilities.the_login(login)
        a = self.query(search='(%s=%s)' % (configuration.attr_login, login),
                    base=configuration.ou_top, attributes=attributes
                    )
        if not a or a[0][0] == None:
            a = self.query(search='(%s=%s)'% (configuration.attr_login, login),
                        base=configuration.ou_top, attributes=attributes
                        )
            if a and a[0][0] != None:
                utilities.send_backtrace('THIS CODE IS USEFUL!',
                                         exception=False)
        if a and a[0][0] != None:
            if len(a[0]) >= 2:
                return a[0][1]
        return {}

L_fast  = None # Fast interactive access
L_slow  = None # Slow request interactive access
L_batch = None # Any request in a batch thread

def init():
    global L_fast, L_slow, L_batch
    utilities.warn('Create LDAP connector')
    L_fast = L_slow = L_batch = LDAP()

#REDEFINE
# If the student login in LDAP is not the same as the student ID.
# This function translate student login to student ID.
# The returned value must be usable safely.
def login_to_student_id(login):
    return utilities.safe(login)

def login_from_ldap(i):
    if configuration.attr_login_alt in i:
        return i[configuration.attr_login_alt][0]
    else:
        return i[configuration.attr_login][0]

def a_mailto(login):
    firstname, surname, mail = L_fast.firstname_and_surname_and_mail(login)
    return '<a href="mailto:%s">%s %s</a><!-- %s -->' % (
        mail, firstname.title(), surname, login)

demo_animaux = {
    'k01':('k01','Bernard' ,'BONOBO'      ,'bbonobo@africa.net'     ,'M',''),
    'k02':('k02','Georges' ,'ROUGE GORGE' ,'grouge-gorge@europe.net','O',''),
    'k03':('k03','Magalie' ,'MIGALE'      ,'mmigale@africa.net'     ,'A',''),
    'k04':('k04','Lucien'  ,'LEZARD'      ,'llezard@france.net'     ,'R',''),
    'k05':('k05','Théodore','TIGRE'       ,'ttigre@asia.net'        ,'M',''),
    'k06':('k06','Simon'   ,'SCORPION'    ,'sscorpion@africa.net'   ,'A',''),
    'k07':('k07','Cécilia' ,'CHEVAL'      ,'ccheval@europe.net'     ,'M',''),
    'k08':('k08','Tatiana' ,'TORTUE'      ,'ttortue@ocean.net'      ,'R',''),
    'k09':('k09','Ambroise','AIGLE'       ,'aaigle@america.net'     ,'O',''),
    'k10':('k10','Bill'    ,'BOA'         ,'bboa@africa.net'        ,'R',''),
    'k11':('k11','Merlin'  ,'MYRIAPODE'   ,'mmerlin@europe.net'     ,'A',''),
    'k12':('k12','Fanny'   ,'FLAMANT ROSE','fflamant-rose@europ.net','O',''),
    'k13':('k13','Olivier' ,'OURS'        ,'oours@us.net'           ,'M',''),
    }
