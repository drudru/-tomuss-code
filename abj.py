#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2008,2009 Thierry EXCOFFIER, Universite Claude Bernard
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

import utilities
import os
import configuration
import inscrits
import time
import document
import teacher
import cgi

js = utilities.js

abjs = None

def a_date(date):
    if date[-1] not in "MA":
        raise ValueError("Bad date:" + date)
    d = [int(v) for v in date[:-1].split('/')]
    if len(d) != 3:
        raise ValueError("Bad date:" + date)
    if (d[0] >= 1 and d[0] <= 31 and
        d[1] >= 1 and d[1] <= 12 and
        d[2] > 2000):
        return '%d/%d/%d%s' % (d[0], d[1], d[2], date[-1])
    raise ValueError("Bad date:" + date)

class Abj(object):
    """ABJ for a given student"""

    def __init__(self, login):
        self.login = inscrits.login_to_student_id(login)
        self.abjs = []
        self.da = []

    def add(self, fro, to, author, comment=''):
        if (fro, to) not in self.abjs:
            self.abjs.append((fro, to, author, comment))
            return True
        return False

    def add_da(self, ue, date, author, comment=''):
        if len(self.da) == 0 or ue not in zip(*self.da)[0]:
            self.da.append((ue, date, author, comment))
            return True
        return False

    def rem(self, fro, to):
        """Bugged function needed for compatibility, use rem2"""
        self.abjs = [abj
                     for abj in self.abjs
                     if abj[0] != fro and abj[1] != to]

    def rem2(self, fro, to):
        self.abjs = [abj
                     for abj in self.abjs
                     if abj[0] != fro or abj[1] != to]

    def rem_da(self, ue):
        self.da = [da for da in self.da if da[0] != ue]

    def js(self):
        s = []
        for fro, to, author, comment in self.abjs:
            s.append('[%s,%s,%s,%s]' % (repr(fro), repr(to), repr(author),
                                        js(comment)))
        return '[' + ','.join(s) + ']'

    def js_da(self):
        s = []
        for ue, date, author, comment in self.da:
            s.append('[%s,%s,%s,%s]' % (repr(ue), repr(date), repr(author),
                                        js(comment)))
        return '[' + ','.join(s) + ']'

    def ues_without_da(self):
        ues = inscrits.ues_of_a_student_short(self.login)
        if len(self.da) == 0:
            return ues
        da = zip(*self.da)[0]
        return [ue for ue in ues if ue not in da]


    def html(self):
        """This function is here because it does not send
        restricted information to students.
        """

        s = []
        if self.abjs:
            s.append('<TABLE class="display_abjs colored">')
            s.append('<TR><TH>ABJ du</TH><TH>Au</TH><TH>Commentaire</TH></TR>')
            for abj in self.abjs: 
                s.append('<TR><TD>' + abj[0] + '</TD><TD>' + abj[1] +
                         '</TD><TD>' + cgi.escape(abj[3]) + '</TD></TR>')
            s.append('</TABLE>')

        if self.da:
            s.append('<TABLE class="display_da colored">')
            s.append('<TR><TH>Dispense pour l\'UE</TH><TH>À partir du</TH><TH>Commentaire</TH></TR>')
            for da in self.da: 
                s.append('<TR><TD>' + da[0] + '</TD><TD>' + da[1] +
                          '</TD><TD>' + cgi.escape(da[3]) + '</TD></TR>')
            s.append('</TABLE>')

        return '\n'.join(s)
 

