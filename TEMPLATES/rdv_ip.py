#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2010 Thierry EXCOFFIER, Universite Claude Bernard
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

import data
import document
import orientation_rp

days = {
    '14:Lundi'   : '20110214',
    '15:Mardi'   : '20110215',
    '16:Mercredi': '20110216',
    '17:Jeudi'   : '20110217',
    }
hoursAM = ('8h30', '9h','9h30','10h','10h30','11h','11h30', '12h')
hoursPM = ('13h','13h30','14h','14h30','15h','15h30', '16h','16h30','17h')

orientation_without_referent_rdv = ('BIO', 'BCH', 'STU')
orientation_without_referent_rdv = ()

def day_for_dsi(day):
    return day.split(':')[0] + '-' + 'Fév'

allhours = hoursAM + hoursPM

separator = ' '

def dayhour(day, hour):
    return day + separator + hour

def convert_hours(t):
    day, hour = t.split(separator)
    hour = hour.split('h')
    if hour[1] == '':
        minute = 0
    else:
        minute = int(hour[1])
    hour = int(hour[0])
    return days[day] + '%02d%02d' % (hour, minute)
    

def create(table):
    attrs = [
        {'title': 'Enseignant', 'type': 'Login', 'width': 14},
        {'title': 'Discipline', 'type': 'Text', 'width': 5},
        {'title': 'Jour', 'width': 6},
        {'title': '8h30', 'type': 'Bool', 'width': 4, 'green':'=OUI'},
        ]
    last = hoursAM[0]
    for i in hoursAM[1:]:
        attrs.append({'title':i, 'type':'COW', 'columns':last
                      , 'width':4, 'green':'=OUI'})
        last = i
    attrs.append({'title':'Pause', 'type':'Note', 'red':1, 'width':1})
    for i in hoursPM:
        attrs.append({'title':i, 'type':'COW', 'columns':last
                      , 'width':4, 'green':'=OUI'})
        last = i

    ro_page = table.new_page('' ,data.ro_user, '', '')
    rw_page = table.new_page('' ,data.rw_user, '', '')
    for i, column in enumerate(attrs):
        for attr, value in column.items():
              table.column_attr(ro_page, str(i), attr, str(value))

    table.table_attr(ro_page, 'default_sort_column', [0,2])# Name and Day.
    table.table_attr(ro_page, 'default_nr_columns', 21)


def update_referents(the_ids, table, page):
    referents = document.table(table.year, table.semester,
                               'referents', create=False)
    if referents is None:
        return ''
    teachers = tuple(referents.lines.values())

    orientation = document.table(table.year, table.semester,
                                 'orientation_rp', create=False)
    if orientation:
        teachers = tuple(orientation.lines.values()) + teachers
    

    ro_page = table.pages[0]
    rw_page = table.pages[1]
    i = len(table.lines)
    table.lock()
    try:
        for v in teachers:
            if v[0].value == '':
                continue
            if len(tuple(table.get_lines(v[0].value))):
                continue # Referent yet in the table
            for day in days:
                table.cell_change(ro_page, '0', str(i), v[0].value)
                if v[1].value:
                    table.cell_change(ro_page, '1', str(i), v[1].value)
                table.cell_change(ro_page, '2', str(i), day)
                table.cell_change(rw_page, '3', str(i), 'NON')
                i += 1
    finally:
        table.unlock()

    

def check(table):
    import _ucbl_
    _ucbl_.check(table, update_referents)


def init(table):
    table.default_sort_column = [0,2] # Compatibility with old files
    table.default_nr_columns = 21 # Compatibility with old files


def content(table):
    return """<script>
    
function update_student_information(line)
{
   if ( ! t_student_picture.parentNode )
      return ;
   t_student_picture.parentNode.innerHTML = '<div style="font-size:60%;width:20em">Mettez "OUI" dans une cellule pour indiquer que vous êtes présent cette demi-heure.<p>Vous pouvez double-cliquer pour basculer la valeur.</div>' ;

   document.getElementById('horizontal_scrollbar').parentNode.style.display = 'none' ;
}

function modification_allowed_on_this_line(data_lin, data_col)
{
  if ( lines[data_lin][0].value === '' )
  {
     alert("Il est interdit d'ajouter des lignes") ;
     return false ;
  }
  if ( columns[data_col].is_empty )
  {
     alert("Il est interdit d'ajouter des colonnes") ;
     return false ;
  }
  return true ;
}

preferences.display_tips = 'NON' ;
</script>
"""


