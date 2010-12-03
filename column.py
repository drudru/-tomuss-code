#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2008-2010 Thierry EXCOFFIER, Universite Claude Bernard
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

###############################################################################

class ColumnAttr(object):
    attrs = {}
    attrs_list = []
    display_table = 0
    update_horizontal_scrollbar = 0
    update_headers = 0
    update_table_headers = 0
    need_authorization = 1
    update_content = False
    formatter = 'function(column, value) { return value ; }'
    empty = 'function(column, value) { return value == "" ; }'
    default_value = '' # XXX Do not put a mutable here or in sub classes
    computed = 0
    
    def __init__(self):
        ColumnAttr.attrs[self.name] = self
        ColumnAttr.attrs_list.append(self)

    def check(self, value):
        """Additionnal value checks"""
        return ''
        
    def encode(self, value):
        return value

    def decode(self, value):
        return value
        
    def set(self, table, page, column, value):
        if table.loading:
            setattr(column, self.name, self.encode(value))
            if self.name != 'comment': # Historical remnent
                column.author = page.user_name
            page.request += 1
            return 'ok.png'
        
        if not table.allow_modification:
            return table.bad_ro(page)
        
        if column == None:
            return table.bad_column(page)

        if not table.authorized_column(page, column):
            return table.bad_auth(page)

        if self.computed and self.name != 'hidden': # XXX Not nice test
            table.error(page, "Attribut de colonne non modifiable:"+self.name)

        if getattr(column.type, 'set_' + self.name) == 'unmodifiable':
            table.error(page, "Attribut de colonne non modifiable:"+self.name)
            
        error = self.check(value)
        if error:
            table.error(page, error)
            raise ValueError(error)

        value = self.encode(value)

        if value == getattr(column, self.name):
            return 'ok.png' # Unchanged value

        setattr(column, self.name, value)
        
        table.log('column_attr(%s,%s,%s,%s)' % (
            repr(self.name), repr(page.page_id), repr(column.the_id),
            repr(self.decode(value))))
        t = '<script>Xcolumn_attr(%s,%s,%s);</script>' % (
            repr(self.name), js(column.the_id), js(self.decode(value)))
        if column.author != page.user_name:
            t += '<script>Xcolumn_attr("author",%s,%s);</script>' % (
                js(column.the_id), js(self.decode(value)))
        table.send_update(page, t + '\n')

        column.author = page.user_name

        if (table.template and hasattr(table.template, 'column_change')):
            table.template.column_change(table, column)

        if self.update_content:
            column.update_content() # To import data (URL in the comment)
            
        return 'ok.png'

    def js(self):
        return (self.name +
                ':{' +
                'display_table:' + str(self.display_table)+
                ',update_horizontal_scrollbar:' + str(self.update_horizontal_scrollbar)+
                ',update_headers:' + str(self.update_headers)+
                ',update_table_headers:' + str(self.update_table_headers)+
                ',need_authorization:' + str(self.need_authorization)+
                ',default_value:' + js(self.default_value)+
                ',formatter:' + self.formatter+
                ',computed:' + str(self.computed)+
                ',empty:' + self.empty+
                '}')


class ColumnType(ColumnAttr):
    name = 'type'
    update_headers = 1
    display_table = 1
    default_value = 'Note'
    def encode(self, value):
        return plugins.types[value]
    def decode(self, value):
        return value.name

class ColumnVisibilityDate(ColumnAttr):
    name = 'visibility_date'
    def check(self, date):
        if date == '':
            return
        mktime = time.mktime(time.strptime(date, '%Y%m%d'))
        if mktime > time.time() + 86400*31:
            return "Date invalide car dans plus d'un mois (%s jours)" % \
                   int((time.mktime(time.strptime(date, '%Y%m%d'))
                        - time.time())/86400)
        if mktime < time.time() - 86400*31:
            return "Date invalide car dans le passé"
    formatter = '''
function(column, value)
{
  if ( value === '' ) return '' ;
  return column.visibility_date.substr(6,2) + '/' +
	 column.visibility_date.substr(4,2) + '/' +
	 column.visibility_date.substr(0,4) ;
}'''

class ColumnFreezed(ColumnAttr):
    name = 'freezed'
    display_table = 1
    def check(self, value):
        if value in ('', 'C', 'F'):
            return ''
        return "Valeur invalide pour 'freezed':" + value

class ColumnTitle(ColumnAttr):
    name = 'title'
    update_table_headers = 1
    # System tables may contains spaces
    # def check(self, value):
    #    if ' ' in value:
    #        return 'Espace interdit dans les titres de colonnes'
    empty = 'function(column, value) { return column.title.substr(0,default_title.length) == default_title ; }'