class Abjs(object):
    """ABJ for a set of students"""

    abjs = {}

    def __init__(self, year, semester):
        self.year = year
        self.semester = semester
        Abjs.abjs[(year, semester)] = self

        self.filename = os.path.join(configuration.db,
                                     'Y'+str(year), 'S'+semester)

        utilities.mkpath(self.filename)
        if configuration.backup:
            utilities.mkpath(configuration.backup + self.filename)
        self.filename = os.path.join(self.filename, 'abjs.py')
        self.module = self.filename.replace(os.path.sep,'.').replace('.py','')
        if not os.path.exists(self.filename):
            utilities.write_file(self.filename, "from abj import add,rem,rem2,add_da,rem_da\n")

        if configuration.backup:
            if not os.path.exists(configuration.backup + self.filename):
                utilities.write_file(configuration.backup + self.filename,
                                     utilities.read_file(self.filename))

        self.load_module()

    def getmtime(self):
        return os.path.getmtime(self.filename)
    
    def update(self):
        """Reload the file if another process modified it"""
        if self.getmtime() <= self.mtime:
            return
        if time.time() - self.last_update < 60*60:
            return
        self.load_module()
        
    def load_module(self):
        self.last_update = time.time()
        self.students = {}
        self.mtime = self.getmtime()
        utilities.unload_module(self.module)
        global abjs
        abjs = self
        try:
            __import__(self.module)
        except ImportError:
            pass
        abjs = None

    def add(self, login, fro, to, user_name='', date='', comment=''):
        login = inscrits.login_to_student_id(login)
        if abjs == None:
            fro = a_date(fro)
            to = a_date(to)
        if login not in self.students:
            self.students[login] = Abj(login)
        if self.students[login].add(fro, to, user_name,comment) \
               and abjs == None:
            date = time.strftime('%Y%m%d%H%M%S')
            s =  'add(%s,%s,%s,%s,%s,%s)\n' % (
                repr(login), repr(fro), repr(to),
                repr(user_name), repr(date), repr(comment)
                                            )
            utilities.append_file(self.filename, s)
            if configuration.backup:
                utilities.append_file(configuration.backup + self.filename, s)

            self.mtime = self.getmtime()

        
    def add_da(self, login, ue, date=None, user_name='', fdate='', comment=''):
        login = inscrits.login_to_student_id(login)
        if login not in self.students:
            self.students[login] = Abj(login)
        if self.students[login].add_da(ue, date, user_name, comment):
            if abjs == None:
                # date = time.strftime('%d/%m/%Y')
                fdate = time.strftime('%Y%m%d%H%M%S')
                s =  'add_da(%s,%s,%s,%s,%s,%s)\n' % (repr(login), repr(ue),
                                                      repr(date),
                                                      repr(user_name),
                                                      repr(fdate),
                                                      repr(comment),
                                                   )
                utilities.append_file(self.filename, s)
                if configuration.backup:
                    utilities.append_file(configuration.backup +
                                          self.filename, s)
                self.mtime = self.getmtime()
        
    def rem(self, login, fro, to, user_name='', date=''):
        """Bugged function needed for compatibility, use rem2"""
        login = inscrits.login_to_student_id(login)
        if abjs == None:
            fro = a_date(fro)
            to = a_date(to)
            date = time.strftime('%Y%m%d%H%M%S')
            if login not in self.students:
                return
            s =  'rem(%s,%s,%s,%s,%s)\n' % (repr(login), repr(fro), repr(to),
                                            repr(user_name), repr(date))
            utilities.append_file(self.filename, s)
            if configuration.backup:
                utilities.append_file(configuration.backup + self.filename, s)
            self.mtime = self.getmtime()
        self.students[login].rem(fro, to)

    def rem2(self, login, fro, to, user_name='', date=''):
        login = inscrits.login_to_student_id(login)
        if abjs == None:
            fro = a_date(fro)
            to = a_date(to)
            date = time.strftime('%Y%m%d%H%M%S')
            if login not in self.students:
                return
            s =  'rem2(%s,%s,%s,%s,%s)\n' % (repr(login), repr(fro), repr(to),
                                            repr(user_name), repr(date))
            utilities.append_file(self.filename, s)
            if configuration.backup:
                utilities.append_file(configuration.backup + self.filename, s)
            self.mtime = self.getmtime()
        self.students[login].rem2(fro, to)

    def rem_da(self, login, ue, user_name='', date=''):
        login = inscrits.login_to_student_id(login)
        if abjs == None:
            date = time.strftime('%Y%m%d%H%M%S')
            s =  'rem_da(%s,%s,%s,%s)\n' % (repr(login), repr(ue),
                                            repr(user_name), repr(date))
            utilities.append_file(self.filename, s)
            if configuration.backup:
                utilities.append_file(configuration.backup + self.filename, s)
            self.mtime = self.getmtime()
        if login not in self.students:
            self.students[login] = Abj(login)
        self.students[login].rem_da(ue)

 
