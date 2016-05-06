#!/usr/bin/python3
# -*- coding: utf-8 -*-
# TOMUSS: The Online Multi User Simple Spreadsheet
# Copyright (C) 2013-2016 Thierry EXCOFFIER, Universite Claude Bernard
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
#    Define classes before using them
#    No else: after for:
#    No format or %

# Set to True if 'B' filter must not found 'b' value.
# This value must never be changed once tables have been created by users
contextual_case_sensitive = False

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

def get_relative_date(txt):
    try:
        nb = float(txt[:-1])
    except:
        return "9999"
    return seconds_to_date(
        millisec()/1000 - nb * letter_to_duration[txt[-1]] * 60*60)

def user_date_to_date(txt):
    if txt == '':
        # Today
        year_month_day = localtime()
        return (str(year_month_day[0])
                + two_digits(year_month_day[1])
                + two_digits(year_month_day[2])
                )
    if is_a_relative_date(txt):
        return get_relative_date(txt)

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
    year_month_day = localtime()
    txt = txt[0].split('/')
    try:
        the_day = int(txt[0])
    except:
        return '9999'
    if isNaN(the_day):
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


class CellAttr:
    def __init__(self):
        pass
class CellAttrCell(CellAttr):
    def __init__(self, what):
        self.what = what
    def fct(self, dummy_line, cell):
        return getattr(cell, self.what)
    def js(self):
        return 'cell.' + self.what
class CellAttrOther(CellAttr):
    def __init__(self, data_col, what):
        self.what = what
        self.data_col = data_col
    def fct(self, line, cell):
        return getattr(line[self.data_col], self.what)
    def js(self):
        return 'line[' + str(self.data_col) + '].' + self.what

class CellAttrConst(CellAttr):
    def __init__(self, value):
        self.value = value
    def fct(self, dummy_line, dummy_cell):
        return self.value
    def js(self):
        return js_str(self.value)
class CellAttrConstDate(CellAttrConst):
    def fct(self, dummy_line, dummy_cell):
        return get_relative_date(self.value)
    def js(self):
        return "get_relative_date(" + js_str(self.value) + ")"

class CellAttrConstSeconds(CellAttr):
    def fct(self, dummy_line, dummy_cell):
        return seconds_to_date()
    def js(self):
        return "seconds_to_date()"

class CellAttrAsDate(CellAttr):
    def __init__(self, cellattr):
        self.cellattr = cellattr
    def fct(self, line, cell):
        return user_date_to_date(self.cellattr.fct(line, cell))
    def js(self):
        return "user_date_to_date(" + self.cellattr.js() + ')'
class CellAttrAsFloat(CellAttrAsDate):
    def fct(self, line, cell):
        return to_float_or_nan(self.cellattr.fct(line, cell))
    def js(self):
        return "to_float_or_nan(" + self.cellattr.js() + ')'
class CellAttrAsString(CellAttrAsDate):
    def fct(self, line, cell):
        return str(self.cellattr.fct(line, cell))
    def js(self):
        return self.cellattr.js() + '.toString()'
class CellAttrAsLower(CellAttrAsDate):
    def fct(self, line, cell):
        return self.cellattr.fct(line, cell).lower()
    def js(self):
        return self.cellattr.js() + '.toLowerCase()'
class CellAttrAsFlat(CellAttrAsDate):
    def fct(self, line, cell):
        return flat(self.cellattr.fct(line, cell))
    def js(self):
        return "flat(" + self.cellattr.js() + ')'
class CellAttrAsFixed(CellAttrAsDate):
    def fct(self, line, cell):
        return as_fixed(self.cellattr.fct(line, cell))
    def js(self):
        return "as_fixed(" + self.cellattr.js() + ")"
class CellAttrTruncate(CellAttr):
    def __init__(self, cellattr, length):
        self.cellattr = cellattr
        self.length = length
    def fct(self, line, cell):
        return self.cellattr.fct(line, cell)[:self.length]
    def js(self):
        return self.cellattr.js() + ".substr(0," + str(self.length) + ')'
class CellAttrAppend(CellAttr):
    def __init__(self, cellattr, value):
        self.cellattr = cellattr
        self.value = value
    def fct(self, line, cell):
        return self.cellattr.fct(line, cell) + self.value
    def js(self):
        return '(' + self.cellattr.js() + '+' + js_str(self.value) + ')'


class FilterNegate:
    # The negation node in the filter tree"""
    def __init__(self, node):
        self.node = node
    def evaluate(self, line, cell):
        return not self.node.evaluate(line, cell)
    def js(self):
        return '!' + self.node.js()

class FilterTrue:
    # True
    def evaluate(self, line, cell):
        return True
    def js(self):
        return 'true'

