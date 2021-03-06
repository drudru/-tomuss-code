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

function bool_completions(value, column)
{
  column.possible_values = [yes, no, ''] ;
  return completions_enumeration(value, column) ;
}

function test_bool(value, column)
{
  if ( value === undefined )
    return '' ;
  if ( value.toUpperCase )
    value = value.toUpperCase() ;
  if ( value == yes_char || value == '1' || value == yes )
    return yes ;
  if ( value == no_char || value == '0' || value == no )
    return no ;
  return '' ;
}

function enumeration_suivi(choices)
{
  if ( ! cell_modifiable_on_suivi() )
    return html(DisplayGrades.value.toString().replace(/_/g, " ")) ;
  
  var v = '<select class="hidden" onchange="'
    + student_input(DisplayGrades.column) + '">' ;
  var sel, value, display ;
  for(var i in choices)
  {
    i = choices[i] ;
    value = i.replace !== undefined ? i : i[0] ;
    if (value == DisplayGrades.value)
      sel = ' selected="1"' ;
    else
      sel = "" ;
    if ( i.replace === undefined )
        {
          if ( sel !== '' )
              i = [i[0], i[1]-1] ;
          value = i[0] ;
          display = i[0] + ' (' + i[1] + ' ' + _('MSG_free') + ')' ;
        }
    else
        display = value ;
    v += '<option value="' + encode_value(value) + '"' + sel + '>'
      + html(display) + '</option>' ;
  }
  v += '</select>' ;

  return v ;
}

function bool_format_suivi()
{
  return enumeration_suivi(['', yes, no]) ;
}
