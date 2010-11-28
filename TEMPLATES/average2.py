#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2009 Thierry EXCOFFIER, Universite Claude Bernard
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

import data

def create(table):
    new_page = table.new_page
    column_attr = table.column_attr
    cell_change = table.cell_change
    p = new_page('' ,data.ro_user, '', '')

    column_attr(p,'_0','title','a')
    column_attr(p,'_1','title','b')
    column_attr(p,'_2','title','c')
    column_attr(p,'_3','title','d')
    column_attr(p,'_4','comment','Elimine le min et le max ]1,1[')
    column_attr(p,'_4','title','Moyenne')
    column_attr(p,'_4','columns','a b c d')
    column_attr(p,'_4','type','Moy')
    column_attr(p,'_5','title','BonneR\xc3\xa9ponse')
    cell_change(p,'_0','*17_1','ABJUS','')
    cell_change(p,'_1','*17_1','ABJUS','')
    cell_change(p,'_2','*17_1','ABJUS','')
    cell_change(p,'_3','*17_1','ABJUS','')
    cell_change(p,'_0','*9_9','ABINJ','')
    cell_change(p,'_1','*9_9','ABINJ','')
    cell_change(p,'_2','*9_9','ABINJ','')
    cell_change(p,'_3','*9_9',4.0,'')
    cell_change(p,'_5','*9_9',0.0,'')
    cell_change(p,'_0','*9_8',1.0,'')
    cell_change(p,'_1','*9_8','ABINJ','')
    cell_change(p,'_2','*9_8','ABJUS','')
    cell_change(p,'_3','*9_8',4.0,'')
    cell_change(p,'_5','*9_8',1.0,'')
    cell_change(p,'_0','*2_0','ABINJ','')
    cell_change(p,'_1','*2_0',2.0,'')
    cell_change(p,'_2','*2_0',3.0,'')
    cell_change(p,'_3','*2_0',4.0,'')
    cell_change(p,'_5','*2_0',2.5,'')
    cell_change(p,'_0','*9_6',1.0,'')
    cell_change(p,'_1','*9_6',2.0,'')
    cell_change(p,'_2','*9_6','ABINJ','')
    cell_change(p,'_3','*9_6','ABINJ','')
    cell_change(p,'_5','*9_6',0.5,'')
    cell_change(p,'_0','*9_5','ABINJ','')
    cell_change(p,'_1','*9_5','ABINJ','')
    cell_change(p,'_2','*9_5',3.0,'')
    cell_change(p,'_3','*9_5',4.0,'')
    cell_change(p,'_5','*9_5',1.5,'')
    cell_change(p,'_0','*9_4',1.0,'')
    cell_change(p,'_1','*9_4','ABJUS','')
    cell_change(p,'_2','*9_4',3.0,'')
    cell_change(p,'_3','*9_4',4.0,'')
    cell_change(p,'_5','*9_4',3.0,'')
    cell_change(p,'_0','*9_3',1.0,'')
    cell_change(p,'_1','*9_3',2.0,'')
    cell_change(p,'_2','*9_3',3.0,'')
    cell_change(p,'_3','*9_3','ABJUS','')
    cell_change(p,'_5','*9_3',2.0,'')
    cell_change(p,'_0','*9_2','ABJUS','')
    cell_change(p,'_1','*9_2',2.0,'')
    cell_change(p,'_2','*9_2',3.0,'')
    cell_change(p,'_3','*9_2',4.0,'')
    cell_change(p,'_5','*9_2',3.0,'')
    cell_change(p,'_0','*9_1',1.0,'')
    cell_change(p,'_1','*9_1','ABINJ','')
    cell_change(p,'_2','*9_1',3.0,'')
    cell_change(p,'_3','*9_1',4.0,'')
    cell_change(p,'_5','*9_1',2.0,'')
    cell_change(p,'_0','*9_0',1.0,'')
    cell_change(p,'_1','*9_0',2.0,'')
    cell_change(p,'_2','*9_0',3.0,'')
    cell_change(p,'_3','*9_0','ABINJ','')
    cell_change(p,'_5','*9_0',1.5,'')
    cell_change(p,'_0','*9_7',1.0,'')
    cell_change(p,'_1','*9_7','ABINJ','')
    cell_change(p,'_2','*9_7','ABINJ','')
    cell_change(p,'_3','*9_7',4.0,'')
    cell_change(p,'_5','*9_7',0.5,'')
    cell_change(p,'_0','*9_11','ABINJ','')
    cell_change(p,'_1','*9_11','ABJUS','')
    cell_change(p,'_2','*9_11','ABJUS','')
    cell_change(p,'_3','*9_11',4.0,'')
    cell_change(p,'_5','*9_11','PPNOT','')
    cell_change(p,'_0','*9_10','ABJUS','')
    cell_change(p,'_1','*9_10','ABJUS','')
    cell_change(p,'_2','*9_10','ABJUS','')
    cell_change(p,'_3','*9_10',4.0,'')
    cell_change(p,'_0','*17_0','ABINJ','')
    cell_change(p,'_1','*17_0','ABINJ','')
    cell_change(p,'_2','*17_0','ABJUS','')
    cell_change(p,'_3','*17_0',4.0,'')
    cell_change(p,'_5','*17_0',0.0,'')
    cell_change(p,'_0','*1_0',1.0,'')
    cell_change(p,'_1','*1_0',2.0,'')
    cell_change(p,'_2','*1_0',3.0,'')
    cell_change(p,'_3','*1_0',4.0,'')
    cell_change(p,'_5','*1_0',2.5,'')
    cell_change(p,'_0','*21_0','ABJUS','')
    cell_change(p,'_1','*21_0','ABJUS','')
    cell_change(p,'_2','*21_0',3.0,'')
    cell_change(p,'_3','*21_0',4.0,'')
    cell_change(p,'_5','*21_0','PPNOT','')