#
# The end of this TEMPLATE file describe the Plugin using the template.
#

import plugin
import configuration
import collections
import referent

class Teacher(object):
    def __init__(self):
        self.hours = set()
        self.orientation = None
        self.name = None
    def add(self, hour):
        self.hours.add(hour)


def get_teachers_hours():
    year, semester = configuration.year_semester_next

    table = document.table(year, semester, 'rdv_ip', create=False)
    if table is None:
        return None

    teachers = collections.defaultdict(lambda: Teacher())
    for k, v in table.lines.items():
        teacher = teachers[v[0].value]
        teacher.name = v[0].value
        teacher.orientation = v[1].value
        
        day = v[2].value
        value = ''
        for i, slot in enumerate(v):
            title = table.columns[i].title
            if not title[0].isdigit():
                continue # Not a time slot
            if slot.value:
                value = slot.value
            if value == "OUI":
                teacher.add(dayhour(day,title))
                
    return teachers

def rdv_ip(server, stats=True, dsi_table=False, student_table=False):
    """Display informations about rdv_ip"""

    teachers = get_teachers_hours()
    if teachers is None:
        server.the_file.write('No table rdv_ip !')
        return

    year, semester = configuration.year_semester_next
    ori = document.table(year, semester, 'orientation_rp', create=False)
    if ori is None:
        server.the_file.write('No table orientation_rp !')
        return

    orientations = collections.defaultdict(
        lambda: collections.defaultdict(lambda: 0))
    for teacher in teachers.values():
        line = tuple(ori.get_lines(teacher.name))
        if not line:
            continue
        line = line[0]
        for col, cell in zip(ori.columns, line)[2:]:
            if col.title.startswith('_'):
                continue
            try:
                nb_students = float(cell.value)
            except ValueError:
                continue
            orientation = orientations[col.title]
            for hour in teacher.hours:
                orientation[hour] += nb_students

    server.the_file.write(
        '''<style>
        .first TD { border-top:1px solid black ; }
        .c12h, .c17h { border-right:1px solid black ; }
        TABLE { border-spacing: 0px }
        </style>''')

    if stats:
        server.the_file.write('''
        Nombre d\'étudiants maximum par créneaux horaire et population.
        <table><thead><tr class="first">''' +
        ''.join('<th class="c' + i + '">' + i
                for i in ('Population','Jour')+hoursAM + hoursPM) +
        '<th>Total journée' +
        '</tr></thead>')
    
        for name in sorted(orientations):
            orientation = orientations[name]
            first = ' class="first"'
            nr = 0
            day_sum = [0] * len(allhours)
            if len(orientation) == 0:
                server.the_file.write(
                    '<tr' + first + '><td>' + name +
                    '<td class="c' + allhours[-1] +
                    '" colspan="%d">Pas de RDV</td>' % (len(allhours) + 1) +
                    '</tr>')
                continue
            for day in sorted(days):
                for j, i in enumerate(allhours):
                    day_sum[j] += orientation[dayhour(day,i)]
                nb_day = sum(orientation[dayhour(day,i)] for i in allhours)
                server.the_file.write(
                    '<tr' + first + '><td>' + name + '<td>' + day +
                    ''.join('<td class="c' + i + '">'
                            + str(int(orientation[dayhour(day,i)]))
                            for i in allhours
                            ) +
                    '<td class="c%s"><b>' % allhours[-1] + str(int(nb_day)) +
                    '</tr>\n')
                nr += nb_day
                first = ''
            server.the_file.write(
                '<tr><td colspan="2"><i>Sur les %d jours' % len(days)
                + ''.join('<td class="c%s"><i>%d' % (hour, i)
                          for hour, i in zip(allhours, day_sum))
                + '<td class="c%s"><b><i>%d' % (allhours[-1], nr)
            )

        server.the_file.write('</table>')

    if dsi_table:
        server.the_file.write('Fichier pour la DSI :<table border><tr>')
        for c in ('Mention','Parcours','Jour','Heure','Effectif','Ouverture immédiate','Obligation','Interdiction'):
            server.the_file.write('<th>' + c)
        server.the_file.write('</tr>')
        for name in sorted(orientation_rp.orientations):
            orientation = orientations[name]
            for day in sorted(days):
                for hour in allhours:
                    nb_max = int(orientation[dayhour(day,hour)])
                    if nb_max:
                        o = 'O'
                    else:
                        o = 'N'
                    server.the_file.write(
                        '<tr><td>' + orientation_rp.orientations[name][1] +
                        '<td>' + name +
                        '<td>' + day_for_dsi(day) +
                        '<td>' + hour +
                        '<td>' + str(nb_max) +
                        '<td>' + o +
                        '<td>&nbsp;' +
                        '<td>&nbsp;' +
                        '</tr>\n')
        server.the_file.write('</table>')
    
    if student_table:
        server.the_file.write('<pre>')
        for teacher in teachers.values():
            if len(teacher.hours) == 0:
                continue
            if teacher.orientation in orientation_without_referent_rdv:
                continue
            for student in referent.students_of_a_teacher(teacher.name):
                server.the_file.write(student + ' ' + repr(teacher.hours)+'\n')


    
    server.the_file.close()


