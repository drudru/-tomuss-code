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

from tableexport import TableExport
import utilities
import document
import plugin

class TableCopy(TableExport):
    default_value = 1
    name = 't_copy'
    action = 'table_copy'
    tip = "Copier la définition de la table, son contenu."
    gui_display = "GUI_a"
    title = 'Copie de table TOMUSS'
    css = """
TABLE.table_copy_diagram { width: auto }
TABLE.table_copy_diagram TD { width: 19% }
TABLE.table_copy_diagram TD { text-align: center; vertical-align: middle }
TABLE.table_copy_diagram TH { background: white ; }
    """

##################################### PLUGIN ################################

def tablecopy(server):
    """Copy the table in another EMPTY one"""

    server.the_file.write("Début de la copie\n")
    table = document.table(server.the_year, server.the_semester,
                           server.the_ue, None, None)
    server.the_file.write("La table à copier a pu être lue.\n")

    dest_year = int(server.the_path[0])
    dest_semester = utilities.safe(server.the_path[1]).replace('.','_')
    option = server.the_path[2]

    dest_table = document.table(dest_year, dest_semester,
                                server.the_ue, create=False)
    if dest_table:
        if not dest_table.empty(empty_even_if_used_page=True,
                                empty_even_if_created_today=True,
                                empty_even_if_column_created=True):
            server.the_file.write("""\nLa table destination n'est pas vide.
            Vous devez la détruire avant d'avoir le droit de faire la copie.
            La destruction est possible à partir du menu de l'UE sur la
            page d'accueil.""")
            return
        dest_table.delete()

    if option == 'history':
        c = utilities.read_file(table.filename)
    elif option == 'content':
        c = table.rewrite()
    elif option == 'columns':
        c = table.rewrite(only_columns=True)
    else:
        server.the_file.write("\nIl y a un bug: '%s'." % option)
        return

    filename = document.table_filename(dest_year, dest_semester, server.the_ue)
    utilities.write_file_safe(filename, c)
    server.the_file.write("La copie a été faite, elle va être vérifiée.\n")
    
    
    dest_table = document.table(dest_year, dest_semester,
                                server.the_ue, create=False)
    if (len(table.columns) != len(dest_table.columns)
        or len(table.masters) != len(dest_table.masters)
        ):
        server.the_file.write("\nErreur de copie... %d/%d %s/%s\n" % (
           len(table.columns), len(dest_table.columns),
           table.masters, dest_table.masters))
        server.the_file.close()
        raise ValueError('Table Copy Error')

    for name in dest_table.masters:
            document.master_of_update('+', name, dest_year, dest_semester,
                                      server.the_ue)

    server.the_file.write("\nOK: Copie faite sans erreur.")

plugin.Plugin('tablecopy', '/{Y}/{S}/{U}/tablecopy/{*}',
              function=tablecopy, teacher=True,
              mimetype = "text/plain; charset=UTF-8",
              )
