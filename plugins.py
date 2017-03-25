#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2008-2012 Thierry EXCOFFIER, Universite Claude Bernard
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

import tomuss_init
import html
import os
import io
from . import plugin
from . import utilities
from . import files
from . import configuration
import collections

suivi_plugins = []

#REDEFINE
# This function do the import of LOCAL Plugins for the TOMUSS server
def plugins_tomuss_more():
    pass

def plugins_tomuss():
    # TOMUSS plugins:
    from .PLUGINS import abj_change
    from .PLUGINS import badpassword
    from .PLUGINS import cell_change
    from .PLUGINS import clean
    from .PLUGINS import gc_state
    from .PLUGINS import home3
    from .PLUGINS import logout
    from .PLUGINS import newpage
    from .PLUGINS import pageaction
    from .PLUGINS import referent_update
    from .PLUGINS import statpage
    from .PLUGINS import student
    from .PLUGINS import live_log
    from .PLUGINS import live_status
    from .PLUGINS import profiling
    from .PLUGINS import tickets
    from .PLUGINS import clients
    from .PLUGINS import send_alert
    from .PLUGINS import master_of
    from .PLUGINS import log
    from .PLUGINS import evaluate
    from .PLUGINS import login_list
    from .PLUGINS import favorite_student
    from .PLUGINS import referent_get
    from .PLUGINS import bilan
    from .PLUGINS import suivi_referent
    from .PLUGINS import send_mail
    from .PLUGINS import reload_plugins
    from .PLUGINS import picture
    from .PLUGINS import change_identity
    from .PLUGINS import auto_update
    from .PLUGINS import backtrace
    from .PLUGINS import save_preferences
    from .PLUGINS import rsskey
    from .PLUGINS import signature
    from .PLUGINS import restart
    from .PLUGINS import opensearch
    from .PLUGINS import fix_modifiables
    from .PLUGINS import get_columns
    from .PLUGINS import create_table
    from . import signature
    if getattr(configuration, 'blur', False):
        from .PLUGINS import blur
    plugins_tomuss_more()

    tomuss_plugins = list(plugin.plugins)
    # Get plugins links from suivi in order to create home page
    plugins_suivi()
    for p in plugin.plugins:
        if p not in tomuss_plugins:
            suivi_plugins.append(p)
            if p.link:
                # print 'Links added from suivi:', p.link
                plugin.add_links(p.link)

    # Restore normal plugins
    plugin.plugins = tomuss_plugins
    init_plugins()

#REDEFINE
# This function do the import of LOCAL Plugins for the 'suivi' server
def plugins_suivi_more():
    pass

def plugins_suivi():
    from .PLUGINS import logout
    from .PLUGINS import suivi_teachers #
    from .PLUGINS import suivi_tables #
    from .PLUGINS import suivi_student #
    from .PLUGINS import unload
    from .PLUGINS import suivi_referents
    from .PLUGINS import suivi_uninterested #
    from .PLUGINS import suivi_referent_list
    from .PLUGINS import suivi_icone
    from .PLUGINS import suivi_bad_students #
    from .PLUGINS import suivi_preferences #
    from .PLUGINS import suivi_ip #
    from .PLUGINS import suivi_badname #
    from .PLUGINS import suivi_groupe #
    from .PLUGINS import live_log
    from .PLUGINS import gc_state
    from .PLUGINS import resume
    from .PLUGINS import suivi_extract
    from .PLUGINS import log
    from .PLUGINS import evaluate
    from .PLUGINS import picture
    from .PLUGINS import change_identity
    from .PLUGINS import reload_plugins
    from .PLUGINS import count
    from .PLUGINS import signature
    from .PLUGINS import public
    from . import signature
    if getattr(configuration, 'blur', False):
        from .PLUGINS import blur
    plugins_suivi_more()
    init_plugins()

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
        return t.__func__.__module__.split('.')[2]
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
    # if attr == 'full_title':
    #    html_class += ' title'
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
            value += '<br/><small>(' + superclass(m).title + ')</small>'
        except AttributeError:
            pass
    f.write('<td class="%s"><div>%s</div></td>' % (
        value_class(k) + html_class,
        value.replace('_',' ')
        ))

