/*
    TOMUSS: The Online Multi User Simple Spreadsheet
    Copyright (C) 2008-2011 Thierry EXCOFFIER, Universite Claude Bernard

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

function is_the_current_semester()
{
  var s = document.getElementById("s") ;
  return s.selectedIndex == s.childNodes.length - 1 ;
}

function is_the_last_semester()
{
  var s = document.getElementById("s") ;
  return s.selectedIndex == s.childNodes.length - 2 ;
}

function current_year_semester()
{
  var s = document.getElementById("s") ;
  return s.childNodes[s.childNodes.length - 1].innerHTML ; 
}

function first_university_year_semester()
{
  var ys = current_year_semester().split('/') ;
  var the_year = ys[0] ;
  var the_semester = ys[1] ;
  // Search first semester
  while ( semesters_year[myindex(semesters, the_semester)] != 0 )
    {
      ys = previous_year_semester(the_year, the_semester) ;
      the_year = ys[0] ;
      the_semester = ys[1] ;
    }
  return [the_year, the_semester] ;
}

var goto_url_last_url ;
var goto_url_last_time ;

function goto_url(url)
{
  if ( url === goto_url_last_url && (millisec() - goto_url_last_time) < 1000 )
    {
      alert("Ne double-cliquez pas, un simple clique suffit !") ;
      return ;
    }
  goto_url_last_url = url ;
  goto_url_last_time = millisec() ;
    
  window.open(url) ;
  // window.location = url ;
}

function go(x)
{
  goto_url(base + year_semester() + "/" + x) ;
}

function the_year()
{
  return Number(year_semester().split('/')[0]) ;
}

function do_action(action, html_class)
{
  if ( html_class == 'veryunsafe' )
    if ( ! confirm('Cette action est irréversible, voulez-vous la faire ?') )
      return ;
  goto_url(base + action) ;
}

function university_year()
{
  var ys = year_semester().split('/') ;
  var i = myindex(semesters, ys[1]) ;
  if ( i == -1 )
    return Number(ys[0]) ;
  return Number(ys[0]) + semesters_year[i] ;
}

function semester()
{
  return year_semester().split('/')[1] ;
}

function go_referent()
{
  var ys = first_university_year_semester() ;
  var s = base + university_year() + "/Referents/" + username2 ;
  if ( semester() != ys[1] )
      s += '/=column_offset=6' ;
  goto_url(s) ;
}

function go_favoris()
{
  var s = base + university_year() + "/Favoris/" + username2 ;
  goto_url(s) ;
}

function go_year(x)
{
  goto_url(base + university_year() + "/" + x) ;
}

function go_year_after(x)
{
  goto_url(base + x + '/' + the_year()) ;
}

function go_suivi(x)
{
    goto_url(suivi[year_semester()] + "/" + x) ;
}

function go_suivi_student(x)
{
  if ( preferences.current_suivi == 'NON' )
    goto_url(suivi[year_semester()] + "/" + x) ;
  else
    goto_url(suivi[current_year_semester()] + "/" + x) ;
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

// To not wait lib.js load
i_am_root = myindex(root, my_identity) != -1 ;
               

update_ues2('');
update_referent_of();
update_favorite_student();
document.getElementById('ue_input_name').focus();
document.getElementById('ue_input_name').select();

change_icones();

document.write('<div id="feedback"></div>') ;
