#!/bin/env python
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


import utilities
import configuration
import data
import os
import time
import threading
import teacher
from files import files
import socket
import inscrits
import column
from cell import Cell, Lines, cellempty
import sender
import plugins
import re

def check_table(t):
    cols = tuple(t.lines.lines.values())
    if cols:
        nr_cols = len(tuple(t.lines.lines.values())[0])
    else:
        return # can't check because there is no lines...
    warn('%s, %s, %s' % (t.ue, len(t.columns), nr_cols))
    if len(t.columns) != nr_cols:
        raise ValueError('bad table')

def date_time(date):
    if date is None:
        return '19700101010101'
    else:
        return time.strptime(date, '%Y%m%d%H%M%S')


warn = utilities.warn

tables = {}

the_head   = utilities.StaticFile(os.path.join('FILES','head.html'))

js = utilities.js

canceled_loads = []

# Key : student_id, give the tables ue name
# Used only in 'suivi' because it does not contain year/semester
tables_of_student = {}

class Page(object):
    def __init__(self, ticket, user_name, page_id, ttable,
                 user_ip, user_browser, date=None):
        self.ticket = ticket
        self.user_name = user_name
        self.page_id = page_id
        self.table = ttable
        self.request = 0
        self.browser_file = None
        self.user_ip = user_ip
        self.user_browser = user_browser
        self.date = date

    def check_identity(self, ticket, user_name, user_ip, user_browser):
        # Allow IP change with the same identity
        if (ticket == self.ticket
            and user_name == self.user_name
            and user_browser == self.user_browser):
            return
        warn('received ticket=%s user_name=%s user_browser=%s ip=%s' % (
            ticket, user_name, user_browser, user_ip), what="Info")
        warn('current  ticket=%s user_name=%s user_browser=%s ip=%s' % (
            self.ticket, self.user_name, self.user_browser, self.user_ip),
             what="Info")
        raise ValueError('Cheater')

    def add_request(self, request, action, path, output_file):
        request_list.append((request, self, action, path, output_file))

    def __str__(self):
        return '%s[%s]:%s(%s)' % (self.table, self.page_id, self.user_name,
                                  self.date)

    def date_time(self):
        return date_time(self.date)
    def day(self):
        return self.date[6:8] + '/' + self.date[4:6] + '/' + self.date[:4]

    def backtrace_html(self):
        import cgi
        return (cgi.escape(str(self)) + '<br>'
               + cgi.escape(self.user_browser) + '<br>'
                + self.user_ip)


def table_filename(year, semester, ue):
    return os.path.join(configuration.db, 'Y'+str(year), 'S'+semester, ue + '.py')

def get_preferences(user_name, create_pref=True):
    my_identity2 = utilities.login_to_module(user_name)
    prefs_table = table(0, 'Preferences', my_identity2, None, None,
                        create=create_pref)
    if prefs_table is None:
        return {}
    else:
        return prefs_table.template.preferences(prefs_table)

#REDEFINE
# This function returns javascript code to be included
# in the header of the 'ue' table
def table_head_more(ue):
    return ''

def table_head(year=None, semester=None, ticket=None,
               user_name='', page_id=-1, ue='',
               create_pref=True,
               attrs_from=0):
    s = configuration.suivi.url(year, semester, ticket)
    prefs_table = get_preferences(user_name, create_pref)
    try:
        background = configuration.semesters_color[configuration.semesters.index(semester)]
        background = '<style>BODY, TABLE INPUT, #current_input, BODY TABLE.colored TD { background-color: ' + background + '}</style>'
    except ValueError:
        background = ''

    my_identity2 = utilities.login_to_module(user_name)

    return (str(the_head) + background +
            '<script>' +
            'page_id = "%d" ;\n' % page_id +
            'my_identity = %s ;\n' % repr(user_name) +
            'my_identity2 = %s ;\n' % repr(my_identity2) +
            'url = %s ;\n' % js(utilities.StaticFile._url_) +
            'year = "%s" ;\n' % year +
            'semester = "%s" ;\n' % semester +
            'ticket = "%s" ;\n' % ticket +
            'ue = "%s" ;\n' % ue +
            'suivi = %s ;\n' % js(s) +
            'version = "%s" ;\n' % configuration.version +
            'root = %s ;\n' % js(list(configuration.root)) +
            'cas_url = %s ;\n' % repr(configuration.cas) +
            'preferences = %s ;\n' % prefs_table +
            'lines = {};\n' +
            'columns = [];\n' +
            'lines_to_load = 0 ;\n' +
            'ticket_time_to_live = %d ;\n' % configuration.ticket_time_to_live+
            'check_down_connections_interval = %d ;\n' % configuration.check_down_connections_interval +
            'table_attr = {\n' +
                ',\n'.join(attr.name+':'+js(getattr(attrs_from, attr.name,
                                                    attr.default_value))
                           for attr in column.TableAttr.attrs.values()
                           ) + '} ;\n' +
            table_head_more(ue) +
            '</script>\n')

def import_template(names):
    for name in names:
        if configuration.regtest and name[0] == 'LOCAL':
            continue
        filename = os.path.join(*name) + '.py'
        if os.path.exists(filename):
            return utilities.import_reload(filename)[0]
    return None