def column_type_list():
    from . import COLUMN_TYPES
    for filename in os.listdir(COLUMN_TYPES.__path__[0]):
        yield 'COLUMN_TYPES', filename
    if configuration.regtest and not configuration.regtest_load_local:
        return

    try:
        from .LOCAL import LOCAL_COLUMN_TYPES
        for filename in os.listdir(LOCAL_COLUMN_TYPES.__path__[0]):
            yield 'LOCAL', 'LOCAL_COLUMN_TYPES', filename
    except ImportError:
        pass

def init_plugins():
    # Compute CSS for plugins
    all_css = set()
    for p in plugin.plugins:
        all_css.add(p.css)
    files.files['style.css'].append('plugins.py', '\n'.join(all_css))

def load_types():
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
                if isinstance(getattr(m, k), collections.Callable):
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

    for m in sorted(types.keys(), key=lambda x: (types[x].human_priority,x)):
      all_js += '_%s() ;\n' % m

    # Here because Column type loading may change ATTRIBUTE definitions
    from . import column
    column.initialize()

    init_plugins()

    files.files['types.js'].append('plugins.py', all_js)

    # Update the types of columns
    from . import document
    for table in document.tables.values():
        for column in table.columns:
            column.type = types[column.type.name]

    return reloadeds


languages = set()

