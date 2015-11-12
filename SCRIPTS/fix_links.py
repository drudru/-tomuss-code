#!/usr/bin/python3

import os
import sys

f = os.popen("find DB/ -type l", "r")

bad_year = []
bad_semester = []
bad_link = []
bad_file = []

n = 17

for name in f:
    name = name.strip()
    path = name.split('/')
    if len(path) != 4:
        continue
    db, year, semester, ue = path
    year = int(year.lstrip('Y'))
    link = os.readlink(name)
    path = link.split('/')
    if len(path) != 5:
        bad_link.append(name)
        print('Strange link:'.ljust(n), name, '->', link)
        continue
    dd, dd2, link_yyear, link_semester, link_ue = link.split(os.path.sep)
    assert ue == link_ue
    link_year = int(link_yyear.lstrip('Y'))
    if link_year+1 == year:
        if semester != 'SPrintemps' or link_semester != 'SAutomne':
            bad_semester.append(name)
            print('Semester previous:'.ljust(n), name, link)
            continue
    elif link_year-1 == year:
        if link_semester != 'SPrintemps' or semester != 'SAutomne':
            bad_semester.append(name)
            print('Semester next:'.ljust(n), name, link)
            continue
    else:
        bad_year.append(name)
        print('Year:'.ljust(n), name, link)
        continue
    link = os.path.join('DB', link_yyear, link_semester, link_ue)
    if not os.path.isfile(link) or os.path.islink(link):
        bad_file.append(name)
        print('Does not exists:'.ljust(n), name, link)

print("Enter YES to delete %s links to a strange file:" % len(bad_link), end=' ')
if sys.stdin.readline().strip() == 'YES':
    for name in bad_link:
        os.unlink(name)

print("Enter YES to delete %s links to a strange year:" % len(bad_year), end=' ')
if sys.stdin.readline().strip() == 'YES':
    for name in bad_year:
        os.unlink(name)

print("Enter YES to delete %s links to a strange semester:" % len(bad_semester), end=' ')
if sys.stdin.readline().strip() == 'YES':
    for name in bad_semester:
        os.unlink(name)

print("Enter YES to delete %s links to non existing file:" % len(bad_file), end=' ')
if sys.stdin.readline().strip() == 'YES':
    for name in bad_file:
        os.unlink(name)
