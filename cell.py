#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2008-2012 Thierry EXCOFFIER, Universite Claude Bernard
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

# WARNING : Assume the table is locked, all this is not thread safe

import time
from . import utilities
from . import data

js = utilities.js

class CellVirtual(object):
    """The <b>set_</b> methods in cells returns a new object if needed.
    It is because an CellEmpty can become a Cell.
    """

    pass

class CellEmpty(CellVirtual):
    """Define an empty cell. It is only to use less memory than a Cell"""
    
    value = ''
    author = ''
    date = ''
    comment = ''
    history = ''
    
    __slots__ = ()
    
    def set_comment(self, comment):
        """Create a non empty cell with the comment and returns it."""
        return Cell(comment=comment)
    
    def set_value(self, value='', author='', date=None):
        """Create a non empty cell with the value and returns it."""
        if date == None:
            date = time.strftime('%Y%m%d%H%M%S')
        return CellValue(value=value, author=author, date=date)
    
    def js(self):
        """Create the javascript code for an empty cell."""
        return 'C()'

    js_student = js

    def json(self):
        return ()

    def empty(self):
        """Returns True"""
        return True

    def copy(self):
        return self

    def date_seconds(self):
        return 0

    def previous_value(self):
        return ''

cellempty = CellEmpty()

class CellValue(CellVirtual):
    """Define a cell without history nor comment
    It is the most used cell content
    """
    
    __slots__ = ('value', 'author', 'date')
    comment = ''
    history = ''

    def __init__(self, value='', author='', date=''):
        self.value = value
        self.author = author
        self.date = date

    def empty(self):
        """Returns True if the cell is empty of user value"""
        return (self.value == ''
                or self.author == data.ro_user
                or self.author == data.rw_user
                or self.author == data.no_user)
    
    def set_comment(self, comment):
        """change the comment on the cell."""
        return Cell(self.value, self.author, self.date, comment)

    def copy(self):
        return CellValue(self.value, self.author, self.date)

    def set_value(self, value='', author='', date=None):
        c = Cell(self.value, self.author, self.date)
        c.set_value(value, author, date)
        return c

    def previous_value(self):
        return ''

    def js(self):
        """Generate the Cell JavaScript object with the minimal code,
        in order to minimize file size."""
        if self.date:
            return 'C(%s,"%s","%s")' % (js(self.value),self.author,self.date)
        elif self.author:
            return 'C(%s,"%s")' % (js(self.value), self.author)
        elif self.value:
            return 'C(%s)' % js(self.value)
        else:
            return 'C()'

    def json(self):
        """Generate the Cell JavaScript object with the minimal code,
        in order to minimize file size."""
        if self.date:
            return (self.value, self.author, self.date)
        elif self.author:
            return (self.value, self.author)
        elif self.value:
            return (self.value,)
        else:
            return ()

    js_student = js

    def date_seconds(self):
        if self.date:
            return time.mktime(time.strptime(self.date, '%Y%m%d%H%M%S'))
        else:
            return 0



class Cell(CellValue):
    """Define a cell with the given attributes.
    It also manage the cell history and a cache to minimize
    CPU time to generate the minimal JavaScript code for the cell.
    Attributes of the cell should not be modified directly.
    """

    __slots__ = ('value', 'author', 'date', 'comment', 'history')
    
    def __init__(self, value='', author='', date='', comment='', history=''):
        """Create a new cell with some attributes in the list:
        'value', 'author', 'date' and 'comment'.
        The date is formatted as YYYYMMDDHHMMSS.
        """
        self.value = value
        self.author = author
        self.date = date
        self.comment = comment
        self.history = history
        
    def set_comment(self, comment):
        """change the comment on the cell."""
        self.comment = comment
        return self

    def copy(self):
        return Cell(self.value, self.author, self.date, self.comment,
                    self.history)

    def set_value(self, value='', author='', date=None):
        """change the value of the cell."""
        if date == None:
            date = time.strftime('%Y%m%d%H%M%S')

        self.history += '%s\n(%s %s),·' % (self.value, self.date, self.author)
        self.value = value
        self.author = author
        self.date = date
        return self

    def previous_value(self):
        if self.history:
            return self.history.split('·')[-2].split('\n')[-2]
        return ''

    def js(self):
        """Generate the Cell JavaScript object with the minimal code,
        in order to minimize file size."""
        if self.history:
            return 'C(%s,"%s","%s",%s,%s)' % (
                js(self.value),
                self.author,
                self.date,
                js(self.comment),
                js(self.history),
                )
        elif self.comment:
            return 'C(%s,"%s","%s",%s)' % (
                js(self.value), self.author, self.date, js(self.comment))
        elif self.date:
            return 'C(%s,"%s","%s")' % (
                js(self.value), self.author, self.date)
        elif self.author:
            return 'C(%s,"%s")' % (
                js(self.value), self.author)
        elif self.value:
            return 'C(%s)' % (
                js(self.value),
                )
        else:
            return 'C()'

    def json(self):
        """Generate the Cell JavaScript object with the minimal code,
        in order to minimize file size."""
        if self.history:
            return (self.value, self.author, self.date, self.comment,
                    self.history)
        elif self.comment:
            return (self.value, self.author, self.date, self.comment)
        elif self.date:
            return (self.value, self.author, self.date)
        elif self.author:
            return (self.value, self.author)
        elif self.value:
            return (self.value, )
        else:
            return ()

    def js_student(self):
        t = self.js()
        if not self.history:
            return t
        return 'C(%s,"%s","%s",%s)' % (
            js(self.value), self.author, self.date, js(self.comment))

