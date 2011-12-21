// -*- coding: utf-8 -*-
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

function students_mails(missing)
{
    var s = '', i, student ;

  for(var i in filtered_lines)
    {
      line = filtered_lines[i] ;
      if ( line[0].value !== '' )
	{
	    student = login_to_id(line[0].value) ;
	    if ( table_attr.mails[student]
	       && table_attr.mails[student].indexOf('@') != -1)
	    // s += table_attr.mails[line[0].value].replace(/'/g,"\\'") + ',' ;
	    s += table_attr.mails[student] + ',' ;
	  else
	    if ( missing )
	      missing.push(line[0].value) ;
	}
      
    }
  return s ;
}

function authors_mails(missing)
{
  var cls = column_list_all() ;
  var cols = [] ;
  for (var column in cls)
    cols.push(cls[column]) ;

  var a = {} ;
  for(var i in filtered_lines)
    {
      line = filtered_lines[i] ;
      for (data_col in cols)
	{
	  cell = line[cols[data_col]] ;
	  if ( cell.author !== '' && cell.author != '*' && cell.value !== '' )
	    {
	      a[cell.author] = cell.author ;
	    }
	}      
    }
  var s = '' ;
  for(var i in a)
    {
      if ( a[i] == i )
	if ( table_attr.mails[i] && table_attr.mails[i].indexOf('@') != -1 )
	  s += table_attr.mails[i] + ',' ;
	else
	  if ( missing )
	      missing.push(i) ;
    }
  return s ;
}

var mail_separator = '\n' ;

function mail_div_box(mails)
{
  return '<textarea readonly="1" class="mails" onclick="this.select()">'
    + mails.replace(/,/g, mail_separator) + '</textarea>' ;
}

