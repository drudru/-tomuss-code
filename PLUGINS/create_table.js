
function create_table()
{
  create_popup('create_table',
	       year_semester() + " : " + _("TITLE_create_table"),
	       _("MSG_create_table_code") + '<br>'
	       + '<input id="create_table_code" maxlength="20">' + '<br>'
	       + _("MSG_create_table_title") + '<br>'
	       + '<input id="create_table_title" style="width:100%">' + '<br>'
	       + _("MSG_create_table_private") + '<br>'
	       + '<textarea id="create_table_private"></textarea>'
	       + _("BEFORE_table_official_ue")
	       + '<select id="create_table_visible">'
	       + '<option>' + _("SELECT_table_official_ue_false") + '</option>'
	       + '<option selected>' + _("SELECT_table_official_ue_true")
	       + '</option>'
	       + '</select><br>'
	       , '<button onclick="create_table_do()">'
	       + _("MSG_create_table_do") + '</button>',
	       false) ;
}

function create_table_do()
{
  var code = document.getElementById("create_table_code").value ;
  var title = document.getElementById("create_table_code").value ;

  if ( code === '' || encode_uri(code) != code )
  {
    Alert("MSG_create_table_code_nice") ;
    return ;
  }
  
  var u = url + "/=" + ticket + "/create_table/" + year_semester() + "/"
      + code + "/" + encode_uri(title) + "/"
      + encode_uri(document.getElementById("create_table_private").value) + "/"
      + document.getElementById("create_table_visible").selectedIndex ;
  create_popup('create_table',
	       year_semester() + " : " + _("TITLE_create_table"),
	       '<iframe src="' + u + '" style="width: 100%"></iframe>',
	       '', false) ;
}