def add(login, fro, to, user_name='', date='', comment=''):
    abjs.add(login, fro, to, user_name, date, comment)

def rem(login, fro, to, user_name='', date=''):
    """Bugged function needed for compatibility, use rem2"""
    abjs.rem(login, fro, to, user_name, date)

def rem2(login, fro, to, user_name='', date=''):
    abjs.rem2(login, fro, to, user_name, date)

def add_da(login, ue, date, user_name='', fdate='', comment=''):
    abjs.add_da(login, ue, date, user_name, fdate, comment)

def rem_da(login, ue, user_name='', date=''):
    abjs.rem_da(login, ue, user_name, date)

@utilities.add_a_lock # Protect the global variable 'abjs'
def get_abjs(year, semester):
    if semester == 'Printemps' \
           and year > configuration.abj_per_semester_before \
           and not configuration.abj_per_semester:
        # Take ABJ from first semester
        semester = 'Automne'
        year -= 1
    year = str(year)
    try:
        return Abjs.abjs[(year, semester)]
    except KeyError:
        return Abjs(year, semester)

def add_abjs(year, semester, ticket, student, fro, to, comment):
    get_abjs(year, semester).add(student, fro, to, ticket.user_name,
                                 comment=comment)

def rem_abjs(year, semester, ticket, student, fro, to):
    """Do not use the bugged function"""
    get_abjs(year, semester).rem2(student, fro, to, ticket.user_name)

def add_abjs_da(year, semester, ticket, student, ue, date, comment):
    get_abjs(year, semester).add_da(student, ue, date, ticket.user_name,
                                    comment=comment)

def rem_abjs_da(year, semester, ticket, student, ue):
    get_abjs(year, semester).rem_da(student, ue, ticket.user_name)

def html_abjs(year, semester, student, read_only=False):
    a = get_abjs(year, semester)
    if read_only:
        a.update()
    try:
        return unicode(a.students[inscrits.login_to_student_id(student)].html(),'utf-8')
    except KeyError:
        return u''

def a_student(f, year, semester, ticket, student, do_close=True):
    """Send student abj with the data to the navigator.    
    """
    student = inscrits.login_to_student_id(student)
    aabjs = get_abjs(year, semester)
    s = '<SCRIPT>'
    s += """set_html(
         '<IMG SRC="'+student_picture_url('%s')+'">');""" \
    % student

    s += "append_html('<A HREF=\"%s/%s\">%s</A>, %s<br>');" % (
        configuration.suivi.url(year,semester,ticket.ticket),
        student.replace("'","\\'"),
        ' '.join(inscrits.firstname_and_surname(student)).replace("'","\\'"),
        ', '.join(inscrits.portail(student)).replace("'","\\'")
        )

    if student in aabjs.students:
        s += "display_abjs(%s);" % unicode(aabjs.students[student].js(),'utf8')
        s += "display_da(%s);" % unicode(aabjs.students[student].js_da(),'utf8')
        t = aabjs.students[student].ues_without_da()
    else:
        s += "display_abjs([]);"
        s += "display_da([]);"
        t = inscrits.ues_of_a_student_short(student)

    t.sort()
    s += "ues_without_da(%s);" % js(t)
    s += '</SCRIPT>'
    f.write(s.encode('utf8'))
    if do_close:
        f.close()
    else:
        f.flush()