def generate_data_files(suivi=False):
    #####################################
    # Generate MO files
    #####################################

    import gettext
    js = utilities.js

    def generate_js(directory, dictionary):
        try:
             dictionary.update(
                 gettext.translation('tomuss', directory,
                                     [language])._catalog.items()
             )
        except IOError:
            return

    import itertools
    local_translation = os.path.join('LOCAL', 'LOCAL_TRANSLATIONS')
    if not os.path.exists(local_translation):
        os.mkdir(local_translation)
    for language in set(itertools.chain(os.listdir('TRANSLATIONS'),
                                        os.listdir(local_translation))):
        language = language.lower()
        languages.add(language)
        filename = os.path.join('TMP', language + '.js')

        if not suivi:
            d = {}
            generate_js('TRANSLATIONS', d)
            generate_js(local_translation, d)
            f = open(filename, 'w', encoding = "utf-8")
            f.write('translations["' + language + '"] = {')
            for k, v in d.items():
                if k:
                    f.write('%s:%s,\n' % (js(k),js(v)))
            f.write('"_":""} ;\n')
            f.close()
        files.files[language + '.js'] = utilities.StaticFile(filename)

    #####################################
    # Generate POT file from data.
    #####################################

    f = open('xxx_tomuss.pot', 'w', encoding = "utf-8")
    g = open(os.path.join('LOCAL', 'xxx_tomuss.pot'), 'w', encoding = "utf-8")

    def w(o, comment, msgid, msgstr):
        if isinstance(o, io.IOBase):
            ww = o
        else:
            if 'LOCAL' in o.__module__:
                ww = g
            else:
                ww = f
        ww.write('#. %s\nmsgid "%s"\nmsgstr "%s"\n\n' % (comment,  msgid,
                  msgstr.replace('"', '\\n').replace('\n','\\n"\n "')))

    head = '''# Texts extracted from a un running TOMUSS instance
# Copyright (C) 2011 Thierry Excoffier, LIRIS, Universite Claude Bernard Lyon 1
# This file is distributed under the same license as TOMUSS
# Thierry.Excoffier@univ-lyon1.fr, 2011

'''
    f.write(head)
    g.write(head)
    w(f, '', '', "Content-Type: text/plain; charset=utf-8")
    w(g, '', '', "Content-Type: text/plain; charset=utf-8")

    for column_type in types:
        w(types[column_type], 'Columns types, button text in the menu',
            'B_' + column_type, column_type)

    from . import column
    for attr_name, value in (list(column.ColumnAttr.attrs.items())
                             + list(column.TableAttr.attrs.items())):
        if isinstance(value, column.TableAttr):
            t = 'TIP_table_attr_'
        else:
            t = 'TIP_column_attr_'
        w(value, 'Attribute Tip', t + attr_name, '???')
    f.close()
    g.close()

    #####################################
    # Documentation automatic generation
    #####################################

    if not os.path.exists('DOCUMENTATION'):
        return

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

    f = open('DOCUMENTATION/xxx_type.html', 'w', encoding = "utf-8")
    f.write(head)
    first_line = True
    for m in types_ordered():
        if first_line:
            f.write('<thead><tr><th>' + '</th><th>'.join(m.keys)
                    .replace('_',' ')
                    .replace('onmousedown','onmouse down')
                    .replace('ondoubleclick','ondouble click')
                    + '</th></tr></thead><tbody>\n')
            first_line = False
        f.write('<tr>')
        for k, t in zip(m.keys, m._values()):
            make_td(f, ' fixed_height', k, m)
            
        f.write('</tr>\n')
    f.write('</tbody></table>\n')
    f.close()

    f = open('DOCUMENTATION/xxx_type2.html', 'w', encoding = "utf-8")
    f.write(head)
    f.write('<thead>')
    f.write('<tr><td>')
    for m in types_ordered():
        f.write('<th>%s</th>' % m.__class__.__name__)
    f.write('</thead>')
    for k in types['Text'].keys:
        f.write('<tr><th>%s</th>' % k)
        for m in types_ordered():
            make_td(f, '', k, m)
        f.write('</tr>\n')
    f.write('</tbody></table>\n')
    f.close()

    f = open('DOCUMENTATION/xxx_column_attr.html', 'w', encoding = "utf-8")
    from . import column
    f.write('''<table border="1">
<tbody>
''')
    exceptions = ('name', 'formatter', 'empty')
    a =  ('name', 'display_table','update_horizontal_scrollbar',
              'update_headers', 'update_table_headers', 'need_authorization',
              'formatter', 'empty', 'default_value',
              'computed')
    f.write('<tr><th>'
            + '</th><th>'.join([plugin.vertical_text(t, exceptions=exceptions)
                                +'&nbsp;&nbsp;'
                                for t in a])
            + '</th></tr>')
    for attr in column.column_attributes():
        f.write('<tr>')
        for i in a:
            f.write('<td>' + html.escape(str(getattr(attr, i))) + '</td>')
        f.write('</tr>\n')
            
    f.write('</tbody></table>\n')
    f.close()

    f = open('DOCUMENTATION/xxx_table_attr.html', 'w', encoding = "utf-8")
    f.write('''<table border="1">
<tbody>
''')
    a += ('only_masters',)
    f.write('<tr><th>'
            + '</th><th>'.join([plugin.vertical_text(t, exceptions=exceptions)
                                +'&nbsp;&nbsp;'
                                for t in a]) + '</th></tr>')
    for attr in column.table_attributes():
        f.write('<tr>')
        for i in a:
            f.write('<td>' + html.escape(str(getattr(attr, i))) + '</td>')
        f.write('</tr>\n')
            
    f.write('</tbody></table>\n')
    f.close()

if __name__ == "__main__":
    load_types()

    generate_data_files()
    configuration.language = 'en'
    configuration.url_files = ''
    plugins_tomuss()
    plugin.create_html('DOCUMENTATION/xxx_tomuss_plugins.html')

    tt = plugin.plugins
    plugin.plugins = suivi_plugins
    plugin.create_html('DOCUMENTATION/xxx_suivi_plugins.html')

    plugin.plugins += tt
    plugin.doc('DOCUMENTATION/xxx_doc_plugins.html')

    ff = open('DOCUMENTATION/xxx_visibility.txt', 'w', encoding = "utf-8")
    from . import column
    for tt in sorted(column.ColumnAttr.attrs):
        tt = column.ColumnAttr.attrs[tt]
        ff.write("%s %s\n" %(tt.name, tt.visible_for()))
    ff.close()
                


