#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2012-2013 Thierry EXCOFFIER, Universite Claude Bernard
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

import ast
from .. import utilities
from .. import configuration
from .. import plugin
from .. import cell

default_links = (
    ################################################################
    # XXX ALWAYS ADD ITEMS TO THE END: because lin_id is the index
    # The order on screen is the priority
    ################################################################
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
    ("debug"  ,   0,"verysafe",'roots',"javascript:go('demo_animaux')"),
    ("debug"  ,   0,"verysafe",'roots',"/0/Test/test_types"),
    ("root_rw",-805,"safe"    ,'roots',"/0/Dossiers/config_cache"),
    ("root_rw",-804,"safe"    ,'roots',"/0/Dossiers/config_login"),
    ("root_rw",-803,"safe"    ,'roots',"/0/Dossiers/config_room"),
    ("root_rw",-802,"safe"    ,'roots',"/0/Dossiers/config_messages"),
    )

columns = {
    '0': {'type': 'Text', 'freezed': 'F',
          'title': utilities._("COL_TITLE_ch_box"),
          'comment': utilities._("COL_COMMENT_ch_box"),
          },
    '1': {'type': 'Note', 'freezed': 'F',
          'title': utilities._("COL_TITLE_ch_priority"),
          'comment': utilities._("COL_COMMENT_ch_priority"),
          'width': 2, 'minmax': '[-1000;1000]',
          },
    '2': {'type': 'Enumeration', 'freezed': 'F',
          'enumeration': 'veryunsafe unsafe safe verysafe',
          'red': 'veryunsafe', 'green': 'verysafe', 'width': 2,
          'title': utilities._("COL_TITLE_ch_htmlclass"),
          'comment': utilities._("COL_COMMENT_ch_htmlclass"),
          },
    '3': {'type': 'Text', 'freezed': 'F',
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
    }

def create(table):
    utilities.warn('Creation')
    if table.year != 0 or table.semester != 'Dossiers':
        raise ValueError('Not allowed')
    ro = table.get_ro_page()
    table.get_a_root_page()
    table.table_attr(ro, 'masters', list(configuration.root))
    table.table_attr(ro, 'default_nr_columns', 7)
    table.table_attr(ro, 'default_sort_column', [0,1])
    table.update_columns(columns, ro)

def add_new_links_in_the_table(table):
    """Create missing lines in the table"""
    rw = table.pages[1]
    def change(lin_id, values):
        yet_in = lin_id in table.lines
        for col, value in enumerate(values):
            col = str(col)
            if  not yet_in or '<script' in str(value):
                table.cell_change(rw, col, lin_id, value)
        
    table.lock()
    try:
        i = 0
        for where, priority, html_class, group, url in  default_links:
            lin_id = str(i)
            i += 1
            change(lin_id,
                   (where, priority, html_class, group, 'LINK_' + url,
                    url, 'HELP_' + url))
        for p in plugin.plugins:
            link = p.link
            if not link:
                continue
            lin_id = p.name
            if link.text:
                text = link.text
            elif link.plugin:
                text = 'LINK_' + link.plugin.name
            else:
                text = ''
            if link.help:
                help = link.help
            elif link.plugin:
                help = 'HELP_' + link.plugin.name
            else:
                help = ''
            change(lin_id, (link.where, link.priority, link.html_class,
                            str(link.group), text, link.url, help))
    finally:
        table.unlock()

def link_values(lin_id, line):
    """Return attributes of a link from the table"""
    if line[1].value:
        priority = float(line[1].value)
    else:
        priority = 0
    if line[2].value:
        html_class = line[2].value
    else:
        html_class = "safe"
    if line[4].value:
        text = utilities._(line[4].value)
    else:
        text = ''
    if line[6].value:
        tip = utilities._(line[6].value)
    else:
        tip = ''

    return {
        "where"      : line[0].value,
        "priority"   : priority,
        "html_class" : html_class,
        "group"      : line[3].value,
        "text"       : text,
        "url"        : line[5].value,
        "help"       : tip,
        "key"        : lin_id,
        }

def update_link(lin_id, line):
    """Update the attribute of the link from the table content"""
    if lin_id[0].isdigit():
        for link in plugin.links_without_plugins:
            if link.key == lin_id:
                break
        else:
            plugin.add_links(plugin.Link(**link_values(lin_id, line)))
            return
    else:
        p = plugin.get(lin_id)
        if not p:
            return
        link = p.link
        if not link:
            return

    for attr_name, value in link_values(lin_id, line).items():
        if isinstance(getattr(link, attr_name), (tuple, list) ):
            value = ast.literal_eval(value)
        if value:
            setattr(link, attr_name, value)

def onload(table):
    add_new_links_in_the_table(table)
    for lin_id, line in table.lines.items():
        if line[0].value:
            update_link(lin_id, line)

def cell_change(table, page, col, lin_id, value, dummy_date):
    """Update all the link attributes"""
    if page.page_id < 2:
        return
    line = table.lines[lin_id]
    data_col = table.columns.from_id(col).data_col
    # Temporary modify the line to update the link with the new value
    tmp = line[data_col]
    try:
        line[data_col] = cell.CellValue(value)
        update_link(lin_id, line)
    finally:
        line[data_col] = tmp

def content(dummy_table):
    return r"""
function update_student_information(line)
{
   if ( ! t_student_picture.parentNode )
      return ;
   t_student_picture.parentNode.innerHTML = '<div style="font-size:60%;width:20em">' + _("HELP_config_home") + '</div>' ;

   document.getElementById('horizontal_scrollbar').parentNode.style.display = 'none' ;
}

"""
