#!/usr/bin/python

"""
The standard input must be a GUI_record file :

SCRIPTS/display_gui_record.py <DB/LOGINS/thi/thierry.excoffier/GUI_record

"""

import sys
import ast

for line in sys.stdin:
    line = ast.literal_eval(line.replace('R','',1))
    print line[0], line[1]
    last = 0
    for v in line[2]:
        t, name, val = (v + [""])[:3]
        print '%10d %30s %s' % (t-last, name, val)
        last = t
