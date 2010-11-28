#!/usr/bin/python
# -*- coding: latin1 -*-

"""
Input :
   * xxx_toute_les_ues
Output :
   * For each UE the responsable list
"""


import sys
import os
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), '..'))

import utilities


import TMP.xxx_toute_les_ues
ues = TMP.xxx_toute_les_ues.all

for i in range(6):
    print '='*80
    print 'Responsable', i
    print '='*80
    for ue in ues.values():
        r = ue.responsables_login()
        if r and len(r) > i:
            print ue.name, r[i].encode('latin1')





        
