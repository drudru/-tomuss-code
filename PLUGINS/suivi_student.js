// -*- coding: utf-8; mode: Java; c-basic-offset: 2; tab-width: 8; -*-


function DisplayUEGradesInit(ue)
{
  table_attr = ue ;
  line = [] ;
  for(var i in ue.line)
    {
      i = ue.line[i] ;
      line.push(C(i[0], i[1], i[2], i[3])) ;
    }
  ue.line_real = line ;
  columns = [] ;
  for(var i in ue.columns)
    columns.push(Col(ue.columns[i])) ;

  for(var data_col in columns)
    {
      init_column(columns[data_col]) ;
      columns[data_col].data_col = data_col ;
    }
  DisplayGrades.table_attr = ue ;
}


/* To send the cell change and feedback */

function _cell(s, url)
{
  var url_s = url.split('/') ;
  var ue = url_s[url_s.length-4] ;
  var grades = display_data["Grades"][0] ;
  table_attr = undefined ;
  for(var i in grades)
    {
      if ( grades[i].ue == ue )
	{
	  DisplayUEGradesInit(grades[i]) ;
	  break ;
	}
    }
  var col_id = url_s[url_s.length-2] ;
  var data_col = data_col_from_col_id(col_id) ;
  var column = columns[data_col] ;
  var new_s = column.real_type.cell_test(s.value, column) ;
  if ( new_s !== undefined )
    s.value = new_s ;

  iframe = document.createElement('iframe') ;
  iframe.className = 'feedback' ;
  iframe.src = url + '/' + encode_uri(s.value) ;

  if ( DisplayGrades.html_object )
    {
      // The DisplayGrades attributes are initialised by 'display_cellbox_tip'
      DisplayGrades.table_attr.line[DisplayGrades.column.data_col][0] = s.value;
      var e = document.createElement("DIV") ;
      DisplayGrades.no_hover = false ;
      e.innerHTML = display_display(DisplayGrades.ue_node) ;
      e = e.firstChild ;
      var line = DisplayGrades.cellbox.parentNode ;
      var position = myindex(line.childNodes, DisplayGrades.cellbox) ;
      e.childNodes[position].appendChild(iframe) ;
      var ue = line.parentNode ;
      ue.removeChild(ue.lastChild) ;
      ue.appendChild(e) ;
    }
  else
    s.parentNode.appendChild(iframe) ;

  unload = document.createElement('IMG') ;
  unload.src = url_suivi + '/=' + ticket + '/unload/' + ue ;
  unload.width = unload.height = 1 ;
  the_body.appendChild(unload) ;

  hide_cellbox_tip() ;
}

function initialize_suivi_real()
{
  lib_init() ;
  instant_tip_display = true ;
  
  document.getElementById('top').innerHTML = '<div id="cellbox_tip"></div>'
    + ( window.devicePixelRatio !== undefined
	? '<meta name="viewport" content="width=device-width,height=device-height,initial-scale=1">'
	: '' )
    + '<div id="display_suivi"></div>'
    ;
  i_am_root = myindex(root, username) != -1 ;
  my_identity = username ;
}

function cell_modifiable_on_suivi()
{
  table_attr = DisplayGrades.table_attr ;
  if ( ! DisplayGrades.cell.modifiable(DisplayGrades.ue.line_real,
				       DisplayGrades.column) )
    return ;
  if ( ! DisplayGrades.column.modifiable )
    return ;
  if ( DisplayGrades.column.modifiable == 2 )
    return true ;
  if ( is_a_teacher
       && DisplayGrades.column.modifiable == 1 ) // So modifiable == 1
    return true ;
}

function DisplayList(node)
{
  return DisplayHorizontal(node, ', ') ;
}
DisplayList.need_node = [] ;

function is_inside_rightclip(element)
{
  while(element)
    {
      if ( element.id == 'rightclip' )
	return true ;
      element = element.parentNode ;
    }
}

function set_rightclip(classe, event)
{
  if ( millisec() - set_rightclip.time < 100 )
    return ;
  set_rightclip.time = millisec() ;
  
  var e = document.getElementById("rightclip") ;
  if ( ! e )
    return ;

  if ( event
       && event.button !== undefined
       && e.className.toString().match('hide_rightclip')
       && is_inside_rightclip(the_event(event).target) )
    stop_event(event) ; // Not follow links when clicking on hidden bodyright

  e.className = e.className.toString()
    .replace(/ [^ ]*_rightclip/g, '') + ' ' + classe ;

  // XXX Kludge : Hide Bodyright if bodyleft is clicked on touch screen
  e.parentNode.parentNode.onmousedown = function(event) {
    if ( is_inside_rightclip(the_event(event).target) )
      return ;
    hide_rightclip(event) ;
  } ;
  return 
}
set_rightclip.time = 0 ;

function show_rightclip(event)
{
  set_rightclip('show_rightclip', event) ;
}

function hide_rightclip(event)
{
  set_rightclip('hide_rightclip', event) ;
}

function rightclip_touch_start(event)
{
  rightclip_touch_start.x = the_event(event).x ;
  console.log("rightclip_touch_start " + rightclip_touch_start.x) ;
}

function rightclip_touch_end(event)
{
  console.log("rightclip_touch_stop " + the_event(event).x) ;
  if ( the_event(event).x > rightclip_touch_start.x + 8 )
    hide_rightclip(event) ;
  if ( the_event(event).x < rightclip_touch_start.x - 8 )
    show_rightclip(event) ;
}

function DisplayRightClip(node)
{
  return [DisplayHorizontal(node),
	  ['hide_rightclip'],
	  [],
	  'id="rightclip" '
	  + 'ontouchstart="rightclip_touch_start(event)" '
	  + 'ontouchmove="rightclip_touch_end(event)" '
	  + 'onclick="show_rightclip(event)" '
	  + 'onmouseenter="show_rightclip(event)" '
	  + 'onmouseleave="hide_rightclip(event)"'] ;
}
DisplayRightClip.need_node = [] ;

function load_full_size_picture(event, login)
{
  var imgs = [] ;

  var tip = get_tip_element() ;
  var yet = tip.getElementsByTagName('IMG') ;
  for(var i in yet)
    imgs['X' + i] = yet[i] ;

  var e = the_event(event).target ;
  while ( e.className != 'tipped' )
    e = e.parentNode ;
  var yet = e.getElementsByTagName('IMG') ;
  for(var i in yet)
    imgs['Y' + i] = yet[i] ;

  for(var i in imgs)
    if ( imgs[i].className == 'big' )
      imgs[i].src = student_picture_url(login) ;
}

function DisplayPicture_(login)
{
  return hidden_txt('<img class="small" alt="' + _('ALT_photo_ID') + '" src="'
		    + student_picture_icon_url(login)
		    + '" style="vertical-align:top">',
		    '<img class="big" alt="'
		     + _('ALT_photo_ID') + '">', undefined, undefined,
		    "load_full_size_picture(event," + js2(login) + ")") ;
}

function DisplayPicture(node)
{
  return DisplayPicture_(display_data['Login']) ;
}
DisplayPicture.need_node = ['Login'] ;

function DisplayOfficial(node)
{
  return '<a href="'
    + bilan_des_notes + display_data['Login']
    + '" target="_blank">'
    + hidden_txt(_("MSG_suivi_student_official_bilan"),
		 _("TIP_suivi_student_official_bilan")
		 ) + '</a>' ;
}
DisplayOfficial.need_node = ['Login'] ;

function DisplayBilan(node)
{
  if ( ! is_a_teacher )
    return '' ;
  return hidden_txt('<a href="' + url + '/=' + ticket + '/bilan/'
		    + display_data['Login'] + '" target="_blank">'
		    + _("MSG_suivi_student_TOMUSS_bilan") + '</a>',
		    _("TIP_suivi_student_TOMUSS_bilan")) ;
}
DisplayBilan.need_node = ['Login'] ;

function displaynames(data)
{
  var mail = '<a href="mailto:' + data[2] + '">'
    + title_case(data[0]) + ' ' + data[1] + '</a>' ;
  if ( data[3] !== undefined )
    mail = DisplayPicture_(data[3]) + mail ;
  return mail ;
}

function DisplayNames(node)
{
  return displaynames(node.data) ;
}

