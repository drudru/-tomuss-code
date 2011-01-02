#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
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

"""Management of the justification for missing courses."""

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
    """Check if the date (DD/MM/YYYY/[MA]) seems fine"""
    if date[-1] not in "MA":
        raise ValueError("Bad date:" + date)
    int_list = [int(v) for v in date[:-1].split('/')]
    if len(int_list) != 3:
        raise ValueError("Bad date:" + date)
    if (int_list[0] >= 1 and int_list[0] <= 31 and
        int_list[1] >= 1 and int_list[1] <= 12 and
        int_list[2] > 2000):
        return '%d/%d/%d%s' % (int_list[0], int_list[1], int_list[2], date[-1])
    raise ValueError("Bad date:" + date)

class Abj(object):
    """ABJ for a given student"""

    def __init__(self, login):
        self.login = inscrits.login_to_student_id(login)
        self.abjs = []
        self.da = []

    def add(self, from_date, to_date, author, comment=''):
        """Add a new ABJ"""
        if (from_date, to_date) not in self.abjs:
            self.abjs.append((from_date, to_date, author, comment))
            return True
        return False

    def add_da(self, ue_code, date, author, comment=''):
        """Add a new DA"""
        if len(self.da) == 0 or ue_code not in zip(*self.da)[0]:
            self.da.append((ue_code, date, author, comment))
            return True
        return False

    def rem(self, from_date, to_date):
        """Bugged function needed for compatibility, use rem2"""
        self.abjs = [abj
                     for abj in self.abjs
                     if abj[0] != from_date and abj[1] != to_date]

    def rem2(self, from_date, to_date):
        """Remove an existing ABJ"""
        self.abjs = [abj
                     for abj in self.abjs
                     if abj[0] != from_date or abj[1] != to_date]

    def rem_da(self, ue_code):
        """Remove an existing DA"""
        self.da = [da for da in self.da if da[0] != ue_code]

    def js(self):
        """All the student ABJ data as a JavaScript fragment"""
        abj_list = []
        for from_date, to_date, author, comment in self.abjs:
            abj_list.append('[%s,%s,%s,%s]' % (repr(from_date), repr(to_date),
                                               repr(author), js(comment)))
        return '[' + ','.join(abj_list) + ']'

    def js_da(self):
        """All the student DA data as a JavaScript fragment"""
        da_list = []
        for ue_code, date, author, comment in self.da:
            da_list.append('[%s,%s,%s,%s]' % (repr(ue_code), repr(date),
                                              repr(author), js(comment)))
        return '[' + ','.join(da_list) + ']'

    def ues_without_da(self):
        """List of the UE_CODE registered by the student, but without DA"""
        ues = inscrits.ues_of_a_student_short(self.login)
        if len(self.da) == 0:
            return ues
        da = zip(*self.da)[0]
        return [ue_code for ue_code in ues if ue_code not in da]

    def html(self):
        """This function is here because it does not send
        restricted information to_date students.
        """
        content = []
        if self.abjs:
            content.append('''
<h2>Informations concernant les absences justifiées</h2>
<TABLE class="display_abjs colored">
<TR><TH>ABJ du</TH><TH>Au</TH><TH>Commentaire</TH></TR>''')
            for abj in self.abjs: 
                content.append('<TR><TD>' + abj[0] + '</TD><TD>' + abj[1] +
                               '</TD><TD>' + cgi.escape(abj[3]) + '</TD></TR>')
            content.append('</TABLE>')

        if self.da:
            content.append("""
<h2>Informations concernant les dispenses d'assiduité</h2>
<TABLE class="display_da colored">
<TR><TH>Dispense pour l'UE</TH>""")
            content.append('<TH>À partir du</TH><TH>Commentaire</TH></TR>')
            for a_da in self.da: 
                content.append('<TR><TD>' + a_da[0] + '</TD><TD>' + a_da[1] +
                               '</TD><TD>'+ cgi.escape(a_da[3]) + '</TD></TR>')
            content.append('</TABLE>')

        return '\n'.join(content)
 