class Table(object):
    def __init__(self, year, semester, ue, ro=True, user=None):

        warn('%s/%s/%s ro=%s user=%s' % (year, semester, ue, ro, user),
             what="table")
        self.year = year
        self.semester = semester
        self.ue = ue
        self.loading = False # The table is not being loaded

        if self.ue == 'abj' or self.ue == 'data':
            # Break the import in the file
            raise ValueError("Invalid table name: '%s'" % self.ue)

        # Remove -1 -2 -3 at the end of the UE name
        if len(ue) > 4 and ue[-1].isdigit() and ue[-2] == '-':
            self.ue_code = ue[:-2]
        else:
            self.ue_code = ue

        for attr in column.TableAttr.attrs.values():
            d = attr.default_value
            if isinstance(d, list):
                d = list(d)
            elif isinstance(d, dict):
                d = dict(d)
            setattr(self, attr.name, d)

        x = teacher.all_ues().get(self.ue_code.split('-')[-1], None)
        if x:
            self.table_title = x.intitule().title().encode('utf-8')
            self.code = x.code()
            self.teachers = list(x.responsables_login())
        else:
            self.teachers = []
        self.pages = []
        self.active_pages = []
        self.columns = column.Columns(self)
        self.lines = Lines(self.columns)
        self.the_lock = threading.Lock()
        self.ro = ro
        self.mtime = 0
        self.the_key_dict = {}
        self.unloaded = False
        self.do_not_unload = 0
        self.modifiable = int(not ro)
        dirname = os.path.join(configuration.db,
                               'Y'+str(self.year), 'S'+self.semester)
        self.filename = os.path.join(dirname, ue + '.py')
        self.is_extended = os.path.islink(self.filename)

        self.template = import_template((
            ('LOCAL', 'LOCAL_TEMPLATES', self.ue_code),
            ('TEMPLATES', self.ue_code),
            ('LOCAL', 'LOCAL_TEMPLATES', self.semester),
            ('TEMPLATES', self.semester),
            ))
        if self.template is None:            
            class TT:
                def create(self, ttable):
                    ttable.new_page('', data.ro_user, '', '')
                    ttable.table_attr(ttable.pages[0],'masters',[ttable.user])

            self.template = TT()

        if hasattr(self.template, 'init'):
            self.template.init(self)

        warn('allow modification:' + str(self.modifiable),what='table')
        created = False
        if self.modifiable:
            utilities.mkpath_safe(dirname)
            if not os.path.exists(self.filename):
                s = ['# -*- coding: utf8 -*- ']
                s.append('from data import *')
                s = '\n'.join(s) + '\n'
                utilities.mkpath_safe(dirname)
                utilities.append_file_safe(self.filename, s)
                created = True

        # Remove final .py
        self.module = self.filename[:-3].replace(os.path.sep,'.')

        if not os.path.exists(self.filename):
            # Read only table and file does not exists
            return

        self.mtime = os.path.getmtime(self.filename)

        if not created:
            data.begin(self)
            try:
                __import__(self.module)
                utilities.unload_module(self.module)
            finally:
                data.end()

            if self.template and hasattr(self.template, 'onload'):
                self.template.onload(self)
        else:
            # Remove this file because it is created the same second
            # than the .py file, So it is not recompiled in some case.
            # os.remove(self.filename + 'c')
            warn('Create start', what='table')
            self.user = user
            # We lock because table change methods expects to be locked.
            # But this lock does not protect anything
            self.lock()
            try:
                self.template.create(self)
            finally:
                self.unlock()
                warn('Unlock', what='table')
            warn('Create end', what='table')
            self.pages[0].request = 1 # Not an empty page, it's for the stats

        if not ro:
            # Check mails or new students
            # Only mail if allow_modification is False
            warn('Update student list', what='table')
            update_students.append(self)

        if ro and self.official_ue:
            # Student are never removed, but it is not important
            for login in self.the_keys():
                if login in tables_of_student:
                    if self.ue not in tables_of_student[login]:
                        tables_of_student[login].append(self.ue)
                else:
                    tables_of_student[login] = [self.ue]

        if self.is_extended:
            # To forbid the edit of the same table with 2 names
            self.modifiable = 0

        if len(self.masters) == 0:
            for login in self.teachers:
                if login not in self.masters:
                    self.masters.append(login.encode('utf8'))

    def update(self):
        """Update the table if the file on disc changed."""
        # warn('Start ro=%s dt=%f p=%s' % (self.ro, time.time() - self.mtime, os.path.exists(self.filename)), what="table")
        if not self.ro:
            return self

        if time.time() - self.mtime < configuration.maximum_out_of_date:
            return self

        if not os.path.exists(self.filename):
            return self

        if os.path.getmtime(self.filename) <= self.mtime:
            return self

        warn('%s time=%s mtime=%s' % (self.ue, time.time(), self.mtime),
             what="table")

        return tables_manage("replace", self.year, self.semester, self.ue,
                             new_table = Table(self.year, self.semester,
                                               self.ue, ro=True))


    def change_mails(self, mails):
        return self.table_attr_computed('mails', mails)
    def change_portails(self, portails):
        return self.table_attr_computed('portails', portails)

    def table_attr_computed(self, attr, value):
        setattr(self, attr, value)
        t = '<script>Xtable_attr(%s,%s);</script>\n' % (repr(attr), js(value))
        self.send_update(None, t)

    def update_mail(self, login, mail):
        warn('update mail of ' + self.location(), what="table")
        self.mails[login] = mail
        self.send_update(None,
                         ('<script>update_mail(' + repr(login)
                         + ',' + js(mail) + ');</script>\n').encode('utf-8')
                         )

    def update_portail(self, login, portail): 
        self.portails[login] = portail
        self.send_update(None,
                         ('<script>update_portail(' + repr(login)
                         + ',' + js(portail) + ');</script>\n').encode('utf-8')
                         )
        
    def lock(self):
        warn('start', what='debug')
        sender.send_live_status('<script>b("%d/%s/%s");</script>\n' %
                                (self.year, self.semester, self.ue))
        self.the_lock.acquire()
        warn('acquired', what='debug')

    def unlock(self):
        warn('start', what='debug')
        self.the_lock.release()
        sender.send_live_status('<script>r("%d/%s/%s");</script>\n' %
                                (self.year, self.semester, self.ue))

    def panic(self, txt):
        utilities.send_backtrace('UE: %s ' % self.ue + txt,
                                 exception=False)
        self.send_update(None, "<script>window.close();</script>\n")
        raise ValueError('PANIC')

    def state_is_fine(self):
        if self.unloaded:
            self.panic('Modification on an unloaded table')
        if not self.the_lock.locked():
            self.panic('Modification on an unlocked table')
        if self.is_extended:
            self.panic('Modification on an extended table')
        if configuration.read_only:
            self.panic('Modification in a readonly process')
                
    def log(self, text):
        self.state_is_fine()
        utilities.append_file_safe(self.filename, text + '\n')
        warn(self.filename + ' ' + text)
        self.mtime = time.time()

    def new_page(self, ticket, user_name, user_ip, user_browser, date=None):
        if not self.loading and self.modifiable:
            self.log('new_page(%s ,%s, %s, %s, %s) # %d' % (
                repr(ticket),
                repr(user_name),
                repr(user_ip),
                repr(user_browser),
                repr(date),
                len(self.pages),
                ))
        p = Page(ticket, user_name, len(self.pages), self,
                 user_ip, user_browser, date)
        p.logged = self.loading or self.modifiable
        self.pages.append(p)
        return p

    def active_page(self, page, ffile):
        warn('page=%s file=%s(%s)' % (page, ffile, ffile.closed), what="table")
        page.browser_file = ffile
        if page not in self.active_pages:
            self.active_pages.append(page)

    def send_update(self, page, value):
        warn('actives: %s' % str(self.active_pages), what='table')
        for p in tuple(self.active_pages):
            if p == page:
                continue
            if p.browser_file.closed:
                self.active_pages.remove(p)
                if not hasattr(p, 'end_of_load'):
                    global canceled_loads
                    # Update list of canceled page load
                    now = time.time()
                    canceled_loads.append((now, p.user_name))
                    old = now - 3600
                    canceled_loads = [i for i in canceled_loads
                                     if i[0] > old]
                    user = p.user_name
                    nr = list([i for i in canceled_loads if i[1] == user])
                    if len(nr) == 4: # 4 cancels in less than one hour
                        warn('Send mail to ' + inscrits.L_fast.mail(user))
                        utilities.send_mail_in_background(
                            inscrits.L_fast.mail(user),
                            'Vous avez des ennuis avec TOMUSS ?',
                            unicode(utilities.read_file(os.path.join('FILES',
                                                             'mail_cancel')),
                                    'utf8').encode('latin1')
                            )

                    # Send a mail to the maintainer
                    utilities.send_backtrace(repr(nr), 'Canceled page load: '
                                             + user,
                                             exception=False)
                        
                continue
            if value is True:
                sender.append(p.browser_file, self.content(p))
            else:
                sender.append(p.browser_file, value)

    def authorized(self, page, value):
        # Authorized because the test have yet be done in the past
        if self.loading:
            return True
        # Values setted by user '' are modifiable
        if value.author == data.rw_user:
            return True
        # Empty values are modifiable by anyone
        if value.value == '':
            return True
        # The user can change its values
        if value.author == page.user_name:
            return True
        # RO and RW users have all the rights
        if page.user_name == data.ro_user or page.user_name == data.rw_user:
            return True
        # Values setted by user '*' are not modifiable
        if value.author == data.ro_user:
            return False
        # The teachers of the UE may change any value setted by another user
        if page.user_name in self.teachers:
            return True
        if page.user_name in self.masters:
            return True
        return False

    def authorized_column(self, page, a_column):
        return self.authorized(page, Cell(a_column.title, a_column.author))

    def cell_change(self, page, col, lin, value=None,
                    date=None, force_update=False):

        if not self.loading and not self.modifiable:
            return self.bad_ro(page)

        a_column = self.columns.from_id(col)
        if a_column == None:
            raise ValueError("Bug in 'cell_change' can't find column %s" % col)

        line = self.lines[lin]
        cell = line[a_column.data_col]

        if value is None:
            value = cell.value

        if not self.authorized(page, cell):
            utilities.warn('cell value = (%s)' % cell.value)
            return self.bad_auth(page)

        old_value = str(cell.value)
        new_value = str(value)
        if old_value == new_value and cell.author == page.user_name:
            return 'ok.png'            

        # if isinstance(value, str) and value.find('.') != -1:
        if a_column.type.name == 'Note':
            try:
                value = float(value)
            except ValueError:
                pass

        if (not self.loading and self.template
            and hasattr(self.template, 'cell_change')):
            self.template.cell_change(self, page, col, lin, value, date)

        if a_column.data_col == 0:
            login = utilities.the_login(old_value)
            if login in self.the_key_dict:
                try:
                    self.the_key_dict[login].remove(lin)
                except:
                    if login:
                        utilities.warn(str(page) + ' old_login=' + login
                                       + ' new_login=' + new_value
                                       + ' lin=' + lin
                                       + ' ' + repr(self.the_key_dict[login]))

            login = utilities.the_login(new_value)
            if login in self.the_key_dict:
                self.the_key_dict[login].append(lin)
            else:
                self.the_key_dict[login] = [lin]

        # The class may change on value change
        cell = line[a_column.data_col] = cell.set_value(value=value,
                                                        author=page.user_name,
                                                        date=date)
        if not self.loading:
            self.log('cell_change(%s,%s,%s,%s,"%s")' % (
                page.page_id,
                repr(col),
                repr(lin),
                repr(value),
                cell.date))
            t = '<script>Xcell_change(%s,%s,%s,%s,%s,%s);</script>\n' % (
                js(col),
                js(lin),
                js(value),
                js(cell.date),
                js(cell.author),
                js(cell.history),
                )
            if force_update:
                self.send_update(None, t)
            else:
                self.send_update(page, t)
            cell_changed_list_fast.append((self, lin, a_column))
        else:
            page.request += 1

        return 'ok.png'

    def default_nr_columns_change(self, n):
        """Deprecated"""
        self.default_nr_columns = n

    def add_master(self, name, page_id=0):
        """Deprecated"""
        name = name.lower()
        if name in self.masters:
            self.masters.remove(name)
        else:
            self.masters.append(name)
        if not self.loading:
            # For old TEMPLATES files
            self.log('table_attr("masters",%d,%s)' % (page_id, repr(name))) 

    def private_toggle(self, page):
        """Deprecated"""
        self.private = 1 - self.private
        if not self.loading: # compatibility with old TEMPLATES
            self.log('table_attr("private",%d,%d)' % (page.page_id,
                                                      self.private))
        return 'ok.png'

    def error(self, page, message):
        utilities.send_backtrace(
            'UE: %s, Page: %s' % (self.ue, page) , subject='###' + message)

        message = message + '''

Normalement vous ne devriez pas voir ce message.
Le responsable du serveur a reçu un mail
le prévenant du problème.

Nous vous conseillons de réactualiser la page
pour éviter tout problème et de refaire
la dernière saisie.
'''

        sender.append(page.browser_file,
                      '<script>alert(%s);</script>\n' % js(message))
        return "bad.png"

    def bad_column(self, page):
        return self.error(page, "Vous utilisez une colonne inexistante !")

    def bad_auth(self, page):
        return self.error(page, "Vous n'avez pas l'autorisation !")

    def bad_ro(self, page):
        return self.error(page, "Valeur seulement accessible en lecture !")

    def comment_change(self, page, col, lin, value):
        if not self.loading and not self.modifiable:
            return self.bad_ro(page)

        a_column = self.columns.from_id(col)
        if a_column == None:
            return self.bad_column(page)

        value = value.replace('\n','')
        line = self.lines[lin]
        if value == line[a_column.data_col].comment:
            return 'ok.png'

        if not self.loading:
            if not self.authorized(page, line[a_column.data_col]):
                return self.bad_auth(page)
            self.log('comment_change(%s,%s,%s,%s)' % (
                page.page_id,
                repr(col),
                repr(lin),
                repr(value),
                ))
            t = '<script>Xcomment_change(%s,%s,%s,%s);</script>\n' % (
                js(page.user_name),
                js(col),
                js(lin),
                js(value),
                )
            self.send_update(page, t)
        else:
            page.request += 1

        line[a_column.data_col] = line[a_column.data_col].set_comment(value)

        return 'ok.png'

    def empty(self, empty_even_if_used_page=False,
              empty_even_if_created_today=False,
              empty_even_if_column_created=False,
              ):
        if not empty_even_if_used_page and self.active_pages:
            return False, 'There is active pages'
        if not empty_even_if_created_today and time.time()-self.mtime <24*3600:
            return False, 'Created/Modified today'
        if self.comment:
            return False, 'There is a table comment: %s' % self.comment
        if not empty_even_if_column_created:
            for c in self.columns:
                if c.author != data.ro_user:
                    return False, 'A column title is set'
        for line in self.lines.values():
            for j in line:
                if not j.empty():
                    return False, 'A cell is not empty'
                if j.comment:
                    return False, 'A cell is with a comment'

        return True, '%d lines' % len(self.lines)

    def problem_in_column_name(self):
        names = set()
        for c in self.columns:
            if c.title in names:
                return 'Duplicate name: ' + c.title
            names.add(c.title)
        for c in self.columns:
            for name in c.depends_on():
                if name not in names:
                    return '"%s" use non-existent column "%s"' %(c.title, name)
        

    def table_comment(self, page, comment):
        """Deprecated"""
        return self.table_attr(page, 'comment', comment)

    def add_empty_column(self, page, the_id):
        if self.columns.columns:
            position = max([c.position for c in self.columns]) + 1
        else:
            position = 0

        a_column = column.Column(the_id, page.user_name, position=position)

        self.columns.append(a_column)
        for line in self.lines.values():
            line.append(cellempty)
        return a_column

    def column_attr(self, page, col_id, attr, value):
        col = self.columns.from_id(col_id)
        if col is None:
            col = self.add_empty_column(page, col_id)
        return column.ColumnAttr.attrs[attr].set(self, page, col, value)

    def column_changed(self, a_column, attribute):
        "An column attribute change, column content may be updated"
        column_changed_list.append((self, a_column, attribute))

    def table_attr(self, page, attr, value):
        return column.TableAttr.attrs[attr].set(self, page, value)

    def column_comment(self, page, col_id, comment):
        """DEPRECATED : use column_attr"""
        self.column_attr(page, col_id, 'comment', comment)

    def column_change(self, page, col_id, title, ttype, test, weight,
                      freezed, hidden=0, width=1):
        """DEPRECATED : use column_attr"""

        col = self.columns.from_id(col_id)
        if col is None:
            col = self.add_empty_column(page, col_id)
        attrs = column.ColumnAttr.attrs
        attrs['type'].set(self, page, col, ttype)
        attrs['title'].set(self, page, col, title)
        attrs['freezed'].set(self, page, col, freezed)
        attrs['hidden'].set(self, page, col, hidden)
        attrs['width'].set(self, page, col, width)

        t = test.split(';')
        if len(t) == 4:
            test = '[' + t[0].strip('[') + ';' + t[3].strip(']') + ']'
            attrs['red'].set(self, page, col, t[1])
            attrs['green'].set(self, page, col, t[2])
        if ttype == 'Nmbr':
            attrs['test_filter'].set(self, page, col, test)
        else:
            if test:
                attrs['minmax'].set(self, page, col, test)

        t = re.split(' +', weight)
        if len(t) > 1:
            weight = t[0]
            attrs['columns'].set(self, page, col, ' '.join(t[1:]))

        if weight:
            attrs['weight'].set(self, page, col, weight)


    def column_delete(self, page, col):
        if not self.loading and not self.modifiable:
            return self.bad_auth(page)
        a_column = self.columns.from_id(col)
        if a_column == None:
            return self.bad_column(page)
        # The first 'if' is to allow teachers to destroy
        # Columns created by 'data.ro_user' if they are not firsts ones.
        # THIS SHOULD BE REMOVED, but not yet.
        # It was tested because bad columns were created.
        if page.user_name not in self.masters and a_column.data_col < 6 :
            if not self.authorized_column(page, a_column):
                return self.bad_auth(page)
        if a_column.type.cell_is_modifiable and not a_column.empty():
            return self.error(page, "Destruction interdite (colonne pas vide)")

        if not self.loading:
            self.log('column_delete(%s,%s)' % (page.page_id, repr(col)))
            t = '<script>Xcolumn_delete(%s,%s);</script>\n' % (
                js(page.user_name), js(col))
            self.send_update(page, t)
        else:
            page.request += 1

        for line in self.lines.values():
            line.pop(a_column.data_col)
        self.columns.pop(a_column.data_col)
            
        return 'ok.png'

    def column_inscrit(self):
        for i, c in enumerate(self.columns):
            if c.freezed == 'C':
                return i
        return None

    def content_head(self, page):
        return table_head(
            self.year, self.semester, page.ticket, page.user_name,
            page.page_id, self.ue,
            attrs_from=self
            )

    def date_change(self, page, date):
        """Deprecated"""
        return column.TableAttr.attrs['dates'].set(self, page, date)

    def logins(self):
        for v in self.lines.values():
            if v[0].value != '':
                yield v[0].value

    def logins_valid(self):
        
        if self.column_inscrit() is None:
            for v in self.lines.values():
                if v[0].value != '':
                    yield v[0].value
        else:
            for v in self.lines.values():
                if v[0].value != '' and v[5].value != 'non':
                    yield v[0].value

    def the_keys(self):
        """Returns a dictionary for fast access by student login"""
        return self.the_key_dict
        if self.the_key_dict:
            return self.the_key_dict
        d = {}
        for k, v in self.lines.items():
            login = utilities.the_login(v[0].value)
            if login in d:
                d[login].append(k)
            else:
                d[login] = [k]
        self.the_key_dict = d
        return d

    def get_lines(self, login):
        try:
            lines = self.the_keys()[utilities.the_login(login)]
        except KeyError:
            return
        for lin in lines:
            yield self.lines[lin]

    def lines_of_grp(self, grp, seq):
        if grp == '':
            return # Do not auto compute ABINJ??? if there is no real groups
        grp_col = self.columns.get_grp()
        seq_col = self.columns.get_seq()
        for line in self.lines.values():
            if line[grp_col].value == grp and line[seq_col].value == seq:
                yield line

    def get_items(self, login):
        try:
            lines = self.the_keys()[utilities.the_login(login)]
        except KeyError:
            return
        for lin in lines:
            yield lin, self.lines[lin]
    
    def authors(self):
        """List of all the logins that have modified a cell value"""
        a = {}
        for v in self.lines.values():
            for cell in v:
                if cell.author not in ('', data.ro_user):
                    a[cell.author] = True
        return list(a.keys())

    def update_columns(self, columns):
        """Update the default columns of the table.
        This can be called by the TEMPLATE 'check' method
        """
        if not self.modifiable:
            return
        ro_page = self.pages[0]
        locked = self.the_lock.locked()
        try:
            if not locked:
                self.lock()
            for col in sorted(columns):
                for attr, value in columns[col].items():
                    self.column_attr(ro_page, col, attr, str(value))
        finally:
            if not locked:
                self.unlock()

    def content(self, page):
        warn('%s content for page %d' % (
            self.filename, page.page_id))
        s = []

        s.append(self.content_head(page))

        try:
            s.append('''  <script><!--
            lines_to_load = %d ;
            %s
            function initialize()
            {
            if ( ! wait_scripts("initialize()") )
               return ;
            document.write(head_html()) ;
            insert_middle();
            ''' % (len(self.lines), utilities.wait_scripts()))
            s.append(self.lines.js())
            s.append(self.columns.js(hide=False))

            s.append('document.write(tail_html());')
            s.append('runlog(columns, lines) ;')
            s.append('}')
            if self.template and hasattr(self.template, 'content'):
                s.append(self.template.content(self))
            s.append('initialize();')
            s.append('--></script>  \n')
        finally:
            pass

        return '\n'.join(s)

    def location(self):
        return '%d %s %s' % (self.year, self.semester, self.ue)

    def rewrite(self, only_columns=False):
        authors = {'*':0}
        s = ['# -*- coding: utf8 -*-']
        s.append('from data import *')
        s.append("new_page('' ,'*', '', '')")
        for c in self.columns:
            # if c.empty() and c.type.cell_compute == 'undefined':
            #    continue
            if c.author not in authors:
                s.append('new_page("",%s,"","")' % repr(c.author))
                authors[c.author] = len(authors)
            a = authors[c.author]

            for attr in column.ColumnAttr.attrs.values():
                if attr.computed:
                    continue
                attr_value = attr.decode(getattr(c, attr.name))
                if attr_value != attr.default_value:
                    s.append('column_attr(%s,%d,%s,%s)' % (
                        repr(attr.name), a, repr(c.the_id),
                        repr(attr_value)))
                         
        for attr in column.TableAttr.attrs.values():
            if attr.computed:
                continue
            attr_value = attr.decode(getattr(self, attr.name))
            if attr_value != attr.default_value:
                s.append('table_attr(%s,%d,%s)' % (
                    repr(attr.name), a,
                    repr(attr_value)))

        if only_columns:
            return '\n'.join(s) + '\n'
                         
        for line_key, line in self.lines.items():
            for col, cell in zip(self.columns, line):
                if cell.value != '':
                    if cell.author not in authors:
                        s.append('new_page("",%s,"","")' % repr(cell.author))
                        authors[cell.author] = len(authors)
                    a = authors[cell.author]

                    s.append('cell_change(%d,%s,%s,%s,%s)' % (
                        a,
                        repr(col.the_id),
                        repr(line_key),
                        repr(cell.value),
                        repr(cell.date),
                        ))
                    if cell.comment:
                        s.append('comment_change(%d,%s,%s,%s)' % (
                            a,
                            repr(col.the_id),
                            repr(line_key),
                            repr(cell.comment),
                            ))
                                                    
        return '\n'.join(s) + '\n'

    def close_active_pages(self):
        for page in self.active_pages:
            try:
                page.browser_file.write('<script>window.parent.close();</script>')
                page.browser_file.close()
            except:
                pass
        self.active_pages = []

    @utilities.add_a_lock
    def do_not_unload_add(self, value):
        self.do_not_unload += value

    def unload(self, force=False):
        if force:
            self.close_active_pages()
        if self.active_pages:
            return
        if self.do_not_unload:
            warn('Unload of do_not_unload: ' + str(self.ue), what="warning")
            return
            
        warn(str(self.ue), what="table")

        # XXX
        # In rare cases the table is unloaded while the student list
        # is being updated. So we finish with a table half updated
        # But it not important.
        self.unloaded = True # write access to the table will make an error.
        try:
            update_students.remove(self) # No update student list.
        except ValueError:
            pass
        tables_manage("del", self.year, self.semester, self.ue)
        utilities.unload_module(self.module) # 2009-09-07 Add this

    def delete(self):
        warn(str(self.ue), what="table")
        self.unload(force=True)
        if not self.unloaded:
            return
        # XXX Not locked, so the table may be reloaded before deletion....
        utilities.unlink_safe(self.filename)
        utilities.unlink_safe(self.filename + 'c', do_backup=False)

        for name in self.masters:
            master_of_update('-', name, self.year, self.semester, self.ue)


    def send_alert(self, text):
        self.send_update(None, '<script>alert(%s);</script>\n' %
                         js('Message de TOMUSS pour : ' + self.ue + '\n\n'
                            + text))

    def __str__(self):
        return '%d/%s/%s' % (self.year, self.semester, self.ue)

    def backtrace_html(self):
        return "Table: " + str(self)

    def readable_by(self, ticket):
        if (self.private
            and ticket.user_name not in self.masters 
            and ticket.user_name not in configuration.root
            ):
            warn('Unauthorized access', what='table')
            return False
        return True

