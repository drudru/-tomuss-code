#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet)
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


# BUG : In many places, there is missing :
#                 unicode(...., configuration.ldap_encoding)

import tomuss_init
import ldap
import re
import time
from . import configuration
from . import utilities
from . import sender

ldap.set_option(ldap.OPT_REFERRALS, 0)
ldap.set_option(ldap.OPT_NETWORK_TIMEOUT, 1) # For connect
ldap.set_option(ldap.OPT_TIMEOUT, 600)       # For reading data

warn = utilities.warn

safe_re = re.compile('[^0-9a-zA-Z-. _]')
def safe(txt):
    """Values safe in an LDAP request"""
    return safe_re.sub('', txt)

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

        dues = dues.keys()
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
            a = dict(zip((configuration.attr_firstname,
                          configuration.attr_surname,
                          configuration.attr_mail),
                         [(i.encode(configuration.ldap_encoding),)
                          for i in demo_animaux[login][1:4]]))
        else:
            a = self.query_login(login, attributes)
        if not a:
            a = {}
        if a.get(configuration.attr_mail) == None:
            a[configuration.attr_mail] = [str(login)] # No unicode please

        return [unicode(a.get(i, ('Inconnu',))[0],configuration.ldap_encoding) for i in attributes]
        

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
                login = login_to_student_id(x[0].lower()).encode('utf-8')
                the_mails[login] = x[1].encode('utf-8')
        return the_mails

    def phone(self, login):
        "Retrieve the phone linked to the login"
        return self.get_attributes(login, (configuration.attr_phone,))[0]

    @utilities.add_a_method_cache
    def firstname_and_surname_and_mail(self, login):
        """From the login of the person, retrieve the name and mail"""
        x = self.get_attributes(login, (configuration.attr_firstname,
                                        configuration.attr_surname,
                                        configuration.attr_mail,
                                        ))
        return [x[0], x[1], x[2].encode('utf8')]

    get_student_info = firstname_and_surname_and_mail

    def firstname_and_surname_and_mail_from_logins(self, logins):
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
        return [unicode(aa.split('APO-')[1].split(',')[0],
                      configuration.ldap_encoding)
                for aa in a if configuration.ou_portail_contains in aa]

    def portails(self, logins):
        """From the login of the person, retrieve the portails"""
        logins = ''.join(['(%s=%s)'
                          % (configuration.attr_login,
                             utilities.the_login(login),
                             )
                          for login in logins
                          ])
        a = self.query(search='(|' + logins + ')',
                       base=configuration.ou_top,
                       attributes=('memberOf', configuration.attr_login)
                       )
        p = {}
        for cn, attrs in a:
            if len(attrs) != 2:
                continue
            p[attrs[configuration.attr_login][0]] = [
                unicode(aa.split('APO-')[1].split(',')[0],
                        configuration.ldap_encoding)
                for aa in attrs['memberOf']
                if configuration.ou_portail_contains in aa]
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
            n = unicode(x[1][configuration.attr_login][0],
                        configuration.ldap_encoding)
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
            return unicode(aa[configuration.attr_login][0],
                           configuration.ldap_encoding).lower()
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
        for start in name.split(' '):
            start = utilities.safe_quote(start.strip())
            if start == '':
                continue
            q.append('(|(%s=%s*)(%s=%s*)(%s=%s*))' % (
                configuration.attr_surname, start,
                configuration.attr_firstname, start,
                configuration.attr_login, start))
        if len(q) == 0:
            return
        q = '(&' + ''.join(q) + ')'
        if ' ' in name and len(name) >= 3:
            q = '(|' + q + '(%s=%s*)' % (configuration.attr_surname,
                                         utilities.safe_space_quote(name))+ ')'
        if base:
            q = '(&(memberof=' + base + ')' + q + ')'

        q = '(&(objectClass=person)' + q + ')' # To accelerate query

        if attributes == None:
            attributes = [configuration.attr_login,
                          configuration.attr_surname,
                          configuration.attr_firstname]
        nr = 100 # Maximum number of answer
        aa = self.query(q,
                        base=configuration.ou_top,
                        attributes=attributes,
                        async=nr+1
                        )
        i = attributes.index(configuration.attr_login)
        for x in self.generator(aa, nr): # For all the answers
            if x.get(configuration.attr_login) == None:
                continue
            r = [unicode(x.get(attr,('',))[0],
                         configuration.ldap_encoding)  
                 for attr in attributes
                 ]
            r[i] = r[i].lower() # login must be in lower case
            yield r
        if self.connexion is not True:
            self.connexion.cancel(aa)

    def query_logins(self, logins, attributes):
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
                r.append([unicode(i.get(attr,('',))[0],
                                 configuration.ldap_encoding)
                         for attr in attributes])
        return r

    def member_of_list(self, login):
        """List of the LDAP groups containing the login"""
        r = self.query_login(login, ('memberOf',))
        if len(r) == 0:
            return ()
        return r.get('memberOf', ())
    member_of_list = utilities.add_a_method_cache(member_of_list,
                                                  not_cached=())


    def etapes_of_student(self, login):
        """Assumes that LDAP contains OU with ' etape-XXXX' inside"""
        a = self.member_of_list(utilities.the_login(login))
        return [aa.split(' etape-')[1].split(',')[0]
                for aa in a if ' etape-' in aa]

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
    def students(self, ue):
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
    """A LDAP connection.
    If a server is broken, take the next one
    """
    def __init__(self, name='LDAP'):
        self.connexion = None
        self.server = -1
        self.name = name
        self.last_query = 0
        self.time_last_mail = 0

    def connect(self):
        if ( len(configuration.ldap_server) == 0
             or configuration.ldap_server[0].endswith('.domain.org')):
            # Fake LDAP server, do not use it
            self.connexion = True
            return
        while True:
            warn('Try connect to ' + configuration.ldap_server[self.server],
                 what="ldap")
            try:
                c = ldap.open(configuration.ldap_server[self.server],
                              port=configuration.ldap_server_port)
                c.simple_bind_s(configuration.ldap_server_login,
                                configuration.ldap_server_password)
                warn('Connect done', what="ldap")
                self.connexion = c
                
                return
            except ldap.SERVER_DOWN:
                warn('Can not connect to %s: SERVER_DOWN'
                     % configuration.ldap_server[self.server], what="error")
                self.server = (self.server + 1) % len(configuration.ldap_server)
            except ldap.TIMEOUT:
                warn('Can not connect to %s: TIMEOUT'
                     % configuration.ldap_server[self.server], what="error")
                self.server = (self.server + 1) % len(configuration.ldap_server)
            time.sleep(1)

    def generator(self, msg_id, nr):
        while nr:
            nr -= 1
            result_type, result = self.connexion.result(msg_id, all=0)
            if result_type == ldap.RES_SEARCH_RESULT:
                break
            if result_type == ldap.RES_SEARCH_ENTRY:
                yield result[0][1]

    def query(self, search, attributes=(configuration.attr_login,),
              base=configuration.ou_groups, async=False):
        """Returns a list of answers.
        A answer is a pair : (CN, dictionnary)
        """
        t = time.time()
        if (t - self.last_query > configuration.ldap_reconnect
            or self.connexion is None):
            self.connect()
        self.last_query = t
        # warn('search=%s base=%s attr=%s' % (search, base, attributes) )
        if self.connexion is True:
            # Fake connexion
            t = {}
            for a in attributes:
                t[a] = [a + '?']
            return (('cn?',t),)
        while True:
            try:
                start_time = time.time()
                sender.send_live_status(
                         '<script>b("/%s");</script>\n' % self.name)
                if async:
                    s = self.connexion.search_ext(base, ldap.SCOPE_SUBTREE,
                                              search, attributes, sizelimit=async)
                else:
                    s = self.connexion.search_s(base, ldap.SCOPE_SUBTREE,
                                                search, attributes)
                sender.send_live_status(
                         '<script>d("%s","/%s","",%6.4f,%s,"","","");</script>\n' %
                         (configuration.ldap_server[self.server],
                          self.name,
                          time.time() - start_time,
                          utilities.js(search + ':' + repr(attributes))))

                return s
            except ldap.LDAPError, e:           
                sender.send_live_status(
                         '<script>d("%s","/%s","",1,"","%s","%s","%s");</script>\n' %
                         (
                    configuration.ldap_server[self.server],
                    self.name,
                    time.ctime(start_time),
                    configuration.ldap_server[self.server],
                    e.__class__.__name__))

                warn('Uncatched: %s: %s QUERY=%s ATTRIBUTES=%s' % (
                    e,
                    configuration.ldap_server[self.server],
                    search, repr(attributes)
                    ), what='error')
                if time.time() > self.time_last_mail + 10:
                    self.time_last_mail = time.time()
                    utilities.send_backtrace(
                        configuration.ldap_server[self.server] + '\n'
                        + 'QUERY=' + search + '\n'
                        + 'ATTRIBUTES=' + repr(attributes) + '\n'
                        + 'BASE=' + base + '\n'
                        , 'LDAP Error')

                if isinstance(e, ldap.SIZELIMIT_EXCEEDED) or \
                   isinstance(e, ldap.NO_SUCH_OBJECT):
                    return ()
                time.sleep(1)
                self.connect() # Assume temporary network problem

    def query_login(self, login, attributes=(configuration.attr_login,),
                    star_is_safe=False):
        if ('*' in login) and not star_is_safe:
            return ()
        if not star_is_safe:
            login = utilities.the_login(login)
        a = self.query(search='(%s=%s)' % (configuration.attr_login, login),
                    base=configuration.ou_top, attributes=attributes
                    )
        a = a[0] # First answer
        if a[0] == None:
            a = self.query(search='(%s=%s)'% (configuration.attr_login, login),
                        base=configuration.ou_top, attributes=attributes
                        )
            a = a[0]
            if a[0] != None:
                utilities.send_backtrace('THIS CODE IS USEFUL!')
        if a[0] != None:
            if len(a) >= 2:
                return a[1]
        return {}