class Abjs(object):
    """ABJ for a set of students"""

    abjs = {}

    def __init__(self, year, semester):
        self.year = year
        self.semester = semester
        Abjs.abjs[(year, semester)] = self

        self.filename = os.path.join(configuration.db,
                                     'Y'+str(year), 'S'+semester)

        utilities.mkpath_safe(self.filename)
        self.filename = os.path.join(self.filename, 'abjs.py')
        self.module = self.filename.replace(os.path.sep,'.').replace('.py','')
        if not os.path.exists(self.filename):
            utilities.append_file_safe(
                self.filename, "from abj import add,rem,rem2,add_da,rem_da\n")

        self.load_module()

    def getmtime(self):
        """Date of the database file modification"""
        return os.path.getmtime(self.filename)
    
    def update(self):
        """Reload the file if another process modified it"""
        if self.getmtime() <= self.mtime:
            return
        if time.time() - self.last_update < configuration.maximum_out_of_date:
            return
        self.load_module()
        
    def load_module(self):
        """Load all the ABJ and DA data"""
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

    def add(self, login, from_date, to_date, user_name='',
            date='', comment=''):
        """Check the ABJ parameters and add the information to the database"""
        login = inscrits.login_to_student_id(login)
        if abjs == None:
            from_date = a_date(from_date)
            to_date = a_date(to_date)
        if login not in self.students:
            self.students[login] = Abj(login)
        if self.students[login].add(from_date, to_date, user_name, comment) \
               and abjs == None:
            date = time.strftime('%Y%m%d%H%M%S')
            to_append = 'add(%s,%s,%s,%s,%s,%s)\n' % (
                repr(login), repr(from_date), repr(to_date),
                repr(user_name), repr(date), repr(comment)
                                            )
            utilities.append_file_safe(self.filename, to_append)

            self.mtime = self.getmtime()

        
    def add_da(self, login, ue_code, date=None, user_name='', fdate='',
               comment=''):
        """Check the DA parameters and add the information to the database"""
        login = inscrits.login_to_student_id(login)
        if login not in self.students:
            self.students[login] = Abj(login)
        if self.students[login].add_da(ue_code, date, user_name, comment):
            if abjs == None:
                # date = time.strftime('%d/%m/%Y')
                fdate = time.strftime('%Y%m%d%H%M%S')
                to_append = 'add_da(%s,%s,%s,%s,%s,%s)\n' % (
                    repr(login), repr(ue_code), repr(date), repr(user_name),
                    repr(fdate), repr(comment))
                utilities.append_file_safe(self.filename, to_append)
                self.mtime = self.getmtime()
        
    def rem(self, login, from_date, to_date, user_name='', date=''):
        """Bugged function needed for compatibility, use rem2"""
        login = inscrits.login_to_student_id(login)
        if abjs == None:
            from_date = a_date(from_date)
            to_date = a_date(to_date)
            date = time.strftime('%Y%m%d%H%M%S')
            if login not in self.students:
                return
            to_append =  'rem(%s,%s,%s,%s,%s)\n' % (
                repr(login), repr(from_date), repr(to_date),
                repr(user_name), repr(date))
            utilities.append_file_safe(self.filename, to_append)
            self.mtime = self.getmtime()
        self.students[login].rem(from_date, to_date)

    def rem2(self, login, from_date, to_date, user_name='', date=''):
        """Remove the ABJ from the database"""
        login = inscrits.login_to_student_id(login)
        if abjs == None:
            from_date = a_date(from_date)
            to_date = a_date(to_date)
            date = time.strftime('%Y%m%d%H%M%S')
            if login not in self.students:
                return
            to_append = 'rem2(%s,%s,%s,%s,%s)\n' % (
                repr(login), repr(from_date), repr(to_date),
                repr(user_name), repr(date))
            utilities.append_file_safe(self.filename, to_append)
            self.mtime = self.getmtime()
        self.students[login].rem2(from_date, to_date)

    def rem_da(self, login, ue_code, user_name='', date=''):
        """Remove the DA from the database"""
        login = inscrits.login_to_student_id(login)
        if abjs == None:
            date = time.strftime('%Y%m%d%H%M%S')
            to_append = 'rem_da(%s,%s,%s,%s)\n' % (repr(login), repr(ue_code),
                                                   repr(user_name), repr(date))
            utilities.append_file_safe(self.filename, to_append)
            self.mtime = self.getmtime()
        if login not in self.students:
            self.students[login] = Abj(login)
        self.students[login].rem_da(ue_code)

 
