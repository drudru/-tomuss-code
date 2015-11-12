#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
BEWARE
Before running this script, run:
   make tomuss_python_O.js tomuss_python.py


This script generate a javascript fileS testing for all the usage
in the table database if the new function give the same result
than the new one.

Argument:   'get'  in order to translate the table data into javascript

Without argument, add the headers and execute.

Edit this source to works with semester other than Automne/Printemps


# Filter hiding not important changes:
grep -v -e 'NaN' -e 'PPNOT»ABJUS' -e "0»ABINJ" -e "»-"
"""

import sys
import re
import os
import glob
import tomuss_init
from .. import files
from .. import tablestat
from .. import utilities
from .. import cell

cell.Cell.js = cell.CellValue.js = lambda s: 'C(%s)' % utilities.js(s.value)

headers = '\n'.join(
        [utilities.read_file("PYTHON_JS/deprecated.js"),
         r"""
window = {location: {pathname:""}}
navigator = "" ;
alert = console.log.bind(console) ;
document = {
   getElementById: function() { }
} ;

function check_compat(data_col, col_id)
{
initialise_columns() ;
columns_filter = function() { return false ; } ;

for(var line in lines)
 {
   compute_average_old(data_col, lines[line]) ;
   var old_value = lines[line][data_col].value ;
   var v = compute_average(data_col, lines[line]) ;
   lines[line][data_col].set_value(v) ;
   var new_val = lines[line][data_col].value.toString()
   if ( old_value.toString() != new_val && new_val != 'NaN' && new_val != '0' )
          {
             if ( Math.abs(old_value - lines[line][data_col].value) < 0.001 )
                  continue ;
             s = ('x(' + js(table)
                  + ',col_id=' + js(col_id)
                  + ',line_id=' + js(line)
                  + ',old=' + js(old_value)
                  + ',new=' + js(lines[line][data_col].value)
                  + ',title=' + js(columns[data_col].title)
                  + ',meanof=' + columns[data_col].mean_of
                  + ',bestof=' + columns[data_col].best_of
                  + ',lineid=' + js(line)
                  + ',student=' + js(lines[line][0].value)
                  + ',cells="'
                 ) ;
             for(var dc in columns[data_col].average_columns)
              {
              dc = columns[data_col].average_columns[dc] ;
              s += (lines[line][dc].value
                     + (lines[line][dc].value === '' ?
                        '[' + columns[dc].empty_is + ']' : '')
                     + '/'
                     + (columns[dc].real_weight_add ? '' : '+')
                     + columns[dc].real_weight
                     + ' '
                    );
              }
             console.log(s + '")');
          }
 }
}
""",
         str(files.files['utilities.js']),
         str(files.files['types.js']),
         str(files.files['lib.js']),
         ])

def content():
    index = 0
    f = None
    size = 0
    for t in tablestat.all_the_tables():
        if t is None:
            continue
        if t.semester not in ('Automne', 'Printemps'):
            t.unload()
            continue
        sys.stderr.write(str(t) + ' ')
        sys.stderr.flush()
        need = False
        for column in t.columns.columns_ordered():
            if column.type.name == 'Moy' and column.columns != '':
                for column_name in re.split(" +", column.columns):
                    col =  t.columns.from_title(column_name)
                    if col is None:
                        sys.stderr.write(' %s Unknown column title: %s.\n'
                               % (t, column_name))
                        break
                else:
                    if not need:
                        if f is None or size > 1000000:
                            if f:
                                f.close()
                            f = open('xxx_%04d_data.js' % index, "w", encoding = "utf-8")
                            index += 1
                            size = 0
                        need = True
                        s = ('\n\ntable=' + utilities.js(str(t)) + ";\n"
                             + t.columns.js(False) + '\n'
                             + 'lines = [] ;\n'
                             + '\n'.join(t.lines.js()) + '\n'
                         )
                        f.write(s)
                        size += len(s)
                    f.write('check_compat(%s,%s);\n' % (
                        column.data_col, utilities.js(column.the_id)))
        t.unload()

if 'get' in sys.argv:
    content()
    sys.argv.remove('get')

if len(sys.argv) != 1:
    files = sys.argv[1:]
else:
    files = glob.glob('xxx_[0-9][0-9][0-9][0-9]_data.js')

for filename in files:
    print("#", filename)
    sys.stdout.flush()
    utilities.write_file('xxx.' + filename,
                         headers + utilities.read_file(filename)
                         )
    os.system('node xxx.' + filename)