class FilterFalse:
    # False
    def evaluate(self, line, cell):
        return False
    def js(self):
        return 'false'

def search_operator(string):
    for operator in filterOperators:
        if string.startswith(operator[0]):
            return string[len(operator[0]):], operator
    return string, operator

class FilterAny:
    operator = None
    data_col_left = None
    data_col_right = None
    def evaluate(self, line, cell):
        return self.python(self.left.fct(line, cell),
                           self.right.fct(line, cell))

    def js(self):
        return self.js_string(self.left.js(), self.right.js())

class FilterDate(FilterAny):
    def __init__(self, operator, what, value, column_type, left):
        if operator[0] == '':
            dummy, operator = search_operator('=')
        self.left = left
        if what != "date":
            self.left = CellAttrAsDate(self.left)
        if is_a_relative_date(value):
            dummy, operator = search_operator(operator[3])
            self.right = CellAttrConstDate(value)
        else:
            value = user_date_to_date(value)
            self.left = CellAttrTruncate(self.left, len(value))
            self.right = CellAttrConst(value)
        self.operator = operator

class FilterFloat(FilterAny):
    def __init__(self, operator, value, column_type, left):
        self.left = CellAttrAsFloat(left)
        self.right = CellAttrConst(value)

class FilterStr(FilterAny):
    def __init__(self, operator, value, column_type, left):
        self.left = CellAttrAsString(left)
        value_lower = value.lower()
        hide_upper = value_lower == value  or  not contextual_case_sensitive
        if hide_upper:
            value = value_lower
            self.left = CellAttrAsLower(self.left)

        value_flat = flat(value)
        hide_diacritics = (value_flat == value
                           or operator[0] == '<'
                           or operator[0] == '>'
                           )
        if hide_diacritics:
            value = value_flat
            self.left = CellAttrAsFlat(self.left)

        self.right = CellAttrConst(value)

class FilterAnyStr(FilterAny):
    def __init__(self, operator, what_right, data_col, value, column_type,
                 left, username=""):
        if data_col >= 0:
            self.right = CellAttrAsString(CellAttrOther(data_col, what_right))
        else:
            if what_right == 'author':
                self.right = CellAttrConst(username)
            else:
                # Undefined behavior
                self.right = CellAttrConst('')
        if value:
            self.right = CellAttrAppend(self.right, value)
        self.right = CellAttrAsFlat(CellAttrAsLower(self.right))
        self.left = CellAttrAsFlat(CellAttrAsLower(left))

class FilterAnyDate(FilterAny):
    def __init__(self, operator, what, what_right, data_col, column_type, left):
        if what_right == 'date' and data_col >= 0:
            self.right = CellAttrOther(data_col, what_right)
        elif what_right == 'date':
            self.right = CellAttrConstSeconds()
        else:
            self.right = CellAttrAsDate(CellAttrOther(data_col, what_right))

        self.left = left
        if what != 'date':
            self.left = CellAttrAsDate(self.left)

class FilterAnyType(FilterAny):
    def __init__(self, operator, what_right, data_col, column_type, left):
        self.right = CellAttrOther(data_col, what_right)
        self.left = left
        if operator[0] == '=':
            self.js_oper = "=="
        else:
            self.js_oper = operator[0]

    def evaluate(self, line, cell):
        left = to_float_or_nan(self.left.fct(line, cell))
        if not isNaN(left):
            right = to_float_or_nan(self.right.fct(line, cell))
            if isNaN(right):
                right = -1e50
            return self.python(left, right)
        right = to_float_or_nan(self.right.fct(line, cell))
        if isNaN(right):
            return self.python(flat(str(self.left.fct(line, cell)).lower()),
                               flat(str(self.right.fct(line, cell)).lower()))
        left = -1e50
        return self.python(left, right)

    def js(self):
        left = self.left.js()
        right = self.right.js()
        return (
            "((isNaN(to_float_or_nan(" + left
            + ')) && isNaN(to_float_or_nan(' + right
            + '))) ? '
            + "flat(" + left  + ".toString().toLowerCase())"
            + self.js_oper
            + "flat(" + right  + ".toString().toLowerCase())"
            + ":to_float_or_small(" + left + ')'
            + self.js_oper
            + "to_float_or_small(" + right + '))'
            )


