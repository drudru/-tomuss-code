#!/usr/bin/python

import sys
import re

c = sys.stdin.read()

for n in "012345678":
    c = re.sub(n + "9999[0-9]*,", chr(ord(n)+1) + ",", c)
    c = re.sub(n + r"\.9999[0-9]*,", chr(ord(n)+1) + ",", c)

print c
