#!/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2008-2013 Thierry EXCOFFIER, Universite Claude Bernard
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

import cgi
import collections
import re
from .. import utilities
from .. import configuration
from .. import document

###############################################################################
# This part is for column import.
# column import can by done on any column type.
###############################################################################

cookies = None

def read_url_not_cached(url):
    """Read an URL content to import in a column"""
    import urllib2
    try:
        f = urllib2.urlopen(url)
        c = f.read()
        f.close()

        if '<html>' in c.lower():
            try:
                from ..LOCAL import fakeuser
                global cookies
                c, cookies = fakeuser.connection(url, cookies)[:2]
            except ImportError:
                utilities.send_backtrace('Missing fakeuser.connection')
        
        return c
    except:
        utilities.send_backtrace('IMPORT ' + url)
        return
read_url = utilities.add_a_cache(read_url_not_cached, timeout=5)    

def error(column, message, more=None):
    if column.table.loading:
        return
    if more is None:
        more = column.url_import
    column.table.send_update(
        None, "<script>Alert('%s', %s);</script>" %(message,
        utilities.js("\n" + column.title + ' : ' + more)))

getters = {
    ':': lambda x: x.history,
    '?': lambda x: x.date,
    '@': lambda x: x.author,
    '#': lambda x: x.comment,
    }

def get_column_from_a_table(column, table_list):
    values = collections.defaultdict(list)
    try:
        getter = getters[table_list[0]]
    except KeyError:
        getter = lambda x: x.value
    table_list = table_list.lstrip(''.join(getters)).strip()
    
    for url in re.split("  *", table_list):
        splited = url.split('/')
        if len(splited) < 2:
            error(column, 'ALERT_url_import_table', url)
            return
        year, semester, table_name, column_name = ([
                column.table.year, column.table.semester] + splited)[-4:]
        year = int(year)
        semester = utilities.safe(semester)
        table_name = utilities.safe(table_name)
        table = document.table(year, semester, table_name, create=False)
        if not table:
            error(column, 'ALERT_url_import_table', url)
            return
        col = table.columns.from_title(column_name)
        if not col:
            error(column, 'ALERT_url_import_column', url)
            return
        if table.private:
            error(column, 'ALERT_url_import_private', url)
            return
        if col.type.cell_compute != 'undefined':
            error(column, 'ALERT_url_import_computed', url)
            return
        for line in table.lines.values():
            values[line[0].value].append((getter(line[col.data_col]), url))
    for line_id, line in column.table.lines.items():
        new_val = values[line[0].value]
        if len(new_val) == 0:
            new_val = ""
        elif len(new_val) == 1:
            new_val = new_val[0][0]
        else:
            new_val = ' '.join("%s(%s)" % (v, u) for v, u in new_val)
        if line[column.data_col].value != new_val:
            column.table.lock()
            try:
                column.table.cell_change(column.table.pages[0],
                                         column.the_id,
                                         line_id, new_val)
            finally:
                column.table.unlock()

@utilities.add_a_lock
def update_column_content(column, url):
    utilities.warn('IMPORT %s' % url)

    url_base = url.split('#')[0]

    if configuration.regtest:
        c = read_url_not_cached(url_base)
    else:
        c = read_url(url_base)
    if c is None:
        error(column, 'ALERT_url_import_bad')
        return
    for encoding in ('utf8', 'latin1'):
        try:
            c = unicode(c, encoding)
            break
        except:
            pass
    else:
        utilities.send_backtrace('Bad encoding for %s' % url,
                                 exception=False)
        return # Bad encoding

    c = c.encode('utf8').replace('\r','\n').split('\n')

    utilities.warn('READ %d LINES IN %s' % (len(c), url))

    try:
        col = int(url.split('#')[1]) - 1
    except (IndexError, ValueError):
        error(column, 'ALERT_url_import_column')
        return

    if col <= 0:
        return

    import csv
    if '\t' in c[0]:
        delimiter = '\t'
    elif ';' in c[0]:
        delimiter = ';'
    else:
        delimiter = ','
    utilities.warn('DELIMITER IS %s' % delimiter)
    for line in csv.reader(c, delimiter=delimiter):
        if len(line) <= col:
            continue
        for line_id, cells in  column.table.get_items(line[0]):
            new_value = line[col]
            if cells[column.data_col].value != new_value:
                column.table.lock()
                try:
                    column.table.cell_change(column.table.pages[0],
                                           column.the_id,
                                           line_id, new_value)
                finally:
                    column.table.unlock()

