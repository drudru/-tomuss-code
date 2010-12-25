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
import _ucbl_
import configuration

# The orientation is the key.
# The couple is : the screen order and the Mention of the Orientation

orientations = {
    
'Portail_Math-Info': ( 0,'Portail Math-Info'),
'MASS'             : ( 1,'MASS'             ),
'MATHMIV'          : ( 2,'MATH'             ),
'INFOMIV'          : ( 3,'INFO'             ),
'Portail_PCSI'     : ( 4,'Portail PCSI'     ),
'EEA'              : ( 5,'GEGP'             ),
'GENPROC'          : ( 6,'GEGP'             ),
'GCC'              : ( 7,'MécaGC'           ),
'PHYPHYCHI'        : ( 8,'PHY'              ),
'Portail_SVT'      : ( 9,'Portail SVT'      ),
'BGSTU_MIV'        : (10,'BIOLOGIE'         ),
'GBC_M_P_BOP'      : (11,'BIOLOGIE'         ),
'BIOCH'            : (12,'BIOCH'            ),
'STE'              : (13,'STE'              ),
}
    
def create(table):
    attrs = [
        {'title': 'Enseignant', 'type': 'Login', 'width': 14},
        {'title': 'Discipline', 'type': 'Text', 'width': 3},
        ]
    i = 1
    for orientation in sorted(orientations,
                              key=lambda x: orientations[x][0]):
        if orientation.startswith('Portail'):
            attrs.append({'title':'_'*i, 'type':'Note', 'red':99, 'width':1})
            i += 1

        attrs.append( {'title': orientation,
                       'type': 'Note',
                       'minmax': '[0;99]',
                       'green': '0',
                       'weight': '+1',
                       'red': '>5',
                       'empty_is': '0',
                       'comment': "Nombre d'étudiants par demi-heure",
                       }
                      )
    attrs.append({'title':'_'*i, 'type':'Note', 'red':99, 'width':1})
    attrs.append(
        {'title': 'TOTAL', 'type': 'Moy', 'red': '>5',
         'columns': ' '.join(orientations)},
        )

    ro_page = table.new_page('' ,data.ro_user, '', '')
    rw_page = table.new_page('' ,data.rw_user, '', '')
    for i, column in enumerate(attrs):
        for attr, value in column.items():
              table.column_attr(ro_page, str(i), attr, str(value))

    table.table_comment(ro_page, "Populations traitées par les enseignants")

def init(table):
    _ucbl_.init(table)
    if (table.year, table.semester) != configuration.year_semester:
        table.modifiable = table.update_inscrits = 0
    table.default_nr_columns = len(orientations) + 3 + len(
        [i for i in orientations if i.startswith('Portail')])
    

def update_referents(the_ids, table, page):
    referents = document.table(table.year, table.semester,
                               'referents', create=False)
    if referents is None:
        return ''

    ro_page = table.pages[0]
    rw_page = table.pages[1]
    i = len(table.lines)
    table.lock()
    try:
        for k, v in referents.lines.items():
            if v[0].value == '':
                continue
            if len(tuple(table.get_lines(v[0].value))):
                continue # Referent yet in the table
            table.cell_change(ro_page, '0', str(i), v[0].value)
            i += 1
    finally:
        table.unlock()

def check(table):
    _ucbl_.check(table, update_referents)

def content(table):
    return r"""<script>
    
function update_student_information(line)
{
   if ( ! t_student_picture.parentNode )
      return ;
   t_student_picture.parentNode.innerHTML = '<div style="font-size:60%;width:15em">Pour chaque population d\'étudiant il faut indiquer le nombre d\'étudiants que vous prenez par demi-heure.</div>' ;

   document.getElementById('horizontal_scrollbar').parentNode.style.display = 'none' ;
}
preferences.display_tips = 'NON' ;
</script>

"""
