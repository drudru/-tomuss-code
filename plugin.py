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

import codecs
import socket
import re
import html
import os
import sys
from . import configuration
from . import utilities
from . import files

warn = utilities.warn

class Link(object):
    def __init__(self,
                 text=None,
                 help='',
                 url=None,
                 target="_blank",
                 html_class='leaves',
                 priority=0,
                 where = None,
                 group = "",
                 key = None, # See TEMPLATES/config_home.py
                 # DEPRECATED, use 'group'
                 authorized = None
                 ):
        self.text = text
        self.url = url
        self.target = target
        self.help = re.sub('[ \t\n]+',' ',help)
        self.html_class = html_class
        self.priority = priority
        self.where = where
        self.plugin = None
        self.group = group
        self.key = key
        if authorized:
            warn("'authorized=' is DEPRECATED, use 'group=' in place for '%s'"%
                 self.text, what='Warning')
        else:
            authorized = lambda server: True
        self.authorized = authorized
        # Where the plugin is defined
        self.module = sys._getframe(1).f_code.co_filename

    def __str__(self):
        return 'Link(%s,%s)' % (self.text, self.url)

    def get_url_and_target(self, plugin):
        if self.target:
            target = ' target="' + self.target + '"'
        else:
            target = ''

        url = self.url
        if url is None:
            if len(self.plugin.url) != 1:
                url = "javascript:alert('" + self.plugin.name + ": you need to indicate «url=» in the Link() definition.')"
            else:
                url = '/' + plugin.url[0]
        if url.startswith('javascript:'):
            target = ''
        elif url.startswith('/'):
            target = ''
        return url, target

    def get_text(self):
        if self.text:
            return self.text
        if self.plugin:
            return utilities._('LINK_' + self.plugin.name)
        else:
            return utilities._('LINK_' + self.url)

    def get_help(self):
        if self.help:
            return self.help
        if self.plugin:
            return utilities._('HELP_' + self.plugin.name)
        else:
            return utilities._('HELP_' + self.url)

# Helper functions for parsing URL
        
def _year(server, path, i): server.the_year = int(path[i])
def _time(server, path, i): server.the_time = int(path[i])
def _something(server, path, i): server.something = path[i]
def _anything(dummy_server, path, i): return True, path[i:]
def _semester(server, path, i): server.the_semester = utilities.safe(
    path[i]).replace('.','_')
def _ue(server, path, i): server.the_ue = utilities.safe(
    path[i]).replace('.','_')
def _page(server, path, i):
    try:
        server.the_page = int(path[i])
    except ValueError:
        return False
def _int(server, path, i):
    server.the_student = utilities.the_login(path[i])
def __int(server, path, i):
    if not path[i].startswith('_'):
        return False
    server.the_student = utilities.the_login(path[i][1:])
def _request_number(server, path, i):
    path = path[i]
    if not path:
        return False
    if not path[0].isdigit():
        return False
    server.request_number = path
def _options(server, path, i):
    while len(path) != i and path[i].startswith('='):
        server.options.append(path[i])
        del path[i]
    if len(path) == i or (len(path) == i+1 and path[i] == ''):
        return True, ()
    else:
        return False
        
specials = {
     '{Y}': _year, '{ }': _time, '{S}': _semester, '{U}': _ue, '{P}': _page,
     '{?}': _something, '{I}': _int, '{_I}': __int, '{*}': _anything,
     '{=}': _options, '{R}': _request_number
     }


plugins = []

