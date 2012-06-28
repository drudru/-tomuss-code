#!/usr/bin/python

"""
Affiche annuaire
"""

import os
import sys
import re
import collections

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

if sys.argv[1] == 'checkmail':
    # SCRIPTS/list.py memberof=CN=139284 APO-UFR Sciences et Technologie,OU=groupes,OU=etudiants,DC=univ-lyon1,DC=fr checkmail | tee xxx
    # Verify if mails are in the form : givenname.surname
    # Make some statistics
    bad = collections.defaultdict(int)
    nr = 0
    dom = collections.defaultdict(int)
    for i in "abcdefghijklmnopqrstuvwxyz":
        q = L.query("(mail=" + i + "*)", attributes=('givenName','sn','mail'),
                    base=configuration.ou_top)
        for j in q:
            if j[0]:
                givenname = unicode(j[1].get('givenName',[''])[0],'utf-8')
                givenname = utilities.flat(givenname).replace(' ','-').upper()
                sn = unicode(j[1].get('sn',[''])[0],'utf8')
                sn = utilities.flat(sn).replace(' ','-').upper()
                mail = unicode(j[1].get('mail',[''])[0],'utf8')
                mail = mail.split(';')[0]
                if sn == '' or givenname == '':
                    continue
                if '@' not in mail:
                    print '@\t' + mail
                    bad['@'] += 1
                    continue
                try:
                    name, domain = mail.upper().split('@')
                except ValueError:
                    print '@@\t', mail
                    bad['@@'] += 1
                    continue

                dom[domain] += 1

                x = re.sub("[-a-zA-Z_.0-9@\']", "", mail)
                if x:
                    bad[x] += 1
                    print repr(x) + '\t' + mail.encode('utf-8')

    for d in sorted(dom.keys(), key=lambda x: dom[x]):
        print d, dom[d].encode('utf-8')
    for k, v in bad.items():
        print k.encode('utf-8'), v
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
