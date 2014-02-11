#!/usr/bin/python
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2013 Thierry EXCOFFIER, Universite Claude Bernard
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#    Contact: Thierry.EXCOFFIER@univ-lyon1.fr

"""
Allow teachers to add messages onto the 'suivi' page of the student.
The messages should contains button to answer.

As the 'signature' framework is used, the student can not
use the suivi until the message is answered.
"""

import cgi
from .. import signature
from .. import configuration
from .. import files
from .. import utilities
from .. import plugin
from .. import inscrits

files.files["lib.js"].append("signature_new", r"""
function signature_new(sl)
{
  signature_new.student_login = sl ;
  create_popup('import_div', _("LABEL_signature_new"),
               _("MSG_signature_new"),
	       '<input id="signature_send_mail" type="checkbox" checked>' +
	       _("MSG_signature_send_mail") + '</input><br>' +
               '<button onclick="signature_add()">' +
	       _("MSG_signature_create") + '</button>',
	       _("MSG_signature_example")
	      ) ;
}

function signature_add()
{
  var send_mail = document.getElementById("signature_send_mail").checked ;
  send_mail = Number(send_mail) ;
  var message = popup_value().join('\n') ;
  if ( message.match(/{{{[^}]+}}}/) )
  {
    window.location = url + "/=" + ticket + '/signature_new/'
      + signature_new.student_login
      + '/' + send_mail + '/' + encode_uri(message) ;
  }
  else
    Alert("ALERT_signature_miss_button") ;
}
""")

def signature_hook(student_login, value, data):
    teacher, send_mail = data
    if int(send_mail):
        fn, sn, mail = inscrits.L_fast.firstname_and_surname_and_mail(
            student_login)
        value = unicode(value, 'utf-8')
        utilities.send_mail(inscrits.L_fast.mail(teacher),
                            utilities.__("SUBJECT_signature_done")
                            + ' ' + value,
                            utilities.__("MSG_signature_answer") + '\n'
                            + student_login + ' ' + fn + ' ' + sn + ' : '
                            + value,
                            frome = mail,
                            show_to=True
                            )
        
configuration.signature_hook = signature_hook


def signature_new(server):
    send_mail, message = server.the_time, unicode(server.something, 'utf-8')
    fn, sn, mail = inscrits.L_fast.firstname_and_surname_and_mail(
        server.ticket.user_name)
    message = (server.__("MSG_signature_from")
               + fn +' '+ sn + ' ' + mail + '\n\n'
               + message)
    message = message.encode('utf-8')
    signature.add_question(server.the_student,
                           message,
                           "signature_hook",
                           (server.ticket.user_name, send_mail),
                           timeout=99999)
    server.the_file.write(server._('MSG_saved')
                          + '<pre>' + cgi.escape(message) + '</pre>')

plugin.Plugin('signature_new', '/signature_new/{I}/{ }/{?}',
              function=signature_new,
              group="staff",
              )


