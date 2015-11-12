#!/bin/env python3
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2008-2013 Thierry EXCOFFIER, Universite Claude Bernard
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

from . import columngreen

class ColumnRed(columngreen.ColumnGreen):
    name = 'red'
    check_and_set = 'set_red'
    css = """
#menutop DIV.tabs #t_column_red, #menutop DIV.tabs #t_column_green,
#menutop DIV.tabs #t_column_redtext, #menutop DIV.tabs #t_column_greentext
{
 width: 25% ;
}
#t_column_red.empty, #t_column_green.empty,
#t_column_redtext.empty, #t_column_greentext.empty
{
  background-image: url('filtre2.png');
  background-repeat: no-repeat;
  background-position: 2px 2px;
}
    """
