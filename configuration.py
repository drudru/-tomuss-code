#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2008-2013 Thierry EXCOFFIER, Universite Claude Bernard
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

"""
This file must not be edited. But you should read it.

The modifications must be done in LOCAL/config.py

Once TOMUSS server is running, the configuration can be done interactively.
"""

import socket
import os
import time

version = '5.2.9'

###############################################################################
# ACLS
# Theses parameters are only used only on the first tomuss start.
# They are used to create :
#   http://127.0.0.1:8888/0/Dossiers/config_acls
# This table must be used to change user groups or add ones.
# Only change the 'root' name, the group tree will be editable in the table.

# The TOMUSS super user
root = ('super.user',)

# Defines authorities by a login name list
invited_teachers = tuple(['ue%d.master' % i for i in range(10)])
invited_administratives = ('tt.master',)
invited_abj_masters = ('abj.master','tt.master')
tt_masters = ('abj.master','tt.master')

#--------------------------------------
# Defines authorities using LDAP groups
#--------------------------------------

teachers = (
    'CN=Teachers,OU=Groupes,DC=univ-lyon1,DC=fr',
    'CN=Professors,OU=Groupes,DC=univ-lyon1,DC=fr',
    )

administratives = (
    'CN=Administratives,OU=Groupes,DC=univ-lyon1,DC=fr',
    'CN=Administratives2,OU=Groupes,DC=univ-lyon1,DC=fr',
    )

abj_masters = (
    'CN=Administratives3,OU=Groupes,DC=univ-lyon1,DC=fr',
    'CN=Administratives4,OU=Groupes,DC=univ-lyon1,DC=fr',
    )

# DEPRECATED: It is not a teacher if it is in one of these groups
# Use '!' in config_ACL table.
not_teachers = (
    'CN=NotTeachers,OU=Groupes,DC=univ-lyon1,DC=fr',
    )
# It is not a teacher if it is one of these login
login_not_teacher = ('banned_login1', 'banned_login2')

referents = (
    "CN=referents-fst,OU=Groupes,OU=UFR Sciences et Technologies,DC=univ-lyon1,DC=fr",
    )

###############################################################################
# The semester list must not change in the time.
# The student 'suivi' is on these semesters.
#
# The semesters are defined in the REAL YEAR order (not university one)
# The quadruples are :
#   * The semester name as it is used on the screen and on the filesystem
#   * The value to add to the year to find the 'university' year.
#     To use semesters with the university year number: use [0, 0] and
#     define the semesters in the order of the university year
#   * The first and last year month of the semester.
#     From 1 to 23, 13 = January the next year
#   * The HTML page background color.
# By the way, you can use 1, 2 or more semesters...
# You need to create TEMPLATES for each semester (See Automne.py)

def set_semesters(*x):
    global semesters, semesters_year, semesters_months, semesters_color
    global university_semesters
    
    semesters, semesters_year, semesters_months, semesters_color = zip(*x)

    # For old Python version
    semesters_year = list(semesters_year)
    semesters = list(semesters)

    # construct the university semesters from previous information
    university_semesters = (semesters[semesters_year.index(0):]
                            + semesters[:semesters_year.index(0)])


set_semesters(
    ('Printemps', -1, [2, 7], '#EEFFEE' ),  # Spring (Semester 2)
    ('Automne'  ,  0, [8,13], '#FFE8D0' ),  # Autumn (Semester 1)
    )

#REDEFINE
# Time span of the given semester
def semester_span(year, semester):
    try:
        i = semesters.index(semester)
    except ValueError:
        return
    def p(month):
        overflow = int(month > 12)
        return '%d/%d' % (month - overflow*12, year + overflow)
    return '1/%s 31/%s' % (p(semesters_months[i][0]),
                           p(semesters_months[i][1]))

###############################################################################
# Or you can edit the configuration table while TOMUSS is running :
#           http://........./0/Dossiers/config_table
# The following variables are used only on the _first_ TOMUSS start.
# They define default values.
###############################################################################