function DisplayReferent(node)
{
  switch(node.data[4])
    {
    case false:
      return hidden_txt(_('MSG_suivi_student_no_referent'),
			_('TIP_suivi_student_no_referent_needed')) ;
    case true:
      return hidden_txt(_('MSG_suivi_student_no_referent'),
			_('TIP_suivi_student_no_referent')) ;
    default:
      return hidden_txt(DisplayNames(node),
			_('MSG_suivi_student_send_to_referent')) ;
    }
}

function DisplayMails(node)
{
  var ref ;
  if ( display_data['Referent'][4] !== undefined )
    ref = ',' + _("MSG_suivi_student_referent") + '<'
      + display_data['Referent'][2] + '>' ;
  else
    ref = '' ;

  return '<a href="mailto:?to='
    + encodeURIComponent(node.data.join(',') + ref)
    + '&subject=' + encodeURIComponent(display_data['Login'] + ' '
			   + display_data['Names'][0]
			   + ' ' + display_data['Names'][1])
    + '">'
    + hidden_txt(_("MSG_suivi_student_mail_all"),
		 _("TIP_suivi_student_mail_all")) + '</a>' ;
}
DisplayMails.need_node = ['Mails', 'Login', 'Referent', 'Names'] ;

function DisplayStudentView(node)
{
  if ( ! is_a_teacher )
    return '' ;
  return '<a href="' + url_suivi + '/../../' + year + '/' + semester
    + '/=' + ticket + '/ '
    + display_data['Login'] + '" target="_blank">'
    + hidden_txt(_("MSG_suivi_student_view"), _("TIP_suivi_student_view"))
    + '</a>' ;
}
DisplayStudentView.need_node = ['Login'] ;

function DisplayCharte(node)
{
  if ( ! is_a_teacher )
    return '' ;
  if ( node.data )
    return _("MSG_suivi_student_contract_checked") ;
  else
    return '<span style="background:red">'
      + _("MSG_suivi_student_contract_unchecked") + '</span>' ;
}

function DisplaySignature(node)
{
  return '<a href="signatures/' + display_data['Login'] + '">'
    + _("MSG_signatures") + '</a>' ;
}
DisplaySignature.need_node = ['Login'] ;

function DisplayReload(node)
{
  if ( ! is_a_teacher || ! display_data['Preferences']
       || ! display_data['Preferences']['debug_suivi'] )
    return '' ;
  return '<a href="reload_plugins">' + _("TITLE_reload_plugins") + '</a>' ;
}
DisplayReload.need_node = [] ;

function DisplayExplanationPopup()
{
  if ( popup_classname() == 'explanations_popup' )
    {
      popup_close() ;
      return ;
    }
  create_popup('explanations_popup',
	       'TOMUSS <span class="copyright">'
	       + display_data['Explanation']
	       + '</span>'
	       + '<a style="" href="mailto:'
	       + maintainer + '?subject='
	       + encodeURI(_('MSG_suivi_student_mail_subject')) + '&body='
	       + encodeURI(_('MSG_suivi_student_mail_body')).replace(/\n/g,
								     '%0A')
	       + '">' + _('MSG_suivi_student_mail_link') + '</a>',
	       _("MSG_suivi_help"),
	       '', false) ;
}

function DisplayExplanation(node)
{
  return hidden_txt('<a href="javascript:DisplayExplanationPopup()">?</a>',
		    _("COL_TITLE_explanations")) ;
}
// DisplayExplanation.need_node = [] ;

function preference_toggle(item)
{
   if ( !is_a_teacher && username != display_data['Login'] )
     {
       Alert("ERROR_value_not_modifiable") ;
       return ; // Can't change student preferences
     }
   
   display_data['Preferences'][item] = 1 - display_data['Preferences'][item] ;
   DisplayPreferencesPopup(true) ;
   DisplayGrades.no_hover = false ;
   display_update_real() ;
   var data = display_data['Preferences'] ;
   var t = [] ;
   for(var i in data)
     t.push(i + '=' + data[i]) ;
   var img = document.createElement('IMG') ;
   img.src = url + '/=' + ticket + '/save_preferences/' + t.join('/') ;
   document.getElementById('preference_' + item).appendChild(img) ;
}

function DisplayPreferencesPopup(do_no_hide)
{
  if ( !do_no_hide && popup_classname() == 'preferences_popup' )
    {
      popup_close() ;
      return ;
      }
  var data = display_data['Preferences'] ;
  var items = [] ;
  for(var item in data)
    items.push(item) ;
  items.sort(function(a,b)
	     {
	       a = _('Preference_' + a) ;
	       b = _('Preference_' + b) ;
	       if ( a < b )
		 return -1 ;
	       if ( a > b )
		 return 1 ;
	       return 0 ;
	     }
	     ) ;
  var s = [], label ;
  for(var item in items)
    {
      item = items[item] ;
      label = 'Preference_' + item ;
      if (  _(label) != label )
	s.push('<li onclick="preference_toggle(\'' + item + '\')"'
	       + ' id="preference_' + item + '"'
	       + ' class="selection_' + data[item] + '">'
	       + _(label)  + '</li>') ;
    }
  create_popup('preferences_popup',
	       '<small>' + _('LABEL_preferences')
	       + '/<a href="' + url_suivi + '/=' + ticket + '/logout">'
	       + _("LABEL_logout") +'</a></small><br>'
	       + (is_a_teacher ? username : display_data['Login']),
	       '<ul>' + s.join('') + '</ul>', '', false) ;
}

function DisplayPreferences(node)
{
  display_do_debug = node.data['debug_suivi'] ;
  for(var item in node.data)
    if ( node.data[item] === undefined )
      node.data[item] = 0 ;
  return hidden_txt('<a href="javascript:DisplayPreferencesPopup()">≡</a>',
		    _("LABEL_preferences")) ;
}
DisplayPreferences.need_node = ['Preferences', 'Login'] ;

function DisplayUEToggle_key(ue)
{
  return year + '/' + semester + '/' + ue ;
}

function DisplayUEToggle_text(ue)
{
  try {
    return localStorage[DisplayUEToggle_key(ue)] == "closed" ? '▶' : '▼' ;
  } catch(e) { return '§' ; }
}

function DisplayUEToggle_is_open(ue)
{
  try {
    return localStorage[DisplayUEToggle_key(ue)] != 'closed' ;
  } catch(e) { return true ; }
}

function DisplayUEToggle_do(event, ue)
{
  var k = DisplayUEToggle_key(ue) ;
  try {
    localStorage[k] = localStorage[k] == "closed" ? "open" : "closed" ;
  }
  catch(e) {
    alert('LocalStorage NOT WORKING: ASK HELP\n\n'
	  + navigator.userAgent + ':\n\n' + e) ;
  }
  var t = the_event(event).target ;
  t.innerHTML = DisplayUEToggle_text(ue) ;
  var content = t.parentNode.parentNode.nextSibling ;
  if ( DisplayUEToggle_is_open(ue) )
    content.style.display = "block" ;
  else
    content.style.display = "none" ;
  if ( content.className.toString().indexOf("UEComment") != -1 )
    {
      content = content.nextSibling ;
      if ( DisplayUEToggle_is_open(ue) )
	content.style.display = "block" ;
      else
	content.style.display = "none" ;
    }
}

function DisplayUEToggle(node)
{
  try {
    return '<a class="clickable" onclick="DisplayUEToggle_do(event,'
      + js2(DisplayGrades.ue.ue) + ')">'
      +  DisplayUEToggle_text(DisplayGrades.ue.ue)
      + '</a>' ;
  }
  catch(e)
    {
      return '' ;
    }
}
DisplayUEToggle.need_node = [] ;


function DisplayUETitle(node)
{
  var ue = DisplayGrades.ue ;
  var title = html(ue.ue + ' ' + (ue.table_title || '')) ;
  if ( is_a_teacher && ue.semester )
    {
      var url_table = url + '/=' + ticket + '/' + ue.year
	+ '/' + ue.semester + '/' + ue.ue ;
      title = '<a href="' + url_table + '" target="_blank">' + title + '</a>' ;
      title = hidden_txt(title, _("MSG_cell_full_table"));
      title += hidden_txt(' (<a href="' + url_table
			  + '/=filters=0_0:'
			  + login_to_id(display_data['Login'])
			  + '=" target="_blank">*</a>)',
			  _("MSG_cell_one_line")) ;
      return '<a name="' + ue.ue + '">' + title + '</a>' ;
    }
  else
      return '<a tabindex="0" name="' + ue.ue + '">' + title + '</a>' ;
}
DisplayUETitle.need_node = [] ;

