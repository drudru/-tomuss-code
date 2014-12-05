# -*- coding: utf-8 -*-
# TOMUSS: The Online Multi User Simple Spreadsheet
# Copyright (C) 2014 Thierry EXCOFFIER, Universite Claude Bernard
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Contact: Thierry.EXCOFFIER@univ-lyon1.fr

"""
"""

def compute_diff_date(data_col, line):
    column = columns[data_col]
    
    if len(column.average_columns) != 2:
        return

    # The column comment give the time divisor.
    # If it contains /7 then the difference is computed in weeks
    div = column.comment.split('/')
    if len(div) == 2:
        div = int(div[1])
    else:
        div = 1

    values = []
    for dc in column.average_columns:
        value = line[dc].value
        col = columns[dc]
        if str(value) == '':
            value = col.empty_is
        values.append(date_to_seconds(user_date_to_date(value)))

    try:
        line[data_col] = line[data_col].set_value(
            (values[1] - values[0])/(div*86400))
    except:
        line[data_col] = line[data_col].set_value('')
