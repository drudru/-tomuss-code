#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2009-2012 Thierry EXCOFFIER, Universite Claude Bernard
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

import sys
import os
import shutil
import httplib

sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), '..'))


import configuration
import utilities
from server import Server, ServerSuivi, check
import time
configuration.regtest = True


import regtestpatch
regtestpatch.do_patch()

root     = configuration.root[0]
abj      = configuration.invited_abj_masters[1]
invited  = configuration.invited_teachers[0]
assert( root != abj )

configuration.language = 'en'

ok_png = utilities.read_file('../FILES/ok.png')
bad_png = utilities.read_file('../FILES/bad.png')
bug_png = utilities.read_file('../FILES/bug.png')
unauthorized_html = utilities._("MSG_new_page_unauthorized")
not_in_demo_mode = utilities._("MSG_evaluate")

year = configuration.year_semester[0]
semester = configuration.year_semester[1]
uyear = utilities.university_year()
ys = '%d/%s' % (year, semester)
ys_old = '%d/%s' % (year-1, semester)

abj_date_old      = '1/1/%d' % (utilities.university_year()-2)
abj_date_previous = '1/1/%d' % (utilities.university_year()-1)
abj_date_current  = '1/1/%d' % (utilities.university_year())
abj_date_next     = '31/12/%d' % (utilities.university_year()+1)

print ys, utilities.university_year()

names = open('xxx.names','w')

def do(t):
    names.write(' ' + t)
    names.flush()
    c = len(sys.argv) == 1 or t in sys.argv or do.found
    if c:
        print t
        do.found = True
    return c
do.found = False


if len(sys.argv) == 1:
    print 'You can indicate in parameters the tests you want to do'

c = ''
s = ''
ss = ''

done = {}