def add(login, from_date, to_date, user_name='', date='', comment=''):
    """Used when importing the database"""
    abjs.add(login, from_date, to_date, user_name, date, comment)

def rem(login, from_date, to_date, user_name='', date=''):
    """Bugged function needed for compatibility, use rem2"""
    abjs.rem(login, from_date, to_date, user_name, date)

def rem2(login, from_date, to_date, user_name='', date=''):
    """Used when importing the database"""
    abjs.rem2(login, from_date, to_date, user_name, date)

def add_da(login, ue_code, date, user_name='', fdate='', comment=''):
    """Used when importing the database"""
    abjs.add_da(login, ue_code, date, user_name, fdate, comment)

def rem_da(login, ue_code, user_name='', date=''):
    """Used when importing the database"""
    abjs.rem_da(login, ue_code, user_name, date)

@utilities.add_a_lock # Protect the global variable 'abjs'
def get_abjs(year, semester):
    """Get the ABJ/DA database for the indicated semester"""
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

def add_abjs(year, semester, ticket, student, from_date, to_date, comment):
    """Helper function"""
    get_abjs(year, semester).add(student, from_date, to_date, ticket.user_name,
                                 comment=comment)

def rem_abjs(year, semester, ticket, student, from_date, to_date):
    """Do not use the bugged function"""
    get_abjs(year, semester).rem2(student, from_date, to_date,
                                  ticket.user_name)

def add_abjs_da(year, semester, ticket, student, ue_code, date, comment):
    """Helper function"""
    get_abjs(year, semester).add_da(student, ue_code, date, ticket.user_name,
                                    comment=comment)

def rem_abjs_da(year, semester, ticket, student, ue_code):
    """Helper function"""
    get_abjs(year, semester).rem_da(student, ue_code, ticket.user_name)

def html_abjs(year, semester, student, read_only=False):
    """Get all the ABJS/DA informations has HTML"""
    the_abjs = get_abjs(year, semester)
    if read_only:
        the_abjs.update()
    try:
        html = the_abjs.students[inscrits.login_to_student_id(student)].html()
        return unicode(html, 'utf-8')
    except KeyError:
        return u''

def a_student(browser, year, semester, ticket, student, do_close=True):
    """Send student abj with the data to_date the navigator."""
    student = inscrits.login_to_student_id(student)
    aabjs = get_abjs(year, semester)
    html = '<SCRIPT>'
    html += """set_html(
         '<IMG SRC="'+student_picture_url('%s')+'">');""" \
    % student

    html += "append_html('<A HREF=\"%s/%s\">%s</A>, %s<br>');" % (
        configuration.suivi.url(year,semester,ticket.ticket),
        student.replace("'","\\'"),
        ' '.join(inscrits.firstname_and_surname(student)).replace("'","\\'"),
        ', '.join(inscrits.portail(student)).replace("'","\\'")
        )

    if student in aabjs.students:
        html += "display_abjs(%s);" % unicode(aabjs.students[student].js(),
                                           'utf8')
        html += "display_da(%s);" % unicode(aabjs.students[student].js_da(),
                                         'utf8')
        ue_list = aabjs.students[student].ues_without_da()
    else:
        html += "display_abjs([]);"
        html += "display_da([]);"
        ue_list = inscrits.ues_of_a_student_short(student)

    ue_list.sort()
    html += "ues_without_da(%s);" % js(ue_list)
    html += '</SCRIPT>'
    browser.write(html.encode('utf8'))
    if do_close:
        browser.close()
    else:
        browser.flush()


def translate_tt(tt_value):
    """Translate some TT values to more informative values"""
    if tt_value.strip() == '1' or tt_value.lower() == 'o':
        return '1/3'
    else:
        return tt_value

