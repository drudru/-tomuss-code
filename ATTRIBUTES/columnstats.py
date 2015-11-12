#!/bin/env python3
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

from . import columnfill

class ColumnStats(columnfill.ColumnFill):
    name = "stats"
    action = "update_histogram"
    gui_display = "GUI_none"

    css = '''
#menutop #t_column_stats {
  width: 100% ;
  table-layout: fixed;
  border-top: 1px solid black;
  border-bottom: 1px solid black;
  border-spacing: 0px ;
  height: 1em ;
  font-size: 125% ; /* Revert the 80% */
}

#menutop #t_column_stats TR {
  vertical-align: bottom ;
}

#t_column_stats TD.m { width: 5em ; }

#menutop #t_column_stats TD {
  white-space: nowrap ;
  padding: 0px ;
}

#menutop #t_column_histogram { 
  height: 1.2em ;
}

#menutop #t_column_histogram SVG {
/*  height: 1.3 em ; */
 }
'''