function DisplayUEMasters(node)
{
  var ue = DisplayGrades.ue ;
  var mails = [] ;
  for(var j in ue.masters)
    mails.push(displaynames(ue.masters[j])) ;
  if ( mails.length )
    return hidden_txt('<small>' + mails.join(', ') + '</small>',
		      _("MSG_abj_master")) ;
  return '' ;
}
DisplayUEMasters.need_node = [] ;

function DisplayUEComment(node)
{
  var ue = DisplayGrades.ue ;
  if ( ue.comment && ue.comment != '' )
    return _("MSG_cell_message")
      + '<em>' + html(ue.comment) + '</em>' ;
  return '' ;
}
DisplayUEComment.need_node = [] ;

function hide_fake_ue(ue)
{
  if ( ! ue.fake_ue )
    return false ;
  for(var i in DisplayUETree.children[ue.ue])
    if ( ! hide_fake_ue(DisplayUETree.dict[DisplayUETree.children[ue.ue][i]]) )
      return false ;
  return true ;
}

function DisplayUE(node)
{
  var s = DisplayVertical(node) ;
  for(var data_col in columns)
    if ( columns[data_col].freezed == "C"
	 && line[data_col].value.match(/\bnon\b/) )
      {
	s = '<div class="nonInscrit">'
	  + _("WARN_unregistered_student") + '<br><br>' + s + '</div>' ;
	break ;
      }
  if ( DisplayUETree.children && DisplayUETree.children[DisplayGrades.ue.ue])
    {
      s = s.substr(0, s.length-6) ; // Remove </div>
      var save = DisplayGrades.ue ;
      var children = DisplayUETree.children[DisplayGrades.ue.ue] ;
      if ( hide_fake_ue(DisplayGrades.ue) )
	return ;
      while ( children.length == 1 && DisplayUETree.dict[children[0]].fake_ue )
	children = DisplayUETree.children[children[0]] ;
      s += '<div style="margin-left: 2em">' ;
      for(var i in children)
	{
	  DisplayGrades.ue = DisplayUETree.dict[children[i]] ;
	  s += display_display(display_definition['UE']) ;
	}
      s += '</div></div>' ;
      DisplayGrades.ue = save ;
    }

  return [s, [], [], 'onmouseenter="enter_in_ue(event)" id="'
	  + DisplayGrades.ue.ue + '"'] ;
}
DisplayUE.need_node = [] ;

function remove_prefix(txt)
{
  return txt.split('-')[1] || txt ;
}

/*REDEFINE
Called before UE tree construction
*/
function DisplayUETreeHook(node)
{
}

function DisplayUETree(node)
{
  DisplayUETreeHook(node) ;
  var ues = display_data["Grades"][0] ;
  var with_prefix = {} ;
  DisplayUETree.dict = {} ;
  for(var i in ues)
    {
      var code = ues[i].ue ;
      with_prefix[remove_prefix(code)] = code ;
      DisplayUETree.dict[code] = ues[i] ;
    }

  var translated = {} ;
  for(var i in node.data)
    if ( node.data[i] != i )
      translated[with_prefix[i] || i]
	= with_prefix[node.data[i]] || node.data[i] ;
  node.data = translated ;

  for(var i in node.data)
    {
      var parent = node.data[i] ;
      if ( ! DisplayUETree.dict[parent] )
	{ // Parent does not exist, so create a fake one
	  ues.push({ue: parent, table_title: "", fake_ue: true}) ;
	  DisplayUETree.dict[parent] = ues[ues.length-1] ;
	}
    }

  ues.sort(function(a,b)
	   { return get_ue_priority(b) < get_ue_priority(a) ? 1 : -1 ; }) ;

  var children = {} ;
  for(var k in ues)
    children[ues[k].ue] = [] ;
  for(var k in ues)
    {
      k = ues[k].ue ;
      var parent = node.data[k] ;
      if ( ! parent )
	continue ;
      children[parent].push(k) ;
    }

  DisplayUETree.children = children ;
  DisplayUETree.parent = node.data ;
}
DisplayUETree.need_node = ["UETree", "Grades"] ;

function DisplayCellAuthor(node)
{
  if ( DisplayGrades.cell.author == '' )
    return '' ;
  return '<span class="displaygrey">'
    + _("DisplayCellAuthorBefore") + '</span>&nbsp;'
    + html(DisplayGrades.cell.author) ;
}
DisplayCellAuthor.need_node = [] ;

function DisplayCellMTime(node)
{
  if ( DisplayGrades.cell.date == '' )
    return '' ;
  return '<span class="displaygrey">' + _("DisplayCellMTimeBefore")
    + '</span>&nbsp;' + date(DisplayGrades.cell.date) ;
}
DisplayCellMTime.need_node = [] ;

function DisplayCellComment(node)
{
  if ( DisplayGrades.cell.comment == '' )
    return '' ;
  return '<span class="displaygrey">' + _("SUIVI_comment") + '</span>&nbsp;'
    + html(DisplayGrades.cell.comment) ;
}
DisplayCellComment.need_node = [] ;

function DisplayCellColumn(node)
{
  return html(DisplayGrades.column.comment) ;
}
DisplayCellColumn.need_node = [] ;

function DisplayCellGroupMembers(node)
{
  var members = DisplayGrades.cellstats.group_members ;
  if ( ! members )
    return '' ;
  if ( members.length == 0 )
    return 'Alone' ;
  var s = [DisplayGrades.column.groupcolumn + ' : '] ;
  for(var i in members)
    s.push(members[i][0] + ' ' + members[i][1] + ' ' + members[i][2]) ;
  return s.join('<br>\n') ;
}
DisplayCellGroupMembers.need_node = [] ;

function DisplayCellRank(node)
{
  if ( DisplayGrades.cellstats === undefined )
    return ' ' ;
  if ( ! DisplayGrades.column.real_weight_add )
    return ' ' ;
    
  var s = ' ' ;
  if ( DisplayGrades.cellstats.rank !== undefined)
    s += (DisplayGrades.cellstats.rank+1)
      + '/' + DisplayGrades.cellstats.nr + ' ' ;
  if ( DisplayGrades.cellstats.rank_grp !== undefined)
    s += (DisplayGrades.cellstats.rank_grp+1)
      + '/' + DisplayGrades.cellstats.nr_in_grp ;
  if ( s != ' ' )
    s = '<span class="displaygrey">' + _("TH_rank") + '</span>' + s ;
  return s ;
}
DisplayCellRank.need_node = [] ;

function DisplayCellAvg(node)
{
  if ( DisplayGrades.cellstats === undefined )
    return '' ;
  if ( DisplayGrades.cellstats.average === undefined)
    return '' ;
  return ' <span class="displaygrey">' + _('Average') + '</span> '
    + DisplayGrades.column.do_rounding(DisplayGrades.cellstats.average)
    +  ' <span class="displaygrey">' + _('Mediane') + '</span> '
    + DisplayGrades.cellstats.mediane ;
}
DisplayCellAvg.need_node = [] ;

function DisplayCellDate(node)
{
  var d = DisplayGrades.column.course_dates ;
  if ( d == '' )
    return '' ;
  d = d.split(/  */) ;
  var x = '' ;
  for(var i in d)
    x += get_date_tomuss_short(d[i]) + ' ' ;
  
  return '<span class="displaygrey">' + _("SUIVI_course_dates")
    + '</span>' + x ;
}
DisplayCellDate.need_node = [] ;

function DisplayCellType(node)
{
  return '<span class="displaygrey">' + _('B_' + DisplayGrades.column.type)
    + '</span>' ;
}
DisplayCellType.need_node = [] ;

function DisplayCellFormula(node)
{
  return DisplayGrades.formula ;
}
DisplayCellFormula.need_node = [] ;

function DisplayCellTitle(node)
{
  var title = html(DisplayGrades.column.title.replace(/_/g, ' ')) ;
  if ( DisplayGrades.column.is_visible() )
    {
      if ( is_a_teacher && DisplayGrades.column.modifiable == 2 )
	title = '<span class="modifiable_by_student">' + title + '</span>' ;
      else if ( is_a_teacher && DisplayGrades.column.visibility == 3 )
	title = '<span class="public_display">' + title + '</span>' ;
    }
  else
    title = '<span class="hidden_to_student">' + title + '</span>' ;
  return title ;
}
DisplayCellTitle.need_node = [] ;