###############################################################################
# Text column definition
###############################################################################

class Text(object):

    human_priority = 0 # To define menu order
    
    # Default values
    default_filter = ''

    # Default tips
    tip_column_title = "TIP_column_title"
    tip_filter = "TIP_filter_Text"
    tip_cell = "TIP_cell_Text"

    # The value is a float most of the time
    should_be_a_float = 0

    # check value to be stored in the cell
    cell_test = 'test_nothing'
    # possible completions
    cell_completions = 'test_nothing'
    # What to do on mouse click
    onmousedown = 'cell_select'
    # How to display the cell value
    formatte = 'text_format'
    # What to do on cell double click
    ondoubleclick = 'undefined'
    # How to compute the cell value
    cell_compute = 'undefined'
    # Cell is modifiable ? (a computed cell may be modifiable)
    cell_is_modifiable = 1
    # In which column display the type
    type_type = 'data'

    # The columns attributes that should be displayed for this type
    # DO NOT INDICATES ATTRIBUTES VISIBLE BY ALL THE COLUMN TYPES
    attributes_visible = ('completion', 'repetition', 'url_import')

    def value_range(self, v_min, v_max):
        """Display the range of the possible values"""
        return ''

    def cell_indicator(self, column, value, cell, lines):
        """Return an HTML class name and a value between 0 and 1
        to indicate that the cell is 'good' or 'bad'"""
        return '', None
    
        if column.title == 'Grp':
            return '', None
        return {'A': ('verygood',1),
                'B': ('', 0.5),
                'C': ('bad', 0.3),
                'D': ('verybad', 0)
               }.get(value, ('',None))

    def formatter(self, column, value, cell, lines, teacher, ticket, line_id):
        """HTML Formatter returns a tuple :
             (text, classname, comment)
        'text' is None if the cell should not be displayed.
        """
        if column.is_modifiable(teacher, ticket, cell):
            e = str(value).replace("%","&#37").replace("'", "&#39;"). \
                replace('"', '&#34;')

            v = '<input class="hidden" onkeypress="if ( the_event(event).keyCode == 13 ) _cell(this,\'%s/=%s/%d/%s/%s/cell/%s/%s\',\'%s\', \'%s\');" value="%s">' % (
                configuration.server_url,
                ticket.ticket,
                column.table.year, column.table.semester,
                column.table.ue, column.the_id, line_id,
                column.type.name, column.minmax, e)
            return (v, '', '')

        if value == '':
            return ('', '', '')

        return (cgi.escape(str(value)).replace('\n','<br>'),
                self.cell_indicator(column, value, cell, lines)[0],
                '')

    def _values(self): # _ to hide it a little
        t = []
        for i in self.keys:
            try:
                t.append(str(getattr(self,i)))
            except KeyError:
                pass
        return t

    def __str__(self):
        return '"' + self.name + '"'

    def test_ok(self, test):
        return True
    
    def attribute_js_value(self, k):
        if k.startswith('set_') or k in (
            'cell_test', 'cell_completions','onmousedown', 'formatte',
            'ondoubleclick', 'cell_compute'):
            return getattr(self, k)
        else:
            return utilities.js(getattr(self, k))

    def update_one(self, the_table, line_id, column):
        """Do some server side compute on the cell.
        This function is used when the user input interactivly one cell.
        """
        pass

    def update_all(self, the_table, column, attr=None):
        """Do some server side compute on the cell.
        This function update the full column content for every line.
        It is called :
           * on page load to check changs.
           * when the 'attr' column attribute is changed.
           * when a column used by this one changed
        """
        if (attr is not None
            and attr.name != 'comment'
            and attr.name != 'url_import'):
            return

        if 'IMPORT(' in column.comment:
            url = re.sub(r'.*IMPORT\(', '', column.comment)
            url = re.sub(r'\).*', '', url)
        elif column.url_import:
            url = column.url_import
        else:
            return
        
        # Reload even if the value is the same
        # if column.import_url == url:
        #    return
        # column.import_url = url

        if ':' not in url:
            get_column_from_a_table(column, url)
            return

        if not (url.startswith('http:')
                or url.startswith('https:')
                or url.startswith('ftp:')
                or (url.startswith('file:') and configuration.regtest)
                ):
            return

        update_column_content(column, url)

Text.keys = sorted([i for i in Text.__dict__ if not i.startswith('_')])
