#!/bin/env python3
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
import time
import threading
import socket
import re
import collections
import html
import inspect
from . import utilities
from . import configuration
from . import column
from . import data
from . import files
from . import inscrits
from .cell import CellValue, Lines, cellempty
from . import sender
from . import plugins

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

the_head = files.add('FILES','head.html')

js = utilities.js

canceled_loads = []

# Key : student_id, give the tables ue name
# Used only in 'suivi' because it does not contain year/semester
tables_of_student = {}

class Page(object):
    request = 0
    last_request = 0
    def __init__(self, the_ticket, user_name, page_id, ttable,
                 user_ip, user_browser, date=None):
        self.ticket = the_ticket
        self.user_name = user_name
        self.page_id = page_id
        self.table = ttable
        self.nr_cell_change = 0
        self.browser_file = None
        self.user_ip = user_ip
        self.user_browser = user_browser
        self.date = date

    def check_identity(self, the_ticket, user_name, user_ip, user_browser):
        # Allow IP change with the same identity
        if (the_ticket == self.ticket
            and user_name == self.user_name
            and user_browser == self.user_browser):
            return
        warn('received ticket=%s user_name=%s user_browser=%s ip=%s' % (
            the_ticket, user_name, user_browser, user_ip), what="Info")
        warn('current  ticket=%s user_name=%s user_browser=%s ip=%s' % (
            self.ticket, self.user_name, self.user_browser, self.user_ip),
             what="Info")
        if configuration.regtest_sync or not configuration.regtest:
            raise ValueError('Cheater')

    def add_request(self, request, action, path, output_file):
        self.last_request = time.time()
        check_requests.the_lock.acquire()
        request_list.append((self.page_id, request, self, action, path,
                             output_file))
        check_requests.the_lock.release()
        utilities.important_job_add('request')

    def __str__(self):
        return '%s[%s]:%s(%s)' % (self.table, self.page_id, self.user_name,
                                  self.date)

    def date_time(self):
        return date_time(self.date)
    def day(self):
        return self.date[6:8] + '/' + self.date[4:6] + '/' + self.date[:4]

    def backtrace_html(self):
        return (html.escape(str(self)) + '<br>'
               + html.escape(self.user_browser) + '<br>'
                + self.user_ip)


def table_filename(year, semester, ue):
    return os.path.join(configuration.db, 'Y'+str(year), 'S'+semester, ue + '.py')

def link_to(filename):
    ln = os.readlink(filename)[:-3].split(os.path.sep)
    ue = ln[-1]
    if len(ln) == 3:
        assert(ln[0] == '..')
        assert(ln[1][0] == 'S')
        year = self.year
        semestre = ln[1][1:]
    elif len(ln) == 5:
        assert(ln[0] == '..')
        assert(ln[1] == '..')
        assert(ln[2][0] == 'Y')
        assert(ln[3][0] == 'S')
        year = int(ln[2][1:])
        semestre = ln[3][1:]
    else:
        assert(len(ln) == 1)
    return year, semestre, ue

def filter_language(language):
    # Remove not translated languages and duplicates
    t = []
    for x in language.strip(",").split(','):
        if x in plugins.languages:
            if x not in t:
                t.append(x)
    return ','.join(t)

def get_preferences(user_name, create_pref=True, the_ticket=None):
    from .PLUGINS import suivi_student
    p = suivi_student.display_preferences_get(user_name)
    for k, v in {'display_tips'   : 1,
                 'nr_favorites'   : 6,
                 'nr_lines'       : 0,
                 'nr_cols'        : 0,
                 'zebra_step'     : 5,
                 'page_step'      : 1,
                 'invert_name'    : 1,
                 'scrollbar_right': 1,
                 'favoris_sort'   : 0,
                 'v_scrollbar'    : 1,
                 'v_scrollbar_nr' : 1,
                 'interface'      : "N",
                 'current_suivi'  : 0,
                 'debug_table'    : 0,
                 'home_3scrollbar': 1,
                 'one_line_more'  : 1,
                 'filter_freezed' : 0,
    }.items():
        if k not in p:
            p[k] = v

    # XXX compatibility with old TOMUSS version
    my_identity2 = utilities.login_to_module(user_name)
    if os.path.exists(table_filename(0, 'Preferences', my_identity2)):
        prefs_table = table(0, 'Preferences', my_identity2, None, None,
                            create=False)
        if prefs_table is not None:
            for k, v in p.items():
                # Do not get theses preferences.
                if k in ('nr_lines', 'nr_cols', 'display_tips'):
                    continue
                if k in prefs_table.lines:
                    p[k] = prefs_table.lines[k][3].value
            if create_pref:
                utilities.manage_key('LOGINS',
                                     os.path.join(user_name,'preferences'),
                                     content = repr(p))
                prefs_table.delete()

    warn('Language in preferences: (%s)' % p.get('language', ''), what="lang")
    if p.get('language', '') == '':
        if the_ticket is None:
            warn('Search old ticket to find language')
            for the_ticket in ticket.tickets.values():
                if the_ticket.user_name == user_name:
                    break
        warn('Language in ticket: (%s)' % the_ticket.language, what="lang")
        p['language'] = the_ticket.language

    p['language'] = filter_language(p['language'])
    warn('Language after filtering: ' + p['language'],what="lang")
    if p['language'] == '':
        warn('Language in server: (%s)' % configuration.language,
             what="lang")
        p['language'] = configuration.language

    return p


#REDEFINE
# This function returns javascript code to be included
# in the header of the 'ue' table
def table_head_more(dummy_ue):
    return ''

def translations_init(language):
    languages = []
    language = filter_language(language + ',' + configuration.language)
    for lang in language.split(','):
        languages.append(
            '<script onload="this.onloadDone=true;" src="%s/%s.js"></script>'
            % (configuration.url_files, lang))
    return ('<script>var translations = {},'
            + 'preferences={"language":%s} ; </script>\n'
            % js(language)
            + '\n'.join(languages) + '\n')


@utilities.add_a_cache0
def all_the_semesters():
    return js(configuration.special_semesters + ''.join(
        '<option>%s/%s</option>' % (year, semester)
        for dummy_url, dummy_port, year, semester, dummy_host in
        configuration.suivi.urls_sorted()))

def table_head(year=None, semester=None, the_ticket=None,
               user_name='', page_id=-1, ue='',
               create_pref=True,
               attrs_from=0, hide_more=False, table=None):
    s = configuration.suivi.url(year, semester, the_ticket)
    t = ticket.tickets.get(the_ticket, None)
    prefs_table = get_preferences(user_name, create_pref, the_ticket=t)
    try:
        background = configuration.semesters_color[configuration.semesters.index(semester)]
        background = '<style>BODY, TABLE INPUT, #current_input, BODY TABLE.colored TD { background-color: ' + background + '}</style>'
    except ValueError:
        background = ''

    my_identity2 = utilities.login_to_module(user_name)

    bookmarked = utilities.manage_key('LOGINS',
                                      os.path.join(user_name, 'bookmarked'))
    if bookmarked:
        bookmarked = (year, semester, ue) in eval(bookmarked)

    return (str(the_head) + background +
            translations_init(prefs_table['language']) +
            '<script>\n' +
            'page_id = "%d" ;\n' % page_id +
            'my_identity = %s ;\n' % repr(user_name) +
            'my_identity2 = %s ;\n' % repr(my_identity2) +
            'url = %s ;\n' % js(configuration.server_url) +
            'year = "%s" ;\n' % year +
            'semester = "%s" ;\n' % semester +
            'ticket = "%s" ;\n' % the_ticket +
            'ue = "%s" ;\n' % ue +
            'suivi = %s ;\n' % js(s) +
            'version = "%s" ;\n' % configuration.version +
            'root = %s ;\n' % js(list(configuration.root)) +
            'cas_url = %s ;\n' % repr(configuration.cas) +
            'preferences = %s ;\n' % prefs_table +
            'bookmarked = %d ;\n' % int(bookmarked)  +
            'lines = {};\n' +
            'columns = [];\n' +
            'lines_to_load = 0 ;\n' +
            'minors = %s ;\n' % js(configuration.major_of(user_name)) +
            'ticket_time_to_live = %d ;\n' % configuration.ticket_time_to_live +
            'upload_max = %d ;\n' % configuration.upload_max +
            'max_visibility_date = %d ;\n' % configuration.max_visibility_date +
            'gui_record = %d ;\n' % int(configuration.gui_record) +
            'all_the_semesters = %s ;\n' % all_the_semesters() +
            'check_down_connections_interval = %d ;\n' % configuration.check_down_connections_interval +
            'table_attr = {\n' +
                ',\n'.join(attr.name+':'+js(
                getattr(attrs_from, attr.name,
                        attr.get_default_value(table)))
                for attr in column.TableAttr.attrs.values()
                ) + '} ;\n' +
            (hide_more and '' or table_head_more(ue)) +
            '</script>\n')

