#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2010-2012 Thierry EXCOFFIER, Universite Claude Bernard
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

from .. import configuration
from .. import plugin
from .. import plugins
from .. import data
from .. import utilities
from .. import sender

def update_column(table):
    do_migrate = False
    for name, typ, width, deprecated in (
        ('plugin'        , 'Text', 4 , False),
        ('info'          , 'Text', 10, False),
        ('link'          , 'Text', 3 , False),
        ('suivi'         , 'Text', 1 , False),
        ('root'          , 'Bool', 1 , True),
        ('abj'           , 'Bool', 1 , True),
        ('referent'      , 'Bool', 1 , True),
        ('teacher'       , 'Bool', 1 , True),
        ('administrative', 'Bool', 1 , True),
        ('invited'       , 'Text', 20, False),
        ):
        if deprecated:
            if table.columns.from_title(name):
                if not table.columns.from_title(name).hidden:
                    table.column_attr(table.pages[0], name, 'hidden', 1)
                    do_migrate = True
            continue
        if not table.columns.from_title(name):
            # XXX To not store type each time (bug elsewhere)
            table.column_attr(table.pages[0], name, 'type', typ)
        table.column_attr(table.pages[0], name, 'width', width)
        table.column_comment(table.pages[0], name,
                             utilities._('COL_TITLE_cp_' + name))
    table.table_attr(table.pages[0], 'default_nr_columns', 5)

    if do_migrate:
        c = table.columns.from_id('invited').data_col
        done = set()
        for p in plugin.plugins + plugins.suivi_plugins:
            if p.name in done:
                continue
            done.add(p.name)
            if p.name not in table.lines:
                continue
            value = table.lines[p.name][c].value.strip()
            if value:
                new = '("grp:' + p.group + '",' + value.lstrip('(')
            else:
                new = '("grp:' + p.group + '",)'
            table.cell_change(table.pages[1], 'invited', p.name, new)

def create(table):
    if table.year != 0 or table.semester != 'Dossiers':
        raise ValueError('Not allowed')
    p = table.new_page('' ,data.ro_user, '', '')
    p = table.new_page('' ,configuration.root[0], '', '')
    table.table_attr(p, 'masters', list(configuration.root))
    update_column(table)
    check(table, from_create=True)

def init(table):
    table.default_sort_column = 2
    table.private = 1
    table.do_not_unload_add('*config_plugin')

def check(table, from_create=False):
    if not from_create:
        table.lock()
        update_column(table)

    d =  {None: '',True: configuration.yes,False:configuration.no}

    try:
        tomuss = set(p.name for p in plugin.plugins)
        suivi = set(p.name for p in plugins.suivi_plugins)
        for p in plugin.plugins + plugins.suivi_plugins:
            if p.name not in table.lines:
                table.cell_change(table.pages[1], 'invited', p.name,
                                  '("grp:' + p.group + '",)')
            table.cell_change(table.pages[0], 'plugin', p.name, p.name)
            if p.documentation:
                table.cell_change(table.pages[0], 'info'  , p.name,
                                  p.documentation)
            if p.link:
                table.cell_change(table.pages[0], 'link', p.name, p.link.where)

            is_in = ''
            if p.name in tomuss:
                is_in += 'T'
            if p.name in suivi:
                is_in += 'S'
                        
            table.cell_change(table.pages[0], 'suivi', p.name, is_in)
            
    finally:
        if not from_create:
            table.unlock()

def onload(table):
    if configuration.regtest:
         # To close a Security Hole
        for p in plugin.plugins + plugins.suivi_plugins:
            p.invited = ('grp:' + p.group,)
        return
    c = table.columns.from_id('invited').data_col
    for p in plugin.plugins + plugins.suivi_plugins:
        try:
            value = tuple(table.get_lines(p.name))[0][c].value
        except IndexError:
            # Was not in the table
            value = '("grp:' + p.group + '",)'
        p.invited = ()
        if value:
            try:
                p.invited = eval(value)
                if not p.invited:
                    utilities.send_backtrace('config_plugin: ' + str(p),
                                             exception=False)
            except:
                utilities.send_backtrace('config_plugin: ' + str(p),
                                         exception=False)
        else:
            utilities.send_backtrace('config_plugin2: ' + str(p),
                                     exception=False)

def cell_change(table, page, col, lin, value, dummy_date):
    if configuration.regtest:
        return # Security Hole
    if col != 'invited':
        return

    plugin_name = table.lines[lin][0].value
    for p in plugin.plugins + plugins.suivi_plugins:
        if plugin_name != p.name:
            continue
        p.invited = ()
        if value.strip() == '':
            continue
        try:
            p.invited = eval(value)
        except:
            sender.append(page.browser_file,
                          '<script>alert("Error!");</script>')
            utilities.send_backtrace('config_plugin')

    if page.page_id > 1:
        configuration.tell_to_reload_config()

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
