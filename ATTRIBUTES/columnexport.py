#!/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2011 Thierry EXCOFFIER, Universite Claude Bernard
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

from columnfill import ColumnFill

class ColumnExport(ColumnFill):
    name = "export"
    action = "export_column"
    css = """

DIV.export_div { 
  border: 4px solid green ;
}

/* Also used by 'import' */

DIV.import_export { 
  position: absolute;
  left: 10%;
  right: 10%;
  top: 25%;
  padding: 0.5em ;
  z-index: 10;
}
DIV.import_export TEXTAREA { 
  width: 100%;
}

DIV.import_export, DIV#import_export P  { 
  background-color: #DDD ;
}

DIV.import_export H2 { margin: 0px ; }


DIV.import_export BUTTON.close { 
  position:absolute;
  right:0px;
  top: 0px;
}
DIV.import_export UL { 
margin-top: 0px ;
margin-bottom: 0px ;
 }

DIV.import_export PRE { 
margin: 0px ;
margin-left: 1em ;
 }

DIV.import_export TD { width: 50% }
DIV.import_export TABLE { width: 100% ; }

"""