plugin.Plugin('rdv_ip', '/rdv_ip',
              function=rdv_ip,
              launch_thread=True,
              root=True,
              link=plugin.Link(
                  text='Rendez-vous IP : statistiques',
                  help="""Analyse des rendez-vous IP""",
                  where='root_rw',
                  html_class='verysafe',
                  )
              )
plugin.Plugin('rdv_ip_dsi', '/rdv_ip_dsi',
              documentation="Création du fichier RdVIP pour la DSI",
              function=lambda server:rdv_ip(server,stats=False,dsi_table=True),
              launch_thread=True,
              root=True,
              link=plugin.Link(
                  text='Rendez-vous IP : DSI',
                  help="""Tableau à envoyer à la DSI""",
                  where='root_rw',
                  html_class='verysafe',
                  )
              )
plugin.Plugin('rdv_ip_student', '/rdv_ip_student',
              documentation="Liste des créneaux des étudiants",
              function=lambda server: rdv_ip(server,
                                             stats=False, student_table=True),
              launch_thread=True,
              root=True,
              link=plugin.Link(
                  text='Rendez-vous IP : étudiant',
                  help="Pour le débuggage, liste les créneaux des étudiants.",
                  where='root_rw',
                  html_class='verysafe',
                  )
              )

"""
http://www.univ-lyon1.fr/cridev/Apogee_Web_Lmd/Rdv_Choix_Ip/index_test.php
http://www.univ-lyon1.fr/cridev/Apogee_Web_Lmd/Rdv_Choix_Ip/affichage_planning.php

18/11/1991
SELECT * FROM RDV_IPUE_CRENEAUX_AUTO WHERE NUM_ETUDIANT = '11004734' ;

DELETE FROM RDV_IPUE_CRENEAUX_AUTO WHERE DATE_CRENEAU < '201102161300' ;

for D in 14 15 16 17 ; do for H in 0830 0900 0930 1000 1030 1100 1130 1200 1300 1330 1400 1430 1500 1530 1600 1630 1700 1730 ; do
echo "INSERT INTO RDV_IPUE_CRENEAUX_AUTO VALUES('11004734', '201102$D$H') ;"
done ; done

"""

def fill_rdv_table(server):
    """Fill the Database with information from TOMUSS"""
    
    teachers = get_teachers_hours()
    s = ["ALTER SESSION SET NLS_DATE_FORMAT='YYYYMMDDHH24MI'",
         "SET TRANSACTION NAME 'tomuss'",
         "DELETE FROM RDV_IPUE_CRENEAUX_AUTO WHERE NUM_ETUDIANT > 0",
         ]

    for teacher in teachers.values():
        if len(teacher.hours) == 0:
            continue
        if teacher.orientation in orientation_without_referent_rdv:
            continue
        for student in referent.students_of_a_teacher(teacher.name):
            for hour in teacher.hours:
                s.append(
                    "INSERT INTO RDV_IPUE_CRENEAUX_AUTO VALUES('%s','%s')" %(
                        student, convert_hours(hour))
                    )
    s.append('COMMIT')

    import time
    import sys
    import cx_Oracle
    import LOCAL.fakeuser
    connection = cx_Oracle.Connection(LOCAL.fakeuser.oracle)
    cursor = cx_Oracle.Cursor(connection)
    for i, command in enumerate(s):
        server.the_file.write(command + '\n')
        cursor.execute(command)
    cursor.close()
    connection.close()

plugin.Plugin('fill_rdv_table', '/fill_rdv_table',
              function=fill_rdv_table,
              launch_thread=True,
              root=True,
              link=plugin.Link(
                  text='Rendez-vous IP : Mise à jour table DSI',
                  help="Recopie les informations dans la table Oracle",
                  where='root_rw',
                  html_class='safe',
                  ),
              mimetype="text/plain",
              )


