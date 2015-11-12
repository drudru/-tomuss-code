#!/usr/bin/python3

import os
import re

def init(port):
    f = os.popen("xmodmap -pk -display :%d" % port, "r")
    keys = {}
    for line in f.readlines():
        line = re.split('[ \t]+', line.strip())
        if len(line) <= 2:
            continue
        try:
            code = int(line[0])
        except ValueError:
            continue
        if line[2]:
            keys[line[2][1:-1]] = (code, 0) # Not shifted
        if len(line) <= 4:
            continue
        if line[4]:
            if line[4][1:-1] not in keys:
                keys[line[4][1:-1]] = (code, 1) # Shifted

    f.close()

    keys[':'] = keys['colon']
    keys['/'] = keys['slash']
    keys['.'] = keys['period']
    keys['='] = keys['equal']
    keys['-'] = keys['minus']
    keys['*'] = keys['asterisk']
    keys['_'] = keys['underscore']
    keys['+'] = keys['plus']

    # for k in list(keys):
    #    keys[k.lower()] = keys[k]
    #    keys[k.upper()] = keys[k]

    return keys

if __name__ == "__main__":
    for k in init(0):
        print(k)
