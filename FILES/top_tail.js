/*
    TOMUSS: The Online Multi User Simple Spreadsheet
    Copyright (C) 2008,2009 Thierry EXCOFFIER, Universite Claude Bernard

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

function year_semester()
{
  var s = document.getElementById("s") ;
  return s.childNodes[s.selectedIndex].innerHTML ;
}

function goto_url(url)
{
  window.open(url) ;
  // window.location = url ;
}

function go(x)
{
goto_url(base + year_semester() + "/" + x) ;
}

function university_year()
{
  var ys = year_semester().split('/') ;
  if ( ys[1] == 'Printemps' )
     ys[0] = ys[0] - 1 ;
  return ys[0] ;
}

function semester()
{
  return year_semester().split('/')[1] ;
}

function go_referent()
{
  var s = base + university_year() + "/Referents/" + username2 ;
  if ( semester() == 'Printemps' )
      s += '/=column_offset=6' ;
  goto_url(s) ;
}

function go_year(x)
{
  goto_url(base + university_year() + "/" + x) ;
}

function go_suivi(x)
{
goto_url(suivi[year_semester()] + "/" + x) ;
}

function change_icones()
{
var icones = document.getElementsByTagName("IMG") ;
for(var img in icones)
   {
   img = icones[img] ;
   if ( img.className == 'icone' || img.className == 'bigicone' )
      {
      img.src = suivi[year_semester()] + '/' +
               img.src.replace(RegExp('.*/'), '') ;
      }
   }
 document.getElementsByTagName('BODY')[0].className = semester() ;
}

var display_tips = true ;

update_ues(ufr);
document.getElementById('ue_input_name').focus();
document.getElementById('ue_input_name').select();

document.getElementById('ue_list_spiral').innerHTML = display_ues(username.replace('.',' ')) ;

change_icones();