function DisplayCellValue(node)
{
  var t = DisplayGrades.column.real_type.formatte_suivi() ;
  if ( ! t )
    return '&nbsp;' ;
  var len ;
  if ( t.match('>') )
    len = t.split('>')[1].split('<')[0].length ;
  else
    len = t.length ;
  if ( len < 40 )
    return t ;
  return [t, 'long_text', '', ''] ;
}
DisplayCellValue.need_node = [] ;

var display_saved = {} ;
var display_saved_nr = 0 ;

function enter_in_ue(event)
{
  if ( popup_classname() === undefined )
    {
      popup_close() ;
    }
  var t = document.getElementById("cellbox_tip") ;
  if ( ! t || ! t.grades )
    return ;
  event = the_event(event) ;
  if ( enter_in_ue.ue != event.target )
    {
      hide_cellbox_tip() ;
      enter_in_ue.ue = event.target ;
    }
}

function hide_cellbox_tip()
{
  var t = document.getElementById("cellbox_tip") ;
  if ( ! t )
    return ;
  t.className = "hidden" ;
  if ( t.grades )
    t.grades.className = t.grades.className.toString()
      .replace(/ tip_displayed/g, "") ;
}

function display_cellbox_tip(event, nr)
{
  hide_the_tip_real(true) ;
  hide_rightclip() ;
  var c = the_event(event).target ;
  while( c.className.toString().indexOf('CellBox') == -1 )
    c = c.parentNode ;

  var t = document.getElementById("cellbox_tip") ;
  if ( t.do_not_display )
    {
      t.do_not_display = false ;
      return ;
    }
  t.onmouseleave = function() {
    // Tricky: if the cellbox tip has the focus, do not hide it
    var s = document.activeElement ;
    while( s )
      {
	if ( s == t )
	  return ;
	s = s.parentNode ;
      }
    t.className = "hidden" ;
  } ;
  t.className = "" ;
  DisplayGrades.cellbox = c ;
  DisplayGrades.column = display_saved[nr][0] ;
  DisplayGrades.cell = display_saved[nr][1] ;
  DisplayGrades.html_object = c.getElementsByTagName('FORM')[0]
    || c.getElementsByTagName('INPUT')[0]
    || c.getElementsByTagName('SELECT')[0] ;
  if ( DisplayGrades.html_object && DisplayGrades.html_object.value )
    DisplayGrades.value = DisplayGrades.html_object.value ;
  else
    DisplayGrades.value = display_saved[nr][2] ;
  DisplayGrades.cellstats = display_saved[nr][3] ;
  DisplayGrades.ue = display_saved[nr][4] ;
  DisplayGrades.formula = display_saved[nr][5] ;
  DisplayGrades.table_attr = display_saved[nr][6] ;
  DisplayGrades.ue_node = display_saved[nr][7] ;
  DisplayGrades.no_hover = true ;
  t.innerHTML = display_display(display_definition['Cell']);
  DisplayGrades.no_hover = false ;
  t.style.top = findPosY(c) - t.childNodes[0].childNodes[0].offsetHeight+'px';
  t.style.left = findPosX(c) + 'px' ;
  t.display_date = millisec() ;

  if ( t.grades )
    t.grades.className = t.grades.className.toString()
      .replace(/ tip_displayed/g, "") ;

  t.grades = c ;
  while( t.grades.className.toString().indexOf('DisplayUE ') == -1 )
    t.grades = t.grades.parentNode ;
  t.grades.className += " tip_displayed" ;
}

function display_tree(column)
{
  if ( column.average_from.length == 0 )
    return '' ;
  if ( ! column_modifiable_attr("columns", column) )
    return '' ;
  var s = ['<ul>'] ;
  var col ;
  for(var i in column.average_from)
    {
      col = columns[data_col_from_col_title(column.average_from[i])] ;
      if ( !col || col.obfuscated )
	return '' ;
      s.push('<li>'
	     // + '<span class="displaygrey">' + _("B_"+col.type) + '</span> '
	     + column.average_from[i]
	     + ' <span class="displaygrey">' + _("BEFORE_column_attr_weight")
	     + '</span>&nbsp;' + col.weight
	     + (display_data['Preferences'].recursive_formula
		? display_tree(col)
		: '') + '</li>'
	     ) ;
    }
  s.push("</ul>") ;
  return s.join("") ;
}

function rank_to_color(rank, nr)
{
  var x = Math.floor(511*rank/nr) ;
  var b, c = '' ;
  if ( rank > nr / 2 )
    {
      b = '255,' + (511-x) + ',' + (511-x) ;
      if ( rank > 3*nr / 4 )
	c = ';color:#FFF' ;
    }
  else
    b = x + ',255,' + x ;

  return 'background: rgb(' + b + ')' + c
}

function grade_to_class(column, grade)
{
  if ( grade == abi )  return 'abinj' ;
  if ( grade == abj )  return 'abjus' ;
  if ( grade == tnr )  return 'tnr' ;
  if ( grade == pre )  return 'prst' ;
  if ( isNaN(grade) )  return '' ;
  
  var ci = (grade - column.min) / (column.max - column.min) ;

  if ( ci > 0.8 ) return 'verygood' ;
  if ( ci > 0.6 ) return 'good' ;
  if ( ci > 0.4 ) return 'mean' ;
  if ( ci > 0.2 ) return 'bad' ;
  return 'verybad' ;
}

function get_cell_class_and_style()
{
  var classes = ['DisplayType' + DisplayGrades.column.type] ;
  var styles = [] ;
  if ( display_data['Preferences'] // Turn around bug on multiple suivi student
       && ! display_data['Preferences']['black_and_white'] )
    {
      if ( DisplayGrades.column.red + DisplayGrades.column.green
	   + DisplayGrades.column.redtext + DisplayGrades.column.greentext != ''
	   && ! display_data['Preferences']['no_teacher_color'])
	classes.push(cell_class(DisplayGrades.column,
				DisplayGrades.ue.line_real,
				DisplayGrades.cell)) ;
      else if ( DisplayGrades.column.real_weight_add )
	{
	  if ( DisplayGrades.cellstats
	       && DisplayGrades.cellstats.rank !== undefined
	       && DisplayGrades.cellstats.nr >= 10
	       && ! display_data['Preferences']['color_value']
	       )
	    styles.push(rank_to_color(DisplayGrades.cellstats.rank,
				      DisplayGrades.cellstats.nr)) ;
	  else if ( (DisplayGrades.column.type == 'Moy'
		     || DisplayGrades.column.type == 'Note'
		     || DisplayGrades.column.type == 'Prst'
		     )
		    && DisplayGrades.cell.value !== ''
		    && (
			display_data['Preferences'].green_prst
			|| DisplayGrades.value != pre
			))
	    classes.push(grade_to_class(DisplayGrades.column,
					DisplayGrades.value)) ;
	}
    }
  if ( DisplayGrades.cell.comment )
    styles.push('font-weight: bold') ;

  return [classes, styles] ;
}

function DisplayCellBox(node)
{
  if ( ! is_a_teacher &&  DisplayGrades.column.title.substr(0,1) == '.' )
    return '' ;
  var s = DisplayVertical(node) ;
  var more = '' ;
  
  if ( ! DisplayGrades.no_hover ) // Stop recursion
    {
      display_saved[display_saved_nr] = [DisplayGrades.column,
					 DisplayGrades.cell,
					 DisplayGrades.value,
					 DisplayGrades.cellstats,
					 DisplayGrades.ue,
					 display_tree(DisplayGrades.column),
					 DisplayGrades.table_attr,
					 DisplayGrades.ue_node
					 ] ;
      if ( DisplayGrades.column.type == 'Moy' )
	{
	  if ( DisplayGrades.column.best != 0 )
	    display_saved[display_saved_nr][5] += _("SUIVI_best_of_before")
	      + DisplayGrades.column.best +  _("SUIVI_best_of_after")
	      + '<br>' ;
	  if ( DisplayGrades.column.worst != 0 )
	    display_saved[display_saved_nr][5] += _("SUIVI_mean_of_before")
	      + DisplayGrades.column.worst +  _("SUIVI_mean_of_after")
	      + '<br>' ;
	}
      else if ( DisplayGrades.column.type == 'Weighted_Percent'
		|| DisplayGrades.column.type == 'Nmbr' )
	{
	  display_saved[display_saved_nr][5] = display_saved[display_saved_nr][5]
	    .replace("<ul", html(DisplayGrades.column.test_filter) + '<ul') ;
	}
      more = 'tabindex="0" onfocus="display_cellbox_tip(event,'
	+ display_saved_nr + ');" onmousemove="display_cellbox_tip(event,'
	+ display_saved_nr + ');" onmouseenter="display_cellbox_tip(event,'
	+ display_saved_nr + ');"' ;
      display_saved_nr++ ;
    }
  var class_and_style = get_cell_class_and_style() ;
  return [s, class_and_style[0], class_and_style[1], more] ;
}
DisplayCellBox.need_node = [] ;

