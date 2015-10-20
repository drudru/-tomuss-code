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

import time
import re
import sys
import math
import os # Really needed

python_mode = True

def replace_all(txt, regexp, value):
    return txt.replace(regexp, value)

def js_str(txt):
    return '"' + txt.replace("\\", "\\\\").replace('"', '\\"') + '"'

# print "".join("\\x%02x" % i for i in range(256))


flat_map = u'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0¡¢£¤¥¦§¨©ª«¬­®¯°±²³´µ¶·¸¹º»¼½¾¿AAAAAAACEEEEIIIIDNOOOOOOOUUUUYÞßaaaaaaaceeeeiiiiðnooooooouuuuyþy'


def flat(txt):
    return txt.translate(flat_map)

try:
    _ = sys.modules['TOMUSS.utilities']._
except KeyError:
    try:
        _ = __import__('utilities')._
    except ImportError:
        _ = lambda x: x

def millisec():
    return time.time() * 1000

def seconds_to_date(seconds):
    return time.strftime('%Y%m%d%H%M%S', time.localtime(seconds))

def date_to_seconds(date):
    return time.mktime(time.strptime(date.ljust(14, '0'), '%Y%m%d%H%M%S'))

localtime = time.localtime

def REsplit(expreg, txt):
    return re.split(expreg, txt)

def to_float(txt):
    try:
        return float(txt.replace(',', '.'))
    except: # Because txt is a float or not a number in a string
        return float(txt)

def to_float_or_nan(txt):
    try:
        return to_float(txt)
    except:
        return nan

def python_pop(array, i):
    array.pop(i)

try:
    from .. import configuration
    def or_keyword():
        return configuration.or_keyword
    def major_of(login):
        return configuration.major_of(login)
except ValueError:
    pass

rint = round
isNaN = math.isnan
ceil = math.ceil
