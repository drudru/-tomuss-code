#!/usr/bin/python
# -*- coding: latin-1 -*-

"""
Suivi Preference statistics
"""

import glob
import collections
import tomuss_init
from .. import utilities

nb_on = collections.defaultdict(int)
nb_set = collections.defaultdict(int)
pairs = collections.defaultdict(int)
data = []
nb = 0
for filename in glob.glob("DB/LOGINS/*/*/preferences"):
    d = eval(utilities.read_file(filename))
    nb += 1
    s = []
    for k in sorted(d):
        if d[k]:
            nb_on[k] += 1
            s.append(k)
    for i in s:
        for j in s:
            if i > j:
                pairs[i, j] += 1
    nb_set[' '.join(s)] += 1
    data.append(d)

print nb, "students with preferences"
for k in sorted(nb_on, key=lambda x: nb_on[x]):
    v = nb_on[k]
    print "%-4d %2d%% %s" % (v, (100*v)/nb, k)
print 'Pairs'
for k in sorted(pairs, key=lambda x: pairs[x]):
    print pairs[k], k
print 'Sets'
for k in sorted(nb_set, key=lambda x: (nb_set[x], x)):
    print nb_set[k], k
print 'Data'
print ','.join(nb_on)
for d in data:
    print ','.join(
        '1' if d.get(i,0) else '0'
        for i in nb_on)
