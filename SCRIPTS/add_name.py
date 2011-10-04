#!/usr/bin/python

"""
It is a filter

Input : a CSV file with student number in first column
Output : the same file with a column inserted with the surname and firstname
"""

import tomuss_init
import inscrits
import csv
import sys

w = csv.writer(sys.stdout)

for line in csv.reader(sys.stdin):
    w.writerow([line[0],
                ' '.join(inscrits.L_batch.firstname_and_surname(line[0])[::-1]).encode('utf8')
                ] + line[1:])




