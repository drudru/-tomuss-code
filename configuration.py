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

import socket
import os
import time

version = '2.12.6'

# The following information can be redefined by python modules
# loaded at the end of this file.
# DO NOT EDIT THE VALUES IN THIS FILE.
# ONLY DO THE IMPORT OF YOUR CONFIGURATION FILE IN THE terminate FUNCTION.
# Or you can edit the configuration table :
#           http://........./0/Dossiers/config_table

###############################################################################
# The following variables are used only on the _first_ TOMUSS start.
# They define default values.
# They are tunable while TOMUSS is running in the table :
#           http://........./0/Dossiers/config_table
###############################################################################

# The student group is 'ranked' if there is less than 'abinj' (normalized)
# students not present or noted.
abinj = 0.25

# Check the list of student each X seconds (for actives UE)
students_check_interval = 3600

# For 'suivi.py' compute teacher statistics each X seconds
teacher_stat_interval = 3600

# For 'suivi.py' reload the table if it is out of date of X seconds
maximum_out_of_date = 60

# The static files stay in navigator cache this time
maxage = 3600

# Unload every table not used every X seconds :
unload_interval = 600

# Send a ' ' to the clients in order to keep them connected, every X seconds
check_down_connections_interval = 60

# The students list of the UE are updated
allow_student_list_update = True

# Allow to remove student from tables
allow_student_removal = True

# The ticket have a TTL...
ticket_time_to_live = 10 * 3600 # in seconds

# Current semester/year
year_semester = (time.localtime()[0], 'Printemps')

# Semester always in the menu on the first page.
# Other are added for each 'suivi' server.
special_semesters = '<option>2008/Test</option><option>2008/Printemps</option>'

# Next semester (usable if UE is closed)
year_semester_next = (time.localtime()[0], 'Automne')

# Semester we don't want to be displayed as a 'master_of'
master_of_exceptions = ('Printemps', 'Automne', 'Test', 'Referents', 'Preferences')

# The TOMUSS super user
root = ('super.user',)

# The mail address of TOMUSS manager (destination address of bug messages)
maintainer = root[0] + '@' + socket.getfqdn()

# SMTP that send messages
smtpserver = '127.0.0.1'

# Reply to for ABJ mail messages
abj_sender = maintainer

# ABJ per semester or per year
abj_per_semester = True
# If 'abj_per_semester' become False, then this is the switch year.
# The years strictly before have abj per semester.
abj_per_semester_before = 2011

# Return True if the name is the code of an official UE.
# The official UE are displayed to the students in the suivi.
def is_an_official_ue(code):
    return True


# LDAP informations
# A list of LDAP server to query
ldap_server = ('ldap1.domain.org', 'ldap2.domain.org', 'ldap3.domain.org')
ldap_server_login = 'login_name'
ldap_server_password = 'the_password'
ldap_server_port = 389
ldap_encoding = 'utf8'
ldap_reconnect = 60

# Defines authorities by a login name list
invited_administratives = ('tt.master',)
invited_abj_masters = ('abj.master','tt.master')
invited_teachers = tuple(['ue%d.master' % i for i in range(10)])


# A login is assumed as a teacher one if it contains this stubstring
teacher_if_login_contains = '#'

# LDAP attributes
attr_login            = "sAMAccountName"
attr_login_alt        = "msSFUName"    # Tried if not found with the first one
attr_mail             = "mail"
attr_surname          = "sn"
attr_firstname        = "givenName"
attr_default_password = "password"

# TOP
ou_top = "DC=univ-lyon1,DC=fr"

# Where all the students belong.
ou_students = 'OU=etudiants,DC=univ-lyon1,DC=fr'

# Where all the groups of students belong.
ou_groups = "OU=groupes,OU=etudiants,DC=univ-lyon1,DC=fr"
ou_ue_contains = 'elp-'         # UE group name contains this string
ou_ue_starts = 'CN=UE-'         # UE name starts with
ou_portail_contains = ' APO-'   # UE portail name contains this string

# Banned list of IP addresses
banned_ip = ( '255.255.255.255', '0.0.0.0' )

# LOGO URL
logo = 'http://xxx.yyy.zzz/logo.png'

#--------------------------------------
# Defines authorities using LDAP groups
#--------------------------------------

teachers = (
    'CN=Teachers,OU=Groupes,DC=univ-lyon1,DC=fr',
    'CN=Professors,OU=Groupes,DC=univ-lyon1,DC=fr',
    )