function mail_window()
{
  var missing = [] ;
  var the_student_mails = students_mails(missing) ;
  var nr_student_mails = the_student_mails.split(',').length - 1 ;

  if ( the_student_mails.search('@') == -1 )
    {
      alert("Désolé, votre navigateur n'a pas encore reçu les adresses mails.\nRéessayez dans quelques secondes.") ;
      return ;
    }

  var link_students = nr_student_mails + ' Étudiants' ;
  if ( mailto_url_usable(the_student_mails) )
    link_students = hidden_txt('<a href="javascript: window.location=\'mailto:?bcc=' +
			       the_student_mails.replace(/'/g,"\\'") + '\'">' + link_students + ' (Lien rapide)</a>',
			       'Suivez le lien pour directement lancer ' +
			       'votre logiciel de messagerie.') ;

  var the_author_mails = authors_mails(missing) ;
  var nr_author_mails = the_author_mails.split(',').length - 1 ;
  var link_authors = nr_author_mails + ' Enseignants' ;
  if ( mailto_url_usable(the_author_mails) )
    link_authors = hidden_txt('<a href="javascript: window.location=\'mailto:?bcc=' +
			       the_author_mails.replace(/'/g,"\\'") + '\'">' + link_authors + ' (Lien rapide)</a>',
			       'Suivez le lien pour directement lancer ' +
			       'votre logiciel de messagerie.') ;

  var missing_text ;
  if ( missing.length )
    {
	missing_text = '<p class="unknown_mails">' + missing.length
	  + ' adresses mail inconnues' ;
       if ( missing.length > 20 )
	 missing_text += '.' ;
       else
	 missing_text += ' : ' + missing ;
       missing_text += '</p>' ;
    }
  else
    missing_text = '' ;

  create_popup('mails_div',
	       'Gestion des mails (des étudiants filtrés) ',
	       '<ul>' +
	       '<li> <b>Cliquez sur une adresse</b> pour toutes les sélectionner.' +
	       '<li> Puis faites <b>Ctrl-C</b> pour les copier' +
	       '<li> Puis faites <b>Ctrl-V</b> dans la liste des destinataires en <b>Copie Carbone Invisible (CCI ou BCC)</b> si vous ne voulez pas que les étudiants connaissent les autres destinataires.' +
	       '</ul>' +
	       'En cas de problème, utilisez le <a href="javascript:mail_separator=\';\';mail_window()">point-virgule</a> ou la <a href="javascript:mail_separator=\',\';mail_window()">virgule</a>  comme séparateur.' +
	       '<table class="colored"><tr>' +
	       '<th>' + link_students +
	       '<th>' + link_authors +
	       '</tr><tr><td>' +
	       mail_div_box(the_student_mails) +
	       '</td><td>' +
	       mail_div_box(the_author_mails) +
	       '</td></tr></table>' + missing_text
	       ,
	       'TOMUSS peut faire du <a href="javascript:personal_mailing()">publi-postage</a> en envoyant les mails pour vous.<br>Ceci permet d\'envoyer des informations personnalisées aux étudiants en fonction du contenu de la table.') ;
}

function personal_mailing()
{
 var nb = 0;
 for(var i in filtered_lines)
   if ( filtered_lines[i][0].value )
     nb++ ;

   create_popup('personal_mailing_div',
		'Envoyer un mail personnalisé aux étudiants filtrés',
		'<p style="background-color:#F00;color:#FFF">N\'ENVOYEZ PAS DE NOTES PAR MAIL AUX ÉTUDIANTS.</p>Les titres de colonne entre crochets sont remplacés par la valeur de la case correspondant à l\'étudiant pour cette colonne. Vous pouvez utiliser toutes les colonnes existantes.<p>&nbsp;<br>Sujet du message : <input id="personal_mailing" style="width:100%" value="' + ue + ' ' + table_attr.table_title + ' : Info pour [Prénom] [Nom]"><br>Votre message&nbsp;:',
		'Pour envoyer, cliquez sur : <BUTTON OnClick="personal_mailing_do();">Envoyer les ' + nb + ' messages</BUTTON>.',
		'Bonjour [Prénom] [Nom].\n\nVotre groupe est [Grp] et votre séquence [Seq]\n\nAu revoir.'
		) ;
}

function personal_mailing_parse_line(text, column_used, column_data_col)
{
  var t = text.split('[') ;
  var col_name, data_col ;
  for(var i in t)
    {
      if ( i == 0 )
	continue ;
      col_name = t[i].split(']')[0] ;
      if ( column_used[col_name] !== undefined )
	continue ;
      data_col = column_title_to_data_col(col_name) ;
      if ( data_col == undefined )
	{
	  alert("La colonne «" + col_name + "» n'existe pas.");
	  return ;
	}
      column_used[col_name] = personal_mailing_do.nr_items++ ;
      column_data_col[data_col] = true ;
    }
  for(var i in column_used)
    {
      text = text.replace('[' + i + ']', '[' + column_used[i] + ']') ;
    }

  return text ;
}

function personal_mailing_do()
{
  var mailing_mail = popup_value() ;
  var subject = document.getElementById('personal_mailing').value ;
  var column_used = {}, column_data_col = {} ;
  var t, col_name, nr, message, line, data_col ;
  var url_content, feedback_content ;
  var nr_frame ;

  nr = 0 ;
  message = '' ;
  personal_mailing_do.nr_items = 0 ;
  for(var line in mailing_mail)
    {
      t = personal_mailing_parse_line(mailing_mail[line],
				      column_used, column_data_col) ;
      if ( t === undefined )
	return ;
      message += t + '\n' ;
    }
  subject = personal_mailing_parse_line(subject, column_used, column_data_col);
  if ( subject === undefined )
    return ;
  subject = encode_uri(subject) ;
  url_content = '' ;
  feedback_content = '' ;
  nr_frame = 0 ;
  for(var i in filtered_lines)
    {
      line = filtered_lines[i] ;

      if ( url_content === '' )
	{
	  nr_frame++ ;
	  url_content = '<iframe src="_URL_/=' + ticket + '/send_mail/'
	    + subject + '/' + encode_uri(message) ;
	}

      if ( line[0].value )
	{
	  url_content += '/' + encode_uri(line[0].value) ;
          for(data_col in column_data_col)
	     url_content += '/' + encode_uri(line[data_col].value) ;
	}

      if ( url_content.length > maximum_url_length
	   || i == filtered_lines.length-1 )
	{
	  feedback_content += url_content
	    + '"></iframe>' ;
	  url_content = '' ;
	}
    }
  var self_mail = '<iframe src="_URL_/=' + ticket + '/send_mail/[POUR_ARCHIVAGE]%20'
    + subject + '/' + encode_uri(message) + '/' + encode_uri(my_identity) ;
  for(var col_name in column_used)
     self_mail += '/' + encode_uri('['+col_name+']') ;
  self_mail += '"></iframe>' ;
  feedback_content += self_mail ;
  

 create_popup('personal_mailing_fb', 'Publipostage', feedback_content, '',
	      false) ;
}

