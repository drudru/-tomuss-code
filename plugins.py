#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

import plugin
import utilities
import files
import cgi
import re
import os
import configuration

suivi_plugins = []

#REDEFINE
# This function do the import of local Plugins for the TOMUSS server
def plugins_tomuss_more():
    pass

def plugins_tomuss():
    import PLUGINS.abj_change
    import PLUGINS.badpassword
    import PLUGINS.cell_change
    import PLUGINS.clean
    import PLUGINS.gc_state
    import PLUGINS.home
    import PLUGINS.home2
    import PLUGINS.logout
    import PLUGINS.newpage
    import PLUGINS.pageaction
    import PLUGINS.referent_update
    import PLUGINS.statpage
    import PLUGINS.student
    import PLUGINS.live_log
    import PLUGINS.live_status
    import PLUGINS.profiling
    import PLUGINS.tickets
    import PLUGINS.clients
    import PLUGINS.send_alert
    import PLUGINS.master_of
    import PLUGINS.log
    import PLUGINS.evaluate
    import PLUGINS.login_list
    import PLUGINS.favorite_student
    import PLUGINS.referent_get
    import PLUGINS.bilan
    import PLUGINS.suivi_referent
    import PLUGINS.send_mail
    import PLUGINS.reload_plugins
    import PLUGINS.picture
    plugins_tomuss_more()

    # Get plugins links from suivi in order to create home page
    plugins = list(plugin.plugins)
    plugins_suivi()
    # Get the new plugins (from suivi)
    global suivi_plugins
    suivi_plugins = [p
                     for p in plugin.plugins
                     if p not in plugins]
    # Restore normal plugins
    plugin.plugins = plugins

    links = [p.link for p in suivi_plugins if p.link]
    print 'Links added from suivi:', [link.text for link in links]
    plugin.links_without_plugins += links

#REDEFINE
# This function do the import of local Plugins for the 'suivi' server
def plugins_suivi_more():
    pass

def plugins_suivi():
    import PLUGINS.logout
    import PLUGINS.suivi_teachers
    import PLUGINS.suivi_tables
    import PLUGINS.suivi_student
    import PLUGINS.unload
    import PLUGINS.suivi_referents
    import PLUGINS.suivi_uninterested
    import PLUGINS.suivi_referent_list
    import PLUGINS.suivi_icone
    import PLUGINS.suivi_bad_students
    import PLUGINS.suivi_preferences
    import PLUGINS.suivi_ip
    import PLUGINS.suivi_badname
    import PLUGINS.suivi_groupe
    import PLUGINS.live_log
    import PLUGINS.gc_state
    import PLUGINS.resume
    import PLUGINS.suivi_extract
    import PLUGINS.log
    import PLUGINS.evaluate
    import PLUGINS.picture
    plugins_suivi_more()

types = {}

def superclass(instance):
    return instance.__class__.__bases__[0]

def childs(type_name):
    "Returns the name of the children of the type."
    for t in types.values():
        try:
            if superclass(t).name == type_name:
                yield t.name
        except AttributeError:
            pass # The Text parent has no 'name' attribute

def types_ordered(root='Text'):
    t = types[root]
    yield t
    for child in t.children:
        for j in types_ordered(types[child].name):
            yield j

def the_value(t):
    try:
        return t.im_func.__module__.split('.')[1]
    except AttributeError:
        return str(t)

@utilities.add_a_cache
def value_class(attr):
    """Extract an HTML display class from the type attributes"""
    d = {}
    for t in types.values():
        d[getattr(t.__class__, attr)] = True
    html_class = ''
    if len(d) == 1:
        html_class += ' identical'
    length = max(len(the_value(x)) for x in d)
    if length > 12:
        if length > 100:
            html_class += ' verylong'
        else:
            html_class += ' long'
    if attr == 'full_title':
        html_class += ' title'
    return html_class

def make_td(f, html_class, k, m):
    t = getattr(m, k)
    if t is None or t == '':
        html_class += ' none'
    if k in m.__class__.__dict__:
        html_class += ' defined'
    value = the_value(t)
    if k == 'full_title':
        try:
            value += '<br/><small>(' + superclass(m).full_title+')</small>'
        except AttributeError:
            pass
    f.write('<td class="%s"><div>%s</div></td>' % (
        value_class(k) + html_class,
        value.replace('_',' ')
        ))

def column_type_list():
    import COLUMN_TYPES
    for filename in os.listdir(COLUMN_TYPES.__path__[0]):
        yield 'COLUMN_TYPES', filename
    if configuration.regtest:
        return

    try:
        import LOCAL.LOCAL_COLUMN_TYPES
        for filename in os.listdir(LOCAL.LOCAL_COLUMN_TYPES.__path__[0]):
            yield 'LOCAL', 'LOCAL_COLUMN_TYPES', filename
    except ImportError:
        pass

