// -*- coding: utf-8 -*-
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

function students_mails(missing)
{
  var s = '', i, student, done = {} ;

  for(var i in filtered_lines)
    {
      line = filtered_lines[i] ;
      if ( line[0].value !== '' )
	{
	    student = login_to_id(line[0].value) ;
	    if ( done[student] )
	       continue ;
	    done[student] = true ;
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
	      a[cell.author] = login_to_id(cell.author) ;
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

function mail_quick_link(mails, link)
{
    return hidden_txt('<a href="javascript: window.location=\'mailto:?bcc=' +
		      mails.replace(RegExp("'","g"),"\\'")
		      + '\'">' + link +' ' + _("MSG_mail_quick_link") + '</a>',
			_("TIP_mail_quick_link")) ;
}

function mail_window()
{
  var missing = [] ;
  var the_student_mails = students_mails(missing) ;
  var nr_student_mails = the_student_mails.split(',').length - 1 ;
  var the_author_mails = authors_mails(missing) ;
  var nr_author_mails = the_author_mails.split(',').length - 1 ;

  if (   the_student_mails.search('@') == -1
       && the_author_mails.search('@') == -1 )
    {
	Alert("ALERT_mail_none") ;
        return ;
    }

  var link_students = nr_student_mails + ' ' + _("MSG_mail_students") ;
  if ( mailto_url_usable(the_student_mails) )
      link_students = mail_quick_link(the_student_mails, link_students) ;
  
  var link_authors = nr_author_mails + ' ' + _("MSG_mail_teachers") ;
  if ( mailto_url_usable(the_author_mails) )
      link_authors =mail_quick_link(the_author_mails, link_authors) ;

  var missing_text ;
  if ( missing.length )
    {
	missing_text = '<p class="unknown_mails">' + missing.length
	  + ' ' + _("MSG_mail_unknow") ;
       if ( missing.length > 20 )
	 missing_text += '.' ;
       else
	 missing_text += ' : ' + missing ;
       missing_text += '</p>' ;
    }
  else
    missing_text = '' ;

  create_popup('mails_div',
	       _("TITLE_mail_popup"),
	       _("MSG_mail_popup") + '<table class="colored"><tr>' +
	       '<th>' + link_students +
	       '<th>' + link_authors +
	       '</tr><tr><td>' +
	       mail_div_box(the_student_mails) +
	       '</td><td>' +
	       mail_div_box(the_author_mails) +
	       '</td></tr></table>' + missing_text
	       ,
		_("MSG_mail_massmail"));
}

function personal_mailing()
{
  var nb = 0;
  for(var i in filtered_lines)
    if ( filtered_lines[i][0].value )
      nb++ ;

  var subject = personal_mailing.old_subject
    || (ue + ' ' + table_attr.table_title + _("MSG_mail_massmail_subject")) ;
  
  create_popup('personal_mailing_div',
	       _("MSG_mail_massmail_title"),
	       _("MSG_mail_massmail_text")
	       + '<input id="personal_mailing" style="width:100%" value="'
	       + encode_value(subject) + '"><br>'
	       + _("MSG_mail_massmail_your_message"),
	       _("MSG_mail_massmail_to_send") + nb
	       + _("MSG_mail_massmail_to_send_2"),
	       _("MSG_mail_massmail_message")
	      ) ;
}


function personal_mailing_do()
{
  var mailing_mail = popup_value() ;
  var subject = document.getElementById('personal_mailing').value ;
  personal_mailing.old_subject = subject ;
  var data_cols = [], data_cols_titles = [] ;
  var t, col_name, nr, message, line, data_col ;
  var url_content, feedback_content ;
  var nr_frame ;

  nr = 0 ;
  message = mailing_mail.join('\n') ;
  var unknown_titles = [] ;

  // Compute used data_cols
  var t = (subject + message).split('[') ;
  for(var i in t)
    {
      if ( i == 0 )
	continue ;
      col_name = t[i].split(']')[0] ;
      data_col = column_title_to_data_col(col_name) ;
      if ( data_col == undefined )
	{
	  unknown_titles.push(col_name) ;
	  continue ;
	}
      if ( myindex(data_cols, data_col) == -1 )
      {
	data_cols.push(data_col) ;
	data_cols_titles.push(col_name) ;
      }
    }
  if ( unknown_titles.length != 0 )
    if ( ! confirm(_("ALERT_mail_unknown_column") + unknown_titles.join(', ')))
      return ;

  // Compute recipients and their data
  var recipents = [] ;
  for(var i in filtered_lines)
    {
      line = filtered_lines[i] ;
      if ( line[0].value )
	{
	  var v = line[0].value ;
          for(data_col in data_cols)
	    v += '\002' + (line[data_cols[data_col]].value === ''
			   ? columns[data_cols[data_col]].empty_is
			   : line[data_cols[data_col]].value) ;
	  recipents.push(v) ;
	}
    }
  do_post_data(
    {'subject': subject,
     'message': message,
     'recipients': recipents.join("\001"),
     'titles': data_cols_titles.join("\001")
    },
    url + '/=' + ticket + '/send_mail') ;
  popup_close();
}