def date_to_time(date):
    """Concert a french date to seconds"""
    return time.mktime(time.strptime(date, "%d/%m/%Y"))
        
def tierstemps(student_id, aall=False, table_tt=None):
    """Returns a strings containing all tiers-temps informations about
    the student from the TT table given."""
    if table_tt == None:
        # Get TT for current year
        table_tt = document.table(utilities.university_year(),
                                  'Dossiers', 'tt')
    for line in table_tt.get_lines(student_id):
        html = ""
        if aall is False:
            try:
                if line[8].value:
                    if time.time() < date_to_time(line[8].value):
                        continue
                if line[9].value:
                    if time.time() > date_to_time(line[9].value):
                        continue
            except ValueError:
                utilities.send_backtrace(repr(line))
        else:
            if line[8].value:
                html += u'À partir du ' + line[8].value + '\n'
            if line[9].value:
                html += u'Jusqu\'au ' + line[9].value + '\n'
            
        if line[3].value:
            html += u"Temps supplémentaire pour les examens écrits : %s\n" % (
                translate_tt(line[3].value))
        if line[4].value:
            html += u"Temps supplémentaire pour les examens oraux : %s\n" % (
                translate_tt(line[4].value))
        if line[5].value:
            html += u"Temps supplémentaire pour les examens de TP : %s\n" % (
                translate_tt(line[5].value))
        if line[6].value == 'OUI':
            html += u"Dispose d'une secrétaire particulière\n"
        if line[7].value == 'OUI':
            html += u"Dispose d'une salle particulière\n"
        if line[10].value:
            html += unicode(line[10].value, 'utf-8') + '\n'
        return html
    return ''

def alpha(browser, year, semester):
    """Returns ABJ/DA information for all the students in CSV format"""
    import csv
    aabjs = get_abjs(year, semester)
    writer = csv.writer(browser, delimiter=';', quoting=csv.QUOTE_ALL)
    for student in aabjs.students.values():
        fn, sn = inscrits.firstname_and_surname(student.login)
        fn = fn.encode('latin1')
        sn = sn.encode('latin1')
        for from_date, to_date, author, comment in student.abjs:
            writer.writerow( (fn, sn, student.login, 'ABJ',
                              from_date, to_date, comment, author) )
        for ue_code, date, author, comment in student.da:
            writer.writerow( (fn, sn, student.login, 'DAS', ue_code, date,
                              comment, author) )
    browser.close()

def title(name, sort_fct):
    """Columns title with the link to sort the HTML table"""
    return (name +
            ' <span class="x">(<a href="javascript:sort(' +
            sort_fct +
            ')">Trier</a>)</span>')

def alpha_html(browser, year, semester, ue_name_endswith=None, author=None):
    """Returns ABJ/DA information for all the students in HTML format"""
    global L
    if L is None:
        L = type(inscrits.L)('LDAP3')

    aabjs = get_abjs(year, semester)
    browser.write('''<html>
<head>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
</head>
<body>
<div id="x">Veuillez patienter, la page se charge.</div>
<table style="table-layout: fixed" border><tbody id="t">
''')
    line = '<tr>'  +  '<td>%s</td>' * 7  +  '</tr>\n'
    browser.write(line % (
        'Prénom',
        title('Nom', 'cmp_name'),
        title('N°',  'cmp_id'),
        'Quoi',
        title('Date', 'cmp_ue'),
        title('Date fin ou UE', 'cmp_ue2'),
        title('Commentaire', 'cmp_comment')))
    for student in aabjs.students.values():

        if ue_name_endswith:
            for ue_code in L.ues_of_a_student_short(student.login):
                if ue_code[-1] == ue_name_endswith:
                    break
            else:
                # No UE ended by the required character
                continue

        fn, sn = inscrits.firstname_and_surname(student.login)
        fn = fn.encode('utf8')
        sn = sn.encode('utf8')
        for from_date, to_date, author2, comment in student.abjs:
            if author is None or author == author2:
                browser.write( line % (fn, sn, student.login, 'ABJ',
                                 from_date, to_date, cgi.escape(comment)) )
        for ue_code, date, author2, comment in student.da:
            if author is None or author == author2:
                browser.write( line % (fn, sn, student.login, 'DAS', date,
                                       ue_code, cgi.escape(comment)) )
    browser.write('</tbody></table>')
    browser.write(utilities.read_file(os.path.join('FILES', 'abj_recap.html')))
    browser.close()