def translate_tt(v):
    if v.strip() == '1' or v.lower() == 'o':
        return '1/3'
    else:
        return v
        

def tierstemps(student_id, aall=False, table=None):
    if table == None:
        # Get TT for current year
        table = document.table(utilities.university_year(), 'Dossiers', 'tt')
    for line in table.get_lines(student_id):
        s = ""
        if aall is False:
            try:
                if line[8].value:
                    if time.time() \
                           < time.mktime(time.strptime(line[8].value,"%d/%m/%Y")):
                        continue
                if line[9].value:
                    if time.time() \
                           > time.mktime(time.strptime(line[9].value,"%d/%m/%Y")):
                        continue
            except ValueError:
                utilities.send_backtrace(repr(line))
        else:
            if line[8].value:
                s += u'À partir du ' + line[8].value + '\n'
            if line[9].value:
                s += u'Jusqu\'au ' + line[9].value + '\n'
            
        if line[3].value:
            s += u"Temps supplémentaire pour les examens écrits : %s\n" % translate_tt(line[3].value)
        if line[4].value:
            s += u"Temps supplémentaire pour les examens oraux : %s\n" % translate_tt(line[4].value)
        if line[5].value:
            s += u"Temps supplémentaire pour les examens de TP : %s\n" % translate_tt(line[5].value)
        if line[6].value == 'OUI':
            s += u"Dispose d'une secrétaire particulière\n"
        if line[7].value == 'OUI':
            s += u"Dispose d'une salle particulière\n"
        if line[10].value:
            s += unicode(line[10].value, 'utf-8') + '\n'
        return s
    return ''

def alpha(f, year, semester):
    import csv
    aabjs = get_abjs(year, semester)
    w = csv.writer(f, delimiter=';', quoting=csv.QUOTE_ALL)
    for student in aabjs.students.values():
        fn, sn = inscrits.firstname_and_surname(student.login)
        fn = fn.encode('latin1')
        sn = sn.encode('latin1')
        for fro, to, author,comment in student.abjs:
            w.writerow( (fn, sn, student.login, 'ABJ', fro, to, comment) )
        for ue, date, author,comment in student.da:
            w.writerow( (fn, sn, student.login, 'DAS', ue, date, comment) )
    f.close()


def alpha_html(f, year, semester, ue_name_endswith=None, author=None):
    global L
    if L is None:
        L = type(inscrits.L)('LDAP3')

    aabjs = get_abjs(year, semester)
    f.write('''<html>
<head>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
</head>
<body>
<div id="x">Veuillez patienter, la page se charge.</div>
<table style="table-layout: fixed" border><tbody id="t">
''')
    format = '<tr>'  +  '<td>%s</td>' * 7  +  '</tr>\n'
    f.write(format%('Prénom',
                    'Nom <span class="x">(<a href="javascript:sort(cmp_name)">Trier</a>)</span>',
                    'N° <span class="x">(<a href="javascript:sort(cmp_id)">Trier</a>)</span>',
                    'Quoi',
                    'Date début <span class="x">(<a href="javascript:sort(cmp_ue)">Trier</a>)</span>',
                    'Date fin ou UE <span class="x">(<a href="javascript:sort(cmp_ue2)">Trier</a>)</span>',
                    'Commentaire <span class="x">(<a href="javascript:sort(cmp_comment)">Trier</a>)</span>'))
    for student in aabjs.students.values():

        if ue_name_endswith:
            for ue in L.ues_of_a_student_short(student.login):
                if ue[-1] == ue_name_endswith:
                    break
            else:
                # No UE ended by the required character
                continue

        fn, sn = inscrits.firstname_and_surname(student.login)
        fn = fn.encode('utf8')
        sn = sn.encode('utf8')
        for fro, to, author2, comment in student.abjs:
            if author is None or author == author2:
                f.write( format % (fn, sn, student.login, 'ABJ', fro, to,
                                   cgi.escape(comment)) )
        for ue, date, author2, comment in student.da:
            if author is None or author == author2:
                f.write( format % (fn, sn, student.login, 'DAS', date, ue,
                                   cgi.escape(comment)) )
    f.write('</tbody></table>')
    f.write(utilities.read_file(os.path.join('FILES', 'abj_recap.html')))
    f.close()


