#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2012 Thierry EXCOFFIER, Universite Claude Bernard
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

import configuration
import utilities
import collections
import referent
import inscrits

acls = None

def create(table):
    """Retrieve informations from configuration.py and old table_config.py"""
    
    if table.year != 0 or table.semester != 'Dossiers':
        raise ValueError('Not allowed')
    
    p = table.new_page('' , configuration.root[0], '', '')

    _ = utilities._
    table.update_columns({
            'a' : {'title': _("COL_TITLE_acls_member"),
                   'comment': _("COL_COMMENT_acls_member"),
                   'type':'Text', "width":8 },
            'b' : {'title': _("COL_TITLE_acls_group"),
                   'comment': _("COL_COMMENT_acls_group"),
                   'type':'Text', "width":4 },
            'c' : {'title': _("COL_TITLE_acls_date"),
                   'comment': _("COL_COMMENT_acls_date"),
                   'type':'Date', "width":4 },
            'd' : {'title': _("COL_TITLE_acls_comment"),
                   'comment': _("COL_COMMENT_acls_comment"),
                   'type':'Text', "width":16 },
            })
            
    table.table_attr(p, 'masters', list(configuration.root))
    table.table_attr(p, 'default_sort_column', [1,0])
    table.table_attr(p, 'default_nr_columns', 4)
    table.table_attr(p, 'private', 1)

    defaults = collections.defaultdict(list)
    # 'roots' are in ALL the groups
    for root in configuration.root:
        defaults['roots'].append(root)

    for ldap_teacher in configuration.teachers:
        defaults['teachers'].append('ldap:' + ldap_teacher)
    for teacher in configuration.invited_teachers:
        defaults['teachers'].append(teacher)
    defaults['teachers'].append(
        'python:configuration.teacher_if_login_contains in login')

    defaults['staff'].append('grp:teachers')
    
    for ldap_administrative in configuration.administratives:
        defaults['administratives'].append('ldap:' + ldap_administrative)
    for administrative in configuration.invited_administratives:
        defaults['administratives'].append(administrative)
    defaults['staff'].append('grp:administratives')

    for ldap_abj_master in configuration.abj_masters:
        defaults['abj_masters'].append('ldap:' + ldap_abj_master)
    for abj_master in configuration.invited_abj_masters:
        defaults['abj_masters'].append(abj_master)
    defaults['staff'].append('grp:abj_masters')
    
    for a_referent in configuration.referents:
        defaults['referents'].append('ldap:' + a_referent)
    if configuration.regtest:
        defaults['referents'].append('a_referent')
    defaults['staff'].append('grp:referents')

    try:
        for login in referent.referents_students().masters:
            defaults['referent_masters'].append(login)
    except ImportError:
        pass
    defaults['staff'].append('grp:referent_masters')
    
    for teacher in configuration.not_teachers:
        defaults['REJECTED'].append('ldap:' + teacher)

    i = 0
    for groupe, members in defaults.items():
        for member in members:
            table.cell_change(p, 'a', str(i), member)
            table.cell_change(p, 'b', str(i), groupe)
            i += 1

def content(dummy_table):
    return r"""
function update_student_information(line)
{
   if ( ! t_student_picture.parentNode )
      return ;
   t_student_picture.parentNode.innerHTML = '' ;

   document.getElementById('horizontal_scrollbar').parentNode.style.display = 'none' ;
}
"""

def init(table):
    global acls
    acls = table
    configuration.is_member_of = is_member_of

def members(group):
    """First level members of a group.
    LDAP members are put in first place for optimization
    """
    membs = [line[0].value
             for line in acls.lines.values()
             if line[1].value == group
             ]
    membs.sort(key=lambda x: x.startswith('ldap:') and 1 or 0)
    return membs

def is_member_of_(login, group, member_of):
    if group[0] == '!':
        true = False
        group = group[1:]
    else:
        true = True
    for member in members(group):
        if member == login:
            return true
        if member.startswith('ldap:'):
            member = member[5:]
            for i in member_of:
                if member.endswith(i):
                    return true
            continue
        if member.startswith('python:') and not configuration.regtest:
            member = member[7:]
            try:
                if eval(member):
                    return true
            except:
                pass
            continue
        if member.startswith('grp:'):
            if is_member_of_(login, member[4:], member_of):
                return true
            continue
    return not true

def is_member_of(login, group):
    # utilities.warn("%s %s" % (login, group))
    member_of = inscrits.L_fast.member_of_list(login)
    if group == '':
        return True
    if group[0] == '!':
        # REJECTED are in no groups
        if is_member_of_(login, "REJECTED", member_of):
            return True
    else:
        if is_member_of_(login, "REJECTED", member_of):
            return False
        if is_member_of_(login, "roots", member_of):
            return True
    return is_member_of_(login, group, member_of)
