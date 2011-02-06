#!/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2008,2010 Thierry EXCOFFIER, Universite Claude Bernard
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

import note

class Moy(note.Note):
    human_priority = -8
    full_title = 'Moyenne'
    tip_cell = "Cellule non modifiable"
    tip_columns = """<b>Noms des colonnes à moyenner</b><br>
    Par exemple : <b>td1 td2 td3</b>.<br>
    Le calcul de la note est la somme des<br>
    &nbsp;&nbsp;&nbsp;&nbsp;<em>td<sub>i</sub>.poids * (td<sub>i</sub>.note - td<sub>i</sub>.min) / (td<sub>i</sub>.max - td<sub>i</sub>.min)</em><br>
    divisée par la somme des poids ne commençant pas par <b>+</b> ou <b>-</b><br>
    Il est normalisé dans l'intervalle que vous avez indiqué.<br>
    Il est tenu compte des ABI, ABJ, PPN..."""
    cell_test = 'test_read_only'
    cell_compute = 'compute_average'
    cell_is_modifiable = 0


    def cell_indicator(self, column, value, cell, lines):
        return '', None

    def formatter(self, column, value, cell, lines, teacher, ticket, line_id):
        if column.type == 'Nmbr':
            what = '(' + column.test_filter + ')'
            minmax = '\002'
        else:
            what = ''
            minmax = self.value_range(*column.min_max())

        if teacher:
            more = ' sur les colonnes : <em>' + column.columns + '</em>'
        else:
            # To not leak invisible columns
            more = ''

        comment = ('Calcul effectué: <b>' + self.full_title + what + '</b>'
                   + more )

        return ('\001' + minmax, '', comment)