var columns, line ;

function DisplayUEGrades(node)
{
  var ue = DisplayGrades.ue ;
  DisplayUEGradesInit(ue) ;
  DisplayGrades.ue_node = node ;

  var s = ' ' ; // Not empty in order to generate a <div>
  var ordered_columns = column_list_all() ;
  for(var data_col in ordered_columns)
    {
      data_col = ordered_columns[data_col] ;
      if ( data_col < 3 )
	continue ;
      if ( columns[data_col].freezed == "C" )
	continue ;
      DisplayGrades.cell = line[data_col] ;
      DisplayGrades.column = columns[data_col] ;
      DisplayGrades.value = line[data_col].value ;
      if ( DisplayGrades.value === '' )
	DisplayGrades.value = DisplayGrades.column.empty_is ;
      DisplayGrades.cellstats = DisplayGrades.ue.stats[DisplayGrades.column.the_id] || {} ;
      var ss = display_display(display_definition['CellBox']);
      if ( DisplayGrades.value === '' && ! cell_modifiable_on_suivi())
	ss = ss.replace('class="', 'class="is_empty ') ;
      s += ss ;
    }
  if ( ! DisplayUEToggle_is_open(ue.ue) )
    return [s, "", "display:none"] ;
  return s ;
}
DisplayUEGrades.need_node = [] ;

/*REDEFINE
 This function allow to sort the table on the suivi page
 in the wanted order.
 By default the UE code
*/
function get_ue_priority(ue)
{
  return ue.ue ;
}

function DisplayGrades(node)
{
  if ( node.data === undefined )
    return '<span style="background:#FF0">' + _("MSG_suivi_student_wait")
      + '</span>' ;

  var s = '' ;
  for(var i in node.data[0])
    {
      DisplayGrades.ue = node.data[0][i] ;
      if ( DisplayUETree.parent
	   && DisplayUETree.parent[DisplayGrades.ue.ue] !== undefined
	   && DisplayUETree.dict[DisplayUETree.parent[DisplayGrades.ue.ue]]
	   !== undefined
	   )
	continue ;
      try
	{
	  s += display_display(display_definition['UE']) ;
	}
      catch(e)
	{
	  console.log(e) ;
	  s += '<h1>' + DisplayGrades.ue.ue + ' : BUG</h1>' + e ;
	}
    }
  var before = _("MSG_suivi_student_not_in_TOMUSS_before") ;
  if ( before == "MSG_suivi_student_not_in_TOMUSS_before" )
    before = '' ;
  else
    before += ' ' ;
  for(var i in node.data[1])
    {
      var t = node.data[1][i][0] + ' ' + node.data[1][i][1] ;
      if ( is_a_teacher )
	s += '<p class="title">' + _("MSG_suivi_student_registered")+t+'</p>';
      else
	s += '<div class="UE UETitle">'
	  + before
	  + t + '</div><div class="UEComment">'
	  + _("MSG_suivi_student_not_in_TOMUSS_after")
	  + '</div>' ;
    }

  return '<hr>' + s ;
}
DisplayGrades.need_node = ['Login', 'Grades', 'Preferences'] ;

function goto_cellbox(o)
{
  goto_cellbox.old = document.getElementById(o.innerHTML.split('<')[0]) ;
  goto_cellbox.old.className = goto_cellbox.old.className.replace("not_yellow",
								  "")+" yellow";
  goto_cellbox.oldo = o ;
  o.className = o.className.replace("not_yellow", "") + " yellow" ;
}

function ungoto_cellbox(o)
{
  if ( goto_cellbox.old )
    {
      goto_cellbox.old.className=goto_cellbox.old.className.replace("yellow",
								      'not_yellow') ;
      goto_cellbox.oldo.className=goto_cellbox.oldo.className.replace("yellow",
								      'not_yellow');
    }
}

function cell_visibility_date(cell, column)
{
  if ( cell[2] === undefined )
    return new Date(0) ;
  var modif_time = get_date_tomuss(cell[2]) ;
  if ( column.visibility_date === '' || column.visibility_date === undefined )
    return modif_time ;
  var column_visible_date = get_date_tomuss(column.visibility_date) ;
  if ( column_visible_date < modif_time )
    return modif_time ;
  else
    return column_visible_date ;
}

function DisplayLastGradesList(time_limit)
{
  var grades = display_data['Grades'][0] ;
  var s = [] ;
  
  for(var ue in grades)
    {
      ue = grades[ue] ;
      for(var data_col in ue.line)
	{
	  var cell = ue.line[data_col] ;
	  if ( cell[0] === '' || cell[0] === undefined )
	    continue ;
	  if ( cell[1].length < 2 )
	    continue ; // System value
	  var time = cell_visibility_date(cell, ue.columns[data_col]) ;
	  time.setHours(0) ;
	  time.setMinutes(0) ;
	  time.setSeconds(0) ;
	  time = time.getTime();
	  if ( time < time_limit )
	    continue ;
	  s.push([ue, data_col, time]) ;
	}
    }
  s.sort(function(a, b) { return b[2] - a[2] ; }) ;
  return s ;
}

function DisplayLastGrades(node)
{
  if ( is_a_teacher )
    return '' ;
  var one_week = millisec() - 7*24*3600000 ;
  var s = DisplayLastGradesList(one_week) ;
  if ( s.length == 0 )
    return '' ;
  var t = [] ;
  var today = new Date() ;
  today.setHours(0) ;
  today.setMinutes(0) ;
  today.setSeconds(0) ;
  today = today.getTime() ;
  var daynames = [_("LABEL_Day0"), _("LABEL_Day1"), _("LABEL_Day2")] ;
  var lastday, max ;
  for(var i in s)
    {
      var ue = s[i][0] ;
      var data_col = s[i][1] ;
      var quand = s[i][2] ;
      var column = ue.columns[data_col] ;
      var cell = ue.line[data_col] ;
      var nb_days = Math.round((today - quand)/86400000) ;
      var day = daynames[nb_days] ;
      if ( day === undefined )
	day = _("LABEL_ThisWeek") ;
      if ( day != lastday )
	{
	  if ( lastday !== undefined )
	    t.push("<br>") ;
	  t.push('<div class="Display day">' + day + '</div>') ;
	  lastday = day ;
	}
      max = "" ;
      if ( column.type == 'Upload' )
	max = _("Kb") ;
      else if ( column.type == 'Note' )
	{
	  if ( !column.minmax )
	    max = "/20" ;
	  else if ( column.minmax.substr(0,3) == "[0;" )
	    max = "/" + column.minmax.split(";")[1].split(']')[0] ;
	}
      if ( max !== "" )
	max = '<span style="font-size:60%">' + max + "</span>" ;
      t.push('<div tabindex="0" onmouseover="goto_cellbox(this)" onmouseout="ungoto_cellbox(this)" class="Display a_grade">'
	     + ue.ue
	     + '<br>' + html(column.title || '???')
	     + '<br><span>' + html(cell[0]) + max + "</span></div>") ;
    }
  return '<hr>' + t.join('') ;
}
DisplayLastGrades.need_node = ['Grades'] ;

function DisplayLogoPopup(node)
{
  if ( popup_classname() == 'logo_popup' )
    {
      popup_close() ;
      return ;
    }
  create_popup('logo_popup',_('MSG_suivi_student_logo'),
	       DisplayLogo.popup_content, '', false) ;
}

function DisplayLogo(node)
{
  if ( node.data === '' || node.data == 'http://xxx.yyy.zzz/logo.png' )
    return '' ;
  var s = [] ;
  for(var i in node.children)
    s.append(display_display(node.children[i])) ;
  DisplayLogo.popup_content = s.join("<br>") ;

  var img = '<img'
    + ( node.children.length
	? ' onclick="DisplayLogoPopup()"'
	: '')
    + ' alt="' + _("MSG_suivi_student_logo") + '"'
    + ' src="' + node.data + '">' ;

  if ( s.length != 0 )
    img = hidden_txt(img, _("MSG_suivi_student_logo")) ;

  return img ;
}

