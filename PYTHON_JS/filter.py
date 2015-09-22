# -*- coding: utf-8 -*-
# TOMUSS: The Online Multi User Simple Spreadsheet
# Copyright (C) 2013-2014 Thierry EXCOFFIER, Universite Claude Bernard
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Contact: Thierry.EXCOFFIER@univ-lyon1.fr

# In order to translate to pure JavaScript:
#    No inherance
#    Define classes before using them
#    No else: after for:

"""
"""

# Set to True if 'B' filter must not found 'b' value.
# This value must never be changed once table have been created by users
contextual_case_sensitive = False


current_seconds, year_month_day = update_today()


nan = float('NaN')

# Dates are defined as string : YYYYMMDDHHMMSS
# We assume that date are all valid.
# YYYYMM = YYYYMM00000000
# User dates:
#    * Day (current month)
#    * Day/Month (current year)
#    * Day/Month/Year
#    * Date[-_ ] Hour
#    * Date[-_ ] Hour:Minute
#    * Date[-_ ] Hour:Minute:Seconds

def two_digits(value):
    if value >= 10:
        return str(value)
    return '0' + str(value)

letter_to_duration = {
    'y': 365*24,
    'm':  30*24,
    'w':   7*24,
    'd':     24,
    'h':      1,
    }
# French translations
letter_to_duration['a'] = letter_to_duration['y']
letter_to_duration['s'] = letter_to_duration['w']
letter_to_duration['j'] = letter_to_duration['d']

def is_a_relative_date(txt):
    return txt != '' and txt[-1] in letter_to_duration

def user_date_to_date(txt):
    if txt == '':
        # Today
        return (str(year_month_day[0])
                + two_digits(year_month_day[1])
                + two_digits(year_month_day[2])
                )
    if is_a_relative_date(txt):
        try:
            nb = float(txt[:-1])
        except:
            return "9999"
        return seconds_to_date(
            current_seconds - nb * letter_to_duration[txt[-1]] * 60*60)

    txt = REsplit("[- _]", txt)
    t = ''
    if len(txt) == 2:
        hour = txt[1].split(':')
        for hms in hour:
            if hms == '':
                break
            try:
                t += two_digits(int(hms))
            except:
                break
    txt = txt[0].split('/')
    try:
        the_day = int(txt[0])
    except:
        return '9999'
    the_month = year_month_day[1]
    if len(txt) >= 2:
        try:
            the_month = int(txt[1])
        except:
            pass
    the_year = year_month_day[0]
    if len(txt) >= 3:
        try:
            the_year = int(txt[2])
        except:
            pass
    return str(the_year) + two_digits(the_month) + two_digits(the_day) + t

    
class FilterNegate:
    # The negation node in the filter tree"""
    def __init__(self, node):
        self.node = node
    def evaluate(self, cell):
        return not self.node.evaluate(cell)
    def js(self):
        return '!' + self.node.js()

class FilterTrue:
    # True
    def evaluate(self, cell):
        return True
    def js(self):
        return 'true'

class FilterFalse:
    # False
    def evaluate(self, cell):
        return False
    def js(self):
        return 'false'

def search_operator(string):
    for operator in filterOperators:
        if string.startswith(operator[0]):
            return string[len(operator[0]):], operator
    return string, operator

class FilterOperator:
    # Compare node to a constant in the filter tree
    # No inherence possible with PythonJS, so there are no sub classes
    def __init__(self, operator, what, value, column_type):
        self.date_value = None
        if what == 'date' or (column_type == 'Date' and what == "value"):
            if operator[0] == '':
                dummy, operator = search_operator('=')
            if operator[3] is not None:
                if is_a_relative_date(value):
                    dummy, operator = search_operator(operator[3])
                self.date_value = user_date_to_date(value)
        self.what = what
        self.operator = operator[0]
        self.python = operator[1]
        self.js_string = operator[2]
        self.is_string_operator = (operator[3] is None
                                   or (what != 'value' and what != 'comment')
                                   or value == '')
        self.is_number = False
        if not self.is_string_operator and self.date_value is None:
            try:
                self.value = to_float(value)
                self.is_number = True
            except:
                self.value = value
                self.is_string_operator = True
        try:
            value = unicode(value, 'utf-8')
        except:
            value = unicode(value) # Number
        low = value.lower()
        self.case_sensitive = low != value and contextual_case_sensitive
        flatted = flat(value)
        self.diacritic_sensitive = flatted != value
        
        if self.case_sensitive:
            self.string_value = value
        else:
            self.string_value = low
        if not self.diacritic_sensitive:
            self.string_value = flat(self.string_value)
        
    def evaluate(self, cell):
        v = getattr(cell, self.what)
        try:
            v = unicode(v, 'utf-8')
            if not self.case_sensitive:
                v = v.lower()
            if not self.diacritic_sensitive:
                v = flat(v)
        except:
            v = str(v) # It is a number
        # print 'v=%s date_value=%s string_operator=%d self.value=%s' % (
        #     v, self.date_value, self.is_string_operator,
        #     getattr(self, 'value', None))
        if self.date_value is not None:
            if self.what == "value":
                v = user_date_to_date(v)
            r = self.python(v[:len(self.date_value)], self.date_value)
        elif self.is_string_operator:
            r = self.python(v, self.string_value)
        else:
            if v == '':
                # To be compatible with javascript
                r = self.python(0, self.value)
            else:
                r = self.python(to_float_or_nan(v), self.value)
        return r

    def js(self):
        if self.date_value is not None:
            if self.what == 'date':
                return self.js_string('cell.date.substr(0,'
                                      + str(len(self.date_value)) + ')',
                                      '"' + self.date_value + '"')
            else:
                return self.js_string('user_date_to_date(cell.value).substr(0,'
                                      + str(len(self.date_value)) + ')',
                                      '"' + self.date_value + '"')
        if self.is_number:
            return self.js_string('to_float_or_nan(cell.' + self.what + ')',
                                  str(self.value))
        
        else:
            if self.what == 'value':
                what = self.what + '.toString()'
            else:
                what = self.what
            what = 'cell.' + what
            if not self.case_sensitive:
                what += '.toLowerCase()'
            if not self.diacritic_sensitive:
                what = 'flat(' + what + ')'
            return self.js_string(what, js_str(self.string_value))