# The language used when creating new tables (for columns, comments...)
# The users can set their preferred language for the interface,
# but their language is not the language used for table creation.
language = 'en'

# The student group is 'ranked' if there is less than 'abinj' (normalized)
# students not present or noted.
abinj = 0.25

# Check the list of student each X seconds (for actives UE)
students_check_interval = 3600

# For 'suivi.py' reload the table if it is out of date of X seconds
maximum_out_of_date = 60

# The static files stay in navigator cache this time
# Beware, the UE list will not be reloaded for this time.
maxage = 3600*24

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
year_semester = (time.localtime()[0], semesters[0])

# Semester always in the menu on the first page.
# Other are added for each 'suivi' server.
special_semesters = '<option>2008/Test</option>'

# Next semester (usable if UE is closed)
year_semester_next = (time.localtime()[0], semesters[1])

# A list of pairs defining writable semesters
year_semester_modifiable = ([2008, 'Test'],)

# UE not by semester, if its code match this regular expression
ue_not_per_semester = "^UE-[A-Z]{3}[0-9]{4}M$"

# Semester we don't want to be displayed as a 'master_of'
master_of_exceptions = ('Test', 'Referents', 'Preferences', 'Favoris')

# The mail address of TOMUSS manager (destination address of bug messages)
maintainer = root[0] + '@' + socket.getfqdn()

# SMTP that send messages
smtpserver = '127.0.0.1'

# Reply to for ABJ mail messages
abj_sender = maintainer

# Display students UE list for which there is no TOMUSS table
suivi_display_more_ue = True

# Number of days in the future allowed for the column visibility date
max_visibility_date = 31

#REDEFINE
# Return True if the name is the code of an official UE.
# The official UE are displayed to the students in the suivi.
def is_an_official_ue(code):
    "Must be 0 or 1 (JavaScript compatible)"
    return 1

#REDEFINE
# Return the list of table manager
# Their only right is to modify the 'masters' table attribute
def get_managers(ue_code):
    "Return a list of managers logins"
    return []

#REDEFINE
# Return True if is is a student login
def is_a_student(login):
    return login and len(login) >= 2 and login[1].isdigit()

#REDEFINE
# Returns 0 if it is not the first registration of the student.
# Else, returns the year of the first registration.
def first_registration(login):
    from . import inscrits
    if login[1:3] == str(year_semester[0])[2:4]:
        for group in inscrits.L_batch.member_of_list(login):
            if '1A,OU=' in group:
                return 1
            if '2A,OU=' in group:
                return 2
            if '3A,OU=' in group:
                return 3
    return 0

#REDEFINE
# Returns True if the student is in the first year.
# The information is displayed in the 'blocnote'
def student_in_first_year(login):
    return first_registration(login) == 1

#REDEFINE
# Returns False to hide the student suivi to every one.
# Returns True to display the student suivi
# Returns None to allow 'suivi' acces to teachers grading the student
# or to anybody if the student has not restricted the access
def visible_from_suivi(dummy_server, dummy_login):
    # You can check the teacher name in dummy_server.ticket.user_name
    # and the student name in dummy_login
    return None

# LDAP informations
# A list of LDAP server to query
ldap_server = ('ldap1.domain.org', 'ldap2.domain.org', 'ldap3.domain.org')
ldap_server_login = 'login_name'
ldap_server_password = 'the_password'
ldap_server_port = 389
ldap_encoding = 'utf8'
ldap_reconnect = 60

# A login is assumed as a teacher one if it contains this stubstring
teacher_if_login_contains = '#'

# LDAP attributes
attr_login            = "sAMAccountName"
attr_login_alt        = "msSFUName"    # Tried if not found with the first one
attr_mail             = "mail"
attr_surname          = "sn"
attr_firstname        = "givenName"
attr_default_password = "password"
attr_phone            = "telephoneNumber"

# TOP
ou_top = "DC=univ-lyon1,DC=fr"

# Where all the students belong.
ou_students = 'OU=etudiants,DC=univ-lyon1,DC=fr'
cn_students = 'CN=etudiants,OU=groupes,OU=etudiants,DC=univ-lyon1,DC=fr'