def underline(txt, char='='):
    """Returns the text preceded with a line of '=' of same length"""
    return '\n' + char * len(txt) + '\n' + txt + '\n' + char * len(txt) + '\n'

def nice_date(date):
    """Returns a DD/MM/YYYY/[AM] nicely formatted"""
    return date.replace('M',' matin').replace('A', u' après-midi')

def get_table_tt(year, semester):
    """Returns the current database for TT"""
    return document.table(utilities.university_year(year, semester),
                          'Dossiers', 'tt')

L = None

def feedback(browser, letter, nr_letters):
    """This function displays a feedback in the browser while
    loading students informations"""
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
def prune_abjs(abj_list, group, sequence, ue_code):
    """Trim unecessary ABJS"""
    return abj_list

def do_prune(abj_list, first_day, last_day, group, sequence, ue_code):
    """Trim unecessary ABJS using first and last day of the course."""
    abjs_pruned = []
    for abjj in abj_list:
        try:
            seconds = date_to_time(abjj[0][:-1])
        except OverflowError:
            seconds = 0
        if seconds >= last_day:
            continue
        try:
            seconds = date_to_time(abjj[1][:-1])
        except OverflowError:
            seconds = 8000000000
        if seconds < first_day:
            continue
        abjs_pruned.append(abjj)

    return prune_abjs(abjs_pruned, group, sequence, ue_code)

def ue_mails_and_comments(ue_code):
    """Returns the mails of the master of the UE and a comment
    about the origin of the mail address"""
    global L
    if L is None:
        L = type(inscrits.L)('LDAP3')

    mails = []
    text = []
    the_ue = teacher.all_ues().get(ue_code[3:], None)
    if the_ue:
        for teacher_name in the_ue.responsables():
            text.append("   * " + teacher_name + ' : ')
            teacher_login = teacher.responsable_pedagogique_ldap(teacher_name)
            if teacher_login is None:
                text.append('ENSEIGNANT INCONNU !')
            else:
                mail = L.mail(teacher_login)
                if mail == None:
                    text.append('MAIL INCONNU !')
                else:
                    mails.append(mail.lower())
                    text.append(mail)
            text.append('\n')

    # Add other mails
            
    other_mails = []
    for an_other_mail in teacher.other_mails(ue_code[3:]):
        an_other_mail = an_other_mail.lower().encode('utf-8')
        if an_other_mail not in mails:
            other_mails.append(an_other_mail)

    if other_mails:
        text.append("   * Adresse venant du fichier des UE ouvertes : " +
                 ', '.join(other_mails) + '\n')
        mails += other_mails

    # Add other mails from SPIRAL

    if the_ue:
        other_mails = []
        for an_other_mail in the_ue.mails():
            an_other_mail = an_other_mail.lower()
            if an_other_mail not in mails:
                other_mails.append(unicode(an_other_mail, 'utf-8'))

        if other_mails:
            text.append("   * Adresses venant de SPIRAL : " +
                     ', '.join(other_mails) + '\n')
            mails += other_mails

    if len(mails) == 0:
        text.append('AUCUN RESPONSABLE CONNU\n')

    return mails, text

