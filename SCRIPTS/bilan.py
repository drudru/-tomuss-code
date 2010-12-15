#!/usr/bin/python
# -*- coding: latin1 -*-

"""
Extract from all the UE for all the years and semesters
the number of student registration in the UE and some statistics.

These informations are stored in LOGINS/XXX/XXXXXX/resume
as a Python fragment.

{
 'UE-CODE': [
       [year,'semester',#prst,#abinj,#abjus,average_value_in_0_1)],
       ...
       ],
 ...
}
"""

import tomuss_init
import configuration
import os
import tablestat
import utilities
import sys
import inscrits

order = {'Printemps':1, 'Automne':0}

class UE:
    def __init__(self):
        self.infos = {}

    def add(self, table, line):
        prst = 0
        abinj = 0
        abjus = 0
        summation = 0
        nr = 0
        for cell, column in zip(line, table.columns)[6:]:
            value = cell.value
            if value == '' and column.empty_is:
                value = column.empty_is
            if value == 'PRST':
                prst += 1
            elif value == 'ABINJ':
                abinj += 1
            elif value == 'ABJUS':
                abjus += 1
            elif column.type.name == 'Note':
                try:
                    min, max = column.min_max()
                    summation += (float(value)-min)/(max-min)
                    nr += 1
                    prst += 1
                except ValueError:
                    pass

        if nr == 0:
            summation = "-1"
        else:
            summation = '%4.2f' % (summation/float(nr))
        
        self.infos[table.year, table.semester] = (prst, abinj, abjus,
                                                  summation)

    def __str__(self):
        keys = list(self.infos.keys())
        keys.sort(key=lambda x: (x[0], order[x[1]]))
        s = []
        for k in keys:
            v = self.infos[k]
            s.append('[' + str(k[0]) + ',' +
                     repr(k[1]) + ',' +
                     str(v[0]) + ',' + str(v[1]) + ',' + str(v[2]) +
                     ',%s' % v[3]
                     + ']')
        return '[' + ',\n'.join(s) + ']'

students = {}


for syear in os.listdir(configuration.db):
    try:
        year = int(syear[1:])
    except ValueError:
        continue
    for semester in os.listdir(os.path.join(configuration.db, syear)):
        if (semester[1:] not in order
            or not os.path.isdir(os.path.join(configuration.db, syear,
                                              semester))
            ):
            continue
        semester = semester[1:]
        for ue in tablestat.les_ues(year, semester,
                                    true_file=True, all_files=False):
            name = ue.ue
            if not name.startswith('UE-'):
                continue
            if name[-1].isdigit():
                continue
            if name[-1] != 'L': # Licence
                continue
            name = name[3:]

            sys.stderr.write(name + ' ')
            sys.stderr.flush()

            for i in ue.logins_valid():
                i = utilities.the_login(str(i))
                if not i in students:
                    students[i] = {}
                s = students[i]
                if name not in s:
                    s[name] = UE()
                lines = tuple(ue.get_lines(i))
                s[name].add(ue , lines[0])

            ue.unload()
import re

def safe(x):
    return re.sub('[^a-zA-Z]', '_', x).encode('latin1')

for i, ues in students.items():
    # a = inscrits.firstname_and_surname(i)
    # print i, safe(a[1].upper()), safe(a[0].lower()),
    s = sorted(list(ues), key=lambda x: len(ues[x].infos))
    s.reverse()

    v = []
    for ue in s:
        v.append( repr(ue) + ':' + str(ues[ue]) )

    print i,
    sys.stdout.flush()
    utilities.manage_key('LOGINS', os.path.join(i, 'resume'),
                         content='{' + ',\n'.join(v) + '}')