# It is not a teacher if it is in one of these groups
not_teachers = (
    'CN=NotTeachers,OU=Groupes,DC=univ-lyon1,DC=fr',
    )

administratives = (
    'CN=Administratives,OU=Groupes,DC=univ-lyon1,DC=fr',
    'CN=Administratives2,OU=Groupes,DC=univ-lyon1,DC=fr',
    )

abj_masters = (
    'CN=Administratives3,OU=Groupes,DC=univ-lyon1,DC=fr',
    'CN=Administratives4,OU=Groupes,DC=univ-lyon1,DC=fr',
    )

referents = (
    "CN=referents-fst,OU=Groupes,OU=UFR Sciences et Technologies,DC=univ-lyon1,DC=fr",
    )

###############################################################################
# The following variables should be fine for testing purpose (local server)
# THEY MUST BE REDEFINED in LOCAL.__init__.py
###############################################################################

# With True, this allow the URLs : http://....../=login.name/
# Where the ticket is the login name.
# If there is a real authentication, it should be set to False.
regtest = False
regtest_sync = False

# Name of the database directory (should not start by ., .. or /)
db = 'DBtest'
# The backup name if prepended to the 'db' name.
backup = 'BACKUP_' # Use None or False or '' if no backup

# URL of the 'tomuss' server
server_port = 8888
server_base_url = 'http://' + socket.getfqdn()
server_url = '%s:%d' % (server_base_url, server_port)

# URLs of the 'suivi' servers
import servers
suivi = servers.Suivi()
suivi.add(time.localtime()[0], 'Printemps', socket.getfqdn() + ':%d', 8889)
suivi.add(time.localtime()[0], 'Automne', socket.getfqdn() + ':%d', 8890)
# suivi.add(2008, 'Automne'  , socket.getfqdn() + ':%d', 8889)

# Do not display 'debug' warning
do_not_display = ('debug', 'auth', 'table', 'ldap', 'plugin', 'check')

# Message on the top page
message = '<b>Envoyez tout de suite un mail à <a href="mailto:' + maintainer + '">l\'administrateur</a> quand il y a un problème.</b>'

ticket_directory = os.path.join('TMP', 'TICKETS')

# A dictionnary of local configuration options
# It is used by TEMPLATES/config_table.py
# It is filled by LOCAL/....py
local_options = {}

###############################################################################
# The following variables are not expected to be useful without modification
###############################################################################

# The CAS server for authentication.
cas = 'https://cas.domain.org/cas'


# Link between the OU and the starts of the UE code.
# This allow to display only the UE of interest for the user.
# A teacher of 'CN=1692 UFR INFORMATIQU...' will see by default UE INF...

ufr_short = {
    'Département Informatique,OU=UFR Sciences et Technologies':('INF','IF'),
    'Département Mathématiques,OU=UFR Sciences et Technologies':('MAT','MT'),
    'Département Physique,OU=UFR Sciences et Technologies':('PHY',),
    'Département Biologie,OU=UFR Sciences et Technologies' : ('BIO',),
    'Département Chimie Biochimie,OU=UFR Sciences et Technologies':('BCH',),
    'CN=1691 UFR GENIE ELECTRIQUE ET DES PROCEDES,OU=Groupes,DC=univ-lyon1,DC=ff': ('GEP',),
    'Département Sciences de la Terre,OU=UFR Sciences et Technologies':('STU',),
    'Département Mécanique,OU=UFR Sciences et Technologies':('MGC',),
    'UFR S.T.A.P.S.': ('SP',),
    'Inst. Sciences et Techniques de l\'Ingénieur de Lyon (ISTIL)':('IS',),
    'OU=IUTB': ('IB',),
    'OU=IUTA': ('IA',),
}