def underline(txt, char='='):
    return '\n' + char * len(txt) + '\n' + txt + '\n' + char * len(txt) + '\n'

def nice_date(d):
    return d.replace('M',' matin').replace('A', u' après-midi')

def get_table_tt(year, semester):
    if semester == 'Printemps':
        return document.table(int(year)-1, 'Dossiers', 'tt')
    else:
        return document.table(year, 'Dossiers', 'tt')

L = None

def feedback(browser, letter, nr_letters):
    if browser:
        nr_letters += 1
        if nr_letters % 80 == 0:
            letter += '\n'
        browser.write(letter)
        browser.flush()
        return nr_letters

#REDEFINE
# When a student has an ABJ it may be outside of UE schedule.
# The function returns the ABJs without ABJ outside of UE planning.
def prune_abjs(abjs, group, sequence, ue):
    return abjs

def do_prune(abjs, first_day, last_day, group, sequence, ue):
        abjs_pruned = []
        for abjj in abjs:
            try:
                ti = time.mktime(time.strptime(abjj[0][:-1], "%d/%m/%Y"))
            except OverflowError:
                ti = 0
            if ti >= last_day:
                continue
            try:
                ti = time.mktime(time.strptime(abjj[1][:-1], "%d/%m/%Y"))
            except OverflowError:
                ti = 8000000000
            if ti < first_day:
                continue
            abjs_pruned.append(abjj)

        return prune_abjs(abjs_pruned, group, sequence, ue)

def ue_mails_and_comments(ue):
    global L
    if L is None:
        L = type(inscrits.L)('LDAP3')

    mails = []
    t = []
    the_ue = teacher.all_ues().get(ue[3:], None)
    if the_ue:
        for teacher_name in the_ue.responsables():
            t.append("   * " + teacher_name + ' : ')
            teacher_login = teacher.responsable_pedagogique_ldap(teacher_name)
            if teacher_login is None:
                t.append('ENSEIGNANT INCONNU !')
            else:
                mail = L.mail(teacher_login)
                if mail == None:
                    t.append('MAIL INCONNU !')
                else:
                    mails.append(mail.lower())                
                    t.append(mail)
            t.append('\n')

    # Add other mails
            
    other_mails = []
    for om in teacher.other_mails(ue[3:]):
        om = om.lower().encode('utf-8')
        if om not in mails:
            other_mails.append(om)

    if other_mails:
        t.append("   * Adresse venant du fichier des UE ouvertes : " +
                 ', '.join(other_mails) + '\n')
        mails += other_mails

    # Add other mails from SPIRAL

    if the_ue:
        other_mails = []
        for om in the_ue.mails():
            om = om.lower()
            if om not in mails:
                other_mails.append(unicode(om, 'utf-8'))

        if other_mails:
            t.append("   * Adresses venant de SPIRAL : " +
                     ', '.join(other_mails) + '\n')
            mails += other_mails

    if len(mails) == 0:
        t.append('AUCUN RESPONSABLE CONNU\n')

    return mails, t