def create_tt():
    if 'create_tt' in done:
        return
    done['create_tt'] = True

    global c
    c = s.url('=' + abj + '/%d/Dossiers/tt' % utilities.university_year())
    assert('Col({the_id:"0_10",type:"Text",author:"*",position:10,title:"%s",width:13})' % utilities._("COL_TITLE_tt_remarks") in c)

    c = s.url('=' + abj + '/%d/Dossiers/tt' % utilities.university_year()
              + '/1/0/cell_change/0_0/0_0/10800000')
    assert( c == ok_png)
    c = s.url('=' + abj + '/%d/Dossiers/tt' % utilities.university_year()
              + '/1/1/cell_change/0_1/0_0/P')
    assert( c == ok_png)
    c = s.url('=' + abj + '/%d/Dossiers/tt' % utilities.university_year()
              + '/1/2/cell_change/0_2/0_0/N')
    assert( c == ok_png)
    c = s.url('=' + abj + '/%d/Dossiers/tt' % utilities.university_year()
              + '/1/3/cell_change/0_3/0_0/1')
    assert( c == ok_png)
    c = s.url('=' + abj + '/%d/Dossiers/tt' % utilities.university_year()
              + '/1/4/cell_change/0_4/0_0/1')
    assert( c == ok_png)
    c = s.url('=' + abj + '/%d/Dossiers/tt' % utilities.university_year()
              + '/1/5/cell_change/0_5/0_0/1')
    assert( c == ok_png)
    c = s.url('=' + abj + '/%d/Dossiers/tt' % utilities.university_year()
              + '/1/6/cell_change/0_6/0_0/OUI')
    assert( c == ok_png)
    c = s.url('=' + abj + '/%d/Dossiers/tt' % utilities.university_year()
              + '/1/7/cell_change/0_7/0_0/OUI')
    assert( c == ok_png)
    c = s.url('=' + abj + '/%d/Dossiers/tt' % utilities.university_year()
              + '/1/8/cell_change/0_10/0_0/TTT')
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
    assert(utilities._("MSG_referent_get_done") in c)
    assert('10900000' in c)
    
    c = s.url('=' + abj + '/%s/referents_students' % ys +
              '/2/2/cell_change/0/line_0/10800000')
    assert(c == ok_png)



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
        # First load : progressive display
        c = s.url('=' + abj + '/0/Preferences/'+utilities.login_to_module(abj))
        lines_id = ['current_suivi', 'display_tips', 'favoris_sort',
                    'interface', 'invert_name', 'language', 'nr_cols',
                    'nr_favorites', 'nr_lines', 'page_step', 'scrollbar_right',
                    'v_scrollbar', 'v_scrollbar_nr', 'zebra_step']
        nr_columns = 4
        nr_pages = 3
        nr_cells = len(lines_id) * (nr_columns-1)
        check('Y0/SPreferences/' + utilities.login_to_module(abj) + '.py',
              masters_expected = [abj], nr_pages = nr_pages,
              nr_columns = nr_columns, lines_id = lines_id,
              nr_cells = nr_cells,
              dump=False)

        # Second load : full table is here
        c = s.url('=' + abj + '/0/Preferences/'+utilities.login_to_module(abj))
        assert('P("zebra_step",[' in c)
        assert('Col({the_id:"0_2",type:"Text",author:"*",freezed:"F",hidden:1,position:2,title:"%s",width:2})' % utilities._("COL_TITLE_order") in c)
        assert('Xcell_change(' not in c)
        assert("x.value=" not in c)
        nr_pages += 1
        check('Y0/SPreferences/' + utilities.login_to_module(abj) + '.py',
              masters_expected = [abj], nr_pages = nr_pages,
              nr_columns = nr_columns, lines_id = lines_id,
              nr_cells = nr_cells,
              dump=False)

        # Try to change explanation : impossible
        c = s.url('='+abj+'/0/Preferences/' + utilities.login_to_module(abj) +
                  '/2/0/cell_change/0_0/display_tips/_A_')
        assert(c == bad_png)
        check('Y0/SPreferences/' + utilities.login_to_module(abj) + '.py',
              masters_expected = [abj], nr_pages = nr_pages,
              nr_columns = nr_columns, lines_id = lines_id,
              nr_cells = nr_cells,
              dump=False)

        # Try to change recommended value : impossible
        c = s.url('='+abj+'/0/Preferences/' + utilities.login_to_module(abj) +
                  '/2/1/cell_change/0_1/display_tips/_B_')
        assert(c == bad_png)
        check('Y0/SPreferences/' + utilities.login_to_module(abj) + '.py',
              masters_expected = [abj], nr_pages = nr_pages,
              nr_columns = nr_columns, lines_id = lines_id,
              nr_cells = nr_cells,
              dump=False)

        # Try to change value : ok
        c = s.url('='+abj+'/0/Preferences/' + utilities.login_to_module(abj) +
                  '/2/2/cell_change/0_3/display_tips/_D_')
        assert(c == ok_png)
        nr_cells += 1
        check('Y0/SPreferences/' + utilities.login_to_module(abj) + '.py',
              masters_expected = [abj], nr_pages = nr_pages,
              nr_columns = nr_columns, lines_id = lines_id,
              nr_cells = nr_cells,
              cell_required = (2,'0_3','display_tips','_D_'),
              dump=False)

        c = s.url('=' + abj + '/0/Preferences/'+utilities.login_to_module(abj))
        assert("'display_tips': '_D_'" in c)


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
        assert('Col({the_id:"col_0",type:"Note",author:"%s",position:0,title:"TITLE0"})' % abj in c)
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
        assert('Col({the_id:"col_0",type:"Note",author:"%s",position:0,title:"TITLE0"})' % abj in c)
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
        assert('Cheater' in c or c == bug_png)

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
                  '/1/1/cell_change/col_0/line_0/~`!@%23$%25^%26*()%2B[]{}|\\;:\'"%01%02.,%3F')
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
        assert("['0', 'Dossiers', 'UE-INF20UE2']" in c)
        c = s.url('=' + root + '/0/Dossiers/UE-INF20UE2')
        assert('TITLE0' in c)
        assert('_TABLE_COMMENT_' in c)
        assert('MARTIN' not in c)

        # Copy content without history
        c = s.url('=' + root + '/%s/UE-INF20UE2/tablecopy/0/Dossiers/content'
                  % ys)
        assert('OK' not in c) # Overwrite not allowed
        c = s.url('=ue1.master/0/Dossiers/UE-INF20UE2/delete_this_table')
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
        a = utilities.read_file('../DBregtest/Y0/SDossiers/UE-INF20UE2.py')
        b = utilities.read_file('../DBregtest/Y%d/S%s/UE-INF20UE2.py' % (
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
        assert('comment:"_COMMENT4_",' in c)
        assert('Col({the_id:"col_0",type:"Note",author:"%s",comment:"_COMMENT_",position:6,title:"TITLE0"})' % root in c)

    if do('ue2'):
        # See 'tomuss.py' for more information on this case
        c = s.url('=' + root + '/%s/UE-INF20UE2' % ys)
        assert('P("0_0",[C("10800000","*","' in c)
        assert('),C("Jacques","*","' in c)
        assert('),C("MARTIN","*","' in c)

    if do('abj'):
        c = s.url('=' + abj + '/%s/abj' % ys)
        assert('abj.js' in c)
        c = s.url('=' + abj + '/%s/abj/display/10800000' % ys)
        # The student is not in any UE
        assert("ues_without_da(['UE-INF20UE2', 'UE-INF20UE2L'])" in c)

        c = s.url('=' + abj + '/%s/abj/0/10800000/add_da/UE-UE1/1/2/3/com1' % ys)
        assert(c == ok_png)
        c = s.url('=' + abj + '/%s/abj/display/10800000' % ys)
        assert("display_da([['UE-UE1','1/2/3','%s',\"com1\"]])" % abj in c)

        c = s.url('=' + abj + '/%s/abj/0/10800000/add_da/UE-UE1/1/2/3/com2' % ys)
        assert(c == ok_png)
        c = s.url('=' + abj + '/%s/abj/display/10800000' % ys)
        assert("display_da([['UE-UE1','1/2/3','%s',\"com1\"]])" % abj in c)

        c = s.url('=' + abj + '/%s/abj/0/10800000/add_da/UE-INF20UE2/%d/1/1/com2' % (ys,year))
        assert(c == ok_png)
        c = s.url('=' + abj + '/%s/abj/display/10800000' % ys)
        
        assert("display_da([['UE-UE1','1/2/3','%s',\"com1\"],['UE-INF20UE2','%d/1/1','%s',\"com2\"]])" % (abj, year, abj) in c)

        c = s.url('=' + abj + '/%s/abj/0/10800000/rem_da/UE-UE1' % ys)
        assert(c == ok_png)
        c = s.url('=' + abj + '/%s/abj/display/10800000' % ys)
        assert("display_da([['UE-INF20UE2','%d/1/1','%s',\"com2\"]])" % (year, abj) in c)


        c = s.url('=' + abj + '/%s/abj/0/10800000/addabj/%s/M/%s/A/com4' % (
            ys, abj_date_old, abj_date_previous))
        assert(c == ok_png)
        c = s.url('=' + abj + '/%s/abj/display/10800000' % ys)
        assert("display_da([['UE-INF20UE2','%d/1/1','%s',\"com2\"]])" % (year, abj) in c)
        assert("display_abjs([['%sM','%sA','%s',\"com4\"]])" % (
            abj_date_old, abj_date_previous, abj) in c)

        c = s.url('=' + abj + '/%s/abj/0/10800000/addabj/%s/M/%s/A/com5' % (
            ys, abj_date_current, abj_date_next))
        assert(c == ok_png)
        c = s.url('=' + abj + '/%s/abj/display/10800000' % ys)
        assert("display_da([['UE-INF20UE2','%d/1/1','%s',\"com2\"]])" % (year, abj) in c)
        assert("display_abjs([['%sM','%sA','%s',\"com4\"],['%sM','%sA','%s',\"com5\"]])" % (
            abj_date_old, abj_date_previous, abj,
            abj_date_current, abj_date_next, abj) in c)

        c = s.url('=' + abj + '/%s/abj/0/10800000/delabj/%s/M/%s/A' % (
            ys, abj_date_old, abj_date_previous))
        assert(c == ok_png)
        c = s.url('=' + abj + '/%s/abj/display/10800000' % ys)
        assert("display_da([['UE-INF20UE2','%d/1/1','%s',\"com2\"]])" % (year, abj) in c)
        assert("display_abjs([['%sM','%sA','%s',\"com5\"]])" % (
            abj_date_current, abj_date_next, abj) in c)

        # Add a DA in licence
        # c = s.url('=' + abj + '/%s/abj/0/10800000/add_da/UE-INF20UE2L/%d/1/1' % (ys,year))

        c = s.url('=' + abj + '/%s/abj/alpha.xls' % ys)
        assert('<tbody id="t"><tr><td>10800000firstname</td><td>10800000surname</td><td>10800000</td><td>ABJ</td><td>%sM</td><td>%sA</td></tr>\n<tr><td>10800000firstname</td><td>10800000surname</td><td>10800000</td><td>DAS</td><td>UE-INF20UE2</td><td>%d/1/1</td></tr>\n</tbody></table>' % (
            abj_date_current, abj_date_next, year))

        # No messages sent because there is no UE master mail
        c = s.url('=' + abj + '/%s/abj/list_mail' % ys)
        assert('UE-INF20UE2L: ' in c)
        assert('UE-INF20UE2: ' not in c)
        assert(utilities._("MSG_no_master") in c)
        assert(utilities._("MSG_abj_send") % 0 in c)

        create_u2()

        # See 'tomuss.py' for more information on this case
        c = s.url('=' + root + '/%s/UE-INF20UE2' % ys)
        assert('P("0_0",[C("10800000","*","' in c)
        assert('),C("Jacques","*","' in c)
        assert('),C("MARTIN","*","' in c)
        assert('),C(11.11,"%s","' % root in c)
        assert("'10800000':\"jacques@martin\"" in c)
        assert('change_abjs({"10800000":[[["%sM","%sA","com5"]],[["UE-INF20UE2","%d/1/1","com2"]],""]});' % (
            abj_date_current, abj_date_next, year) in c)

        c = s.url('=' + root + '/%s/UE-INF20UE2/resume' % ys)
        assert(utilities._("TH_ABJ_list") in c)
        assert('10800000 10800000SURNAME 10800000Firstname' in c)
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
        assert("'10800000':\"jacques@martin\"" in c)
        assert('change_abjs({"10800000":[[["%sM","%sA","com5"]],[["UE-INF20UE2","%d/1/1","com2"]],""]});' % (
            abj_date_current, abj_date_next, year) in c)

        c = s.url('=' + root + '/%s/UE-INF20UE2/resume' % ys)
        assert(utilities._("TH_ABJ_list") in c)
        assert('10800000 10800000SURNAME 10800000Firstname' in c)
        # assert('Du %s matin au %s apr' % (
        #    abj_date_current, abj_date_next) in c)
        assert(str(abj_date_current) in c)
        assert(str(abj_date_next) in c)
        # assert('avec une DA' in c)
        # assert('partir du %d/1/1' % year in c) # XXX


    if do('extension'):
        c = s.url('=' + abj + '/%s/extension' % ys)
        c = s.url('=' + abj + '/%s/extension/1/0/table_attr_masters/' % ys + abj)
        assert( c == ok_png)
        c = s.url('=' + abj + '/%s/extension/extension' % ys)
        assert( utilities._("MSG_extension_ok").split('\n')[1] in c)

    if do('tt'):
        create_tt()

        c = s.url('=' + root + '/%s/UE-INF20UE2' % ys)
        assert(utilities._("COL_COMMENT_+room") + '\\nTTT\\n' in c)
        assert(utilities._("COL_COMMENT_+write") + ' : 1/3\\n' in c)
        assert(utilities._("COL_COMMENT_+speech") + ' : 1/3\\n' in c)
        assert(utilities._("COL_COMMENT_+practical") + ' : 1/3\\n' in c)
        assert(utilities._("COL_COMMENT_+assistant") in c)

        s.stop()
        s.restart()

        c = s.url('=' + root + '/%s/UE-INF20UE2' % ys)
        assert(utilities._("COL_COMMENT_+room") + '\\nTTT\\n' in c)
        assert(utilities._("COL_COMMENT_+write") + ' : 1/3\\n' in c)
        assert(utilities._("COL_COMMENT_+speech") + ' : 1/3\\n' in c)
        assert(utilities._("COL_COMMENT_+practical") + ' : 1/3\\n' in c)
        assert(utilities._("COL_COMMENT_+assistant") in c)

        c = s.url('=' + root + '/%s/UE-INF20UE2/resume' % ys)
        assert('- TTT' in c)
        assert(utilities._("COL_COMMENT_+room")  in c)
        assert(utilities._("COL_COMMENT_+assistant") in c)
        assert(utilities._("COL_COMMENT_+practical") + ' : 1/3' in c)
        assert(utilities._("COL_COMMENT_+write") + ' : 1/3' in c)
        assert(utilities._("COL_COMMENT_+speech") + ' : 1/3' in c)

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
        assert('''columns = [
Col({the_id:"col_1",type:"Note",author:"%s",position:0,title:"TITLE1"})
];''' % abj in c)

    if do('referents'):
        create_referents()

    if do('rss'):
        create_u2()
        ss.start()
        c = ss.url('%s/rss/10800000' % ys)
        assert(utilities._("MSG_suivi_student_RSS_forbiden_title") in c)
        key = utilities.manage_key('LOGINS', '10800001/rsskey')
        assert(key is False)
        c = ss.url('=%s/%s/%%2010800000' % (root, ys))
        key = utilities.manage_key('LOGINS', '10800000/rsskey')
        time.sleep(1)
        print key
        print os.getcwd()
        assert(key is not False)
        c = ss.url('%s/rss/%s' % (ys, key))        
        # assert('UE-INF20UE2 : TITLE0 : 22.22/20' in c)
        assert('<title>UE-INF20UE2 : TITLE0 : 11.11/20</title>' in c)

    if do('suivi'):
        create_tt()
        create_referents()
        create_u2()
        ss.start()
        c = ss.url('=' + abj + '/%s/10800000' % ys)
        assert('/=%s/%s/UE-INF20UE2\\">UE-INF20UE2 </a>' % (abj,ys) in c)
        assert('Col({the_id:"col_0",type:"Note",author:"%s",position:6,title:"TITLE0"})' % root in c)
        assert('),C(11.11,"%s","' % root in c)
        assert(r"\"MSG_Note_rank_before\",\"\x3Cb\x3E1\x3C/b\x3E\");\nWrite(\"MSG_Note_rank_middle\",\"\x3Cb\x3E1\x3C/b\x3E\");\nWrite(\"MSG_Note_rank_after_1\");\x3C/script\x3E\x3Cbr\x3E\x3Cscript\x3E\nWrite(\"MSG_Note_rank_before\",\"\x3Cb\x3E2\x3C/b\x3E\");\nWrite(\"MSG_Note_rank_middle\",\"\x3Cb\x3E2\x3C/b\x3E\");\nWrite(\"MSG_Note_rank_after_2\"" in c)
        assert(utilities._("MSG_cell_message")+"<em>_TABLE_COMMENT_</em>" in c)

        c = s.url('=' + root + '/%s/UE-XXX9999L' % ys)
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
        assert('/=%s/%s/UE-INF20UE2\\">UE-INF20UE2 </a>' % (abj,ys) in c)
        assert('/=%s/%s/UE-XXX9999L\\">UE-XXX9999L </a>' % (abj,ys) in c)

        assert(r'''"TITLE0": ["\x3Cselect class=\"hidden\" onchange=\"_cell(this,'http://''' in c)
        assert(r'''/=%s/%d/Printemps/UE-XXX9999L/cell/col_0/0_0');\"\x3E\x3Coption value=\"\"  selected=\"1\"\x3E\x3C/option\x3E\x3Coption value=\"OUI\" \x3EOUI\x3C/option\x3E\x3Coption value=\"NON\" \x3ENON\x3C/option\x3E\x3C/select\x3E","",""]''' % (abj, year) in c)
        assert('toto' in c)

        c = s.url('=' + abj + '/%s/UE-XXX9999L/cell/col_0/0_0/OUI' % ys)
        assert('<body style="background:green">' == c)

        c = ss.url('=' + abj + '/%s/unload/UE-XXX9999L' % ys)
        assert(c == '')

        c = ss.url('=' + abj + '/%s/10800000' % ys)
        assert('/=%s/%s/UE-INF20UE2\\">UE-INF20UE2 </a>' % (abj,ys) in c)
        assert('/=%s/%s/UE-XXX9999L\\">UE-XXX9999L </a>' % (abj,ys) in c)
        assert(r'''"TITLE0": ["\x3Cselect class=\"hidden\" onchange=\"_cell(this,'http://''' in c)
        assert(r'''/=%s/%s/Printemps/UE-XXX9999L/cell/col_0/0_0');\"\x3E\x3Coption value=\"\" \x3E\x3C/option\x3E\x3Coption value=\"OUI\"  selected=\"1\"\x3EOUI\x3C/option\x3E\x3Coption value=\"NON\" \x3ENON\x3C/option\x3E\x3C/select\x3E","",""]''' % (abj, year) in c)

        c = s.url('=' + root + '/%s/UE-XXX9999L/cell/col_0/0_0/NON' % ys)
        assert('<body style="background:red">' == c)
        

    if do('suivistat'):
        create_tt()
        create_referents()
        create_u2()
        ss.start()
        c = ss.url('=' + abj + '/%s/%s' % (ys, root) )
        assert('/=%s/%s/UE-INF20UE2/=full_filter=@%s" target="_blank">%s %s UE-INF20UE2<' % (abj, ys, root, year, semester) in c)
        assert(utilities._("MSG_suivi_student_ue_changes") % (3,1) in c)

        c = ss.url('=' + root + '/%s/uninterested' % ys )
        assert('10800000' in c)
        assert('10800001' not in c)
        assert('<td>1</td>' in c)

        c = ss.url('=' + root + '/%s/*3' % ys )
        assert(utilities._("MSG_suivi_referents_nr_referents") + '3' in c)
        assert(utilities._("MSG_suivi_referents_nr_students") + '2' in c)

        c = ss.url('=' + abj + '/%s/*1' % ys )
        assert(utilities._("TITLE_suivi_bad_student") in c)
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
        assert(utilities._("COL_TITLE_nb_cells_entered") in c)
        assert('{"0": [C("%s"),' % abj in c)

        c = ss.url('=' + abj + '/%s/*2' % ys )
        assert(utilities._("COL_TITLE_nb_teachers") in c)
        # assert('P([C("teachers","*"),' in c)
        assert('"1": [C("UE-INF20UE2"),' in c)

    if do('private'):
        c = s.url('=' + root + '/%s/UE-INF11UE2' % ys)
        c = s.url('=' + root + '/%s/UE-INF11UE2/1/0/table_attr_masters/' % ys + root)
        assert( c == ok_png)
        c = s.url('=' + root + '/%s/UE-INF11UE2/1/1/table_attr_private/1' % ys)
        assert( c == ok_png)
        c = s.url('=' + abj + '/%s/UE-INF11UE2' % ys)
        assert(utilities._("MSG_new_page_unauthorized") in c)
        c = s.url('=' + root + '/%s/UE-INF11UE2/1/2/cell_change/0_0/0_0/10800000' % ys)
        c = s.url('=' + root + '/%s/UE-INF11UE2/1/3/cell_change/0_3/0_0/X'% ys)
        assert( c == ok_png)
        ss.start()
        c = ss.url('%s/rss2/UE-INF11UE2' % ys)
        assert(utilities._("MSG_suivi_student_RSS_table").split("<br>")[1] % 4
               in c)
        c = ss.url('=' + abj + '/%s/10800000' % ys)
        assert('"Grp": ["X","",""],' in c)


    if do('resume'):
        create_u2()
        ss.start()
        c = ss.url('=' + root + '/%s/resume/UE-INF20UE2/UE-INF20UE2' % ys)
        assert('lines = {"0": [C("10800001"),C(),C(),C(1),C(1),C()],\n"1": [C("10800000"),C("Jacques"),C("MARTIN"),C(1),C(1),C()]}' in c)

    if do('delete_this_table'):
        create_u2()
        c = s.url('=' + abj + '/%s/UE-INF20UE2/delete_this_table' % ys)
        assert(utilities._("MSG_extension_not_master") in c)
        c = s.url('=ue1.master/%s/UE-INF20UE2/delete_this_table' % ys)
        assert(utilities._("MSG_delete_this_table_done") in c)
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
        now_plus_32_days = time.strftime('%Y%m%d',
                                         time.localtime(time.time()+86400*63)
                                         )
        c = s.url('=' + root + '/%s/UE-INF20UE9/1/3/column_attr_visibility_date/col_0/%s' % (ys, now_plus_32_days))
        assert(c == bug_png)
        now_plus_30_days = time.strftime('%Y%m%d',
                                         time.localtime(time.time()+86400*30)
                                         )
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
        assert('/=%s/%s/UE-INF20UE9\\">UE-INF20UE9 </a>' % (abj,ys) in c)
        # The rank is twice in the file
        c = c.replace('7.77','',1)
        assert('7.77' in c)
        c = c.replace('7.77','',1)
        assert('7.77' not in c)
        c = c.replace('8.88','',1)
        assert('8.88' in c)
        c = c.replace('8.88','',1)
        assert('8.88' not in c)
        # This history is visible
        assert('1.234' in c)

        # The student the rank 7.77 is not in the file (not visible)
        # And the rank 8.88 twice
        c = ss.url('=' + abj + '/%s/%%2010123456' % ys)
        assert('<h2 class="title">UE-INF20UE9 : </h2>' in c)
        assert('7.77' not in c)
        
        c = c.replace('8.88','',1)
        assert('8.88' in c)
        c = c.replace('8.88','',1)
        assert('8.88' not in c)
        # This history is not visible
        assert('1.234' not in c)

    if do('import'):
        s.url('=' + root + '/%s/UE-INF21UE9' % ys)
        c = s.url('=' + root + '/%s/UE-INF21UE9/1/0/column_attr_title/col_0/T1' % ys)
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-INF21UE9/1/1/column_attr_title/col_1/T2' % ys)
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-INF21UE9/1/2/cell_change/0_0/0_0/10123456' % ys)
        assert(c == ok_png)
        f = open('xxx.csv', 'w')
        f.write('qqqq,qqq,qqqq\n10123456,4.4444,XXXXYYYY\nttt,yyy,uuu,uu')
        f.close()
        csv = ('file://%s/xxx.csv' % os.getcwd()).replace('/','%01')
        c = s.url('=' + root + '/%s/UE-INF21UE9/1/3/column_attr_comment/col_0/xxIMPORT(%s%%232)yy' % (ys, csv))
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-INF21UE9/1/4/column_attr_comment/col_1/xxIMPORT(%s%%233)yy' % (ys, csv))
        assert(c == ok_png)
        time.sleep(1)
        ss.start()
        c = ss.url('=' + abj + '/%s/10123456' % ys)
        assert('xxyy' in c) # URL not visible
        assert('4.4444' in c)
        assert('XXXXYYYY' in c)

        # Change values
        f = open('xxx.csv', 'w')
        f.write('qqqq,qqq,qqqq\n10123456,val=é,val=è\r\nttt,yyy,uuu,uu\n1,2,3')
        f.close()
        c = s.url('=' + root + '/%s/UE-INF21UE9/1/5/column_attr_comment/col_0/xxIMPORT()yy' % ys)
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-INF21UE9/1/6/column_attr_comment/col_1/xxIMPORT()yy' % ys)
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-INF21UE9/1/7/column_attr_comment/col_0/xxIMPORT(%s%%232)yy' % (ys, csv))
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-INF21UE9/1/8/column_attr_comment/col_1/xxIMPORT(%s%%233)yy' % (ys, csv))
        assert(c == ok_png)
        # time.sleep(1)
        c = s.url('=' + root + '/%s/UE-INF21UE9' % ys)
        assert('4.4444' in c)
        assert('XXXXYYYY' in c)
        assert('val=é' in c)
        assert('val=è' in c)
        f = open('xxx.csv', 'w')
        f.write('qqqq,qqq,qqqq\r10123456,val2=\xe9,val2=\xe8\rttt,yyy,uuu,uu\r1,2,3')
        f.close()
        c = s.url('=' + root + '/%s/UE-INF21UE9/1/9/column_attr_comment/col_0/xxIMPORT()yy' % ys)
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-INF21UE9/1/10/column_attr_comment/col_1/xxIMPORT()yy' % ys)
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-INF21UE9/1/11/column_attr_comment/col_0/xxIMPORT(%s%%232)yy' % (ys, csv))
        assert(c == ok_png)
        c = s.url('=' + root + '/%s/UE-INF21UE9/1/12/column_attr_comment/col_1/xxIMPORT(%s%%233)yy' % (ys, csv))
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
        utilities.mkpath('DBregtest/Y%d/SAutomne' % (year-1))
        utilities.write_file('DBregtest/Y%d/SAutomne/UE-pastue.py' % (year-1),
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
        c = s.url('=' + abj +'/%s/UE-lost/2' % ys)
        assert(c.startswith('<script>window.parent.location = "'))
        
    if do('template_reload'):
        f = open('../TEMPLATES/xxx_regtest.py', 'w')
        f.write('''
from data import ro_user
def content(table):
    return "XXX_REGTEST1"
def create(table):
    table.new_page("", ro_user, "", "")
''')
        f.close()
        c = s.url('=' + abj +'/%s/xxx_regtest-1' % ys)
        assert("XXX_REGTEST1" in c)
        time.sleep(1)

        f = open('../TEMPLATES/xxx_regtest.py', 'a')
        f.write('def content(table): return "XXX_REGTEST2"\n')
        f.close()
        c = s.url('=' + abj +'/%s/xxx_regtest-3' % ys)
        assert("XXX_REGTEST2" in c)
        os.unlink('../TEMPLATES/xxx_regtest.py')
        os.unlink('../TEMPLATES/xxx_regtest.pyc')

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

        # os.mkdir('../DBregtest/Y%d' % (year-1))
        # os.mkdir('../BACKUP_DBregtest/Y%d' % (year-1))
        utilities.mkpath('../DBregtest/Y%d/S%s' % (year-1, semester))
        utilities.mkpath('../BACKUP_DBregtest/Y%d/S%s' % (year-1, semester))
        os.rename('../DBregtest/Y%d/S%s/UE-etape.py' % (year, semester),
        '../DBregtest/Y%d/S%s/UE-etape.py' % (year-1, semester))
        
        c = s.url('=' + abj +'/%s/UE-etape' % ys_old)
        assert('modifiable:0' in c)
        c = s.url('='+abj+'/%s/UE-etape/1/6/table_attr_modifiable/1' % ys_old)
        assert(c == ok_png)
        c = s.url('='+abj+'/%s/UE-etape/1/7/cell_change/0_0/L4/10800003' % ys_old)
        assert(c == ok_png)

        c = s.url('=' + abj +'/%s/UE-etape' % ys_old)
        assert('10800003' in c)
        assert('etape-10800003' not in c)

    if do('enumeration'):
        c = s.url('=' + abj +'/%s/UE-enum' % ys)
        assert('modifiable:1' in c)
        c = s.url('='+abj+'/%s/UE-enum/1/0/column_attr_type/A/Enumeration'%ys)
        assert(c == ok_png)
        c = s.url('='+abj+'/%s/UE-enum/1/1/column_attr_columns/A/X%%20Y'%ys)
        assert(c == ok_png)
        c = s.url('=' + abj +'/%s/UE-enum' % ys)
        assert(',columns:"X Y",' in c)

    if do('regtest-bug1'):
       while True:
           c = s.url('='+root+'/0/Dossiers/config_table')
           if '"unload_interval' in c:
              break

       conf = os.path.join('..', 'DBregtest','Y0','SDossiers', 'config_table.py')
       try:
          os.unlink(conf + 'c')
       except:
          pass
       ticket_ttl = 6
       utilities.write_file(conf + '.old', utilities.read_file(conf))
       utilities.append_file(conf,'''
cell_change(1,'0_2','check_down_connections_interval',2,"")
cell_change(1,'0_2','unload_interval',2,"")
cell_change(1,'0_2','ticket_time_to_live','%d',"")
''' % ticket_ttl)
       s.stop()
       import glob
       for t in glob.glob(os.path.join('..','TMP','TICKETS','*')):
           os.unlink(t)
       s.restart(more=['regtest-bug1'])

       c = s.url('='+root+'/0/Dossiers/config_table')
       assert('C(2,"super.user","","","600\\n(' in c) # History

       c = s.url('='+abj+'/%d/Dossiers/regtest-bug1' % uyear)
       assert('runlog' in c)

       # TOMUSS assumes that this page come from the future so it must
       # be from en read-only table (not the case here).
       # So it redirect browser in order to reload the table (read-only)
       c = s.url('='+abj+'/%d/Dossiers/regtest-bug1/10' % uyear)
       assert('window.parent.location' in c)
       c = s.url('='+abj+'/%d/Dossiers/regtest-bug1/0' % uyear)

       # We are not allowed to see an old page from an other navigator
       assert('window.parent.click_to_revalidate_ticket' in c)

       # This the good page content
       c = s.url('='+abj+'/%d/Dossiers/regtest-bug1/1' % uyear,
                 display_log_if_error=False, timeout=1)
       # Because page load does not end
       assert('***TIMEOUT***' in c)
       assert('window.parent.server_answered()' in c)

       # The frame connection is now broken.
       # Wait the page unloading
       while True:
          c = s.url('='+root+'/stat')
          if 'regtest-bug1' not in c:
             break
          time.sleep(1)

       # Create a column
       ok = False
       try:
          c = s.url('='+abj+'/%d/Dossiers/regtest-bug1/1/0/column_attr_title/col_0/TITLE0' % uyear, display_log_if_error=False, stop_if_error=False)
       except httplib.BadStatusLine:
          # The ticket is no more fine : the server does not reply
          ok = True
       assert( ok )

       # Make the ticket last longer because if it is short regtest may fail
       utilities.append_file(conf,
       'cell_change(1,"0_2","ticket_time_to_live","1000","")\n')
       c = s.url('=' + root + '/0/Dossiers/config_table/page_unload')
       assert(utilities._("MSG_page_unload_after") in c)
       c = s.url('=' + root + '/0/Dossiers/config_table')
       assert( ok )

       # The browser attempt to reconnect
       c = s.url('='+abj+'/%d/Dossiers/regtest-bug1/1' % uyear,
                 display_log_if_error=False, timeout=2)
       # Because page load does not end
       assert('***TIMEOUT***' in c)
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
        assert('/UE-modifcol' in c)
        assert('UE-modifcol/cell/A/0_1' in c)
        assert('UE-modifcol/cell/B/0_1' in c)
        assert('UE-modifcol/cell/C/0_1' not in c)

        c = ss.url('=10800001/%s/' % ys)
        assert('/UE-modifcol' in c)
        assert('UE-modifcol/cell/A/0_1' not in c)
        assert('UE-modifcol/cell/B/0_1' in c)
        assert('UE-modifcol/cell/C/0_1' not in c)

        # Not modifiable by student
        c = s.url('=10800001/%s/UE-modifcol' % ys + '/cell/C/0_1/NON')
        assert('red' in c)
        c = s.url('=10800001/%s/UE-modifcol' % ys + '/cell/A/0_1/NON')
        assert('red' in c)

        # For the teacher
        c = s.url('=' + abj + '/%s/UE-modifcol' % ys + '/cell/C/0_1/OUI')
        assert('red' in c)
        c = s.url('=' + abj + '/%s/UE-modifcol' % ys + '/cell/A/0_1/OUI')
        assert('green' in c)
        c = s.url('=' + abj + '/%s/UE-modifcol' % ys + '/cell/B/0_1/OUI')
        assert('green' in c)

        # The student can't modify a teacher note
        c = s.url('=10800001/%s/UE-modifcol' % ys + '/cell/B/0_1/NON')
        assert('red' in c)
        # The student can't modify another student note
        c = s.url('=10800001/%s/UE-modifcol' % ys + '/cell/B/0_0/NON')
        assert('red' in c)

        # Teacher erase the note
        c = s.url('=' + abj + '/%s/UE-modifcol' % ys + '/cell/B/0_1/')
        assert('green' in c)
        # The student can now modify its note
        c = s.url('=10800001/%s/UE-modifcol' % ys + '/cell/B/0_1/NON')
        assert('green' in c)
        # The student can change its note
        c = s.url('=10800001/%s/UE-modifcol' % ys + '/cell/B/0_1/OUI')
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
        assert( 'value=\\"QQQQ\\"' not in c)
        assert( 'value=\\"WWWW\\"' in c)
        assert( 'value=\\"RRRR\\"' in c)
        assert( 'value=\\"EEEE\\"' in c)

        c = ss.url('=10800002/%s/' % ys)
        assert( 'value=\\"RRRR\\"' in c)
        assert( 'value=\\"EEEE\\"' not in c)

        c =s.url('=10800001/%s/UE-repetition/cell/C/L3/EEEE' % ys)
        assert('green' in c)

        c =s.url('=10800002/%s/UE-repetition/cell/C/L5/EEEE' % ys)
        assert('red' in c)

        c =s.url('='+abj+'/%s/UE-repetition/1/28/cell_change/C/L4/EEEE'%ys)
        assert(c == bad_png)

        
if '1' in sys.argv:
   sys.argv.remove('1')
   only_once = True
else:
   only_once = False


n = 0
m = []
while True:
    start = time.time()
    exit_status = 1
    try:
        tests()
        exit_status = 0
        print 'Test fine'
    except AssertionError:
        if c == '':
            print 'assert: empty !!!!!'
        elif c == bad_png:
            print 'assert: bad_png'
        elif c == ok_png:
            print 'assert: ok_png'
        elif c == bug_png:
            print 'assert: bug_png'
        else:
            f = open('xxx.html', 'w')
            f.write(c)
            f.close()
            print c
        print 'End of regressions tests : failure'       
        raise
    finally:
        try:
            s.stop()
        except:
            shutil.rmtree('../DBregtest', ignore_errors=True)
            shutil.rmtree('../BACKUP_DBregtest', ignore_errors=True)
            
        m.append('Running time : %g seconds' % (time.time() - start))
        if ss and ss.started:
            ss.stop()
        for i in m:
            print i
        if only_once:
            break

sys.exit(exit_status)
        




    
        
