#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2008-2009 Thierry EXCOFFIER, Universite Claude Bernard
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
import os
import inscrits
import configuration
import referent
import teacher
import time
import document

top = utilities.StaticFile(os.path.join('FILES','top.html'))

options = '<option>2008/Test</option><option>2008/Printemps</option>'
urls = configuration.suivi.urls.values()
# XXX HORRIBLE KLUDGE because Autumne is before Printemps
# sort the semesters by time
urls.sort(cmp=lambda x,y: cmp( (x[2], y[3]), (y[2], x[3]) ))
for url, port, year, semester, host in urls:
    if configuration.year_semester[1] == semester and configuration.year_semester[0] == year:
        selected = ' selected'
    else:
        selected = ''
    options += '<option%s>%s/%s</option>' % (selected, year, semester)
top.replace_on_load('</select>', options + '</select>')

import files
files.files['middle.js'].replace_on_load('__OPTIONS__',
                                         options.replace('selected',''))

def home_page(server):
    """Display TOMUSS home page, it extracts some links from the
    plugin list. The page content depends on user role."""
    f = server.the_file
    ticket = server.ticket

    ufr = inscrits.ufr_of_teacher(ticket.user_name)

    if inscrits.password_ok(ticket.user_name):
        password_ok = ''
    else:
        password_ok = configuration.bad_password

    f.write(top.replace('_MESSAGE_', password_ok)
            .replace('_BASE_',
                     configuration.server_url+'/='+ticket.ticket+'/')
            .replace('_SUIVI_', configuration.suivi.all(ticket.ticket))
            .replace('_UFR_',
                     'UE-' + configuration.ufr_short.get(ufr,('',''))[0])
            .replace('_USERNAME2_',
                    utilities.login_to_module(ticket.user_name))
            .replace('_USERNAME_', ticket.user_name)
            .replace('_TICKET_', ticket.ticket)
            .replace('_MESSAGE2_', configuration.message)
            .replace('_ADMIN_', configuration.maintainer)            
            )
    f.write('''<table class="undertop"><tr><th>Quelques liens :</th></tr><tr><td><ul class="t2">''')

    if ticket.is_an_abj_master:
        f.write('<li>Gestion des ABJ, DA et TT<ul>')
        f.write('<li> <a href="javascript:go_year(\'Dossiers/tt\')">Modification des TT</a> (<a href="javascript:go_year(\'Dossiers/tt/=read-only=\')">consultation</a>)')
        for message in plugin.get_menu_for('abj_master', server):
            f.write('<li> ' + message + '</li>\n')
        f.write('</ul>')

    #####################################################################

    favorites = utilities.manage_key('LOGINS',
                                     os.path.join(ticket.user_name, 'pages'))
    if favorites is False:
        favorites = {}
    else:
        favorites = eval(favorites)
    sorted_favorites = list(favorites.keys())
    sorted_favorites.sort(key= lambda x: favorites[x])
    sorted_favorites.reverse()

    if favorites:
        all_ues = teacher.all_ues()
        f.write('<li> Vos UE favorites : <ul>')
        for ue in sorted_favorites[:6]:
            try:
                intitule = all_ues.get(ue.split('-')[1]).intitule().encode('utf8')
            except:
                intitule = '???'
            f.write('<li> <a href="javascript:go(\'%s\')">%s %s</a>' % (
            ue, ue, intitule))
        f.write('</ul>')

    #####################################################################

    master_of = utilities.manage_key('LOGINS',
                                     os.path.join(ticket.user_name,
                                                  'master_of'))
    if master_of is False:
        master_of = []
    else:
        master_of = eval(master_of)
    master_of.sort()

    if master_of:
        f.write('<li> Tableaux (hors UE) dont vous êtes responsable : <ul>')
        for year, semester, ue in master_of:
            intitule = '%s/%s/%s' % (year, semester, ue)
            f.write('<li> <a target="_blank" href="/=%s/%s">%s</a>' % (
            ticket.ticket, intitule, intitule))
        f.write('</ul>')

    #####################################################################

    f.write('<li><a href="javascript:go_suivi(\'\')">Suivi des étudiants</a>')
    f.write('<li> Référents : ' +
            '<a href="javascript:go(\'referents\')">Table TOMUSS</a> :: ' +
            '<a href="javascript:go_suivi(\'referents.csv\')">Table CSV</a>')
    if ticket.is_a_referent_master:
        f.write(' :: <a href="/=%s/referents">Affectation</a>' % ticket.ticket)
    f.write('</li>\n')


    f.write('<li> Statistiques : ' +
            '<a href="javascript:go_suivi(\'*\')">Enseignants</a> :: ' +
            '<a href="javascript:go_suivi(\'*2\')">UEs</a> :: ' +
            '<a href="javascript:go_suivi(\'*3\')">Référents</a> :: ' +
            '<a href="javascript:go_suivi(\'*1\')">Étudiants sans IP</a> :: ' +
            '<a target="_blank" href="/stats.html">TOMUSS</a>'
            '</li>\n')

    if ticket.user_name in configuration.root:
        f.write('<li>Pour les administrateurs<ul><li>liens sans danger :<ul>')
        f.write('<li><a href="javascript:go_suivi(\'badname\')">Liste des noms ne correspondant pas au numéro d\'étudiant</a>')
        f.write('<li><a  target="_blank"href="%s/preferences">Fusion des préférences</a>'
                % configuration.suivi.url(configuration.year_semester[0],
                                          configuration.year_semester[1],
                                          ticket=ticket.ticket))
        f.write('<li><a href="javascript:go_suivi(\'ip\')">Pour faire les IP automatiquement</a>')
        f.write('<li><a href="javascript:go_suivi(\'uninterested\')">Étudiants suivis ne regardant pas TOMUSS</a>')
        f.write('<li><a target="_blank" href="/=%s/2009/Dossiers/javascript_regtest_ue">Tests de régression en JavaScript</a>' % ticket.ticket)
        f.write('<li><a href="javascript:go(\'demo_animaux\')">Démo animaux</a>')
        for message in plugin.get_menu_for('root_ro', server):
            f.write('<li> ' + message + '</li>\n')
        f.write('</ul>')


        f.write('<li>liens dangereux :<ul>')
        f.write('<li><a href="javascript:go_suivi(\'favorites\')">Ne PAS UTILISER : Réinitialisation des UE favorites à partir du semestre indiqué en cas de bug.</a>')
        f.write('<li><a target="_blank" href="/=%s/0/Dossiers/config_table">Configuration de TOMUSS</a>' % ticket.ticket)
        for message in plugin.get_menu_for('root_rw', server):
            f.write('<li> ' + message + '</li>\n')
        f.write("""<li> Envoyer une fenêtre d'alerte à tous les utilisateurs en ligne avec le message suivant (il est éditable)&nbsp;: <form action="javascript:var m = document.getElementById('message').value ; if(confirm('Vous allez envoyer le message :\\n\\n' + m)) window.location='=%s/send_alert//' + m"><input id="message" name="x" class="keyword" value="Le serveur va être redémarré dans quelques secondes, il est conseillé (mais non obligatoire) de réactualiser la page après le redémarrage."></form>""" % ticket.ticket)
        f.write('</ul>')

        f.write('</ul>')


        f.write("<li>Les portails : " +
                ',\n'.join(['<a href="javascript:go(%s)">%s</a>' %(
            repr('portail-' + p),p)
                            for p in configuration.the_portails])
                )



    f.write('''</ul></td></tr></table>''')

    f.write('''<table class="undertop"><tr><th>Les étudiants pour lesquels vous êtes référent :</th></tr><tr><td><ul class="t3">''')
    s = []
    mails = []
    students = []
    for login in referent.students_of_a_teacher(ticket.user_name):
        firstname,surname,mail = inscrits.firstname_and_surname_and_mail(login)
        students.append( (surname, firstname, mail,
                          utilities.the_login(login)) )
    students.sort() # alpha
    for firstname, surname, mail, student in students:
        s.append('<li><script>hidden(\'<img class="icone" src="%s/_%s">\',\n\'<img class="bigicone" src="%s/_%s">\');\n hidden(' % (
            configuration.suivi.url(ticket=ticket.ticket),
            student,
            configuration.suivi.url(ticket=ticket.ticket),
            student) +
                 '\'\\x3Ca href="javascript:go_suivi(\\\'' +
                 student +
                 '\\\')"\\x3E' +
                 (firstname + ' ' + surname).replace("'", "\\'") +
                 '\\x3C/a\\x3E\',\n' +
                 '\'<img class="photo" src="%s">\'' % configuration.picture(inscrits.login_to_student_id(student)) +
                 ');</script>\n</li>\n')
        if mail:
            mails.append(mail)
    f.write('\n'.join(s).encode('utf-8'))
    f.write('''</ul>''')
    if mails:
        f.write("<p><script>hidden('Explication des Icones.','Le carré de gauche représente les présences, celui de droite les notes.<br>Dans les deux cas, les informations les plus récentes sont en haut du carré');</script>")
        f.write('<p>Pour le groupe complet d\'étudiant :<ul>')
        f.write('<li><a href="mailto:?subject=[REFERENT]&bcc=%s">Envoyer un message aux étudiants suivis</a>.' % ','.join(mails).encode('utf-8'))
        f.write('<li><a href="javascript:go_suivi(\'' +
                ','.join(zip(*students)[3]) + '\')">Suivi</a> : Affiche un résumé pour tous les étudiants.')
        f.write('<li><a href="javascript:go_referent()">Blocnote</a> pour faire le suivi.')
    f.write('''</ul></td></tr></table>''')
    
    f.write('''<table class="undertop"><tr><th>Les UEs pour lesquelles vous êtes un <b>responsable indiqué dans SPIRAL&nbsp;:</b></th></tr><tr><td>''')

    f.write('<div class="ue_list" id="ue_list_spiral"></div>')
    f.write('</td></tr></table>')
    f.write('</td></tr></table>')
    # XXX Tester si accept gz dans les headers
    try:
        encodings = server.headers['Accept-Encoding']
    except KeyError:
        encodings = ''
    utilities.warn('Encodings: ' + encodings)
    if 'Safari' not in ticket.user_browser \
       and 'Konqueror' not in ticket.user_browser \
       and 'gzip' in encodings:
        f.write('<script src="/all_ues.js.gz"></script>')
    else:
        f.write('<script src="/all_ues.js"></script>')
    f.write('<script src="/top_tail.js"></script>')


plugin.Plugin('homepage', '/home', function=home_page, teacher=True,
              launch_thread=True)
