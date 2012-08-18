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

import configuration
import plugin
import plugins
import data
import utilities

def update_column(table):
    for name, typ, width, deprecated in (
        ('plugin'        , 'Text', 8 , False),
        ('info'          , 'Text', 20, False),
        ('link'          , 'Text', 6 , False),
        ('suivi'         , 'Text', 1 , False),
        ('root'          , 'Bool', 1 , True),
        ('abj'           , 'Bool', 1 , True),
        ('referent'      , 'Bool', 1 , True),
        ('teacher'       , 'Bool', 1 , True),
        ('administrative', 'Bool', 1 , True),
        ('invited'       , 'Text', 20, False),
        ):
        if table.columns.from_title(name):
            if deprecated:
                table.column_attr(table.pages[0], name, 'hidden', 1)
            else:
                table.column_attr(table.pages[0], name, 'width', width)
            continue
        if deprecated:
            continue
        table.column_change(table.pages[0], name, name, typ,'','','',0,width)
        table.column_comment(table.pages[0], name,
                             utilities._('COL_TITLE_cp_' + name))
    table.table_attr(table.pages[0], 'default_nr_columns', 5)


def create(table):
    if table.year != 0 or table.semester != 'Dossiers':
        raise ValueError('Not allowed')
    p = table.new_page('' ,data.ro_user, '', '')
    table.table_attr(p, 'masters', list(configuration.root))
    update_column(table)

def init(table):
    table.default_sort_column = 2
    table.private = 1

def check(table):
    table.lock()
    update_column(table)
    table.unlock()

    table.lock()

    d =  {None: '',True: configuration.yes,False:configuration.no}

    try:
        for p in plugin.plugins + plugins.suivi_plugins:
            table.cell_change(table.pages[0], 'plugin', p.name, p.name)
            if p.documentation:
                table.cell_change(table.pages[0], 'info'  , p.name,
                                  p.documentation)
            if p.link:
                table.cell_change(table.pages[0], 'link', p.name, p.link.where)
            
        for p in plugins.suivi_plugins:
            table.cell_change(table.pages[0], 'suivi', p.name, 'S')
            
    finally:
        table.unlock()

def onload(table):
    if configuration.regtest:
        return # Security Hole
    c = table.columns.from_id('invited').data_col
    for p in plugin.plugins + plugins.suivi_plugins:
        try:
            value = tuple(table.get_lines(p.name))[0][c].value
        except IndexError:
            value = '()'
        p.invited = ()
        if value:
            try:
                p.invited = eval(value)
            except:
                utilities.send_backtrace('config_plugin')

import config_table

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
    config_table.tell_to_reload_config()