# Where all the teacher belong.
cn_teachers = 'CN=5 HARP-Groupe des groupes Personnels,OU=Groupes,DC=univ-lyon1,DC=fr'

# Where all the groups of students belong.
ou_groups = "OU=groupes,OU=etudiants,DC=univ-lyon1,DC=fr"
ou_ue_contains = 'elp-'         # UE group name contains this string
ou_ue_starts = 'CN=UE-'         # UE name starts with
ou_ue_starts2 = 'CN=EC-'        # UE name starts with
ou_portail_contains = ' APO-'   # UE portail name contains this string

# Banned list of IP addresses
banned_ip = ( '255.255.255.255', '0.0.0.0' )

# LOGO URL
logo = 'http://xxx.yyy.zzz/logo.png'

# Message for students
suivi_student_message = ""

# Allow the students to make their 'suivi' page private
suivi_student_allow_private = False

# Allow the recording of user interaction with the table editor
gui_record = False


###############################################################################
# The following variables should be fine for testing purpose (local server)
###############################################################################

# With True, this allow the URLs : http://....../=login.name/
# Where the ticket is the login name.
# If there is a real authentication, it should be set to False.
regtest = False
regtest_sync = False

# Name of the database directory (should not start by ., .. or /)
db = 'DB'
# The backup name is prepended to the 'db' name.
backup = 'BACKUP_' # Use None or False or '' if no backup

# URL of the 'tomuss' server
server_port = 8888
server_base_url = 'http://' + socket.getfqdn()
server_url = '%s:%d' % (server_base_url, server_port)

# URLs of the 'suivi' servers
# This example defines 3 servers for the current university year.
# Changing these values may break the regression tests.
# You must redefine your semesters in LOCAL/config.py
# To launch only one process: use the same port number
from . import servers
suivi = servers.Suivi(https=False)
suivi.add(time.localtime()[0]  , semesters[0],socket.getfqdn()+':%d', 8889)
suivi.add(time.localtime()[0]  , semesters[1],socket.getfqdn()+':%d', 8890)

# Do not display 'debug' warning
do_not_display = ('debug', 'auth', 'table', 'ldap', 'plugin',
                  'check', 'lang', 'DNU')

# Message on the top page
message = ''

ticket_directory = os.path.join('TMP', 'TICKETS')

# A dictionnary of local configuration options
# It is used by TEMPLATES/config_table.py
# It is filled by LOCAL/....py scripts
# For exemple, to define 'configuration.FOO' attribute :
#   configuration.FOO = True
#   configuration.local_options['FOO'] = 'Set to True to enable option FOO'
# Once the default value for the option is defined, it can be modified
# using the configuration table as the other options.

local_options = {}

###############################################################################
# The following variables are not expected to be useful without modification
###############################################################################

# The CAS server for authentication.
cas = 'https://configure.cas.url.or.use.regtest.parameter/cas'

# OU containing student by year of inscription.
# It is only useful to do the automatic selection of referent-teacher students
the_portails = {
    'MATINFL1' :
    ("CN=DV0041 etape-DV0041,OU=groupes,OU=etudiants,DC=univ-lyon1,DC=fr",
     ),
    'MATL2' :
    ("CN=MT3522 etape-MT3522,OU=groupes,OU=etudiants,DC=univ-lyon1,DC=fr",
     ),
    'INFL2' :
    ("CN=IF6720 etape-IF6720,OU=groupes,OU=etudiants,DC=univ-lyon1,DC=fr",
     ),
    'INFL3' :
    ('CN=IF6731 etape-IF6731,OU=groupes,OU=etudiants,DC=univ-lyon1,DC=fr',
     'CN=IF6733 etape-IF6733,OU=groupes,OU=etudiants,DC=univ-lyon1,DC=fr',
     'CN=IF6734 etape-IF6734,OU=groupes,OU=etudiants,DC=univ-lyon1,DC=fr',
     ),
    'MATL3' :
    ('CN=MT3531 etape-MT3531,OU=groupes,OU=etudiants,DC=univ-lyon1,DC=fr',
     'CN=MT3532 etape-MT3532,OU=groupes,OU=etudiants,DC=univ-lyon1,DC=fr',
     'CN=MT3533 etape-MT3533,OU=groupes,OU=etudiants,DC=univ-lyon1,DC=fr',
     'CN=MT3534 etape-MT3534,OU=groupes,OU=etudiants,DC=univ-lyon1,DC=fr',
     ),
    'UFRFST' : # The groups of student that should have a referent teacher
    (
        'CN=176511 CGE-UFR Sciences et Technologie,OU=groupes,OU=etudiants,DC=univ-lyon1,DC=fr',
        'CN=148891 CGE-UFR Sciences et Technologie,OU=groupes,OU=etudiants,DC=univ-lyon1,DC=fr',
        'CN=139284 APO-UFR Sciences et Technologie,OU=groupes,OU=etudiants,DC=univ-lyon1,DC=fr',
#        'CN=OU=UFR Sciences et Technologies,DC=univ-lyon1,DC=fr',
        ),
    }

