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
    column_change = table.column_change
    column_comment = table.column_comment
    cell_change = table.cell_change

    p = new_page('' ,data.ro_user, '', '')
    column_change(p,'0_0','ID','Text','','','F',0,4)
    column_change(p,'0_1','Pr\xc3\xa9nom','Text','','','F',0,8)
    column_change(p,'0_2','Nom','Text','','','F',0,8)
    column_change(p,'0_3','Grp','Text','','','',0,1)
    column_change(p,'0_4','Seq','Text','','','',0,1)
    column_change(p,'0_5','Inscrit','Text','','','C',1,1)
    column_change(p,'1_0','S\xc3\xa9ance1','Note','[0;20]','1','',0,4)
    cell_change(p,'1_0','1_0',10.0,"20080716161115")
    column_change(p,'1_1','S\xc3\xa9ance2','Note','[0;20]','1','',0,4)
    column_change(p,'1_1','S\xc3\xa9ance2','Note','[0;10]','1','',0,4)
    cell_change(p,'1_1','1_0',5.0,"20080716161126")
    column_change(p,'1_2','S\xc3\xa9ance3','Moy','[0;20]','1','',0,4)
    column_change(p,'1_2','S\xc3\xa9ance3','Moy','[0;20]','1 S\xc3\xa9ance1 S\xc3\xa9ance2','',0,4)
    column_change(p,'1_2','S\xc3\xa9ance3','Moy','[0;40]','1 S\xc3\xa9ance1 S\xc3\xa9ance2','',0,4)
    cell_change(p,'1_0','1_1','ABINJ',"20080716161204")
    cell_change(p,'1_1','1_1',5.0,"20080716161209")
    cell_change(p,'1_0','1_2','ABJUS',"20080716161218")
    cell_change(p,'1_1','1_2',5.0,"20080716161219")
    cell_change(p,'1_0','1_3','ABINJ',"20080716161224")
    cell_change(p,'1_1','1_3','ABINJ',"20080716161226")
    cell_change(p,'1_0','1_4','ABINJ',"20080716161231")
    cell_change(p,'1_1','1_4','ABJUS',"20080716161232")
    cell_change(p,'1_0','1_5','ABJUS',"20080716161240")
    cell_change(p,'1_1','1_5','ABJUS',"20080716161241")
    cell_change(p,'1_1','1_6',5.0,"20080716161303")
    cell_change(p,'1_1','1_7','ABINJ',"20080716161306")
    cell_change(p,'1_1','1_8','ABJUS',"20080716161308")
    column_change(p,'2_0','S\xc3\xa9ance1','Note','[0;20]','1','',0,4)
    column_change(p,'2_0','S\xc3\xa9ance1','Note','[0;20]','2','',0,4)
    cell_change(p,'2_0','1_0',13.0,"20080716161604")
    column_change(p,'2_1','S\xc3\xa9ance2','Moy','[0;20]','1','',0,4)
    column_change(p,'2_1','S\xc3\xa9ance2','Moy','[0;20]','1 S\xc3\xa9ance3 S\xc3\xa9ance4','',0,4)
    column_change(p,'2_0','S\xc3\xa9ance4','Note','[0;20]','2','',0,4)
    column_change(p,'2_1','S\xc3\xa9ance22','Moy','[0;20]','1 S\xc3\xa9ance3 S\xc3\xa9ance4','',0,4)
    cell_change(p,'0_5','1_7','non',"20080716161804")
    cell_change(p,'0_5','1_6','non',"20080716161804")
    cell_change(p,'0_5','1_5','non',"20080716161804")
    cell_change(p,'0_5','1_4','non',"20080716161804")
    cell_change(p,'0_5','1_3','non',"20080716161804")
    cell_change(p,'0_5','1_2','non',"20080716161804")
    cell_change(p,'0_5','1_1','non',"20080716161804")
    cell_change(p,'0_5','1_0','non',"20080716161804")
    cell_change(p,'0_5','1_8','non',"20080716161804")
    cell_change(p,'2_0','1_5',13.0,"20080716161814")
    cell_change(p,'2_0','1_6',13.0,"20080716161815")
    cell_change(p,'2_0','1_6','ABJUS',"20080716161826")
    cell_change(p,'2_0','1_6',13.0,"20080716161830")
    cell_change(p,'2_0','1_4','ABINJ',"20080716161837")
    cell_change(p,'2_0','1_3','ABJUS',"20080716161840")
    cell_change(p,'2_0','1_2',13.0,"20080716161851")
    cell_change(p,'2_0','1_1',13.0,"20080716161852")
    cell_change(p,'2_0','1_7','PPNOT',"20080716161912")
    cell_change(p,'2_0','1_2','PPNOT',"20080716161921")
    cell_change(p,'2_0','1_8',13.0,"20080716161928")
    column_change(p,'4_0','COMPARER','Text','','','',0,4)
    cell_change(p,'4_0','1_5','13',"20080716161944")
    cell_change(p,'4_0','1_6','NaN',"20080716161947")
    cell_change(p,'4_0','1_4','0',"20080716161951")
    cell_change(p,'4_0','1_3','0',"20080716161952")
    cell_change(p,'4_0','1_2','10',"20080716161957")
    cell_change(p,'4_0','1_1','10.33',"20080716161959")
    cell_change(p,'4_0','1_0','12',"20080716162000")
    cell_change(p,'4_0','1_7','NaN',"20080716162003")
    cell_change(p,'4_0','1_8','NaN',"20080716162005")
    cell_change(p,'1_0','5_0','PPNOT',"20080716162232")
    cell_change(p,'1_1','5_0','PPNOT',"20080716162256")
    cell_change(p,'2_0','5_0',13.0,"20080716162303")
    cell_change(p,'4_0','5_0','13',"20080716162316")
    cell_change(p,'1_0','5_1','ABJUS',"20080716162328")
    cell_change(p,'1_1','5_1','PPNOT',"20080716162340")
    cell_change(p,'2_0','5_1',13.0,"20080716162346")
    cell_change(p,'4_0','5_1','13',"20080716162350")
    column_change(p,'1_0','Note1','Note','[0;20]','1','',0,4)
    column_change(p,'1_2','S\xc3\xa9ance3','Moy','[0;40]','1 Note1 S\xc3\xa9ance2','',0,10)
    column_change(p,'1_1','Note2','Note','[0;10]','1','',0,4)
    column_change(p,'1_2','S\xc3\xa9ance3','Moy','[0;40]','1 Note1 Note2','',0,10)
    column_change(p,'1_2','Moyenne1','Moy','[0;40]','1 Note1 Note2','',0,10)
    column_change(p,'2_0','Note3','Note','[0;20]','2','',0,4)
    column_change(p,'2_1','S\xc3\xa9ance22','Moy','[0;20]','1 Moyenne1 Note3','',0,10)
    column_change(p,'2_1','Moyenne2','Moy','[0;20]','1 Moyenne1 Note3','',0,10)
    column_change(p,'4_0','BonneR\xc3\xa9ponse','Text','','','',0,8)
    column_change(p,'m3','Moyenne3','Moy','[0;20]','1 Note1 Note2 Note3','',0,10)
    column_comment(p,'m3','Moyenne des 2 meilleurs notes')
    column_change(p,'br3','BonneReponse3','Text','','','',0,10)
    cell_change(p,'br3','1_0',   12,"")
    cell_change(p,'br3','1_1',   12,"")
    cell_change(p,'br3','1_2','NaN',"")
    cell_change(p,'br3','1_3',    0,"")
    cell_change(p,'br3','1_4',    0,"")
    cell_change(p,'br3','1_5','NaN',"")
    cell_change(p,'br3','1_6','NaN',"")
    cell_change(p,'br3','1_7','NaN',"")
    cell_change(p,'br3','1_8','NaN',"")
    cell_change(p,'br3','5_0','NaN',"")
    cell_change(p,'br3','5_1','NaN',"")
