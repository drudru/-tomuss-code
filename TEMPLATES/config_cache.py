#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2013 Thierry EXCOFFIER, Universite Claude Bernard
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

"""
The title and help is translated if it is found in the translations files.
"""

from .. import data
from .. import utilities
from .. import configuration

columns = {
    '0': {'type': 'Text', 'freezed': 'F', "width": 10,
          'title': utilities._("TH_cache_name"),
          },
    '1': {'type': 'Text', 'freezed': 'F', "width": 10,
          'title': utilities._("TH_cache_what"),
          },
    '2': {'type': 'Text', 'freezed': 'F',
          'title': utilities._("TH_cache_maxage"),
          "width": 2
          },
    }

def create(table):
    utilities.warn('Creation')
    if table.year != 0 or table.semester != 'Dossiers':
        raise ValueError('Not allowed')
    ro = table.get_ro_page()
    table.get_a_root_page()
    table.table_attr(ro, 'masters', list(configuration.root))
    table.table_attr(ro, 'default_nr_columns', 3)
    table.table_attr(ro, 'default_sort_column', [0,1])
    table.table_attr(ro, 'table_title',
                     utilities._('LINK_/0/Dossiers/config_cache'))
    table.update_columns(columns, ro)

def get_lin_id(cache):
    return cache.fct.__module__.split('.',1)[1] + '.' + cache.fct.func_name
    
def add_new_links_in_the_table(table):
    """Create missing lines in the table"""
    ro = table.pages[0]
    rw = table.pages[1]
    table.lock()
    try:
        for cache in utilities.caches:
            lin_id = get_lin_id(cache)
            if lin_id in table.lines:
                continue
            table.cell_change(ro, '0', lin_id, lin_id)
            table.cell_change(rw, '1', lin_id, cache.__doc__ or '???')
            table.cell_change(rw, '2', lin_id, cache.timeout)
    finally:
        table.unlock()

def onload(table):
    add_new_links_in_the_table(table)
    for cache in utilities.caches:
        lin_id = get_lin_id(cache)
        if lin_id not in table.lines:
            continue
        cache.timeout = int(table.lines[lin_id][2].value)

def cell_change(dummy_table, page, col, lin_id, value, dummy_date):
    """Update all the link attributes"""
    if page.page_id < 2:
        return
    if col != "2":
        return
    for cache in utilities.caches:
        if lin_id == get_lin_id(cache):
            try:
                cache.timeout = int(value)
            except ValueError:
                from .. import sender
                sender.append(page.browser_file,
                              '<script>Alert("ALERT_int_required");</script>')
                utilities.send_backtrace('value=%s' % value, 'config_cache')
                raise
            break

def content(dummy_table):
    return r"""
function update_student_information(line)
{
   if ( ! t_student_picture.parentNode )
      return ;
   t_student_picture.parentNode.innerHTML = '<div style="font-size:60%;width:20em">' + _("HELP_config_cache") + '</div>' ;

   document.getElementById('horizontal_scrollbar').parentNode.style.display = 'none' ;
}

"""
