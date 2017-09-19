#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2009-2015 Thierry EXCOFFIER, Universite Claude Bernard
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
#    Contact: Thierry.EXCOFFIER@univ-lyon1.fr

import ast
import sys
import os
import shutil
import http.client
import time
import json
import traceback

sys.argv.append("real_regtest")
sys.argv.append("protect_do_not_display")

import tests_config
tests_config.init(time.localtime()[0])

import tomuss_init
from .. import configuration
from .. import utilities
from .server import Server, ServerSuivi, check
sys.argv.remove("real_regtest")
sys.argv.remove("protect_do_not_display")

configuration.do_not_display = ('debug', 'auth', 'table', 'ldap', 'plugin',
                                'check', 'lang', 'DNU', 'info')

configuration.regtest = True

root     = configuration.root[0]
abj      = configuration.invited_abj_masters[1]
invited  = configuration.invited_teachers[0]
assert( root != abj )



configuration.language = 'en'

ok_png = utilities.read_file('FILES/ok.png','bytes')
bad_png = utilities.read_file('FILES/bad.png','bytes')
bug_png = utilities.read_file('FILES/bug.png','bytes')
unauthorized_html = utilities._("MSG_new_page_unauthorized")
not_in_demo_mode = utilities._("MSG_evaluate")
deletion_done = utilities._("MSG_delete_this_table_done")

year = configuration.year_semester[0]
semester = configuration.year_semester[1]
uyear = utilities.university_year()
ys = '%d/%s' % (year, semester)
ys_old = '%d/%s' % (year-1, semester)

abj_date_old      = '1/1/%d' % (uyear-2)
abj_date_previous = '1/1/%d' % (uyear-1)
abj_date_current  = '1/1/%d' % (uyear)
abj_date_next     = '31/12/%d' % (uyear+1)

now_plus_32_days = time.strftime('%Y%m%d',time.localtime(time.time()+86400*63))
now_plus_30_days = time.strftime('%Y%m%d',time.localtime(time.time()+86400*30))

print(ys, uyear)

_ = utilities._


names = open('xxx.names','w', encoding = "utf-8")

def do(t):
    names.write(' ' + t)
    names.flush()
    c = len(sys.argv) == 1 or t in sys.argv or do.found
    if c:
        print(t)
        do.found = True
    return c
do.found = False

def save_sec():
    save_sec.time = int(time.time())
def wait_sec():
    while int(time.time()) == save_sec.time:
        time.sleep(0.1)

if len(sys.argv) == 1:
    print('You can indicate in parameters the tests you want to do')

c = ''
s = ''
ss = ''

done = {}

def create_tt():
    if 'create_tt' in done:
        return
    done['create_tt'] = True
    tt = '=' + abj + '/%d/Dossiers/tt' % uyear

    global c
    c = s.url(tt)
    assert_col({"the_id":"0_8","type":"Date","author":"*","position":3,
                "title":_("TH_begin"),"width":6}, c)

    c = s.url(tt + '/1/0/column_attr_title/col_0/COL_TITLE')
    assert( c == ok_png)
    c = s.url(tt + '/1/1/column_attr_comment/col_0/COL_COMMENT')
    assert( c == ok_png)
    c = s.url(tt + '/1/2/cell_change/0_0/0_0/10800000')
    assert( c == ok_png)
    c = s.url(tt + '/1/3/cell_change/col_0/0_0/CELL_VALUE')
    assert( c == ok_png)
    c = s.url(tt + '/1/4/comment_change/col_0/0_0/CELL_COMMENT')
    assert( c == ok_png)

def create_u2():
    if 'create_u2' in done:
        return
    done['create_u2'] = True

    global c

    c = s.url('=' + root + '/%s/UE-INF20UE2' % ys)
    time.sleep(1)
    c = s.url('=' + root + '/%s/UE-INF20UE2' % ys +
              '/1/0/column_attr_title/col_0/TITLE0')
    assert(c == ok_png)
    c = s.url('=' + root + '/%s/UE-INF20UE2' % ys +
              '/1/1/cell_change/col_0/0_0/11.11') # A note
    assert(c == ok_png)
    c = s.url('=' + root + '/%s/UE-INF20UE2' % ys +
              '/1/2/cell_change/0_0/0_0/10800000') # Student ID
    assert(c == bad_png)
    check('Y%d/S%s/UE-INF20UE2.py' % (year, semester),
          cell_required = (0,'0_5','0_0','ok'))

    # Add bad student
    c = s.url('=' + root + '/%s/UE-INF20UE2' % ys +
              '/1/3/cell_change/col_0/0_1/22.22') # A note
    assert(c == ok_png)
    c = s.url('=' + root + '/%s/UE-INF20UE2' % ys +
              '/1/4/cell_change/0_0/0_1/10800001') # Student ID
    assert(c == ok_png)
    check('Y%d/S%s/UE-INF20UE2.py' % (year, semester),
          cell_required = (0,'0_5','0_1','non'))

    # Add table comment
    c = s.url('=' + root + '/%s/UE-INF20UE2' % ys +
              '/1/5/table_attr_comment/_TABLE_COMMENT_')
    assert(c == ok_png)

    # Add a master
    c = s.url('=' + root + '/%s/UE-INF20UE2' % ys +
              '/1/6/table_attr_masters/ue1.master')
    assert(c == ok_png)

    # Verify number of loads
    c = utilities.manage_key('LOGINS', os.path.join(root, 'pages'))
    assert("'UE-INF20UE2':" in c)

def create_referents():
    if 'create_referents' in done:
        return
    done['create_referents'] = True
    global c
    c = s.url('=' + abj + '/%s/referents_students' % ys)
    c = s.url('=' + abj + '/%s/referents_students' % ys +
              '/2/0/cell_change/a/line_0/toto')
    assert(c == ok_png)
    c = s.url('=' + abj + '/%s/referents_students' % ys +
              '/2/1/cell_change/a/line_1/a_referent')
    assert(c == ok_png)

    # Create a column in referents table (a a line)
    c = s.url('=a_referent/referent_get/10900000')
    assert(_("MSG_referent_get_done") in c)
    assert('10900000' in c)
    
    c = s.url('=' + abj + '/%s/referents_students' % ys +
              '/2/2/cell_change/0/line_0/10800000')
    assert(c == ok_png)

def assert_col(attrs, lines, contains="", startswith="", endswith=""):
    s = []
    for line in lines.split('\n'):
        if 'Col(' in line:
            s.append(line)
        if '"the_id": "%s"' % attrs['the_id'] not in line:
            continue
        if contains not in line:
            continue
        if not line.startswith(startswith):
            continue
        if not line.endswith(endswith):
            continue
        for attr, value in attrs.items():
            assert('"%s": %s' % (attr, json.dumps(value)) in line)
        return True
    else:
        raise ValueError('c=%s s=%s e=%s\nNot found: %s\nIn :\n%s'
                         % (contains, startswith, endswith,
                            attrs, '\n'.join(s)))