#-----------------------------------------
# Defines some URL
#-----------------------------------------

# Append the student ID in order to have the full student history
bilan_des_notes = "http://students.domain.org/history?student_id="

#REDEFINE
# This function returns the URL of the student picture.
# This example assumes that TOMUSS itself send pictures.
def picture(student_id, ticket):
    from . import utilities
    return (utilities.StaticFile._url_ + '/=' + ticket.ticket
            + '/picture/' + student_id + '.JPG')

#REDEFINE
# This function returns a string inserted into student suivi page
def more_on_suivi(student_login, server):
    return ''

#REDEFINE
# To add external information in the 'bilan'
# This function is used by PLUGINS/bilan.py to get external information
def external_bilan(login):
    return "[]"

#REDEFINE
# Returns True to display the UE name if the student is registered for the UE
# but is not in the TOMUSS table (because it is uncreated for example)
def suivi_check_student_lists(login):
    return True

#REDEFINE
# This function returns JavaScript data, for example 'var my_var = "Value";'.
# The data is used by 'generate_home_page_hook' javascript function
# that is called when the home page HTML is generated.
def home_page_js_hook(dummy_server):
    return ''

#REDEFINE
# These functions must NEVER be redefined once TOMUSS is in usage,
# because the date are stored in plain text in files.
# So changing this function will broke every existing files
def date_to_time(date):
    """XXX Convert a french date to seconds"""
    return time.mktime(time.strptime(date, "%d/%m/%Y"))
def tuple_to_date(time_tuple):
    """XXX Convert time tuple to date"""
    return time.strftime('%d/%m/%Y', time_tuple)
        

# And an error message if the password is trivial
bad_password = lambda: """
<div onclick="this.style.display='none';"
     style="border:5px solid black;padding:5px;position:absolute;left:10%;top:10%;right:10%;background:red;color:white;font-size:150%">
""" + __import__('utilities')._("MSG_trivial_password")

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
index_are_computed = os.path.exists(os.path.join('TMP', 'index_are_computed'))

config_debug = ''

def do_nothing(*args):
    pass

###############################################################################
# Terminate configuration
###############################################################################

def terminate():
    """Apply local change to the modules, should be called once
    all the modules are loaded"""

    from . import utilities
    import sys

    if not regtest:
        from .LOCAL import config # Your local configuration goes inside LOCAL

    global url_files, maxage, backup
    
    url_files = server_url + '/files/' + version
    
    if db == 'DBregtest':
        utilities.do_not_display = ()
        maxage = 1

    if not os.path.exists(db):
        utilities.mkpath(db, mode=0700)
    if backup and not os.path.isdir(backup + db):
        utilities.mkpath(backup + db, mode=0700)

    if os.path.exists('tomuss.py'):
        utilities.mkpath('TMP')
        if not os.path.exists(ticket_directory):
            os.mkdir(ticket_directory, 0700)

        if not os.path.isdir(backup + db):
            sys.stderr.write('Backup disabled : directory does not exists\n')
            backup = ''

    from . import inscrits
    inscrits.init()

