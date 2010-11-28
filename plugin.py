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

import configuration
import utilities
import files
import socket
import re

warn = utilities.warn

class Useles(object):
    closed = False
    def close(self):
        self.closed = True
    def flush(self):
        pass
    def write(self, txt):
        raise ValueError('write on Useles')

Useles = Useles()

class Link(object):
    def __init__(self,
                 text=None,
                 help='',
                 url=None,
                 target="_blank",
                 html_class='leaves',
                 priority=0,
                 where = None,
                 authorized = lambda server: True,
                 ):
        self.text = text
        self.url = url
        self.target = target
        self.help = re.sub('[ \t\n]+',' ',help)
        self.html_class = html_class
        self.priority = priority
        self.where = where
        self.authorized = authorized
        self.plugin = None

    def html(self, server, plugin, with_help=False):
        if self.target:
            target = ' target="' + self.target + '"'
        else:
            target = ''

        url = self.url
        if url is None:
            assert(len(plugin.url) == 1)
            url = '/' + plugin.url[0]
        if url.startswith('javascript:'):
            target = ''
        elif url.startswith('/'):
            url = '%s/=%s%s' % (configuration.server_url, server.ticket.ticket, url)

        text = self.text
        if text is None:
            text = plugin.name

        if self.html_class:
            html_class = ' class="' + self.html_class + '"'
        else:
            html_class = ''

        if with_help:
            help = '<div class="help">' + self.help + '</div>'
            icon = '<img class="safety" src="' + configuration.server_url + '/' + self.html_class + '.png">'
        else:
            help = ''
            icon = ''

        if url == '':
            tag = 'span'
        else:
            tag = 'a'

        return '%s<%s%s%s href="%s">%s%s</%s>' % (icon, tag, html_class, target,
                                            url, text, help, tag)
        


plugins = []