# OU containing student by year of inscription.
the_portails = {
    'MATINFL1' :
    ("CN=DV0011 etape-DV0011,OU=groupes,OU=etudiants,DC=univ-lyon1,DC=fr",
     "CN=DV011B etape-DV011B,OU=groupes,OU=etudiants,DC=univ-lyon1,DC=fr",
     ),
    'MATINFL2' :
    ("CN=DV0012 etape-DV0012,OU=groupes,OU=etudiants,DC=univ-lyon1,DC=fr",
     "CN=DV012B etape-DV012B,OU=groupes,OU=etudiants,DC=univ-lyon1,DC=fr",
     ),
    'INFL3' :
    ('CN=IF5631 etape-IF5631,OU=groupes,OU=etudiants,DC=univ-lyon1,DC=fr',
     "CN=IF531B etape-IF531B,OU=groupes,OU=etudiants,DC=univ-lyon1,DC=fr",
     ),
    'MATL3' :
    ('CN=MT2731 etape-MT2731,OU=groupes,OU=etudiants,DC=univ-lyon1,DC=fr',
     "CN=MT231B etape-MT231B,OU=groupes,OU=etudiants,DC=univ-lyon1,DC=fr",
     ),
    'MIVMATL3' :
    ("CN=MT2734 etape-MT2734,OU=groupes,OU=etudiants,DC=univ-lyon1,DC=fr",
     ),
    'MIVINFL3' :
    ('CN=IF5633 etape-IF5633,OU=groupes,OU=etudiants,DC=univ-lyon1,DC=fr',
     ),
    'UFRFST' :
    (
        'CN=148891 CGE-UFR Sciences et Technologie,OU=groupes,OU=etudiants,DC=univ-lyon1,DC=fr',
        'CN=139284 APO-UFR Sciences et Technologie,OU=groupes,OU=etudiants,DC=univ-lyon1,DC=fr',
        'CN=OU=UFR Sciences et Technologies,DC=univ-lyon1,DC=fr',
        ),
    }

#-----------------------------------------
# Defines some URL
#-----------------------------------------

# Append the student ID in order to have the full student history
bilan_des_notes = "http://students.domain.org/history?student_id="

#REDEFINE
# This function returns the URL of the student picture.
# This example is for the demonstration site, in which the students
# picture are dispatched by the TOMUSS server.
def picture(student_id):
    import utilities
    return utilities.StaticFile._url_ + '/' + student_id + '.png'

#REDEFINE
# This function returns a string inserted into student suivi page
def more_on_suivi(student_login):
    return ''

# And an error message if the password is trivial
bad_password = """
<div onclick="this.style.display='none';"
     style="border:5px solid black;padding:5px;position:absolute;left:10%;top:10%;right:10%;background:red;color:white;font-size:150%">
     Vous devez changer votre mot de passe car il est trop simple.<br><br>
     N'importe quel étudiant peut changer ses notes ou faire
     une escroquerie en votre nom."""

###############################################################################
###############################################################################

# XXX Avoid bug in Python 2.4 (fildes not closed in circular list)

import urllib
urllib.addinfourl.close_original = urllib.addinfourl.close
def close_patched(self):
    try:
        self.fp._sock.recv=None
    except:
        pass
    return self.close_original()
urllib.addinfourl.close = close_patched

###############################################################################
# DO NOT MODIFY
###############################################################################
read_only = False

config_debug = ''

###############################################################################
# Terminate configuration
###############################################################################

def terminate():
    """Apply local change to the modules, should be called once
    all the modules are loaded"""

    import utilities
    import sys

    if not regtest:
        import LOCAL     # Your local configuration goes inside LOCAL

    global maxage, backup

    if db == 'DBtest' or db == 'DBregtest':
        utilities.do_not_display = ()
        maxage = 1

    for dirname in (db, os.path.join(db, 'Y0', 'Stats')):
        if not os.path.isdir(dirname):
            utilities.mkpath(dirname)
        if backup and not os.path.isdir(backup + dirname):
            utilities.mkpath(backup + dirname)

    if os.path.exists('tomuss.py'):
        if not os.path.isdir(db):
            utilities.mkpath(db)
        if not os.path.isdir(backup + db):
            utilities.mkpath(backup + db)
        if not os.path.isdir('TMP'):
            utilities.mkpath('TMP')
        if not os.path.exists(ticket_directory):
            os.mkdir(ticket_directory)

        if not os.path.exists(os.path.join(db, '__init__.py')):
            utilities.write_file(os.path.join(db, '__init__.py'),'')
        if not os.path.exists(os.path.join(backup + db, '__init__.py')):
            utilities.write_file(os.path.join(backup + db, '__init__.py'),'')

        if not os.path.isdir(backup + db):
            sys.stderr.write('Backup disabled : directory does not exists\n')
            backup = ''

    import inscrits
    utilities.warn('Create LDAP connector')
    inscrits.L = inscrits.LDAP()