def tests():
    global c, s, ss, done
    done = {}
    ss = ServerSuivi()
    s = Server()
    s.start()
    if do('badurl'):
        c = s.url('=' + root + '/BADURL')
        assert(c == 'bad_url')
        c = s.url('='+root+'/evaluate/5-2')
        assert(not_in_demo_mode in c)
    if do('homeroot'):
        c = s.url('=' + root)
        assert("javascript:go('clean')" in c)
    if do('homeabj'):
        c = s.url('=' + abj)
        assert("javascript:go('abj')" in c)
    if do('stat'):
        c = s.url('=' + root + '/stat')
        assert("<table border>" in c)
    if do('profiling'):
        c = s.url('=' + root + '/profiling/%d' % year )
        assert("initialize()" in c)
    if do('gc'):
        c = s.url('=' + root + '/gc')
        assert(not_in_demo_mode in c)

    if do('preferences'):
        c = s.url('=' + abj).split('preferences=')[-1]
        c = c.split(';')[0]
        assert('"language":"' in c)

        c = s.url('=' + abj + '/save_preferences/debug_home=1')
        assert(c == ok_png)

        c = utilities.read_file('DBregtest/LOGINS/%s/%s/preferences' % (
            abj[:3], abj))
        assert("{\n'debug_home':1,\n}" == c)

        c = s.url('=' + abj).split('HomePreferences')[1]
        assert('"debug_home": 1' in c)

    if do('emptydossier'):
        c = s.url('=' + abj + '/%d/Dossiers/emptydossier' % uyear)

        lines_id = []
        nr_columns = 0
        nr_pages = 2
        nr_cells = 0
        check('Y%d/SDossiers/emptydossier.py' % uyear,
              masters_expected = [abj], nr_pages = nr_pages,
              nr_columns = nr_columns, lines_id = lines_id,
              nr_cells = nr_cells,
              dump=False)

        # Create cell in non existent column
        c = s.url('='+abj+'/%d/Dossiers/emptydossier' % uyear +
                  '/1/0/cell_change/col_0/line_0/_VALUE_')
        assert(c == bug_png)
        check('Y%d/SDossiers/emptydossier.py' % uyear,
              masters_expected = [abj], nr_pages = nr_pages,
              nr_columns = nr_columns, lines_id = lines_id,
              nr_cells = nr_cells,
              dump=False)

        # Create column
        c = s.url('='+abj+'/%d/Dossiers/emptydossier' % uyear +
                  '/1/1/column_attr_title/col_0/TITLE0')
        assert(c == ok_png)
        nr_columns += 1
        check('Y%d/SDossiers/emptydossier.py' % uyear,
              masters_expected = [abj], nr_pages = nr_pages,
              nr_columns = nr_columns, lines_id = lines_id,
              nr_cells = nr_cells,
              column_required =('title', 1, 'col_0', 'TITLE0'),
              dump=False)

        # Create cell
        c = s.url('='+abj+'/%d/Dossiers/emptydossier' % uyear +
                  '/1/2/cell_change/col_0/line_0/_VALUE_')
        assert(c == ok_png)
        lines_id = ['line_0']
        nr_cells += 1
        check('Y%d/SDossiers/emptydossier.py' % uyear,
              masters_expected = [abj], nr_pages = nr_pages,
              nr_columns = nr_columns, lines_id = lines_id,
              nr_cells = nr_cells,
              cell_required = (1,'col_0','line_0','_VALUE_'),
              dump=False)

        # Change comment on cell
        c = s.url('='+abj+'/%d/Dossiers/emptydossier' % uyear +
                  '/1/3/comment_change/col_0/line_0/_COMMENT_')
        nr_cells += 1
        check('Y%d/SDossiers/emptydossier.py' % uyear,
              masters_expected = [abj], nr_pages = nr_pages,
              nr_columns = nr_columns, lines_id = lines_id,
              cell_required = (1,'col_0','line_0','_COMMENT_'),
              nr_cells = nr_cells,
              dump=False)

        # Change cell value
        c = s.url('='+abj+'/%d/Dossiers/emptydossier' % uyear +
                  '/1/4/cell_change/col_0/line_0/_VALUE_2_')
        assert(c == ok_png)
        lines_id = ['line_0']
        nr_cells += 1
        
        check('Y%d/SDossiers/emptydossier.py' % uyear,
              masters_expected = [abj], nr_pages = nr_pages,
              nr_columns = nr_columns, lines_id = lines_id,
              nr_cells = nr_cells,
              cell_required = (1,'col_0','line_0','_VALUE_2_'),
              dump=False)

        # Check HTML
        c = s.url('=' + abj + '/%d/Dossiers/emptydossier' % uyear)
        nr_pages += 1
        check('Y%d/SDossiers/emptydossier.py' % uyear,
              masters_expected = [abj], nr_pages = nr_pages,
              nr_columns = nr_columns, lines_id = lines_id,
              nr_cells = nr_cells,
              dump=False)
        assert_col({"the_id":"col_0","type":"Note","author":abj,
                   "position":0,"title":"TITLE0"}, c)
        assert('P("line_0",[C("_VALUE_2_","%s","' % abj in c)
        assert('","_COMMENT_","_VALUE_\\n(' in c) # History

    if do('badorder'):
        c = s.url('=' + abj + '/%d/Dossiers/badorder' % uyear)
        lines_id = []
        nr_columns = 0
        nr_pages = 2
        nr_cells = 0
        check('Y%d/SDossiers/badorder.py' % uyear,
              masters_expected = [abj], nr_pages = nr_pages,
              nr_columns = nr_columns, lines_id = lines_id,
              nr_cells = nr_cells,
              dump=False)

        # Create cell comment in non existent cell
        g = s.url('=' + abj + '/%d/Dossiers/badorder' % uyear +
                  '/1/2/comment_change/col_0/line_0/_COMMENT_',
                  returns_file=True)
        check('Y%d/SDossiers/badorder.py' % uyear,
              masters_expected = [abj], nr_pages = nr_pages,
              nr_columns = nr_columns, lines_id = lines_id,
              nr_cells = nr_cells,
              dump=False)

        # Create cell in non existent column
        f = s.url('=' + abj + '/%d/Dossiers/badorder' % uyear +
                  '/1/1/cell_change/col_0/line_0/_VALUE_', returns_file=True)
        check('Y%d/SDossiers/badorder.py' % uyear,
              masters_expected = [abj], nr_pages = nr_pages,
              nr_columns = nr_columns, lines_id = lines_id,
              nr_cells = nr_cells,
              dump=False)

        c = s.url('='+abj+'/%d/Dossiers/badorder' % uyear +
                  '/1/0/column_attr_title/col_0/TITLE0')
        assert(c == ok_png)
        assert(f.read() == ok_png)
        f.close()
        assert(g.read() == ok_png)
        g.close()
        
        lines_id = ['line_0']
        nr_cells += 2
        nr_columns += 1
        check('Y%d/SDossiers/badorder.py' % uyear,
              masters_expected = [abj], nr_pages = nr_pages,
              nr_columns = nr_columns, lines_id = lines_id,
              nr_cells = nr_cells,
              dump=False)
        
        # Check HTML
        c = s.url('=' + abj + '/%d/Dossiers/badorder' % uyear)
        nr_pages += 1
        check('Y%d/SDossiers/badorder.py' % uyear,
              masters_expected = [abj], nr_pages = nr_pages,
              nr_columns = nr_columns, lines_id = lines_id,
              nr_cells = nr_cells,
              dump=False)
        assert_col({"the_id":"col_0","type":"Note","author":abj,
                    "position":0,"title":"TITLE0"}, c)
        assert('P("line_0",[C("_VALUE_","%s","' % abj in c)
        assert('","_COMMENT_")])' in c)

    if do('badsyntax'):
        c = s.url('=' + abj + '/%d/Dossiers/badsyntax' % uyear)
        c = s.url('=' + abj + '/%d/Dossiers/badsyntax' % uyear +
                  '/1/0/cell_change/col_0/line_0/_VALUE_')
        assert(c == bug_png)
        c = s.url('=' + abj + '/%d/Dossiers/badsyntax' % uyear +
                  '/1/1/cell_chane/col_0/line_0/_VALUE_')
        assert(c == bug_png)
        c = s.url('=' + abj + '/%d/Dossiers/badsyntax' % uyear +
                  '/1/0/dsfsdffds')
        assert(c == ok_png) # ok for old requests

    if do('master'):
        c = s.url('=' + root + '/%d/Dossiers/master' % uyear)
        c = s.url('=' + root + '/%d/Dossiers/master' % uyear +
                  '/1/0/column_attr_title/col_0/TITLE0')
        assert(c == ok_png)
        c = s.url('=' + root + '/%d/Dossiers/master' % uyear +
                  '/1/1/cell_change/col_0/line_0/_VALUE_')
        assert(c == ok_png)
        lines_id = ['line_0']
        nr_columns = 1
        nr_pages = 2
        nr_cells = 1
        cell_required = (1,'col_0','line_0','_VALUE_')
        check('Y%d/SDossiers/master.py' % uyear,
              masters_expected = [root], nr_pages = nr_pages,
              nr_columns = nr_columns, lines_id = lines_id,
              nr_cells = nr_cells,
              cell_required = cell_required,
              dump=False)

        c = s.url('=' + abj + '/%d/Dossiers/master' % uyear)
        assert(c == unauthorized_html)

        c = s.url('=' + root + '/%d/Dossiers/master' % uyear +
                  '/1/2/table_attr_masters/super.user%20' + abj)
        check('Y%d/SDossiers/master.py' % uyear,
              masters_expected = [root,abj], nr_pages = nr_pages,
              nr_columns = nr_columns, lines_id = lines_id,
              nr_cells = nr_cells,
              cell_required = cell_required,
              dump=False)

        c = utilities.manage_key('LOGINS', os.path.join(root, 'master_of'))
        assert("('%d', 'Dossiers', 'master')" % uyear in c)
        assert("('0', 'Dossiers', 'config_table')" in c)

        c = s.url('=' + abj + '/%d/Dossiers/master' % uyear)
        assert("masters:['%s', '%s']" % (root, abj) in c)
        nr_pages += 1
        check('Y%d/SDossiers/master.py' % uyear,
              masters_expected = [root,abj], nr_pages = nr_pages,
              nr_columns = nr_columns, lines_id = lines_id,
              nr_cells = nr_cells,
              cell_required = cell_required,
              dump=False)

        c = s.url('=' + abj + '/%d/Dossiers/master' % uyear +
                  '/2/0/cell_change/col_0/line_0/_VALUE_2_')
        assert(c == ok_png)
        nr_cells += 1
        cell_required = (2,'col_0','line_0','_VALUE_2_')
        check('Y%d/SDossiers/master.py' % uyear,
              masters_expected = [root,abj], nr_pages = nr_pages,
              nr_columns = nr_columns, lines_id = lines_id,
              nr_cells = nr_cells,
              cell_required = cell_required,
              dump=False)

        c = s.url('=' + root + '/%d/Dossiers/master' % uyear +
                  '/1/3/table_attr_masters/' + root)
        check('Y%d/SDossiers/master.py' % uyear,
              masters_expected = [root], nr_pages = nr_pages,
              nr_columns = nr_columns, lines_id = lines_id,
              nr_cells = nr_cells,
              cell_required = cell_required,
              dump=False)

        c = s.url('=' + abj + '/%d/Dossiers/master' % uyear)
        assert(c == unauthorized_html)

        c = s.url('=' + abj + '/%d/Dossiers/master' % uyear +
                  '/2/1/cell_change/col_0/line_0/_VALUE3_')
        # It is ok because we are the cell author.
        # But it could be 'bad' because we are not a master in 'Dossiers'
        assert(c == ok_png)
        nr_cells += 1
        cell_required = (2,'col_0','line_0','_VALUE3_')
        check('Y%d/SDossiers/master.py' % uyear,
              masters_expected = [root], nr_pages = nr_pages,
              nr_columns = nr_columns, lines_id = lines_id,
              nr_cells = nr_cells,
              cell_required = cell_required,
              dump=False)

    if do('badpage'):
        c = s.url('=' + abj + '/%d/Dossiers/badpage' % uyear +
                  '/1/0/column_change/col_0/TITLE0/Note/[0;20]/1//1')
        # The answer may be different if the user is yet
        # authenticated or not
        assert(c == "<type 'exceptions.IndexError'>\nlist index out of range"
               or c == bug_png)

        c = s.url('=' + abj + '/%d/Dossiers/badpage' % uyear)
        c = s.url('=' + abj + '/%d/Dossiers/badpage' % uyear +
                  '/99/0/column_change/col_0/TITLE0/Note/[0;20]/1//1')
        assert(c == bug_png)

        # Take the page of somebody else
        c = s.url('=' + root + '/%d/Dossiers/badpage' % uyear +
                  '/0/0/column_change/col_0/TITLE0/Note/[0;20]/1//1')
        assert( c == bug_png or 'Cheater' in c)

    if do('cellprotect'):
        c = s.url('=' + root + '/9999/Test/cellprotect')
        c = s.url('=' + root + '/9999/Test/cellprotect' +
                  '/1/0/column_attr_title/col_0/TITLE0')
        assert(c == ok_png)
        c = s.url('=' + root + '/9999/Test/cellprotect' +
                  '/1/1/cell_change/col_0/line_0/_VALUE_1_')
        assert(c == ok_png)
        lines_id = ['line_0']
        nr_columns = 7
        nr_pages = 2
        nr_cells = 1
        check('Y9999/STest/cellprotect.py',
              masters_expected = [], nr_pages = nr_pages,
              nr_columns = nr_columns, lines_id = lines_id,
              nr_cells = nr_cells,
              dump=False)
        c = s.url('=' + abj + '/9999/Test/cellprotect')
        assert('P("line_0",[C(),C(),C(),C(),C(),C()' in c)
        assert('),C("_VALUE_1_","%s","' % root in c)
        c = s.url('=' + abj + '/9999/Test/cellprotect' +
                  '/2/0/cell_change/col_0/line_0/_VALUE_2_')
        assert(c == bad_png)
        c = s.url('=' + root + '/9999/Test/cellprotect' +
                  '/1/2/cell_change/col_0/line_0/_VALUE_2_')
        assert(c == ok_png)
        nr_cells = 2
        nr_pages += 1
        check('Y9999/STest/cellprotect.py',
              masters_expected = [], nr_pages = nr_pages,
              nr_columns = nr_columns, lines_id = lines_id,
              nr_cells = nr_cells,
              dump=False)
        
        c = s.url('=' + abj + '/9999/Test/cellprotect' +
                  '/2/1/comment_change/col_0/line_0/_COMMENT_')
        assert(c == bad_png)
        # nr_cells += 1
        cell_required = (2,'col_0','line_0','_COMMENT_')
        cell_required = (1, 'col_0', 'line_0', '_VALUE_2_')
        check('Y9999/STest/cellprotect.py',
              masters_expected = [], nr_pages = nr_pages,
              nr_columns = nr_columns, lines_id = lines_id,
              nr_cells = nr_cells,
              cell_required = cell_required,
              dump=False)

        c = s.url('=' + abj + '/9999/Test/cellprotect')
        assert('P("line_0",[C(),C(),C(),C(),C(),C()' in c)
        assert('),C("_VALUE_2_","%s","' % root in c)
        assert('_COMMENT_' not in c)


    if do('badchars'):
        c = s.url('=' + root + '/9999/Test/badchars')
        c = s.url('=' + root + '/9999/Test/badchars' +
                  '/1/0/column_attr_title/col_0/TITLE0')
        assert(c == ok_png)
        c = s.url('=' + root + '/9999/Test/badchars' +
                  '/1/1/cell_change/col_0/line_0/~`!@%23$24%25^%26*()%2B[]{}|\\;:\'"$2F$3F.,$3F')
        assert(c == ok_png)
        lines_id = ['line_0']
        nr_columns = 7
        nr_pages = 2
        nr_cells = 1
        cell_required = (1,'col_0','line_0','~`!@#$%^&*()+[]{}|\\;:\'"/?.,?')
        check('Y9999/STest/badchars.py',
              masters_expected = [], nr_pages = nr_pages,
              nr_columns = nr_columns, lines_id = lines_id,
              nr_cells = nr_cells,
              cell_required = cell_required,
              dump=False)

    if do('addfirstmaster'):
        c = s.url('=' + abj + '/9999/Test/addfirstmaster')
        c = s.url('=' + abj + '/9999/Test/addfirstmaster' +
                  '/1/0/table_attr_masters/' + abj)
        assert(c == ok_png)
        check('Y9999/STest/addfirstmaster.py', masters_expected = [abj])
        c = s.url('=' + abj + '/9999/Test/addfirstmaster' +
                  '/1/1/table_attr_masters/' + abj + '%20' + root)
        assert(c == ok_png)
        check('Y9999/STest/addfirstmaster.py', masters_expected = [abj,root])

    if do('badaddmaster'):
        c = s.url('=' + root + '/9999/Test/badaddmaster')
        c = s.url('=' + root + '/9999/Test/badaddmaster' +
                  '/1/0/table_attr_masters/' + root)
        assert(c == ok_png)
        c = s.url('=' + abj + '/9999/Test/badaddmaster')
        assert("masters:['%s']" % root in c)
        c = s.url('=' + abj + '/9999/Test/badaddmaster' +
                  '/2/0/table_attr_masters/' + abj)
        assert(c == bad_png)

    if do('tablecopy'):
        create_u2()

        # Copy only columns
        c = s.url('=' + root + '/%s/UE-INF20UE2/tablecopy/0/Dossiers/columns'
                  % ys)
        assert('OK' in c)
        c = s.url('=ue1.master')
        assert('["0", "Dossiers", "UE-INF20UE2"]' in c)
        c = s.url('=' + root + '/0/Dossiers/UE-INF20UE2')
        assert('TITLE0' in c)
        assert('_TABLE_COMMENT_' in c)
        assert('MARTIN' not in c)

        # Copy content without history
        c = s.url('=' + root + '/%s/UE-INF20UE2/tablecopy/0/Dossiers/content'
                  % ys)
        assert('OK' not in c) # Overwrite not allowed
        c = s.url('=ue1.master/0/Dossiers/UE-INF20UE2/delete_this_table')
        assert(deletion_done in c)
        c = s.url('=' + root + '/%s/UE-INF20UE2/tablecopy/0/Dossiers/content'
                  % ys)
        assert('OK' in c)
        c = s.url('=' + root + '/0/Dossiers/UE-INF20UE2')
        assert('MARTIN' in c)

        # Copy history
        c = s.url('=' + root + '/%s/UE-INF20UE2/tablecopy/0/Dossiers/history'
                  % ys)
        assert('OK' not in c) # Overwrite not allowed
        c = s.url('=ue1.master/0/Dossiers/UE-INF20UE2/delete_this_table')
        c = s.url('=' + root + '/%s/UE-INF20UE2/tablecopy/0/Dossiers/history'
                  % ys)
        assert('OK' in c)
        a = utilities.read_file('DBregtest/Y0/SDossiers/UE-INF20UE2.py')
        b = utilities.read_file('DBregtest/Y%d/S%s/UE-INF20UE2.py' % (
            year, semester))
        assert( a == b )

    if do('masterpower'):
        c = s.url('=' + root + '/9999/Test/masterpower')
        c = s.url('=' + root + '/9999/Test/masterpower' +
                  '/1/0/column_attr_title/col_0/TITLE0')
        assert(c == ok_png)
        c = s.url('=' + root + '/9999/Test/masterpower' +
                  '/1/1/cell_change/col_0/line_0/_VALUE_')
        assert(c == ok_png)

        c = s.url('=' + abj + '/9999/Test/masterpower')
        c = s.url('=' + abj + '/9999/Test/masterpower' +
                  '/2/0/table_attr_masters/' + abj)
        assert(c == ok_png)
        c = s.url('=' + abj + '/9999/Test/masterpower' +
                  '/2/1/cell_change/col_0/line_0/_VALUE_2_')
        assert(c == ok_png)
        lines_id = ['line_0']
        nr_columns = 7
        nr_pages = 3
        nr_cells = 2
        cell_required = (2,'col_0','line_0','_VALUE_2_')
        check('Y9999/STest/masterpower.py',
              masters_expected = [abj], nr_pages = nr_pages,
              nr_columns = nr_columns, lines_id = lines_id,
              nr_cells = nr_cells,
              cell_required = cell_required,
              dump=False)
        
    if do('comments'):
        c = s.url('=' + root + '/9999/Test/comments')
        c = s.url('=' + root + '/9999/Test/comments' +
                  '/1/0/column_attr_comment/col_0/_COMMENT_')
        assert(c == ok_png)
        c = s.url('=' + root + '/9999/Test/comments' +
                  '/1/1/column_attr_title/col_0/TITLE0')
        assert(c == ok_png)
        lines_id = []
        nr_columns = 7
        nr_pages = 2
        nr_cells = 0
        column_required = ('comment', 1, 'col_0', '_COMMENT_')
        check('Y9999/STest/comments.py',
              masters_expected = [], nr_pages = nr_pages,
              nr_columns = nr_columns, lines_id = lines_id,
              nr_cells = nr_cells,
              column_required = column_required,
              dump=False)

        c = s.url('=' + abj + '/9999/Test/comments')
        c = s.url('=' + abj + '/9999/Test/comments' +
                  '/2/0/column_attr_comment/col_0/_COMMENT2_')
        assert(c == bad_png)
        
        column_required = ('comment', 1, 'col_0', '_COMMENT_')
        nr_pages += 1
        # nr_columns += 1
        check('Y9999/STest/comments.py',
              masters_expected = [], nr_pages = nr_pages,
              nr_columns = nr_columns, lines_id = lines_id,
              nr_cells = nr_cells,
              column_required = column_required,
              dump=False)

        c = s.url('=' + abj + '/9999/Test/comments' +
                  '/2/1/table_attr_comment/_COMMENT3_')
        assert(c == ok_png)
        column_required = (2, '_COMMENT3_')
        check('Y9999/STest/comments.py',
              masters_expected = [], nr_pages = nr_pages,
              nr_columns = nr_columns, lines_id = lines_id,
              nr_cells = nr_cells,
              column_required = column_required,
              dump=False)
        
        c = s.url('=' + root + '/9999/Test/comments' +
                  '/1/2/table_attr_comment/_COMMENT4_')
        assert(c == ok_png)
        column_required = (1, '_COMMENT4_')
        check('Y9999/STest/comments.py',
              masters_expected = [], nr_pages = nr_pages,
              nr_columns = nr_columns, lines_id = lines_id,
              nr_cells = nr_cells,
              column_required = column_required,
              dump=False)

        c = s.url('=' + root + '/9999/Test/comments')
        assert('comment:"_COMMENT4_"' in c)
        assert_col({"the_id":"col_0","type":"Note","author":root,
                   "comment":"_COMMENT_","position":6,"title":"TITLE0"}, c)

    if do('ue2'):
        # See 'tomuss.py' for more information on this case
        c = s.url('=' + root + '/%s/UE-INF20UE2' % ys)
        assert('P("0_0",[C("10800000","*","' in c)
        assert('),C("Jacques","*","' in c)
        assert('),C("MARTIN","*","' in c)

    if do('abj'):
        c = s.url('=' + abj + '/%s/abj' % ys)
        assert('abj.js' in c)
        c = s.url('=' + abj + '/%s/abj/0/10800000/display' % ys)
        # The student is not in any UE
        assert("ues_without_da(['UE-INF20UE2', 'UE-INF20UE2L'])" in c)

        c = s.url('=' + abj + '/%s/abj/0/10800000/add_da/UE-UE1/1/2/3/com1' % ys)
        assert("display_da([['UE-UE1','1/2/3','%s',\"com1\"]])" % abj in c)

        c = s.url('=' + abj + '/%s/abj/0/10800000/add_da/UE-UE1/1/2/3/com2' % ys)
        assert("display_da([['UE-UE1','1/2/3','%s',\"com1\"]])" % abj in c)

        c = s.url('=' + abj + '/%s/abj/0/10800000/add_da/UE-INF20UE2/1/1/%d/com2' % (ys,year))
        assert("display_da([['UE-UE1','1/2/3','%s',\"com1\"],['UE-INF20UE2','1/1/%d','%s',\"com2\"]])" % (abj, year, abj) in c)

        c = s.url('=' + abj + '/%s/abj/0/10800000/rem_da/UE-UE1' % ys)
        assert("display_da([['UE-INF20UE2','1/1/%d','%s',\"com2\"]])" % (year, abj) in c)


        c = s.url('=' + abj + '/%s/abj/0/10800000/addabj/%s/M/%s/A/com4' % (
            ys, abj_date_old, abj_date_previous))
        assert("display_da([['UE-INF20UE2','1/1/%d','%s',\"com2\"]])" % (year, abj) in c)
        assert("display_abjs([['%sM','%sA','%s',\"com4\"]])" % (
            abj_date_old, abj_date_previous, abj) in c)

        c = s.url('=' + abj + '/%s/abj/0/10800000/addabj/%s/M/%s/A/com5' % (
            ys, abj_date_current, abj_date_next))
        assert("display_da([['UE-INF20UE2','1/1/%d','%s',\"com2\"]])" % (year, abj) in c)
        assert("display_abjs([['%sM','%sA','%s',\"com4\"],['%sM','%sA','%s',\"com5\"]])" % (
            abj_date_old, abj_date_previous, abj,
            abj_date_current, abj_date_next, abj) in c)

        c = s.url('=' + abj + '/%s/abj/0/10800000/delabj/%s/M/%s/A' % (
            ys, abj_date_old, abj_date_previous))
        assert("display_da([['UE-INF20UE2','1/1/%d','%s',\"com2\"]])" % (year, abj) in c)
        assert("display_abjs([['%sM','%sA','%s',\"com5\"]])" % (
            abj_date_current, abj_date_next, abj) in c)

        # Add a DA in licence
        # c = s.url('=' + abj + '/%s/abj/0/10800000/add_da/UE-INF20UE2L/1/1/%d' % (ys,year))

        c = s.url('=' + abj + '/%s/abj/alpha.xls' % ys)
        assert('<tbody id="t"><tr><td>10800000firstname</td><td>10800000surname</td><td>10800000</td><td>ABJ</td><td>%sM</td><td>%sA</td></tr>\n<tr><td>10800000firstname</td><td>10800000surname</td><td>10800000</td><td>DAS</td><td>UE-INF20UE2</td><td>1/1/%d</td></tr>\n</tbody></table>' % (
            abj_date_current, abj_date_next, year))

        # No messages sent because there is no UE master mail
        c = s.url('=' + abj + '/%s/abj/list_mail' % ys)
        assert('UE-INF20UE2L: ' in c)
        assert('UE-INF20UE2: ' not in c)
        assert(_("MSG_no_master") in c)
        assert(_("MSG_abj_send") % 0 in c)

        create_u2()

        # See 'tomuss.py' for more information on this case
        c = s.url('=' + root + '/%s/UE-INF20UE2' % ys)
        assert('P("0_0",[C("10800000","*","' in c)
        assert('),C("Jacques","*","' in c)
        assert('),C("MARTIN","*","' in c)
        assert('),C(11.11,"%s","' % root in c)
        assert('"10800000":"jacques@martin"' in c)
        assert('change_abjs({"10800000":[[["%sM","%sA","com5"]],[["UE-INF20UE2","1/1/%d","com2"]],""]});' % (
            abj_date_current, abj_date_next, year) in c)

        c = s.url('=' + root + '/%s/UE-INF20UE2/resume' % ys)
        assert(_("TH_ABJ_list") in c)
        assert('10800000 MARTIN Jacques' in c)
        # assert('Du %s matin au %s apr' % (
        #    abj_date_current, abj_date_next) in c)
        assert(str(abj_date_current) in c)
        assert(str(abj_date_next) in c)
        # assert('avec une DA' in c)
        # assert('partir du %s' % year in c)

        s.stop()
        s.restart()

        c = s.url('=' + root + '/%s/UE-INF20UE2' % ys)
        assert('P("0_0",[C("10800000","*","' in c)
        assert('),C("Jacques","*","' in c)
        assert('),C("MARTIN","*","' in c)
        assert('),C(11.11,"%s","' % root in c)
        assert('"10800000":"jacques@martin"' in c)
        assert('change_abjs({"10800000":[[["%sM","%sA","com5"]],[["UE-INF20UE2","1/1/%d","com2"]],""]});' % (
            abj_date_current, abj_date_next, year) in c)

        c = s.url('=' + root + '/%s/UE-INF20UE2/resume' % ys)
        assert(_("TH_ABJ_list") in c)
        assert('10800000 MARTIN Jacques' in c)
        # assert('Du %s matin au %s apr' % (
        #    abj_date_current, abj_date_next) in c)
        assert(str(abj_date_current) in c)
        assert(str(abj_date_next) in c)
        # assert('avec une DA' in c)
        # assert('partir du 1/1/%d' % year in c) # XXX


    if do('extension'):
        c = s.url('=' + abj + '/%s/extension' % ys)
        c = s.url('=' + abj + '/%s/extension/1/0/table_attr_masters/' % ys + abj)
        assert( c == ok_png)
        c = s.url('=' + abj + '/%s/extension/extension' % ys)
        assert( _("MSG_extension_ok").split('\n')[1] in c)

    if do('tt'):
        create_tt()

        c = s.url('=' + root + '/%s/UE-INF20UE2' % ys)
        assert('COL_COMMENT: CELL VALUE (CELL COMMENT)' in c)

        s.stop()
        s.restart()

        c = s.url('=' + root + '/%s/UE-INF20UE2' % ys)
        assert('COL_COMMENT: CELL VALUE (CELL COMMENT)' in c)

        c = s.url('=' + root + '/%s/UE-INF20UE2/resume' % ys)
        assert('- COL_COMMENT: CELL VALUE (CELL COMMENT)' in c)

    if do('delcol'):
        c = s.url('=' + abj + '/%d/Dossiers/delcol' % uyear)
        c = s.url('='+abj+'/%d/Dossiers/delcol' % uyear +
                  '/1/0/column_attr_title/col_0/TITLE0')
        assert( c == ok_png)
        c = s.url('='+abj+'/%d/Dossiers/delcol' % uyear +
                  '/1/1/cell_change/col_0/line_0/_VALUE_')
        assert(c == ok_png)
        c = s.url('='+abj+'/%d/Dossiers/delcol' % uyear +
                  '/1/2/column_delete/col_0')
        assert(c == bad_png)
        c = s.url('='+abj+'/%d/Dossiers/delcol' % uyear +
                  '/1/3/cell_change/col_0/line_0/')
        assert(c == ok_png)
        c = s.url('='+abj+'/%d/Dossiers/delcol' % uyear +
                  '/1/4/column_delete/col_0')
        assert(c == ok_png)
        c = s.url('='+abj+'/%d/Dossiers/delcol' % uyear +
                  '/1/5/column_attr_title/col_1/TITLE1')
        assert( c == ok_png)

        s.stop()
        s.restart()

        c = s.url('=' + abj + '/%d/Dossiers/delcol' % uyear)
        assert_col({"the_id":"col_1","type":"Note","author":abj,
                   "position":0,"title":"TITLE1"}, c,
                   )

    if do('referents'):
        create_referents()

    if do('rss'):
        create_u2()
        save_sec()
        ss.start()
        c = ss.url('%s/rss/10800000' % ys)
        assert(_("MSG_suivi_student_RSS_forbiden_title") in c)

        c = ss.url('=%s/%s/%%2010800000' % (root, ys))
        assert('<iframe' not in c)
        key = utilities.manage_key('LOGINS', '10800001/rsskey')
        assert(key is False)

        ss.url('=10800000/%s' % ys)
        s.url('=10800000/rsskey')
        key = utilities.manage_key('LOGINS', '10800000/rsskey')
        assert(key is not False)
        c = ss.url('%s/rss/%s' % (ys, key))
        assert('<title>UE-INF20UE2 : TITLE0 : 11.11/20</title>' in c)

        c2 = ss.url('%s/rss/%s' % (ys, key))
        assert(c.split('</lastBuildDate>')[1] ==
               c2.split('</lastBuildDate>')[1])

        wait_sec()
        c = s.url('=' + root + '/%s/UE-INF20UE2' % ys)
        page = c.split('page_id = "')[1].split('"')[0]
        c = s.url('=' + root + '/%s/UE-INF20UE2' % ys +
                  '/%s/0/column_attr_visibility_date/col_0/%s'
                  % (page, now_plus_30_days))
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-INF20UE2' % ys +
                  '/%s/1/column_attr_visibility_date/col_0/'
                  % (page,))
        assert(c == ok_png)

        c = ss.url('=' + root + '/%s/unload/%s' % (ys, 'UE-INF20UE2'))
        assert(c == '')
        c = ss.url('%s/rss/%s' % (ys, key))
        assert('<title>UE-INF20UE2 : TITLE0 : 11.11/20</title>' in c)
        assert(c.split('</lastBuildDate>')[1] !=
               c2.split('</lastBuildDate>')[1]) # RSS want the most recent date

    if do('suivi'):
        create_tt()
        create_referents()
        create_u2()
        ss.start()
        c = ss.url('=' + abj + '/%s/10800000' % ys)
        assert('"ue": "UE-INF20UE2"' in c)
        assert_col({"the_id":"col_0","type":"Note","author":root,
                   "position":6,"title":"TITLE0"}, c)

        assert(', [11.11, "%s", "' % root in c)
        assert('"rank": 1' in c)
        assert('"rank_grp": 0' in c)
        assert('"nr_in_grp": 1' in c)
        assert('"nr": 2' in c)
        assert('"average": 16.665' in c)
        assert('"mediane": 11.11' in c)

        c = s.url('=' + root + '/%s/UE-XXX9999L' % ys)
        time.sleep(3)
        # XXX DBregtest/Y2013/SPrintemps/UE-XXX9999L.py sometime broken
        c = s.url('=' + root + '/%s/UE-XXX9999L' % ys +
                  '/1/0/column_attr_type/col_0/Bool')
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-XXX9999L' % ys +
                  '/1/1/column_attr_title/col_0/TITLE0')
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-XXX9999L' % ys +
                  '/1/2/column_attr_modifiable/col_0/1')
        assert(c == ok_png)
        time.sleep(1) # In order to update table

        c = ss.url('=' + abj + '/%s/10800000' % ys)
        assert('"ue": "UE-INF20UE2"' in c)
        assert('"ue": "UE-XXX9999L"' in c)

        assert('toto' in c)

        c = s.url('=' + abj + '/%s/UE-XXX9999L/cell/col_0/0_0/%s' % (
                ys, _("yes")))
        assert('<body style="background:green">' in c)

        c = ss.url('=' + abj + '/%s/unload/UE-XXX9999L' % ys)
        assert(c == '')

        c = ss.url('=' + abj + '/%s/10800000' % ys)
        assert('"ue": "UE-INF20UE2"' in c)
        assert('"ue": "UE-XXX9999L"' in c)

        c = s.url('=' + root + '/%s/UE-XXX9999L/cell/col_0/0_0/%s' % (
                ys, _("no")))
        assert('<body style="background:red">' in c)
        

    if do('suivistat'):
        create_tt()
        create_referents()
        create_u2()
        ss.start()
        c = ss.url('=' + abj + '/%s/%s' % (ys, root) )
        # Currently no more displayed on suivi (modified_tables)
        # assert('/=%s/%s/UE-INF20UE2/=full_filter=@%s" target="_blank">%s %s UE-INF20UE2<' % (abj, ys, root, year, semester) in c)
        # assert(_("MSG_suivi_student_ue_changes") % (3,1) in c)

        c = ss.url('=' + root + '/%s/uninterested' % ys )
        assert('10800000' in c)
        assert('10800001' not in c)
        assert('<td>1</td>' in c)

        c = ss.url('=' + root + '/%s/*3' % ys )
        assert(_("MSG_suivi_referents_nr_referents") + '3' in c)
        assert(_("MSG_suivi_referents_nr_students") + '2' in c)

        c = ss.url('=' + abj + '/%s/*1' % ys )
        assert(_("TITLE_suivi_bad_student") in c)
        assert('10800000' not in c)
        assert('10800001' in c)
        assert('22.2' in c)

        c = ss.url('=' + root + '/%s/referents.csv' % ys )
        assert(';10800000;MartiN;Jacques;surnametoto;Firstnametoto;mail@toto' in c)

    if do('suivitable'):
        create_tt()
        create_referents()
        create_u2()
        ss.start()

        c = ss.url('=' + abj + '/%s/*' % ys )
        assert(_("COL_TITLE_nb_cells_entered") in c)
        # le dictionnaire n'est pas toujours dans le meme ordre
        assert(': [C("%s"),' % abj in c)


        c = ss.url('=' + abj + '/%s/*2' % ys )
        assert(_("COL_TITLE_nb_teachers") in c)
        # assert('P([C("teachers","*"),' in c)
        # le dictionnaire n'est pas toujours dans le meme ordre
        assert(': [C("UE-INF20UE2"),' in c)

    if do('private'):
        c = s.url('=' + root + '/%s/UE-INF11UE2' % ys)
        c = s.url('=' + root + '/%s/UE-INF11UE2/1/0/table_attr_masters/' % ys + root)
        assert( c == ok_png)
        c = s.url('=' + root + '/%s/UE-INF11UE2/1/1/table_attr_private/1' % ys)
        assert( c == ok_png)
        c = s.url('=' + abj + '/%s/UE-INF11UE2' % ys)
        assert(_("MSG_new_page_unauthorized") in c)
        c = s.url('=' + root + '/%s/UE-INF11UE2/1/2/cell_change/0_0/0_0/10800000' % ys)
        c = s.url('=' + root + '/%s/UE-INF11UE2/1/3/cell_change/0_3/0_0/X'% ys)
        assert( c == ok_png)
        c = s.url('=' + root + '/%s/UE-INF11UE2' % ys)
        assert( ('C("X","%s"' % root) in c)
        ss.start()
        c = ss.url('%s/rss2/UE-INF11UE2' % ys)
        assert(_("MSG_suivi_student_RSS_table").split("<br>")[1] % 2
               in c)
        c = ss.url('=' + abj + '/%s/10800000' % ys)
        assert('[], [], ["X", "%s"' % root in c)


    if do('resume'):
        create_u2()
        ss.start()
        c = ss.url('=' + root + '/%s/resume/UE-INF20UE2/UE-INF20UE2' % ys)
        # assert('lines = {"0": [C("10800001"),C(),C(),C(1),C(1),C()],\n"1": [C("10800000"),C("Jacques"),C("MARTIN"),C(1),C(1),C()]}' in c)
        assert(': [C("10800001"),C(),C(),C(1),C(1),C()]' in c)
        assert(': [C("10800000"),C("Jacques"),C("MARTIN"),C(1),C(1),C()]' in c)

    if do('delete_this_table'):
        create_u2()
        c = s.url('=' + abj + '/%s/UE-INF20UE2/delete_this_table' % ys)
        assert(_("MSG_extension_not_master") in c)
        c = s.url('=ue1.master/%s/UE-INF20UE2/delete_this_table' % ys)
        assert(_("MSG_delete_this_table_done") in c)
        assert(check('%s/UE-INF20UE2.py', exists=False))
        assert(check('%s/UE-INF20UE2.pyc', exists=False))

    if do('empty_is'):
        c = s.url('=' + root + '/%s/UE-INF20UE3' % ys)
        time.sleep(1)
        c = s.url('=' + root + '/%s/UE-INF20UE3/1/0/column_attr_title/col_0/TITLE0' % ys)
        assert(c == ok_png)
        c = s.url('=' + abj + '/%s/UE-INF20UE3' % ys)
        c = s.url('=' + abj + '/%s/UE-INF20UE3/2/0/column_attr_title/col_1/TITLE1' % ys)
        assert(c == ok_png)

        c = s.url('=' + abj + '/%s/UE-INF20UE3/2/1/column_attr_title/col_0/TITLE2' % ys)
        assert(c == bad_png)

        c = s.url('=' + abj + '/%s/UE-INF20UE3/2/2/column_attr_empty_is/col_1/EMPTY1' % ys)
        assert(c == ok_png)

        c = s.url('=' + abj + '/%s/UE-INF20UE3/2/3/column_attr_empty_is/col_0/EMPTY0' % ys)
        assert(c == bad_png)

    if do('visibility'):
        s.url('=' + root + '/%s/UE-INF20UE9' % ys)
        c = s.url('=' + root + '/%s/UE-INF20UE9/1/0/column_attr_visibility_date/col_0/99' % ys)
        assert(c == bug_png)
        c = s.url('=' + root + '/%s/UE-INF20UE9/1/1/column_attr_title/col_0/TITLE99' % ys)
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-INF20UE9/1/2/column_attr_visibility_date/col_0/99' % ys)
        assert(c == bug_png)
        c = s.url('=' + root + '/%s/UE-INF20UE9/1/3/column_attr_visibility_date/col_0/%s' % (ys, now_plus_32_days))
        assert(c == bug_png)
        c = s.url('=' + root + '/%s/UE-INF20UE9/1/4/column_attr_visibility_date/col_0/%s' % (ys, now_plus_30_days))
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-INF20UE9/1/5/cell_change/0_0/lin_0/10123456' % ys)
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-INF20UE9/1/6/cell_change/col_0/lin_0/7.77' % ys)
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-INF20UE9/1/7/column_attr_title/col_1/TITLE88' % ys)
        assert(c == ok_png)
        now = time.strftime('%Y%m%d')
        c = s.url('=' + root + '/%s/UE-INF20UE9/1/8/column_attr_visibility_date/col_1/%s' % (ys, now))
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-INF20UE9/1/9/cell_change/col_1/lin_0/1.234' % ys)
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-INF20UE9/1/10/cell_change/col_1/lin_0/8.88' % ys)
        assert(c == ok_png)
        ss.start()
        c = ss.url('=' + abj + '/%s/10123456' % ys)
        assert('"ue": "UE-INF20UE9"' in c)
        assert('7.77' in c)
        assert('8.88' in c)
        # This history is visible
        assert('1.234' in c)

        # The student the rank 7.77 is not in the file (not visible)
        c = ss.url('=' + abj + '/%s/%%2010123456' % ys)
        assert('7.77' not in c)
        assert('8.88' in c)
        # This history is not visible
        assert('1.234' not in c)

    if do('visibility2'):
        s.url('=' + root + '/%s/UE-INF22UE9' % ys)
        c = s.url('='+root+'/%s/UE-INF22UE9/1/0/column_attr_visibility/col_0/1' % ys)
        assert(c == ok_png)
        c = s.url('='+root+'/%s/UE-INF22UE9/1/1/cell_change/0_0/lin_0/10045678' % ys)
        assert(c == ok_png)
        c = s.url('='+root+'/%s/UE-INF22UE9/1/2/cell_change/col_0/lin_0/12.31' % ys)
        assert(c == ok_png)
        c = s.url('='+root+'/%s/UE-INF22UE9/1/3/column_attr_visibility/col_1/2' % ys)
        assert(c == ok_png)
        c = s.url('='+root+'/%s/UE-INF22UE9/1/4/cell_change/col_1/lin_0/19.62' % ys)
        assert(c == ok_png)
        
        ss.start()
        c = ss.url('=' + abj + '/%s/10045678' % ys)
        assert('"ue": "UE-INF22UE9"' in c)
        assert('12.31' in c)
        assert('19.62' not in c)
        c = ss.url('=' + abj + '/%s/%%2010045678' % ys)
        assert('12.31' not in c)
        assert('19.62' not in c)
        
    if do('import'):
        s.url('=' + root + '/%s/UE-INF21UE9' % ys)
        c = s.url('=' + root + '/%s/UE-INF21UE9/1/0/column_attr_title/col_0/T1' % ys)
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-INF21UE9/1/1/column_attr_title/col_1/T2' % ys)
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-INF21UE9/1/2/cell_change/0_0/0_0/10123456' % ys)
        assert(c == ok_png)
        f = open('xxx.csv', 'w', encoding = "utf-8")
        f.write('qqqq,qqq,qqqq\n10123456,4.4444,XXXXYYYY\nttt,yyy,uuu,uu')
        f.close()
        csv = ('file://%s/xxx.csv' % os.getcwd()).replace('/','$2F')
        c = s.url('=' + root + '/%s/UE-INF21UE9/1/3/column_attr_comment/col_0/xxIMPORT(%s$232)yy' % (ys, csv))
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-INF21UE9/1/4/column_attr_comment/col_1/xxIMPORT(%s$233)yy' % (ys, csv))
        assert(c == ok_png)
        time.sleep(1)
        ss.start()
        c = ss.url('=' + abj + '/%s/10123456' % ys)
        assert('xxyy' in c) # URL not visible
        assert('4.4444' in c)
        assert('XXXXYYYY' in c)

        # Change values
        f = open('xxx.csv', 'w', encoding = "utf-8")
        f.write('qqqq,qqq,qqqq\n10123456,val=é,val=è\r\nttt,yyy,uuu,uu\n1,2,3')
        f.close()
        c = s.url('=' + root + '/%s/UE-INF21UE9/1/5/column_attr_comment/col_0/xxIMPORT()yy' % ys)
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-INF21UE9/1/6/column_attr_comment/col_1/xxIMPORT()yy' % ys)
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-INF21UE9/1/7/column_attr_comment/col_0/xxIMPORT(%s$232)yy' % (ys, csv))
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-INF21UE9/1/8/column_attr_comment/col_1/xxIMPORT(%s$233)yy' % (ys, csv))
        assert(c == ok_png)
        # time.sleep(1)
        c = s.url('=' + root + '/%s/UE-INF21UE9' % ys)
        assert('4.4444' in c)
        assert('XXXXYYYY' in c)
        assert('val=é' in c)
        assert('val=è' in c)
        f = open('xxx.csv', 'w', encoding = "utf-8")
        f.write('qqqq,qqq,qqqq\r10123456,val2=\xe9,val2=\xe8\rttt,yyy,uuu,uu\r1,2,3')
        f.close()
        c = s.url('=' + root + '/%s/UE-INF21UE9/1/9/column_attr_comment/col_0/xxIMPORT()yy' % ys)
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-INF21UE9/1/10/column_attr_comment/col_1/xxIMPORT()yy' % ys)
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-INF21UE9/1/11/column_attr_comment/col_0/xxIMPORT(%s$232)yy' % (ys, csv))
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-INF21UE9/1/12/column_attr_comment/col_1/xxIMPORT(%s$233)yy' % (ys, csv))
        assert(c == ok_png)
        # time.sleep(1)
        c = s.url('=' + root + '/%s/UE-INF21UE9' % ys)
        assert('4.4444' in c)
        assert('XXXXYYYY' in c)
        assert('val=é' in c)
        assert('val=è' in c)
        assert('val2=é' in c)
        assert('val2=è' in c)

    if do('past'):
        # Normal user can't modify the past
        utilities.mkpath_safe('DBregtest/Y%d/SAutomne' % (year-1))
        utilities.write_file_safe('DBregtest/Y%d/SAutomne/UE-pastue.py'
                                  % (year-1),
                             """# -*- coding: utf8 -*-
from data import *
new_page('' ,'*', '', '', None)
""")    
        c = s.url('=' + abj + '/%d/Automne/UE-pastue' % (year-1))
        assert('columns = [' in c)
        assert('modifiable:0' in c)
        c = s.url('=' + abj + '/%d/Automne/UE-pastue/1/0/column_attr_comment/col_0/test' % (year-1))
        assert(c == bad_png)
        c = s.url('=' + abj + '/%d/Automne/UE-pastue/1/1/table_attr_modifiable/1' % (year-1))
        assert(c == bad_png)

        # root can modify table attribute in the past.
        s.url('=' + root + '/%d/Automne/UE-pastue' % (year-1))
        c = s.url('=' + root + '/%d/Automne/UE-pastue/2/0/table_attr_masters/%s' % (year-1, abj))
        assert(c == bad_png)
        c = s.url('=' + root + '/%d/Automne/UE-pastue/2/1/table_attr_modifiable/1' % (year-1))
        assert(c == ok_png)
        c = s.url('=' + root + '/%d/Automne/UE-pastue/2/2/table_attr_masters/%s' % (year-1, abj))
        assert(c == ok_png)
        c = s.url('=' + root + '/%d/Automne/UE-pastue/2/3/table_attr_modifiable/0' % (year-1))
        assert(c == ok_png)

        # abj can now modify the table attributes (not values)
        c = s.url('=' + abj + '/%d/Automne/UE-pastue/1/2/column_attr_comment/col_0/test2' % (year-1))
        assert(c == bad_png)
        c = s.url('=' + abj + '/%d/Automne/UE-pastue/1/3/table_attr_comment/col_0/cococo' % (year-1))
        assert(c == bad_png)
        c = s.url('=' + abj + '/%d/Automne/UE-pastue/1/4/table_attr_modifiable/1' % (year-1))
        assert(c == ok_png)
        c = s.url('=' + abj + '/%d/Automne/UE-pastue/1/5/column_attr_comment/col_0/test3' % (year-1))
        assert(c == ok_png)

        # Can't create an UE in the past
        s.url('=' + root + '/%d/Automne/UE-pastue2' % (year-1))
        assert(c == ok_png)
        assert(os.path.exists('DBregtest/Y%d/SAutomne/UE-pastue.py' % (year-1)))
        assert(not os.path.exists('DBregtest/Y%d/SAutomne/UE-pastue2.py' % (year-1)))
                             
    if do('modifiable'):
        c = s.url('=' + abj +'/%s/UE-modif' % ys)
        assert('modifiable:1' in c)
        c = s.url('=' + abj +'/%s/UE-modif/1/0/table_attr_modifiable/0' % ys)
        assert(c == bad_png)
        c = s.url('=' + abj +'/%s/UE-modif/1/1/table_attr_masters/%s'%(ys,abj))
        assert(c == ok_png)
        c = s.url('=' + abj +'/%s/UE-modif/1/2/table_attr_modifiable/0' % ys)
        assert(c == ok_png)
        check('Y%d/S%s/UE-modif.py' % (year, semester), nr_pages = 2)

        c = s.url('=' + abj +'/%s/UE-modif' % ys)
        assert('modifiable:0' in c)
        c = s.url('=' + abj +'/%s/UE-modif' % ys)
        assert('modifiable:0' in c)
        c = s.url('=' + abj +'/%s/UE-modif/3/0/table_attr_masters/'%(ys))
        assert(c == bad_png)
        check('Y%d/S%s/UE-modif.py' % (year, semester), nr_pages = 2)
        c = s.url('=' + abj +'/%s/UE-modif/3/1/table_attr_modifiable/1'%(ys))
        assert(c == ok_png)
        check('Y%d/S%s/UE-modif.py' % (year, semester), nr_pages = 4)

    if do('lostpage'):
        c = s.url('=' + abj +'/%s/UE-lost' % ys)
        assert('modifiable:1' in c)
        c = s.url('=' + abj +'/%s/UE-lost/1/0/table_attr_masters/%s'%(ys,abj))
        assert(c == ok_png)
        c = s.url('=' + abj +'/%s/UE-lost/1/1/table_attr_modifiable/0' % ys)
        assert(c == ok_png)
        check('Y%d/S%s/UE-lost.py' % (year, semester), nr_pages = 2)
        c = s.url('=' + abj +'/%s/UE-lost' % ys)
        assert('modifiable:0' in c)
        check('Y%d/S%s/UE-lost.py' % (year, semester), nr_pages = 2)
        s.stop()
        s.restart()
        check('Y%d/S%s/UE-lost.py' % (year, semester), nr_pages = 2)
        c = s.url('=' + abj +'/%s/UE-lost/0/0' % ys)
        assert('click_to_revalidate_ticket' in c)
        c = s.url('=' + abj +'/%s/UE-lost/2/0' % ys)
        assert('server_answered' in c)
        
    if do('template_reload'):
        f = open('TEMPLATES/xxx_regtest.py', 'w', encoding = "utf-8")
        f.write('''
from data import ro_user
def content(table):
    return "XXX_REGTEST1"
def create(table):
    table.new_page("", ro_user, "", "")
''')
        f.close()
        t = time.time()
        c = s.url('=' + abj +'/%s/xxx_regtest-1' % ys)
        assert("XXX_REGTEST1" in c)
        while time.time() - t < 1:
            pass
        f = open('TEMPLATES/xxx_regtest.py', 'a', encoding = "utf-8")
        f.write('def content(table): return "XXX_REGTEST2"\n')
        f.close()
        c = s.url('=' + abj +'/%s/xxx_regtest-3' % ys)
        assert("XXX_REGTEST2" in c)
        from ..TEMPLATES import xxx_regtest
        os.unlink(xxx_regtest.__cached__)

    if do('code_etape'):
        c = s.url('=' + abj +'/%s/UE-etape' % ys)
        assert('modifiable:1' in c)
        c = s.url('='+abj+'/%s/UE-etape/1/0/column_attr_type/A/Code_Etape'%ys)
        assert(c == ok_png)
        c = s.url('='+abj+'/%s/UE-etape/1/1/cell_change/0_0/L1/10800000' % ys)
        assert(c == ok_png)
        c = s.url('='+abj+'/%s/UE-etape/1/2/cell_change/0_0/L2/10800001' % ys)
        assert(c == ok_png)
        c = s.url('='+abj+'/%s/UE-etape/1/3/column_attr_columns/A/ID' % ys)
        assert(c == ok_png)

        c = s.url('=' + abj +'/%s/UE-etape' % ys)
        assert('etape-10800000' in c)
        assert('etape-10800001' in c)
        c = s.url('='+abj+'/%s/UE-etape/1/4/cell_change/0_0/L3/10800002' % ys)
        assert(c == ok_png)

        c = s.url('=' + abj +'/%s/UE-etape' % ys)
        assert('etape-10800002' in c)

        c = s.url('='+abj+'/%s/UE-etape/1/5/table_attr_masters/%s' % (ys,abj))
        assert(c == ok_png)

        # os.mkdir('DBregtest/Y%d' % (year-1))
        # os.mkdir('BACKUP_DBregtest/Y%d' % (year-1))
        utilities.mkpath('DBregtest/Y%d/S%s' % (year-1, semester))
        utilities.mkpath('BACKUP_DBregtest/Y%d/S%s' % (year-1, semester))
        os.rename('DBregtest/Y%d/S%s/UE-etape.py' % (year, semester),
        'DBregtest/Y%d/S%s/UE-etape.py' % (year-1, semester))
        
        c = s.url('=' + abj +'/%s/UE-etape' % ys_old)
        assert('modifiable:0' in c)
        c = s.url('=' + abj +'/%s/UE-etape/1/6' % ys_old)
        assert('set_updating(1);' in c)
        c = s.url('='+abj+'/%s/UE-etape/1/6/table_attr_modifiable/1' % ys_old)
        assert(c == ok_png)
        c = s.url('='+abj+'/%s/UE-etape/1/7/cell_change/0_0/L4/10800003' % ys_old)
        assert(c == ok_png)
        time.sleep(0.1)
        c = s.url('=' + abj +'/%s/UE-etape' % ys_old)
        assert('10800003' in c)
        assert('etape-10800003' in c)

    if do('enumeration'):
        c = s.url('=' + abj +'/%s/UE-enum' % ys)
        assert('modifiable:1' in c)
        c = s.url('='+abj+'/%s/UE-enum/1/0/column_attr_type/A/Enumeration'%ys)
        assert(c == ok_png)
        c = s.url('='+abj+'/%s/UE-enum/1/1/column_attr_columns/A/X%%20Y'%ys)
        assert(c == ok_png)
        c = s.url('=' + abj +'/%s/UE-enum' % ys)
        assert('"columns": "X Y"' in c)

    if do('regtest-bug1'):
       while True:
           c = s.url('='+root+'/0/Dossiers/config_table')
           if '"unload_interval' in c:
              break

       conf = os.path.join('DBregtest','Y0','SDossiers', 'config_table.py')
       try:
          os.unlink(conf + 'c')
       except:
          pass
       ticket_ttl = 1
       utilities.write_file_safe(conf + '.old', utilities.read_file(conf))
       utilities.append_file_safe(conf,'''
cell_change(1,'0_2','check_down_connections_interval',2,"")
cell_change(1,'0_2','unload_interval',2,"")
cell_change(1,'0_2','ticket_time_to_live','%d',"")
''' % ticket_ttl)
       s.stop()
       import glob
       for t in glob.glob(os.path.join('TMP','TICKETS','*')):
           os.unlink(t)
       s.restart(more=['regtest-bug1'])

       c = s.url('='+root+'/0/Dossiers/config_table')
       assert('C(2,"super.user","","","600\\n(' in c) # History

       c = s.url('='+abj+'/%d/Dossiers/regtest-bug1' % uyear)
       assert('runlog' in c)

       # TOMUSS assumes that this page come from the future so it must
       # be from a read-only table (not the case here).
       # So it redirect browser in order to reload the table (read-only)
       c = s.url('='+abj+'/%d/Dossiers/regtest-bug1/10/0' % uyear)
       assert('window.parent.location' in c)
       c = s.url('='+abj+'/%d/Dossiers/regtest-bug1/0/0' % uyear)

       # We are not allowed to see an old page from an other navigator
       assert('window.parent.click_to_revalidate_ticket' in c)

       # This the good page content
       c = s.url('='+abj+'/%d/Dossiers/regtest-bug1/1/0' % uyear,
                 display_log_if_error=False, timeout=1)
       # Because page load does not end
       assert('***TIMEOUT***' in c)
       assert('window.parent.server_answered()' in c)

       # The frame connection is now broken.
       # Wait the page unloading
       while True:
          c = s.url('='+root+'/stat')
          if 'regtest-bug1' not in c:
              # Wait more to be sure
              time.sleep(1)
              break
          time.sleep(1)

       # Create a column
       ok = False
       try:
          c = s.url('='+abj+'/%d/Dossiers/regtest-bug1/1/0/column_attr_title/col_0/TITLE0' % uyear, display_log_if_error=False, stop_if_error=False)
       except http.client.BadStatusLine:
          # The ticket is no more fine : the server does not reply
          ok = True
       assert( ok )

       # Make the ticket last longer because if it is short regtest may fail
       utilities.append_file_safe(conf,
       'cell_change(1,"0_2","ticket_time_to_live","1984","")\n')
       c = s.url('=' + root + '/0/Dossiers/config_table/page_unload')
       assert(_("MSG_page_unload_after") in c)
       c = s.url('=' + root + '/0/Dossiers/config_table')
       assert( 'C("1984","super.user"' in c )

       # The browser attempt to reconnect
       c = s.url('='+abj+'/%d/Dossiers/regtest-bug1/1/0' % uyear,
                 display_log_if_error=False)
       # Because page load does not end
       # assert('***TIMEOUT***' in c)
       assert('window.parent.server_answered()' in c)

       # The ticket is now valid
       c = s.url('='+abj+'/%d/Dossiers/regtest-bug1/1/0/column_attr_title/col_0/TITLE0' % uyear)
       assert(c == ok_png)

       utilities.write_file(conf, utilities.read_file(conf + '.old'))

       s.stop()
       s.restart()

    if do('modifiable-column'):
        c = s.url('=' + abj +'/%s/UE-modifcol' % ys)
        # Modifiable by teacher
        c = s.url('='+abj+'/%s/UE-modifcol/1/0/column_attr_type/A/Bool'%ys)
        assert(c == ok_png)
        c = s.url('='+abj+'/%s/UE-modifcol/1/1/column_attr_modifiable/A/1'%ys)
        assert(c == ok_png)
        # Modifiable by student
        c = s.url('='+abj+'/%s/UE-modifcol/1/2/column_attr_type/B/Bool'%ys)
        assert(c == ok_png)
        c = s.url('='+abj+'/%s/UE-modifcol/1/3/column_attr_modifiable/B/2'%ys)
        assert(c == ok_png)
        # Modifiable by nobody
        c = s.url('='+abj+'/%s/UE-modifcol/1/4/column_attr_type/C/Bool'%ys)
        assert(c == ok_png)
        c = s.url('='+abj+'/%s/UE-modifcol/1/5/column_attr_modifiable/C/0'%ys)
        assert(c == ok_png)
        # Add 2 students
        c = s.url('=' + abj + '/%s/UE-modifcol' % ys
                  + '/1/6/cell_change/0_0/0_0/10800000')
        assert(c == ok_png)
        c = s.url('=' + abj + '/%s/UE-modifcol' % ys
                  + '/1/7/cell_change/0_0/0_1/10800001')
        assert(c == ok_png)

        ss.start()
        c = ss.url('=' + abj + '/%s/10800001' % ys)
        assert('UE-modifcol' in c)
        # assert('UE-modifcol/cell/A/0_1' in c)
        # assert('UE-modifcol/cell/B/0_1' in c)
        # assert('UE-modifcol/cell/C/0_1' not in c)

        c = ss.url('=10800001/%s/' % ys)
        assert('UE-modifcol' in c)
        # assert('UE-modifcol/cell/A/0_1' not in c)
        # assert('UE-modifcol/cell/B/0_1' in c)
        # assert('UE-modifcol/cell/C/0_1' not in c)

        # Not modifiable by student
        c = s.url('=10800001/%s/UE-modifcol' % ys + '/cell/C/0_1/' + _("no"))
        assert('red' in c)
        c = s.url('=10800001/%s/UE-modifcol' % ys + '/cell/A/0_1/' + _("no"))
        assert('red' in c)

        # For the teacher
        c = s.url('=' + abj + '/%s/UE-modifcol' % ys + '/cell/C/0_1/'+_("yes"))
        assert('green' in c)
        c = s.url('=' + abj + '/%s/UE-modifcol' % ys + '/cell/A/0_1/'+_("yes"))
        assert('green' in c)
        c = s.url('=' + abj + '/%s/UE-modifcol' % ys + '/cell/B/0_1/'+_("yes"))
        assert('green' in c)

        # The student can't modify a teacher note
        c = s.url('=10800001/%s/UE-modifcol' % ys + '/cell/B/0_1/' + _("no"))
        assert('red' in c)
        # The student can't modify another student note
        c = s.url('=10800001/%s/UE-modifcol' % ys + '/cell/B/0_0/' + _("no"))
        assert('red' in c)

        # Teacher erase the note
        c = s.url('=' + abj + '/%s/UE-modifcol' % ys + '/cell/B/0_1/')
        assert('green' in c)
        # The student can now modify its note
        c = s.url('=10800001/%s/UE-modifcol' % ys + '/cell/B/0_1/' + _("no"))
        assert('green' in c)
        # The student can change its note
        c = s.url('=10800001/%s/UE-modifcol' % ys + '/cell/B/0_1/' + _("yes"))
        assert('green' in c)

        # Try to send garbage
        c = s.url('=10800001/%s/UE-modifcol' % ys + '/cell/B/0_1/GOOD_OR_BAD')
        assert('green' in c) # No check on cell values : good or bad ?

        # Student look suivi
        # XXX PROBLEM: This test work randomly
        # c = ss.url('=10800001/%s/' % ys)
        # assert('GOOD_OR_BAD' not in c)

        c = ss.url('=10800001/%s/unload/UE-modifcol' % ys)
        c = ss.url('=10800001/%s/' % ys)
        assert('GOOD_OR_BAD' in c)

        
    if do('repetition'):
        c = s.url('=' + abj +'/%s/UE-repetition' % ys)
        c =s.url('='+abj+'/%s/UE-repetition/1/0/column_attr_repetition/A/1'%ys)
        assert(c == ok_png)
        c = s.url('='+abj+'/%s/UE-repetition/1/1/cell_change/A/L1/10' % ys)
        assert(c == ok_png)
        c = s.url('='+abj+'/%s/UE-repetition/1/2/cell_change/A/L2/10' % ys)
        assert(c == bad_png)

        c =s.url('='+abj+'/%s/UE-repetition/1/3/column_attr_repetition/B/1'%ys)
        assert(c == ok_png)
        c = s.url('='+abj+'/%s/UE-repetition/1/4/column_attr_type/B/Enumeration' % ys)
        assert(c == ok_png)
        c = s.url('='+abj+'/%s/UE-repetition/1/5/column_attr_enumeration/B/QQQQ%%20WWWW' % ys)
        assert(c == ok_png)
        c = s.url('='+abj+'/%s/UE-repetition/1/6/cell_change/B/L2/QQQQ' % ys)
        assert(c == ok_png)
        c = s.url('='+abj+'/%s/UE-repetition/1/7/column_attr_title/B/EEE' % ys)
        assert(c == ok_png)
        c = s.url('='+abj+'/%s/UE-repetition/1/8/cell_change/0_0/L3/10800001' % ys)
        assert(c == ok_png)
        c = s.url('='+abj+'/%s/UE-repetition/1/9/cell_change/A/L3/20' % ys)
        assert(c == ok_png)
        c = s.url('='+abj+'/%s/UE-repetition/1/10/column_attr_modifiable/B/2' % ys)
        assert(c == ok_png)

        # Test repetition within grp/seq

        c =s.url('='+abj+'/%s/UE-repetition/1/11/column_attr_repetition/C/-1'%ys)
        assert(c == ok_png)
        c =s.url('='+abj+'/%s/UE-repetition/1/12/cell_change/0_3/L3/grpA'%ys)
        assert(c == ok_png)
        c =s.url('='+abj+'/%s/UE-repetition/1/13/cell_change/0_4/L3/seqA'%ys)
        assert(c == ok_png)
        c =s.url('='+abj+'/%s/UE-repetition/1/14/cell_change/0_3/L2/grpB'%ys)
        assert(c == ok_png)
        c =s.url('='+abj+'/%s/UE-repetition/1/15/cell_change/0_4/L2/seqA'%ys)
        assert(c == ok_png)
        c =s.url('='+abj+'/%s/UE-repetition/1/16/cell_change/0_3/L1/grpA'%ys)
        assert(c == ok_png)
        c =s.url('='+abj+'/%s/UE-repetition/1/17/cell_change/0_4/L1/seqB'%ys)
        assert(c == ok_png)
        c =s.url('='+abj+'/%s/UE-repetition/1/18/column_attr_type/C/Enumeration'%ys)
        c =s.url('='+abj+'/%s/UE-repetition/1/19/column_attr_enumeration/C/EEEE%%20RRRR'%ys)
        c =s.url('='+abj+'/%s/UE-repetition/1/20/cell_change/C/L1/EEEE'%ys)
        assert(c == ok_png)
        c =s.url('='+abj+'/%s/UE-repetition/1/21/cell_change/C/L2/EEEE'%ys)
        assert(c == ok_png)
        c =s.url('='+abj+'/%s/UE-repetition/1/22/column_attr_modifiable/C/2' % ys)
        assert(c == ok_png)
        c =s.url('='+abj+'/%s/UE-repetition/1/23/cell_change/0_3/L4/grpA'%ys)
        assert(c == ok_png)
        c =s.url('='+abj+'/%s/UE-repetition/1/24/cell_change/0_4/L4/seqA'%ys)
        assert(c == ok_png)
        c = s.url('='+abj+'/%s/UE-repetition/1/25/cell_change/0_0/L5/10800002' % ys)
        assert(c == ok_png)
        c =s.url('='+abj+'/%s/UE-repetition/1/26/cell_change/0_3/L5/grpA'%ys)
        assert(c == ok_png)
        c =s.url('='+abj+'/%s/UE-repetition/1/27/cell_change/0_4/L5/seqB'%ys)
        assert(c == ok_png)

        ss.start()
        c = ss.url('=10800001/%s/' % ys)
        assert( '"enumeration": ["", "WWWW"]' in c)
        assert( '"enumeration": ["", "EEEE", "RRRR"]' in c)

        c = ss.url('=10800002/%s/' % ys)
        assert( '"enumeration": ["", "WWWW"]' in c)
        assert( '"enumeration": ["", "RRRR"]' in c)

        c =s.url('=10800001/%s/UE-repetition/cell/C/L3/EEEE' % ys)
        assert('green' in c)

        c =s.url('=10800002/%s/UE-repetition/cell/C/L5/EEEE' % ys)
        assert('red' in c)

        c =s.url('='+abj+'/%s/UE-repetition/1/28/cell_change/C/L4/EEEE'%ys)
        assert(c == bad_png)

    if do('acls'):
        acls = '=' + root + '/0/Dossiers/config_acls/'
        ss.start()
        # User not in LDAP
        c = s.url('=user.1/%s/UE-acls' % ys)
        assert('is_a_teacher = 0' in c and 'initialize_suivi_real()' in c)
        c = s.url(acls)
        assert('grp:referents' in c)
        c = s.url(acls + '1/0/cell_change/a/L1/user.1')
        assert(c == ok_png)
        c = s.url('=user.1/%s/UE-acls' % ys)
        assert('initialize_suivi_real()' in c)
        c = s.url(acls + '1/1/cell_change/b/L1/referents')
        assert(c == ok_png)
        c = s.url('=user.1/%s/UE-acls' % ys)
        assert('runlog(columns, lines)' in c)
        time.sleep(1)
        c = ss.url('=user.1/%s/user.2' % ys)
        assert('is_a_teacher = 1' in c and 'initialize_suivi_real()' in c)
        
        # User in LDAP
        c = s.url('=user.2/%s/UE-acls' % ys)
        assert('runlog(columns, lines)' in c)

        # User in LDAP but not teacher
        c = s.url('=user.3/%s/UE-acls' % ys)
        assert('is_a_teacher = 0' in c and 'initialize_suivi_real()' in c)

    if do('owner'):
        c = s.url('=' + abj +'/%s/UE-owner' % ys)
        assert( 'runlog' in c )
        c = s.url('='+abj+'/%s/UE-owner/1/0/column_attr_type/A/Surname' % ys)
        assert( c == ok_png )
        c = s.url('='+abj+'/%s/UE-owner/1/1/column_attr_columns/A/ID' % ys)
        assert( c == ok_png )
        c = s.url('='+abj+'/%s/UE-owner/1/2/cell_change/0_0/a/10800001' % ys)
        assert( c == ok_png )
        c = s.url('='+abj+'/%s/UE-owner/1/3/cell_change/A/a/FOO' % ys)
        assert( c == bad_png )  # XXX
        c = s.url('='+abj+'/%s/UE-owner/1/4/column_attr_type/A/Text' % ys)
        assert( c == ok_png )
        c = s.url('='+abj+'/%s/UE-owner/1/5/cell_change/A/a/FOO' % ys)
        assert( c == ok_png )

    if do('signature'):
        ss.start()
        c = ss.url('=' + abj +'/%s/10800001' % ys)
        assert( '["Signature", ""]' in c )
        c = ss.url('=p0800001/%s' % ys)
        assert( 'LABEL_signature_new' not in c )
        c = s.url('=' + abj
                  + '/signature_new/p0800001/1/sig_message{{{sig_button}}}')

        assert(utilities._("MSG_saved") in c)
        c = ss.url('=p0800001/%s' % ys)
        assert('AskQuestion' in c)
        assert('tt.masterSurname' in c)
        assert('sig_message' in c)
        assert('\\x3Esig_button<' in c)
        c = s.url('=p0800001/signature/0/sig_button')
        assert( c == ok_png )
        c = ss.url('=p0800001/%s/signatures/p0800002' % ys)
        assert(utilities._('TITLE_signatures') in c)
        assert('sig_message' in c)
        assert(')sig_button<' in c)

    if do('extract'):
        c = s.url('=' + root + '/%s/UE-extract' % ys)
        time.sleep(1)
        c = s.url('=' + root + '/%s/UE-extract' % ys +
                  '/1/0/column_attr_title/col_0/a')
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-extract' % ys +
                  '/1/1/column_attr_title/col_1/b')
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-extract' % ys +
                  '/1/2/cell_change/0_0/L1/10800099')
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-extract' % ys +
                  '/1/3/cell_change/col_0/L1/1')
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-extract' % ys +
                  '/1/4/cell_change/col_1/L1/2')
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-extract' % ys +
                  '/1/5/column_attr_title/col_2/Moy')
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-extract' % ys +
                  '/1/6/column_attr_type/col_2/Moy')
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-extract' % ys +
                  '/1/7/column_attr_columns/col_2/a$20b')
        assert(c == ok_png)
        ss.start()
        c = ss.url('=' + root +'/%s/extract/UE-extract:Moy' % ys)
        assert('<td>10800099<td>1.5' in c)
        
        c = ss.url('=' + root +'/%s/fusion/UE-extract:Moy' % ys)
        assert('<tr><td>10800099<td>10800099Firstname<td>10800099Surname<td>UE-extract<td>1.5' in c)

    if do('cell_writable'):
        c = s.url('=' + root + '/%s/UE-cell_writable' % ys)
        time.sleep(1)
        c = s.url('=' + root + '/%s/UE-cell_writable' % ys +
                  '/1/0/column_attr_title/col_0/a')
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-cell_writable' % ys +
                  '/1/1/cell_change/0_0/L1/10800099')
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-cell_writable' % ys +
                  '/1/2/cell_change/col_0/L1/1')
        assert(c == ok_png)
        
        c = s.url('=' + abj + '/%s/UE-cell_writable' % ys)
        c = s.url('=' + abj + '/%s/UE-cell_writable' % ys +
                  '/2/0/cell_change/col_0/L1/2')
        assert(c == bad_png)

        c = s.url('=' + root + '/%s/UE-cell_writable' % ys +
                  '/1/3/column_attr_cell_writable/col_0/=1')
        assert(c == ok_png)
        c = s.url('=' + abj + '/%s/UE-cell_writable' % ys +
                  '/2/1/cell_change/col_0/L1/2')
        assert(c == ok_png)
        c = s.url('=' + abj + '/%s/UE-cell_writable' % ys +
                  '/2/2/cell_change/col_0/L1/3')
        assert(c == bad_png)

        c = s.url('=' + root + '/%s/UE-cell_writable' % ys +
                  '/1/4/column_attr_cell_writable/col_0/@' + abj)
        assert(c == ok_png)
        c = s.url('=' + abj + '/%s/UE-cell_writable' % ys +
                  '/2/3/cell_change/col_0/L1/4')
        assert(c == ok_png)

    if do('groupcolumn'):
        
        s.url('=' + root + '/%s/UE-groupcolumn' % ys)
        c = s.url('=' + root + '/%s/UE-groupcolumn' % ys +
                  '/1/0/column_attr_title/C0/C0')
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-groupcolumn' % ys +
                  '/1/1/column_attr_title/C1/C1')
        assert(c == ok_png)


        # another user set a cell
        s.url('=' + abj + '/%s/UE-groupcolumn' % ys)
        c = s.url('=' + abj + '/%s/UE-groupcolumn' % ys +
                  '/2/0/cell_change/C1/L12/16.61')

        
        c = s.url('=' + root + '/%s/UE-groupcolumn' % ys +
                  '/1/2/column_attr_groupcolumn/C1/C0')
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-groupcolumn' % ys +
                  '/1/3/column_attr_groupcolumn/C1/C0')
        assert(c == ok_png)
        n = 4
        for student, group in (
                ('10800111', '1'), # 4
                ('10800112', '1'), # 6
                ('10800113', '2'), # 8
                ('10800114', '2'), # 10
                ('10800115', '2'), # 12
                ('10800116', ''),  # 14
                ('10800117', ''),  # 16
                ):
            c = s.url('=' + root + '/%s/UE-groupcolumn' % ys +
                      '/1/%s/cell_change/0_0/L%d/%s' % (n, n, student))
            assert(c == ok_png)
            c = s.url('=' + root + '/%s/UE-groupcolumn' % ys +
                      '/1/%d/cell_change/C0/L%d/%s' % (n+1,n, group))
            assert(c == ok_png)
            n += 2

        # First user modify values
        c = s.url('=' + root + '/%s/UE-groupcolumn' % ys +
                  '/1/%d/cell_change/C1/L4/13.31' % n)
        assert(c == ok_png)
        n += 1
        c = s.url('=' + root + '/%s/UE-groupcolumn' % ys +
                  '/1/%d/cell_change/C1/L8/14.41' % n)
        assert(c == ok_png)
        n += 1
        c = s.url('=' + root + '/%s/UE-groupcolumn' % ys +
                  '/1/%d/cell_change/C1/L14/15.51' % n)
        assert(c == ok_png)

        for cell in (
                (1, 'C1', 'L4', 13.31),
                (1, 'C1', 'L6', 13.31),
                (1, 'C1', 'L8', 14.41),
                (1, 'C1', 'L10', 14.41),
                (2, 'C1', 'L12', 16.61), # untouched
                (1, 'C1', 'L14', 15.51),
                ):
            check('Y%d/S%s/UE-groupcolumn' % (year, semester) + '.py',
                  cell_required = cell, dump=False)
        
    if do('upload'):
        try:
            os.unlink('UPLOAD/%s/UP-upload/A/0_0' % ys)
        except OSError:
            pass
        c = s.url('=' + abj +'/%s/UE-upload' % ys)
        # Modifiable by student
        c = s.url('='+abj+'/%s/UE-upload/1/0/column_attr_type/A/Upload'%ys)
        assert(c == ok_png)
        c = s.url('='+abj+'/%s/UE-upload/1/1/column_attr_modifiable/A/2'%ys)
        assert(c == ok_png)
        c = s.url('='+abj+'/%s/UE-upload/1/2/column_attr_cell_writable/A/=0.016|='%ys)
        assert(c == ok_png)
        # Add student
        c = s.url('=' + abj + '/%s/UE-upload' % ys
                  + '/1/3/cell_change/0_0/0_0/10800000')
        assert(c == ok_png)

        ss.start()
        c = ss.url('=' + abj + '/%s/10800000' % ys)
        assert('UE-upload' in c)
        s.url('=10800000/bad_url') # Create the ticket on GET not POST
        c = s.post('=10800000/%s/UE-upload/upload_post/A/0_0' % ys,
                   fields = ( ("filename", "foo.txt"), ),
                   files = ( ("data", "FOO.TXT", b"the file content"), )
               )
        assert('Uploaded file size in bytes: 16' in c)
        assert('Uploaded file type: text/plain; charset=us-ascii' in c)
        assert('>foo.txt<' in c)
        # assert('No virus found.' in c)
        c = utilities.read_file('UPLOAD/%s/UE-upload/A/0_0' % ys,
                                encoding="bytes")
        assert(c == b"the file content")

        c = s.post('=10800000/%s/UE-upload/upload_post/A/0_0' % ys,
                   fields = ( ("filename", "foo.txt"), ),
                   files = ( ("data", "FOO.TXT", b"the file content 2"), )
               )
        assert('Uploaded file size in bytes: 18' in c)
        c = utilities.read_file('UPLOAD/%s/UE-upload/A/0_0' % ys,
                                encoding="bytes")
        assert(c == b"the file content 2")

        c = s.url('=' + abj +'/%s/UE-upload' % ys)
        assert('C(0.018,"10800000",' in c)
        assert(',"text/plain; charset=us-ascii foo.txt",' in c)
        c = s.post('=10800000/%s/UE-upload/upload_post/A/0_0' % ys,
                   fields = ( ("filename", "foo.txt"), ),
                   files = ( ("data", "FOO.TXT", b"the file content 3"), )
               )
        assert(utilities._("ERROR_value_not_modifiable") in c)

        c = s.url('='+abj+'/%s/UE-upload/1/3/column_attr_cell_writable/A/?<0.0001h'%ys)
        assert(c == ok_png)
        c = s.post('=10800000/%s/UE-upload/upload_post/A/0_0' % ys,
                   fields = ( ("filename", "foo.txt"), ),
                   files = ( ("data", "FOO.TXT", b"the file content 4"), )
               )
        assert(utilities._("ERROR_value_not_modifiable") in c)

        c = s.url('='+abj+'/%s/UE-upload/1/4/column_attr_cell_writable/A/?<0.01h'%ys)
        assert(c == ok_png)
        c = s.post('=10800000/%s/UE-upload/upload_post/A/0_0' % ys,
                   fields = ( ("filename", "foo.txt"), ),
                   files = ( ("data", "FOO.TXT",
                              b"the\rfile\ncontent 5 \201\002"), )
               )
        assert('Your file has been successfuly sent.' in c)
        c = utilities.read_file('UPLOAD/%s/UE-upload/A/0_0' % ys,
                                 encoding="bytes" )
        assert(c == b"the\rfile\ncontent 5 \201\002")
    if do('start_job'):
        c = [[],[],[]]
        t = time.time()
        def f1(c=c):
            c[0].append(time.time()-t)
            time.sleep(0.1)
            return time.time() # Tell that all data before this time is processed
        def f2(c=c):
            c[1].append(time.time()-t)
            time.sleep(0.2)
            return time.time() # Tell that all data before this time is processed
        def f3(c=c):
            c[2].append(time.time()-t)
            time.sleep(0.239)
            return time.time() # Tell that all data before this time is processed
        while time.time() < t + 1:
            utilities.start_job(f1, 0.6, important="f1")
            utilities.start_job(f2, 0.3, important="f2")
            utilities.start_job(f3, 0, important="f3")
            time.sleep(0.001)
        assert(len(c[0]) == 1 and len(c[1]) == 2 and len(c[2]) == 5)
        while len(utilities.current_jobs) != 0:
            time.sleep(0.1)
        assert(len(c[0]) == 2 and len(c[1]) == 2 and len(c[2]) == 5)

    if do('repet-grp'):
        c = s.url('=' + abj +'/%s/UE-repet-grp' % ys)
        c =s.url('='+abj+'/%s/UE-repet-grp/1/0/column_attr_repetition/COL/1'%ys)
        assert(c == ok_png)
        c =s.url('='+abj+'/%s/UE-repet-grp/1/1/column_attr_groupcolumn/COL/Grp'%ys)
        assert(c == ok_png)
        c = s.url('=' + abj + '/%s/UE-repet-grp' % ys +
                  '/1/2/cell_change/0_0/0_0/10800001')
        assert(c == ok_png)
        c = s.url('=' + abj + '/%s/UE-repet-grp' % ys +
                  '/1/3/cell_change/0_3/0_0/A')
        assert(c == ok_png)
        c = s.url('=' + abj + '/%s/UE-repet-grp' % ys +
                  '/1/4/cell_change/0_0/0_1/10800002')
        assert(c == ok_png)
        c = s.url('=' + abj + '/%s/UE-repet-grp' % ys +
                  '/1/5/cell_change/0_3/0_1/A')
        assert(c == ok_png)
        c = s.url('=' + abj + '/%s/UE-repet-grp' % ys +
                  '/1/6/cell_change/COL/0_0/7')
        assert(c == ok_png)
        check('Y%d/S%s/UE-repet-grp.py' % (year, semester),
              cell_required = (1, 'COL', '0_1', 7.))
        c = s.url('=' + abj + '/%s/UE-repet-grp' % ys +
                  '/1/7/cell_change/0_0/0_2/10800003')
        assert(c == ok_png)
        c = s.url('=' + abj + '/%s/UE-repet-grp' % ys +
                  '/1/8/cell_change/0_0/0_3/10800004')
        assert(c == ok_png)
        c = s.url('=' + abj + '/%s/UE-repet-grp' % ys +
                  '/1/9/cell_change/0_3/0_2/B')
        assert(c == ok_png)
        c = s.url('=' + abj + '/%s/UE-repet-grp' % ys +
                  '/1/10/cell_change/0_3/0_3/B')
        assert(c == ok_png)
        c = s.url('='+abj+'/%s/UE-repet-grp/1/11/column_attr_repetition/COL/2'
                  % ys)
        assert(c == ok_png)
        c = s.url('=' + abj + '/%s/UE-repet-grp' % ys +
                  '/1/12/cell_change/COL/0_3/7')
        assert(c == ok_png)
        check('Y%d/S%s/UE-repet-grp.py' % (year, semester),
              cell_required = (1, 'COL', '0_2', 7.))

    if do('nmbr'):
        # Check Nmbr with 0 columns
        c = s.url('=' + abj +'/%s/UE-nmbr' % ys)
        c = s.url('='+abj+'/%s/UE-nmbr/1/0/column_attr_title/A/A' % ys)
        assert( c == ok_png )
        c = s.url('='+abj+'/%s/UE-nmbr/1/1/column_attr_type/A/Nmbr' % ys)
        assert( c == ok_png )
        c = s.url('='+abj+'/%s/UE-nmbr/1/2/cell_change/0_0/0_0/10800100' % ys)
        assert(c == ok_png)
        c = s.url('='+abj+'/%s/UE-nmbr/1/3/column_attr_title/B/B' % ys)
        assert( c == ok_png )
        c = s.url('='+abj+'/%s/UE-nmbr/1/4/column_attr_type/B/Note' % ys)
        assert( c == ok_png )
        c = s.url('='+abj+'/%s/UE-nmbr/1/5/cell_change/B/0_0/11.11' % ys)
        assert(c == ok_png)
        c = s.url('='+abj+'/%s/UE-nmbr/1/6/column_attr_type/C/Moy' % ys)
        assert( c == ok_png )
        c = s.url('='+abj+'/%s/UE-nmbr/1/7/column_attr_columns/C/A%%20B' % ys)
        assert( c == ok_png )
        ss.start()
        c = ss.url('=' + root + '/10800100')
        assert('"columns": "A B"' in c)
        assert(' 11.11,' in c)
        assert(' 5.555,' in c)

    if do('js-api'):
        c = s.url('=' + abj +'/%s/UE-js' % ys)
        data = []
        for script in c.split('<script ')[1:]:
            url = script.split(':%d/' % configuration.server_port
                           )[1].split('"')[0]
            data.append(s.url(url, read_bytes=True))
        utilities.write_file("xxx.js.gz", b''.join(data), encoding="bytes")
        data = []
        for script in c.split('<script>')[1:]:
            script = script.replace("<!--", "")
            script = script.split("</script>")[0].replace("-->", "")
            script = script.replace("\ninitialize()", "\n")
            data.append(script)
        utilities.write_file("xxx.js", '\n'.join(data))
        f = os.popen("""
        (
         cat REGTEST_SERVER/preamble.js xxx.js
         zcat xxx.js.gz
         cat REGTEST_SERVER/tests.js
        ) >xxx_full.js
        (node xxx_full.js || nodejs xxx_full.js) 2>&1 3>&1
        """, "r")
        for c in f.readlines():
            print("NODEJS:" + c.strip())
            if 'tests are fine' in c:
                break
        else:
            js_tests_failed
        f.close()

    if do('import2'):
        s.url('=' + abj + '/%s/UE-imp' % ys)
        c = s.url('=' + abj + '/%s/UE-imp/1/0/column_attr_title/C/N' % ys)
        assert( c == ok_png )
        c = s.url('=' + abj + '/%s/UE-imp/1/1/column_attr_empty_is/C/!Def!'%ys)
        assert( c == ok_png )
        c = s.url('=' + abj + '/%s/UE-imp/1/2/cell_change/0_0/0_0/p0800001'%ys)
        assert(c == ok_png)
        c = s.url('=' + abj + '/%s/UE-imp/1/3/cell_change/0_0/0_1/p0800002'%ys)
        assert(c == ok_png)

        s.url('=' + abj + '/%s/UE-imp2' % ys)
        c = s.url('=' + abj +'/%s/UE-imp2/1/0/cell_change/0_0/0_0/p0800001'%ys)
        assert(c == ok_png)
        c = s.url('=' + abj + '/%s/UE-imp2/1/1/column_attr_title/C/E' % ys)
        assert( c == ok_png )
        u = ('UE-imp/N').replace('/', '$2F')
        c = s.url('=' + abj + ('/%s/UE-imp2/1/2/column_attr_url_import/C/'%ys)
                  + u)
        assert( c == ok_png )
        c = s.url('=' + abj + '/%s/UE-imp2' % ys)
        assert('C("!Def!","*","' in c)

        c = s.url('=' + abj +'/%s/UE-imp2/1/3/cell_change/0_0/0_1/p0800002'%ys)
        assert(c == ok_png)
        c = s.url('=' + abj + '/%s/UE-imp2' % ys)
        assert(c.count("!Def!") == 2)

    if do('average_change'):
        c = s.url('=' + root + '/%s/UE-avg_chg' % ys)
        c = s.url('=' + root + '/%s/UE-avg_chg' % ys +
                  '/1/0/column_attr_title/col_0/a')
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-avg_chg' % ys +
                  '/1/1/column_attr_type/col_1/Moy')
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-avg_chg' % ys +
                  '/1/2/column_attr_title/col_1/Moy')
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-avg_chg' % ys +
                  '/1/3/column_attr_columns/col_1/a')
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-avg_chg' % ys +
                  '/1/4/cell_change/0_0/lin_0/a_login')
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-avg_chg' % ys +
                  '/1/5/cell_change/col_1/lin_0/16.43')
        assert(c == bad_png) # Average not changeable because not master
        c = s.url('=' + root + '/%s/UE-avg_chg' % ys +
                  '/1/6/table_attr_masters/' + abj)
        assert(c == ok_png)
        c = s.url('=' + abj + '/%s/UE-avg_chg' % ys)
        c = s.url('=' + abj + '/%s/UE-avg_chg' % ys +
                  '/2/0/cell_change/col_1/lin_0/16.43')
        assert(c == ok_png) # Average changeable because master
        c = s.url('=' + root + '/%s/UE-avg_chg' % ys)
        assert("16.43" in c)

        # If a value is changed: modified average is not erased server
        # side (except if it is needed)
        c = s.url('=' + root + '/%s/UE-avg_chg' % ys +
                  '/1/7/cell_change/col_0/lin_0/11.11')
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-avg_chg' % ys)
        assert("11.11" in c)
        assert("16.43" in c)

        # No more possible to modify the average if it is a number
        c = s.url('=' + root + '/%s/UE-avg_chg' % ys +
                  '/1/8/cell_change/col_1/lin_0/17.87')
        assert(c == bad_png)
        c = s.url('=' + root + '/%s/UE-avg_chg' % ys)
        assert("17.87" not in c)

        # Erase value: average is modifiable by master
        time.sleep(1)
        c = s.url('=' + root + '/%s/UE-avg_chg' % ys +
                  '/1/9/cell_change/col_0/lin_0/ABJUS')
        assert(c == ok_png)

        c = s.url('=' + root + '/%s/UE-avg_chg' % ys +
                  '/1/10/cell_change/col_1/lin_0/9.99')
        assert(c == bad_png)
        c = s.url('=' + abj + '/%s/UE-avg_chg' % ys +
                  '/2/1/cell_change/col_1/lin_0/9.99')
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-avg_chg' % ys)
        assert('C("ABJUS"' in c)
        date = c.split('C(9.99,"' + abj + '","')[1][:14]

        # Must be possible to set the same value
        c = s.url('=' + root + '/%s/UE-avg_chg' % ys +
                  '/1/11/cell_change/col_0/lin_0/')
        assert(c == ok_png)
        time.sleep(1)
        c = s.url('=' + abj + '/%s/UE-avg_chg' % ys +
                  '/2/2/cell_change/col_1/lin_0/9.99')
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-avg_chg' % ys)
        date2 = c.split('C(9.99,"' + abj + '","')[1][:14]
        assert(date2 > date)

    if do('variable'):
        import re
        for k, v in tests_config.vars.items():
            c = s.url('get_var/' + k)
            assert(ast.literal_eval(c) == v[1])
        c = s.url('=' + root + '/0/Variables/_variables')
        c = re.sub('"[0-9]+"', '""', c)
        assert( 'C("int","?",""),C("","?","")' in c)
        assert( 'C("tuple","?",""),C("(8, 9)","?","")' in c)
        assert( 'C("str","?",""),C("\'7\'","?","")' in c)
        assert( 'C("list","?",""),C("[10, 11]","?","")' in c)
        c = s.url('=' + root +
                  '/0/Variables/_variables/2/0/cell_change/2/test_int/2017')
        assert(c == ok_png)
        c = s.url('get_var/test_int')
        assert(c == "2017")
        c = s.url('=' + root +
                  '/0/Variables/_variables/2/1/cell_change/2/test_int/a')
        assert(c == bug_png)
        c = s.url('get_var/test_int')
        assert(c == "2017")
        c = s.url('=' + root +
                  '/0/Variables/_variables/2/2/cell_change/2/test_list/[0,1]')
        assert(c == ok_png)
        c = s.url('get_var/test_list')
        assert(c == "[0, 1]")
        c = s.url('=' + root +
                  '/0/Variables/_variables/2/3/cell_change/2/test_list/')
        assert(c == bug_png)

    if do('public'):
        s.url('=' + abj + '/%s/UE-public' % ys)
        c = s.url('='+abj+'/%s/UE-public/1/0/column_attr_title/C/ColT' % ys)
        assert(c == ok_png)
        c = s.url('='+abj+'/%s/UE-public/1/1/cell_change/C/L/12.34' % ys)
        assert(c == ok_png)
        ss.start()
        c = ss.url('/public/%s/UE-public' % ys)
        assert(c == '')
        c = s.url('='+abj+'/%s/UE-public/1/2/column_attr_visibility/C/3' % ys)
        assert(c == ok_png)
        c = ss.url('=' + abj + '/%s/unload/UE-public' % ys)
        assert(c == '')
        c = ss.url('public/%s/UE-public' % ys)
        cols = ast.literal_eval(c.split("var columns = ")[1].split(";")[0])
        assert(len(cols) == 1)
        col = cols[0]
        assert(col["author"] == abj)
        assert(col["title"] == "ColT")
        assert(col["visibility"] == 3)
        lines = ast.literal_eval(c.split("var lines = ")[1].split(";")[0])
        assert(len(lines) == 1)
        line = lines['L']
        assert(len(line) == 1)
        cell = line[0]
        assert(len(cell) == 3)
        assert(cell[0] == 12.34)
        assert(cell[1] == abj)

        c = s.url('='+abj+'/%s/UE-public/1/3/column_attr_visibility/D/3' % ys)
        assert(c == ok_png)
        c = s.url('='+abj+'/%s/UE-public/1/4/column_attr_cell_writable/D/' % ys)
        assert(c == ok_png)
        c = s.url('='+abj+'/%s/UE-public/1/5/column_attr_modifiable/D/2' % ys)
        assert(c == ok_png)
        c = s.url('='+abj+'/%s/UE-public/1/6/cell_change/D/L/6.78' % ys)
        assert(c == ok_png)
        c = s.url('='+abj+'/%s/UE-public/1/7/column_attr_type/D/Upload' % ys)
        assert(c == ok_png)
        c = ss.url('=' + abj + '/%s/unload/UE-public' % ys)
        assert(c == '')
        c = ss.url('public/%s/UE-public' % ys)
        cols = ast.literal_eval(c.split("var columns = ")[1].split(";")[0])
        assert(len(cols) == 2)
        assert("modifiable" not in cols[1])
        lines = ast.literal_eval(c.split("var lines = ")[1].split(";")[0])
        assert(len(lines) == 1)
        line = lines['L']
        assert(len(line) == 2)
        cell = line[1]
        assert(len(cell) == 3)
        assert(cell[0] == 6.78)
        assert(cell[1] == abj)

        c = s.post('=' + abj + '/%s/UE-public/upload_post/D/L' % ys,
                   fields = ( ("filename", "foo.txt"), ),
                   files = ( ("data", "FOO.TXT", b"the file content"), )
               )
        assert('Your file has been successfuly sent.' in c)

        c = s.url('=' + abj + '/%s/UE-public/upload_get/D/L' % ys)
        assert(c == "the file content")
        c = s.url('%s/UE-public/upload_get/D/L' % ys)
        assert('You are here because you followed a direct link inside TOMUSS'
               in c)
        c = s.url('%s/UE-public/upload_get_public/D/L' % ys)
        assert(c == "the file content")
        c = s.url('=garbage/%s/UE-public/upload_get_public/D/L' % ys)
        assert(c == "the file content")

        # Add a public with login
        c = s.url('='+abj+'/%s/UE-public/1/8/column_attr_visibility/E/4' % ys)
        assert(c == ok_png)
        c = s.url('='+abj+'/%s/UE-public/1/9/cell_change/E/L/13.57' % ys)
        assert(c == ok_png)
        c = ss.url('=' + abj + '/%s/unload/UE-public' % ys)
        c = ss.url('public/%s/UE-public' % ys)
        assert('13.57' not in c)
        c = ss.url('=john.doe/public_login/%s/UE-public' % ys)
        assert('13.57' in c)

