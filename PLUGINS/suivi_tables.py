#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet)
#    Copyright (C) 2008 Thierry EXCOFFIER, Universite Claude Bernard
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
from tablestat import TableStat, les_ues

def table_statistics_table(year, semester):
    filename = document.table_filename(year, semester, 'tables')

    tables = {'': TableStat('')}
    for t in les_ues(year, semester):
        tables[t.ue] = table = TableStat(t.ue)
        table.nr_cols = len(t.columns)
        table.nr_pages = len(t.pages)
        table.nr_lines = len(t.lines)
        table.t = t
        col_inscrit = t.column_inscrit()
        for line in t.lines.values():
            if col_inscrit != None:
                if line[col_inscrit].value == 'ok':
                    table.nr_inscrits += 1
                elif line[col_inscrit].value == 'non':
                    table.nr_not_inscrits += 1
                group_and_seq = line[3].value + '/' + line[4].value
                table.group_and_seq[group_and_seq] = True
                
            for v in line:
                table.update(v)

    max_cels = max([t.nr for t in tables.values()])
    max_cols = max([t.nr_cols for t in tables.values()])
    max_lines = max([t.nr_lines for t in tables.values()])
    max_pages = max([t.nr_pages for t in tables.values()])
    # max_students = max([t.nr_students for t in tables.values()])
    max_comment = max([t.nr_comments for t in tables.values()])
    max_teachers = max([len(t.teachers) for t in tables.values()])

    f = open(filename, "w")
    f.write("""# -*- coding: utf8 -*-
from data import *
new_page('' ,'*', '', '')
column_change (0,'0_0','UE','Text','','','F',0,4)
column_comment(0,'0_0','Code APOGÉE de l\\'UE')
column_change (0,'0_1','#cellules','Note','[0;%s]','','',0,2)
column_comment(0,'0_1','Nombre de cellules saisies')
column_change (0,'0_2','#enseignants','Note','[0;%s]','','',0,2)
column_comment(0,'0_2','Nombre d\\'enseignants ayant fait une saisie')
column_change (0,'0_3','#lignes','Note','[0;%s]','','',0,2)
column_comment(0,'0_3','Nombre de lignes (donc d\\'étudiants)')
column_change (0,'0_4','#colonnes','Note','[0;%s]','','',0,2)
column_comment(0,'0_4','Nombre total de colonnes')
column_change (0,'0_5','#pages','Note','[0;%s]','','',0,2)
column_comment(0,'0_5','Nombre d\\'affichage de la page')
column_change (0,'0_6','#commentaires','Note','[0;%s]','','',0,2)
column_comment(0,'0_6','Nombre de cellules avec un commentaire')
column_change (0,'0_7','Première_modification','Date','','','',0,4)
column_change (0,'0_8','Dernière_modification','Date','','','',0,4)
column_change (0,'0_9','#inscrits','Note','[0;NaN]','','',0,2)
column_comment(0,'0_9','Nombre d\\'étudiants inscrits officiellement')
column_change (0,'0_a','#noninscrits','Note','[0;NaN]','','',0,2)
column_comment(0,'0_a','Nombre d\\'étudiants illégaux')
column_change (0,'0_b','Étendue','Bool','[0;20]','','',0,1)
column_comment(0,'0_b','UE à cheval sur Automne/Printemps')
column_change (0,'0_c','Vide','Text','[0;20]','','',0,4)
column_comment(0,'0_c','S\\'il y a un nombre de lignes != 0, alors la table est vide')
column_change (0,'0_d','Grp/Seq','Text','[0;20]','','',0,2)
column_comment(0,'0_d','Nombre de groupes d\\'étudiants')
table_comment(0, 'Statistiques par UE')
table_attr('default_nr_columns', 0, 14)
""" % (max_cels, max_teachers, max_lines, max_cols,  max_pages, max_comment))

    for i, t in enumerate(tables.values()):
        if t.name == '':
            continue
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
cell_change(0,'0_a','%d',%s,'')
cell_change(0,'0_b','%d','%s','')
cell_change(0,'0_c','%d',%s,'')
cell_change(0,'0_d','%d',%s,'')
""" % (i, repr(t.name), i, repr(str(t.nr)), i, repr(str(len(t.teachers))),
       i, repr(t.nr_lines),i, repr(t.nr_cols), i, repr(str(t.nr_pages)),
       i, repr(str(t.nr_comments)),
       i, repr(t.date_min), i, repr(t.date_max),
       i, repr(t.nr_inscrits), i, repr(t.nr_not_inscrits),
       i, t.t.is_extended and 'OUI' or 'NON' ,
       i, utilities.js(t.t.empty()[1]),
       i, len([g for g in t.group_and_seq if g != '']),
       ))
    f.close()


# table_statistics_table = utilities.add_a_cache0(
#     table_statistics_table, timeout=configuration.teacher_stat_interval)

def table_stat(server):
    """Create a table of statistics about all the tables,
    redirect the browser on this table."""
    table_statistics_table(server.year, server.semester)

def headers(server):    
    return (
        ('Location','%s/=%s/%d/%s/tables' % (
        configuration.server_url, server.ticket.ticket,
        server.year, server.semester)), )

plugin.Plugin('tables', '/*2',
              function=table_stat,
              teacher=True,
              response=307,
              headers = headers,
              launch_thread = True,
              link=plugin.Link(text='Statistiques UE',
                               url="javascript:go_suivi('*2')",
                               where="informations",
                               html_class="verysafe",
                               help="""Pour chaque UE,
                               affiche les statistiques concernant l'UE""",
                               ),
              )

