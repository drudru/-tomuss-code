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

function next_semester(a)
{
  if ( a[1] == 'P' )
    return [a[0], 'a'] ;
  return [a[0]+1, 'P'] ;
}

var names = {'a': 'Aut.', 'P': 'Print.'} ;
var names_full = {'a': 'Automne', 'P': 'Printemps'} ;

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


function bilan(ticket, login, resume, firstname, surname, mail, suivi,
	       i_can_refer, external_info)
{
  var older = [9999, 'P'] ;
  var newer = [0, 'A'] ;
  var s ;

  s = '<html><head><link rel="stylesheet" href="/bilan.css" type="text/css">'
    + '<title>' + firstname + ' ' + surname + '</title>'
    + '</head>'
    + '<body>'
    + '<img class="picture" src="' + student_picture_url(login) + '">'
    + '<h1>' + login + ' ' + firstname + ' ' + surname
    + ' <a class="mail" href="mailto:' + mail + '">' + mail + '</a></h1>'
    + '<div class="hidden_on_paper">'
    + 'Les informations officielles sont dans le <a href="' + bilan_link(login) + '" target="_blank">Bilan APOGÉE</a> qui peut être plus à jour que les informations affichées ici.'
    + "<p>Le tableau représente les informations stockées par TOMUSS, des UE où l'étudiant a été inscrit peuvent manquer."
    + "<ul><li>Si la case est blanche et vide, l'étudiant est inscrit dans TOMUSS mais aucune information n'a été saisie"
    + '<li>Le carré de couleur contient : Vert : Présences ou Note., Bleu : Absence justifiée, Rouge : Absence injustifiée'
    + "<li>La note sur 20 est une moyenne de TOUTES les notes saisies dans TOMUSS sans tenir compte des poids. <b>Ce n'est pas la note de l'UE</b>"
    + '</ul>' ;

  if ( false && i_can_refer )
    s += '<a href="_URL_/=' + ticket + '/referent_get/' + login +
      '">Je veux devenir le référent pédagogique de cet étudiant</a> (vous ne pourrez plus vous en séparer sauf si quelqu\'un vous le prend)' ;

  s += '</div>';
  document.write(s) ;

  var ues = update_ues_with_external_data(resume, external_info) ;

  // Compute first and last semester
  for(var i in resume)
    {
      var semesters = resume[i] ;
      for(var j in semesters)
	{
	  semester = semesters[j] ;
	  if ( semester[1] == 'Printemps' )
	    semester[1] = 'P' ;
	  else if ( semester[1] == 'Automne' )
	    semester[1] = 'a' ;
	  else
	    continue ;
	  if ( semester < older )
	    older = semester ;
	  if ( semester > newer )
	    newer = semester ;
	}
    }

  // Sort the semesters by time
  for(var i in resume)
    resume[i].sort() ;

  s = '<table>' ;
  s += '<tr><td>UE' ;
  for(var i = older ; i <= newer ; i = next_semester(i) )
    {
      s += '<td><a href="' + suivi[i[0] + '/' + names_full[i[1]]] + '/'
	+ login + '">' + i[0] + '<br>' + names[i[1]] + '</a></td>';
      
    }
  s += '</tr>' ;
  for(var i in ues)
    {
      var t = resume[ues[i]] ;
      s += '<tr class="' + t.tr_class + '"><td style="text-align:right">' + ues[i] + '</td>' ;
      if ( t === undefined )
	alert(1);
      for(var j = older ; j <= newer ; j = next_semester(j) )
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
	  if ( t[0][0] == j[0] && t[0][1] == j[1] )
	    {
	      var v = t[0] ;
	      var n = v[2] + v[3] + v[4] ;
	      s += '<td class="inscrit"><a href="/=' + ticket + '/'
		+ j[0] + '/' + names_full[j[1]] +'/UE-' + ues[i]
		+ '/=read-only=/=filters=0:' + login_to_id(login)
		+ '=" target="_blank">' ;
	      if ( n == 0 )
		s += '&nbsp;' ;
	      else
		{
		  if ( v[5] != -1 )
		    s += '<span style="float:right">' + (v[5]*20).toFixed(1)
		      + '</span>' ;

		  s += '<img class="info prst" src="_URL_/ok.png" style="height:'
		    + (size*v[2]/n).toFixed(2) + 'em"><br>\n' ;
		  s += '<img class="info abjus" src="_URL_/abjus.png" style="height:'
		    + (size*v[4]/n).toFixed(2) + 'em"><br>\n' ;
		  s += '<img class="info abinj" src="_URL_/bad.png" style="height:'
		    + (size*v[3]/n).toFixed(2) + 'em"><br>\n' ;
		}
	      s += '</a></td>' ;
	      t.shift() ;
	    }
	  else
	    {
	      s += '<td>&nbsp;</td>' ;
	    }
	}
      if ( t.length )
	      s += '<td>' + t[0][2] + '</td>' ;
      s += '</tr>\n' ;
    }

  s += '</table>' ;

  document.write(s) ;
}
