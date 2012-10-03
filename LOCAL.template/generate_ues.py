#!/usr/bin/python
# -*- coding: latin-1 -*-

"""
Input :
   * ??? (it depends on 'get_ue_dict' function
Output :
   * TMP/xxx_toute_les_ues.py
   * FILES/all_ues.js
   * FILES/all_ues.js.gz
"""

import tomuss_init
from .. import teacher

teacher.all_ues(compute=True)
