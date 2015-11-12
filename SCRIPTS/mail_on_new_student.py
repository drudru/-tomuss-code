#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#    Copyright (C) 2014 Thierry EXCOFFIER, Universite Claude Bernard
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#    Contact: Thierry.EXCOFFIER@univ-lyon1.fr

"""
Send a mail to all table masters with new students
since the last time the script was launched.

Do not send the mail if the table has more than 90% new students.

Last run date in seconds is stored in 'TMP/mail_on_new_student_timestamp'

"""

import time
import collections
import os
import tomuss_init
from .. import utilities
from .. import inscrits
from .. import tablestat
from .. import configuration
from .. import data
from .. import teacher

frome = configuration.maintainer
no_mail_if_more_than = 0.9 # new students
timestamp = os.path.join('TMP', 'mail_on_new_student_timestamp')
try:
    last_run = float(utilities.read_file(timestamp))
except IOError:
    last_run = 0
today = time.time()

# {Teacher} -> {Table} -> [Student]
teachers = collections.defaultdict(lambda: collections.defaultdict(list))

all_ues = teacher.all_ues()

formate = '%10s %-40s %8s %-8s %s'

header = formate % (utilities._("COL_TITLE_0_0"),
                    utilities._("COL_TITLE_0_2")
                    + ' ' + utilities._("COL_TITLE_0_1"),
                    utilities._("COL_TITLE_0_3"),
                    utilities._("COL_TITLE_0_4"),
                    ''
                   )

if True:
    all_tables = tablestat.les_ues(configuration.year_semester[0],
                                   configuration.year_semester[1],
                                   ro=True)
else:
    # For debugging only : check the tables given in parameter
    import sys
    from .. import document
    all_tables = [document.table(configuration.year_semester[0],
                                 configuration.year_semester[1],
                                 code_ue, create=False)
                  for code_ue in sys.argv[1:]
                  ]

for table in all_tables:
    print(table)
    if '-' not in table.ue or not table.official_ue:
        table.unload()
        continue
    ue = table.ue
    if ue not in all_ues:
        ue = ue.split('-')[-1]
        if ue not in all_ues:
            table.unload()
            continue
    students = []
    students_removed = []
    col_inscrit = table.column_inscrit()
    for line in table.lines.values():
        if line[0].date_seconds() < last_run:
            continue
        if (line[0].author == data.ro_user
            and configuration.is_a_student(line[0].value)):
            add = True
        elif (line[0].value == ''
              and configuration.is_a_student(line[0].previous_value())):
            add = False
        elif (line[0].author == data.rw_user
              and configuration.is_a_student(line[0].value)):
            if col_inscrit is None or line[col_inscrit].value == 'non':
                add = False
            else:
                continue
        else:
            continue

        etapes = inscrits.L_batch.etapes_of_student(line[0].value)
        if add:
            students.append(formate % (
                line[0].value,
                line[2].value + ' ' + line[1].value.title(),
                line[3].value,
                line[4].value,
                ' '.join(etapes)
            ))
        else:
            student_id = line[0].previous_value()
            if line[1].value:
                # If the value is here, use it.
                fn = line[2].value
                sn = line[1].value
                grp = line[3].value,
                seq = line[4].value,
            else:
                fn = line[2].previous_value()
                sn = line[1].previous_value()
                grp = line[3].previous_value()
                seq = line[4].previous_value()
            students_removed.append(formate % (
                student_id, fn + ' ' + sn.title(), grp, seq,
                ' '.join(etapes)
            ))
    if (len(students) != 0
        and len(students) < no_mail_if_more_than * len(table.lines)

        or

        len(students_removed) != 0
        and len(students_removed) < no_mail_if_more_than * len(table.lines)
    ):
        for teach in table.masters:
            teachers[teach][ue] = (students, students_removed)
    table.unload()

for teach, ues in teachers.items():
    mail = inscrits.L_batch.mail(teach)
    if not mail:
        continue
    message = [utilities._("mail_on_new_student") + '\n\n\n']
    for ue, student_lists in ues.items():
        students, students_removed = student_lists

        m = ('='*79 + '\n'
             + ue + ' ' + all_ues[ue].intitule() + '\n'
             + ', '.join(all_ues[ue].responsables_login()) + '\n'
             + '-'*79 + '\n'
             + header + '\n'
             + '-'*79 + '\n'
             )

        if students:
            m += utilities._("mail_on_new_student+") + '\n' + ''.join(
                '%s\n' % student
                for student in students)
        if students_removed:
            m += '\n' + utilities._("mail_on_new_student-") + '\n' + ''.join(
                '%s\n' % student
                for student in students_removed)

        message.append(m)
    print(''.join(message))
    utilities.send_mail(mail,
                        utilities._("MSG_auto_update_done"),
                        '\n\n'.join(message),
                        show_to=True)



utilities.write_file(timestamp, str(today))