def send_alert(text):    
    for atable in tables_values():
        atable.send_alert(text)

@utilities.add_a_lock
def tables_manage(action, year, semester, ue, do_not_unload=0, new_table=None):
    if action == 'get':
        try:
            t = tables[year, semester, ue]
            if t:
                t.do_not_unload_add(do_not_unload)
            return t
        except KeyError:
            tables[year, semester, ue] = None
            return False
    elif action == 'del':
        try:
            del tables[year, semester, ue]
            return
        except KeyError:
            return # Yet destroyed
    elif action == 'replace':
        tables[year, semester, ue] = new_table
        return new_table
    else:
        raise ValueError("Unknown action '%s'" % action)

def tables_values():
    # Use list because the tables may change while creating the list.
    # Do not use a tuple because it must be sortable
    # XXX Need a lock ?
    return [t
            for t in list(tables.values())
            if t not in (None, False, True)
            ]

            


def table(year, semester, ue, page=None, ticket=None, ro=False, create=True,
          do_not_unload=0):
    # utilities.warn('%s/%s/%s page=%s ticket=%s ro=%s create=%s' % (
    #    year, semester, ue, page, ticket, ro, create))
    year = int(year)
    t = tables_manage('get', year, semester, ue, do_not_unload)
    if t is None:
        # Somebody else is creating the table
        while t is None:
            time.sleep(0.1)
            t = tables_manage('get', year, semester, ue, do_not_unload)

    elif t is False:
        # I must create the table
        # Only one thread can be here at the same time.
        try:
            if ticket == None:
                if (not create
                    and not os.path.exists(table_filename(year, semester, ue))):
                    del tables[year, semester, ue]
                    return None
                t = Table(year, semester, ue, ro)
            else:
                t = Table(year, semester, ue, ro, user=ticket.user_name)
        except:
            # The table import failed, allow the new one to retry
            tables[year, semester, ue] = False
            raise
        t.do_not_unload_add(do_not_unload) # Only on this case
        tables[year, semester, ue] = t
    else:
        # Table yet loaded
        t = t.update()
        
    if page == None:
        if ticket == None:
            return t
        if not t.readable_by(ticket):
            return None, None
        # The new page may append work to check_students_in_tables
        # And the work is done without call to 'table'.
        # So possible simultaneous execution is possible.
        t.lock()
        try:
            page = t.new_page(ticket.ticket,
                              ticket.user_name,
                              ticket.user_ip,
                              ticket.user_browser,
                              time.strftime('%Y%m%d%H%M%S'))
        finally:
            t.unlock()
        return t, page

    try:
        page = t.pages[page]
    except IndexError:
        if t.modifiable:
            raise IndexError("REAL BUG: Page unknow in %s" % t)
        else:
            raise IndexError("Bug raised by TOMUSS restart on %s" % t)
    page.check_identity(ticket.ticket, ticket.user_name,
                        ticket.user_ip, ticket.user_browser)
    return t, page