def load_types():
    import csv

    types.clear()

    # Load TYPES modules
    reloadeds = []
    for path in column_type_list():
        filename = path[-1]
        if filename.endswith('.py'):
            if filename == '__init__.py':
                continue
            fullname = os.path.sep.join(path)
            m, reloaded = utilities.import_reload(fullname)
            filename = filename[:-3]
            for title in (filename.title(), filename.upper()):
                try:
                    m = m.__dict__[title]
                    break
                except KeyError:
                    continue
            else:
                raise ValueError("BUG TYPE: " + filename)
            setattr(m, 'name', m.__name__)
            m = m()
            m.fullname = fullname
            types[m.name] = m
            reloadeds.append((m.name, reloaded))

    # Terminate loading
    for name, t in types.items():
        t.children = list(childs(name))
    for t in types.values():
        t.children.sort(key=lambda x: len(types[x].children))
    all_js = "// FOLLOWING CODE IS COMPUTED FROM 'COLUMN_TYPES' content\n"
    for m in types_ordered():
        try:
            js = utilities.read_file(m.fullname.replace('.py', '.js'))
        except IOError:
            js = ''
        for k in m.keys:
            value = getattr(m,k)
            js = js.replace('__' + k.upper() + '__',m.attribute_js_value(k))
        js = js.replace('__NAME__', m.name)
        js = js.split('\n')
        if '*/' in js:
            js = js[js.index('*/')+1:]
        all_js += '\n'.join(js)

        s = superclass(m)
        if hasattr(s, 'name'): # m is not the top class
            # Create class
            v = []
            for k in m.keys:
                if getattr(m, k) == getattr(s, k):
                    continue
                if callable(getattr(m, k)):
                    continue                    
                v.append('  t.%s = %s ;' % (k, m.attribute_js_value(k)))
            all_js += '''
function _%s()
{
  var t = _%s() ;
  t.title = '%s' ;
%s
  return t ;
}
''' % (m.name, s.name, m.name, '\n'.join(v))

    for m in sorted(types.keys(), key=lambda x: (types[x].human_priority,
                                                 types[x].full_title)):
      all_js += '_%s() ;\n' % m

    # Here because Column type loading may change ATTRIBUTE definitions
    import column
    column.initialize()
    
    files.files['types.js'].append_text = re.sub(
        '(?ms)// FOLLOWING CODE IS COMPUTED.*// END OF FOLLOWING CODE', '',
        files.files['types.js'].append_text)
    files.files['types.js'].append(all_js + '// END OF FOLLOWING CODE\n')

    if not os.path.exists('DOCUMENTATION'):
        return reloadeds

    head = """
<META HTTP-EQUIV="Content-Type" CONTENT="text/html;charset=UTF-8">
<style>
TABLE.types { background: #000 ; border-spacing: 1px; }
TABLE.types TD, TABLE.types TH { background: #FFF ; }
TABLE.types TR TD { padding: 0px; }
TABLE.types TR TD.fixed_height { height: 60px; }
TABLE.types TR TD DIV { height: 100% ; overflow: hidden; }
TABLE.types TH { font-size: 60% ; }
TABLE.types TR { vertical-align: top ; }
TABLE.types .identical { color: #888 ; }
TABLE.types .long { font-size: 60% ; }
TABLE.types .verylong { font-size: 40% ; }
TABLE.types .title, TABLE.types TH { background: #8F8 ; font-weight: lighter; font-size: 100%}
TABLE.types .none { background: #DDD ; color: #DDD ; }
TABLE.types .defined { background: #FDD ; }
</style>
<table class="types">"""

    f = open('DOCUMENTATION/xxx_type.html', 'w')
    f.write(head)
    first_line = True
    for m in types_ordered():
        if first_line:
            f.write('<thead><tr><th>' + '</th><th>'.join(m.keys).replace('_',' ').replace('onmousedown','onmouse down').replace('ondoubleclick','ondouble click') + '</th></tr></thead><tbody>\n')
            first_line = False
        f.write('<tr>')
        for k, t in zip(m.keys, m._values()):
            make_td(f, ' fixed_height', k, m)
            
        f.write('</tr>\n')
    f.write('</tbody></table>\n')
    f.close()

    f = open('DOCUMENTATION/xxx_type2.html', 'w')
    f.write(head)
    first_line = True
    for k in types['Text'].keys:
        if first_line:
            f.write('<thead>')
        f.write('<tr><th>%s</th>' % k)
        for m in types_ordered():
            make_td(f, '', k, m)
        f.write('</tr>\n')
        if first_line:
            f.write('</thead>')
            first_line = False
    f.write('</tbody></table>\n')
    f.close()

    f = open('DOCUMENTATION/xxx_column_attr.html', 'w')
    import column
    f.write('''<table border="1">
<tbody>
''')
    a =  ('name', 'display_table','update_horizontal_scrollbar',
              'update_headers', 'update_table_headers', 'need_authorization',
              'formatter', 'empty', 'default_value',
              'computed')
    f.write('<tr><th>' + '</th><th>'.join([plugin.vertical_text(t)+'&nbsp;&nbsp;' for t in a]) + '</th></tr>')
    for attr in column.column_attributes():
        f.write('<tr>')
        for i in a:
            f.write('<td>' + cgi.escape(str(getattr(attr, i))) + '</td>')
        f.write('</tr>\n')
            
    f.write('</tbody></table>\n')
    f.close()

    f = open('DOCUMENTATION/xxx_table_attr.html', 'w')
    f.write('''<table border="1">
<tbody>
''')
    a += ('only_masters',)
    f.write('<tr><th>' + '</th><th>'.join([plugin.vertical_text(t)+'&nbsp;&nbsp;' for t in a]) + '</th></tr>')
    for attr in column.table_attributes():
        f.write('<tr>')
        for i in a:
            f.write('<td>' + cgi.escape(str(getattr(attr, i))) + '</td>')
        f.write('</tr>\n')
            
    f.write('</tbody></table>\n')
    f.close()
    return reloadeds

if __name__ == "__main__":
    load_types()
    
    plugins_tomuss()
    plugin.html('DOCUMENTATION/xxx_tomuss_plugins.html')

    t = plugin.plugins
    plugin.plugins = suivi_plugins
    plugin.html('DOCUMENTATION/xxx_suivi_plugins.html')

    plugin.plugins += t
    plugin.doc('DOCUMENTATION/xxx_doc_plugins.html')