class Template(object):
    loaded = {}
    module = None
    update_time = 0

    def __init__(self, name):
        self.name = name

    def update_template(self):
        if time.time() - self.update_time < 2:
            if not configuration.regtest:
                return
        self.update_time = time.time()
        if self.name == "NONE":
            return
        self.module = utilities.import_reload(self.name)[0]
        if hasattr(self.module, 'prototype'):
            prototype = import_template(self.module.prototype)
        else:
            prototype = None
        for item in ('init', 'create', 'onload', 'cell_change',
                     'comment_change', 'content', 'css', 'check'):
            if hasattr(self.module, item):
                self.__dict__[item] = getattr(self.module, item)
            elif prototype:
                self.__dict__[item] = getattr(prototype, item)

    def init(*args, **keys):
        pass
    def create(self, ttable):
        ttable.get_ro_page()
        ttable.table_attr(ttable.pages[0], 'masters', [ttable.user])
    def onload(*args, **keys):
        pass
    def cell_change(*args, **keys):
        pass
    def comment_change(*args, **keys):
        pass
    css = ''
    def check(*args, **keys):
        pass
    def content(*args, **keys):
        return ''

def search_template(name):
    if name in Template.loaded:
        return Template.loaded[name]
    for path in (
            ('LOCAL', 'LOCAL_TEMPLATES', name.lstrip('/')),
            ('TEMPLATES', name.lstrip('/')),
        ):
        if (configuration.regtest or name.startswith('/')
            ) and path[0] == 'LOCAL':
            continue
        filename = os.path.join(*path) + '.py'
        if os.path.exists(filename):
            t = Template(filename)
            Template.loaded[name] = t
            return t

def import_template(ue, semester=''):
    t = search_template(ue) or search_template(semester) or Template('NONE')
    t.update_template()
    return t

