#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
This script check for all the usages in the table database
if the new function give the same result than the old one.

To do so:

   * Compute with the old function if 'column.old_function' is True
     else compute with the new function.

   * Run:  make tomuss_python.py ; ./average_compatibility.py
     It will display differences greater then 0.001

   * The file 'changes.py' contains values that are modified

   * If the average must be changed, the past must not be modified.
     In order to freeze it, run './backward_fix.py'
     DANGEROUS: so check it before not in production

To rerun testing only tables with problems:

    make tomuss_python.py ; ./average_compatibility.py YEAR/SEMESTER/UE ...


Edit this source to works with semester other than Automne/Printemps
"""

import math
import sys
import os
import tomuss_init
from .. import tablestat
from .. import document

def check(tables, f):
    f.write("changes = [\n")
    nr_averages = 0
    nr_changed_averages = 0
    last_table = None
    for t in tables:
        if t is None:
            continue
        if (last_table is None
            or last_table.year != t.year
            or last_table.semester != t.semester
        ):
            last_table = t
            semester_nr_averages = 0
            semester_nr_changed_averages = 0
            nr_tables = 0
            print("")
        nr_tables += 1
        print("{:4d}/{:10.10s} {:4d} tables {:6d} averages {:3d} changes {}\033[K\r"
              .format(t.year, t.semester, nr_tables,
                      semester_nr_averages, semester_nr_changed_averages,
                      t.ue), flush=True, end="")
        if t.semester not in ('Automne', 'Printemps'):
            t.unload()
            continue
        one_error = False
        for column in t.columns.columns_ordered():
            if column.type.name != 'Moy' or column.columns == '':
                continue
            column.old_function = True
            t.compute_columns()
            old_values = {}
            for key, line in t.lines.items():
                old_values[key] = line[column.data_col].value

            save_rounding = column.rounding
            column.rounding = 0
            t.compute_columns()
            column.rounding = save_rounding
            perfect_values = {}
            for key, line in t.lines.items():
                perfect_values[key] = line[column.data_col].value

            column.old_function = False
            t.compute_columns()
            errors = []
            for key, line in t.lines.items():
                nr_averages += 1
                semester_nr_averages += 1
                try:
                    if (math.isnan(old_values[key]) and
                        math.isnan(line[column.data_col].value)):
                        continue
                except TypeError:
                    continue # ABI replaced by a grade
                if abs(old_values[key] - line[column.data_col].value) >= 0.001:
                    errors.append((
                        str(t),
                        column.the_id,
                        key,
                        perfect_values[key],
                        old_values[key],
                        line[column.data_col].value),
                    )
            if errors:
                one_error = True
                nr_changed_averages += len(errors)
                semester_nr_changed_averages += len(errors)
                f.write("# {} {} {}\n".format(t, column.title, column.round_by))
                f.write("# table, column, line, perfect, old, new\n")
                for change in errors:
                    f.write('\t' + repr(change) + ',\n')
        t.unload()
    f.write("]\n")
    f.write("nr_averages = {}\n".format(nr_averages))
    f.write("nr_changed_averages = {}\n".format(nr_changed_averages))

print("************** Outputs in 'changes.py' ******************")
output = open(os.path.join("PYTHON_JS", "changes.py"), "w")
if len(sys.argv) == 1:
    check(tablestat.all_the_tables(), output)
else:
    check(
        [
            document.table(*table_name.split('/'))
            for table_name in sys.argv[1:]
        ],
        output
        )
output.close()
