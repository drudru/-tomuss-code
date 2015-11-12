#!/usr/bin/python3
# -*- coding: latin1 -*-

"""

"""

import os
import time
import sys

sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), '..'))
from .. import configuration
configuration.terminate()

from .. import document

t = document.table(2009,'Automne', 'UE-TVL1002L-3', ro=True, create=False)


