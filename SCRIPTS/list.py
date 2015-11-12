#!/usr/bin/python3

"""
Affiche annuaire
"""

import sys
import re
import collections
import tomuss_init

from .. import configuration
from .. import inscrits
from .. import utilities

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
    bad = collections.defaultdict(list)
    nr = 0
    dom = collections.defaultdict(int)
    for i in "abcdefghijklmnopqrstuvwxyz":
        q = L.query("(mail=" + i + "*)", attributes=(
                configuration.attr_login,
                configuration.attr_firstname,
                configuration.attr_surname,
                configuration.attr_mail),
                    base=configuration.ou_top)
        for j in q:
            if j[0]:
                login = j[1].get(configuration.attr_login,[''])[0]
                givenname = j[1].get(configuration.attr_firstname,[''])[0]
                givenname = utilities.flat(givenname).replace(' ','-').upper()
                sn = j[1].get(configuration.attr_surname,[''])[0]
                sn = utilities.flat(sn).replace(' ','-').upper()
                mail = j[1].get(configuration.attr_mail,[''])[0]
                mail = mail.split(';')[0]
                if sn == '' or givenname == '':
                    continue
                if '@' not in mail:
                    print('%-24s @\t' % login + mail)
                    bad['@'].append(login)
                    continue
                try:
                    name, domain = mail.upper().split('@')
                except ValueError:
                    print('%-24s @@\t' % login + mail)
                    bad['@@'].append(login)
                    continue

                dom[domain] += 1

                x = re.sub("[-a-zA-Z_.0-9@\']", "", mail)
                if x:
                    bad[x].append(login + ':' + mail)
                    print('%-24s ' % login + repr(x) + '\t' + mail)

    for d in sorted(list(dom.keys()), key=lambda x: dom[x]):
        print(d, dom[d])
    for k, v in bad.items():
        print(k, v)
    sys.exit(0)

q = L.query("(" + s + ")", attributes=(), base=configuration.ou_top)

for j in q:
    try:
        print(j[0])
    except:
        pass
for j in q[0][1].items():
    if j[0] == 'memberOf':
        print(j[0])
        for kk in j[1]:
            print('\t' + kk)
    else:
        if len(j[1]) == 1:
            print(j[0] + ':', j[1][0])
        else:
            print(j[0])
            for k in j[1]:
                print('\t' + k)


sys.stderr.close()

"""
    if True:
        # display information about about an object
        # q = L.query("(CN=DV012B*)", attributes=("DN",), base=configuration.ou_top)
        #q = L.query("(CN=*)", base='OU=LISTES DE DIFFUSIONS ETUDIANTES,OU=IUT A,DC=univ-lyon1,DC=fr',
        # q = L.query("(CN=*APO*medecine*)", base='DC=univ-lyon1,DC=fr', attributes=("CN",)        )
        # q = L.query("(CN=127376 APO-M*)", attributes=(), base=configuration.ou_top)
"""