def remove_unused_tables():
    """Do not call from a thread"""
    warn('start', what="table")
    for atable in tables_values():
        if not atable.active_pages:
            atable.unload()
    warn('stop', what="table")

# continuous update of students lists for all tables
def check_students_in_tables():
    while True:
        time.sleep(configuration.students_check_interval)
        for t in tables_values():
            update_students.append(t)
            time.sleep(10) # Avoid overload


# continuous update of students lists
update_students = []

def check_new_students_real():
    try:
        while update_students:
            t = update_students.pop()
            t.do_not_unload_add(1)
            if t.unloaded:
                continue
            utilities.bufferize_this_file(t.filename)
            try:
                warn('start update students of %s' % t.ue, what="table")

                if t.template and hasattr(t.template, 'check'):
                    t.template.check(t)
                warn('done %s' % t.ue, what="table")

                if t.modifiable:
                    for a_column in t.columns:
                        a_column.type.update_all(t, a_column)
            finally:
                t.do_not_unload_add(-1)
                utilities.bufferize_this_file(None)
            
    except IndexError:
        if not configuration.regtest:
            raise # Real problem
        # XXX The regtest raise a bug, why ?

def check_new_students():
    while True:
        if configuration.regtest_sync:
            time.sleep(0.001)
        else:
            time.sleep(1)

        check_new_students_real()

