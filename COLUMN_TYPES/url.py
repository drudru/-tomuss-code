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

import text
import re
import cgi

class URL(text.Text):
    human_priority = 10
    tip_cell = "TIP_cell_URL"
    ondoubleclick = 'follow_url'
    attributes_visible = ('weight',)

    def formatter(self, column, value, cell, lines, teacher, ticket, line_id):
        if value == '':
            return ('', '', '')
        value = str(value).split(' ', 1)
        if len(value) > 1:
            title = value[1]
        else:
            if 'TITLE(' in column.comment:
                title = re.sub(r'.*TITLE\(', '', column.comment)
                title = re.sub(r'\).*', '', title)
            else:
                title = '<script>Write("MSG_URL");</script>'

        if 'BASE(' in column.comment:
            base = re.sub(r'.*BASE\(', '', column.comment)
            base = re.sub(r'\).*', '', base)
        else:
            base = ''


        return ('<a href="%s">%s</a>' % (base + value[0],
                                         cgi.escape(title)), '', '')

