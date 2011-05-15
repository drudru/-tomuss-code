#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2008-2011 Thierry EXCOFFIER, Universite Claude Bernard
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

from utilities import js, warn
import utilities
import configuration
import cgi
import re
import time
import plugins
import hashlib
import data
import os
import files
import sender

class ColumnAttr(object):
    attrs = {}
    
    display_table = 0               # Update the table content on change
    update_horizontal_scrollbar = 0 # Update the horizontal scroolbar
    update_headers = 0              # Update the Cell/Column/Table headers
    update_table_headers = 0        # Update the table headers
    need_authorization = 1          # Authorization needed to modify attribute
    update_content = False          # On change, update column content
    only_masters = 0                # Only the table masters see the attribute
    # String to display to the user
    formatter = 'function(column, value) { return value ; }'
    # Return true if empty
    empty = 'function(column, value) { return value === "" ; }'
    # Verify, clean up the attribute and store special value
    check_and_set = "undefined"
    visible_for = []                # The 'types' needing this attribute
    default_value = ''              # XXX Must not be a mutable value
    computed = 0                    # Is a computed attribute (not modifiable)
    tip = ''                        # Helpful message
    what = 'column'                 # It is a 'column' attribute
    priority = 0
    gui_display = 'GUI_input'
    action = ''
    title = ''
    css = ''
    
    def __init__(self):
        self.__class__.attrs[self.name] = self
        try:
            js = utilities.read_file(
                os.path.join('ATTRIBUTES',
                             self.__class__.__name__.lower() + '.js'))
            js = '*/'.join(js.split('*/')[1:])
        except IOError:
            js = ''
        self.js_functions = js

    def check(self, value):
        """Additionnal value checks"""
        return ''
        
    def encode(self, value):
        """Translate the value (string from browser or other) into
        the Python iternal coding (not stored form)"""
        return value

    def decode(self, value):
        """Translate the internal value into a Python/Javascript object
        to be send into the database or into the browser"""
        return value
        
    def set(self, table, page, column, value):
        """Set the value of the attribute"""
        if table.loading:
            setattr(column, self.name, self.encode(value))
            if self.name != 'comment': # Historical remnent
                column.author = page.user_name
            page.request += 1
            return 'ok.png'
        
        if not table.modifiable:
            return table.bad_ro(page)
        
        if column == None:
            return table.bad_column(page)

        if not table.authorized_column(page, column):
            return table.bad_auth(page)

        if self.computed and self.name != 'hidden': # XXX Not nice test
            return table.error(page,
                               "Attribut de colonne non modifiable:"+self.name)
        # The columns list is not modifiable for a Note
        # But the names in column list must be renamed on column rename.
        # It is so because columns_list value is not forgotten when
        # the type is changed.
        # if getattr(column.type, 'set_' + self.name) == 'unmodifiable':
        #    return table.error(page,
        #                       "Attribut de colonne non modifiable:"+self.name)
            
        error = self.check(value)
        if error:
            table.error(page, error)
            raise ValueError(error)

        value = self.encode(value)

        # The "value == ''" is here because in some case Javascript want
        # to create a column by sending an empty title.
        # Even is 'empty' is the default value for the title, it must be saved
        # in order to create the column.
        if value == getattr(column, self.name) and value == '':
            return 'ok.png' # Unchanged value

        setattr(column, self.name, value)
        
        table.log('column_attr(%s,%s,%s,%s)' % (
            repr(self.name), page.page_id, repr(column.the_id),
            repr(self.decode(value))))
        t = '<script>Xcolumn_attr(%s,%s,%s);</script>' % (
            repr(self.name), js(column.the_id), js(self.decode(value)))
        if column.author != page.user_name:
            t += '<script>Xcolumn_attr("author",%s,%s);</script>' % (
                js(column.the_id), js(page.user_name))
        table.send_update(page, t + '\n')

        column.author = page.user_name
        table.column_changed(column, self)

        return 'ok.png'

    def js(self):
        """Attribute JavaScript description"""
        return (self.name +
                ':{' +
                'display_table:' + str(self.display_table)+
                ',update_horizontal_scrollbar:' + str(self.update_horizontal_scrollbar)+
                ',update_headers:' + str(self.update_headers) +
                ',update_table_headers:' + str(self.update_table_headers) +
                ',need_authorization:' + str(self.need_authorization) +
                ',default_value:' + js(self.default_value) +
                ',formatter:' + self.formatter +
                ',computed:' + str(self.computed) +
                ',only_masters:' + str(self.only_masters) +
                ',empty:' + self.empty +
                ',check_and_set:' + self.check_and_set +
                ',visible_for:' + js(self.visible_for) +
                ',gui_display:' + js(self.gui_display) +
                ',title:' + js(self.title) +
                ',action:' + js(self.action) +
                ',tip:' + js(self.tip) +
                ',name:' + js(self.name) +
                ',what:' + js(self.what) +
                '}')