class ColumnComment(ColumnAttr):
    name = 'comment'
    update_headers = 1
    update_content = True

class ColumnAuthor(ColumnAttr):
    computed = 1
    name = 'author'

class ColumnWidth(ColumnAttr):
    default_value = 4
    name = 'width'
    def encode(self, value):
        return int(value)
    
class ColumnHidden(ColumnAttr):
    computed = 1
    default_value = 0
    name = 'hidden'
    def encode(self, value):
        try:
            return int(value)
        except ValueError:
            return 0
    def check(self, value):
        if value in ('0', '1',0,1):
            return ''
        return "Valeur invalide pour 'hidden':" + repr(value)

class ColumnGreen(ColumnAttr):
    need_authorization = 0
    name = 'green'
    display_table = 1
class ColumnRed(ColumnGreen):
    name = 'red'

class ColumnWeight(ColumnAttr):
    default_value = '1'
    name = 'weight'
    def check(self, value):
        float(value)

class ColumnPosition(ColumnAttr):
    position = 0
    name = 'position'
    def encode(self, value):
        return float(value)

class ColumnTestFilter(ColumnAttr):
    default_value = '!ABINJ'
    name = 'test_filter'

class ColumnMinMax(ColumnAttr):
    default_value = '[0;20]'
    display_table = 1
    name = 'minmax'

class ColumnEmptyIs(ColumnAttr):
    name = 'empty_is'
    update_content = True
    display_table = 1
    
class ColumnColumns(ColumnAttr):
    name = 'columns'
    display_table = 1

ColumnType()
ColumnTitle()
ColumnRed()
ColumnGreen()
ColumnWeight()
ColumnEmptyIs()
ColumnTestFilter()
ColumnWidth()
ColumnHidden()
ColumnFreezed()
ColumnVisibilityDate()
ColumnComment()
ColumnPosition()
ColumnColumns()
ColumnAuthor()
ColumnMinMax()

class TableAttr(ColumnAttr):
    attrs = {}
    formatter = 'function(value) { return value ; }'
    empty = 'function(value) { return value == "" ; }'
    def __init__(self):
        TableAttr.attrs[self.name] = self

    def update(self, table, old_value, new_value):
        """Called when the user make the change, not when loading table"""
        pass
        
    def set(self, table, page, value):
        if table.loading:
            setattr(table, self.name, self.encode(value))
            page.request += 1
            return 'ok.png'
        
        if not table.allow_modification:
            return table.bad_ro(page)

        teachers = table.teachers + table.masters
        if ( (page.user_name not in teachers) and len(teachers) != 0):
            return table.bad_auth(page)

        error = self.check(value)
        if error:
            t = '<script>alert("%s\\nLa modification n\'a pas été enregistrée");</script>\n' % error
            table.send_update(None, t)
            return 'bad.png'

        value = self.encode(value)
        old_value = getattr(table, self.name)

        if value == old_value:
            return 'ok.png' # Unchanged value

        self.update(table, old_value, value) # Side effect of attribute change

        setattr(table, self.name, value)
        
        table.log('table_attr(%s,%s,%s)' % (
            repr(self.name), repr(page.page_id), repr(self.decode(value))))
        t = '<script>Xtable_attr(%s,%s);</script>\n' % (
            repr(self.name), js(self.decode(value)))
        table.send_update(page, t)
            
        return 'ok.png'

class TableModifiable(TableAttr):
    name = 'modifiable'
    default_value = 1
    def encode(self, value):
        return int(value)
    def check(self, value):
        value = int(value)
        if value == 0 or value == 1:
            return
        return "Cet attribut '%s' peut être seulement 0 ou 1" % self.__class__.__name__

class TablePrivate(TableModifiable):

    formatter = r'''
function(value)
{
  if ( (table_attr.masters.length == 0 || ! i_am_the_teacher) && value == 1)
    {
      alert('Vous ne pouvez pas rendre cette table privée car\nvous ne pourriez plus la voir.\nCommencez par vous ajouter comme étant\nun des responsable de cette table') ;
      return ;
    }
  return value ;
}'''

    name = 'private'
    default_value = 0