def ue_resume(ue_code, year, semester, browser=None):
    """Returns all the ABJ/DA/TT informations about the all the UE students"""
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
    the_ue = teacher.all_ues().get(ue_code[3:], None)

    if browser:
        text = []
        browser.write('Génération de la page :\n')
    else:
        text = [u"""Mesdames, Messieurs,

Voici la liste des étudiants en dispense d'assiduité, en tiers temps
et ceux qui ont justifié leurs absences.
Ces informations sont disponibles sur http://tomuss.univ-lyon1.fr/
Sur ce site il est possible d'afficher les ABJ pour une date donnée.

Cordialement.

"""]

    if not the_ue:
        text.append(underline(ue_code + u' : Titre non renseigné dans SPIRAL'))
    else:
        text.append(underline(ue_code + ' : ' + the_ue.intitule()))

    text.append(u'\nPour accéder à la version à jour de ces informations '
             u'suivez le lien :\n\n')
    text.append('    %s/%s/%s/%s/resume\n' % (
        configuration.server_url, year, semester, ue_code))
    #
    # The UE managers
    #
    text.append(underline("Responsables de l'UE", char='-'))
    mails, infos = ue_mails_and_comments(ue_code)
    text += infos

    the_students = []
    first_day = 0
    last_day = 8000000000
    if current_year:
        for infos in L.students(ue_code):
            if infos[0] not in the_students:
                the_students.append((infos[0], infos[4], infos[5]))

    if len(the_students) == 0:
        # Fast process but may be incomplete
        table_ue = document.table(year, semester, ue_code, create=False)
        if table_ue:
            the_students = [(line[0].value, line[3].value, line[4].value)
                            for line in table_ue.lines.values()
                            if line[0].value]
            first_day = table_ue.dates[0]
            last_day = table_ue.dates[1] + 86400 # End of last day
            table_ue.unload()
    if first_day == 0:
        if semester == 'Automne':
            first_day = time.mktime( (year  , 8, 15, 0, 0, 0, 0, 0, 0) )
            last_day  = time.mktime( (year+1, 1, 31, 0, 0, 0, 0, 0, 0) )
        elif semester == 'Printemps':
            first_day = time.mktime( (year  , 1, 31, 0, 0, 0, 0, 0, 0) )
            last_day  = time.mktime( (year  , 7, 31, 0, 0, 0, 0, 0, 0) )
    utilities.warn('first_day=%s %s' % (first_day, last_day))
    #
    # The ABJ
    #
    first = True
    infos = []
    for student_login, group, sequence in the_students:
        student_id = inscrits.login_to_student_id(student_login)
        student = aabjs.students.get(student_id)
        if not student:
            continue
        
        abjs_pruned = do_prune(student.abjs, first_day, last_day,
                               group, sequence, ue_code) 

        if len(abjs_pruned) == 0:
            continue
        nr_letters = feedback(browser, 'A', nr_letters)
        if first:
            first = False
            text.append(underline("Liste des ABJ", char='-'))
        fs = L.firstname_and_surname(student.login)
        the_abjs = ('   * ' + student.login + ' ' + fs[1].upper() + ' ' +
                    fs[0].title() + '\n')
        for abj in abjs_pruned:
            if abj[0] == abj[1]:
                an_abj = '      - Le ' + nice_date(abj[0])
            elif abj[0][:-1] == abj[1][:-1]:
                an_abj = '      - Le ' + abj[0][:-1]
            else:
                an_abj = "      - Du " + nice_date(abj[0]) + ' au ' \
                  + nice_date(abj[1]) + ' inclus'
            if abj[3]:
                an_abj += ' (' + unicode(abj[3],'utf8') + ')'
            
            the_abjs += an_abj + '\n'
        infos.append( (utilities.flat(fs[1]).lower(),
                    utilities.flat(fs[0]).lower(),
                    the_abjs) )
    if infos:
        infos.sort()
        text += zip(*infos)[2]
    #
    # The DA
    #
    first = True
    infos = []
    for student_login, group, sequence in the_students:
        student_id = inscrits.login_to_student_id(student_login)
        student = aabjs.students.get(student_id)
        if not student:
            continue
        dates = [d for d in student.da if d[0] == ue_code]
        if dates:
            nr_letters = feedback(browser, 'D', nr_letters)
            if first:
                first = False
                text.append(underline(u"Liste des étudiants avec une DA",
                                   char='-'))
            fs = L.firstname_and_surname(student_login)
            an_abj = ('   * ' + student_login + ' '
                      + fs[1].upper() + ' ' + fs[0].title()
                      + u' à partir du ' + dates[0][1])
            if dates[0][3]:
                an_abj += ' (' + dates[0][3] + ')'
            an_abj += '\n'
            
            infos.append((utilities.flat(fs[1]).lower(),
                          utilities.flat(fs[0]).lower(),
                          an_abj))
    if infos:
        infos.sort()
        text += zip(*infos)[2]
    #
    # The TT
    #
    first = True
    tt_logins = list(table_tt.logins())
    infos = []

    for student_login, group, sequence in the_students:
        if not student_login in tt_logins:
            continue
        infos_tt = tierstemps(student_login, True, table_tt = table_tt)
        nr_letters = feedback(browser, 'T', nr_letters)
        if first:
            first = False
            text.append(underline(u"Liste des étudiants avec un tiers temps",
                               char='-'))
        fs = L.firstname_and_surname(student_login)
        a_tt = ('   * ' + student_login + ' ' + fs[1].upper() + ' '
                + fs[0].title() + '\n')
        for line in infos_tt.split('\n')[:-1]:
            a_tt += '      - ' + line + '\n'
        infos.append((utilities.flat(fs[1]).lower(),
                      utilities.flat(fs[0]).lower(),
                      a_tt))

    if infos:
        infos.sort()
        text += zip(*infos)[2]

    return text, mails