class Table(object):
    new_abjs = None
    force_update = 0
    
    def __init__(self, year, semester, ue, ro=True, user=None):

        warn('%s/%s/%s ro=%s user=%s' % (year, semester, ue, ro, user),
             what="table")
        self.year = year
        self.semester = semester
        self.ue = ue
        self.loading = False # The table is not being loaded
        self.sent_to_browsers = [] # Nothing has been sent

        if self.ue == 'abj' or self.ue == 'data':
            # Break the import in the file
            raise ValueError("Invalid table name: '%s'" % self.ue)

        # Remove -1 -2 -3 ... -9999... at the end of the UE name
        ue_code = ue.split('-')
        if len(ue_code) > 2 and utilities.is_an_int(ue_code[-1]):
            self.ue_code = '-'.join(ue_code[:-1])
        else:
            self.ue_code = ue

        for attr in column.TableAttr.attrs.values():
            d = attr.get_default_value(self)
            if isinstance(d, list):
                d = list(d)
            elif isinstance(d, dict):
                d = dict(d)
            setattr(self, attr.name, d)

        self.pages = []
        self.active_pages = []
        self.columns = column.Columns(self)
        self.lines = Lines(self.columns)
        self.the_lock = threading.Lock()
        self.ro = ro
        self.mtime = 0
        self.the_key_dict = collections.defaultdict(list)
        self.unloaded = False
        self.do_not_unload = []
        dirname = os.path.join(configuration.db,
                               'Y'+str(self.year), 'S'+self.semester)
        self.filename = os.path.join(dirname, ue + '.py')

        self.template = import_template(self.ue_code, self.semester)
        self.template.init(self)

        if self.template.module:
            for v in self.template.module.__dict__.values():
                if isinstance(v, utilities.Variables):
                    self.group = v._group

        created = False
        self.on_disc = True
        if self.modifiable:
            utilities.mkpath_safe(dirname)
            if not os.path.exists(self.filename):
                s = ['# -*- coding: utf8 -*- ']
                s.append('from TOMUSS.data import *')
                s = '\n'.join(s) + '\n'
                utilities.mkpath_safe(dirname)
                utilities.append_file_safe(self.filename, s)
                created = True
        else:
            if not os.path.exists(self.filename):
                self.on_disc = False

        if not os.path.exists(self.filename):
            # Read only table and file does not exists
            return

        self.mtime = os.path.getmtime(self.filename)

        if not created:
            data.begin(self)
            try:
                c = compile(utilities.read_file(self.filename), self.filename,
                            'exec')
                eval(c)
                del c
            finally:
                data.end()

        else:
            if ro:
                return # Do not create the table
            # Remove this file because it is created the same second
            # than the .py file, So it is not recompiled in some case.
            # os.remove(self.filename + 'c')
            warn('Create start', what='table')
            self.user = user # Usable by template.create()
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

        self.template.onload(self)
            
        if not ro:
            # Check mails or new students
            # Only mail if allow_modification is False
            warn('Update student list', what='table')
            update_students.append(self)

        if ro and self.official_ue and not configuration.index_are_computed:
            # Student are never removed, but it is not important
            for login in self.the_keys():
                if login in tables_of_student:
                    if self.ue not in tables_of_student[login]:
                        tables_of_student[login].add(self.ue)
                else:
                    tables_of_student[login] = set((self.ue,))

        if ro:
            self.compute_columns()

        self.extensions = []
        if self.semester == configuration.university_semesters[0]:
            for dy, sem in zip(configuration.semesters_year,
                               configuration.semesters):
                if sem == self.semester:
                    continue
                if os.path.islink(table_filename(year-dy, sem, self.ue)):
                    self.extensions.append((year-dy, sem))

    @utilities.add_a_lock
    def compute_columns(self):
        """ """
        for column in self.columns:
            column.type.update_for_suivi(column)

        from .PYTHON_JS import tomuss_python
        from . import cell
        tomuss_python.columns = self.columns.columns
        tomuss_python.C = cell.Cell
        for i in ('abi', 'abj', 'ppn', 'tnr', 'pre'):
            setattr(tomuss_python, i, getattr(configuration, i, ''))
            setattr(tomuss_python, i+'_short',
                        getattr(configuration, i+'_short', ''))
        for column in self.columns.columns_ordered():
            column.real_weight = tomuss_python.to_float(column.weight)
            column.real_weight_add = not column.weight.startswith(('+','-'))
            column.min, column.max = column.min_max()
            column.best_of = -int(tomuss_python.to_float(column.best))
            column.mean_of = -int(tomuss_python.to_float(column.worst))
            if column.rounding == '':
                column.round_by = 0
            else:
                column.round_by = float(column.rounding)
            column.nmbr_filter = tomuss_python.Filter(column.test_filter,
                                                      '',
                                                      column.type.name).evaluate
            if column.is_computed():
                try:
                    column.average_columns = [
                        self.columns.from_title(title).data_col
                        for title in column.depends_on()
                    ]
                except:
                    column.average_columns = []
                if column.type.name == 'Nmbr':
                    column.max = len(column.average_columns)
                cell_compute = eval(column.type.cell_compute,
                                    tomuss_python.__dict__
                                )
                for line in self.lines.values():
                    tomuss_python.compute_cell_safe(column.data_col, line,
                                                    cell_compute)

    def update(self):
        """Update the table if the file on disc changed.
        It is used only by 'suivi' servers
        """
        # warn('Start ro=%s dt=%f p=%s' % (self.ro, time.time() - self.mtime, os.path.exists(self.filename)), what="table")
        if not self.ro:
            return self

        if not os.path.exists(self.filename):
            # Do not work (to to recreate it)
            # tables_manage("del", self.year, self.semester, self.ue)
            # Should return None, but as it is very intrusive
            # Make a non dangerous kludge
            self.official_ue = False
            return self
        
        if time.time() - self.mtime < configuration.maximum_out_of_date:
            return self

        if os.path.getmtime(self.filename) <= self.mtime:
            return self

        warn('%s time=%s mtime=%s' % (self.ue, time.time(), self.mtime),
             what="table")

        return tables_manage("replace", self.year, self.semester, self.ue,
                             new_table = Table(self.year, self.semester,
                                               self.ue, ro=True))


    def change_mails(self, mails):
        self.table_attr_computed('mails', mails)
    def change_portails(self, portails):
        self.table_attr_computed('portails', portails)

    def table_attr_computed(self, attr, value):
        if getattr(self, attr) == value:
            return
        setattr(self, attr, value)
        t = '<script>Xtable_attr(%s,%s);</script>\n' % (repr(attr), js(value))
        self.send_update(None, t)

    def update_mail(self, login, mail):
        warn('update mail of ' + self.location(), what="table")
        self.mails[login] = mail
        self.send_update(None,
                         ('<script>update_mail(' + repr(login)
                         + ',' + js(mail) + ');</script>\n')
                         )

    def update_portail(self, login, portail): 
        self.portails[login] = portail
        self.send_update(None,
                         ('<script>update_portail(' + repr(login)
                         + ',' + js(portail) + ');</script>\n')
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
        p.index = len(self.sent_to_browsers)
        self.pages.append(p)
        return p

    def active_page(self, page, ffile):
        warn('page=%s file=%s(%s)' % (page, ffile, ffile.closed), what="table")
        page.browser_file = ffile
        if page not in self.active_pages:
            self.active_pages.append(page)

    def remove_active_page(self, page):
        self.active_pages.remove(page)
        page.browser_file = None # stop a memory leak
            
    def send_update(self, page, value, store=True):
        warn('%s actives: %s' % (page, str(self.active_pages)), what='table')
        if store:
            self.sent_to_browsers.append(value)
        for p in tuple(self.active_pages):
            if p == page:
                continue
            if p.browser_file.closed:
                self.remove_active_page(p)
                if hasattr(p, 'start_load') and not hasattr(p, 'end_of_load'):
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
                        user_mail = inscrits.L_fast.mail(user)
                        if user_mail:
                            utilities.send_mail_in_background(
                                user_mail,
                                # XXX need translation
                                utilities._("MSG_document_problems"),
                                utilities.read_file(
                                        os.path.join('FILES', 'mail_cancel'))
                                )

                    # Send a mail to the maintainer
                    utilities.send_backtrace(
                        repr(nr),
                        utilities._("MSG_document_canceled") + user,
                        exception=False)
                        
                continue
            if value is True:
                sender.append(p.browser_file, self.content(p),
                              index=len(self.sent_to_browsers), page=p)
            else:
                sender.append(p.browser_file, value,
                              index=len(self.sent_to_browsers), page=p)

    @utilities.add_a_method_cache
    def cell_writable_filter(self, filter_user_type):
        from .PYTHON_JS import tomuss_python
        return tomuss_python.Filter(*filter_user_type).evaluate

    def authorized(self, user_name, value, column=None, line=None):
        # Authorized because the test have yet be done in the past
        if self.loading:
            return True
        # RO and RW users have all the rights
        if user_name == data.ro_user or user_name == data.rw_user:
            return True
        # Values setted by user '*' are not modifiable
        if value.author == data.ro_user and value.value != '':
            return False
        # The masters of the UE may change any value setted by another user
        if user_name in self.masters:
            return True
        # Values setted by user '' are modifiable
        if value.author == data.rw_user:
            return True
        if column and column.cell_writable:
            return self.cell_writable_filter(
                (column.cell_writable, user_name, column.type.name)
            )(line, value)
        # Empty values are modifiable by anyone
        if value.value == '':
            return True
        # The user can change its values
        if value.author == user_name:
            return True
        return False

    def authorized_column(self, user_name, a_column):
        return self.authorized(
            user_name, CellValue(a_column.title, a_column.author))

    def cell_change(self, page, col, lin, value=None,
                    date=None, force_update=False,
                    change_author=True):
        if not self.loading and not self.modifiable:
            return self.bad_ro(page)
        a_column = self.columns.from_id(col)
        if a_column == None:
            raise ValueError(utilities._("MSG_document_bug_column") % col)

        on_a_new_line = lin not in self.lines
        line = self.lines[lin]
        cell = line[a_column.data_col]

        if value is None:
            value = cell.value

        if not self.loading and not force_update:
            if not self.authorized(page.user_name, cell, a_column, line):
                utilities.warn('cell value = (%s)' % cell.value)
                return self.bad_auth(page, "cell_change %s/%s/%s" % (
                        col, lin, value))
            if a_column.locked and page.user_name != data.ro_user:
                self.error(page, utilities._("MSG_document_column_locked"))
                return 'bad.png'

        old_value = str(cell.value)
        new_value = str(value)
        if new_value == 'nan':
            value = "nan"
        # If the old value is the float 10
        # And the new one the string 10
        # The string compare will be false because "10.0" != "10"
        # So we also compare non string values.
        try:
            equal = old_value == new_value or float(cell.value) == float(value)
        except ValueError:
            equal = False
        if equal:
            if cell.author == page.user_name:
                return 'ok.png'
            if not change_author:
                return 'ok.png'

        # if isinstance(value, str) and value.find('.') != -1:
        if a_column.type.should_be_a_float:
            try:
                if value != "nan":
                    value = float(value)
            except ValueError:
                pass

        if (not self.loading
            and a_column.repetition
            and value != ''
            and not equal
            # 'repetition' is checked only for the first member
            and not getattr(a_column, 'groupcolumn_running', False)
        ):
            data_col = a_column.data_col
            group = None
            if a_column.groupcolumn:
                group = self.columns.from_title(a_column.groupcolumn)
                if group:
                    group = group.data_col
            if a_column.repetition > 0:
                verify_lines = self.lines.values()
            else:
                grp = line[self.columns.get_grp()].value
                seq = line[self.columns.get_seq()].value
                verify_lines = self.columns.table.lines_of_grp(grp, seq)
            if group is None:
                n = 0
                for a_line in verify_lines:
                    if a_line[data_col].value == value:
                        n += 1
            else:
                groups = set()
                for a_line in verify_lines:
                    if a_line[data_col].value == value:
                        groups.add(str(line[group].value))
                n = len(groups)
            if n >= abs(a_column.repetition):
                sender.append(
                    page.browser_file,
                    '<script>alert(_("ALERT_repetition")+%s+"/"+%s);</script>\n'
                    % (js(value), js(a_column.title)))
                return 'bad.png'

        if not self.loading and not equal:
            self.template.cell_change(self, page, col, lin, value, date)

        if a_column.data_col == 0:
            login = utilities.the_login(old_value)
            if login in self.the_key_dict:
                try:
                    self.the_key_dict[login].remove(lin)
                    if len(self.the_key_dict[login]) == 0:
                        del self.the_key_dict[login]
                except:
                    if login:
                        utilities.warn(str(page) + ' old_login=' + login
                                       + ' new_login=' + new_value
                                       + ' lin=' + lin
                                       + ' ' + repr(self.the_key_dict[login]))
            new_login = utilities.the_login(new_value)
            self.the_key_dict[new_login].append(lin)
            if not self.loading and self.official_ue:
                indexes_to_update.append((self, login, new_login))
                for y, s in self.extensions:
                    indexes_to_update_append(y, s, self.ue, login, new_login)

        elif on_a_new_line:
            self.the_key_dict[''].append(lin)

        # The class may change on value change
        cell = line[a_column.data_col] = cell.set_value(value=value,
                                                        author=page.user_name,
                                                        date=date)
        page.nr_cell_change += 1
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

            if (a_column.groupcolumn
                and not getattr(a_column, 'groupcolumn_running', False)
                ):
                a_column.groupcolumn_running = True
                try:
                    for line_key, i_line in a_column.lines_of_the_group(line):
                        if self.authorized(page.user_name,
                                           i_line[a_column.data_col],
                                           a_column, i_line):
                            self.cell_change(page, a_column.the_id,
                                             line_key, value,
                                             force_update=True)
                finally:
                    a_column.groupcolumn_running = False

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

    def get_a_page_for(self, user_list):
        """Returns a page for one of the users in the list.
        If not exists, create one with the first user.
        If the user list is empty, create a page for the rw_user
        """
        rw = None
        for p in self.pages:
            if p.user_name in user_list:
                return p
            if p.user_name == data.rw_user:
                rw = p
        if user_list:
            return self.new_page('', user_list[0], '', '')
        if rw:
            return rw
        return self.new_page('', data.rw_user, '', '')

    def get_a_master_page(self):
        """Returns a page modifiable by the masters.
        Create one if there is none"""
        return self.get_a_page_for(self.masters)

    def get_ro_page(self):
        """Returns a page modifiable by nobody."""
        return self.get_a_page_for((data.ro_user,))

    def get_a_root_page(self):
        """Returns a page for root."""
        return self.get_a_page_for((configuration.root[0],))

    def get_rw_page(self):
        """Returns a page modifiable by anybody."""
        return self.get_a_page_for(())

    def get_nobody_page(self):
        """Returns a page for the nobody user."""
        return self.get_a_page_for((data.no_user,))

    def private_toggle(self, page):
        """Deprecated"""
        self.private = 1 - self.private
        if not self.loading: # compatibility with old TEMPLATES
            self.log('table_attr("private",%d,%d)' % (page.page_id,
                                                      self.private))
        return 'ok.png'

    def error(self, page, message, more_in_mail=""):
        utilities.send_backtrace(
            'UE: %s, Page: %s' % (self.ue, page)
            + '\n' + more_in_mail, subject='###' + message,
            exception=False)
        if '_(' not in message:
            # The message is not javascript program
            message = js(message)
        message = message + '+"\\n\\n"+_("ERROR_server_bug")'
        sender.append(page.browser_file,
                      '<script>alert(%s);</script>\n' % message)
        return "bad.png"

    def bad_column(self, page):
        return self.error(page, '_("ALERT_column_not_exist")')

    def bad_auth(self, page, more_in_mail=""):
        return self.error(page, '_("ALERT_not_authorized")', more_in_mail)

    def bad_ro(self, page):
        return self.error(page, '_("ALERT_value_ro")')

    def comment_change(self, page, col, lin, value):
        if not self.loading and not self.modifiable:
            return self.bad_ro(page)

        a_column = self.columns.from_id(col)
        if a_column == None:
            return self.bad_column(page)

        line = self.lines[lin]
        if value == line[a_column.data_col].comment:
            return 'ok.png'

        
        if not self.loading:
            if not self.authorized(page.user_name,
                                   line[a_column.data_col], a_column, line):
                return self.bad_auth(page, "comment_change %s/%s/%s" % (
                        col, lin, value))
            self.template.comment_change(self, page, col, lin, value)
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

        line[a_column.data_col] = line[a_column.data_col].set_comment(value)

        return 'ok.png'

    def empty(self, empty_even_if_used_page=False,
              empty_even_if_created_today=False,
              empty_even_if_column_created=False,
              ):
        if not empty_even_if_used_page and self.active_pages:
            return False, utilities._("MSG_document_table_active")
        if not empty_even_if_created_today and time.time()-self.mtime <24*3600:
            return False, utilities._("MSG_document_table_today")
        if self.comment:
            return False, utilities._("MSG_document_table_comment"
                                      ) % html.escape(self.comment)
        if not empty_even_if_column_created:
            for c in self.columns:
                if c.author != data.ro_user and c.author != data.no_user:
                    return False, utilities._("MSG_document_table_title")
        for line in self.lines.values():
            for j in line:
                if not j.empty():
                    return False, utilities._("MSG_document_table_cell")
                if j.comment:
                    return False, utilities._("MSG_document_table_cell_comment")

        return True, utilities._("MSG_document_table_lines") % len(self.lines)

    def problem_in_column_name(self):
        names = set()
        for c in self.columns:
            if c.title in names:
                return utilities._("MSG_document_table_duplicate") + c.title
            names.add(c.title)
        for c in self.columns:
            for name in c.depends_on():
                if name not in names:
                    return utilities._("MSG_document_table_no_column") % (
                        c.title, name)
        return ""
        

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
        date = time.strftime('%Y%m%d%H%M%S')
        return column.ColumnAttr.attrs[attr].set(self, page, col, value, date)

    def column_changed(self, a_column, attribute):
        "An column attribute change, column content may be updated"
        column_changed_list.append((self, a_column, attribute))

    def table_attr(self, page, attr, value):
        date = time.strftime('%Y%m%d%H%M%S')
        return column.TableAttr.attrs[attr].set(self, page, value, date)

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
        attrs['type'].set(self, page, col, ttype, '')
        attrs['title'].set(self, page, col, title, '')
        attrs['freezed'].set(self, page, col, freezed, '')
        attrs['hidden'].set(self, page, col, hidden, '')
        attrs['width'].set(self, page, col, width, '')

        t = test.split(';')
        if len(t) == 4:
            test = '[' + t[0].strip('[') + ';' + t[3].strip(']') + ']'
            attrs['red'].set(self, page, col, t[1], '')
            attrs['green'].set(self, page, col, t[2], '')
        if ttype == 'Nmbr':
            attrs['test_filter'].set(self, page, col, test, '')
        else:
            if test:
                attrs['minmax'].set(self, page, col, test, '')

        t = re.split(' +', weight)
        if len(t) > 1:
            weight = t[0]
            attrs['columns'].set(self, page, col, ' '.join(t[1:]), '')

        if weight:
            attrs['weight'].set(self, page, col, weight, '')


    def column_delete(self, page, col):
        if not self.loading and not self.modifiable:
            return self.bad_ro(page)
        a_column = self.columns.from_id(col)
        if a_column == None:
            return self.bad_column(page)
        # The first 'if' is to allow teachers to destroy
        # Columns created by 'data.ro_user' if they are not firsts ones.
        # THIS SHOULD BE REMOVED, but not yet.
        # It was tested because bad columns were created.
        if page.user_name not in self.masters and a_column.data_col < 6 :
            if not self.authorized_column(page.user_name, a_column):
                return self.bad_auth(page, "column_delete %s" % col)
        if (a_column.type.cell_is_modifiable
            and not a_column.empty_of_user_values()):
            return self.error(page, '_("ALERT_delete_not_empty")')

        if not self.loading:
            self.log('column_delete(%s,%s)' % (page.page_id, repr(col)))
            t = '<script>Xcolumn_delete(%s,%s);</script>\n' % (
                js(page.user_name), js(col))
            self.send_update(page, t)

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
            attrs_from=self, table=self
            )

    def date_change(self, page, date):
        """Deprecated"""
        return column.TableAttr.attrs['dates'].set(self, page, date, '')

    def logins(self):
        for v in self.lines.values():
            if v[0].value != '':
                yield v[0].value

    def logins_valid(self):
        c = self.column_inscrit()
        if c is None:
            for v in self.lines.values():
                if v[0].value != '':
                    yield v[0].value
        else:
            for v in self.lines.values():
                if v[0].value != '' and v[c].value != 'non':
                    yield v[0].value

    def the_keys(self):
        """Returns a dictionary for fast access by student login"""
        return self.the_key_dict

    def get_lines(self, login):
        login = utilities.the_login(login)
        if login in self.the_key_dict:
            for lin in self.the_key_dict[login]:
                yield self.lines[lin]
        return

    def lines_of_grp(self, grp, seq):
        if grp == '':
            return # Do not auto compute ABINJ??? if there is no real groups
        grp_col = self.columns.get_grp()
        seq_col = self.columns.get_seq()
        if grp_col and seq_col:
            for line in self.lines.values():
                if line[grp_col].value == grp and line[seq_col].value == seq:
                    yield line

    def get_items(self, login):
        login = utilities.the_login(login)
        if login in self.the_key_dict:
            for lin in self.the_key_dict[login]:
                yield lin, self.lines[lin]
        return
    
    def authors(self):
        """List of all the logins that have modified a cell value"""
        a = {}
        for v in self.lines.values():
            for cell in v:
                if cell.author not in ('', data.ro_user, data.no_user):
                    a[cell.author] = True
        return tuple(a)

    def update_columns(self, columns, ro_page=None):
        """Update the default columns of the table.
        This can be called by the TEMPLATE 'check' method
        """
        if not self.modifiable:
            return
        if ro_page is None:
            ro_page = self.pages[0]
        locked = self.the_lock.locked()
        try:
            if not locked:
                self.lock()
            for col in sorted(columns):
                for attr, value in columns[col].items():
                    value = str(value)
                    a_column = self.columns.from_id(col)
                    if a_column is None or value!= str(getattr(a_column, attr)):
                        self.column_attr(ro_page, col, attr, value)
        finally:
            if not locked:
                self.unlock()

    def content(self, page):
        warn('%s content for page %d' % (
            self.filename, page.page_id))
        s = []

        s.append(self.content_head(page))

        try:
            s.append('  <script><!--')
            s.append(utilities.wait_scripts())
            s.append('var page_index = %d ;' % page.index)
            s.append('--></script> ')
            lines = self.lines.js()
            i = 0
            nb = 100
            to_load = len(lines)
            while lines:
                s.append('<script><!--')
                s.append('\n'.join(lines[:nb]))
                del lines[:nb]
                i += nb
                s.append('--></script><div class="loading_bar"><div style="width:%d%%">&nbsp;</div></div>'
                         % int(i*100./to_load) )
            s.append('  <style>DIV.loading_bar { display: none;}</style>')
            s.append('<style id="template_style">'
                     + self.template.css + '</style>')
            s.append('''  <script><!--
            function initialize()
            {
            if ( ! wait_scripts("initialize()") )
               return ;
            var t = document.getElementsByTagName("DIV");
            for(var i=0; i<t.length; i++)
                if ( t[i].className == "loading_bar" )
                    t[i].parentNode.removeChild(t[i]) ;
            document.write(head_html()) ;
            insert_middle();
            ''')
            if page.user_name in self.masters:
                hide = None
            else:
                hide = False
            s.append(self.columns.js(hide=hide))

            s.append('document.write(tail_html());')
            s.append('runlog(columns, lines) ;')
            s.append('set_updating(%s) ;' % int(self in update_students))
            s.append('}')
            if self.new_abjs:
                s.append(self.new_abjs)
            s.append(self.template.content(self))
            s.append('initialize();')
            s.append('--></script>  \n')
        finally:
            pass

        try:
            return '\n'.join(s)
        except UnicodeDecodeError:
            utilities.send_backtrace('\n'.join(repr(i)
                                               for i in s),
                                     "UNICODE PROBLEM")
            raise

    def location(self):
        return '%d %s %s' % (self.year, self.semester, self.ue)

    def rewrite(self, only_columns=False, user_name=''):
        s = ['# -*- coding: utf8 -*-']
        s.append('from data import *')
        s.append("new_page('' ,'" + data.ro_user + "', '', '')")
        pages = collections.defaultdict(lambda: 1)
        pages[data.ro_user] = 0
        if user_name:
            s.append("new_page('' ,'%s', '', '')" % user_name)
        else:
            authors = set()
            for c in self.columns:
                authors.add(c.author)
            for line in self.lines.values():
                for cell in line:
                    authors.add(cell.author)
            authors.discard(data.ro_user)
            for author in authors:
                pages[author] = len(pages)
                s.append("new_page('' ,'%s', '', '')" % author)
            
        for c in self.columns:
            for attr in column.ColumnAttr.attrs.values():
                if attr.name == 'author':
                    continue
                attr_value = attr.decode(getattr(c, attr.name))
                if attr_value != attr.default_value:
                    s.append('column_attr(%s,%d,%s,%s)' % (
                        repr(attr.name), pages[c.author],
                        repr(c.the_id), repr(attr_value)))
                         
        for attr in column.TableAttr.attrs.values():
            if attr.computed:
                continue
            if attr.name in ('modifiable', 'dates'):
                continue
            attr_value = getattr(self, attr.name)
            if attr.name == 'masters':
                if user_name not in attr_value:
                    attr_value.append(user_name)
                if '' in attr_value:
                    attr_value.remove('')
            attr_value = attr.decode(attr_value)
            if attr_value != attr.default_value:
                s.append('table_attr(%s,0,%s)' % (
                    repr(attr.name),
                    repr(attr_value)))

        if only_columns:
            return '\n'.join(s) + '\n'
                         
        for line_key, line in self.lines.items():
            for col, cell in zip(self.columns, line):
                if cell.value != '':
                    s.append('cell_change(%d,%s,%s,%s,%s)' % (
                            pages[cell.author],
                            repr(col.the_id),
                            repr(line_key),
                            repr(cell.value),
                            repr(cell.date),
                            ))
                    if cell.comment:
                        s.append('comment_change(%d,%s,%s,%s)' % (
                                pages[cell.author],
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

    def do_not_unload_add(self, value):
        if value:
            self.do_not_unload.append(value)
    def do_not_unload_remove(self, value):
        self.do_not_unload.remove(value)

    def unload(self, force=False):
        if force:
            self.close_active_pages()
            self.do_not_unload = []
        if '*' in ''.join(self.do_not_unload):
            return
        warn(str(self.ue), what="table")

        # XXX
        # In rare cases the table is unloaded while the student list
        # is being updated. So we finish with a table half updated
        # But it is not important.
        deleted = tables_manage("del", self.year, self.semester, self.ue)
        try:
            if deleted:
                update_students.remove(self) # No update student list.
        except ValueError:
            pass

        return deleted

    def delete(self):
        warn(str(self.ue), what="table")
        utilities.manage_key('CLOSED', self.ue, separation=5,
                             content='%d/deleted_table_%s' % (self.year,
                                                              self.semester)
                             )
        self.unload(force=True)
        if not self.unloaded:
            return
        # XXX Not locked, so the table may be reloaded before deletion....
        utilities.unlink_safe(self.filename)

        for name in self.masters:
            self.master_of_update('-', name)
        for login in self.the_keys():
            indexes_to_update.append((self, login, ''))
            for y, s in self.extensions:
                indexes_to_update_append(y, s, self.ue, login, '')

        def remove_bookmarks():
            import glob
            bookmark = (self.year, self.semester, self.ue)
            for filename in glob.glob(os.path.join(configuration.db, 'LOGINS',
                                                   '*', '*', 'bookmarked')):
                login = filename.split(os.path.sep)[-2]
                key = os.path.join(login, 'bookmarked')
                bookmarked = eval(utilities.manage_key('LOGINS', key))
                if bookmark in bookmarked:
                    bookmarked.remove(bookmark)
                    utilities.manage_key(
                        'LOGINS', key,
                        content = utilities.stable_repr(bookmarked))
                    warn('Remove %s bookmark for %s' % (bookmark, login))
            warn("Remove bookmarks done")
        utilities.start_new_thread(remove_bookmarks, ())            

    def send_alert(self, text):
        self.send_update(None, '<script>alert(_("ALERT_message_for")+%s);</script>\n' %
                         js(self.ue + '\n\n' + text))

    def __str__(self):
        return '%d/%s/%s' % (self.year, self.semester, self.ue)

    def backtrace_html(self):
        return "Table: " + str(self)

    def readable_by(self, the_ticket):
        if the_ticket.user_name in self.masters:
            return True
        if the_ticket.user_name in self.teachers:
            return True
        if the_ticket.user_name in self.managers:
            return True
        if the_ticket.user_name in configuration.root:
            return True
        if self.private:
            warn('Unauthorized access (private)', what='table')
            return False
        if self.teachers:
            warn('Unauthorized access (not teacher)', what='table')
            return False
        return True

    def master_of_update(self, what, name):
        if self.semester in configuration.master_of_exceptions:
            return
        d = utilities.manage_key('LOGINS', os.path.join(name, 'master_of'))
        if d is False:
            d = []
        else:
            d = eval(d)

        t = (str(self.year), self.semester, self.ue)
        if (t in d) and what == '-':
            d.remove(t)
        elif (t not in d) and what == '+':
            d.append(t)
        else:
            return

        utilities.manage_key('LOGINS', os.path.join(name, 'master_of'),
                             content = utilities.stable_repr(d))

    def the_abjs(self):
        from . import abj

        grp_col = self.columns.get_grp()
        seq_col = self.columns.get_seq()
        t = []
        for login in self.logins():
            tt = abj.tierstemps(login)
            student = abj.Abj(self.year, self.semester, login)
            line = list(self.get_lines(login))
            if line:
                line = line[0]
                the_abjs= abj.do_prune(
                    student.abjs,
                    self.dates[0], self.dates[1]+86400,
                    grp_col and line[grp_col].value or '',
                    seq_col and line[seq_col].value or '',
                    self.ue)
            else:
                the_abjs = ()
            da = student.da
            if tt or the_abjs or da:
                t.append("%s:[[%s],[%s],%s]" % (
                    js(login),
                    ','.join(['[%s,%s,%s]' % (js(a),js(b),js(d))
                              for a,b,dummy_c,d in the_abjs]),
                    ','.join(['[%s,%s,%s]' % (js(a),js(b),js(d))
                              for a,b,dummy_c,d in da]),
                    js(tt)))

        self.new_abjs = 'change_abjs({%s});\n' % ',\n'.join(t)
        return self.new_abjs

    def update_the_abjs(self):
        old_abjs = self.new_abjs
        if self.the_abjs() != old_abjs:
            self.send_update(None,'<script>' + self.new_abjs + '</script>')

    def retrieve_student_list(self):
        """This function allows to call old code in order
        to upgrade TOMUSS without having to update customized code.
        """
        return retrieve_student_list(self.ue_code,
                                     self.year, self.semester, self)

def get_cell_from_table_ro(server, allowed_types=None):
    """server.the_path must starts by 'col_id/lin_id'
    Return an error string or the tuple (table, column, lin_id)
    """
    t = table(server.the_year, server.the_semester,
              server.the_ue, create=False)
    if not t:
        return "Can't find table"
    col_id = server.the_path[0]
    lin = server.the_path[1]
    column = t.columns.from_id(col_id)
    if not column:
        return "Can't find column"
    if allowed_types  and  column.type.name not in allowed_types:
        return "Not an %s column type" % allowed_types
    if (not server.ticket.is_a_teacher
        and t.the_keys()[server.ticket.user_name][0] != lin):
        return 'Your are not allowed to read/modify this value'
    return t, column, lin

def get_cell_from_table(server, allowed_types=None):
    """server.the_path must starts by 'col_id/lin_id'
    Return an error string or the tuple (table, page, column, lin_id)
    Once the cell value is modified, call:
         table.do_not_unload_remove('cell_change')
    """
    err = get_cell_from_table_ro(server, allowed_types)
    if isinstance(err, str):
        return err
    t, column, lin = err
    if not column.is_modifiable(server.ticket.is_a_teacher,
                                server.ticket,
                                t.lines[lin][column.data_col]):
        return server._("ERROR_value_not_modifiable")

    if not t.authorized(server.ticket.user_name,
                        t.lines[lin][column.data_col],
                        column):
        return server._("ERROR_value_not_modifiable")

    t, page = table(server.the_year, server.the_semester,
                    server.the_ue, None, server.ticket,
                    do_not_unload='cell_change')

    if t is None:
        return server._("MSG_bad_ticket")

    return t, page, column, lin

def retrieve_student_list(ue, year=None, semester=None, table=None):
    args = inspect.getargspec(inscrits.L_batch.students).args
    options = {}
    if year is None:
        year, semester = configuration.year_semester
    if 'year' in args and 'semester' in args:
        options['year'] = year
        options['semester'] = semester
    if table and 'table' in args:
        options['table'] = table
    try:
        return inscrits.L_batch.students(ue, **options)
    except:
        utilities.send_backtrace("", "Can't get student list for %s %s %s"
                                 % (year, semester, ue))
        return ()
    
def send_alert(text):
    for atable in tables_values():
        atable.send_alert(text)

@utilities.add_a_lock
def tables_manage(action, year, semester, ue, do_not_unload=0, new_table=None):
    if action == 'get':
        try:
            t = tables[year, semester, ue]
            if t and do_not_unload:
                t.do_not_unload_add(do_not_unload)
            return t
        except KeyError:
            tables[year, semester, ue] = None
            return False
    elif action == 'del':
        try:
            t = tables[year, semester, ue]
            if not t:
                return # Yet destroyed
            if t.do_not_unload:
                warn('Unload of do_not_unload: '
                     + str(t.ue) + repr(t.do_not_unload), what="warning")
                return False
            if t.active_pages:
                warn('Unload with active pages.', what="warning")
                return False
            # write access to the table will make an error.
            t.unloaded = True

            # A loop because extended table have multiple keys
            for k, v in list(tables.items()):
                if v is t:
                    del tables[k]
            return True
        except KeyError:
            return # Yet destroyed
    elif action == 'replace':
        old = tables.get((year, semester, ue), None)
        tables[year, semester, ue] = new_table
        return new_table
    else:
        raise ValueError("Unknown action '%s'" % action)

def tables_values():
    # Use list because the tables may change while creating the list.
    # Do not use a tuple because it must be sortable
    # XXX Need a lock ?
    return [t
            for k, t in tuple(tables.items())
            if t not in (None, False, True)
            and k == (t.year, t.semester, t.ue)
            ]

def table(year, semester, ue, page=None, ticket=None, ro=False, create=True,
          do_not_unload=0):
    """With a ticket : return table and page
    Without ticket : return only the table
    """
    # utilities.warn('%s/%s/%s page=%s ticket=%s ro=%s create=%s' % (
    #    year, semester, ue, page, ticket, ro, create))
    if configuration.read_only:
        ro = True
    year = int(year)
    t = tables_manage('get', year, semester, ue, do_not_unload)
    if t is None:
        # Somebody else is creating the table
        while t is None:
            time.sleep(0.1)
            t = tables_manage('get', year, semester, ue, do_not_unload)

    if t is False:
        # I must create the table
        # Only one thread can be here at the same time.
        try:
            filename = table_filename(year, semester, ue)
            if os.path.islink(filename):
                y, s, u = link_to(filename)
                t = table(y, s, u, page=page, ticket=ticket, ro=ro,
                          create=create, do_not_unload=do_not_unload)
                if (y, s, u) in tables:
                    tables[year, semester, ue] = tables[y, s, u]
                else:
                    del tables[year, semester, ue]
                return t
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
            # tables[year, semester, ue] = False
            # raise
            utilities.send_backtrace("", "Can't load %s/%s/%s" % (
                    year, semester, ue))
            # tables[year, semester, ue] contains None
            # So no need to call table_manage
            del tables[year, semester, ue]
            if ticket:
                return None, None
            else:
                return None
        t.do_not_unload_add(do_not_unload) # Only on this case
        tables[year, semester, ue] = t
    else:
        # Table yet loaded
        t = t.update()

    t.atime = time.time()

    if page is not None and not t.modifiable and page >= len(t.pages):
        # Bug raised by TOMUSS restart (page list is lost)
        # XXX : if 2 users are on the same unmodifiable table,
        # then there is 50% chance that the second one is
        # with the bad page and so the bad ticket.
        # It will be accused of hacking.
        page = None

    if page == None:
        if ticket == None:
            return t
        if not t.readable_by(ticket):
            try:
                t.do_not_unload_remove('new_page')
            except ValueError:
                pass
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

    page = t.pages[page]
    page.check_identity(ticket.ticket, ticket.user_name,
                        ticket.user_ip, ticket.user_browser)
    return t, page


def remove_unused_tables():
    """Do not call from a thread"""
    warn('start', what="table")
    now = time.time()
    for atable in tables_values():
        if atable.active_pages:
            continue
        if now - atable.atime < configuration.unload_interval:
            continue
        atable.unload()
            
    warn('stop', what="table")

# continuous update of students lists for all tables
def check_students_in_tables():
    while True:
        time.sleep(configuration.students_check_interval)
        for t in tables_values():
            update_students.append(t)
            time.sleep(0.1) # Avoid overload

# continuous update of students lists
update_students = []

@utilities.add_a_lock # The lock is here for regression tests
def check_new_students_real():
    try:
        while update_students:
            t = update_students.pop()
            t.do_not_unload_add('check_new_students_real')
            # XXX Not a good test, but a lock is overkill
            if t.unloaded:
                continue
            try:
                utilities.important_job_add('check_new_students_real')
                t.send_update(None, "<script>set_updating(1);</script>")
                utilities.bufferize_this_file(t.filename)
                warn('start update students of %s' % t.ue, what="table")

                try:
                    t.template.check(t)
                except UserWarning:
                    pass
                except:
                    utilities.send_backtrace('', 'Student list %s' % t)

                warn('done %s' % t.ue, what="table")
                mails = inscrits.L_batch.mails(tuple(t.logins()) + t.authors())
                mails.update(t.mails)
                t.change_mails(mails)
                if t.modifiable:
                    if t.force_update or getattr(t, 'update_inscrits', True):
                        for a_column in t.columns:
                            if not a_column.locked:
                                a_column.type.update_all(t, a_column)
                    t.force_update = 0
                t.update_the_abjs()
            finally:
                utilities.important_job_remove('check_new_students_real')
                t.do_not_unload_remove('check_new_students_real')
                utilities.bufferize_this_file(None)
                t.send_update(None, "<script>set_updating(0);</script>")
            
    except IndexError:
        if not configuration.regtest:
            raise # Real problem
        # XXX The regtest raise a bug, why ?

indexes_to_update = []

def update_index(login, action=None):
    if not login:
        return
    if utilities.safe(login) != login:
        return
    c = utilities.manage_key('LOGINS', os.path.join(login, 'index'))
    if c:
        c = eval(c)
    else:
        c = []
    if action is None:
        return c
    c = action(c) # Update index content
    utilities.manage_key('LOGINS', os.path.join(login, 'index'),
                         content = utilities.stable_repr(c))

def indexes_to_update_append(the_year, the_semester, the_ue, old, new):
    class X:
        year = the_year
        semester = the_semester
        ue = the_ue
    indexes_to_update.append((X, old, new))

def check_indexes_to_update():
    while indexes_to_update:
        tabl, old, new = indexes_to_update.pop(0)
        def remove(x):
            try:
                x.remove((tabl.year, tabl.semester, tabl.ue))
            except ValueError:
                pass
            return x
        def append(x):
            x.append((tabl.year, tabl.semester, tabl.ue))
            return x
        update_index(old, remove)
        update_index(new, append)

def update_indexes(year, semester, ue):
    the_table = table(year, semester, ue)
    for login in the_table.logins_valid():
        indexes_to_update.append((the_table, '', utilities.the_login(login)))

def check_new_students():
    while True:
        if configuration.regtest_sync:
            time.sleep(0.01)
        else:
            time.sleep(1)

        check_indexes_to_update()
        check_new_students_real()

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
            s.append('[' + utilities.js(lo)
                     + ',' + utilities.js(surname.upper())
                     + ',' + utilities.js(firstname.title())
                     + ',' + utilities.js(cn)
                     + ']')
    else:
        s = []
    s = '<script>login_list(' + utilities.js(name) + \
        ',[' + ',\n'.join(s) + ']);</script>\n'
    sender.append(page.browser_file, s)
            

# Do the real job to answer to modification requests
# It is complicated because we may receive request in bad order.
# So we keep a list of requests and sort it.

def it_is_a_bad_request(request, page, tabl, output_file):
    if page.request > request:
        # An old request was given. Assume same answer XXX
        try:
            tabl.do_not_unload_remove('page_action')
        except:
            # May be raised by template reloading: forgot request
            utilities.send_backtrace("do_not_unload_remove failed")
        try:
            warn('Old request asked : %d in place of %d' % (
                request, page.request))
            output_file.write(files.files['ok.png'].bytes())
            output_file.close()
            sender.append(page.browser_file,
                          '<script>saved(%d);</script>\n' % request,
                          index=len(tabl.sent_to_browsers), page=page)
        except IOError:
            pass
        except:
            utilities.send_backtrace('Exception request %d' % request)
        return True
    if tabl.unloaded:
        # No sense to do the do_not_unload_add(-1)
        utilities.send_backtrace('Request on unloaded table ' + tabl.ue,
                                 exception=False)
        return True

def should_be_delayed(request, page, tabl):
    if tabl.the_lock.locked():
        return True
    if page.request < request:
        return True

def process_request(page, tabl, action, path):
    page.request += 1
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
            tabl.force_update = 1
            page.answer = 'ok.png'
        else:
            warn('BUG: %s' % str(path), what="error")
    finally:
        tabl.do_not_unload_remove('page_action')
        tabl.unlock()
    # We don't want asynchronous update when doing regtest
    if configuration.regtest_sync:
        update_students.append(tabl)
        check_new_students_real()


request_list = []
def check_requests():
    while True:
        time.sleep(0.1)
        my_request_list = list(request_list)
        if len(my_request_list) == 0:
            # To not flush buffers of currently student list updates
            # In fact the buffering only gain 10% in user time and is
            # a little less secure. So it is disabled (see YYY comments)
            continue
        my_request_list.sort(key=lambda x: (x[0], x[1]))
        to_discard = set()
        for r in my_request_list:
            page_id, request, page, action, path, output_file = r
            tabl = page.table
            warn('R=%d P=%d A=%s P=%s DNU=%s' % (
                    request, page_id, action, path, tabl.do_not_unload),
                 what="DNU")
            if it_is_a_bad_request(request, page, tabl, output_file):
                request_list.remove(r)
                continue
            # utilities.bufferize_this_file(tabl.filename) # YYY
            # It is only useful to compare to previous requests
            if should_be_delayed(request, page, tabl):
                if (time.time()
                    - page.last_request) > configuration.pending_request_TTL:
                    to_discard.add(page)
                # do not decrement do_not_unload
                # Keep in request_list
                continue
            # Remove from request list.
            # If there is an error, browser will send a new request
            request_list.remove(r)
            try:
                real_bug = True
                process_request(page, tabl, action, path)
            except:
                warn('bug raised', what="error")
                utilities.send_backtrace('check_requests: '+action+repr(path))
                page.answer = 'bug.png'
                real_bug = False

            check_requests.the_lock.acquire()
            if not request_list:
                utilities.important_job_remove('request')
            check_requests.the_lock.release()

            try:
                warn('Send %s(%s) %s %s' % (output_file, output_file.closed,
                                            page.answer, page.browser_file),
                     what="table")
                if not output_file.closed:
                    output_file.write(files.files[page.answer].bytes())
                    output_file.close()
                sender.append(page.browser_file,
                              '<script>saved(%d);</script>\n' % request,
                              index=len(tabl.sent_to_browsers), page=page)
                if page.answer == 'bug.png' and real_bug:
                    sender.append(page.browser_file,
                                  '<script>Alert("ERROR_server_bug");</script>')
            except socket.error:
                pass

        # Old requests without an answer: forget them
        for page_to_discard in to_discard:
            s = []
            for r in tuple(request_list):
                page_id, request, page, action, path, output_file = r
                if page is not page_to_discard:
                    continue
                request_list.remove(r)
                page.table.do_not_unload_remove('page_action')

                if action == 'cell_change':
                    col = page.table.columns.from_id(path[0])
                    if not col:
                        continue
                    line = page.table.lines[path[1]]
                    old_value = line[col.data_col].value
                    if str(old_value).rstrip("0.") != path[2].rstrip('.0'):
                        s.append('[%s] %s %s %s %s current:%s unsaved:%s\n'
                                 % (request, line[0].value, line[1].value,
                                    line[2].value, col.title,
                                    old_value, path[2]))
                else:
                    s.append("[%s] %s %s\n" % (request, action, path))
            if s:
                s = ["Verify if these values really need to be saved\n\n",
                     "Page: ", str(page_to_discard), "\n\n",
                     "No more browser requests since %s seconds"
                     % configuration.pending_request_TTL,
                    '\n\n',
                     "Erased requests :\n"
                 ] + s
                utilities.send_mail_in_background(
                    configuration.maintainer,
                    "TOMUSS: Erase old pending requests",
                    ''.join(s),
                    show_to=True)

        # utilities.bufferize_this_file(None) # YYY Flush buffers
                           
check_requests.the_lock = threading.Lock()
        

# continuous send of packets to check connections
from . import ticket
def check_down_connections():
    while True:
        # This is done here, because testing this once per minute is fine.
        # Force rewrite of modified files in TMP/version/file
        # These files can be used by a static file server
        for f in files.files.values():
            if 'image' not in f.mimetype:
                try:
                    str(f)
                except :
                    pass
            else :
                try:
                    f.bytes()
                except OSError:
                    pass

        time.sleep(configuration.check_down_connections_interval)
        for ttable in tables_values():
            ttable.send_update(None, '<script>connected();</script>',
                               store=False)
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
            # Update mail if new teacher
            login = the_table.lines[lin][a_column.data_col].author
            if login not in the_table.mails:
                m = inscrits.L_fast.mail(login)
                if m:
                    the_table.update_mail(login, m)
            # Update mail if login changed
            if a_column.data_col == 0:
                login = the_table.lines[lin][0].value
                if isinstance(login, str):
                    m = inscrits.L_fast.mail(login)
                    if m:
                        the_table.update_mail(login, m)

column_changed_list = []

def update_computed_values_slow():
    while True:
        time.sleep(0.1)
        while column_changed_list:
            the_table, a_column, attr = column_changed_list.pop()
            a_column.type.update_all(the_table, a_column, attr)
            for col in the_table.columns.use(a_column):
                col.type.update_all(the_table, col)

def virtual_table(server, the_columns, the_lines, table_attrs={}, js="",css=""):
    """Send the table to the browser without storage.
    Do not use in a not threaded plugin.
    """
    if not hasattr(server, "year"):
        server.year = server.__dict__.get("the_year", 0)
    if not hasattr(server, "semester"):
        if hasattr(server, 'the_semester'):
            server.semester = server.the_semester
        else:
            server.semester = "?"
    for i, a_column in enumerate(the_columns):
        if not a_column.position:
            a_column.position = i
    class TMP:
        pass
    tmp = TMP()
    tmp.__dict__ = table_attrs
    
    server.the_file.write(table_head(server.year,
                                     server.semester,
                                     server.ticket.ticket,
                                     create_pref = False,
                                     attrs_from=tmp,
                                     user_name=server.ticket.user_name
                                     )
                          )
    lines = []
    for i, line in enumerate(the_lines):
        lines.append('"%d": %s' % (i, line.js()))
    lines = '{' + ',\n'.join(lines) + '}'
    columns = '[' + ',\n'.join([the_column.js(hide=False)
                                for the_column in the_columns]) + ']'
    server.the_file.write("""
    <style>%s</style>
    <script>
    %s
    %s
    function initialize()
    {
    if ( ! wait_scripts("initialize()") )
               return ;
    document.write(head_html()) ;
    insert_middle();
    columns = %s ;
    lines = %s ;
    document.write(tail_html()) ;
    table_attr.table_title = %s ;
    runlog(columns, lines) ;
    }
    initialize() ;
    </script>
    """ % (css, utilities.wait_scripts(),
           js, columns, lines, utilities.js(repr(server.the_path)) ))

    logins = list(line[0].value
                  for line in the_lines
                  if line[0].value
                  )
    mails = inscrits.L_batch.mails(logins)
    server.the_file.write("<script>Xtable_attr('mails',%s);</script>\n"
                          % utilities.js(mails))
       
def start_threads():
    utilities.start_new_thread_immortal(check_new_students, ())
    utilities.start_new_thread_immortal(check_students_in_tables, ())
    utilities.start_new_thread_immortal(check_requests, ())
    utilities.start_new_thread_immortal(check_down_connections, ())
    utilities.start_new_thread_immortal(update_computed_values_fast, ())
    utilities.start_new_thread_immortal(update_computed_values_slow, ())

