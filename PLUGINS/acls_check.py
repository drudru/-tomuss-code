#!/bin/env python3
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2018 Thierry EXCOFFIER, Universite Claude Bernard
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

from .. import plugin
from .. import utilities
from .. import cell
from .. import column
from .. import document
from .. import inscrits
from .. import configuration

def acls_check(server):
    p1 = utilities.ProgressBar(server)
    nr = len(configuration.config_acls_all_users()) - 1
    all_users = set()
    for i, login in enumerate(configuration.config_acls_all_users()):
        p1.update(i, nr)
        if (not configuration.is_member_of(login, 'grp:roots')
            and login != ''):
            all_users.add(login.lstrip('!'))

    p2 = utilities.ProgressBar(server)
    all_groups = configuration.config_acls_all_the_groups()
    lines = []
    for i, login in enumerate(all_users):
        p2.update(i, len(all_users))
        if len(inscrits.L_slow.member_of_list(login)) == 0:
            fn,sn,mail = inscrits.L_slow.firstname_and_surname_and_mail(login)
            lines.append(cell.Line((
                cell.CellValue(login),
                cell.CellValue(fn),
                cell.CellValue(sn),
                cell.CellValue(mail),
                cell.CellEmpty(),
                cell.CellValue(' '.join(
                    group
                    for group in all_groups
                    if login in configuration.acls_config_members(group)
                    )),
                )))
            continue

        for group in all_groups:
            if not configuration.is_member_of(login, group):
                m = []
                accepted = []
                rejected = []
                for subgroup in configuration.acls_config_members(group):
                    sg = subgroup.lstrip('!')
                    if login == sg or configuration.is_member_of(login,(sg,)):
                        if subgroup == sg:
                            accepted.append(subgroup)
                        else:
                            rejected.append(subgroup)
                if rejected and not accepted:
                    fn,sn,mail = inscrits.L_slow.firstname_and_surname_and_mail(login)
                    lines.append(cell.Line((
                        cell.CellValue(login),
                        cell.CellValue(fn),
                        cell.CellValue(sn),
                        cell.CellValue(mail),
                        cell.CellValue(group),
                        cell.CellValue('!!! {} {}'.format(accepted, rejected) )
                        )))
                    
                continue
            subgroups = {subgroup
                         for subgroup in configuration.acls_config_members(group)
                         if not subgroup.startswith('!')
                        }
            m = []
            for i in subgroups:
                if (i == login
                    or ':' in i and configuration.is_member_of(login, (i,))
                    ):
                    if ':' not in i:
                        i = "***" + i + "***"
                    m.append(i)
            if len(m) > 1:
                m.sort()
                fn,sn,mail = inscrits.L_slow.firstname_and_surname_and_mail(login)
                lines.append(cell.Line((
                    cell.CellValue(login),
                    cell.CellValue(fn),
                    cell.CellValue(sn),
                    cell.CellValue(mail),
                    cell.CellValue(group),
                    cell.CellValue(' '.join(m)),
                    )))
    p1.hide()
    p2.hide()
    columns = [
        column.Column('0', '', title=server._('COL_TITLE_0_0')),
        column.Column('1', '', title=server._('COL_TITLE_0_1'), width=1),
        column.Column('2', '', title=server._('COL_TITLE_0_2'), width=1),
        column.Column('3', '', title=server._('TITLE_table_attr_mail'), width=1),
        column.Column('4', '', title=server._("COL_COMMENT_acls_group"),
                      red='='),
        column.Column('5', '', title=server._("COL_COMMENT_acls_group"),
                      width=20, red="~***|~!!!", green="~!!!"),
        ]
    document.virtual_table(server, columns, lines,
                           table_attrs={'default_nr_columns': 6,
                                        'comment': server._("MSG_acls_check")
                                        })


plugin.Plugin('acls_check', '/acls_check',
              launch_thread = True,
              function=acls_check, group='roots',
              )
