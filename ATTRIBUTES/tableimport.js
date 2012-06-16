// -*- coding: utf-8 -*-
/*
    TOMUSS: The Online Multi User Simple Spreadsheet
    Copyright (C) 2011 Thierry EXCOFFIER, Universite Claude Bernard

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

    Contact: Thierry.EXCOFFIER@bat710.univ-lyon1.fr
*/

function table_import()
{
  create_popup('import_div', _("TITLE_tableimport"),
	       _("MSG_tableimport_before"), _("MSG_tableimport_after")
	       + '<BUTTON OnClick="import_columns_do();">'
	       + _("B_tableimport") + '</BUTTON>.') ;
}

function import_columns_do()
{
  // Do not remove padding here (IE bug on split)
  var import_lines = popup_value() ;
  var lines = [] ;
  var item ;
  for(var line in import_lines)
    {
      line = import_lines[line] ;
      item = line.split('\t') ;
      if ( item.length > 5 && type_title_to_type(item[0]) )
	lines.push(item) ;
    }
  if ( lines.length == 0 )
    {
      Alert("ALERT_tableimport") ;
      return ;
    }
  var cols = [] ;
  alert_append_start();
  for(var line in lines)
    {
      line = lines[line] ;
      var column = columns[add_empty_columns()] ;

      var i = -1 ;
      for(var c in column_attributes)
	{
	  if ( column_attributes[c].computed )
	    continue ;
	  if ( c == 'position' )
	    continue ;
	  i++ ;
	  if ( c != 'type' && ! column_modifiable_attr(c, column) )
	    continue ;
	  column_attr_set(column, c, line[i]) ;
	}

      create_column(column) ;
      cols.push(column) ;
    }
  // 3 loops because of the formula (dependencies)
  for(var i in cols)
    {
      init_column(cols[i]) ;
    }
  popup_close() ;
  alert_append_stop();
  table_header_fill() ;
}