if '1' in sys.argv:
   sys.argv.remove('1')
   only_once = True
else:
   only_once = False

os.system("ps -fle | grep ./tomuss")
   
n = 0
m = []
while True:
    start = Server.start_time = time.time()
    exit_status = 1
    try:
        tests()
        exit_status = 0
        print('Test fine')
    except AssertionError:
        if c == '':
            print('assert: empty !!!!!')
        elif c == bad_png:
            print('assert: bad_png')
        elif c == ok_png:
            print('assert: ok_png')
        elif c == bug_png:
            print('assert: bug_png')
        else:
            print("Unknown value:", str(c)[:1000])
            f = open('xxx.html', 'w', encoding = "utf-8")
            f.write(c)
            f.close()
            print(c)
        print('End of regressions tests : failure')
        traceback.print_exc(file=sys.stdout)
        break
    except:
        traceback.print_exc(file=sys.stdout)
        break
    finally:
        try:
            s.stop()
        except:
            shutil.rmtree('DBregtest', ignore_errors=True)
            shutil.rmtree('BACKUP_DBregtest', ignore_errors=True)
        if ss and ss.started:
            ss.stop()

        if exit_status == 0 and do('sync'):
            assert(os.system("cd REGTEST_SERVER ; ./sync.py") == 0)
            
        m.append('Running time : %g seconds' % (time.time() - start))
        for i in m:
            print(i)
        if only_once:
            break

sys.exit(exit_status)
