#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet)
#    Copyright (C) 2008,2009 Thierry EXCOFFIER, Universite Claude Bernard
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
#    Contact: Thierry.EXCOFFIER@bat710.univ-lyon1.fr

import plugin
import configuration
import document
import utilities
import referent
import data
from tablestat import TableStat, les_ues

def teachers_statistics_table(year, semester):
    utilities.warn('start', what='debug')
    filename = document.table_filename(year, semester, 'teachers')

    teachers = {'': TableStat('')}
    for t in les_ues(year, semester):
        for c in t.columns:
            user_name = c.author
            if user_name not in teachers:
                teachers[user_name] = TableStat(user_name)
            teachers[user_name].nr_cols += 1
        for p in t.pages:
            if p.user_name not in teachers:
                teachers[p.user_name] = TableStat(p.user_name)
            teachers[p.user_name].nr_pages += 1
            try:
                teachers[p.user_name].pages_per_table[t.ue] += 1
            except:
                teachers[p.user_name].pages_per_table[t.ue] = 1
        for line in t.lines.values():
            for v in line[6:]:
                teachers[v.author].update(v, table=t)

    year = utilities.university_year(year, semester)
    for t in referent.les_blocsnotes(year):
        for p in t.pages:
            if p.user_name not in teachers:
                teachers[p.user_name] = TableStat(p.user_name)
            teachers[p.user_name].nr_pages += 1
        user_name = utilities.module_to_login(t.ue)
        if user_name not in teachers:
            teachers[user_name] = TableStat(user_name)
        # teachers[user_name].nr_students = len([x for x in t.logins() if x])
        teachers[user_name].nr_students = len(
            referent.students_of_a_teacher(user_name))
        for line in t.lines.values():
            for v in line[3:]:
                teachers[v.author].update(v, blocnote=True)

    del teachers[data.ro_user]
    del teachers[data.rw_user]

    if len(teachers):
        max_cels = max([t.nr for t in teachers.values()])
        max_cols = max([t.nr_cols for t in teachers.values()])
        max_pages = max([t.nr_pages for t in teachers.values()])
        max_students = max([t.nr_students for t in teachers.values()])
        max_blocnote = max([t.nr_blocnote for t in teachers.values()])
        max_comment = max([t.nr_comments for t in teachers.values()])
    else:
        max_cels = max_cols = max_pages = max_students = max_blocnote = max_comment = 1


        

    f = open(filename, "w")
    f.write("""# -*- coding: utf8 -*-
from data import *
new_page('' ,'*', '', '')
column_change (0,'0_0','Enseignant','Text','','','F',0,6)
column_comment(0,'0_0','Identifiant (login) de l\\'enseignant')
column_change (0,'0_1','Prénom','Text','','','F',0,4)
column_change (0,'0_2','Nom','Text','','','F',0,4)
column_change (0,'0_3','#cellules_saisies','Note','[0;%s]','','',0,2)
column_comment(0,'0_3','Nombre de cellules saisies')
column_change (0,'0_4','#colonnes_créées','Note','[0;%s]','','',0,2)
column_comment(0,'0_4','Nombre de colonnes créées.')
column_change (0,'0_5','#pages_vues','Note','[0;%s]','','',0,2)
column_comment(0,'0_5','Nombre de tables affichées')
column_change (0,'0_6','#commentaires','Note','[0;%s]','','',0,2)
column_comment(0,'0_6','Nombre de commentaires de cellule saisis')
column_change (0,'0_7','#Étudiants_suivis','Note','[0;%s]','','',0,2)
column_comment(0,'0_7','Nombre d\\'étudiants suivis en tant que référent pédagogique')
column_change (0,'0_8','#blocnote_saisie','Note','[0;%s]','','',0,2)
column_comment(0,'0_8','Nombre de cellules saisies dans le blocnote du référent pédagogique')
column_change (0,'0_9','Première_modification','Date','','','',0,4)
column_change (0,'0_10','Dernière_modification','Date','','','',0,4)
table_comment (0,'Statistiques par enseignant pour l\\'ensemble des tables')
table_attr('default_nr_columns', 0, 11)
""" % (max_cels, max_cols, max_pages, max_comment, max_students, max_blocnote))

    for i, t in enumerate(teachers.values()):
        s = t.name.split('.')
        if len(s) == 1:
            s = ('', s[0])
        f.write("""cell_change(0,'0_0','%d',%s,'')
cell_change(0,'0_1','%d',%s,'')
cell_change(0,'0_2','%d',%s,'')
cell_change(0,'0_3','%d',%s,'')
cell_change(0,'0_4','%d',%s,'')
cell_change(0,'0_5','%d',%s,'')
cell_change(0,'0_6','%d',%s,'')
cell_change(0,'0_7','%d',%s,'')
cell_change(0,'0_8','%d',%s,'')
cell_change(0,'0_9','%d',%s,'')
cell_change(0,'0_10','%d',%s,'')
""" % (i, repr(t.name), i, repr(s[0]), i, repr(s[1]), i, repr(str(t.nr)),
       i, repr(t.nr_cols), i, repr(str(t.nr_pages)),
       i, repr(str(t.nr_comments)),
       i, repr(t.nr_students),
       i, repr(str(t.nr_blocnote)),
       i, repr(t.date_min), i, repr(t.date_max)))

    f.close()

    utilities.warn('end statistics', what='debug')


#teachers_statistics_table = utilities.add_a_cache0(
#    teachers_statistics_table, timeout=configuration.teacher_stat_interval)


def teachers_stat(server):
    """Create a table of statistics about all the teachers,
    redirect the browser on this table."""
    teachers_statistics_table(server.year, server.semester)


def headers(server):    
    return (
        ('Location','%s/=%s/%d/%s/teachers' % (
        configuration.server_url, server.ticket.ticket,
        server.year, server.semester)), )

plugin.Plugin('teachers', '/*',
              function=teachers_stat,
              teacher=True,
              response=307,
              headers = headers,
              launch_thread = True,
              link=plugin.Link(text='Statistiques enseignants',
                               url="javascript:go_suivi('*')",
                               where="informations",
                                                    html_class="verysafe",
                               help="""Pour chaque enseignant,
                               affiche les statistiques sur
                               les informations saisies dans TOMUSS""",
                   ),
              )


