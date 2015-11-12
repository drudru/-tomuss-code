#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Translate all the TOMUSS table files to be readable by Python3.
  * The argument is the top database dir: DB
  * Untranslatable lines are kept identical.
  * Original files are renamed with an ~ at the end
  * Older TOMUSS versions should be able to read the new DB format
"""
import os
import re
import sys
import glob
import ast

def traduction(txt):
    if type(txt) == str:
        try:
            return txt.encode("latin-1").decode("utf-8")
        except UnicodeDecodeError: # Not '\xc3\xa9' but 'é' in the DB file
            pass
    return txt

match = re.compile(r"^([^(]*)(\(.*,.*\))(.*)$") # 3 groups: Name,Tuple,Padding

def tr_one_file(path):
    if os.path.islink(path):
        return
    new = []
    with open(path, "r", encoding = "utf-8") as f:
        for line in f:
            try:
                function, parameters, comment = match.findall(line)[0]
                parameters = ast.literal_eval(parameters)
            except:
                new.append(line)
                continue
            parameters = ','.join(repr(traduction(i))
                                  for i in parameters)
            new.append("{}({}){}\n".format(function, parameters, comment))
    os.rename(path, path + "~")
    with open(path, "w", encoding = "utf-8") as f:
        f.write(''.join(new))

def tr_files(paths):
    last = ''
    for path in paths:
        start = path[:14]
        if start != last:
            print("\n", start, end='')
            last = start
        print("*", end='', flush=True)
        tr_one_file(path)
    print()
    print()

print("Translate tables")
tr_files(glob.glob(os.path.join(sys.argv[1],"Y*","S*","*.py")))
print("Translate abj")
tr_files(glob.glob(os.path.join(sys.argv[1],"LOGINS","*","*","abj_*")))
print("Translate signatures")
tr_files(glob.glob(os.path.join(sys.argv[1],"LOGINS","*","*","signatures")))