class Plugin(object):
    def __init__(self, name, url, function=lambda x: 0, teacher=None,
                 abj_master=None, referent_master=None, root=None,
                 authenticated=True,
                 administrative=None,
                 password_ok = True,
                 response = 200,
                 mimetype = "text/html; charset=UTF-8",
                 headers = lambda server: (),
                 launch_thread = False,
                 keep_open = False,
                 cached = False,
                 link = None,
                 documentation = '',
                 referent=None,
                 ):
        if url[0] != '/':
            raise ValueError('not an absolute URL')
        self.name            = name
        self.url             = url[1:].split('/')
        if self.url == ['']:
            self.url = []
        self.function        = function
        self.authenticated   = authenticated
        self.teacher         = teacher
        self.administrative  = administrative
        self.referent        = referent
        self.referent_master = referent_master
        self.abj_master      = abj_master
        self.root            = root
        self.response        = response
        self.mimetype        = mimetype
        self.headers         = headers
        self.launch_thread   = launch_thread
        self.keep_open       = keep_open
        self.password_ok     = password_ok
        self.cached          = cached
        self.invited         = ()
        self.link            = link
        if link:
            link.plugin = self
        if documentation:
            self.documentation = documentation
        else:
            self.documentation = function.__doc__

        plugins.append(self)
        plugins.sort(lambda x, y: cmp(x.url, y.url))

    def __str__(self):
        s = '%14s %-21s ' % (self.name, '/'.join(self.url))
        s += {None: '', True:'Auth', False:'!Auth'}\
             [self.authenticated].rjust(6)
        s += {None: '', True:'Teacher', False:'!Teacher'}\
             [self.teacher].rjust(9)
        s += {None: '', True:'Adm', False:'!Adm'}\
             [self.administrative].rjust(5)
        s += {None: '', True:'Ref', False:'!Ref'}\
             [self.referent].rjust(5)
        s += {None: '', True:' ABJM', False:'!ABJM'}\
             [self.abj_master].rjust(6)
        s += {None: '', True:'RefM', False:'!RefM'}\
             [self.referent_master].rjust(6)
        s += {None: '', True:'root', False:'!root'}\
             [self.root].rjust(6)
        s += {None: '', True:'PassOK', False:'!PassOK'}\
             [self.password_ok].rjust(8)
        s += {None: '', True:'LThrd', False:'!LThrd'}\
             [self.launch_thread].rjust(7)
        return s

    def html(self):
        s = '<tr><td><a href="Welcome.xml#plugin_%s">%s</a></td><td>%s</td>'% (
            self.name, self.name, '/'.join(self.url))
        s += '<td>' + str(self.authenticated)[0] + '</td>'
        s += '<td>' + str(self.teacher)[0] + '</td>'
        s += '<td>' + str(self.referent)[0] + '</td>'
        s += '<td>' + str(self.administrative)[0] + '</td>'
        s += '<td>' + str(self.abj_master)[0] + '</td>'
        s += '<td>' + str(self.referent_master)[0] + '</td>'
        s += '<td>' + str(self.root)[0] + '</td>'
        s += '<td>' + str(self.password_ok)[0] + '</td>'
        s += '<td>' + str(self.launch_thread)[0] + '</td>'
        s += '<td>' + str(self.cached)[0] + '</td>'
        s += '<td>' + str(self.keep_open)[0] + '</td>'
        if self.response == 200:
            s +=  '<td>' + str(self.mimetype) + '</td>'
        else:
            s +=  '<td>' + str(self.response) + '</td>'
        s += '</tr>'
        return s

    def doc(self):
        import os
        s = '<tr><td><b><a name="plugin_%s">%s</a></b><br/>' % (
            self.name, self.name)
        if self.function.__doc__:
            filename_full = self.function.func_code.co_filename
            filename = filename_full.split(os.path.sep)[-1]
            s += ('<a href="' +
                  '..' + filename_full.replace(os.getcwd(), '') + '">' +
                  filename + ':' +
                  str(self.function.func_code.co_firstlineno) + '</a>')

        s += '</td><td>'
        if self.link:
            import cgi
            s += '<b>%s</b> in %s<br/><em>%s</em>' % (
                cgi.escape(self.link.text),
                self.link.where,
                cgi.escape(self.link.help),
                )
        s += '</td><td>'
        if self.documentation:
            s += self.documentation
        s += '</td></tr>'
        
        return s

    def is_allowed(self, server):
        if not self.authenticated:
            return True
        if server.ticket == None:
            return False
        if server.ticket.user_name in self.invited:
            return True
        if self.teacher is True and not server.ticket.is_a_teacher:
            return False
        if self.teacher is False and server.ticket.is_a_teacher:
            return False
        if self.referent is True and not server.ticket.is_a_referent:
            return False
        if self.administrative is True \
           and not server.ticket.is_an_administrative:
            return False
        if self.administrative is False and server.ticket.is_an_administrative:
            return False
        if self.root is True and server.ticket.user_name not in configuration.root:
            return False
        if self.abj_master and not server.ticket.is_an_abj_master:
            return False
        if self.referent_master and not server.ticket.is_a_referent_master:
            return False
        if self.password_ok is True and not server.ticket.password_ok:
            return False
        if self.password_ok is False and server.ticket.password_ok:
            return False
        return True

    def path_match(self, server):
        path = server.the_path
        url = self.url
        path = list(path)
        server.options = []
        try:
            for i, f in enumerate(url):
                if f == '{Y}':
                    server.the_year = int(path[i])
                    continue
                if f == '{ }':
                    server.the_time = int(path[i])
                    continue
                if f == '{S}':
                    server.the_semester = utilities.safe(path[i]).replace('.','_')
                    continue
                if f == '{U}':
                    server.the_ue = utilities.safe(path[i]).replace('.','_')
                    continue
                if f == '{P}':
                    server.the_page = int(path[i])
                    continue
                if f == '{?}':
                    server.something = path[i]
                    continue
                if f == '{I}':
                    if not path[i][-1].isdigit():
                        return False
                    server.the_student = utilities.the_login(path[i])
                    continue
                if f == '{_I}':
                    if not path[i].startswith('_'):
                        return False
                    server.the_student = utilities.the_login(path[i][1:])
                    continue
                if f == '{*}':
                    return True, path[i:]
                if f == '{=}':
                    while len(path) != i and path[i].startswith('='):
                        server.options.append(path[i])
                        del path[i]
                    if len(path) == i or (len(path) == i+1 and path[i] == ''):
                        return True, ()
                    else:
                        return False
                if f != path[i]:
                    return False

        except (ValueError, IndexError):
            return False

        if len(path) == len(url):
            return True, ()
        else:
            return False

def vertical_text(text, size=12):
    height = str(int(size)*9)
    size = str(size)
    return '<svg xmlns="http://www.w3.org/2000/svg"><text transform="matrix(0,-1,1,0,' + size + ',' + str(height) + ')">' + text + '</text></svg>\n'

