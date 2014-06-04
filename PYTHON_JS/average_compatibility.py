#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This script generate a javascript fileS testing for all the usage
in the table database if the new function give the same result
than the new one.

Argument:   'get'  in order to translate the table data into javascript

Without argument, add the headers and execute.

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
document = {
   getElementById: function() { }
} ;

function check_compat(data_col)
{
initialise_columns() ;
columns_filter = function() { return false ; } ;

for(var line in lines)
 {
   compute_average_old(data_col, lines[line]) ;
   var old_value = lines[line][data_col].value ;
   compute_average(data_col, lines[line]) ;
   var new_val = lines[line][data_col].value.toString()
   if ( old_value.toString() != new_val && new_val != 'NaN' && new_val != '0' )
          {
             if ( Math.abs(old_value - lines[line][data_col].value) < 0.001 )
                  continue ;
             s = [table + '/' + columns[data_col].title
                  + ' meanof=' + columns[data_col].mean_of
                  + ' bestof=' + columns[data_col].best_of
                  + ' ' + lines[line][0].value] ;
             for(var dc in columns[data_col].average_columns)
              {
              dc = columns[data_col].average_columns[dc] ;
              s.push(lines[line][dc].value
                     + (lines[line][dc].value === '' ?
                        '[' + columns[dc].empty_is + ']' : '')
                     + '/'
                     + (columns[dc].real_weight_add ? '' : '+')
                     + columns[dc].real_weight
                    );
              }
             console.log(s.join(' ') + ' ' + old_value + '»' + lines[line][data_col].value);
          }
 }
}
""",
         str(files.files['utilities.js']),
         str(files.files['types.js']),
         str(files.files['lib.js']),
         ])

def content():
    for t in tablestat.all_the_tables():
        if t is None:
            continue
        print t
        need = False
        for column in t.columns.columns_ordered():
            if column.type.name == 'Moy' and column.columns != '':
                sys.stderr.write('\t%s\n' % column.title)

                for column_name in re.split(" +", column.columns):
                    col =  t.columns.from_title(column_name)
                    if col is None:
                        print (' %s Unknown column title: %s.\n'
                               % (t, column_name))
                        break
                else:
                    f = open('xxx_%d_data.js' % t.year, "a")
                    if not need:
                        print '\tCopy table'
                        need = True
                        f.write('\n\ntable=' + utilities.js(str(t)) + ";\n"
                                + t.columns.js(False) + '\n'
                                + 'lines = [] ;\n'
                                + '\n'.join(t.lines.js()) + '\n'
                                )
                    f.write('check_compat(%s);\n' % column.data_col)
                    f.close()
        t.unload()

if 'get' in sys.argv:
    content()

for filename in glob.glob('xxx_*_data.js'):
    print '\n'*3
    print filename
    print '\n'*3
    utilities.write_file('xxx.js',
                         headers + utilities.read_file(filename)
                         )
    os.system('node xxx.js')
