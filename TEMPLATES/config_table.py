#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2009 Thierry EXCOFFIER, Universite Claude Bernard
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

import document # Fix circular import problem
import data
import utilities
import configuration
import sender

def create(table):
    utilities.warn('Creation')
    if table.year != 0 or table.semester != 'Dossiers':
        raise ValueError('Not allowed')
    p = table.new_page('' ,data.ro_user, '', '')
    table.table_attr(p, 'masters', list(configuration.root))
    table.column_change(p,'0_0','Variable'           ,'Text','','','F',0,2 )
    table.column_change(p,'0_1','Explications'       ,'Text','','','F',0,10)
    table.column_change(p,'0_2','Valeur courante'    ,'Text','','','F',0,10 )
    table.table_attr(p, 'default_nr_columns', 3)
    table.table_attr(p, 'default_sort_column', 1)
    table.new_page('' ,configuration.root[0], '', '')

def init(table):
    table.default_sort_column = 1 # compatibility with old files
    table.private = 1

variables = {
    'abinj': "S'ils ont presque tous une note, ceux qui n'en ont pas ont 0/ABINJ. Si vous mettez 0.25 cela indique que si moins du quart du groupe n'a pas de note alors ils auront 0 ou ABINJ automatiquement.",
    "do_not_display": "Liste des TAG de message à ne pas afficher dans les logs, mettre à vide pour avoir tous les messages",
    'message': "Le message à afficher sur la page d'accueil. On peut y mettre du HTML",
    
    "year_semester": "Semestre : le semestre courant, seul ouvert en écriture.",
    "year_semester_next": "Semestre : le suivant. Modifiable si une UE est fermée (étudiants disparus ou UE vide)",
    "ue_not_per_semester": "UE non semestrialisée si le code correspond à cette expression régulière",
    "master_of_exceptions": "Semestre : ceux que l'on ne veut pas afficher dans la liste des tables dont est responsable",
    "allow_student_list_update": "Semestre : Si 'True' alors la liste des étudiants est mise à jour régulièrement. Il faut mettre à 'False' quand on s'approche de la remise à 0 de la base IP",
    "allow_student_removal": "Semestre : Si 'True' alors on enlève des tables les étudiants non inscrits.",
    'abj_per_semester': "Semestre : Si 'True' les ABJ sont par semestre et non par année",


    'maintainer': "Mail : Adresse ou sont envoyés les messages d'erreur de TOMUSS",
    'smtpserver': 'Mail : Adresse du serveur SMTP pour envoyer des mails',
    'abj_sender': 'Mail : Nom de la personne "envoyant" les mails via TOMUSS listant les ABJ pour toutes les UEs',

    
    'ldap_server': 'LDAP : Liste des serveurs à utiliser (un à la fois)',
    'ldap_server_login': "LDAP : login permettant du compte en lecture seule",
    "ldap_server_password": "LDAP : Mot de passe du compte lecture seule",
    "ldap_server_port": "LDAP : Port utilisés par les serveurs",
    "ldap_encoding": "LDAP : Codage des caractères dans les réponses",

    "attr_login": "LDAP : nom du champ contenant le login",
    "attr_login_alt": "LDAP : nom du champ contenant le login alternatif",
    "attr_mail": "LDAP : nom du champ contenant l'adresse mail",
    "attr_surname": "LDAP : nom du champ contenant le nom de famille",
    "attr_firstname": "LDAP : nom du champ contenant le prénom",
    "attr_default_password": "LDAP : nom du champ contenant le mot de passe par défaut",

    "ou_top": "LDAP: Racine de la hiérarchie",
    "ou_students": "LDAP: Endroit ou sont stockés les comptes étudiants",
    "cn_students": "LDAP: Endroit ou sont stockés les comptes étudiants",
    "cn_teachers": "LDAP: Endroit ou sont stockés les comptes enseignants",
    "ou_groups": "LDAP: Endroit ou sont stockés les groupes d'étudiants",
    "ou_ue_contains": "LDAP: Un objet est une UE avec les séquences/groupe s'il contient cette chaine de caractère",
    "ou_ue_starts": "LDAP: Un objet est une UE s'il commence par cette chaine de caractère",
    "ou_ue_starts2": "LDAP: Un objet est une UE s'il commence par cette chaine de caractère",
    "ou_portail_contains": "LDAP: Un objet est un portail s'il contient cette chaine de caractères",

    "banned_ip": "Accès : Liste des adresses IP interdites",
    "root": "Accès : Liste des utilisateurs ayant tous les droits",
    "teachers": "Accès : Les comptes enseignants sont dans ces groupes",
    "teacher_if_login_contains" : "Accès : C'est un enseignant si son login contient cette chaine de caractères",
    "administratives": "Accès : Les comptes administratifs sont dans ces groupes LDAP",
    "abj_masters": "Accès : Les comptes gestionnaires d'ABJ/TT sont dans ces groupes LDAP",
    "referents": "Accès : Les groupes LDAP définissant les référents pédagogiques",
    "invited_teachers": "Accès : Liste d'enseignants à ajouter au groupe LDAP",
    "invited_administratives": "Accès : Liste des administratifs à ajouter au groupe LDAP",
    "invited_abj_masters": "Accès : Liste des gestionnaires d'ABJ à ajouter au groupe LDAP",


    'students_check_interval': 'Temps : Rechargement de la liste des étudiants : Période en seconde',
    'teacher_stat_interval': 'Temps : Statistiques concernant les enseignants : durée de vie du cache en secondes',
    'maximum_out_of_date': 'Temps : Pour le suivi : durée minimum en secondes entre 2 mise à jour de la même table',
    'maxage': 'Temps : Fichiers statiques : nombre de secondes ou ils restent dans le cache du navigateur',
    'ldap_reconnect': 'Temps : Ferme les connexions LDAP inutilisées pendant cette durée',
    "ticket_time_to_live": "Temps : Durée de vie des tickets en secondes",
    "unload_interval": "Temps : Interval entre deux déchargements des tables inutilisées",
    "check_down_connections_interval": "Temps : Interval de temps pour l'envoi de paquets pour garder les clients vivants",
    "config_debug": "Débuggage en live : résultat de l'évaluation de fonction Python",
    "not_teachers": "Accès : Refuse l'accès s'il appartient à l'un de ces groupes",
    "logo": "URL du logo de fond d'écran",
    "suivi_display_more_ue": "Suivi : Si vrai affiche les UE de l'annuaire qui ne sont pas des tables TOMUSS",
    "language": "Langue utilisée lors de la création des tables pour les titres de colonnes et commentaires.",

    "suivi_student_message": "Message a afficher aux étudiants dans leur suivi",
    }

