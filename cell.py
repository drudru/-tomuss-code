#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2008,2009 Thierry EXCOFFIER, Universite Claude Bernard
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

import utilities
import cgi
import configuration
import time
import data
import inscrits

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
        return Cell(value=value, author=author, date=date)
    
    def js(self):
        """Create the javascript code for an empty cell."""
        return 'C()'

    js_student = js

    def empty(self):
        """Returns True"""
        return True

cellempty = CellEmpty()

class Cell(CellVirtual):
    """Define a cell with the given attributes.
    It also manage the cell history and a cache to minimize
    CPU time to generate the minimal JavaScript code for the cell.
    Attributes of the cell should not be modified directly.
    """

    __slots__ = ('value', 'author', 'date', 'comment', 'history', 'cache')
    
    def __init__(self, value='', author='', date='', comment=''):
        """Create a new cell with some attributes in the list:
        'value', 'author', 'date' and 'comment'.
        The date is formatted as YYYYMMDDHHMMSS.
        """
        self.value = value
        self.author = author
        self.date = date
        self.comment = comment
        self.history = ''
        self.cache = None
        
    def set_comment(self, comment):
        """change the comment on the cell."""
        self.comment = comment
        self.cache = None
        return self

    def set_value(self, value='', author='', date=None):
        """change the value of the cell."""
        if date == None:
            date = time.strftime('%Y%m%d%H%M%S')

        self.history += '%s\n(%s %s),·' % (self.value, self.date, self.author)
        self.value = value
        self.author = author
        self.date = date
        self.cache = None
        return self

    def js(self):
        """Generate the Cell JavaScript object with the minimal code,
        in order to minimize file size."""
        if not self.cache:
            if self.history:
                self.cache = 'C(%s,"%s","%s",%s,%s)' % (
                    js(self.value),
                    self.author,
                    self.date,
                    js(self.comment),
                    js(self.history),
                    )
            elif self.comment:
                self.cache = 'C(%s,"%s","%s",%s)' % (
                    js(self.value), self.author, self.date, js(self.comment))
            elif self.date:
                self.cache = 'C(%s,"%s","%s")' % (
                    js(self.value), self.author, self.date)
            elif self.author:
                self.cache = 'C(%s,"%s")' % (
                    js(self.value), self.author)
            elif self.value:
                self.cache = 'C(%s)' % (
                    js(self.value),
                    )
            else:
                self.cache = 'C()'
            
        return self.cache

    def js_student(self):
        t = self.js()
        if not self.history:
            return t
        return 'C(%s,"%s","%s",%s)' % (
            js(self.value), self.author, self.date, js(self.comment))

    def empty(self):
        """Returns True if the cell is empty"""
        return (self.value == ''
                or self.author == data.ro_user
                or self.author == data.rw_user)



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

    def js(self, for_student=False):
        """Translate the line in JavaScript"""
        if for_student:
            return '[' + ','.join([cell.js_student()
                                   for cell in self.cells]) + ']'
        else:
            return '[' + ','.join([cell.js() for cell in self.cells]) + ']'

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

    def line_compute_js(self, line, for_student=False):
        """Create the JavaScript program that initalizes 'line' with
        all the informations for the student.
        The value computing is done in javascript."""
        s = []
        s.append('<script>')
        if for_student:
            s.append(self.columns.js(hide=1))
        else:
            s.append(self.columns.js(hide=True))
        s.append('line = ' + line.js(for_student) + ';')
        s.append('for(var data_col in columns) { init_column(columns[data_col]); columns[data_col].data_col = data_col ; }')
        s.append('update_columns(line);')
        s.append('</script>\n')
        return '\n'.join(s)

    def line_html(self, table, line, line_id, ticket, link=True):
        """Returns an HTML string displaying all the information in the line.
        This function is used to display the 'suivi'.
        The content is not the same for teacher and students because
        teacher have access to table links and boolean toggle to directly
        modify the tables.
        This function is expensive because the student rank is computed
        for all 'Note' columns.
        """
        more = []
        for login in table.masters:
            firstname, surname, mail = inscrits.L_fast.firstname_and_surname_and_mail(login)
            more.append('<a href="mailto:%s">%s %s</a>' %
                        (mail, firstname.title().encode('utf8'),
                         surname.upper().encode('utf8')))
        if more:
            more = (" <small>(Responsables de l'UE : "
                    + ', '.join(more)
                    + ')</small>')
        else:
            more = ''
        if link:
            s = ['<p class="title">']
            s.append(
                utilities.tipped(table.ue + ' '
                                 + cgi.escape(table.table_title),
                                 'Voir le tableau de note complet',
                                 url='%s/=%s/%d/%s/%s' %
                                 (configuration.server_url,
                                  ticket,
                                  table.year, table.semester,
                                  table.ue)
                                 , classname='title'))
            s.append(
                utilities.tipped(' (*)',
                                 'Afficher seulement la ligne de cet étudiant',
                                 url='%s/=%s/%d/%s/%s/=filters=0:%s=' %
                                 (configuration.server_url,
                                  ticket,
                                  table.year, table.semester,
                                  table.ue, line[0].value)
                                 , classname='title'))
            s.append(more)
        else:
            s = ['<h2 class="title">' + table.ue + ' : ' +
                 cgi.escape(table.table_title) + more + '</h2>']
        if table.comment.strip():
            s.append('<p style="margin-top:0">Petit message : <em>'
                     + cgi.escape(table.comment) + '</em></p>')
        s.append(self.line_compute_js(line,for_student=not link))

        grp = self.get_grp(line)
        seq = self.get_seq(line)
        lines = list(table.lines_of_grp(grp, seq))
        
        # Put cells in column order
        val_col = zip(line.cells, self.columns.columns)
        s.append('<script>display_suivi({')
        ss = []
        empty_line = True
        for cell, column in val_col[3:]:
            if not link:
                # Student display : so the column must be visible
                if not column.visible():
                    continue
            v, classname, comment = column.cell(cell,lines,link,ticket,line_id)
            if empty_line and v and column.title not in('Grp','Seq','Inscrit'):
                empty_line = False
            ss.append('%s: [%s,"%s",%s]' % (js(column.title),
                                    js(v), classname, js(comment)))
        s.append(',\n'.join(ss))
        s.append('});</script>\n') ;

        if empty_line and table.ue_code != table.ue:
            # If the table name ends with -1 -2 -3...
            # we don't display empty lines
            return ''

        return '\n'.join(s) # + 'empty=%s' % empty_line


    def js(self, for_student=False):
        """Create JavaScript generating all the lines data."""
        s = []
        for line_id, line in self.lines.items():
            s.append('P(%s,' % utilities.js(line_id)
                     + line.js(for_student) + ');')
        return '\n'.join(s)