class Plugin(object):
    def __init__(self, name, url, function=lambda x: 0,
                 authenticated=True,
                 password_ok = True,
                 response = 200,
                 mimetype = "text/html; charset=UTF-8",
                 headers = lambda server: (),
                 launch_thread = False,
                 keep_open = False,
                 cached = False,
                 link = None,
                 documentation = '',
                 css='',
                 priority=0,
                 group="",
                 unsafe=True,
                 # server.uploaded will contain the data
                 upload_max_size = 0,
                 no_output = False, # The plugin writes an answer to browser
                 # Following parameters are deprecated, use group=groupname
                 teacher=None, referent=None, administrative=None,
                 abj_master=None, referent_master=None, root=None,
                 ):
        if url[0] != '/':
            raise ValueError('not an absolute URL')
        if '/' in name:
            raise ValueError('/ is not allowed in plugin name')
        for var in ('teacher', 'abj_master', 'referent_master', 'root',
                    'administrative', 'referent'):
            value = locals()[var]
            if value is not None:
                if var == 'teacher':
                    var2 = 'staff'
                else:
                    var2 = var + 's'
                if value is False:
                    var2 = '!' + var2
                warn("'%s=%s' is DEPRECATED, use 'group=%s'" %(var,value,var2),
                     what='Warning')
                group = var2

        self.name            = name
        self.url             = url[1:].split('/')
        if self.url == ['']:
            self.url = []
        self.function        = function
        self.authenticated   = authenticated
        if not authenticated:
            unsafe = False
        self.response        = response
        self.mimetype        = mimetype
        # XXX si dans mimetype il y a autre chose que utf-8 ???
        if mimetype and ("utf-8" in mimetype or "UTF-8" in mimetype):
            self.codec       = codecs.getwriter("utf-8")
        else :
            self.codec       = lambda x: x

        self.headers         = headers
        self.launch_thread   = launch_thread
        self.keep_open       = keep_open
        self.password_ok     = password_ok
        self.cached          = cached
        self.invited         = ()
        self.link            = link
        self.css             = css
        self.priority        = priority
        self.group           = group
        self.unsafe          = unsafe
        self.no_output       = no_output
        if upload_max_size and not launch_thread:
            raise ValueError("Uploads must be in a thread")
        if upload_max_size and 'html' not in mimetype:
            raise ValueError("Uploads must return HTML mime type")
        self.upload_max_size = upload_max_size
        # Where the plugin is defined
        self.module = sys._getframe(1).f_code.co_filename
        if link:
            link.plugin = self
        if documentation:
            self.documentation = documentation
        else:
            self.documentation = function.__doc__

        for plugin in plugins:
            if plugin.name == self.name:
                f1 = plugin.function.__code__.co_filename
                f2 = self.function.__code__.co_filename
                if f1.split(os.path.sep)[-1] == f2.split(os.path.sep)[-1]:
                    # __main__ module is loaded twice
                    continue
                raise ValueError('Two plugins named "%s" (%s & %s)' %
                                 (self.name, f1, f2))

        for p in plugins:
            if p.name == self.name:
                utilities.warn('Remove duplicate plugin name: %s' % p.name)
                plugins.remove(p)
                break
        plugins.append(self)
        plugins.sort(key=lambda x: (x.priority, x.url))

    def __str__(self):
        s = '%14s %-21s ' % (self.name, '/'.join(self.url))
        s += {None: '', True:'Auth', False:'!Auth'}\
             [self.authenticated].rjust(6)
        s += {None: '', True:'PassOK', False:'!PassOK'}\
             [self.password_ok].rjust(8)
        s += {None: '', True:'LThrd', False:'!LThrd'}\
             [self.launch_thread].rjust(7)
        s += ' ' + self.group
        return s

    def html(self):
        s = '<tr><td><a href="Welcome.xml#plugin_%s">%s</a></td><td>%s</td>'% (
            self.name, self.name, '/'.join(self.url))
        s += '<td>' + str(self.authenticated)[0] + '</td>'
        s += '<td>' + self.group + '</td>'
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
        s = '<tr><td><b><a name="plugin_%s">%s</a></b><br/>' % (
            self.name, self.name)
        if self.function.__doc__:
            filename_full = self.function.__code__.co_filename
            filename = filename_full.split(os.path.sep)[-1]
            s += ('<a href="' +
                  'src' + filename_full.replace(os.getcwd(), '') + '">' +
                  filename + ':' +
                  str(self.function.__code__.co_firstlineno) + '</a>')

        s += '</td><td>'
        if self.link:
            s += '<b>%s</b> in %s<br/><em>%s</em>' % (
                html.escape(self.link.get_text()),
                self.link.where,
                html.escape(self.link.get_help()),
                )
        s += '</td><td>'
        if self.documentation:
            s += self.documentation
        s += '</td></tr>'
        
        return s

    def is_allowed(self, server):
        if not self.authenticated:
            return True, 'Not authenticated'
        if server.ticket == None:
            return False, 'No ticket'
        if self.password_ok is True and not server.ticket.password_ok:
            return False, 'Only with good password'
        if self.password_ok is False and server.ticket.password_ok:
            return False, 'Only with bad password'
        return (configuration.is_member_of(server.ticket.user_name,
                                           self.invited),
                'invited: ' + repr(self.invited))
                    
    def path_match(self, server):
        path = server.the_path
        url = self.url
        path = list(path)
        server.options = []
        try:
            for i, f in enumerate(url):
                try:
                    v = specials[f](server, path, i)
                    if v is not None:
                        return v
                except KeyError:
                    if f != path[i]:
                        return False

        except (ValueError, IndexError):
            return False

        if len(path) == len(url):
            return True, ()
        else:
            return False

    def backtrace_html(self):
        return "Plugin: " + str(self)

    def send_response(self, server):
        server.send_response(self.response)
        if not self.cached:
            server.send_header('Cache-Control', 'no-cache')
            server.send_header('Cache-Control', 'no-store')
        else:
            server.send_header('Cache-Control',
                               'max-age=%d' % configuration.maxage)

        for h in self.headers(server):
            warn('send header: %s' % str(h), what='plugin')
            server.send_header(*h)
        server.send_header('Content-Type', self.mimetype)
        for domain in configuration.domains:
            server.send_header('Access-Control-Allow-Origin', domain)
        server.end_headers()