def check(table):
    utilities.warn('Check')
    p_ro = table.pages[0]
    p_rw = table.pages[1]

    table.lock()
    try:
        for variable, comment in variables.items():
            if variable not in table.lines:
                # Do not change user entered value
                # Do not change default value after the first time.
                v = configuration.__dict__[variable]
                if isinstance(v, list) or isinstance(v, tuple):
                    if len(v) == 0:
                        v = '()'
                    else:
                        v = '(' + ','.join([utilities.js(i) for i in v]) + ',)'
                elif isinstance(v, bool):
                    v = repr(v)
                table.cell_change(p_ro,'0_0', variable,variable)
                table.cell_change(p_rw, '0_2', variable, v)
            table.cell_change(p_ro, '0_1', variable, comment)
    finally:
        table.unlock()

def set_value(variable, value):
    if variable == 'config_debug':
        try:
            if configuration.regtest:
                return 'Action not allowed in demo mode'
            else:
                return repr(eval(value))
        except:
            import traceback
            import sys
            return '\n'.join(list(traceback.format_tb(sys.exc_info()[2])))
    
    current = configuration.__dict__[variable]

    if isinstance(current, tuple) or isinstance(current, list) \
             or isinstance(current, bool):
        if configuration.regtest:
            import re
            try:
                # Forbidden: function calls and item access
                if re.match(r".*.[[(].*",value):
                    utilities.warn('Possible Hacking:' + value, what='error')
                    return
            except TypeError:
                pass
        value = eval(value)
        assert(isinstance(value, type(current)))
    elif isinstance(current, float):
        value = float(value)
    elif isinstance(current, int):
        value = int(value)
    configuration.__dict__[variable] = value

def onload(table):
    variables.update(configuration.local_options)

    if len(table.lines) == 0:
        return
    utilities.warn('Onload')
    for variable in variables:
        if variable in table.lines: # do not create it by reading it
            set_value(variable, table.lines[variable][2].value)

    # Can't be done before (not nice :-( )
    import files
    files.files['doc_table.html'].replace('config_table',
                                          '_ADMIN_', configuration.maintainer)


def cell_change(table, page, col, lin, value, date):
    if page.page_id <= 1:
        return
    if col != '0_2':
        return
    try:
        a = set_value(lin, value)
        if a is not None:
            sender.append(page.browser_file,
                          '<script>alert("Eval:\\n"+%s);</script>' %
                          utilities.js(a))
    except:
        import traceback
        import sys
        sender.append(page.browser_file,
                      '<script>alert(%s);</script>' %
                      utilities.js(str(sys.exc_info()[0])))
        raise

    tell_to_reload_config()

def tell_to_reload_config():
    utilities.start_new_thread(tell_reload_config, ())

def tell_reload_config():
    import urllib2
    utilities.warn('Tell "suivi" to reload config')
    for url, port, year, semester, host in configuration.suivi.urls.values():
        try:
            f = urllib2.urlopen(url + '/load_config')
            f.read()
            f.close()
        except urllib2.URLError:
            pass # If one 'suivi' server is not running, continue
        