class TableDates(TableAttr):
    name = 'dates'
    default_value = [0,2000000000]
    formatter = '''
function(value)
{
  if ( value.join )
    {
       first_day = new Date() ;
       first_day.setTime(value[0]*1000) ;

       last_day = new Date() ;
       last_day.setTime(value[1]*1000) ;
       var s = formatte_date(last_day) ;
       
       last_day.setTime(value[1]*1000 + 1000*86400) ;

       return formatte_date(first_day) + ' ' + s ;
    }

  var v = value.replace(/[ ,][ ,]*/g, ' ') ;
  var vs = v.split(' ') ;
  if ( vs.length != 2 )
    {
      alert('Saisir les 2 dates séparées par un espace') ;
      return ;
    }
  var d1 = parse_date(vs[0]).getTime() ;
  var d2 = parse_date(vs[1]).getTime() ;
  if ( isNaN(d1) || isNaN(d2) )
    {
      alert('Une des dates est mal écrite') ;
      return ;
    }
  if ( d1 > d2 )
    {
      alert('La date de début doit être AVANT la date de fin') ;
      return ;
    }
  v = date_to_store(vs[0]).replace(/..$/,'') + ' '
    + date_to_store(vs[1]).replace(/..$/,'') ;
  
  return v ;
}'''
    def encode(self, value):
        if isinstance(value, str):        
            dates = value.split(' ')
            first_day = time.mktime(time.strptime(dates[0], '%d/%m/%Y'))
            last_day = time.mktime(time.strptime(dates[1], '%d/%m/%Y'))
            return [first_day, last_day]
        else:
            return value
        
    def decode(self, value):
        return time.strftime('%d/%m/%Y ',time.localtime(value[0])) + \
               time.strftime('%d/%m/%Y',time.localtime(value[1]))

    def check(self, value):
        value = self.encode(value)
        if value[0] > value[1]:
            return 'La première date doit être avant la deuxième'

class TableMasters(TableAttr):
    name = 'masters'
    default_value = []
    # Side effect to update 'i_am_the_teacher' global variable
    formatter = '''
function(value)
{
if ( value.join )
  {
   teachers = value ;
   value = value.join(' ') ;
  }
else
   teachers = value.split(' ') ;
if ( teachers.length )
    i_am_the_teacher = myindex(teachers, my_identity) != -1 ;
else
    i_am_the_teacher = true ;

return value ;
}'''
    def encode(self, value):
        if isinstance(value, str):
            return re.split(' +', value.strip().lower())
        else:
            return value
    def check(self, value):
        value = self.encode(value)
        if len(value) == 0:
            return
        import inscrits
        for login in value:
            if not inscrits.is_a_teacher(login):
                return "Ce n'est pas un enseignant : " + login
    def update(self, table, old_value, new_value):
        import document
        for login in new_value:
            if login not in old_value:
                document.master_of_update('+', login,
                                          table.year, table.semester, table.ue)
        for login in old_value:
            if login not in new_value:
                document.master_of_update('-', login,
                                          table.year, table.semester, table.ue)

TableModifiable()
TableMasters()
TableDates()
TablePrivate()


import files
files.files['types.js'].append('var column_attributes = {\n' +
                               ',\n'.join(attr.js()
                                        for attr in ColumnAttr.attrs_list
                                        ) +
                               '} ;\n' +
                               'var table_attributes = {\n' +
                               ',\n'.join(attr.js()
                                        for attr in TableAttr.attrs.values()
                                        ) +
                               '} ;\n')


    

###############################################################################

# content, cookies, ticket = fakeuser.connection(url_dir)
# content, cookies, ticket = fakeuser.connection(url_ip, cookies)

cookies = None

def read_url_not_cached(url):
    import urllib2
    try:
        f = urllib2.urlopen(url)
        c = f.read()
        f.close()

        if '<html>' in c.lower():
            try:
                import LOCAL.fakeuser
                global cookies
                c, cookies = LOCAL.fakeuser.connection(url, cookies)[:2]
            except ImportError:
                utilities.send_backtrace('Missing LOCAL.fakeuser.connection')
        
        return c
    except:
        utilities.send_backtrace('IMPORT ' + url)
        return
read_url = utilities.add_a_cache(read_url_not_cached, timeout=5)    


@utilities.add_a_lock
def update_column_content(column, url):
    warn('IMPORT %s' % url)

    url_base = url.split('#')[0]

    if configuration.regtest:
        c = read_url_not_cached(url_base)
    else:
        c = read_url(url_base)
    if c is None:
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

    warn('READ %d LINES IN %s' % (len(c), url))

    try:
        col = int(url.split('#')[1]) - 1
    except (IndexError, ValueError):
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
        for attr in ColumnAttr.attrs.values():
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

    def update_content(self):
        """Fill the column with external content"""

        if 'IMPORT(' not in self.comment:
            return
        
        url = re.sub(r'.*IMPORT\(', '', self.comment)
        url = re.sub(r'\).*', '', url)

        if self.import_url == url:
            return

        self.import_url = url

        if not (url.startswith('http:')
                or url.startswith('https:')
                or url.startswith('ftp:')
                or (url.startswith('file:') and configuration.regtest)
                ):
            return

        utilities.start_new_thread(update_column_content, (self, url))


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

    def update_content(self):
        """Update each column with external content"""
        for column in self.columns:
            column.update_content()

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

        

        


        