def vertical_text(text, size=12, exceptions=()):
    if text in exceptions:
        return text
    height = str(int(size)*9)
    size = str(size)
    return '<svg xmlns="http://www.w3.org/2000/svg"><text transform="matrix(0,-1,1,0,' + size + ',' + str(height) + ')">' + text + '</text></svg>\n'

def create_html(filename):
    f = open(filename, 'w', encoding = "utf-8")
    f.write("<table class=\"plugin\" border=\"1\"><thead><tr>"
            "<th>Name</th>"
            "<th>URL template</th>"
            "<th>" + vertical_text('Authenticated') + "</th>"
            "<th>" + vertical_text('Group allowed') + "</th>"
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
    uniq = list(uniq.values())
    uniq.sort(key=lambda x: x.name)
    
    f = open(filename, 'w', encoding = "utf-8")
    f.write('<table border="1" class="plugin_doc">')
    f.write('<thead><tr><th>Name and location</th><th>Link and position</th><th>Explanations</th></tr></thead>')
    for p in uniq:
        f.write(p.doc())
    f.write('</table>')
    f.close()
    
# To add links on the home page, use the home configuration page
#  on the home page.
links_without_plugins = []

def add_links(*links):
    """Add the link if the url is not yet in the table"""
    for link in links:
        for t in links_without_plugins:
            if t.url == link.url:
                break
        else:
            links_without_plugins.append(link)

def remove_links(*links):
    """Remove the link from the table"""
    for link in links:
        for t in links_without_plugins:
            if t.url == link.url:
                links_without_plugins.remove(t)
                break

def get_links(server):
    for link in links_without_plugins:
        if (configuration.is_member_of(server.ticket.user_name, link.group)
           and link.authorized(server)):
            if link.plugin and not link.plugin.is_allowed(server)[0]:
                    continue # Not allowed by plugin
            yield link, link.plugin
    for p in plugins:
        if (p.link
            and p.is_allowed(server)[0]
            and configuration.is_member_of(server.ticket.user_name,
                                           p.link.group)
            ):
            yield p.link, p


def bad_url(server):
    """The URL is bad"""
    server.the_file.write(server._('ERROR_bad_url')
                          + '<a href="%s/=%s">%s</a>' % (
            configuration.server_url, server.ticket.ticket,
            configuration.server_url
                          ))
    utilities.send_backtrace("PATH: %s\nREFERER: %s" % (
            server.the_path,
            server.headers.get("referer")),
                             "Bad URL", exception=False)

def bad_url_message(server):
    server.the_file.write('bad_url')

to_top = None



def execute(server, plugin):
    if server.do_profile:
        import cProfile
        import time
        pr = cProfile.Profile(time.time)
        pr.enable()
    if plugin.launch_thread:
        server.the_file._sock.settimeout(60)
        try:
            x = None
            try:
                if plugin.mimetype and plugin.upload_max_size:
                    x = "uploading_%d" % id(server)
                    utilities.important_job_add(x)
                    server.uploaded = server.get_field_storage(
                        plugin.upload_max_size)
                    try:
                        plugin.send_response(server)
                    except AttributeError:
                        if not plugin.no_output:
                            raise

                plugin.function(server)
            finally:
                if x:
                    utilities.important_job_remove(x)
        except:
            utilities.send_backtrace('Path = ' + str(server.the_path) + '\n' +
                                     'Ticket = ' + str(server.ticket) + '\n',
                                     subject = 'Plugin ' + plugin.name,
                                     )
            try:
                if plugin.mimetype:
                    if 'image' in plugin.mimetype:
                        server.the_file.write(files.files['bug.png'].bytes())
                    else:
                        server.the_file.write('*'*100 + "<br>\n"
                                              + server._("ERROR_server_bug")
                                              + "<br>\n" + '*'*100)
                server.close_connection_now()
            except:
                pass
            server.the_file = None
            return
        # keep_open forcément à faux pour 90/ des plugins
        if not plugin.keep_open:
            server.close_connection_now()
        server.the_file = None
        
    else:
        plugin.function(server)
    if server.do_profile:
        pr.disable()
        pr.dump_stats("xxx.prof")
        import pstats
        ps = pstats.Stats('xxx.prof')
        ps.strip_dirs().sort_stats('cumulative').print_stats()

    server.log_time(plugin.name)

def search_plugin(server, manage_error):
    for p in plugins:
        if manage_error is False and p.authenticated:
            # Only test plugin without authentication
            continue
        # warn('%s %s' % (p, p.is_allowed(server)))
        if p.is_allowed(server)[0]:
            t = p.path_match(server)
            if t != False:
                server.the_path = t[1]
                return p
    return False

def get(name):
    """Get plugin from name"""
    for p in plugins:
        if p.name == name:
            return p

@utilities.add_a_lock
def dispatch_request(server, manage_error=True):
    warn('dispatch %s' % server.the_path, what='debug')
    unsafe = server.unsafe()
    p = search_plugin(server, manage_error)
    if p is False:
        if manage_error:
            global to_top
            if to_top is None:
                # Here because the regtest value is now fine
                if configuration.regtest:
                    to_top = Plugin('bad-url', '/{url_not_possible}',
                                    function = bad_url_message,
                                    priority=1)
                else:
                    to_top = Plugin('bad-url', '/{url_not_possible}',
                                    function = bad_url, 
                                    priority=1)
                to_top.invited = ('grp:',)
            p = to_top
        else:
            return False

    if p.unsafe and unsafe:
        server.send_response(p.response)
        server.send_header('Content-Type', 'text/html; charset=UTF-8')
        server.end_headers()
        from . import authentication
        url = (authentication.authentication_redirect
               + server.path.replace("unsafe=1", "unsafe=0"))

        to_send = server._('MSG_beware_XSS') + '<br><a href="' + url + '">' + url.split("?")[0] + '</a>'
        server.the_file.write(to_send.encode("utf-8"))
        server.the_file.close()
        utilities.send_backtrace("XSS attack on " + server.ticket.user_name,
                                 "URL: %s\nTICKET: %s" % (url, server.ticket),
                                 exception=False)
        return

    server.the_file = p.codec(server.the_file)

    try:
        server.the_ue = server.the_ue
    except AttributeError:
        pass
        
    warn('match %s(%s), path: %s' % (p.name, p.url, server.the_path),
         what='plugin')

    if p.mimetype and not p.upload_max_size:
        p.send_response(server)
    server.plugin = p
    
    if p.keep_open or p.launch_thread:
        server.do_not_close_connection()
        warn('keep_open (closed=%s)' % server.the_file.closed, what='plugin')

    if p.launch_thread:
        warn('launch thread with %s' % server.the_file, what='plugin')
        utilities.start_new_thread(execute, (server, p))
    else:
        execute(server, p)
    warn('done', what='plugin')

            
            