def html(filename):
    f = open(filename, 'w')
    f.write("<table class=\"plugin\" border=\"1\"><thead><tr>"
            "<th>Name</th>"
            "<th>URL template</th>"
            "<th>" + vertical_text('Authenticated') + "</th>"
            "<th>" + vertical_text('Teacher') + "</th>"
            "<th>" + vertical_text('Referent') + "</th>"
            "<th>" + vertical_text('Administrator') + "</th>"
            "<th>" + vertical_text('Abj master') + "</th>"
            "<th>" + vertical_text('Referent master') + "</th>"
            "<th>" + vertical_text('root') + "</th>"
            "<th>" + vertical_text('Password OK') + "</th>"
            "<th>" + vertical_text('Backgrounded') + "</th>"
            "<th>" + vertical_text('Cached') + "</th>"
            "<th>" + vertical_text('Keep open') + "</th>"
            "<th>Mime Type</th></tr></thead><tbody>\n""")
    for p in plugins:
        f.write(p.html().replace('>N<','>&nbsp;<')+"\n")
    f.write("</tbody></table>\n")  
    f.close()

def doc(filename):
    uniq = {}
    for p in plugins:
        uniq[p.name] = p
    uniq = uniq.values()
    uniq.sort(key=lambda x: x.name)
    
    f = open(filename, 'w')
    f.write('<table border="1" class="plugin_doc">')
    f.write('<thead><tr><th>Name and location</th><th>Link and position</th><th>Explanations</th></tr></thead>')
    for p in uniq:
        f.write(p.doc())
    f.write('</table>')
    f.close()
    

links_without_plugins = [
    Link(text='Consultation des TT',
         url="javascript:go_year('Dossiers/tt/=read-only=')",
         where="abj_master",
         html_class="verysafe",
         authorized = lambda s: s.ticket.is_an_abj_master,
         priority = -100,
         ),
    Link(text='Modification des TT',
         url="javascript:go_year('Dossiers/tt')",
         where="abj_master",
         html_class="unsafe",
         authorized = lambda s: s.ticket.is_an_abj_master,
         priority = -99,
         ),
    Link(text='Statistiques TOMUSS',
         url="stats.html",
         where="informations",
         html_class="verysafe",
         help="""Affiche les statistiques sur l'utilisation de TOMUSS""",
         ),
    Link(text='Table des référents pédagogiques',
         url="javascript:go('referents')",
         help="""Il faut indiquer dans cette table TOMUSS
         la liste des enseignants référents pédagogiques.
         Il est possible de modifier manuellement des affectations
         d'étudiants.""",
         html_class='safe',
         where='abj_master',
         priority=999,
         authorized = lambda s: s.ticket.is_a_referent_master,
         ),                               
    Link(text='Afficher la configuration de TOMUSS',
         where="root_rw",
         html_class="verysafe",
         url="/0/Dossiers/config_table/=read-only=",
         help="""Utiliser ce lien si vous voulez seulement regarder
         la configuration de TOMUSS.""",
         authorized = lambda s: s.ticket.user_name in configuration.root,
         priority = -1000,
         ),
    Link(text='Éditer la configuration de TOMUSS',
         where="root_rw",
         html_class="unsafe",
         url="/0/Dossiers/config_table",
         help="""La moindre erreur d'édition dans cette table peut
         bloquer TOMUSS. Si vous ne voulez pas modifier la configuration,
         demandez à afficher la configuration.""",
         authorized = lambda s: s.ticket.user_name in configuration.root,
         priority = -999,
         ),
    Link(text='Éditer la configuration des plugins de TOMUSS',
         where="root_rw",
         html_class="safe",
         url="/0/Dossiers/config_plugin",
         help="""Permet de voir la liste des plugins et d'ajouter
         des utilisateurs autorisés""",
         authorized = lambda s: s.ticket.user_name in configuration.root,
         priority = -998,
         ),
    Link(text="Tests de régression en JavaScript",
         where="debug",
         html_class="verysafe",
         url="/2009/Dossiers/javascript_regtest_ue",
         help="""Lance des tests de régression sur votre navigateur.""",
         authorized = lambda s: s.ticket.user_name in configuration.root,
         ),
    Link(text="Table de moyennes",
         where="debug",
         html_class="verysafe",
         url="/2008/Test/average",
         help="""Table pour vérifier les moyennes""",
         authorized = lambda s: s.ticket.user_name in configuration.root,
         ),
    Link(text="Démo animaux",
         where="debug",
         html_class="verysafe",
         url="javascript:go('demo_animaux')",
         help="""UE utilisée dans la démonstration de TOMUSS""",
         authorized = lambda s: s.ticket.user_name in configuration.root,
         ),
    Link(text="Tous les types de colonne",
         where="debug",
         html_class="verysafe",
         url="/2008/Test/test_types",
         help="""Une table pour tester les types.""",
         authorized = lambda s: s.ticket.user_name in configuration.root,
         ),
    ]


