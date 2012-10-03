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

"""
The forms may use column comments to compute number of lines and color.

To do so, add to the column comment:

     ///Number_Of_Line 3HexaDigitColor

for exemple, 10 lines green :

    my column comment ///10 8F8

"""


from ..column import TableAttr

class TableForms(TableAttr):
    name = 'forms'
    default_value = 1
    action = "table_forms"
    gui_display = "GUI_a"
    css = '''
.tableform {
   position: absolute ;
   background: #DDD ;
   border: 2px solid black;
   overflow: hidden ;
   z-index: 30 ; /* Above tips */
}

.tableform DIV.formtable {
   overflow: auto ;
}

.tableform TABLE {
   width: 100% ;
   border-spacing: 0px ;
}
.tableform TABLE TR {
  vertical-align: top ;
}

.tableform TABLE TD {
  border-top: 1px solid black ;
}

.tableform .ctitle {
  width: 25% ;
}

.tableform TR.ro TEXTAREA, .tableform TR.ro INPUT {
   background-color: #DDD ;
}

.tableform TEXTAREA:focus, BODY.tomuss .tableform INPUT:focus {
  border: 3px solid #00F ;
  padding: 0px ;
}

.tableform TEXTAREA, BODY.tomuss .tableform INPUT {
  border: 1px solid black ;
  padding: 2px ;
  margin: 1px ;
}

.tableform TD IMG {
   float: right;
   height: 1em;
   width: 1em;
   right: 0px;
 }

.tableform TEXTAREA, .tableform INPUT {
   background: white ;
   width: 100% ;
}
BODY.tomuss .tableform H1 { text-align: center; font-size: 140%; }

.tableform .close { float: right ; }

TABLE#thetable TR.currentformline TD {
    background-color: #000 ;
    color: #FFF ;
 }




'''
