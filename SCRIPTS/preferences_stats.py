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
nb = 0
for filename in glob.glob("DB/LOGINS/*/*/preferences"):
    d = eval(utilities.read_file(filename))
    nb += 1
    for k, v in d.items():
        if v:
            nb_on[k] += 1

print nb, "students with preferences"
for k in sorted(nb_on, key=lambda x: nb_on[x]):
    v = nb_on[k]
    print "%20s %3d %d%%" % (k, v, (100*v)/nb)
            
