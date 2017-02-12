#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2009-2013 Thierry EXCOFFIER, Universite Claude Bernard
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

import ast
from .. import utilities
from .. import configuration
from .. import sender
from .. import files

def create(table):
    utilities.warn('Creation')
    if table.year != 0 or table.semester != 'Dossiers':
        raise ValueError('Not allowed')
    p = table.get_ro_page()
    _ = utilities._
    table.table_attr(p, 'masters', list(configuration.root))
    table.column_change(p,'0_0',_("COL_TITLE_ct_variable"),'Text','','','F',0,2)
    table.column_change(p,'0_1',_("COL_TITLE_ct_what")  ,'Text','','','F',0,10)
    table.column_change(p,'0_2',_("COL_TITLE_ct_value") ,'Text','','','F',0,10 )
    table.table_attr(p, 'default_nr_columns', 3)
    table.table_attr(p, 'default_sort_column', 1)
    table.get_a_root_page()

variable_list = [
    'abinj',
    "do_not_display",
    'message',
    "year_semester",
    "year_semester_next",
    "ue_not_per_semester",
    "master_of_exceptions",
    "allow_student_list_update",
    "allow_student_removal",
    'maintainer',
    'smtpserver',
    'abj_sender',
    'ldap_server',
    'ldap_server_login',
    "ldap_server_password",
    "ldap_server_port",
    "ldap_encoding",
    "attr_login",
    "attr_login_alt",
    "attr_mail",
    "attr_surname",
    "attr_firstname",
    "attr_default_password",
    "ou_top",
    "ou_students",
    "cn_students",
    "cn_teachers",
    "ou_groups",
    "ou_ue_contains",
    "ou_ue_starts",
    "ou_ue_starts2",
    "ou_portail_contains",
    "banned_ip",
    "root",
    "teachers",
    "teacher_if_login_contains" ,
    "administratives",
    "abj_masters",
    "referents",
    "invited_teachers",
    "invited_administratives",
    "invited_abj_masters",
    'students_check_interval',
    'maximum_out_of_date',
    'maxage',
    'ldap_reconnect',
    "ticket_time_to_live",
    "unload_interval",
    "check_down_connections_interval",
    "not_teachers",
    "login_not_teacher",
    "logo",
    "suivi_display_more_ue",
    "language",
    "suivi_student_message",
    "tt_masters",
    "year_semester_modifiable",
    "year_semester_update_student_list",
    "suivi_student_allow_private",
    "max_visibility_date",
    "gui_record",
    "time_between_mails",
    "grp_modifiable",
    "advertising",
    "removal_allowed",
    "upload_max",
    "single_logout",
    "authenticate_iframe",
    "special_days",
    "allowed_grades",
    ]

deprecated = set(('root', 'invited_teachers', 'invited_administratives',
                  'invited_abj_masters', 'tt_masters', 'teachers',
                  'administratives', 'abj_masters',
                  'referents'))

variables = {}

def check(table):
    utilities.warn('Check')
    p_ro = table.pages[0]
    p_rw = table.pages[1]

    table.lock()
    try:
        for variable, comment in variables.items():
            if variable not in table.lines:
                if variable in deprecated:
                    continue
                else:
                    # Do not change user entered value
                    # Do not change default value after the first time.
                    v = configuration.__dict__[variable]
                    if isinstance(v, list) or isinstance(v, tuple):
                        if len(v) == 0:
                            v = '()'
                        else:
                            v = '('+','.join([utilities.js(i) for i in v])+',)'
                    elif isinstance(v, (bool, dict)):
                        v = repr(v)
                    table.cell_change(p_ro,'0_0', variable,variable)
                    table.cell_change(p_rw, '0_2', variable, v)
            if variable in deprecated and variable in table.lines:
                table.cell_change(p_ro, '0_1', variable,
                                  utilities._("COL_TITLE_ct_deprecated"))
            else:
                table.cell_change(p_ro, '0_1', variable, comment)
    finally:
        table.unlock()

def set_value(variable, value):
    current = configuration.__dict__[variable]

    if isinstance(current, tuple) or isinstance(current, list) \
             or isinstance(current, bool) or isinstance(current, dict):
        if configuration.regtest:
            import re
            try:
                # Forbidden: function calls and item access
                if re.match(r".*.[[(].*",value):
                    utilities.warn('Possible Hacking:' + value, what='error')
                    return
            except TypeError:
                pass
        value = ast.literal_eval(value)
        if not isinstance(value, type(current)):
            utilities.warn("VARIABLE=%s CURRENT=%s NEW=%s" %
                 (variable, current, value), what="error")
            raise ValueError("Big issue")
    elif isinstance(current, float):
        value = float(value)
    elif isinstance(current, int):
        value = int(value)
    configuration.__dict__[variable] = value
    if variable == 'logo':
        files.files['style.css'].replace("config_table", '_LOGO_', value)
    if variable == 'maintainer':
        files.files['doc_table.html'].replace('config_table', '_ADMIN_', value)

def init(table):
    table.do_not_unload_add('*config_table')

    for v in variable_list:
        variables[v] = utilities._("config_table_" + v)
    variables.update(configuration.local_options)
    
def onload(table):
    """Copy table content into configuration"""

    if len(table.lines) == 0:
        return
    utilities.warn('Onload')
    for variable in variables:
        if variable in table.lines: # do not create it by reading it
            set_value(variable, table.lines[variable][2].value)


def cell_change(dummy_table, page, col, lin, value, dummy_date):
    if page.page_id <= 1:
        return
    if col != '0_2':
        return
    try:
        a = set_value(lin, value)
        if a is not None:
            sender.append(page.browser_file,
                          '<script>alert("Eval:\\n"+%s);</script>' %
                          utilities.js(a))
    except:
        import sys
        sender.append(page.browser_file,
                      '<script>alert(%s);</script>' %
                      utilities.js(str(sys.exc_info()[0])))
        raise

    tell_to_reload_config()

def tell_to_reload_config():
    configuration.config_acls_clear_cache()    
    utilities.start_new_thread(tell_reload_config, ())

configuration.tell_to_reload_config = tell_to_reload_config
    
def tell_reload_config():
    import urllib.request, urllib.error, urllib.parse
    import random
    import os

    utilities.warn('Tell "suivi" to reload config')
    i = str(random.randrange(1000000000))
    utilities.write_file(os.path.join('TMP', 'xxx.load_config'), i)
    for url, port, year, semester, host in configuration.suivi.servers():
        try:
            utilities.read_url(url + '/load_config/' + i)
        except urllib.error.URLError:
            pass # If one 'suivi' server is not running, continue
        