def ue_resume(ue, year, semester, browser=None):
    global L
    if L is None:
        L = type(inscrits.L)('LDAP3')
    nr_letters = 0

    current_year =   (year, semester) == configuration.year_semester
    
    aabjs = get_abjs(year, semester)
    table_tt = get_table_tt(year, semester)
    #
    # The UE title
    #
    the_ue = teacher.all_ues().get(ue[3:], None)

    if browser:
        t = []
        browser.write('Génération de la page :\n')
    else:
        t = [u"""Mesdames, Messieurs,

Voici la liste des étudiants en dispense d'assiduité, en tiers temps
et ceux qui ont justifié leurs absences.
Ces informations sont disponibles sur http://tomuss.univ-lyon1.fr/
Sur ce site il est possible d'afficher les ABJ pour une date donnée.

Cordialement.

"""]

    if not the_ue:
        t.append(underline(ue + u' : Titre non renseigné dans SPIRAL'))
    else:
        t.append(underline(ue + ' : ' + the_ue.intitule()))

    t.append(u'\nPour accéder à la version à jour de ces informations suivez le lien :\n\n')
    t.append('    %s/%s/%s/%s/resume\n' % (
        configuration.server_url, year, semester, ue))
    #
    # The UE managers
    #
    t.append(underline("Responsables de l'UE", char='-'))
    mails, tt = ue_mails_and_comments(ue)
    t += tt


    the_students = []
    first_day = 0
    last_day = 8000000000
    if current_year:
        for infos in L.students(ue):
            if infos[0] not in the_students:
                the_students.append((infos[0],infos[4],infos[5]))

    if len(the_students) == 0:        
        # Fast process but may be incomplete
        table = document.table(year, semester, ue, create=False)
        if table:
            the_students = [(line[0].value, line[3].value, line[4].value)
                            for line in table.lines.values()
                            if line[0].value]
            first_day = table.first_day
            last_day = table.last_day + 86400 # End of last day
            table.unload()
            table = None
    if first_day == 0:
        if semester == 'Automne':
            first_day = time.mktime( (year, 8, 15   ,0,0,0,0,0,0) )
            last_day = time.mktime( (year+1, 1, 31  ,0,0,0,0,0,0) )
        elif semester == 'Printemps':
            first_day = time.mktime( (year, 1, 31  ,0,0,0,0,0,0) )
            last_day = time.mktime( (year, 7, 31  ,0,0,0,0,0,0) )
    utilities.warn('first_day=%s %s' % (first_day, last_day))
    #
    # The ABJ
    #
    first = True
    tt = []
    for student_login, group, sequence in the_students:
        student = aabjs.students.get(inscrits.login_to_student_id(student_login))
        if not student:
            continue
        
        abjs_pruned = do_prune(student.abjs, first_day, last_day,
                               group, sequence, ue) 

        if len(abjs_pruned) == 0:
            continue
        nr_letters = feedback(browser, 'A', nr_letters)
        if first:
            first = False
            t.append(underline("Liste des ABJ", char='-'))
        fs = L.firstname_and_surname(student.login)
        s = '   * '+student.login+' '+fs[1].upper() + ' ' +fs[0].title() + '\n'
        for abj in abjs_pruned:
            if abj[0] == abj[1]:
                x = '      - Le ' + nice_date(abj[0])
            elif abj[0][:-1] == abj[1][:-1]:
                x = '      - Le ' + abj[0][:-1]
            else:
                x = "      - Du " + nice_date(abj[0]) + ' au ' \
                  + nice_date(abj[1]) + ' inclus'
            if abj[3]:
                x += ' (' + unicode(abj[3],'utf8') + ')'
            
            s += x + '\n'
        tt.append( (utilities.flat(fs[1]).lower(),
                    utilities.flat(fs[0]).lower(),
                    s) )
    if tt:
        tt.sort()
        t += zip(*tt)[2]
    #
    # The DA
    #
    first = True
    tt = []
    for student_login, group, sequence in the_students:
        student = aabjs.students.get(inscrits.login_to_student_id(student_login))
        if not student:
            continue
        dates = [d for d in student.da if d[0] == ue]
        if dates:
            nr_letters = feedback(browser, 'D', nr_letters)
            if first:
                first = False
                t.append(underline(u"Liste des étudiants avec une DA",
                                   char='-'))
            fs = L.firstname_and_surname(student_login)
            s = ('   * ' + student_login + ' '
                 + fs[1].upper() + ' ' + fs[0].title()
                 + u' à partir du ' + dates[0][1])
            if dates[0][3]:
                s += ' (' + dates[0][3] + ')'
            s += '\n'
            
            tt.append((utilities.flat(fs[1]).lower(),
                       utilities.flat(fs[0]).lower(),
                       s))
    if tt:
        tt.sort()
        t += zip(*tt)[2]
    #
    # The TT
    #
    first = True
    tt_logins = list(table_tt.logins())
    tt = []

    for student_login, group, sequence in the_students:
        if not student_login in tt_logins:
            continue
        infos = tierstemps(student_login, True, table = table_tt)
        nr_letters = feedback(browser, 'T', nr_letters)
        if first:
            first = False
            t.append(underline(u"Liste des étudiants avec un tiers temps",
                               char='-'))
        fs = L.firstname_and_surname(student_login)
        s = '   * '+student_login+' ' + fs[1].upper()+' '+fs[0].title() + '\n'
        for line in infos.split('\n')[:-1]:
            s += '      - ' + line + '\n'
        tt.append((utilities.flat(fs[1]).lower(),
                   utilities.flat(fs[0]).lower(),
                   s))

    if tt:
        tt.sort()
        t += zip(*tt)[2]


    return t, mails

