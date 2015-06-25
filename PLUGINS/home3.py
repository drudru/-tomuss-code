#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2015 Thierry EXCOFFIER, Universite Claude Bernard
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

import os
from .. import plugin
from .. import utilities
from .. import inscrits
from .. import configuration
from .. import referent
from .. import document
from .. import files
from .. import display

D = display.Display

files.add('PLUGINS', 'home3.css')
files.add('PLUGINS', 'home3.js')

D('Home'         , []          ,0, js='Vertical')
D('X34X'            , 'Home'      ,0)

def home_page(server):
    display.send_headers(server, "home3.css", "home3.js", "initialize_home3")
    display.data_to_display(server, "Home")

plugin.Plugin('homepage3', '/homepage3/{=}', function=home_page, group='staff',
              launch_thread=True, unsafe=False)