def FilterOperator(operator, what, value, column_type,
                   left, username, errors, columns):
    if value and value[0] in filterAttributes:
        what_right = filterAttributes[value[0]]
        elsewhere = from_another_column(value[1:], errors, columns)
    else:
        what_right = "value"
        elsewhere = from_another_column(value, errors, columns)
    if elsewhere is None:
        if (operator[0] == "~"
            or (operator[0] == "" and what != "date")
            or what == "history"
            or (value == '' and (what == 'value' or what == 'comment'))
        ):
            f = FilterStr(operator, str(value), column_type, left)
        elif what == 'date' or (column_type == 'Date' and what == "value"):
            f = FilterDate(operator, what, str(value), column_type, left)
        else:
            try:
                f = FilterFloat(operator, to_float(value), column_type, left)
            except:
                f = FilterStr(operator, str(value), column_type, left)
    else:
        data_col, string = elsewhere
        if data_col == -1:
            if what_right == 'author':
                f = FilterAnyStr(operator, what_right, -1, string,
                                 column_type, left, username)
            elif what_right == 'date':
                f = FilterAnyDate(operator, what, what_right, -1, column_type,
                                  left)
            else:
                return FilterFalse()
        elif operator[0] == "~" or operator[0] == "" or string != "":
            f = FilterAnyStr(operator, what_right, data_col, string,
                             column_type, left)
        elif what == 'date' or  (column_type == 'Date' and what == "value"):
            f = FilterAnyDate(operator, what,what_right, data_col, column_type,
                              left)
        else:
            f = FilterAnyType(operator, what_right, data_col, column_type,
                              left)
        if data_col >= 0:
            f.data_col_right = data_col

    if f.operator is None:
        f.operator = operator
    f.python = f.operator[1]
    f.js_string = f.operator[2]
    return f

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

def from_another_column(string, errors, columns):
    if not string.startswith('['):
        return None
    s = string.split(']')
    if len(s) == 1:
        return None
    if s[0][1:] == '':
        return -1, string[len(s[0])+1:]
    data_col = data_col_from_col_title(s[0][1:], columns)
    if data_col or data_col == 0:
        return data_col, string[len(s[0])+1:]
    errors["«" + s[0][1:] + '» ' + _("ALERT_url_import_column")] = True
    return None

class Filter:
    # Parse the filter to create a list of nodes
    def __init__(self, string, username, column_type, the_columns=None):
        if the_columns is None:
            try:
                the_columns = columns # Global value for JavaScript
            except:
                the_columns = None # Home page
        self.errors = {}
        self.string = string
        while string.startswith(" "):
            string = string[1:]
        if string == '':
            self.filters = [[FilterTrue()]]
            return
        self.filters = [] # 'ORed' list of 'ANDed' items
        # OR is replaced by its translation
        string = replace_all(string," " + or_keyword() + " ", " | ")
        mode = "|"
        while string:
            node, string = self.parse(string, username, column_type,
                                      the_columns)
            if mode == '|':
                self.filters.append([node])
            else:
                self.filters[-1].append(node)
            if len(string) and (string[0] == '|' or string[0] == '&'):
                mode = string[0]
                string = string[1:].lstrip()
            else:
                mode = '&'

    def parse(self, string, username, column_type, columns):
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
        elsewhere = from_another_column(string, self.errors, columns)
        if elsewhere is None:
            left = CellAttrCell(attr)
            if attr == 'value':
                left = CellAttrAsFixed(left)
        else:
            data_col, string = elsewhere
            if data_col == -1:
                if attr == 'author':
                    left = CellAttrConst(username)
                elif attr == 'date':
                    left = CellAttrConstSeconds()
                else:
                    return FilterFalse(), ''
            else:
                left = CellAttrOther(data_col, attr)
                if attr == 'value':
                    left = CellAttrAsFixed(left)
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
                    and next_char not in '&|@#:?<>=~!['
                    and negate == False
                    and elsewhere is None
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

        node = FilterOperator(operator, attr, value, column_type,
                              left, username, self.errors, columns)

        if elsewhere is not None and elsewhere[0] >= 0:
            node.data_col_left = elsewhere[0]

        if negate:
            node = FilterNegate(node)

        return node, string[i:].lstrip()

    def evaluate(self, line, cell):
        result = False
        for f in self.filters:
            bad = False
            for ff in f:
                if not ff.evaluate(line, cell):
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
                value = js(line, cell)
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
        f = eval('(function x(line, cell) { return ' + self.js() + ';})')
        f.errors = self.get_errors()
        f.filter = self.string
        return f

    def get_errors(self):
        s = ""
        for i in self.errors:
            s += i + "<br>\n"
        if s != "":
            return s

    def other_data_col(self):
        cols = []
        for ored in self.filters:
            for f in ored:
                if f.data_col_left not in cols:
                    cols.append(f.data_col_left)
                if f.data_col_right not in cols:
                    cols.append(f.data_col_right)
        cols = [i
                for i in cols
                if i or i == 0
                ]
        cols.sort()
        return cols