def get_menu_for(where, server, with_help=False):
    messages = []
    if with_help:
        for link in links_without_plugins:
            if link.where == where and link.authorized(server):
                if link.plugin and not link.plugin.is_allowed(server):
                    continue # Not allowed by plugin
                messages.append((link.priority,
                                 link.html(server,None,with_help)))
    for p in plugins:
        if p.link and p.link.where == where and p.is_allowed(server):
                messages.append((p.link.priority,
                                p.link.html(server,p,with_help)))

    if messages:
        return zip(*sorted(messages))[1]
    else:
        return []


def bad_url(server):
    """As the URL is bad, the navigator is redirected to the home page"""
    warn('path: %s' % server.the_path, what="error")
    warn('from: %s' % server.headers.get("Referer"), what="error")

def bad_url_message(server):
    server.the_file.write('bad_url')

to_top = None



def execute(server, plugin):
    if plugin.launch_thread:
        try:
            plugin.function(server)
        except:
            utilities.send_backtrace('Path = ' + str(server.the_path) + '\n' +
                                     'Ticket = ' + str(server.ticket) + '\n',
                                     subject = 'Plugin ' + plugin.name,
                                     )
            try:
                if 'image' in plugin.mimetype:
                    server.the_file.write(files.files['bug.png'])
                else:
                    server.the_file.write('*'*100+u"<br>\nLe serveur a rencontré un problème, l'administrateur a été prévenu.<br>\n".encode('utf8')+'*'*100)
                server.the_file.close()
            except socket.error:
                pass
            raise
        if not plugin.keep_open:
            server.the_file.close()
        server.the_file = None
        
    else:
        plugin.function(server)

    server.log_time(plugin.name)

def search_plugin(server):
    for p in plugins:
        if p.is_allowed(server):
            t = p.path_match(server)
            if t != False:
                server.the_path = t[1]
                return p
    return False


class FakeRequestHandler(object):
    def log_time(self, *args, **keys):
        try:
            self.server.the_year = self.the_year
            self.server.the_semester = self.the_semester
        except AttributeError:
            pass
        self.server.log_time(*args,**keys)

    def backtrace_html(self):
        import cgi
        s = repr(self) + '\n'
        s += '<h2>SERVER HEADERS</h2>\n'
        for k,v in self.headers.items():
            s += '<b>' + k + '</b>:' + cgi.escape(str(v)) + '<br>\n'
        s += '<h2>SERVER DICT</h2>\n'
        for k,v in self.__dict__.items():
            if k != 'headers':
                s += '<b>' + k + '</b>:' + cgi.escape(str(v)) + '<br>\n'
        return s

def dispatch_request(server, manage_error=True):

    s = FakeRequestHandler()
    s.the_path = server.the_path
    s.headers = server.headers
    s.ticket = server.ticket
    s.the_file = server.the_file
    s.start_time = server.start_time
    s.server = server
    
    try:
        s.year = server.year
        s.semester = server.semester
        s.the_port = server.the_port
    except AttributeError:
        pass
    
    warn('dispatch %s' % server.the_path, what='debug')
    p = search_plugin(s)
    
    if p is False:
        if manage_error:
            global to_top
            if to_top is None:
                if configuration.regtest:
                    to_top = Plugin('bad-url', '/{url_not_possible}',
                                    function = bad_url_message)
                else:
                    to_top = Plugin('bad-url', '/{url_not_possible}',
                                    response=307,
                                    function = bad_url, 
                                    headers = lambda x: (
                                        ('Location', '%s/=%s' %
                                         (configuration.server_url,
                                          x.ticket.ticket)),
                                        ))
            p = to_top
        else:
            return False

    try:
        server.the_ue = s.the_ue
    except AttributeError:
        pass
        
    warn('match %s(%s), path: %s' % (p.name, p.url, server.the_path),
         what='plugin')

    if p.mimetype:
        server.wfile = server.the_file
        server.send_response(p.response)
        if not p.cached:
            server.send_header('Cache-Control', 'no-cache')
            server.send_header('Cache-Control', 'no-store')
        for h in p.headers(s):    
            warn('send header: %s' % str(h), what='plugin')
            server.send_header(*h)
        server.send_header('Content-Type', p.mimetype)
        server.end_headers()
    server.plugin = p
    s.plugin = p
    if p.keep_open or p.launch_thread:
        server.wfile = Useles
        warn('keep_open (closed=%s)' % server.the_file.closed, what='plugin')

    if p.launch_thread:
        warn('launch thread with %s' % server.the_file, what='plugin')
        utilities.start_new_thread(execute, (s, p))
    else:
        execute(s, p)
    warn('done', what='plugin')

# To really be sure to never have concurrent request processing
dispatch_request = utilities.add_a_lock(dispatch_request)
        
            
            
