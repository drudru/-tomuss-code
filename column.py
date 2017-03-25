#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2008-2014 Thierry EXCOFFIER, Universite Claude Bernard
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

import os
import re
import time
import json
import math
import collections
from .utilities import js
from . import utilities
from . import configuration
from . import plugins
from . import data
from . import files
from . import sender

class ColumnAttr(object):
    attrs = {}
    
    display_table = 0               # Update the table content on change
    update_horizontal_scrollbar = 0 # Update the horizontal scroolbar
    update_headers = 0              # Update the Cell/Column/Table headers
    update_table_headers = 0        # Update the table headers
    need_authorization = 1          # Authorization needed to modify attribute
    only_masters = 0                # Only the table masters see the attribute
    propagate = 1                   # Change is sent to other browsers
    # String to display to the user
    formatter = 'function(column, value) { return value ; }'
    # Return true if empty
    empty = 'function(column, value) { return value === "" ; }'
    # Verify, clean up the attribute and store special value
    check_and_set = "undefined"
    default_value = ''              # XXX Must not be a mutable value
    computed = 0                    # Is a computed attribute (not modifiable)
    what = 'column'                 # It is a 'column' attribute
    strokable = 1                   # The <A> is strokable if false
    # If 1: the attribute is not removed from screen, it is only shaded
    always_visible = 0
    priority = 0
    gui_display = 'GUI_input'
    action = ''
    css = ''
    javascript = ''
    # name = '' # BREAK ALL DO NOT SET THIS VALUE
    
    def __init__(self):
        self.__class__.attrs[self.name] = self
        try:
            jsf = utilities.read_file(
                os.path.join('ATTRIBUTES',
                             self.__class__.__name__.lower() + '.js'))
            jsf = '*/'.join(jsf.split('*/')[1:]) # remove first comment
        except IOError:
            jsf = self.javascript
        self.js_functions = jsf

    def get_default_value(self, table):
        if hasattr(self.default_value, '__call__'):
            return self.default_value(table)
        else:
            return self.default_value

    def check(self, value):
        """Additionnal value checks"""
        return ''

    def check_error(self, value):
        return '_("ALERT_invalid_value") + %s + "=" + %s' % (
            utilities.js(self.name),  utilities.js(value))
    
    def encode(self, value):
        """Translate the value (string from browser or other) into
        the Python internal coding (not the stored form)"""
        if isinstance(value, bytes):
            raise ValueError("Encoding problem for %s" % value)
        return value

    def decode(self, value):
        """Translate the internal value into a Python/Javascript object
        to be send into the database or into the browser"""
        return value
        
    def set(self, table, page, column, value, date):
        """Set the value of the attribute"""
        if table.loading:
            setattr(column, self.name, self.encode(value))
            setattr(column, self.name + '__mtime', date)
            if self.name != 'comment': # Historical remnent
                column.author = page.user_name
            if self.name == 'columns': # XXX Copy past and not the right place
                column.column_ordered_cache = None
            return 'ok.png'

        if not table.modifiable:
            return table.bad_ro(page)
        
        if column == None:
            return table.bad_column(page)

        if not table.authorized_column(page.user_name, column
                                       ) and self.name != 'width':
            return table.bad_auth(page)

        if self.computed and self.name != 'hidden': # XXX Not nice test
            return table.error(page,
                               utilities._("MSG_column_colattr_unmodifiable")
                               + self.name)
        error = self.check(value)
        if error:
            table.error(page, error)
            raise ValueError(error)

        value = self.encode(value)

        if self.name == 'type':
            if column.type.type_type != 'data' and value.type_type == 'data':
                # give the user the erase access
                for line_id, line in table.lines.items():
                    cell = line[column.data_col]
                    if cell.value and cell.author == data.ro_user:
                        table.cell_change(page, column.the_id, line_id,
                                          cell.value, force_update=True)
                column.type.leave_this_type(table, page, column, value)

        # The "value == ''" is here because in some case Javascript want
        # to create a column by sending an empty title.
        # Even is 'empty' is the default value for the title, it must be saved
        # in order to create the column.
        if value == getattr(column, self.name) and value != '':
            return 'ok.png' # Unchanged value

        if self.name == 'title':
            if table.columns.from_title(value):
                table.error(page,
                            "Two columns with the same title: {}".format(value)
                )
                raise ValueError(error)

        setattr(column, self.name, value)
        setattr(column, self.name + '__mtime', date)
        
        table.log('column_attr(%s,%s,%s,%s,%s)' % (
            repr(self.name), page.page_id, repr(column.the_id),
            repr(self.decode(value)), repr(date)))

        if self.propagate:
            t = '<script>Xcolumn_attr(%s,%s,%s);</script>' % (
                repr(self.name), js(column.the_id), js(self.decode(value)))
            if True: # XXX Should be only done if the column is a new one
                t += '<script>Xcolumn_attr("author",%s,%s);</script>' % (
                    js(column.the_id), js(page.user_name))
            table.send_update(page, t + '\n')

        if column.author != data.ro_user:
            column.author = page.user_name

        if self.name == 'columns':
            column.column_ordered_cache = None

        table.column_changed(column, self)

        return 'ok.png'

    def visible_for(self):
        visible_for = []
        for p in plugins.types.values():
            if self.name in p.attributes_visible:
                visible_for.append(p.name)
        return visible_for

    def js(self):
        """Attribute JavaScript description"""

        return ('"' + self.name + '"' +
                ':{' +
                'display_table:' + str(self.display_table)+
                ',update_horizontal_scrollbar:' + str(self.update_horizontal_scrollbar)+
                ',update_headers:' + str(self.update_headers) +
                ',update_table_headers:' + str(self.update_table_headers) +
                ',need_authorization:' + str(self.need_authorization) +
                ',default_value:' + js(self.get_default_value(None)) +
                ',formatter:' + self.formatter +
                ',computed:' + str(self.computed) +
                ',only_masters:' + str(self.only_masters) +
                ',empty:' + self.empty +
                ',check_and_set:' + self.check_and_set +
                ',visible_for:' + js(self.visible_for()) +
                ',gui_display:' + js(self.gui_display) +
                ',action:' + js(self.action) +
                ',name:' + js(self.name) +
                ',what:' + js(self.what) +
                ',strokable:' + js(self.strokable) +
                ',always_visible:' + js(self.always_visible) +
                '}')

