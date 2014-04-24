/* -*- coding: utf-8 -*- */
/*
    TOMUSS: The Online Multi User Simple Spreadsheet
    Copyright (C) 2010-2011 Thierry EXCOFFIER, Universite Claude Bernard

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

var size = 1.3 ;

/*REDEFINE
Update the'ues' list with external informations.
'ues' is a dictionary of tables (see SCRIPTS/bilan.py).
This function returns the order of the lines to display.
*/
function update_ues_with_external_data(resume, external_info)
{
  var ues = [] ;
  for(var i in resume)
    ues.push(i) ;
  ues.sort(function(a,b) {
	     if ( resume[a][0] > resume[b][0] )
	       return 1 ;
	     if ( resume[a][0] < resume[b][0] )
	       return -1 ;
	     return 0 ; } ) ;
  return ues ;
}

/*REDEFINE
Returns a string to insert after the title of the bilan page.
 */
  function bilan_external_header(login)
{
    return '' ;
}

function bilan(ticket, login, resume, firstname, surname, mail, suivi,
	       i_can_refer, external_info)
{
  var older = [9999, 1] ;
  var newer = [0, 0] ;
  var s ;

  s = '<html><head><link rel="stylesheet" href="/bilan.css" type="text/css">'
    + '<title>' + firstname + ' ' + surname + '</title>'
    + '</head>'
    + '<body>'
    + '<img class="picture" src="' + student_picture_url(login) + '">'
    + '<h1>' + login + ' ' + firstname + ' ' + surname
    + ' <a class="mail" href="mailto:' + mail + '">' + mail + '</a></h1>'
    + '<div class="hidden_on_paper">'
    + bilan_external_header(login)
    + '<p>' + _("MSG_bilan") ;

  if ( false && i_can_refer )
    s += '<a href="' + url_suivi + '/=' + ticket + '/referent_get/' + login +
	'">' + _("MSG_bilan_take_student") + '</a>' ;

  s += '</div>';
  document.write(s) ;

  var ues = update_ues_with_external_data(resume, external_info) ;

  // Compute first and last semester
  for(var i in resume)
    {
      var t_semesters = resume[i] ;
      var semester ;
      for(var j in t_semesters)
	{
	  j = t_semesters[j] ;
	  semester = [j[0], myindex(semesters, j[1])] ;	  
	  if ( semester[1] == -1 )
	    continue ;
	  if ( semester < older )
	    older = semester ;
	  if ( semester > newer )
	    newer = semester ;
	  j[1] = semester[1] ; // To sort by time
	}
    }

  // Sort the semesters by time
  for(var i in resume)
    resume[i].sort() ;

  s = '<table>' ;
  s += '<tr><td>UE' ;
  for(var i = older ; i <= newer ; i = next_year_semester_number(i[0], i[1]) )
    {
      semester = semesters[i[1]] ;
      s += '<td><a href="' + suivi[i[0] + '/' + semester] + '/'
	+ login + '">' + i[0] + '<br>' + semester.substr(0,4) + '</a></td>';
    }
  s += '</tr>' ;
  for(var i in ues)
    {
      var t = resume[ues[i]] ;
      s += '<tr class="' + t.tr_class + '"><td style="text-align:right">' + ues[i] + '</td>' ;
      if ( t === undefined )
	alert(1);
      for(var j = older ; j <= newer ; j = next_year_semester_number(j[0],j[1]) )
	{
	  if ( t[0] === undefined )
	    {
	      s += '<td>&nbsp;</td>' ;
	      continue;
	    }
	  else if ( t[0][3] === undefined )		
	    {
	      var tmp = t[0] ;
	      t.splice(0,1) ;
	      t.push(tmp) ;
	    }
	  semester = semesters[j[1]] ;
	  if ( t[0][0] == j[0] && t[0][1] == j[1] )
	    {
	      var v = t[0] ;
	      var n = v[2] + v[3] + v[4] ;
	      s += '<td class="inscrit"><a href="/=' + ticket + '/'
		+ j[0] + '/' + semester +'/' + ues[i]
		+ '/=read-only=/=filters=0_0:' + login_to_id(login)
		+ '=" target="_blank">' ;
	      if ( n == 0 )
		s += '&nbsp;' ;
	      else
		{
		  if ( v[5] != -1 )
		    s += '<span style="float:right">' + (v[5]*20).toFixed(1)
		      + '</span>' ;

		  s += '<img class="info prst" src="_FILES_/ok.png" style="height:'
		    + (size*v[2]/n).toFixed(2) + 'em">\n' ;
		  s += '<img class="info abjus" src="_FILES_/abjus.png" style="height:'
		    + (size*v[4]/n).toFixed(2) + 'em">\n' ;
		  s += '<img class="info abinj" src="_FILES_/bad.png" style="height:'
		    + (size*v[3]/n).toFixed(2) + 'em">\n' ;
		}
	      s += '</a></td>' ;
	      t.shift() ;
	    }
	  else
	    {
	      s += '<td>&nbsp;</td>' ;
	    }
	}
      if ( t.length ) // Display remaining external information
	s += '<td>' + t[0][2] + '</td>' ;
      s += '</tr>\n' ;
    }

  s += '</table>' ;

  document.write(s) ;
}
