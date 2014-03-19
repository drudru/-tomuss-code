/*
    TOMUSS: The Online Multi User Simple Spreadsheet
    Copyright (C) 2008-2014 Thierry EXCOFFIER, Universite Claude Bernard

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

function follow_url(in_value)
{
  var url_base = the_current_cell.column.comment.split('BASE(') ;
  if ( url_base.length == 1 )
    url_base = the_current_cell.column.url_base ;
  else
    {
      url_base = url_base[1].split(')')[0] ;
    }

  value = url_base + in_value.split(' ', 1)[0] ;
   var safe = value.replace(/[&%?]/,'') ;
  if ( safe != value || (
    value.substr(0,5) != 'http:' && value.substr(0,5) != 'https:' ))
	{
	  if ( ! confirm(_("ALERT_follow_url") + "\n" + value) )
		{
		return value ;
		}
	}

   window.open(value) ;
   return in_value ;
}

function url_format_suivi()
{
  if ( DisplayGrades.value === '' )
    return ' ' ;

  var value = DisplayGrades.value.toString().split(' ') ;
  var title ;
  if (value.length > 1)
    title = value.slice(1).join(' ') ;
  else
  {
    if (DisplayGrades.column.url_title)
      title = DisplayGrades.column.url_title ;
    else
      title = _("MSG_URL") ;
  }

  if (title.substr(0,7) !== '<script')
    title = html(title) ;

  return '<a target="_blank" href="' + DisplayGrades.column.url_base
    + value[0] + '">' + title + '</a>' ;
}

