#!/usr/bin/python
# -*- coding: latin1 -*-

"""
Input :
   * ???
Output :
   * TMP/xxx_toute_les_ues.py
   * FILES/all_ues.js
   * FILES/all_ues.js.gz
"""

import os
import tomuss_init
import utilities
import teacher

debug = False

teacher.all_ues(compute=True)

ff = utilities.AtomicWrite(os.path.join('TMP','all_ues.js'))
ff.write('all_ues = {\n')
ue_list = []
for ue, uev in teacher.all_ues().items():
    print ue
    ue_list.append('%s:%s' % (utilities.js(ue).encode('utf-8'),
                                  uev.js().encode('utf-8')))
ff.write(',\n'.join(ue_list))
ff.write('} ;\n')
ff.close()

os.system('gzip -9 <TMP/all_ues.js >all_ues.js.gz')
os.rename('all_ues.js.gz',os.path.join('TMP','all_ues.js.gz'))
