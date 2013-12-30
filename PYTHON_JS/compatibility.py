#!/usr/bin/python

"""
This script generate a javascript file testing for all the usage
in the table database if the new function give the same result
than the new one.

"""

import collections
import sys
import re
import tomuss_init
from .. import tablestat
from .. import utilities

print utilities.read_file("deprecated.js")
print """
function check_compat(filter, cells, column_type)
{
    var f = compile_filter_generic_old(filter) ;
    var g = new Filter(filter, "none", column_type) ;
    var gc = g.compiled_js() ;
    for(var i=0; i<cells.length; i++)
       if ( f(cells[i]) != gc(cells[i]) )
          {
             console.log('BUG for filter "' + filter + '" ' + g.js()
                         + ' and cell ' + cells[i]
                         + " old=" + f(cells[i]) + ' new=' + gc(cells[i])) ;
          }
}

"""


sys.stderr.write('Loading all tables\n')
for t in tablestat.all_the_tables():
    if t is None:
        continue
    sys.stderr.write('*')
    sys.stderr.flush()
    filters = collections.defaultdict(list)
    for column in t.columns:
        if column.type.name == 'Nmbr' and column.columns != '':
            sys.stderr.write('\n%s %s Use Nmbr.' % (t, column.title))
            for column_name in re.split(" +", column.columns):
                col =  t.columns.from_title(column_name)
                if col is None:
                    sys.stderr.write(' %s Unknown column title: %s.\n'
                                     % (t, column_name))
                    continue
                data_col = col.data_col
                for line in t.lines.values():
                    filters[column.test_filter, column.type.name].append(
                        line[data_col])

        for attr in ('red', 'green', 'redtext', 'greentext'):
            v = getattr(column, attr)
            if v == '':
                continue
            if isinstance(v, (float, int)):
                continue
            if v[0].isdigit():
                continue
            sys.stderr.write('\n%s %s Use %s.' % (t, column.title, attr))
            for line in t.lines.values():
                filters[v, column.type.name].append(line[column.data_col])
            

    for k, v in filters.items():
        print '// ' + t
        print ('check_compat(' + utilities.js(k[0]) + ',['
               + ','.join(cell.js()
                          for cell in v)
               + '], %s);' % utilities.js(k[1])
               )
