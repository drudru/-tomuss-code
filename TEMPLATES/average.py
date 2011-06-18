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
    p = table.new_page('' ,data.ro_user, '', '')
    
    column_attr = table.column_attr
    table_attr = table.table_attr
    cell_change = table.cell_change

    column_attr(p,'00','title','ID')
    column_attr(p,'00','freezed','F')
    column_attr(p,'00','type','Text')
    column_attr(p,'00','position',0)
    column_attr(p,'10','title','Note1')
    column_attr(p,'10','position',6)
    column_attr(p,'11','minmax','[0;10]')
    column_attr(p,'11','title','Note2')
    column_attr(p,'11','position',7)
    column_attr(p,'12','minmax','[0;40]')
    column_attr(p,'12','title','Moyenne1')
    column_attr(p,'12','width',10)
    column_attr(p,'12','type','Moy')
    column_attr(p,'12','columns','Note1 Note2')
    column_attr(p,'12','position',8)
    column_attr(p,'20','weight','2')
    column_attr(p,'20','title','Note3')
    column_attr(p,'20','position',9)
    column_attr(p,'21','title','Moyenne2')
    column_attr(p,'21','width',10)
    column_attr(p,'21','type','Moy')
    column_attr(p,'21','columns','Moyenne1 Note3')
    column_attr(p,'21','position',10)
    column_attr(p,'40','title','BonneR\xc3\xa9ponse')
    column_attr(p,'40','width',8)
    column_attr(p,'40','type','Text')
    column_attr(p,'40','position',11)
    column_attr(p,'m3','comment','Moyenne des 2 meilleurs notes')
    column_attr(p,'m3','title','Moyenne3')
    column_attr(p,'m3','width',10)
    column_attr(p,'m3','type','Moy')
    column_attr(p,'m3','columns','Note1 Note2 Note3')
    column_attr(p,'m3','position',12)
    column_attr(p,'br3','title','BonneReponse3')
    column_attr(p,'br3','width',10)
    column_attr(p,'br3','type','Text')
    column_attr(p,'br3','position',13)
    table_attr(p, 'default_nr_columns', 9)
    cell_change(p,'00','50','9','')
    cell_change(p,'10','50','PPNOT','20080716162232')
    cell_change(p,'11','50','PPNOT','20080716162256')
    cell_change(p,'20','50',13.0,'20080716162303')
    cell_change(p,'40','50','13','20080716162316')
    cell_change(p,'br3','50','NaN','')
    cell_change(p,'00','51','10','')
    cell_change(p,'10','51','ABJUS','20080716162328')
    cell_change(p,'11','51','PPNOT','20080716162340')
    cell_change(p,'20','51',13.0,'20080716162346')
    cell_change(p,'40','51','13','20080716162350')
    cell_change(p,'br3','51','NaN','')
    cell_change(p,'00','17','7','')
    cell_change(p,'11','17','ABINJ','20080716161306')
    cell_change(p,'20','17','PPNOT','20080716161912')
    cell_change(p,'40','17','NaN','20080716162003')
    cell_change(p,'br3','17','NaN','')
    cell_change(p,'00','16','6','')
    cell_change(p,'11','16',5.0,'20080716161303')
    cell_change(p,'20','16',13.0,'20080716161830')
    cell_change(p,'40','16','NaN','20080716161947')
    cell_change(p,'br3','16','NaN','')
    cell_change(p,'00','15','5','')
    cell_change(p,'10','15','ABJUS','20080716161240')
    cell_change(p,'11','15','ABJUS','20080716161241')
    cell_change(p,'20','15',13.0,'20080716161814')
    cell_change(p,'40','15','13','20080716161944')
    cell_change(p,'br3','15','NaN','')
    cell_change(p,'00','14','4','')
    cell_change(p,'10','14','ABINJ','20080716161231')
    cell_change(p,'11','14','ABJUS','20080716161232')
    cell_change(p,'20','14','ABINJ','20080716161837')
    cell_change(p,'40','14','0','20080716161951')
    cell_change(p,'br3','14',0,'')
    cell_change(p,'00','13','3','')
    cell_change(p,'10','13','ABINJ','20080716161224')
    cell_change(p,'11','13','ABINJ','20080716161226')
    cell_change(p,'20','13','ABJUS','20080716161840')
    cell_change(p,'40','13','0','20080716161952')
    cell_change(p,'br3','13',0,'')
    cell_change(p,'00','12','2','')
    cell_change(p,'10','12','ABJUS','20080716161218')
    cell_change(p,'11','12',5.0,'20080716161219')
    cell_change(p,'20','12','PPNOT','20080716161921')
    cell_change(p,'40','12','10','20080716161957')
    cell_change(p,'br3','12','NaN','')
    cell_change(p,'00','11','1','')
    cell_change(p,'10','11','ABINJ','20080716161204')
    cell_change(p,'11','11',5.0,'20080716161209')
    cell_change(p,'20','11',13.0,'20080716161852')
    cell_change(p,'40','11','10.33','20080716161959')
    cell_change(p,'br3','11',12,'')
    cell_change(p,'00','10','0','')
    cell_change(p,'10','10',10.0,'20080716161115')
    cell_change(p,'11','10',5.0,'20080716161126')
    cell_change(p,'20','10',13.0,'20080716161604')
    cell_change(p,'40','10','12','20080716162000')
    cell_change(p,'br3','10',12,'')
    cell_change(p,'00','18','8','')
    cell_change(p,'11','18','ABJUS','20080716161308')
    cell_change(p,'20','18',13.0,'20080716161928')
    cell_change(p,'40','18','NaN','20080716162005')
    cell_change(p,'br3','18','NaN','')
