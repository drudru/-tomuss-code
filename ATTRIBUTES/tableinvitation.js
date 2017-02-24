// -*- coding: utf-8 -*-
/*
    TOMUSS: The Online Multi User Simple Spreadsheet
    Copyright (C) 2017 Thierry EXCOFFIER, Universite Claude Bernard

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

    Contact: Thierry.EXCOFFIER@univ-lyon1.fr
*/

function send_invitation()
{
  var subject = localStorage['invitation.subject.' + ue]
      || (_("MSG_invitation_subject_default") + ' '
	  + ue + ' ' + table_attr.table_title) ;
  var message = localStorage['invitation.message.' + ue]
      || _("MSG_invitation_message_default") ;
  var mails = localStorage['invitation.mails.' + ue]
      || "john.doe@example.org\nfrancois.chirac@example.org" ;

  create_popup('invitation_div',
	       _("MSG_invitation_title"),
	       _("MSG_invitation_subject")
	       + '<input id="invitation_subject" style="width:100%" value="'
	       + encode_value(subject) + '"><br>'
	       + _("MSG_invitation_message")
	       , _("MSG_invitation_mails")
	       + '<textarea id="invitation_mails">'
	       + encode_value(mails) + '</textarea>'
	       + '<button onclick="invitation_do()">'
	       + _("MSG_invitation_send") + '</button>'
	       + ' <input id="invitation_days" style="width:2em" value="2">'
	       + ' ' + _("ALERT_columnvisibility_date_far_futur2")
	       + ' <select id="invitation_type" style="font-size:140%">'
	       + '<option value="sharable" default>'
	       + _("MSG_invitation_sharable") + "</option>"
	       + '<option value="one_shot" default>'
	       + _("MSG_invitation_one_shot") + "</option>"
	       + "</select>"
	       , _("MSG_invitation_message_default")
	      ) ;
}

function invitation_do()
{
  var mailing_mail = popup_value() ;
  var message = mailing_mail.join('\n') ;
  var subject = document.getElementById('invitation_subject').value ;
  var mails = document.getElementById('invitation_mails').value ;
  var type = document.getElementById('invitation_type').value ;
  localStorage['invitation.subject.' + ue] = subject ;
  localStorage['invitation.message.' + ue] = message ;
  localStorage['invitation.mails.' + ue] = mails ;

  var d = {'subject': subject,
	   'message': message,
	   'type': type,
	   "days": document.getElementById('invitation_days').value,
	   'recipients': mails.replace(/[\n\t ;,]+/g, "\001")
	  } ;
  do_post_data(d, url + '/=' + ticket + '/' + year + "/" + semester
	       + "/" + ue + '/invitation') ;
  popup_close();
}