class TableAttr(ColumnAttr):
    attrs = {}
    formatter = 'function(value) { return value ; }'
    empty = 'function(value) { return value === "" ; }'
    what = 'table'                 # It is a 'column' attribute

    def update(self, table, old_value, new_value, page):
        """Called when the user make the change, not when loading table"""
        pass
        
    def set(self, table, page, value, date):
        if table.loading:
            setattr(table, self.name, self.encode(value))
            setattr(table, self.name + '__mtime', date)
            return 'ok.png'

        teachers = table.masters

        if (page.user_name not in teachers
            and page.user_name not in configuration.root
            and page.user_name != data.ro_user
            and (self.name != 'masters'
                 or page.user_name not in table.managers)
            ):

            if not table.modifiable:
                return table.bad_ro(page)

            if len(teachers) != 0:
                return table.bad_auth(page)

            if self.name == 'modifiable':
                return table.bad_auth(page)

        if not table.modifiable and not self.name == 'modifiable':
            return table.bad_ro(page)

        error = self.check(value)
        if error:
            if '_(' not in error:
                error = utilities.js(error)
            t = '<script>alert(%s + "\\n" +%s);</script>\n' % (
                error, utilities.js(utilities._("ALERT_column_not_saved")))
                                                               
            sender.append(page.browser_file, t)
            return 'bad.png'

        value = self.encode(value)
        old_value = getattr(table, self.name)

        if value == old_value:
            return 'ok.png' # Unchanged value

        # Compute side effects of the attribute change
        self.update(table, old_value, value, page)

        setattr(table, self.name, value)
        setattr(table, self.name + '__mtime', date)
        
        table.log('table_attr(%s,%s,%s,%s)' % (
            repr(self.name), page.page_id, repr(self.decode(value)),
            repr(date)))
        t = '<script>Xtable_attr(%s,%s);</script>\n' % (
            repr(self.name), js(self.decode(value)))
        table.send_update(page, t)
            
        return 'ok.png'

attributes = []

