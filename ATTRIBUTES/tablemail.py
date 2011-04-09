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

from column import TableAttr

class TableMail(TableAttr):
    name = "mail"
    tip = """Gestion des mails"""
    gui_display = "GUI_button"
    need_authorization = 0
    action = "mail_window"
    title = 'Mails'
    css = '''
DIV.import_export TEXTAREA.mails {
  width: 100% ;
  height: 10em ;
  font-size: 70%;
}

DIV.mails_div .unknown_mails { background: #FF0 ; }
DIV.mails_div, DIV.personal_mailing_div  { border: 4px solid black ; }

DIV.mails_div .popup_input { display: none }

'''



