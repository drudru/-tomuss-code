// -*- coding: utf-8; mode: Java; c-basic-offset: 2; tab-width: 8; -*-

/* To send the cell change and feedback */

function _cell(s, url, col_type, minmax)
{
  var ticket = document.location.pathname.split('/')[1] ;
  var url_s = url.split('/') ;
  var ue = url_s[url_s.length-4] ;
  var unload = document.getElementById('unload') ;
  var iframe = s.parentNode.lastChild ;

  if ( iframe.tagName != 'IFRAME' )
    {
      iframe = document.createElement('iframe') ;
      iframe.className = 'feedback' ;
      s.parentNode.appendChild(iframe) ;
    }

  if ( col_type )
      {
	  var false_column = {'minmax': minmax}, new_s ;
	  
	  if ( minmax )
	      {
		  set_test_note(minmax, false_column) ;
	      }
	  new_s = type_title_to_type(col_type).cell_test(s.value,
							 false_column) ;
	  if ( new_s !== undefined )
	      s.value = new_s ;
	  else
	      {
		  if ( iframe )
		      iframe.parentNode.removeChild(iframe) ;
		  return ;
	      }
      }

  iframe.src = url + '/' + encode_uri(s.value) ;

  if ( unload )
    unload.src = 'unload/' + ue;
}

function hide_empty()
{
  document.getElementById('computed_style').textContent = 'DIV.empty, .empty, DIV.empty P { display: none ; }' ;
}

function show_empty()
{
  document.getElementById('computed_style').textContent = '.notempty { display: none ; }' ;
}

function initialize_suivi_real()
{
  lib_init() ;
  instant_tip_display = true ;
  document.getElementById('x').innerHTML = _("MSG_suivi_student_wait") ;
  
  var s ;
  s = ''
    + '<style id="computed_style">.notempty { display: none ; }</style>\n'
    + '<img id="unload" width="1" height="1">\n'
    + '<div class="identity">'
    + '<a href="_FILES_/suivi_student_doc.html">' + _("MSG_help") + '</a>, '
    + '<a href="mailto:' + maintainer + '?subject='
    + encodeURI(_('MSG_suivi_student_mail_subject')) + '&body='
    + encodeURI(_('MSG_suivi_student_mail_body')).replace(/\n/g, '%0A')
    + '">' +  _('MSG_suivi_student_mail_link') + '</a>, '
    + '<a href="' + url_suivi + '/=' + ticket + '/logout">'
    + _("LABEL_logout") +'</a> '
    + '<b>' + username + '</b><br>' ;

  if ( myindex(root, username) != -1 )
    s += '<a href="reload_plugins">' + _("TITLE_reload_plugins") + '</a>' ;

  s += '</div>' ;
  
  if ( is_a_teacher )
    s += '<a href="javascript:hide_empty()" class="empty">'
    + _("MSG_hide_empty_cells")
    + '</a><a href="javascript:show_empty()" class="notempty">'
    + _("MSG_show_empty_cells") + '</a>'
    + '<br><br>' ;
  else
  {
    s += '<style>DIV.empty P { display: none ; }</style>'
    + '<p style="padding: 0.5em; border:3px solid black ; margin: 0.5em ;background-color: #FF8080; font-size: 150%">'
      + _("MSG_suivi_student_important")
      + '</p>' ;
  }
  
  document.getElementById('top').innerHTML = s ;
}

function private_toggle()
{
  window.location = url + '/=' + ticket + '/private/' + (1-private) ;
}

function popup_private()
{
  create_popup('private_div',
	       _("LINK_suivi_student_private"),
	       _("MSG_suivi_student_private_full")
	       + '<p><button onclick="private_toggle()">'
	       + (private ? _("MSG_suivi_student_private_public")
		  : _("MSG_suivi_student_private_private"))
		  + '</button>',
	       '', false
	      );
}

function catch_this_student(event, login)
{
  event = the_event(event) ;
  if ( confirm(_('TIP_suivi_student_get')) )
    {
      create_popup('import_div',_('TIP_suivi_student_get'),
		   '<iframe src="' + url + '/=' + ticket + '/referent_get/'
		   + student_login + '" style="width:100%;height:5em">iframe</iframe>',
		   '', false) ;
    }
}