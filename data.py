#!/usr/bin/env python3

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

# 'table' global variable is setted from 'document.Table'

import threading

lock = threading.Lock() # Don't allow 2 page loading at same time

ro_user = '*' # The data entered by this user are unmodifiable
rw_user = ''  # The data entered by this user are modifiable by anybody
no_user = '?' # A non existent user (data modifiable only by the table master)

_table = None

def begin(table):
    """Start the importation of a table (set lock)"""
    lock.acquire()
    global _table
    _table = table
    table.loading = True

def end():
    """Stop the importation of a table (release lock)"""
    global _table
    assert(_table.loading == True)
    _table.loading = False
    _table = None
    lock.release()

def new_page(ticket, user_name, user_ip, user_browser, date=None):
    """Create a new page in the table, the identifier of page (page_id)
    is an integer starting from 0."""
    _table.new_page(ticket, user_name, user_ip, user_browser, date)

def column_delete(page_id, col):
    """Delete the column if it is empty."""
    _table.column_delete(_table.pages[page_id], col)

def cell_change(page_id, col, lin, value, date):
    """Change the value of a cell."""
    _table.cell_change(_table.pages[page_id], col, lin, value, date)

def comment_change(page_id, col, lin, value):
    """Change the comment on a cell."""
    _table.comment_change(_table.pages[page_id], col, lin, value)

def table_attr(attr, page_id, value, date=''):
    """Set a table attribute"""
    from . import column
    attr = column.TableAttr.attrs[attr]
    page = _table.pages[page_id]
    attr.set(_table, page, value, date)

def column_attr(attr, page_id, col_id, value, date=''):
    """Set a column attribute"""
    from . import column
    attr = column.ColumnAttr.attrs[attr]
    col = _table.columns.from_id(col_id)
    page = _table.pages[page_id]
    if col is None:
        col = _table.add_empty_column(page, col_id)

    attr.set(_table, page, col, value, date)

# DEPRECATED !!!!!!!!!
# The following function are only used to load table created
# with old TOMUSS version

def column_empty_is(page_id, col, empty_is):
    """DEPRECATED: Change the column empty_is value."""
    column_attr('empty_is', page_id, col, empty_is)

def column_visibility_date(page_id, col, date):
    """DEPRECATED: Specify the date of visibility"""
    column_attr('visibility_date', page_id, col, date)

def column_comment(page_id, col, comment):
    """DEPRECATED: Change the column comment."""
    column_attr('comment', page_id, col, comment)

def column_position(page_id, col, position):
    """DEPRECATED: Define the column position (the columns are sorted by position."""
    column_attr('position', page_id, col, position)

def column_change(page_id, col, title, ttype, test, weight, freezed,
                  hidden, width):
    """DEPRECATED: Change some attributes of the column."""
    _table.column_change(_table.pages[page_id],
                         col, title, ttype, test, weight, freezed,
                         hidden, width)

def add_master(name, page_id=None):
    """DEPRECATED: Add or remove a master on the page."""
    _table.add_master(name, page_id)

def date_change(page_id, dates):
    """DEPRECATED: Change the table dates."""
    _table.date_change(_table.pages[page_id], dates)

def private_toggle(page_id):
    """DEPRECATED: Change the privacy state of the table."""
    _table.private_toggle(_table.pages[page_id])

def table_comment(page_id, comment):
    """DEPRECATED: Change the table comment."""
    _table.table_comment(_table.pages[page_id], comment)

def default_nr_columns(nr):
    """DEPRECATED: Specify the default number of columns displayed on screen."""
    _table.default_nr_columns_change(nr)