def master_of_update(what, name, year, semester, ue):
    if semester in configuration.master_of_exceptions:
        return

    d = utilities.manage_key('LOGINS', os.path.join(name, 'master_of'))
    if d is False:
        d = []
    else:
        d = eval(d)

    t = (str(year), semester, ue)
    if (t in d) and what == '-':
        d.remove(t)
    elif (t not in d) and what == '+':
        d.append(t)
    else:
        return

    d = utilities.manage_key('LOGINS', os.path.join(name, 'master_of'),
                             content = repr(d))


def login_list(page, name):
    # XXX Not very clean the : configuration.teachers[-1]
    t = list(inscrits.L_slow.firstname_or_surname_to_logins(
        name.replace('_',' '),
        base=configuration.teachers[-1],
        attributes = [configuration.attr_login,
                      configuration.attr_surname,
                      configuration.attr_firstname,
                      'cn']
        ))
    t.sort(key = lambda x: x[1] + x[2])
    if t:
        s = []
        for lo, surname, firstname, cn in t:
            s.append('[' + utilities.js(lo.encode('ufr8'))
                     + ',' + utilities.js(surname.upper().encode('ufr8'))
                     + ',' + utilities.js(firstname.title().encode('ufr8'))
                     + ',' + utilities.js(cn.encode('ufr8'))
                     + ']')
    else:
        s = []
    s = '<script>login_list(' + utilities.js(name) + \
        ',[' + ',\n'.join(s) + ']);</script>\n'
    sender.append(page.browser_file, s)
            

