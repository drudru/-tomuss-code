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

class ColumnStats(ColumnFill):
    name = "stats"
    tip = """Histogramme des valeurs des cellules de la colonne<br>
    en tenant compte du filtrage.<br>
    Les colonnes de gauche indiquent le nombre de cases<br>
    contenant des valeurs particulières :<br>
    PPN, ABI, ABJ, PRE, OUI, NON et vide"""
    action = "update_histogram"
    gui_display = "GUI_none"
    title = '''
<table id="t_column_stats">
<tr>
<td>
<script>
hidden('<div id="t_column_histogram"></div>', 'HISOT')
</script>
</td><td class="m">
<script>
hidden('<div id="t_column_average"></div>',
       "Moyenne des nombres de la colonne.")
</script>
</td></tr></table>'''

    css = '''
#menutop #t_column_stats {
  width: 100% ;
  table-layout: fixed;
  border: 1px solid black;
  border-spacing: 0px ;
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
  height: 1.5em ;
}

#menutop #t_column_histogram SVG {
  height: 1.5em ;
 }
'''


