#!/bin/env python
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

import cgi
import utilities
import re
import configuration

###############################################################################
# This part is for column import.
# column import can by done on any column type.
###############################################################################

cookies = None

def read_url_not_cached(url):
    """Read an URL content to import in a column"""
    import urllib2
    try:
        f = urllib2.urlopen(url)
        c = f.read()
        f.close()

        if '<html>' in c.lower():
            try:
                import LOCAL.fakeuser
                global cookies
                c, cookies = LOCAL.fakeuser.connection(url, cookies)[:2]
            except ImportError:
                utilities.send_backtrace('Missing LOCAL.fakeuser.connection')
        
        return c
    except:
        utilities.send_backtrace('IMPORT ' + url)
        return
read_url = utilities.add_a_cache(read_url_not_cached, timeout=5)    


@utilities.add_a_lock
def update_column_content(column, url):
    utilities.warn('IMPORT %s' % url)

    url_base = url.split('#')[0]

    if configuration.regtest:
        c = read_url_not_cached(url_base)
    else:
        c = read_url(url_base)
    if c is None:
        return
    for encoding in ('utf8', 'latin1'):
        try:
            c = unicode(c, encoding)
            break
        except:
            pass
    else:
        utilities.send_backtrace('Bad encoding for %s' % url,
                                 exception=False)
        return # Bad encoding

    c = c.encode('utf8').replace('\r','\n').split('\n')

    utilities.warn('READ %d LINES IN %s' % (len(c), url))

    try:
        col = int(url.split('#')[1]) - 1
    except (IndexError, ValueError):
        return

    if col <= 0:
        return

    import csv
    if '\t' in c[0]:
        delimiter = '\t'
    elif ';' in c[0]:
        delimiter = ';'
    else:
        delimiter = ','
    for line in csv.reader(c, delimiter=delimiter):
        if len(line) <= col:
            continue
        for line_id, cells in  column.table.get_items(line[0]):
            new_value = line[col]
            if cells[column.data_col].value != new_value:
                column.table.lock()
                try:
                    column.table.cell_change(column.table.pages[0],
                                           column.the_id,
                                           line_id, new_value)
                finally:
                    column.table.unlock()

###############################################################################
# Text column definition
###############################################################################