to_send_ok = [] # (Recipent, Title, message) list

def list_mail(browser, year, semester, only_licence=True):
    """Compute and display for all the UE the 'ue_resume'.
    Store the result in order to send all the mails after human check"""
    global L
    if L is None:
        L = type(inscrits.L)('LDAP3')

    to_send = []
    sender = configuration.abj_sender
    browser.write("Les messages seront envoyés au nom de " + sender)
    browser.write('<pre>')

    aabjs = get_abjs(year, semester)
    ues = {}
    for student in aabjs.students.values():
        for a_da in student.da:
            ues[a_da[0]] = True
        if student.abjs:
            for ue_code in L.ues_of_a_student_short(student.login):
                ues[ue_code] = True

    table_tt = get_table_tt(year, semester)
    tt_logins = list(table_tt.logins())
    for student_login in tt_logins:
        for ue_code in L.ues_of_a_student_short(student_login):
            ues[ue_code] = True

    if only_licence:
        ues = [ue_code for ue_code in ues if ue_code[-1] == 'L']

    for ue_code in ues:
        lines, mails = ue_resume(ue_code, year, semester)
        browser.write(''.join(lines).encode('utf8'))
        if mails:
            to_send.append( (mails,
                             'ABJ + DA + TT pour l\'UE ' + ue_code,
                             ''.join(lines).encode('latin1') ) )

    global to_send_ok
    to_send_ok = to_send
    
    browser.write('''</pre>
<h1>SUIVEZ LE LIEN POUR ENVOYER LES %d MESSAGES AUX ENSEIGNANTS</a></h1>
ATTENTION une fois que vous cliquez sur le lien à la fin de cette ligne,
es messages seront envoyés : <a href="send_mail">Envoyer!</a>
''' % len(to_send))
    browser.close()


to_send_ok_example = [
    (['exco@bat710.univ-lyon1.fr', 'thierry.excoffier@bat710.univ-lyon1.fr'],
     'UE_CODE x',
     'blabla'),
    (['exco@liris.univ-lyon1.fr', u'excé@www710.univ-lyon1.fr'],
     'UE_CODE y',
     'blaBLA'),
    (['exco@bat710.univ-lyon1.fr', 'thierry.excoffier@bat710.univ-lyon1.fr'],
     'UE_CODE z',
     'blabla'),
    ]

def send_mail(browser):
    """Send all the mails generated by 'list_mail'"""
    for recipients, mail_title, text in to_send_ok:
        try:
            error = utilities.send_mail(recipients,
                                        mail_title,
                                        text,
                                        configuration.abj_sender)
            if error:
                browser.write("<pre>" + error + "</pre>")
            else:
                browser.write("<p>" + repr(recipients) + ' : message envoyé')
        except UnicodeEncodeError:
            browser.write("<pre>BUG dans abj.send_mail</pre>")
