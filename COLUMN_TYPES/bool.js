/*
    TOMUSS: The Online Multi User Simple Spreadsheet
    Copyright (C) 2008,2010 Thierry EXCOFFIER, Universite Claude Bernard

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

function toggle_bool(value)
{
  return toggle_PA(test_bool, value, [yes, no]) ;
}

function test_bool(value, column)
{
  if ( value === undefined )
    return '' ;
  var v = value.toUpperCase() ;
  if ( v == yes_char || v == '1' || v == yes )
    return yes ;
  if ( v == no_char || v == '0' || v == no )
    return no ;
  return '' ;
}

function enumeration_suivi(choices)
{
  if ( ! cell_modifiable_on_suivi() )
    return html(DisplayGrades.value.replace(/_/g, " ")) ;
  
  var v = '<select class="hidden" onchange="'
    + student_input(DisplayGrades.column) + '">' ;
  var sel ;
  for(var i in choices)
  {
    i = choices[i] ;
    if (i == DisplayGrades.value)
      sel = ' selected="1"' ;
    else
      sel = "" ;
    v += '<option value="' + encode_value(i) + '"' + sel + '>'
      + html(i) + '</option>' ;
  }
  v += '</select>' ;

  return v ;
}

function bool_format_suivi()
{
  return enumeration_suivi(['', yes, no]) ;
}