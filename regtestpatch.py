#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet)
#    Copyright (C) 2008 Thierry EXCOFFIER, Universite Claude Bernard
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

"""
Modify the application in order to support regression tests.
"""

import configuration
import inscrits
import referent

def do_patch():

    if configuration.regtest:
        configuration.db = 'DBregtest'
        configuration.allow_student_list_update = True
        
    if configuration.regtest:
        class LDAP_regtest(inscrits.Empty):
            def students(self, ue):
                if ue == 'UE-INF20UE2' or ue == 'UE-XXX9999L':
                    yield ('10800000', 'Jacques', 'MARTIN', 'jacques@martin',
                           'A', '1')
                if len(ue) == 3 and ue.startswith('UE') and ue[-1].isdigit():
                    for i in inscrits.demo_animaux.values()[-1]:
                        yield i
                return

            def etapes_of_students(self, logins):
                return dict( (login, ('etape-' + login,)) for login in logins )
            
            def firstname_and_surname_and_mail(self, r):
                if r == 'toto':
                    return 'firstnametoto', 'surnametoto', 'mail@toto'
                else:
                    if r.startswith('k'):
                        return super(type(self),self
                                     ).firstname_and_surname_and_mail(r)
                    else:
                        return r+'Firstname', r+'Surname', 'mail?'
            def is_a_teacher(self, login):
                if login in configuration.root:
                    return True
                if login in configuration.invited_abj_masters:
                    return True
                if login in configuration.invited_teachers:
                    return True
                if login == 'a_referent':
                    return True

            def ues_of_a_student_short(self, login):
                if login == '10800000':
                    return ['UE-INF20UE2L', 'UE-INF20UE2']
                return []

            def query_logins(self, logins, attributes):
                r = []
                for login in logins:
                    q = self.query_login(login, attributes)
                    r.append([login]+[q[i][0] for i in attributes[1:]])
                return r

            def is_a_referent(self, login):
                if login == configuration.root or login == 'a_referent':
                    return True
                return False

            def firstname_or_surname_to_logins(self, name, base=None,
                                               attributes=None):
                if attributes == None:
                    attributes = [configuration.attr_login,
                                  configuration.attr_surname,
                                  configuration.attr_firstname]
                all = []
                name = name.lower()
                for i, infos in inscrits.demo_animaux.items():
                    if (i.lower() == name
                        or infos[1].lower().startswith(name)
                        or infos[2].lower().startswith(name)
                        ):
                        r = []
                        for a in attributes:
                            if a == configuration.attr_login:
                                r.append(unicode(i,
                                                 configuration.ldap_encoding))
                            elif a == configuration.attr_surname:
                                r.append(infos[2])
                            elif a == configuration.attr_firstname:
                                r.append(infos[1])
                            elif a == configuration.attr_mail:
                                r.append(unicode(infos[3],
                                                 configuration.ldap_encoding))
                        all.append(r)
                return all


        inscrits.LDAP = LDAP_regtest

    # AFTER : because it creates an LDAP connection
    configuration.terminate()

    if not configuration.regtest:
        return

    configuration.do_not_display = ()
    
    import authentication
    import utilities
    def ticket_login_name(ticket_key, service):
        """Redefined by local configuration"""
        utilities.warn(service, what='auth')
        return ticket_key
    authentication.ticket_login_name = ticket_login_name

    def ticket_ask(server, server_url, service):
        """Redefined by local configuration"""
        utilities.warn(service, what='auth')
        try:
            server.send_response(307)
            server.send_header('Location', '%s/=user.name' % server_url)
            server.end_headers()
        except socket.error:
            utilities.warn('Do not wait redirection', what="error")
    authentication.ticket_ask = ticket_ask



    def student_list(f, portails, not_in):
        return {'10800000': referent.Student(('10800000', 'JacqueS',
                                              'MartiN', 'jacques@martin',
                                              ()), portail='L1'),
                '10800001': referent.Student(('10800001', str(f),
                                              str(portails), '', ()),
                                             portail='L2'),
                }
    referent.student_list = student_list

    import TEMPLATES.Printemps
    TEMPLATES.Printemps.cell_change = lambda table,page,col,lin,value,date:0

    def is_an_official_ue(code):
        return '-' in code
    configuration.is_an_official_ue = is_an_official_ue


