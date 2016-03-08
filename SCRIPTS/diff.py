#!/usr/bin/python3

"""
For example:

   SCRIPTS/diff.py 2015/Automne/UE-MGC1035M 2016/Printemps/UE-MGC1035M 
"""

import sys
import tomuss_init
from .. import document
from .. import configuration

print("Loading table {}".format(sys.argv[1]))
old = document.table(*sys.argv[1].split('/'))
print("Loading table {}".format(sys.argv[2]))
new = document.table(*sys.argv[2].split('/'))
                   
if set(old.logins_valid()) != set(new.logins_valid()):
    print("Not the same login list")
    exit(1)

old_cols = set(col.title for col in old.columns.columns)
new_cols = set(col.title for col in new.columns.columns)
if old_cols != new_cols:
    print("Not the same column list")
    print("Only in old: {}".format(old_cols - new_cols))
    print("Only in new: {}".format(new_cols - old_cols))
    exit(1)

for login in old.logins_valid():
    line_old = tuple(old.get_lines(login))
    line_new = tuple(new.get_lines(login))
    if len(line_old) != 1 or len(line_new) != 1:
        print("Multiple identical logins")
        exit(1)
    line_old = line_old[0]
    line_new = line_new[0]
    for col in old_cols:
        col_old = old.columns.from_title(col)
        col_new = new.columns.from_title(col)
        if line_old[col_old.data_col].value != line_new[col_new.data_col].value:
            print("{} {} {}({}) != {}({})".format(
                login, col,
                line_old[col_old.data_col].value,
                line_old[col_old.data_col].date,
                line_new[col_new.data_col].value,
                line_new[col_new.data_col].date
            ))
