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
    for name, help, typ, width in (
        ('plugin'        , 'Plugin name'                  , 'Text', 4 ),
        ('info'          , 'Plugin description'           , 'Text', 20),
        ('link'          , 'Home page link'               , 'Text', 4 ),
        ('suivi'         , 'Is a "suivi" only plugin'     , 'Text', 1 ),
        ('root'          , 'Need Root rights'             , 'Bool', 1 ),
        ('abj'           , 'Need abj master rights'       , 'Bool', 1 ),
        ('referent'      , 'Need referent master rights'  , 'Bool', 1 ),
        ('teacher'       , 'Need teacher rights'          , 'Bool', 1 ),
        ('administrative', 'Need administrative rights'   , 'Bool', 1 ),
        ('invited'       , 'Login list with plugin access', 'Text', 8 ),
        ):
        if table.columns.from_title(name):
            continue
        table.column_change(table.pages[0], name, name, typ,'','','',0,width)
        table.column_comment(table.pages[0], name, help)
    table.table_attr(table.pages[0], 'default_nr_columns', len(table.columns))

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

    d =  {None: '',True:'OUI',False:'NON'}

    try:
        for p in plugin.plugins + plugins.suivi_plugins:
            table.cell_change(table.pages[0], 'plugin', p.name, p.name)
            if p.documentation:
                table.cell_change(table.pages[0], 'info'  , p.name,
                                  p.documentation)
            if p.link:
                table.cell_change(table.pages[0], 'link', p.name, p.link.where)
            
            table.cell_change(table.pages[0], 'root', p.name, d[p.root])
            table.cell_change(table.pages[0], 'abj', p.name,  d[p.abj_master])
            table.cell_change(table.pages[0], 'teacher', p.name, d[p.teacher])
            table.cell_change(table.pages[0], 'referent', p.name,d[p.referent_master])
            table.cell_change(table.pages[0], 'administrative', p.name,
                              d[p.administrative])
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

def cell_change(table, page, col, lin, value, date):
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
