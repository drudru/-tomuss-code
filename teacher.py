#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheetl)
#    Copyright (C) 2008-2011 Thierry EXCOFFIER, Universite Claude Bernard
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

if __name__ == "__main__":
    import SCRIPTS.tomuss_init
    
import inscrits
import utilities
import os
import document
import configuration

warn = utilities.warn

#REDEFINE
# Returns the UE list from LDAP or other sources.
# This function is called once per night,
# so it can be long to execute.
# The function result is stored as a Python and JavaScript file
def get_ue_dict():
    if configuration.ldap_server[0] != 'ldap1.domain.org':
        ldap_ues = inscrits.L_batch.get_ldap_ues()
    else:
        ldap_ues = ()
    ues = {}
    for apoge in ldap_ues:
        ues[apoge] = UE(apoge, [], 'UNKNOWN TITLE',
                        [], 0, [], 1, 1, [], 0)
    for i in range(1,10):
        name = "UE%d" % i
        ues[name] = UE(
            name, # UE Name
            ['ue%d.master' % i],# Teacher names
            u'UE%d Title' % i,  # UE title
            [],                 # Departments of UE
            1000+i,             # SPIRAL key for the UE
            ['ue%d.master' % i],# Login of teachers
            1,                  # #students registered
            0,                  # #students registered in EC
            ['ue%d_test@test.org' % i], # Teachers mails
            0,                  # ADE key for the UE
            ) 
    return ues


def create_all_ues_js(ues):
    ff = utilities.AtomicWrite(os.path.join('TMP','all_ues.js'))
    ff.write('all_ues = {\n')
    ue_list = []
    for ue, uev in ues.items():
        print ue
        ue_list.append('%s:%s' % (utilities.js(ue).encode('utf-8'),
                                      uev.js().encode('utf-8')))
    ff.write(',\n'.join(ue_list))
    ff.write('} ;\n')
    ff.close()

    os.system('gzip -9 <TMP/all_ues.js >all_ues.js.gz')
    os.rename('all_ues.js.gz',os.path.join('TMP','all_ues.js.gz'))

all_ues_is_running = False

def all_ues(compute=False):
    warn('start', what='debug')
    try:
        # Load precalculated ues
        # If the file is modified, reload it
        warn('import', what='debug')
        import TMP.xxx_toute_les_ues
        warn('import done', what='debug')
        if compute is False:
            t = os.path.getmtime(os.path.join('TMP', 'xxx_toute_les_ues.py'))
            if not hasattr(TMP.xxx_toute_les_ues,'t') \
                   or TMP.xxx_toute_les_ues.t != t:
                warn('Reload all ues')
                utilities.unload_module('TMP.xxx_toute_les_ues')
                import TMP.xxx_toute_les_ues
                TMP.xxx_toute_les_ues.t = t
                warn('ok')

            return TMP.xxx_toute_les_ues.all
    except ImportError:
        warn("The UE list does not exists, create first one")
        compute = True
    warn('compute', what='debug')

    ues = get_ue_dict()
        
    f = utilities.AtomicWrite(os.path.join('TMP','xxx_toute_les_ues.py'),
                              reduce_ok=False)
    f.write('# -*- coding: utf8 -*-\nfrom teacher import UE\nall = {\n')
    for ue in ues:
        f.write('%s:%s,\n' % (repr(ue), ues[ue]))
    f.write('}\n')
    f.close()

    global all_ues_is_running
    if compute and not all_ues_is_running:
        all_ues_is_running = True
        create_all_ues_js(ues)
        all_ues_is_running = False

    return ues


def login_to_ue(login):
    ues = []    
    for ue in all_ues().values():
        if login in ue.responsables_login():
            ues.append(ue)
    return [(ue.intitule(), ue.name) for ue in ues]
    