L_fast  = None # Fast interactive access
L_slow  = None # Slow request interactive access
L_batch = None # Any request in a batch thread

def init():
    global L_fast, L_slow, L_batch
    utilities.warn('Create LDAP connector')
    L_fast = LDAP()
    L_slow = LDAP('LDAP2')
    L_batch = LDAP('LDAP3')

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
    'k01':('k01',u'Bernard' ,u'BONOBO'      ,'bbonobo@africa.net'     ,'M',''),
    'k02':('k02',u'Georges' ,u'ROUGE GORGE' ,'grouge-gorge@europe.net','O',''),
    'k03':('k03',u'Magalie' ,u'MIGALE'      ,'mmigale@africa.net'     ,'A',''),
    'k04':('k04',u'Lucien'  ,u'LEZARD'      ,'llezard@france.net'     ,'R',''),
    'k05':('k05',u'Théodore',u'TIGRE'       ,'ttigre@asia.net'        ,'M',''),
    'k06':('k06',u'Simon'   ,u'SCORPION'    ,'sscorpion@africa.net'   ,'A',''),
    'k07':('k07',u'Cécilia' ,u'CHEVAL'      ,'ccheval@europe.net'     ,'M',''),
    'k08':('k08',u'Tatiana' ,u'TORTUE'      ,'ttortue@ocean.net'      ,'R',''),
    'k09':('k09',u'Ambroise',u'AIGLE'       ,'aaigle@america.net'     ,'O',''),
    'k10':('k10',u'Bill'    ,u'BOA'         ,'bboa@africa.net'        ,'R',''),
    'k11':('k11',u'Merlin'  ,u'MYRIAPODE'   ,'mmerlin@europe.net'     ,'A',''),
    'k12':('k12',u'Fanny'   ,u'FLAMANT ROSE','fflamant-rose@europ.net','O',''),
    'k13':('k13',u'Olivier' ,u'OURS'        ,'oours@us.net'           ,'M',''),
    }

if __name__ == "__main__":
    init()
    print L_fast.firstname_and_surname_and_mail_from_logins(('11210822','11209176'))
    # import document # If not here, this main can't execute ???
    # configuration.terminate()
    # init()
    from . import inscrits
    L = inscrits.L_fast
    for ii in L.students('UE-BIO2010L'):
        print ii
    print L.phone('thierry.excoffier')
    print L.ues_of_a_student('p0805711')
    print L.ues_of_a_student_short('p0805711')
    for ii in L.ues_of_a_student_with_groups('p0805711'):
        print ii

