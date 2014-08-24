#!/usr/bin/python

import sys
import re
import os
import cgi

import tomuss_init

###############################################################################
# Create 'xxx_redefined.html'
###############################################################################

def code(txt):
    return cgi.escape(txt).replace(' ','&nbsp;') + '<br/>'

def parse(filename):
    t = []
    f = open(filename, 'r')
    state = 'outside'
    for line in f:
        striped = line.strip()
        if '/*REDEFINE' == striped:
            state = 'inside'
            comment = ''
        elif '#REDEFINE' == striped:
            state = 'inside-python'
            comment = ''
        elif state == 'inside':
            if '*/' == striped:
                state = 'get-function'
            else:
                comment += striped + ' '
        elif state == 'inside-python':
            if striped[0] == '#':
                comment += striped.strip('#') + ' '
            else:
                body = code(striped)
                if striped.startswith('class'):
                    state = 'finish'
                else:
                    state = 'get-body-python'
        elif state == 'get-function':
            body = code(striped)
            state = 'get-body'
        elif state == 'get-body':
            body += code(line)
            if striped.strip() == '}':
                state = 'finish'
        elif state == 'get-body-python':
            if striped.strip() == '':
                state = 'finish'
            else:
                body += code(line)

        if state == 'finish':
            t.append([comment, body, filename])
            state = 'outside'
            
    f.close()
    return t


f = open('xxx_redefined.html','w')
redefined = []
for place in ('.', 'FILES', 'PLUGINS', 'TEMPLATES', 'COLUMN_TYPES', 'ATTRIBUTES'):
    for n in os.listdir(place):
        if n.endswith('.js') or n.endswith('.py'):
            redefined += parse(os.path.join(place,n))

f.write('<table border="1">\n')
for i in redefined:
    f.write('<tr><td>' + i[2] + '</td><td><tt><small>' + i[1] + '</small></tt></td><td>' + i[0] + '</td></tr>\n')
f.write('</table>\n')
f.close()
    

###############################################################################
# Create 'xxx_data.html'
###############################################################################
from .. import data
g = open('xxx_data.html', 'w')
for key, value in data.__dict__.items():
    if hasattr(value, 'func_name') and 'DEPRECATED' not in value.func_doc:
        g.write('<p><b>' + key + '</b>(' + ', '.join(value.func_code.co_varnames) +
                '): ' + str(value.func_doc) + '</p>')
g.close()

###############################################################################
# Create 'xxx_objects.html'
###############################################################################

from .. import cell
from .. import column
from .. import teacher
g = open('xxx_objects.html', 'w')
objects = list(cell.__dict__.items()) + list(column.__dict__.items()) + \
          list(teacher.__dict__.items())
objects.sort(key=lambda x: x[0])
for key, value in objects:
    if not isinstance(value, type):
        continue
    if value.__doc__ is None:
        continue
    g.write('<h3><a name="' + key + '">' + key + '</a></h3>\n' +
            '<p>' + str(value.__doc__) + '</p>\n')
    x = []
    for k, v in value.__dict__.items():
        if not hasattr(v, '__call__'):
            continue
        s = '<li>\'<b>' + k + '</b>\''
        if v.func_doc:
            s += ": " + str(v.func_doc)
        s += '</li>'
        x.append(s)
    if x:
        x.sort()
        g.write('Methods : <ul>%s</ul>\n' % '\n'.join(x))
    
g.close()

###############################################################################
# Create 'xxx_toc.html
###############################################################################

new = []
for line in sys.stdin.readlines():
    if '_INCLUDE_' not in line:
        new.append(line)
        continue
    try:
        g = open(line.strip().split(' ')[-1], 'r')
        new += g.readlines()            
        g.close()
    except IOError:
        try:
            g = open(os.path.join("DOCUMENTATION",
                                  line.strip().split(' ')[-1]), 'r')
            new += g.readlines()            
            g.close()
        except IOError:
            pass

        
toc = ''
for line in new:
    sys.stdout.write(line)
    if '"#' in line:
        continue
    if '<h2>' in line or '<h3>' in line:
        # sys.stderr.write('(' + line + ')')
        name = line.split('name="')[1].split('"')[0]
        line = re.sub('<a name="[^"]*">', '', line)
        line = re.sub('</a>', '', line)
        line = line.replace('>', '><a href="#' + name + '">', 1)
        line = line.replace('</', '</a></')
        toc += line

g = open('xxx_toc.html', 'w')
g.write(toc)
g.close()