function DisplayYearSemester(node)
{
  return '<span class="Display">' + year + '<br>' + semester + '</span>' ;
}
DisplayYearSemester.need_node = [] ;

function DisplayGoHome(node)
{
  if ( ! is_a_teacher && node.data )
    return ['<a href="' + url + '/=' + ticket + '">'
	    + _("MSG_signature_done") + '</a>',
	    [],
	    ['width:10em; text-align:center; white-space:normal; font-size:80%']
	    ] ;
}

function DisplaySemesters(node, textual)
{
  var y = '9999' ;
  for(var ys in node.data)
    if ( ys < y )
      y = ys ;
  y = y.split('/')[0] ; // Older year
  var s = semesters[0] ; // First semester of the real year
      
  var t = [], highlight ;
  do
    {
      if ( textual )
	{
	  t.push('<p><a href="' + node.data[y + '/' + s]
		 + '/=' + ticket + '/' + display_data['Login'] + '/*">'
		 + y + ' ' + s + '</a>'
		 ) ;
	}
      else
	{
	  if ( s == semesters[0] )
	    t.push('</tr><tr><td>' + y + '</td>') ;
	  if ( y == year && s == semester)
	    highlight = ' style="background: #FF0"' ;
	  else
	    highlight = '' ;
	  
	  if (is_a_teacher)
	    icone = '<img class="icone" src="' + node.data[y + '/' + s]
	      + '/=' + ticket + '/_' + display_data['Login'] + '">' ;
	  else
	    icone = '' ;
	  if ( node.data[y + '/' + s] )
	    t.push('<td' + highlight + '><a href="' + node.data[y + '/' + s]
		   + '/=' + ticket + '/' + display_data['Login'] + '">'
		   + icone + s + '</a></td>') ;
	  else
	    t.push('<td>&nbsp;</td>') ;
	}

      ys = next_year_semester(y, s) ;
      y = ys[0] ;
      s = ys[1] ;
    }
  while(node.data[y + '/' + s] || s != semesters[0]) ;
  if ( textual )
    return t.join('') ;
  return '<table class="tomuss_links colored">'
    + '<tr><th colspan="3">'
    + hidden_txt(_("MSG_suivi_student_semesters"),
		 _("TIP_suivi_student_semesters"))
    + t.join('\n') + '</tr></table>' ;
}
DisplaySemesters.need_node = ['Semesters', 'Login'] ;

function DisplayGetStudent(node)
{
  if ( ! is_a_teacher )
    return '' ;
  if ( display_data['Referent'][3] == username )
    return '' ; // I am yet its referent

  return hidden_txt('<img onclick="catch_this_student('
		    + js2(display_data['Login']) + ')" '
		    + 'alt="' + _("MSG_home_become_referent") + '" '
		    + 'src="' + url_files
		    + '/butterflynet.png">', _('MSG_bilan_take_student'));
}
DisplayGetStudent.need_node = ['Referent', 'Login'] ;

function DisplayIsPrivate(node)
{
  var s = _("MSG_suivi_student_private") ;
  if ( node.data[0] )
    s += '<p>' + _("MSG_suivi_student_private_referent")
      + ' ' + DisplayNames(node) ;
  return s ;
}

function DisplayPreamble(node)
{
  if ( is_a_teacher )
    return '' ;
  return '<title>TOMUSS</title>' + _("MSG_suivi_student_important") ;
}
DisplayPreamble.need_node = [] ;

function DisplayMessages(node)
{
  var m = [] ;
  var abjs = display_data['Abjs'] ;
  for(var i in abjs)
    if ( abjs[i][2].substr(0, 13) == '{{{MESSAGE}}}' )
      m.push(parse_date(abjs[i][0]).formate('%d/%m/%Y')
	     + ' : ' + abjs[i][2].replace('{{{MESSAGE}}}', '')) ;
  return m.join('<br>') ;
}
DisplayMessages.need_node = ['Abjs'] ;

function DisplayNewSignature(node)
{
  if ( ! is_a_teacher )
    return '' ;
  return hidden_txt('<a href="javascript:signature_new(\''
		    + display_data['Login'] + '\')">'
		    + _("LABEL_signature_new") + '</a>',
		    _("TIP_signature_new")) ;
}
DisplayNewSignature.need_node = ['Login'] ;

function sign(t, message_id)
{
  if ( ! confirm(unescape(t.textContent || t.innerHTML)) )
     return ;
  t.parentNode.style.opacity = 0.5 ;
  var img = document.createElement('IMG') ;
  img.src = url + '/=' + ticket + '/signature/' + message_id
            + '/' + encode_uri(t.textContent) ;
  img.style.width = '20px' ;
  img.style.height = '20px' ;
  t.parentNode.insertBefore(img, t) ;
  var b = t.parentNode.getElementsByTagName('BUTTON') ;
  for(var i=0; i<b.length; i++)
     b[i].disabled = true ;

  var b = document.getElementsByTagName('BUTTON') ;
  for(var i=0; i<b.length; i++)
     if ( b[i].id != "signature_done" && ! b[i].disabled )
        return ;
  document.getElementById("signature_done").style.display = 'block' ;
}

function DisplayAskQuestion(node)
{
  return '<h2>' + hidden_txt(_('TITLE_signature')) + '</h2>'
    + node.data.join('') + '<hr>'
    + '<button id="signature_done" style="display:none" onclick="location.reload()">'
    + _('MSG_signature_done') + '</button>' ;
}

function DisplayAbjs(node)
{
  if ( node.data.length == 0 )
    return '' ;
  var t = [] ;
  for(var i in node.data)
    if ( node.data[i][2].substr(0, 13) != '{{{MESSAGE}}}' )
      t.push('<TR><TD>' + node.data[i][0] + '</TD><TD>' + node.data[i][1]
	     + '</TD><TD>' +  html(node.data[i][2])
	     + '</TD></TR>') ;
  if ( t.length == 0 )
    return '' ; // Only message and no ABJ
  
  return '<TABLE class="display_abjs colored"><tr>'
    + '<th>' + _("MSG_abjtt_from_before")
    + '<th>' + _("TH_until")
    + '<th>' + _("TH_comment")
    + t.join('')
    + '</table>' ;
}

function display_first_line(txt)
{
  txt = html(txt) ;
  if ( txt.indexOf('\n') == -1 )
    return txt ;
  var t = txt.split('\n') ;
  return t[0] + hidden_txt('<br><b>' + _("MSG_see_more") + '</b>',
			   t.slice(1, t.length).join('')) ;
}

function DisplayDA(node)
{
  if ( node.data.length == 0 )
    return '' ;
  
  var t = [] ;
  for(var i in node.data)
    t.push('<TR><TD>' + node.data[i][0] + '</TD><TD>' + node.data[i][1]
	   + '</TD><TD>' + display_first_line(node.data[i][2])
	   + '</TD></TR>') ;
  
  return '<TABLE class="display_abjs colored"><tr>'
    + '<th>' + _("TH_da_for_ue")
    + '<th>' + _("MSG_abj_tt_from")
    + '<th>' + _("TH_comment")
    + t.join('')
    + '</table>' ;
}

function DisplayRSS(node)
{
  if ( node.data === false )
    return '<iframe src="' + url + '/=' + ticket + '/rsskey"></iframe>' ;
  
  return hidden_txt('<a href="' + url_suivi + '/rss/' + node.data + '">'
		    + _("MSG_suivi_student_RSS")
		    + '<img src="' + url_files
		    + '/feed.png" alt="' + _("TIP_suivi_student_RSS")
		    + '" style="border:0px"></a>',
		    _("TIP_suivi_student_RSS"))
    + '<link href="' + url_suivi + '/rss/' + node.data
    + '" rel="alternate" title="TOMUSS" type="application/rss+xml">' ;
}