# Do the real job to answer to modification requests
# It is complicated because we may receive request in bad order.
# So we keep a list of requests and sort it.
request_list = []
def check_requests():
    my_request_list = []

    while True:
        time.sleep(0.1)
        
        # This is thread safe
        while request_list:
            my_request_list.append( request_list.pop() )
    
        my_request_list.sort()
        
        # warn('Requests: ' + '\n'.join([','.join([str(y) for y in x])                                     for x in my_request_list]), what='debug')
        t = []
        for r in my_request_list:
            request, page, action, path, output_file = r
            tabl = page.table
            warn('R=%d P=%d A=%s P=%s DNU=%d' % (request, page.page_id,
                                                 action, path,
                                                 tabl.do_not_unload),
                 what="DNU")
            if page.request > request:
                # An old request was given. Assume same answer XXX
                tabl.do_not_unload_add(-1)
                try:
                    warn('Old request asked : %d in place of %d' % (
                        request, page.request))
                    output_file.write(files['ok.png'])
                    output_file.close()
                except IOError:
                    pass
                except:
                    utilities.send_backtrace('Exception request %d' % request)
                continue
            if tabl.unloaded:
                utilities.send_backtrace('Request on unloaded table '+tabl.ue)
                continue # Forget this bad request
            if (page.request < request     # Wait missing requests
                or tabl.the_lock.locked()  # Do not wait on an locked table
                ):
                # do not decrement do_not_unload
                t.append(r)
                continue
            page.request += 1

            try:
                real_bug = True
                page.answer = 'bug.png'
                tabl.lock()
                try:
                    if action.startswith('column_attr_'):
                        page.answer = tabl.column_attr(page, path[0],
                                                       action[12:], path[1])
                    elif action.startswith('table_attr_'):
                        page.answer = tabl.table_attr(page,
                                                      action[11:], path[0])
                    elif action == 'cell_change':
                        col, lin, value  = path
                        page.answer = tabl.cell_change(page, col, lin, value)
                    elif action == 'comment_change':
                        col, lin, value = path
                        page.answer = tabl.comment_change(page, col, lin, value)
                    elif action == 'column_delete':
                        col = path[0]
                        page.answer = tabl.column_delete(page, col)
                    elif action == 'login_list':
                        login_list(page, utilities.safe(path[0]))
                        page.answer = 'ok.png'
                    elif action == 'update_content':
                        if tabl not in update_students:
                            update_students.append(tabl)
                    else:
                        warn('BUG: %s' % str(path), what="error")
                finally:
                    tabl.do_not_unload_add(-1)
                    tabl.unlock()
                # We don't want asynchronous update when doing regtest
                if configuration.regtest_sync:
                    update_students.append(tabl)
                    check_new_students_real()
            except:
                warn('bug raised', what="error")
                utilities.send_backtrace('check_requests : ' + action +repr(path))
                page.answer = 'bug.png'
                real_bug = False

            try:
                warn('Send %s(%s) %s' % (output_file, output_file.closed,
                                         page.answer), what="table")
                output_file.write(files[page.answer])
                output_file.close()
                sender.append(page.browser_file,
                              '<script>saved(%d);</script>\n' % request)
                if page.answer == 'bug.png' and real_bug:
                    sender.append(page.browser_file,
                                  """<script>
alert("Un bug c'est produit, l'administrateur a été prévenu. Vérifiez la valeur que vous avez saisie") ;
</script>\n""")
                    
            except socket.error:
                pass

        my_request_list = t
                           