to_send_ok = [] # (Recipent, Title, message) list

def list_mail(f, year, semester, only_licence=True):
    global L
    if L is None:
        L = type(inscrits.L)('LDAP3')

    to_send = []
    sender = configuration.abj_sender
    f.write("Les messages seront envoyés au nom de " + sender)
    f.write('<pre>')

    aabjs = get_abjs(year, semester)
    ues = {}
    for student in aabjs.students.values():
        for da in student.da:
            ues[da[0]] = True
        if student.abjs:
            for ue in L.ues_of_a_student_short(student.login):
                ues[ue] = True

    table_tt = get_table_tt(year, semester)
    tt_logins = list(table_tt.logins())
    for student_login in tt_logins:
        for ue in L.ues_of_a_student_short(student_login):
            ues[ue] = True

    if only_licence:
        ues = [ue for ue in ues if ue[-1] == 'L']

    for ue in ues:
        lines, mails = ue_resume(ue, year, semester)
        f.write(''.join(lines).encode('utf8'))
        if mails:
            to_send.append( (mails,
                             'ABJ + DA + TT pour l\'UE ' + ue,
                             ''.join(lines).encode('latin1') ) )

    global to_send_ok
    to_send_ok = to_send
    
    f.write('</pre><h1>SUIVEZ LE LIEN POUR ENVOYER LES %d MESSAGES AUX ENSEIGNANTS</a></h1>ATTENTION une fois que vous cliquez sur le lien à la fin de cette ligne, les messages seront envoyés : <a href="send_mail">Envoyer!</a>' % len(to_send))
    f.close()


xxx = [
    (['exco@bat710.univ-lyon1.fr', 'thierry.excoffier@bat710.univ-lyon1.fr'],
     'UE x',
     'blabla'),
    (['exco@liris.univ-lyon1.fr', u'excé@www710.univ-lyon1.fr'],
     'UE y',
     'blaBLA'),
    (['exco@bat710.univ-lyon1.fr', 'thierry.excoffier@bat710.univ-lyon1.fr'],
     'UE z',
     'blabla'),
    ]

def send_mail(f):
    for recipients, title, text in to_send_ok:
        try:
            error = utilities.send_mail(recipients,
                                        title,
                                        text,
                                        configuration.abj_sender)
            if error:
                f.write("<pre>" + error + "</pre>")
            else:
                f.write("<p>" + repr(recipients) + ' : message envoyé')
        except UnicodeEncodeError:
            f.write("<pre>BUG dans abj.send_mail</pre>")
