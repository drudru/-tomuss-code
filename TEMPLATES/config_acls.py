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

import time
from .. import configuration
from .. import utilities
from .. import referent
from .. import inscrits

acls = None

def defaults():
    # 'roots' are in ALL the groups
    for root in configuration.root:
        yield 'roots', root

    for ldap_teacher in configuration.teachers:
        yield 'teachers', 'ldap:' + ldap_teacher
    for teacher in configuration.invited_teachers:
        yield 'teachers', teacher
    yield 'teachers', 'python:configuration.teacher_if_login_contains in login'

    yield 'staff', 'grp:teachers'
    
    for ldap_administrative in configuration.administratives:
        yield 'administratives', 'ldap:' + ldap_administrative
    for administrative in configuration.invited_administratives:
        yield 'administratives', administrative
    yield 'staff', 'grp:administratives'

    for ldap_abj_master in configuration.abj_masters:
        yield 'abj_masters', 'ldap:' + ldap_abj_master
    for abj_master in configuration.invited_abj_masters:
        yield 'abj_masters', abj_master
    yield 'staff', 'grp:abj_masters'
    
    for a_referent in configuration.referents:
        yield 'referents', 'ldap:' + a_referent
    if configuration.regtest:
        yield 'referents', 'a_referent'
    yield 'staff', 'grp:referents'

    try:
        for login in referent.referents_students().masters:
            yield 'referent_masters', login
    except ImportError:
        pass
    yield 'staff', 'grp:referent_masters'
    yield 'see_private_suivi', 'grp:roots'

def create(table):
    """Retrieve informations from configuration.py and old table_config.py"""
    
    if table.year != 0 or table.semester != 'Dossiers':
        raise ValueError('Not allowed')
    
    p = table.get_a_root_page()

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
            
    i = 0
    for group, member in defaults():
        table.cell_change(p, 'a', str(i), member)
        table.cell_change(p, 'b', str(i), group)
        i += 1
            
    table.table_attr(p, 'masters', list(configuration.root))
    table.table_attr(p, 'default_sort_column', [1,0])
    table.table_attr(p, 'default_nr_columns', 4)
    table.table_attr(p, 'private', 1)

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
    table.do_not_unload_add('*config_acls')

def cell_change(table, page, col, lin, value, dummy_date):
    """Only here to clear cache and update ACLS in 'suivi' servers"""
    if page.page_id == 0:
        return
    configuration.tell_to_reload_config()
    
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

def trace(fct):
    def f(*args, **keys):
        try:
            a = fct(*args, **keys)
        except:
            print 'RAISE ERROR'
            raise
        print fct, repr(args)[:50], keys, '====>', a
        return a
    return f

# @trace
def login_is_member(login, member, member_of):
    """No negation (!) here.
    'member' is ONE group name
    'member_of' contains the LDAP groups of the login
    """
    if member == login:
        return True
    elif member.startswith('ldap:'):
        if login in configuration.login_not_teacher:
            return False
        member = member[5:]
        # Remove if it is in a group of non teacher.
        # This is deprecated, do not use it.
        for i in configuration.not_teachers:
            for j in member_of:
                if j.endswith(i):
                    return False
        for i in member_of:
            if i.endswith(member):
                return True
    elif member.startswith('python:') and not configuration.regtest:
        member = member[7:]
        try:
            if eval(member):
                return True
        except:
            pass
    elif member.startswith('grp:'):
        if member == 'grp:':
            return True
        return is_member_of_(login, members(member[4:]), member_of)
    return False


def is_member_of_(login, group, member_of):
    """The negation ! has priority over the other AT THE SAME LEVEL
    'group' is a list of group name
    'member_of' contains the LDAP groups of the login
    If the group list contains only a !group, then it mean ALL-group
    """
    if group == '':
        return True
    if isinstance(group, str):
        group = (group, )

    # To support deprecated syntax
    group = [g.replace("grp:!", "!grp:") for g in group]

    for member in group:
        if member.startswith('!'):
            if login_is_member(login, member[1:], member_of):
                return False

    if len(group) == 1 and group[0].startswith("!"):
        return True
    
    for member in group:
        if not member.startswith('!'):
            if login_is_member(login, member, member_of):
                return True
    return False


cache = {}

def is_member_of(login, group):
    """A group name or a tuple"""
    if (login, group) not in cache:
        if time.time() - clear_cache.last_clear > 3600:
            clear_cache()
        member_of = inscrits.L_fast.member_of_list(login)
        if group == '':
            result = True
        elif is_member_of_(login, members("roots"), member_of):
            if group:
                if '!' in group[0]:
                    result = False
                else:
                    result = True
            else:
                result = False
        else:
            if isinstance(group, str):
                grp = ("grp:" + group,)
            else:
                grp = group
            result = is_member_of_(login, grp, member_of)

        cache[login, group] = result

    return cache[login, group]

def clear_cache():
    utilities.warn("Clear Cache")
    cache.clear()
    clear_cache.last_clear = time.time()

clear_cache()

configuration.config_acls_clear_cache = clear_cache