class Text(object):

    human_priority = 0 # To define menu order
    
    # Title displayed in the TYPE menu
    full_title = 'Texte libre'

    # The following variables contains the name of a JavaScript
    # function defined in the text.js file
    
    set_title = 'set_title'
    set_type = 'set_type'
    set_test_filter = 'unmodifiable'
    set_minmax = 'unmodifiable'
    set_weight = 'unmodifiable'
    set_green = 'set_green'
    set_red = 'set_red'
    set_empty_is = 'set_empty_is'
    set_columns = 'unmodifiable'
    set_visibility_date = 'set_visibility_date'
    set_comment = 'set_comment'
    set_freezed = 'test_nothing'
    set_width = 'test_float'
    set_position = 'test_float'
    set_hidden = 'test_float'
    set_author = 'test_nothing'

    # Default values
    default_filter = ''

    # Default tips
    tip_column_title = """Titre de la colonne, cliquez dessus
pour la trier dans une direction ou l'autre."""
    tip_title = """<b>Titre de la colonne.</b><br>
    Indiquez des noms compréhensibles pour les étudiants.<br>
    Noms standards pour importer dans APOGÉE&nbsp;:
    <ul>
    <li> APO_CC : Contrôle Continu (seule note à saisir si l'UE est 100% contrôle continue).
    <li> APO_CP : Partiel.
    <li> APO_CT : Examen.
    <li> APO_CT2 : Examen, session 2.
    </ul>"""
    tip_type = """<b>Type de la colonne</b>, il indique le contenu des cellules :
<ul>
<li> 'Text' : du texte libre
<li> 'Note' : une note, ou un indicateur de présence
<li> 'Moy' : calcul de la moyenne pondérée de plusieurs colonnes
<li> 'Prst' : Cellules cliquables pour indiquer la présence
<li> 'Nmbr' : Compte le nombre de cellules contenant une valeur
<li> 'Date' : Des dates de la forme JJ/MM/AAAA
<li> 'Bool' : Oui ou Non
<li> 'Max' : Maximum sur plusieurs colonnes
</ul>"""
    tip_filter = """Exemple de filtre :
<ul>
<li><b>abc</b> pour afficher seulement les valeurs commençant par <b>abc</b>
<li><b>~ab</b> pour afficher les valeurs contenant <b>ab</b>
<li><b>!A</b> pour afficher seulement les valeurs ne commençant pas par <b>A</b>
</ul>"""
    tip_weight = ''
    tip_test_filter = ''
    tip_minmax = ''
    tip_cell = "Texte libre"
    tip_columns = ''
    tip_red = """<b>Colorie en rouge</b> les cellules contenant<br>
    une valeur inférieure à celle indiquée.<br>On peut utiliser un filtre"""
    tip_green = """<b>Colorie en vert</b> les cellules contenant<br>
    une valeur supérieure à celle indiquée.<br>On peut utiliser un filtre"""
    tip_visibility_date = """<b>Date où la colonne devient visible pour les étudiants</b>.<br>
    La date est indiquée sous la forme JJ/MM/AAAA.<br>
    <b><em>Si rien n'est indiqué : tout est visible par les étudiants.</em></b>"""
    tip_empty_is = """<b>Valeur par défaut des cellules vides</b>.<br>
    Cette valeur sera utilisée dans les moyennes que<br>
    cela soit dans le tableau ou le suivi des étudiants.<br>
    La case restera vide dans le tableau.<br>
    Par exemple : ABINJ, PRST, 0, 10..."""
    tip_comment = """Tapez un commentaire pour cette colonne.<br>
    Il est visible par les étudiants."""
    tip_author = "Personne qui a modifié la définition<br>de la colonne pour la dernière fois :"


    # The value is a float most of the time
    should_be_a_float = 0


    # check value to be stored in the cell
    cell_test = 'test_nothing'
    # What to do on mouse lcick
    onmousedown = 'cell_select'
    # How to display the cell value
    formatte = 'text_format'
    # What to to on cell double click
    ondoubleclick = 'undefined'
    # How to compute the cell value
    cell_compute = 'undefined'
    # Cell is modifiable ? (a computed cell may be modifiable)
    cell_is_modifiable = 1

    def value_range(self, v_min, v_max):
        """Display the range of the possible values"""
        return ''

    def cell_indicator(self, column, value, cell, lines):
        """Return an HTML class name and a value between 0 and 1
        to indicate that the cell is 'good' or 'bad'"""
        return '', None
    
        if column.title == 'Grp':
            return '', None
        return {'A': ('verygood',1),
                'B': ('', 0.5),
                'C': ('bad', 0.3),
                'D': ('verybad', 0)
               }.get(value, ('',None))

    def formatter(self, column, value, cell, lines, teacher, ticket, line_id):
        """HTML Formatter returns a tuple :
             (text, classname, comment)
        'text' is None if the cell should not be displayed.
        """
        if value == '':
            return ('', '', '')

        return (cgi.escape(str(value)),
                self.cell_indicator(column, value, cell, lines)[0],
                '')

    def _values(self): # _ to hide it a little
        t = []
        for i in self.keys:
            try:
                t.append(str(getattr(self,i)))
            except KeyError:
                pass
        return t

    def __str__(self):
        return '"' + self.name + '"'

    def test_ok(self, test):
        return True
    
    def attribute_js_value(self, k):
        if k.startswith('set_') or k in (
            'cell_test', 'onmousedown', 'formatte', 'ondoubleclick',
            'cell_compute'):
            return getattr(self, k)
        else:
            return utilities.js(getattr(self, k))

    def update_one(self, the_table, line_id, column):
        """Do some server side compute on the cell.
        This function is used when the user input interactivly one cell.
        """
        pass

    def update_all(self, the_table, column, attr=None):
        """Do some server side compute on the cell.
        This function update the full column content for every line.
        It is called :
           * on page load to check changs.
           * when the 'attr' column attribute is changed.
           * when a column used by this one changed
        """
        if attr is not None and attr.name != 'comment':
            return

        if 'IMPORT(' not in column.comment:
            return
        
        url = re.sub(r'.*IMPORT\(', '', column.comment)
        url = re.sub(r'\).*', '', url)

        if column.import_url == url:
            return

        column.import_url = url

        if not (url.startswith('http:')
                or url.startswith('https:')
                or url.startswith('ftp:')
                or (url.startswith('file:') and configuration.regtest)
                ):
            return

        update_column_content(column, url)

Text.keys = sorted([i for i in Text.__dict__ if not i.startswith('_')])
Text.keys.remove('full_title')
Text.keys.insert(0, 'full_title')