# Should be subclasses, but not possible with PythonJS
# The arguments are:
#    * the filter operation,
#    * the python eval
#    * a function creating the JavaScript code to do the same evaluation.
#    * The reverse numeric operator

def LE(a, b): return a <= b
def LE_str(a, b): return '(' + a + '<=' + b + ')'
def LT(a, b): return a < b
def LT_str(a, b): return '(' + a + '<' + b + ')'
def GE(a, b): return a >= b
def GE_str(a, b): return '(' + a + '>=' + b + ')'
def GT(a, b): return a > b
def GT_str(a, b): return '(' + a + '>' + b + ')'
def EQ(a, b): return a == b
def EQ_str(a, b): return '(' + a + '==' + b + ')'
def TILDE(a, b): return b in a
def TILDE_str(a, b): return '(' + a + '.indexOf(' + b + ') != -1)'
def START(a, b): return a.startswith(b)
def START_str(a, b): return '(' + a + '.substr(0,' + b + '.length)==' + b + ')'
def AUTHOR(a, b): return a == b or a in major_of(b)
def AUTHOR_str(a, b): return ('(' + a + '==' + b + '||myindex(minors,'
                              + a + ')!=-1)')

filterOperators = [
    ['<=', LE, LE_str, '>='],
    ['<' , LT, LT_str, '>' ],
    ['>=', GE, GE_str, '<='],
    ['>' , GT, GT_str, '<' ],
    ['=' , EQ, EQ_str, '=' ],
    ['~' , TILDE, TILDE_str, None],
    [''  , START, START_str, None],
    ]
filterAttributes = {'@': 'author',
                    '#': 'comment',
                    ':': 'history',
                    '?': 'date'}

class Filter:
    # Parse the filter to create a list of nodes
    def __init__(self, string, username, column_type):
        if string == '':
            self.filters = [[FilterTrue()]]
            return
        self.filters = [] # 'ORed' list of 'ANDed' items
        # OR is replaced by its translation
        string = replace_all(string," " + or_keyword() + " ", " | ")
        mode = "|"
        while string:
            node, string = self.parse(string, username, column_type)
            if mode == '|':
                self.filters.append([node])
            else:
                self.filters[-1].append(node)
            if len(string) and (string[0] == '|' or string[0] == '&'):
                mode = string[0]
                string = string[1:].lstrip()
            else:
                mode = '&'

    def parse(self, string, username, column_type):
        negate = False
        if string[0] == '!':
            negate = True
            string = string[1:]
        # Uncomment to allow white space after negation
        # string = string.lstrip()
        if string:
            attr = filterAttributes.get(string[0], "value")
            if attr != 'value':
                string = string[1:]
        else:
            attr = 'value'
            if negate:
                return FilterFalse(), ''
            else:
                return FilterTrue(), ''
        string, operator = search_operator(string)
        value = ''
        protected = False
        i = 0
        for char in string:
            i += 1
            if not protected:
                if char == ' ':
                    # Search non space char
                    next_char = ""
                    for next_char in string[i:]:
                        if next_char != ' ':
                            break
                    if next_char == ' ':
                        break

                if (char == ' '
                    and operator[0] == ''
                    and attr == 'value'
                    and filterAttributes.get(next_char, '') == '' # the value
                    and search_operator(next_char)[1][0] == ''    # starting by
                    and next_char not in '&|@#:?<>=~!'
                    and negate == False
                    ):
                    # Filter 'a b' is to translated as 'a\ b' because
                    # starting by both 'a' and 'b' is impossible
                    # End users WANTS this
                    pass
                elif " |&".find(char) >= 0:
                    i -= 1
                    break
                if char == '\\':
                    protected = True
                    continue
            else:
                protected = False
            value += char

        if len(value) == 0 and operator[0] == '':
            if attr == 'author':
                value = username
                operator = ['', AUTHOR, AUTHOR_str, None]
            elif attr == 'comment' or attr == 'history':
                # Special filters : '#' and ':'
                dummy, operator = search_operator('=')
                negate = not negate

        node = FilterOperator(operator, attr, value, column_type)
        if negate:
            node = FilterNegate(node)

        return node, string[i:].lstrip()

    def evaluate(self, cell):
        result = False
        for f in self.filters:
            bad = False
            for ff in f:
                if not ff.evaluate(cell):
                    bad = True
                    break
            if not bad:
                result = True
                break

        if debug:
            error = False
            if not python_mode: # not python_mode:
                error = "Can not compile js: " + self.js()
                js = self.compiled_js()
                error = "Can not evaluate compiled filter: " + js
                value = js(cell)
                if value == result:
                    error = False
                else:
                    error = ("Unexpected value: '" + value
                             + "' in place of '" + result
                             + "' for:\n\tcell: " + cell.js()
                             + '\n\tjs: ' + js + "'")
            if error:
                print(error)
                raise ValueError(error)

        return result

    def js(self):
        return '(' + '||'.join(['&&'.join([ff.js()
                                           for ff in f])
                                for f in self.filters
                             ]) + ')'

    def compiled_js(self):
        return eval('(function x(cell) { return ' + self.js() + ';})')

