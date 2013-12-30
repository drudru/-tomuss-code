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

"""
"""

debug = False # It is set to True by filter_regtest.py

# Set to True if 'B' filter must not found 'b' value.
# This value must never be changed once table have been created by users
contextual_case_sensitive = False

try:
    #WITHJAVASCRIPT#
    pythonjs.configure(javascript=True)
    #WITHJAVASCRIPT#
    pythonjs.configure(runtime_exceptions=False)
    pass
except:
    pass

flat_map = u'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0¡¢£¤¥¦§¨©ª«¬­®¯°±²³´µ¶·¸¹º»¼½¾¿AAAAAAACEEEEIIIIDNOOOOOOOUUUUYÞßaaaaaaaceeeeiiiiðnooooooouuuuyþy'


# print "".join("\\x%02x" % i for i in range(256))

python_mode = hasattr("", 'translate')

if python_mode:
    # Python
    def flat(txt):
        return txt.translate(flat_map)
else:
    @javascript
    def char_flat(c):
        return flat_map.substr(c.charCodeAt(0),1)
    @javascript
    def flat(txt):
        return JS(u'txt.replace(/[\x80-\xFF]/g, char_flat)')

if not python_mode:
    unicode = str

year_month_day = None
current_seconds = None

if python_mode:
    def update_today():
        time = __import__('time')
        global year_month_day
        year_month_day = time.localtime()
        current_seconds = time.time()
else:
    def update_today():
        JS("""year_month_day = new Date() ; year_month_day = [year_month_day.getFullYear(), year_month_day.getMonth() + 1, year_month_day.getDate()] ; current_seconds = new Date() ; current_seconds = current_seconds.getTime()/1000 ;""")

update_today()

if python_mode:
    def seconds_to_date(seconds):
        time = __import__('time')
        return time.strftime('%Y%m%d%H%M%S', time.localtime(seconds))
else:
    def seconds_to_date(seconds):
        d = JS("new Date(seconds * 1000)")
        return (d.getFullYear() + two_digits(d.getMonth()+1)
                + two_digits(d.getDate()) + two_digits(d.getHours())
                + two_digits(d.getMinutes()) + two_digits(d.getSeconds()) )

if python_mode:
    def REsplit(expreg, txt):
        re = __import__('re')
        return re.split(expreg, txt)
else:
    def REsplit(expreg, txt):
        return txt.split(RegExp(expreg))

def js_str(txt):
    return "'" + txt.replace("\\","\\\\").replace("'","\\'") + "'"

def to_float(txt):
    try:
        return float(txt.replace(',', '.'))
    except: # Because txt is a float or not a number in a string
        return float(txt)

def to_float_or_nan(txt):
    try:
        return to_float(txt)
    except:
        if python_mode:
            return float('NaN')
        else:
            return JS("NaN")
    
# Dates are defined as string : YYYYMMDDHHMMSS
# We assume that date are all valid.
# YYYYMM = YYYYMM00000000
# User dates:
#    * Day (current month)
#    * Day/Month (current year)
#    * Day/Month/Year
#    * Date[-_ ]Hour
#    * Date[-_ ]Hour:Minute
#    * Date[-_ ]Hour:Minute:Seconds

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
    try:
        the_month = int(txt[1])
    except:
        the_month = year_month_day[1]
    try:
        the_year = int(txt[2])
    except:
        the_year = year_month_day[0]
    return str(the_year) + two_digits(the_month) + two_digits(the_day) + t

    
class FilterNegate(object):
    """The negation node in the filter tree"""
    def __init__(self, node):
        self.node = node
    def eval(self, cell):
        return not self.node.eval(cell)
    def js(self):
        return '!' + self.node.js()

class FilterTrue(object):
    """True"""
    def eval(self, cell):
        return True
    def js(self):
        return 'true'

class FilterFalse(object):
    """False"""
    def eval(self, cell):
        return False
    def js(self):
        return 'false'

def search_operator(string):
    for operator in filterOperators:
        if string.startswith(operator[0]):
            return string[len(operator[0]):], operator
    return string, operator

class FilterOperator(object):
    """Compare node to a constant in the filter tree"""
    """No inherence possible with PythonJS, so there are no sub classes"""
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
        
    def eval(self, cell):
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
filterOperators = [
    ['<=', lambda a, b: a <= b, lambda a, b: '(' + a + '<=' + b + ')', '>='],
    ['<' , lambda a, b: a < b , lambda a, b: '(' + a + '<'  + b + ')', '>' ],
    ['>=', lambda a, b: a >= b, lambda a, b: '(' + a + '>=' + b + ')', '<='],
    ['>' , lambda a, b: a > b , lambda a, b: '(' + a + '>'  + b + ')', '<' ],
    ['=' , lambda a, b: a == b, lambda a, b: '(' + a + '==' + b + ')', '=' ],
    ['~' ,
     lambda a, b: b in a,
     lambda a, b: '(' + a + '.indexOf('+b+')!=-1)',
     None
     ],
    [''  ,
     lambda a, b: a.startswith(b),
     lambda a, b: '(' + a + '.substr(0,' + b + '.length)==' + b + ')',
     None
     ],
    ]

filterAttributes = {'@': 'author',
                    '#': 'comment',
                    ':': 'history',
                    '?': 'date'}

class Filter(object):
    """Parse the filter to create a list of nodes"""
    def __init__(self, string, username, column_type):
        if string == '':
            self.filters = [('', FilterTrue())]
            return
        self.filters = []
        # __OR__ is replaced by its translation
        string = string.replace(" __OR__ ", " | ").strip()
        mode = ''
        while string:
            string = string.strip()
            node, string = self.parse(string, username, column_type)
            self.filters.append((mode, node))
            if len(string) and (string[0] == '|' or string[0] == '&'):
                mode =  string[0]
                string = string[1:]
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
                if (char == ' '
                    and operator[0] == ''
                    and attr == 'value'
                    and len(string) > i
                    and filterAttributes.get(string[i], '') == '' # the value
                    and search_operator(string[i])[1][0] == ''    # starting by
                    and string[i] not in '&|'
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
                dummy, operator = search_operator('=')
            elif attr == 'comment' or attr == 'history':
                # Special filters : '#' and ':'
                dummy, operator = search_operator('=')                
                negate = not negate

        node = FilterOperator(operator, attr, value, column_type)
        if negate:
            node = FilterNegate(node)
        return node, string[i:]

    def eval(self, cell):
        for f in self.filters:
            if f[0] == '':
                result = f[1].eval(cell)
            elif f[0] == '&':
                result = result and f[1].eval(cell)
            else:
                result = result or f[1].eval(cell)

        if debug:
            error = False
            if not python_mode:
                error = "Can not compile js: " + self.js()
                js = self.compiled_js()
                error = "Can not evaluate compiled filter: " + js
                value = js(cell)
                if value == result:
                    error = False
                else:
                    error = (u"Unexpected value: «" + value
                             + u'» in place of «' + result
                             + u'» for:\n\tcell: ' + cell.js()
                             + '\n\tjs: ' + js + u'»')
            if error:
                raise ValueError(error)

        return result

    def js(self):
        return '(' + ''.join([filter[0] + filter[0] + filter[1].js()
                             for filter in self.filters
                             ]) + ')'

    def compiled_js(self):
        return eval('(function x(cell) { return ' + self.js() + ';})')