function DisplayLinksTable(node)
{
  if ( node.children.length == 0 )
    return '' ;
  var t = ['<table class="colored"><tr><th colspan="2">'
	   + _('SUIVI_linkstable') + '</tr>'] ;
  var i = 0 ;
  for(var ii in node.children)
    {
      if ( i % 2 == 0 )
	{
	  if ( i != 0 )
	    t.push('</tr>') ;
	  t.push('<tr>') ;
	}
      var c = display_display(node.children[ii]) ;
      if ( display_data['Preferences']['debug_suivi'] )
	{
	  t.push('<td>' + (c || ('<span class="displaygrey">'
				 + node.children[ii].name + '</span>'))) ;
	  i++ ;
	}
      else
	{
	  if ( c !== '' )
	    {
	      t.push('<td>' + c) ;
	      i++ ;
	    }
	}
    }
  if ( i % 2 == 1 )
    t.push('<td>&nbsp;') ;
  t.push('</tr></table>') ;
  return t.join('') ;
}
DisplayLinksTable.need_node = ['Preferences'] ;

function DisplayTT(node)
{
  return '<TABLE class="colored"><tr><th>' + _("MSG_suivi_student_tt")+'</tr>'
    + '<tr><td>' + html(node.data).replace(/\n/g,'<br>') + '</tr></table>' ;
}

function memberof_tree(lines, line, column, max, need_tr)
{
  var i ;
  for(i = line+1; i<max; i++)
    {
      if ( lines[i][column] !== lines[i-1][column] )
	break ;
    }
  var nb = i - line ;
  var s = '' ;
  if ( need_tr )
    s += '<tr>' ;
  s += '<td rowspan="' + nb + '">' + lines[line][column] ;
  if ( lines[line][column+1] === undefined )
    return {'html': s + '</tr>', 'nb': 1} ;
  i = line ;
  need_tr = false ;
  while(i < line+nb)
    {
      var r = memberof_tree(lines, i, column+1, line+nb, need_tr) ;
      s += r['html'] ;
      i += r['nb'] ;
      need_tr = true ;
    }
  return {'html': s, 'nb': nb} ;
}

function DisplayMemberOf(node)
{
  if ( ! is_a_teacher )
    return '' ;
  var grp, reversed = [] ;
  for(var i in node.data[0])
    {
      grp = node.data[0][i].split(',') ;
      grp.reverse() ;
      reversed.push(grp) ;
    }
  reversed.sort() ;

  // The 'overflow' indicates to the tip framework to not hide the tip
  var mo = '<div style="overflow:scroll; height:20em;overflow-x: hidden">'
     + '<table class="memberof">' ;
  for(var i=0; i<reversed.length; )
    {
      var r = memberof_tree(reversed, i, 0, reversed.length, true) ;
      mo += r['html'] ;
      i += r['nb'] ;
    }
  mo += '</table></div>' ;

  var etapes = '' ;
  for(var i in node.data[1])
    etapes += ' ' + hidden_txt(node.data[1][i][0], html(node.data[1][i][1])) ;
    
  return hidden_txt(_("MSG_suivi_student_memberof"), mo) + etapes ;
}

function DisplayACLS(node)
{
  if ( node.data === undefined || ! is_a_teacher)
    return '' ;
  var groups = [] ;
  for(var i in node.data)
    groups.push(i) ;
  groups.sort() ;
  var s = [] ;
  for(var i in groups)
    {
      i = groups[i] ;
      s.push(node.data[i] ? i : '<span style="color: #888">' + i + '</span>') ;
    }
  return '<div style="font-size: 80%">ACLS: ' + s.join(", ") + '</div>' ;
}

function DisplayStudents(node)
{
  var s = _("MSG_suivi_student_contact_for") + '<table class="colored">' ;
  for(var i in node.data)
    {
      s += '<tr>' ;
      for(j in node.data[i])
	s += '<td>' + html(node.data[i][j]) ;
      s += '</tr>' ;
    }
  return s + '</table>' ;
}

function DisplayTables(node)
{
  var s = [] ;
  if ( node.data.length == 0 )
    return '' ;
  node.data.sort() ;
  s.push('<hr>' + _("MSG_suivi_student_ue_changes")) ;
  for(var year=node.data[0][0]; year <= node.data[node.data.length-1][0];year++)
    {
      for(var sem=0; sem<semesters.length; sem++)
	{
	  var semester = semesters[sem] ;
	  var ss = [] ;
	  for(var i in node.data)
	    if ( node.data[i][0] == year && node.data[i][1] == semester )
	      ss.push('<a target="_blank" href="'
			+ url + '/=' + ticket + '/' + year
			+ '/' + semester + '/' + node.data[i][2]
			+ '/=full_filter=@' + display_data['Login'] + '">'
			+ node.data[i][2] + '</a><sup>'
			+ hidden_txt(node.data[i][3],
				       _("TH_suivi_student_nr_grades"))
			+ '</sup> ') ;
	  if ( ss.length )
	    s.push('<tr><td>' + year + '&nbsp;' + semester + '<td>'
		   + ss.join('') + '</tr>') ;
	}
    }
  return '<table class="colored">' + s.join('') + '</table>' ;
}
DisplayTables.need_node = ['Tables', 'Login'] ;

function DisplayMoreOnSuivi(node)
{
  return node.data ;
}


function tomuss_plusone()
{
  gapi.plusone.render('tomuss_plusone',
		      {
			'href': "http://perso.univ-lyon1.fr/thierry.excoffier/TOMUSS/home.html",
			  'size': 'medium'
			  }
		      ) ;

  function facebook(d, s, id) {
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) return;
    js = d.createElement(s); js.id = id;
    js.src = "https://connect.facebook.net/en_US/sdk.js#xfbml=1&appId=527673290646131&version=v2.0";
    fjs.parentNode.insertBefore(js, fjs);
  } ;
  facebook(document, 'script', 'facebook-jssdk');

}

function DisplayAdvertising(node)
{
  if ( node.data == false )
    return '' ;
  if ( ! tomuss_plusone.done )
    {
      setTimeout(tomuss_plusone, 1000) ;
      tomuss_plusone.done = true ;
      
      var po = document.createElement('script');
      po.type = 'text/javascript';
      po.async = true;
      po.defer = true;
      po.src = 'https://apis.google.com/js/platform.js';
      the_body.appendChild(po);
    }

  return '<div id="fb-root"></div><div style="margin-top:1em;"><small>' + _("DisplayAdvertising")
    + '&nbsp;:</small><br><div id="tomuss_plusone"></div><br>'
    + '<div class="fb-like" data-href="http://perso.univ-lyon1.fr/thierry.excoffier/TOMUSS/home.html" data-layout="button_count" data-action="like" data-show-faces="false" data-share="false"></div>' ;
}
DisplayAdvertising.need_node = [] ;


function DisplaySetReferentDo()
{
  var answer = prompt(_("MSG_suivi_student_set_referent_name")) ;
  if ( answer !== null && answer !== '' )
    {
      document.getElementById('DisplaySetReferent').innerHTML +=
	'<br><IFRAME style="width:100%;height:5em" src="'
	+ url + '/=' + ticket + '/referent_set_force/' + answer
	+ '/' + display_data['Login'] + '"></IFRAME>' ;
    }
}


function DisplaySetReferent(node)
{
  return '<div id="DisplaySetReferent"><a onclick="DisplaySetReferentDo()">'
    + _("MSG_suivi_student_set_referent") + '</a></div>' ;
}
DisplayAdvertising.need_node = ['SetReferent', 'Login'] ;


function DisplayGrpMessages(node)
{
  var s = '' ;
  for(var i in node.data)
    s += '<div>' + node.data[i] + '</div>' ;
  return s ;
}

function DisplayToTextual(node)
{
  var today = new Date() ;
  var img = special_days[today.getDate() +'/' + (today.getMonth()+1)] || "●" ;

  return '<a href="' + display_data['Login'] + '/*"'
    + (img ==  "●" ? '' : 'style="font-size:200%"') + '>'
    + img + '<span style="color: #FFF;font-size: 2px; opacity: 0.1">'
    + _("MSG_T_to_textual") + '</span></a>' ;
}
DisplayToTextual.need_node = ['Login'] ;

function DisplayT_Title(node)
{
  the_body.className = 'textual' ;
  return '<title>TOMUSS</title>' + year + ' ' + semester + ', '
    + display_data['T_Names'][0] + ' '
    + display_data['T_Names'][1] + ', '
    + display_data['T_Login'] + ', '
    + display_data['T_Names'][2] + '<br>'
    + _("MSG_suivi_student_important") ;
}
DisplayT_Title.need_node = ['T_Names', 'T_Login'] ;

function DisplayT_Message(node)
{
  return '<section><h2>' + html(node.data) + '</h2></section>' ;
}