def column_attributes():
    for attr in attributes:
        if isinstance(attr, ColumnAttr) and not isinstance(attr, TableAttr):
            yield attr

def table_attributes():
    for attr in attributes:
        if isinstance(attr, TableAttr):
            yield attr

types_using_columns = ()

def initialize():
    global attributes

    attributes = []
    reloadeds = []
    names = set()
    attr_files = [os.path.join('ATTRIBUTES', filename)
                  for filename in os.listdir('ATTRIBUTES')
                  ]
    if not configuration.regtest:        
        local_attr = os.path.join('LOCAL', 'LOCAL_ATTRIBUTES')
        if os.path.isdir(local_attr):
            attr_files += [os.path.join(local_attr, filename)
                           for filename in os.listdir(local_attr)]
    
    for name in attr_files:
        if not name.endswith('.py'):
            continue
        the_module, reloaded = utilities.import_reload(name)
        for key, item in the_module.__dict__.items():
            if hasattr(item, 'name'):
                if key in names:
                    continue
                if key.startswith('__'):
                    continue
                names.add(key)
                attributes.append(item())
                reloadeds.append((item.__name__, reloaded))

    attributes.sort(key=lambda x: (x.priority, x.name))

    files.files['types.js'].append('column.py',
        'var column_attributes = {\n' +
        ',\n'.join(attr.js() for attr in column_attributes() ) + '} ;\n' +
        'var table_attributes = {\n' +
        ',\n'.join(attr.js() for attr in table_attributes() ) + '} ;\n' +
        '\n'.join(attr.js_functions for attr in attributes) +
        '\n')


    css = '\n'.join(set(attr.css for attr in attributes))
    files.files['style.css'].append('column.py', css)

    global types_using_columns
    types_using_columns = set(ColumnAttr.attrs['columns'].visible_for())
    
    return reloadeds