class UE(object):
    """Contains all the information about the UE (Unity of Evaluation)."""
    def __init__(self, name, responsable=(), intitule=None, pparcours=(),
                 code=-1,responsable_login=[], nr_students_ue=0,
                 nr_students_ec=0, mails=(), planning={}, credit=-1,
                 old_names=[]):
        """This object may retrieve information from other data sources"""

        # The name is an human lisible code for the UE.
        self.name = name
        self._responsables = responsable
        self._responsables_login = responsable_login
        self._intitule = intitule
        self._parcours = pparcours
        self._code = code
        # Number of students subscribing to the UE
        self._nr_students_ue = nr_students_ue
        # Number of students subscribing to the EC
        self._nr_students_ec = nr_students_ec
        # These mails can't be extracted from responsable logins.
        self._mails = tuple(mails)
        self.len = len(pparcours)
        self.planning = planning
        self.credit = credit
        self.old_names = old_names

    def responsables(self):
        """Returns the NAME list of the manager of the UE."""
        return self._responsables

    def responsables_login(self):
        """Returns the LOGIN list of the manager of the UE."""
        if len(self._responsables_login) == 0:
            self._responsables_login = [responsable_pedagogique_ldap(name)
                                        for name in self._responsables]
            self._responsables_login = [ x.lower()
                                         for x in self._responsables_login
                                         if x != None ]
        return self._responsables_login

    def intitule(self):
        """Returns the title of the UE."""
        return self._intitule

    def parcours(self):
        """Return the list of diploma using this UE."""
        return self._parcours

    def code(self):
        """Returns a database code to access this UE."""
        return self._code

    def mails(self):
        """Returns all the mails of the managers of this UE."""
        return self._mails

    def __cmp__(self, other):
        return cmp(self.len, other.len)

    def __str__(self):
        """Returns the Python code creating this object."""
        return 'UE(%s,%s,%s,%s,%d,%s,%d,%d,%s,%s,%d,%s)' % (
            repr(self.name),
            repr(self._responsables),
            repr(self._intitule),
            repr(self._parcours),
            self._code,
            repr(self.responsables_login()),
            self._nr_students_ue, self._nr_students_ec,
            repr(self._mails),
            self.planning,
            self.credit,
            self.old_names,
            )

    def js(self, read_tt=True):
        """Returns the code to create the JavaScript object for this one.
        If read_tt is a list, then TT students are stored in the list.
        """
        if read_tt is not False:
            table = document.table(utilities.university_year(),
                                   'Dossiers', 'tt')
            tt = 0
            ue = document.table(configuration.year_semester[0],
                                configuration.year_semester[1],
                                'UE-' + self.name,
                                create=False)
            nr_students = 0
            if ue:
                for student in ue.the_keys():
                    if len(student) < 3: # Garbage student id (bad user input)
                        continue
                    if utilities.the_login(student) in table.the_keys():
                        tt += 1
                        if isinstance(read_tt, list):
                            read_tt.append(utilities.the_login(student))
                if (self._intitule) is None or len(self._intitule) <= 1:
                    # Too small UE name : take the comment as title
                    self._intitule = ue.comment
                nr_students = len(ue.the_keys())
                ue.unload()

            if nr_students <= 10: # Problem ?
                for student in inscrits.L_batch.students('UE-' + self.name):
                    if utilities.the_login(student[0]) in table.the_keys():
                        tt += 1
                        if isinstance(read_tt, list):
                            read_tt.append(utilities.the_login(student[0]))
        else:
            tt = 0
        

        return 'UE(%s,[%s],%s,[%s],%d,[%s],%d,%d,%s,%d,%d,%s)' % (
            utilities.js(self.name),
            ','.join([utilities.js(r) for r in self._responsables]),
            utilities.js(self._intitule),
            ','.join([utilities.js(p) for p in self._parcours]),
            self._code,
            ','.join([utilities.js(r) for r in self._responsables_login]),
            self._nr_students_ue, self._nr_students_ec, 
            self.planning,
            tt,
            self.credit,
            utilities.js(self.old_names),
            )

    def short_parcours(self):
        """Returns the UFR managing this UE."""
        return self.name[0:3]

def other_mails(code):
    try:
        import TMP.xxx_mails
    except ImportError:
        return []
    try:
        return TMP.xxx_mails.mails[code]
    except KeyError:
        return []

def responsable_pedagogique_ldap(name):
    surname = []
    firstname = []
    for x in name.split(' '):
        if x.upper() == x:
            surname.append(x)
        else:
            firstname.append(x)
    return inscrits.L_batch.firstname_and_surname_to_login(' '.join(firstname),
                                                           ' '.join(surname))

def responsables_pedagogiques_ldap(ue):
    return all_ues()[ue].responsable_login()

def parcours_names(les_ues):
    names = {}
    for ue in les_ues.values():
        for q in ue.parcours():
            names[q] = True
    return names.keys()

def ues_for_parcour(les_ues, p):
    t = []
    for ue in les_ues.values():
        if p in ue.parcours():
            t.append(ue)
    return t

if __name__ == "__main__":
    document.table(0, 'Dossiers', 'config_table', None, None)
    print UE('BIO3082L').js()