class TableAttr(ColumnAttr):
    attrs = {}
    formatter = 'function(value) { return value ; }'
    empty = 'function(value) { return value === "" ; }'
    what = 'table'                 # It is a 'column' attribute

    def update(self, table, old_value, new_value, page):
        """Called when the user make the change, not when loading table"""
        pass
        
    def set(self, table, page, value):
        if table.loading:
            setattr(table, self.name, self.encode(value))
            page.request += 1
            return 'ok.png'

        teachers = table.masters

        if (page.user_name not in teachers
            and page.user_name not in configuration.root
            and page.user_name != data.ro_user):

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
            t = '<script>alert("%s\\nLa modification n\'a pas été enregistrée");</script>\n' % error
            sender.append(page.browser_file, t)
            return 'bad.png'

        value = self.encode(value)
        old_value = getattr(table, self.name)

        if value == old_value:
            return 'ok.png' # Unchanged value

        # Compute side effects of the attribute change
        self.update(table, old_value, value, page)

        setattr(table, self.name, value)
        
        table.log('table_attr(%s,%s,%s)' % (
            repr(self.name), page.page_id, repr(self.decode(value))))
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

def initialize():
    global attributes

    attributes = []
    reloadeds = []
    names = set()
    for name in os.listdir('ATTRIBUTES'):
        if not name.endswith('.py'):
            continue
        the_module, reloaded = utilities.import_reload(
            os.path.join('ATTRIBUTES', name))
        for key, item in the_module.__dict__.items():
            if hasattr(item, 'name'):
                if key in names:
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


    css = '\n'.join([attr.css for attr in attributes])
    files.files['style.css'].append('column.py', css)
    
    return reloadeds

initialize()

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
        self.import_url = None
        self.type = plugins.types[ColumnAttr.attrs['type'].default_value]

        for attr in ColumnAttr.attrs.values():
            if attr.name in ('type', 'author'):
                continue
            setattr(self, attr.name, keys.get(attr.name, attr.default_value))

    def depends_on(self):
        """Return the list of columns used to compute this one"""
        if self.columns:
            return re.split(' +', self.columns.strip())
        return ()

    def empty(self):
        """Returns True if all the cells in the column are empty."""
        i = self.data_col
        for line in self.table.lines.values():
            if line[i].value:
                return False
        return True

    def dump(self):
        """'print' all the column information for debugging"""
        print self.js()
        i = self.data_col
        for line in self.table.lines.values():
            print line[0].value, line[1].value, line[2].value, line[i].value

    def min_max(self):
        """From the Note 'test' value stored as [min;red;green;max]
        returns the min and the max as float numbers."""
        x = self.minmax.strip('[]').split(';')
        v_min, v_max = x[0], x[-1]
        try:
            return float(v_min), float(v_max)
        except ValueError:
            return 0, 20

    def js(self, hide, obfuscated={}):
        """Returns the JavaScript describing the column."""
        s = []
        for attr in column_attributes():
            if hide and attr.name == 'comment':
                value = re.sub(r'(TITLE|IMPORT|BASE)\([^)]*\)', '', self.comment)
            else:
                value = getattr(self, attr.name)
            if hide is 1: # see line_compute_js
                if not self.visible():
                    if attr.name == 'comment':
                        value = ''
                    elif attr.name == 'title':
                        value = obfuscated[value]
                    # Type obfuscation is not possible because the
                    # averages can't be computed on javascript side :
                    # elif attr.name == 'type' and value.name == 'Note':
                    #    value = 'Prst'
                if value and attr.name == 'columns':
                    for old, new in obfuscated.items():
                        value = (' ' + value + ' ').replace(
                            ' ' + old + ' ', ' ' + new + ' ')[1:-1]
                
            if value != attr.default_value:
                s.append( attr.name + ':' + js(value) )
                                 
        return 'Col({the_id:%s,%s})' % (js(self.the_id), ','.join(s))

    def cell(self, cell, lines, teacher, ticket, line_id):
        """Format a cell value in order to display it.
        It uses the formatter defined by the column type."""
        if cell.value != '':
            value = cell.value
        else:
            value = self.empty_is
            
        return self.type.formatter(self, value, cell, lines, teacher,
                                   ticket, line_id)

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
        cells = []
        for line in lines:
            try:
                cells.append(float(line[data_col].value))
            except ValueError:
                continue

        all_cells = []
        for line in self.table.lines.values():
            try:
                all_cells.append(float(line[data_col].value))
            except ValueError:
                continue
            
        return all_cells, cells

    def visible(self):
        """Returns true if the column is visible for the student"""
        if self.title.startswith('.'):
            return False
        if self.visibility_date:
            date = time.strftime('%Y%m%d')
            if self.visibility_date > date:
                return False
        return True

class Columns(object):
    """A set of Column associated to a table.
    The columns are stored in a list, so they have an index.
    They also have an unique 'id' used to communicate with the client
    because the columns are not in the same order in all the clients.
    """
    grp_cache = False
    seq_cache = False
    
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

    def js(self, hide):
        """Returns the javaScript code describing all the columns."""
        obfuscated = {}
        if hide is 1:
            for c in self.columns:
                if not c.visible():
                    obfuscated[c.title] = hashlib.md5(c.title).hexdigest()
            
        return 'columns = [\n'+',\n'.join([c.js(hide, obfuscated)
                                           for c in self.columns]) + '\n];'

    def __iter__(self):
        """Iterate over the columns."""
        return self.columns.__iter__()

        

        


        