class Column(object):
    """The Column object contains all the informations about the column.
    Once the Column is integrated in a table, it memorizes the table pointer.
    """
    data_col = table = None # To remove pychecker complaint
    
    def __init__(self, col, username, **keys):
        """Create the column with the same defaults than in the column object
        in the javascript side."""
        self.the_id = col
        self.author = username
        # Disable optimization
        # self.import_url = None
        if 'type' in keys:
            self.type = plugins.types[keys['type']]
            del keys['type']
        else:
            self.type = plugins.types[ColumnAttr.attrs['type'].default_value]

        for attr in ColumnAttr.attrs.values():
            if attr.name in ('type', 'author'):
                continue
            setattr(self, attr.name, keys.get(attr.name, attr.default_value))

    def depends_on(self):
        """Return the list of columns used to compute this one"""
        if self.columns and self.type.name in types_using_columns:
            return re.split(' +', self.columns.strip())
        return ()

    def empty(self):
        """Returns True if all the cells in the column are empty."""
        i = self.data_col
        for line in self.table.lines.values():
            if line[i].value:
                return False
        return True

    def empty_of_user_values(self):
        """Returns True if all the cells in the column are empty."""
        i = self.data_col
        for line in self.table.lines.values():
            if not line[i].empty():
                return False
        return True

    def dump(self):
        """'print' all the column information for debugging"""
        print(self.js())
        i = self.data_col
        for line in self.table.lines.values():
            print(line[0].value, line[1].value, line[2].value, line[i].value)

    def min_max(self):
        """From the Note 'test' value stored as [min;red;green;max]
        returns the min and the max as float numbers."""
        if self.type.name == 'Nmbr':
            return 0, max(1, len(self.depends_on()))
        x = self.minmax.strip('[]').split(';')
        v_min, v_max = x[0], x[-1]
        try:
            return float(v_min), float(v_max)
        except ValueError:
            return 0, 20

    def js(self, hide, python=False):
        """Returns the JavaScript describing the column.
        hide=None  : For the table editor if it is a table master
        hide=False : For the table editor
        hide=1     : for a student on the suivi
        hide=True  : for a teacher on the suivi
        """
        d = {}
        for attr in column_attributes():
            value = getattr(self, attr.name)
            if attr.name == 'url_import' and ':' in value and hide is not None:
                continue # private in case of password protected url
            elif attr.name == 'comment':
                if hide:
                    value = re.sub(r'(TITLE|IMPORT|BASE)\([^)]*\)', '', value)
            elif attr.name == 'columns':
                if hide:
                    titles = []
                    for title in self.depends_on():
                        col = self.table.columns.from_title(title)
                        if col and col.visible(hide):
                            titles.append(title)
                    value = ' '.join(titles)
            elif attr.name == 'visibility_date':
                if value == '':
                    # Became visible on the last change
                    value = max(getattr(self, 'visibility_date__mtime',''),
                                getattr(self, 'visibility__mtime', '')
                                )[:8]
            if value != attr.default_value:
                if attr.name == 'type':
                    value = value.name
                d[attr.name] = value
        d['the_id'] = self.the_id
        if python:
            return d
        else:
            return 'Col(' + json.dumps(d) + ')'

    def stat(self, cell, lines, line):
        """Format a cell value in order to display it.
        It uses the formatter defined by the column type."""
        if cell.value != '':
            value = cell.value
        else:
            value = self.empty_is
        d = self.type.stat(self, value, cell, lines)
        if self.groupcolumn:
            names = []
            for line_key, i_line in self.lines_of_the_group(line):
                names.append([i.value for i in i_line[:3]])
            d["group_members"] = names
        return d

    def cell_indicator(self, cell, lines):
        """Compute if the cell value is a good or bad one.
        Returns the HTML class name associated and a value between 0 and 1"""
        if cell.value != '':
            value = cell.value
        else:
            value = self.empty_is
        return self.type.cell_indicator(self, value, cell, lines)

    def nr_cells_not_empty_and_empty(self, lines):
        """Compute the total number of cells and the number of empty cell
        in the column."""        
        data_col = self.data_col
        nr = 0
        nr_empty = 0
        for line in lines:
            if line[data_col].value == '':
                nr_empty += 1
            nr += 1
        return nr, nr_empty
        
    def cell_values(self, lines):
        """Compute the list of cells FLOAT values with the given Grp and Seq"""
        data_col = self.data_col
        def get_floats(the_lines):
            cells = []
            for line in the_lines:
                try:
                    if line[0].value:
                        value = float(line[data_col].value)
                        if not math.isnan(value):
                            cells.append(value)
                except ValueError:
                    continue
            return cells
            
        return get_floats(self.table.lines.values()), get_floats(lines)

    def visible(self, hide):
        """Returns true if the column is visible.
        See 'js' method for explanation about 'hide'
        """
        if not hide:
            return True # For the table
        if hide is True and self.visibility != 2:
            return True # Teacher
        if self.title.startswith('.'):
            return False
        if self.visibility == 3:
            return True
        if self.visibility > 0:
            return False
        if self.visibility_date:
            date = time.strftime('%Y%m%d')
            if self.visibility_date > date:
                return False
        return True

    def is_modifiable(self, teacher, ticket, cell, line):
        """From 'suivi' by student or teacher"""
        return (self.table.modifiable
                # Commented because always modifiable from the table editor
                and (self.modifiable == 2 or teacher)
                and self.table.authorized(ticket.user_name, cell, column=self,
                                          line=line)
                )

    def is_computed(self):
        return self.type.cell_compute != 'undefined'

    def cell_is_modifiable(self):
        return self.type.cell_is_modifiable

    def lines_of_the_group(self, a_line):
        """Return a list of (lin_id, line) for lines in the same group.
        The line in argument is not listed."""
        if not self.groupcolumn:
            return
        col = self.table.columns.from_title(self.groupcolumn)
        if not col:
            return
        data_col = col.data_col
        group = str(a_line[data_col].value)
        if group == '':
            return
        for lin_id, line in self.table.lines.items():
            if line is a_line:
                continue
            if str(line[data_col].value) == group:
                yield lin_id, line

    def get_the_groups(self):
        """Return a dict:   {"group_name": [line,...],...}
        Beware: the empty groupe name is possible
        """
        if not self.groupcolumn:
            return {}
        col = self.table.columns.from_title(self.groupcolumn)
        if not col:
            return {}
        data_col = col.data_col
        d = collections.defaultdict(list)
        for lin_id, line in self.table.lines.items():
            d[str(line[data_col].value)].append(line)
        return d

    def __str__(self):
        return '%s/%s' % (self.table, self.title)

