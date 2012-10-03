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

from ..column import ColumnAttr

class ColumnFill(ColumnAttr):
    name = "fill"
    gui_display = "GUI_a"
    need_authorization = 0
    action = "fill_column"
    default_value = 1
    check_and_set = 'function() { return 1; }'
    css = """
    DIV.fill_column_div { border: 4px solid red ; }
    #stop_the_auto_save { float:right; font-size:70%; border:1px solid red}
    DIV.fill_column_div BUTTON, DIV.fill_column_div SELECT { font-size: 100% }
    DIV.fill_column_div TEXTAREA { height: 5em }
    #tablefill { font-size: 100%; }
    #tablefill SPAN, #tablefill .content { padding: 3px }
    #tablefill .contents { margin-top: 3px; height: 10.1em }
    #tablefill DIV.titles SPAN:first-child { font-weight: normal }
    #tablefill TEXTAREA { height: 5em }
    #tablefill INPUT { width: 100% }
    """