C = Cell # To be compatible with PythonJS translated javascript


class Line(object):
    """The Line object is usable as a Python list."""
    def __init__(self, cells):
        """Create the Line from a Cell list."""
        self.cells = cells

    def __getitem__(self, k):
        """Take a Cell in the line."""
        return self.cells[k]

    def __setitem__(self, k, v):
        """Replace a Cell in the line."""
        self.cells[k] = v

    def pop(self, k):
        """Remove the selected cell from the line."""
        self.cells.pop(k)

    def append(self, v):
        """Add a new cell in the line."""
        self.cells.append(v)

    def __len__(self):
        """The the number of cell in the line."""
        return len(self.cells)

    def js(self):
        """Translate the line in JavaScript."""
        return '[' + ','.join([cell.js() for cell in self.cells]) + ']'

    def json(self, for_student=False, columns=None):
        """Translate the line in JavaScript"""
        if for_student:
            return [cell.json()[:4] # Hide history
                    for cell, col in zip(self.cells, columns)
                    if col.visible(hide=1)
                    ]
        else:
            return [cell.json()
                    for cell, col in zip(self.cells, columns)
                    if col.visible(hide=True)
                    ]

class Lines(object):
    """The Lines object is usable as a Python list of Line.
    But as it knows the columns it performs some high level functions.
    It is a dictionnary of lines, the key is the line_id.
    """
    
    def __init__(self, columns):
        """Create an empty set of lines for the given columns"""
        self.lines = {}
        self.columns = columns

    def __iter__(self):
        """Iterate over all the lines."""
        return self.lines.__iter__()

    def items(self):
        """Iterate on the line to get the pair: (line_id, line)."""
        return self.lines.items()

    def keys(self):
        """Iterate on the line to get the line keys: line_id."""
        return self.lines.keys()

    def values(self):
        """Iterate on the line to get the line values."""
        return self.lines.values()

    def __getitem__(self, line):
        """Access to a non existent Line create a new line
        with the good number of empty cells."""
        if line not in self.lines:
            self.lines[line] = Line( [cellempty] * len(self.columns) )
        return self.lines[line]

    def __contains__(self, k):
        """Returns True if the line_id is known."""
        return k in self.lines

    def __len__(self):
        """Returns the number of lines."""
        return len(self.lines)


    def get_grp(self, line):
        """Get the 'Grp' value for the student"""
        grp = self.columns.get_grp()
        if grp is None:
            return None
        else:
            return line[grp].value

    def get_seq(self, line):
        """Get the 'Seq' value for the student"""
        seq = self.columns.get_seq()
        if seq is None:
            return None
        else:
            return line[seq].value

    def line_indicator(self, line, what):
        """Returns a list of (date, cell_indicator)
        for the column type given. It is used to compute icons."""
        s = []
        grp = self.get_grp(line)
        seq = self.get_seq(line)
        lines = list(self.columns.table.lines_of_grp(grp, seq))
        for value, column in zip(line, self.columns.columns)[6:]:
            if column.type.name == what or (what=='Note' and column.type.name == 'Text'):
               c = column.cell_indicator(value, lines)[1]
               if c != None:
                    s.append((value.date, c))                        
        return s

    def line_stat(self, table, line, link):
        """Returns an HTML string displaying all the information in the line.
        This function is used to display the 'suivi'.
        The content is not the same for teacher and students because
        teacher have access to table links and boolean toggle to directly
        modify the tables.
        This function is expensive because the student rank is computed
        for all 'Note' columns.
        """
        grp = self.get_grp(line)
        seq = self.get_seq(line)
        lines = list(table.lines_of_grp(grp, seq))
        
        # Put cells in column order
        val_col = zip(line.cells, self.columns.columns)
        d = {}
        for cell, column in val_col[3:]:
            if not column.visible(hide = link and True or 1):
                continue
            s = column.stat(cell, lines)
            if s:
                d[column.the_id] = column.stat(cell, lines)

        # XXX
        # if empty_line and table.ue_code != table.ue:
        #     # If the table name ends with -1 -2 -3...
        #     # we don't display empty lines
        #     return {}

        return d

    def js(self):
        """Create JavaScript generating all the lines data."""
        s = []
        for line_id, line in self.lines.items():
            s.append('P(%s,' % utilities.js(line_id)
                     + line.js() + ');')
        return s

