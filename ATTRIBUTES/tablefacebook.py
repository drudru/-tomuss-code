#!/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2011-2014 Thierry EXCOFFIER, Universite Claude Bernard
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

from ..column import TableAttr

class TableFaceBook(TableAttr):
    name = "facebook"
    gui_display = "GUI_button"
    need_authorization = 0
    action = "tablefacebook"
    css = '''
DIV.facebook {
  border: 1px solid #888 ;
  display: block ;
  float: left;
  padding: 1px ;
  border-spacing: 0px ;
  background-color: inherit ;
  height: 12.5em;
  width: 8em ;
  margin: 2px ;
  overflow: hidden;
  position: relative;
}
DIV.facebook DIV.items {
    position: absolute;
    top: 0em;
    right: 0em ;
    left: 0em ;
    }
DIV.facebook DIV.content {
    bottom: 0px ;
    position: absolute;
    }
DIV.facebook DIV.item { opacity: 0.3; right: 0; height: 1em }
DIV.facebook DIV.selecteditem { opacity: 0.7; }
DIV.facebook SPAN { float: left }
DIV.facebook SPAN IMG { width: 0.5em; height: 0.5em }
DIV.facebook IMG.pic {
  width: 8em ;
  border: 0 ;
}

DIV.import_export.phone_facebook { left: 5%; right: 5% ; top: 5% ; height: 90%; }

@media print { DIV.facebook { font-size: 75% ; } }
'''