function DisplayT_Messages(node)
{
  var m = DisplayMessages(node) ;
  var s = '' ;
  s += '<p>' + m + '</p>' ;
  for(var i in node.data)
    s += '<p>' + node.data[i] + '</p>' ;
  if ( s === '' )
    return "" ;
  return '<section><h2>' + _("MSG_T_Messages") + '</h2>' + s +  '</section>' ;
}
DisplayT_Messages.need_node = ['Abjs'] ;


function DisplayT_Grades_Lasts(node)
{
  display_data['Grades'] = display_data['T_Grades'] ; // Compatibility
  var one_month = millisec() - 30*24*3600000 ;
  var s = DisplayLastGradesList(one_month) ;
  var t  = [] ;
  for(var i in s)
    {
      DisplayUEGradesInit(s[i][0]) ;
      DisplayGrades.ue = s[i][0] ;
      DisplayGrades.column = columns[s[i][1]] ;
      t.push(DisplayT_Grades_Cell(true)) ;
    }
  return '<section><h2>' + _("MSG_T_last_grades") + '</h2>' + t.join("")
    + '</section>' ;
}
DisplayT_Grades_Lasts.need_node = ['T_Grades'] ;

var translated_acronyms = ["abi", "abj", "pre", "tnr", "ppn"] ;

function DisplayT_Grades_Cell(display_ue)
{
  var column = DisplayGrades.column ;
  DisplayGrades.cell = line[column.data_col] ;
  DisplayGrades.value = DisplayGrades.cell.value ;
  if ( DisplayGrades.value === '' )
    DisplayGrades.value = column.empty_is ;
  if ( DisplayGrades.value === '' && !cell_modifiable_on_suivi() )
    return '' ;
  DisplayGrades.cellstats = DisplayGrades.ue.stats[column.the_id] ||{};
  var sep = '<p>' ;
  var formula = '' ;
  var cellstats = DisplayGrades.cellstats ;
  var cell = DisplayGrades.cell ;
  if ( column.average_from && column.average_from.length )
    {
      formula = [] ;
      for(var i in column.average_columns)
	{
	  var col = columns[column.average_columns[i]] ;
	  var s = html(col.title).replace(/[-_]/g, " ") ;
	  if ( column.type == 'Moy' )
	    s += ' ' + _("MSG_T_weight") + ' ' + col.weight ;
	  formula.push(s) ;
	}
      formula = sep + _('B_' + column.type)
	+ ( column.type == 'Weighted_Percent' || column.type == 'Nmbr'
	    ? " '" + html(column.test_filter) + "'"
	    : '')
	+ ' : ' + formula.join(', ') ;
    }
  var formatted = column.real_type.formatte_suivi()
    .replace(RegExp('>/([0-9])'), '>' + _('MSG_T_on') + '$1')
    .replace(/0*<small/g, '<small')
    .replace(/[.]<small/g, '<small') ;
  var column_comment = html(column.comment) ;
  var comment = html(cell.comment) ;
  if ( ! cell_modifiable_on_suivi() )
    {
      //  PRST → Present
      for(var i in translated_acronyms)
	formatted = formatted.replace(RegExp(_(translated_acronyms[i])),
				      _('MSG_T_' + translated_acronyms[i])) ;
      var tip = formatted.replace(/.*(<table.*<.table>).*/, "$1") ;
      if ( tip !== formatted )
	{
	  // The only case is the Notation column type
	  comment = tip.replace("<table", '<table style="width:auto"') ;
	  column_comment = '' ;
	}
    }
  return '<section><h4>'
    + (display_ue ? html(DisplayGrades.ue.ue)
       + ' ' + html(DisplayGrades.ue.table_title || '') + ', ' : '')
    + html(column.title.replace(/[-_]/g, ' '))
    + ' : ' + formatted + '</h4>'
    + (column_comment
       ? sep + _('MSG_T_column_comment') + ' ' + column_comment
       : '')
    + (comment
       ? sep + _('MSG_T_cell_comment') + ' ' + comment
       : '')
    + (cell.author.length > 1
       ? sep + _('MSG_T_cell_author')+' '+html(cell.author.replace(/[.]/, ' '))
       : '')
    + (cell.author.length > 1
       ? sep + _('MSG_T_cell_date') + ' ' + date_full(cell.date)
       : '')
    + formula
    + (cellstats && column.real_weight_add && cellstats.rank !== undefined
       ? sep + _('MSG_T_rank_global') + ' ' + (cellstats.rank+1)
       + _('MSG_T_on') + DisplayGrades.cellstats.nr
       : '')
    + (cellstats && column.real_weight_add && cellstats.rank_grp !== undefined
       && cellstats.nr_in_grp != cellstats.nr
       ? sep + _('MSG_T_rank_group')
       + ' ' + (cellstats.rank_grp+1)
       + _('MSG_T_on') + cellstats.nr_in_grp
       : '')
    + (cellstats && cellstats.average !== undefined
       ? sep + _('MSG_T_average') + ' ' + cellstats.average.toFixed(2)
       + sep + _('MSG_T_mediane') + ' ' + cellstats.mediane.toFixed(2)
       : '')
    + '</section>'
    ;
}


function DisplayT_Grades(node)
{
  display_data['Grades'] = display_data['T_Grades'] ; // Compatibility
  var grades = display_data['T_Grades'][0] ;
  var u = [] ;
  for(var ue in grades)
    {
      ue = grades[ue] ;
      DisplayGrades.ue = ue ;
      DisplayUEGradesInit(ue) ;
      var ordered_columns = column_list_all() ;
      var g = [] ;
      for(var data_col in ordered_columns)
	{
	  data_col = ordered_columns[data_col] ;
	  if ( data_col < 3 )
	    continue ;
	  if ( columns[data_col].freezed == "C" )
	    continue ;
	  DisplayGrades.column = columns[data_col] ;
	  g.push(DisplayT_Grades_Cell()) ;
	}
      u.push('<section><h3>' + ue.ue + ' ' + html(ue.table_title || '')
	     + ((ue.masters && ue.masters.length != 0)
		? ', ' + _("MSG_T_masters") + ' ' + DisplayUEMasters()
		: '')
	     + '</h3>'
	     + '<a name="' + ue.ue + '">' + g.join('') + '</a></section>') ;
    }
  u.sort() ;

  return '<section><h2>' + _("MSG_T_UEs") + '</h2>' + u.join("") +'</section>';
}
DisplayT_Grades.need_node = ['T_Grades'] ;

function DisplayT_Abjs(node)
{
  display_data['Abjs'] = display_data['T_Abjs'] ; // Compatibility
  var m = DisplayAbjs(node) ;
  if ( m )
    return '<section><h2>' + _("MSG_T_Abjs") + '</h2>' + m + '</section>';
  else
    return '' ;
}

function DisplayT_DA(node)
{
  display_data['DA'] = display_data['T_DA'] ; // Compatibility
  var m = DisplayDA(node) ;
  if ( m )
    return '<section><h2>' + _("TITLE_abjtt_da")+'</h2>' + m + '</section>';
  else
    return '' ;
}

function DisplayT_TT(node)
{
  display_data['TT'] = display_data['T_TT'] ; // Compatibility
  var m = DisplayTT(node) ;
  if ( m )
    return '<section><h2>' + _("MSG_suivi_student_tt") + '</h2>'
      + m + '</section>' ;
  else
    return '' ;
}

function DisplayT_Semesters(node)
{
  display_data['Login'] = display_data['T_Login'] ; // Compatibility
  display_data['Semesters'] = display_data['T_Semesters'] ; // Compatibility
  var m = DisplaySemesters(node, true) ;
  if ( m )
    return '<section><h2>' + _("MSG_suivi_student_semesters")
      + '</h2>' + m + '</section>' ;
  else
    return '' ;
}
DisplayT_Semesters.need_node = ['T_Semesters', 'T_Login'] ;

function DisplayT_LinksTable(node)
{
  var s = [] ;
  var content = node.children[0].children ;
   for(var i in content)
     {
       c = display_display(content[i]) ;
       if ( c !== '' )
	 s.push(c.replace(/<div class=.(tipped|help)[^>]*>/g,
			  '<div style="display:inline">')
		.replace(/<div class="text">/g,
			 ' : <div style="display:inline">') 
		.replace(/(<div><.div>|<p>|<.p>)/g, '')) ;
     }
   return '<section><h2>' + _("MSG_T_informations") + '</h2>'
     + s.join("<br>") + '</section>' ;
}
DisplayT_LinksTable.need_node = [] ;
