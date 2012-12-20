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

"""
The title and help is translated if it is found in the translations files.
"""

from .. import data
from .. import utilities
from .. import configuration
from .. import plugin
from .. import cell

default_links = (
    ("abj_master", -99, "unsafe", 'abj_masters',
     "javascript:go_year('Dossiers/tt')"),
    ("abj_master", -100, "verysafe", "abj_masters",
     "javascript:go_year('Dossiers/tt/=read-only=')"),
    ("informations",0,"verysafe", ""  ,"//stats.html"),
    ('referents',999,'safe'   ,'roots',"javascript:go('referents_students')"),
    ("root_rw",-900,"verysafe",'roots',"/0/Dossiers/config_table/=read-only="),
    ("root_rw",-809,"unsafe"  ,'roots',"/0/Dossiers/config_table"),
    ("root_rw",-808,"unsafe"  ,'roots',"/0/Dossiers/config_acls"),
    ("root_rw",-807,"safe"    ,'roots',"/0/Dossiers/config_plugin"),
    ("root_rw",-806,"safe"    ,'roots',"/0/Dossiers/config_home"),
    ("debug"  ,   0,"verysafe",'roots',"/0/Dossiers/javascript_regtest_ue"),
    ("debug"  ,   0,"verysafe",'roots',"/0/Test/average"),
    ("debug"  ,   0,"verysafe",'roots',"javascript:go('demo_animaux')"),
    ("debug"  ,   0,"verysafe",'roots',"/0/Test/test_types"),
    )

def create(table):
    utilities.warn('Creation')
    if table.year != 0 or table.semester != 'Dossiers':
        raise ValueError('Not allowed')
    ro = table.new_page('' ,data.ro_user, '', '')
    rw = table.new_page('' ,configuration.root[0], '', '')
    table.table_attr(ro, 'masters', list(configuration.root))
    table.table_attr(ro, 'default_nr_columns', 7)
    table.table_attr(ro, 'default_sort_column', [0,1])
    table.update_columns(
        {
            '0': {'type': 'Text',
                  'freezed': 'F',
                  'title': utilities._("COL_TITLE_ch_box"),
                  'comment': utilities._("COL_COMMENT_ch_box"),
                  },
            '1': {'type': 'Note',
                  'freezed': 'F',
                  'title': utilities._("COL_TITLE_ch_priority"),
                  'comment': utilities._("COL_COMMENT_ch_priority"),
                  'width': 2,
                  'minmax': '[-100;100]',
                  },
            '2': {'type': 'Enumeration',
                  'freezed': 'F',
                  'enumeration': 'veryunsafe unsafe safe verysafe',
                  'red': 'veryunsafe',
                  'green': 'verysafe',
                  'title': utilities._("COL_TITLE_ch_htmlclass"),
                  'comment': utilities._("COL_COMMENT_ch_htmlclass"),
                  'width': 2,
                  },
            '3': {'type': 'Text',
                  'freezed': 'F',
                  'title': utilities._("COL_TITLE_ch_group"),
                  'comment': utilities._("COL_COMMENT_ch_group"),
                  'width': 6,
                  },
            '4': {'type': 'Text',
                  'title': utilities._("COL_TITLE_ch_title"),
                  'comment': utilities._("COL_COMMENT_ch_title"),
                  'width': 12,
                  },
            '5': {'type': 'URL',
                  'title': utilities._("COL_TITLE_ch_url"),
                  'comment': utilities._("COL_COMMENT_ch_url"),
                  'width': 12,
                  },
            '6': {'type': 'Text',
                  'title': utilities._("COL_TITLE_ch_help"),
                  'comment': utilities._("COL_COMMENT_ch_help"),
                  'width': 12,
                  },
            }, ro)
    i = 0
    for where, priority, html_class, group, url in  default_links:
        table.cell_change(rw, '0', str(i), where)
        table.cell_change(rw, '1', str(i), priority)
        table.cell_change(rw, '2', str(i), html_class)
        table.cell_change(rw, '3', str(i), group)
        table.cell_change(rw, '4', str(i), 'LINK_' + url)
        table.cell_change(rw, '5', str(i), url)
        table.cell_change(rw, '6', str(i), 'HELP_' + url)
        i += 1


def add_link(line_id, line):
    if line[1].value:
        priority = float(line[1].value)
    else:
        priority = 0
    if line[2].value:
        html_class = line[2].value
    else:
        html_class = "safe"
    plugin.add_links(
        plugin.Link(
            where      = line[0].value,
            priority   = priority,
            html_class = html_class,
            group      = line[3].value,
            text       = utilities._(line[4].value),
            url        = line[5].value,
            help       = utilities._(line[6].value),
            key        = line_id,
            ))
    
def onload(table):
    """Add URLs to the home page"""
    for line_id, line in table.lines.items():
        add_link(line_id, line)
        
def cell_change(table, page, col, lin, value, dummy_date):
    if page.page_id < 2:
        return
    for link in plugin.links_without_plugins:
        if link.key == lin:
            plugin.links_without_plugins.remove(link)
    data_col = table.columns.from_id(col).data_col
    line = table.lines[lin]
    tmp = line[data_col]
    line[data_col] = cell.CellValue(value)
    add_link(lin, line)
    line[data_col] = tmp

        