# continuous send of packets to check connections
import sender
import ticket
def check_down_connections():
    while True:
        time.sleep(configuration.check_down_connections_interval)
        for ttable in tables_values():
            ttable.send_update(None, '<script>connected();</script>')
            for page in ttable.active_pages:
                if page.ticket not in ticket.tickets:
                    warn('%s ticked expired page=%s ticket=%s' % (
                        ttable.filename,
                        page.page_id,
                        page.ticket), what='error')
                    continue
                                                  
                t = ticket.tickets[page.ticket]
                if '-' in t.ticket:
                    sender.send_live_status('<script>d("%s","%s","%s",0.01,"pong", "%s",%s,%s);</script>\n'%(
                        t.user_ip,
                        t.ticket.split('-')[1] + '/' + t.user_name,
                        t.access_right(),
                        ttable.year, utilities.js(ttable.semester),
                        utilities.js(ttable.ue)))

# Update computed values

cell_changed_list_fast = []

def update_computed_values_fast():
    while True:
        time.sleep(0.1)
        while cell_changed_list_fast:
            the_table, lin, a_column = cell_changed_list_fast.pop()
            for col in the_table.columns.use(a_column):
                col.type.update_one(the_table, lin, col)

column_changed_list = []

def update_computed_values_slow():
    while True:
        time.sleep(0.1)
        while column_changed_list:
            the_table, a_column, attr = column_changed_list.pop()
            column.type.update_all(the_table, a_column, attr)
            for col in the_table.columns.use(a_column):
                col.type.update_all(the_table, col)

def start_threads():
    utilities.start_new_thread_immortal(check_new_students, ())
    utilities.start_new_thread_immortal(check_students_in_tables, ())
    utilities.start_new_thread_immortal(check_requests, ())
    utilities.start_new_thread_immortal(check_down_connections, ())
    utilities.start_new_thread_immortal(update_computed_values_fast, ())
    utilities.start_new_thread_immortal(update_computed_values_slow, ())

