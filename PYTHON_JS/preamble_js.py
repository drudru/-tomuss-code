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

python_mode = False

# For RapydScript:

if "console" not in window:
    window.console = console

try:
    javascript
except:
    # javascript decorator is only used by PythonJS translator
    javascript = def(x): return x

try:
    str
except:
    str = def(x): return "" + x

try:
    "".join([])
except:
    def __join__(t):
        return t.join(this)
    String.prototype.join = __join__

try:
    "".strip()
except:
    String.prototype.strip = String.prototype.trim

try:
    "".lstrip()
except:
    if String.prototype.trimLeft:
        String.prototype.lstrip = String.prototype.trimLeft
    else:
        def __trimLeft__():
            i = 0
            while this[i] == ' ':
                i += 1
            return this[i:]
        String.prototype.lstrip = __trimLeft__

try:
    "".startswith("")
except:
    def __startswith__(t):
        return this.substr(0, len(t)) == t
    String.prototype.startswith = __startswith__

try:
    "".find("")
except:
    String.prototype.find = String.prototype.indexOf

try:
    "".lower()
except:
    String.prototype.lower = String.prototype.toLowerCase

try:
    [].append(0)
except:
    o = Object
    o.defineProperty(Array.prototype, 'append' ,
                          {'enumerable': False,'value': Array.prototype.push}) ;

try:
    {}.get("p", "m")
except:
    def __getter__(key, defaultv):
        if this[key] is undefined:
            return defaultv
        return this[key]
    o = Object
    o.defineProperty(Object.prototype, 'get' ,
                          {'enumerable': false, 'value': __getter__}) ;

def replace_all(txt, regexp, value):
    return txt.replace(RegExp(regexp, "g"), value)

def js_str(txt):
    return JSON.stringify(txt)

##############################################################################
#
# Not easely writable in Python
#
##############################################################################


flat_map = '\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0¡¢£¤¥¦§¨©ª«¬­®¯°±²³´µ¶·¸¹º»¼½¾¿AAAAAAACEEEEIIIIDNOOOOOOOUUUUYÞßaaaaaaaceeeeiiiiðnooooooouuuuyþy'

def or_keyword():
    return _('or')

@javascript
def char_flat(c):
    return flat_map.substr(c.charCodeAt(0),1)

@javascript
def flat(txt):
    return txt.replace(RegExp('[\\x80-\\xFF]', 'g'), char_flat)

unicode = str

def update_today():
    year_month_day = new(Date)
    current_seconds = year_month_day.getTime()/1000
    year_month_day = [year_month_day.getFullYear(),
                      year_month_day.getMonth() + 1,
                      year_month_day.getDate()]
    return current_seconds, year_month_day

def seconds_to_date(seconds):
    d = new(Date)
    d.setTime(seconds * 1000)
    return (d.getFullYear() + two_digits(d.getMonth()+1)
            + two_digits(d.getDate()) + two_digits(d.getHours())
            + two_digits(d.getMinutes()) + two_digits(d.getSeconds()) )

def date_to_seconds(date):
    return get_date_tomuss(date).getTime() / 1000

def REsplit(expreg, txt):
    return txt.split(RegExp(expreg))

def to_float_or_nan(txt):
    try:
        return Number.prototype.constructor(txt.replace(',', '.'))
    except:
        return Number.prototype.constructor(txt)

def to_float(txt):
    n = to_float_or_nan(txt)
    if isNaN(n):
        raise ValueError("not float")
    return n

rint = Math.round
ceil = Math.ceil