class Columns(object):
    """A set of Column associated to a table.
    The columns are stored in a list, so they have an index.
    They also have an unique 'id' used to communicate with the client
    because the columns are not in the same order in all the clients.
    """
    grp_cache = False
    seq_cache = False
    column_ordered_cache = None
    
    def __init__(self, table):
        """Create an empty set associated to the table."""
        self.table = table
        self.columns = []  # A list to not change the order

    def from_id(self, col):
        """Retrieve the column from its 'id'."""
        for column in self.columns:
            if column.the_id == col:
                return column
        return None

    def from_title(self, title):
        """Retrieve the column from its 'title'."""
        for column in self.columns:
            if column.title == title:
                return column
        return None

    def data_col_from_title(self, title):
        """Retrieve the column from its 'title'."""
        for column in self.columns:
            if column.title == title:
                return column.data_col
        return None

    def __getitem__(self, k):
        """Get the column at the given index."""
        return self.columns[k]

    def use(self, column):
        """Columns using this one."""
        return (col
                for col in self.columns
                if column.title in col.depends_on()
                )

    def get_grp(self):
        """Get the data_col of the column named 'Grp'"""
        if self.grp_cache is False:
            column = self.from_title('Grp')
            if column:
                self.grp_cache = column.data_col
            else:
                self.grp_cache = None
        return self.grp_cache

    def get_seq(self):
        """Get the data_col of the column named 'Seq'"""
        if self.seq_cache is False:
            column = self.from_title('Seq')
            if column:
                self.seq_cache = column.data_col
            else:
                self.seq_cache = None
        return self.seq_cache

    def __setitem__(self, k, v):
        """Set the column at the given index and update some information
        in order to have faster access."""
        self.columns[k] = v
        v.data_col = k
        v.table = self.table

    def append(self, column):
        """Add a new column."""
        self.columns.append(None)
        self[len(self.columns)-1] = column


    def pop(self, k):
        """Remove the column at the given index."""
        self.columns.pop(k)
        for i, v in enumerate(self.columns):
            v.data_col = i

    def __len__(self):
        """Returns the number of columns."""
        return len(self.columns)

    def js(self, hide, python=False):
        """Returns the javaScript code describing all NEEDED columns."""
        columns = [ c
                    for c in self.columns
                    if c.visible(hide)
                ]

        if python:
            return [c.js(hide, python=True)
                    for c in columns]
        else:
            return 'columns = [\n'+',\n'.join([c.js(hide)
                                               for c in columns]) + '\n];'

    def __iter__(self):
        """Iterate over the columns."""
        return self.columns.__iter__()

    def columns_ordered(self):
        """Returns columns with the good computing order for dependencies.
        Beware: the last item can be an unused column."""
        if self.column_ordered_cache:
            return self.column_ordered_cache
        done = []
        while len(done) != len(self.columns):
            for c in self.columns:
                if c in done:
                    continue
                for title in c.depends_on():
                    column = self.table.columns.from_title(title)
                    if column and column not in done:
                        break
                else:
                    done.append(c)
        self.column_ordered_cache = done
        return done
        
    def result_column(self):
        """
        Return the result column if there is one or:
          * False : no column found (bug?)
          * () : no computed result columns
          * 0 : there is a grade not used in the computation of the result
        """
        ordered = self.columns_ordered()
        if not ordered:
            return False
        for may_be_top in ordered[::-1]:
            if may_be_top.is_computed():
                break
        else:
            return ()
        if (may_be_top.type.name == 'Weighted_Percent'
            and ordered[-2].type.name == 'Moy'):
            may_be_top = ordered[-2]
        to_add = [may_be_top.title]
        used_titles = set()
        while to_add:
            title = to_add.pop()
            used_titles.add(title)
            column = self.from_title(title)
            if column:
                to_add += column.depends_on()
            else:
                print('XXX not found:', title)
        for column in self.columns:
            if column.type.name == 'Note' and column.title not in used_titles:
                return 0
        return may_be_top

    def left_to_right(self):
        return sorted(self.columns, key=lambda c: c.position)
