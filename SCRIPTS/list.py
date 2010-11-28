#!/usr/bin/python

"""
Affiche annuaire
"""

import os
import sys
import re

sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), '..'))

import configuration
configuration.terminate()
import inscrits
import utilities

L = inscrits.LDAP()

v = sys.argv[1]

if '=' not in v:
    s = 'SAMAccountName=' + v
else:
    s = v

if len(sys.argv) > 2:
    if sys.argv[2] == 'checkmail':
        # Verify if mails are in the form : givenname.surname
        # Make some statistics
        q = L.query("(" + s + ")", attributes=('givenname','sn','mail'), base=configuration.ou_top)
        bad = 0
        bad2 = 0
        nr = 0
        dom = {}
        for j in q:
            if j[0]:
                givenname = unicode(j[1].get('givenName',[''])[0],'utf8')
                givenname = utilities.flat(givenname).replace(' ','-').upper()
                sn = unicode(j[1].get('sn',[''])[0],'utf8')
                sn = utilities.flat(sn).replace(' ','-').upper()
                mail = unicode(j[1].get('mail',[''])[0],'utf8')
                mail = mail.split(';')[0]
                if '@' not in mail:
                    continue
                if sn == '' or givenname == '':
                    continue

                name, domain = mail.upper().split('@')

                if domain not in dom:
                    dom[domain] = 0
                dom[domain] += 1
                    
                if not domain.endswith('UNIV-LYON1.FR'):
                    bad2 += 1

                nr += 1
                if givenname + '.' + sn != name:
                    print givenname, sn, mail
                    bad += 1

        print nr, 'people'
        print '%4.1f%% bad mail' % ((100.*bad)/nr)
        print '%4.1f%% bad domain' % ((100.*bad2)/nr)
        for d in sorted(dom.keys(), key=lambda x: dom[x]):
            print d, dom[d]
                    
                
    sys.exit(0)
    



q = L.query("(" + s + ")", attributes=(), base=configuration.ou_top)

for j in q:
    try:
        print j[0]
    except:
        pass
for j in q[0][1].items():
    if j[0] == 'memberOf':
        print j[0]
        for kk in j[1]:
            print '\t' + kk
    else:
        if len(j[1]) == 1:
            print j[0] + ':', j[1][0]
        else:
            print j[0]
            for k in j[1]:
                print '\t' + k


sys.stderr.close()

"""
    if True:
        # display information about about an object
        # q = L.query("(CN=DV012B*)", attributes=("DN",), base=configuration.ou_top)
        #q = L.query("(CN=*)", base='OU=LISTES DE DIFFUSIONS ETUDIANTES,OU=IUT A,DC=univ-lyon1,DC=fr',
        # q = L.query("(CN=*APO*medecine*)", base='DC=univ-lyon1,DC=fr', attributes=("CN",)        )
        # q = L.query("(CN=127376 APO-M*)", attributes=(), base=configuration.ou_top)
"""
