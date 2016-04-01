#!/usr/bin/python3
# -*- coding: latin-1 -*-

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

import os
import sys
import re
import collections
import math
import tomuss_init
from .. import configuration
from .. import tablestat
from .. import utilities
from .. import document
print(configuration.suivi)

# teacher -> { (year, semester, ue): number_of_cell }
teachers_tables = collections.defaultdict(
    lambda: collections.defaultdict(int))

class UE:
    def __init__(self):
        self.infos = {}

    def add(self, table, line, result):
        prst = 0
        abinj = 0
        abjus = 0
        summation = 0
        nr = 0
        weight = 0.
        key = (table.year, table.semester, table.ue)
        for cell, column in list(zip(line, table.columns))[6:]:
            if len(cell.author) > 1:
                teachers_tables[cell.author][key] += 1
            value = cell.value
            if not column.is_computed() and value == '' and column.empty_is:
                value = column.empty_is
            if value == configuration.pre:
                prst += 1
            elif value == configuration.abi:
                abinj += 1
            elif value == configuration.abj:
                abjus += 1
            if column.type.name == 'Note':
                try:
                    if column.weight[0] in '+-':
                        continue
                    cell_weight = float(column.weight)
                    min, max = column.min_max()
                    if value == configuration.abi:
                        value = min
                    else:
                        value = float(value)
                    if value >= min and value <= max:
                        summation += (value - min) / (max - min) * cell_weight
                        weight += cell_weight
                        nr += 1
                        prst += 1
                except ValueError:
                    pass

        summ = "-1"
        if result:
            min, max = result.min_max()
            try:
                summ = (float(line[result.data_col].value) - min) / max
            except ValueError:
                pass
        if summ == "-1" or math.isnan(summ):
            if nr == 0 or weight == 0.:
                if nr != 0 and weight == 0:
                    print('Null column weight in', table)
                summ = "-1"
            else:
                summ = '%.3f' % (summation/weight)
        
        self.infos[table.year, table.semester] = (prst, abinj, abjus, summ, nr)

    def __str__(self):
        keys = list(self.infos.keys())
        keys.sort(key=lambda x: utilities.semester_key(x[0], x[1]))
        s = []
        for k in keys:
            v = self.infos[k]
            s.append('[' + str(k[0]) + ',' +
                     repr(k[1]) + ',' +
                     str(v[0]) + ',' + str(v[1]) + ',' + str(v[2]) +
                     ',%s' % v[3] + ',' + str(v[4]) 
                     + ']')
        return '[' + ',\n'.join(s) + ']'

students = {}
students_index = collections.defaultdict(list)

for syear in os.listdir(configuration.db):
    try:
        year = int(syear[1:])
    except ValueError:
        continue
    for semester in os.listdir(os.path.join(configuration.db, syear)):
        if (semester[1:] not in configuration.semesters
            or not os.path.isdir(os.path.join(configuration.db, syear,
                                              semester))
            ):
            continue
        semester = semester[1:]
        for ue in tablestat.les_ues(year, semester,
                                    true_file=False, all_files=True):
            if not ue.official_ue:
                ue.unload()
                continue
            result = ue.columns.result_column()
            if result:
                ue.compute_columns()
            name = ue.ue
            for i in ue.the_keys():
                students_index[i].append((year, semester, ue.ue))
            if (year, semester) != (ue.year, ue.semester):
                # ue.unload()
                continue

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
                s[name].add(ue, lines[0], result)

            ue.unload()

# Update all the student indexes
# It is done only to be sure there is no bad index file (initialisation or bug)
# But if a student list is modified while this script run
# then the index will be bad for one day.
# The index are computed on 'suivi' semesters, not the others
for login, value in students_index.items():
    if len(login) >= 3:
        document.update_index(login, lambda x: value)
utilities.write_file(os.path.join('TMP', 'index_are_computed'),
                     'done')

def safe(x):
    return re.sub('[^a-zA-Z]', '_', x)


for i, ues in students.items():
    print(i)
    try:
        utilities.manage_key('LOGINS', os.path.join(i, 'resume'),
                             content=utilities.stable_repr(ues))
    except IOError:
        # Non existent student
        print('Non existent student:', i)


for teacher, tables in teachers_tables.items():
    print(teacher)
    if utilities.manage_key('LOGINS', os.path.join(teacher, 'tables')):
        # Only update the key if it exists
        utilities.manage_key('LOGINS', os.path.join(teacher, 'tables'),
                             content=utilities.stable_repr(tables))

