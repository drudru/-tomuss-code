// -*- coding: utf-8; mode: Java; c-basic-offset: 2; tab-width: 8; -*-

var i_am_root ;
var unload_element ;
var the_body ;

/* To send the cell change and feedback */

function _cell(s, url)
{
  var url_s = url.split('/') ;
  var ue = url_s[url_s.length-4] ;

  iframe = document.createElement('iframe') ;
  iframe.className = 'feedback' ;
  if ( DisplayGrades.html_object )
    {
      var cell = DisplayGrades.html_object.parentNode.parentNode ;
      if ( cell.lastChild.tagName != 'IFRAME' )
	cell.appendChild(document.createElement('br')) ;
      cell.appendChild(iframe) ;
    }
  else
    s.parentNode.appendChild(iframe) ;

  DisplayGrades.html_object.value = s.value ;
  var new_s = DisplayGrades.column.real_type.cell_test(s.value,
						       DisplayGrades.column) ;
  if ( new_s !== undefined )
    s.value = new_s ;

  iframe.src = url + '/' + encode_uri(s.value) ;

  unload = document.createElement('IMG') ;
  unload.src = url_suivi + '/=' + ticket + '/unload/' + ue ;
  unload.width = unload.height = 1 ;
  the_body.appendChild(unload) ;

  hide_cellbox_tip() ;
  s.blur() ;
}

function hide_empty()
{
  set_style_content('.is_empty { display: none ; }') ;
}

function show_empty()
{
  set_style_content('.is_notempty { display: none ; }') ;
}

function set_style_content(content)
{
  hide_cellbox_tip() ;
  var s = document.getElementById('computed_style') ;
  if ( ! s )
    return ;
  while(s.firstChild)
    s.removeChild(s.firstChild) ;
  s.appendChild(document.createTextNode(content)) ;
}

function initialize_suivi_real()
{
  lib_init() ;
  instant_tip_display = true ;
  
  document.getElementById('top').innerHTML = '<div id="cellbox_tip"></div>'
    + '<style id="computed_style"></style>'
    + ( window.devicePixelRatio !== undefined
	? '<meta name="viewport" content="width=device-width,height=device-height,initial-scale=1">'
	: '' ) ;
  setTimeout(hide_empty, 10) ;
  i_am_root = myindex(root, username) != -1 ;
  my_identity = username ;
  column_get_option_running = true ; // Do not set option in URL
  the_body = document.getElementsByTagName('BODY')[0] ;
}

function cell_modifiable_on_suivi()
{
  table_attr = DisplayGrades.table_attr ;
  if ( ! DisplayGrades.cell.modifiable(DisplayGrades.column) )
    return ;
  if ( ! DisplayGrades.column.modifiable )
    return ;
  if ( DisplayGrades.column.modifiable == 2 )
    return true ;
  if ( is_a_teacher
       && DisplayGrades.column.modifiable == 1 ) // So modifiable == 1
    return true ;
}

function display_create_tree()
{
   for(var i in display_definition)
     {
       display_definition[i].children = [] ;
       display_definition[i].name = i ;
       display_definition[i].containers = display_definition[i][0] ;
       display_definition[i].priority = display_definition[i][1] ;
       display_definition[i].js = 'Display'
	 + (display_definition[i][2] || i ) ;
       display_definition[i].fct = eval(display_definition[i].js) ;
     }
   for(var i in display_definition)
     for(var j=0; j<display_definition[i].containers.length; j++)
       if ( ! display_definition[display_definition[i].containers[j]
				 ])
	 alert('Unknown parent for ' + i + ' ' + j ) ;
       else
	 display_definition[display_definition[i].containers[j]
			    ].children.push(display_definition[i]) ;
   for(var i in display_definition)
       display_definition[i].children.sort(function(a,b)
					   {return a.priority - b.priority;});
}

function display_display(node)
{
  node.data = display_data[node.name] ;
  if ( node.data === "" )
    return '' ;
  var need_node = node.fct.need_node ;
  if ( node.data === undefined && need_node === undefined)
    return '' ;  
  for(var i in need_node)
    if ( display_data[need_node[i]] === undefined )
      return '' ;
  var content = node.fct(node) ;
  var classes = ['Display', node.js, node.name] ;
  var styles = [] ;
  var more = '' ;
  if ( content instanceof Array)
    {
      classes = classes.concat(content[1]) ;
      styles = styles.concat(content[2]) ;
      more = ' ' + content[3] ;
      content = content[0] ;
    }
  if ( content === '' )
    return '' ;
  if ( styles.length )
    styles = ' style="' + styles.join(';') + '"' ;
  else
    styles = '' ;
  
  return '<div class="' + classes.join(' ') + '"' + styles + more + '>'
    + content + '</div>' ;
}

function detect_small_screen(force)
{
  if ( window_width() == detect_small_screen.window_width )
    return ;
  detect_small_screen.window_width = window_width() ;
      
  var smallscreen, not_working=0, width, lefts = [], div ;
  var divs = document.getElementsByTagName('DIV') ;
  var top_class = semester ;
  for(i = 0 ; i < divs.length ; i++)
    {
      div = divs[i] ;
      if ( div === undefined || div.className === undefined )
	continue ;
      if ( div.className.toString().match(/(DisplayExplanation|DisplayContact|DisplayLogout)/)
	   && ( div.offsetLeft < 10
		|| the_body.className.toString().indexOf("bad_inline_block") != -1 )
	   )
	not_working++ ;
      if ( div.className.toString().indexOf('BodyLeft') != -1 )
	{
	  lefts.push(div) ;
	  continue ;
	}
      if ( div.className.toString().indexOf('BodyRight') == -1 )
	continue ;
      if ( detect_small_screen.initial_width === undefined
	   || detect_small_screen.initial_width < div.offsetWidth )
	{
	  detect_small_screen.initial_width = div.offsetWidth ;
	}
      smallscreen = detect_small_screen.initial_width / window_width() > 0.35 ;
    }
  if ( not_working == 3 && window_width() > 300 )
    {
      top_class += ' bad_inline_block' ;
      smallscreen = false ;
    }
  if ( smallscreen === undefined )
    return ;
  if ( smallscreen )
    top_class += ' smallscreen' ;
  if ( the_body.className != top_class ) // To not relaunch CSS animation
    {
      the_body.className = top_class ;
      hide_rightclip() ;
    }
  detect_small_screen.small_screen = smallscreen ;
  var twidth = window_width() - (smallscreen
				? 100
				 : (detect_small_screen.initial_width + 30)
				) ; // +30 for FireFox
  if ( twidth > 100 )
    for(var i in lefts)
      lefts[i].style.width = twidth + 'px' ;
  hide_cellbox_tip() ;
}

var display_update_nb = 0 ;

function display_update(key_values, top)
{
  if ( display_update_nb == 1 )
    setInterval(detect_small_screen, 100) ;
  for(var i in key_values)
    display_data[key_values[i][0]] = key_values[i][1] ;
  document.write('<div id="display' + display_update_nb + '">'
		 + display_display(display_definition[top]) + '</div>') ;

  var old = document.getElementById('display' + (display_update_nb-1)) ;
  if ( old )
    old.parentNode.removeChild(old) ;

  display_update_nb++ ;
  detect_small_screen.window_width = 0 ; // Force update
  detect_small_screen() ;
}

function DisplayHorizontal(node, separator)
{
   var children = [] ;
   if ( separator === undefined )
     separator = '&nbsp;' ;
   if ( node.data !== undefined )
     children.push(node.data) ;
   var c ;
   for(var i in node.children)
     {
       c = display_display(node.children[i]) ;
       if ( c )
	 children.push(c) ;
     }
   return children.join(separator) ;
}
DisplayHorizontal.need_node = [] ;

function DisplayVertical(node)
{
  return DisplayHorizontal(node, '<br>\n') ;
}
DisplayVertical.need_node = [] ;

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
  var e = document.getElementById("rightclip") ;

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

function DisplayPicture(node)
{
  return hidden_txt('<img class="small" src="'
		    + student_picture_url(display_data['Login']) + '">',
		    '<img src="'
		    + student_picture_url(display_data['Login']) + '">') ;
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
  return '<a href="mailto:' + data[2] + '">'
    + data[0].substr(0,1)
    + data[0].substr(1).toLowerCase() + ' '
    + data[1] + '</a>' ;
}

function DisplayNames(node)
{
  return displaynames(node.data) ;
}

function DisplayReferent(node)
{
  switch(node.data[3])
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
  if ( display_data['Referent'][3] === undefined )
    ref = ',' + _("MSG_suivi_student_referent") + '<'
      + display_data['Referent'][2] + '>' ;
  else
    ref = '' ;

  return '<a href="mailto:?to='
    + node.data.join(',') + ref
    + '&subject=' + display_data['Login'] + ' '
    + display_data['Names'][0] + ' ' + display_data['Names'][1]
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

function DisplayEmptyCell(node)
{
  if ( ! is_a_teacher )
    return '' ;
  return '<a href="javascript:hide_empty()" class="is_empty">' + _("MSG_hide_empty_cells")
    + '</a><a href="javascript:show_empty()" class="is_notempty">'
    + _("MSG_show_empty_cells") + '</a>' ;
}
DisplayEmptyCell.need_node = [] ;

function DisplayReload(node)
{
  if ( ! is_a_teacher || ! i_am_root )
    return '' ;
  return '<a href="reload_plugins">' + _("TITLE_reload_plugins") + '</a>' ;
}
DisplayReload.need_node = [] ;

function DisplayProfiling(node)
{
  if ( ! is_a_teacher || ! i_am_root )
    return '' ;
  var t = [] ;
  for(var i in node.data)
    t.push([node.data[i], i]) ;
  t.sort(function(a,b) { return b[0] - a[0] ; }) ;
  return hidden_txt(_('LINK_profiling'), t.join('<br>')) ;
}

function DisplayExplanation(node)
{
  return '<span class="copyright">TOMUSS ' + node.data + '</span> '
    + '<a href="_FILES_/suivi_student_doc.html">' + _("MSG_help") + '</a>' ;
}
DisplayExplanation.need_node = [] ;

function DisplayContact(node)
{
  return '<a href="mailto:' + maintainer + '?subject='
    + encodeURI(_('MSG_suivi_student_mail_subject')) + '&body='
    + encodeURI(_('MSG_suivi_student_mail_body')).replace(/\n/g, '%0A')
    + '">' +  _('MSG_suivi_student_mail_link') + '</a>' ;
}
DisplayContact.need_node = [] ;

function DisplayLogout(node)
{
  return '<a href="' + url_suivi + '/=' + ticket + '/logout">'
    + _("LABEL_logout") +'</a> '
    + '<b>' + username + '</b>' ;
}
DisplayLogout.need_node = [] ;

function DisplayUETitle(node)
{
  var ue = DisplayGrades.ue ;
  var title = html(ue.ue + ' ' + (ue.table_title || '')) ;
  if ( is_a_teacher )
    {
      var url_table = url + '/=' + ticket + '/' + ue.year
	+ '/' + ue.semester + '/' + ue.ue ;
      title = '<a href="' + url_table + '" target="_blank">' + title + '</a>' ;
      title = hidden_txt(title, _("MSG_cell_full_table"));
      title += hidden_txt(' (<a href="' + url_table
			  + '/=filters=0_0:' + display_data['Login']
			  + '=" target="_blank">*</a>)',
			  _("MSG_cell_one_line")) ;
    }
  return '<a name="' + ue.ue + '">' + title + '</a>' ;
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

function DisplayUE(node)
{
  var s = DisplayVertical(node) ;
  for(var data_col in columns)
    if ( columns[data_col].freezed == "C"
	 && line[data_col].value.indexOf('non') != -1 )
      {
	s = '<div class="nonInscrit">'
	  + _("WARN_unregistered_student") + '<br><br>' + s + '</div>' ;
	break ;
      }

  return [s, [], [], 'onmouseenter="enter_in_ue(event)"'] ;
}
DisplayUE.need_node = [] ;


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

function DisplayCellRank(node)
{
  if ( DisplayGrades.cellstats === undefined )
    return ' ' ;
  if ( ! DisplayGrades.column.real_weight_add )
    return ' ' ;
    
  var s = ' ' ;
  if ( DisplayGrades.cellstats.rank !== undefined)
    s += DisplayGrades.cellstats.rank +'/'+  DisplayGrades.cellstats.nr + ' ' ;
  if ( DisplayGrades.cellstats.rank_grp !== undefined)
    s +=DisplayGrades.cellstats.rank_grp+'/'+DisplayGrades.cellstats.nr_in_grp;
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
  return ' <span class="displaygrey">' + _('Average') + '</span>&nbsp;'
    + DisplayGrades.column.do_rounding(DisplayGrades.cellstats.average)
    +  ' <span class="displaygrey">' + _('Mediane') + '</span>&nbsp;'
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
    + '&nbsp;</span>' + x ;
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
  return html(DisplayGrades.column.title.replace(/_/g, ' ')) ;
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
  if ( len < 50 )
    return t ;
  return [t, 'long_text', '', ''] ;
}
DisplayCellValue.need_node = [] ;

var display_saved = {} ;
var display_saved_nr = 0 ;

function enter_in_ue(event)
{
  var t = document.getElementById("cellbox_tip") ;
  if ( ! t || ! t.grades )
    return ;
  hide_cellbox_tip() ;
}

function hide_cellbox_tip()
{
  var t = document.getElementById("cellbox_tip") ;
  t.className = "hidden" ;
  if ( t.grades )
    t.grades.className = t.grades.className.toString()
      .replace(/ tip_displayed/g, "") ;
}

function display_cellbox_tip(event, nr)
{
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
  t.className = "" ;
  DisplayGrades.column = display_saved[nr][0] ;
  DisplayGrades.cell = display_saved[nr][1] ;
  DisplayGrades.html_object = c.getElementsByTagName('INPUT')[0]
    || c.getElementsByTagName('SELECT')[0] ;
  if ( DisplayGrades.html_object )
    DisplayGrades.value = DisplayGrades.html_object.value ;
  else
    DisplayGrades.value = display_saved[nr][2] ;
  DisplayGrades.cellstats = display_saved[nr][3] ;
  DisplayGrades.ue = display_saved[nr][4] ;
  DisplayGrades.formula = display_saved[nr][5] ;
  DisplayGrades.table_attr = display_saved[nr][6] ;
  DisplayGrades.no_hover = true ;
  t.innerHTML = display_display(display_definition['Cell']);
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
      if ( col.obfuscated )
	return '' ;
      s.push('<li>'
	     // + '<span class="displaygrey">' + _("B_"+col.type) + '</span> '
	     + column.average_from[i]
	     + ' <span class="displaygrey">' + _("BEFORE_column_attr_weight")
	     + '</span>&nbsp;' + col.weight
	     + display_tree(col) + '</li>'
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
  
  var ci = (grade - column.min) / (column.max - column.min) ;

  if ( ci > 0.8 ) return 'verygood' ;
  if ( ci > 0.6 ) return 'good' ;
  if ( ci > 0.4 ) return 'mean' ;
  if ( ci > 0.2 ) return 'bad' ;
  return 'verybad' ;
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
					 DisplayGrades.table_attr
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
      more = 'onmousemove="display_cellbox_tip(event,'
	+ display_saved_nr + ');" onmouseenter="display_cellbox_tip(event,'
	+ display_saved_nr + ');"' ;
      display_saved_nr++ ;
    }
  var classes = ['DisplayType' + DisplayGrades.column.type] ;
  var styles = [] ;
  if ( DisplayGrades.column.red + DisplayGrades.column.green
       + DisplayGrades.column.redtext + DisplayGrades.column.greentext != '' )
    classes.push(cell_class(DisplayGrades.cell, DisplayGrades.column)) ;
  else if ( DisplayGrades.column.real_weight_add )
    {
      if ( DisplayGrades.cellstats
	   && DisplayGrades.cellstats.rank !== undefined
	   && DisplayGrades.cellstats.nr >= 10
	   )
	styles.push(rank_to_color(DisplayGrades.cellstats.rank,
				  DisplayGrades.cellstats.nr)) ;
      else if ( (DisplayGrades.column.type == 'Moy'
		 || DisplayGrades.column.type == 'Note'
		 || DisplayGrades.column.type == 'Prst'
		 )
		&& DisplayGrades.cell.value !== '')
	classes.push(grade_to_class(DisplayGrades.column,
				    DisplayGrades.value)) ;
    }
    
  if ( DisplayGrades.cell.comment )
    styles.push('font-weight: bold') ;
  
  return [s, classes, styles, more] ;
}
DisplayCellBox.need_node = [] ;

var columns, line ;

function DisplayUEGrades(node)
{
  var ue = DisplayGrades.ue ;
  table_attr = undefined ;
  line = [] ;
  for(var i in ue.line)
    {
      i = ue.line[i] ;
      line.push(C(i[0], i[1], i[2], i[3])) ;
    }
  columns = [] ;
  for(var i in ue.columns)
    columns.push(Col(ue.columns[i])) ;
  
  for(var data_col in columns)
    {
      init_column(columns[data_col]) ;
      columns[data_col].data_col = data_col ;
    }
  update_columns(line);

  DisplayGrades.table_attr = ue ;
  var s = '' ;
  for(var data_col in columns)
    {
      if ( data_col < 3 )
	continue ;
      if ( columns[data_col].freezed == "C" )
	continue ;
      DisplayGrades.cell = line[data_col] ;
      DisplayGrades.column = columns[data_col] ;
      DisplayGrades.value = line[data_col].value ;
      if ( DisplayGrades.value === '' )
	DisplayGrades.value = DisplayGrades.column.empty_is ;
      DisplayGrades.cellstats = DisplayGrades.ue.stats[data_col] || {} ;
      var ss = display_display(display_definition['CellBox']);
      if ( DisplayGrades.value === '' && ! cell_modifiable_on_suivi())
	ss = ss.replace('class="', 'class="is_empty ') ;
      s += ss ;
    }
  return s ;
}
DisplayUEGrades.need_node = [] ;

function DisplayGrades(node)
{
  if ( node.data === undefined )
    return '<span style="background:#FF0">' + _("MSG_suivi_student_wait")
      + '</span>' ;

  node.data[0].sort(function(a,b) { return b.ue < a.ue ? 1 : -1 ; }) ;
  var s = '' ;
  for(var i in node.data[0])
    {
      DisplayGrades.ue = node.data[0][i] ;
      s += display_display(display_definition['UE']) ;
    }
  for(var i in node.data[1])
    {
      var t = node.data[1][i][0] + ' ' + node.data[1][i][1] ;
      if ( is_a_teacher )
	s += '<p class="title">' + _("MSG_suivi_student_registered")+t+'</p>';
      else
	s += '<h2 class="title">' + _("MSG_suivi_student_not_in_TOMUSS_before")
	  + t + '</h2><p>' + _("MSG_suivi_student_not_in_TOMUSS_after") ;
    }

  return '<hr>' + s ;
}
DisplayGrades.need_node = ['Login'] ;

function goto_cellbox(o)
{
  window.location.hash = o.innerHTML.split('<')[0] ;
}

function DisplayLastGrades(node)
{
  if ( is_a_teacher )
    return '' ;
  var grades = display_data['Grades'][0] ;
  var s = [] ;
  var one_week = millisec() - 7*24*3600000 ;
  
  for(var ue in grades)
    {
      ue = grades[ue] ;
      for(var data_col in ue.line)
	{
	  var cell = ue.line[data_col] ;
	  if ( cell[0] === '' )
	    continue ;
	  if ( cell[2] === undefined
	       || get_date_tomuss(cell[2]).getTime() < one_week )
	    continue ;
	  if ( cell[1].length < 2 )
	    continue ; // System value
	  s.push([ue, data_col]) ;
	}
    }
  if ( s.length == 0 )
    return '' ;
  s.sort(function(a, b) {
      return a[0].line[a[1]][2] < b[0].line[b[1]][2] ? 1 : -1
	}) ;
  var t = [] ;
  var today = new Date() ;
  today.setHours(0) ;
  today.setMinutes(0) ;
  today.setSeconds(0) ;
  today = today.getTime() ;
  var daynames = [_("LABEL_Day0"), _("LABEL_Day1"), _("LABEL_Day2")] ;
  var lastday ;
  for(var i in s)
    {
      var ue = s[i][0] ;
      var data_col = s[i][1] ;
      var cell = ue.line[data_col] ;
      var quand = get_date_tomuss(cell[2]) ;
      quand.setHours(0) ;
      quand.setMinutes(0) ;
      quand.setSeconds(0) ;
      quand = quand.getTime() ;
      var column = ue.columns[data_col] ;
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
      
      t.push('<div onclick="goto_cellbox(this)" class="Display a_grade">'
	     + ue.ue
	     + '<br>' + html(column.title)
	     + '<br><span>' + html(cell[0]) + "</span></div>") ;
    }
  return '<hr>' + t.join('') ;
}
DisplayLastGrades.need_node = ['Grades'] ;

function DisplayLogo(node)
{
  if ( node.data === '' || node.data == 'http://xxx.yyy.zzz/logo.png' )
    return '' ;
  return '<img src="' + node.data + '">' ;
}

function DisplaySemesters(node)
{
  var y = year, s = semester ;
  if ( node.data[y + '/' + s] === undefined )
    return '' ;
  var ys ;
  do
    {
      ys = previous_year_semester(y, s) ;
      
      if ( node.data[ys[0] + '/' + ys[1]] === undefined )
	break ;

      y = ys[0] ;
      s = ys[1] ;
    }
  while(1) ;
  s = semesters[0] ; // First semester of the real year
      
  var t = [], highlight ;
  do
    {
      if ( s == semesters[0] )
	t.push('</tr><tr><td>' + y + '</td>') ;
      if ( y == year && s == semester)
	highlight = ' style="background: #FF0"' ;
      else
	highlight = '' ;

      if (is_a_teacher)
	icone = '<img class="icone" src="' + node.data[y + '/' + s] + '/_'
	  + display_data['Login'] + '">' ;
      else
	icone = '' ;
      if ( node.data[y + '/' + s] )
	t.push('<td' + highlight + '><a href="' + node.data[y + '/' + s]
	       + '/=' + ticket + '/' + display_data['Login'] + '">'
	       + icone + s + '</a></td>') ;
      else
	t.push('<td>&nbsp;</td>') ;

      ys = next_year_semester(y, s) ;
      y = ys[0] ;
      s = ys[1] ;
    }
  while(node.data[y + '/' + s] || s != semesters[0]) ;
  return '<table class="tomuss_links colored">'
    + '<tr><th colspan="3">'
    + hidden_txt(_("MSG_suivi_student_semesters"),
		 _("TIP_suivi_student_semesters"))
    + t.join('\n') + '</tr></table>' ;
}
DisplaySemesters.need_node = ['Semesters', 'Login'] ;


function catch_this_student(event, login)
{
  event = the_event(event) ;
  if ( confirm(_('MSG_bilan_take_student')) )
    {
      create_popup('import_div',_('MSG_bilan_take_student'),
		   '<iframe src="' + url + '/=' + ticket + '/referent_get/'
		   + display_data['Login']
		   + '" style="width:100%;height:5em">iframe</iframe>',
		   '', false) ;
    }
}

function DisplayGetStudent(node)
{
  if ( ! is_a_teacher )
    return '' ;
  if ( display_data['Referent'][4] == username )
    return '' ; // I am yet its referent

  return hidden_txt('<img onclick="catch_this_student(event)" '
		    + 'src="' + url_files
		    + '/butterflynet.png">', _('MSG_bilan_take_student'));
}
DisplayGetStudent.need_node = ['Referent'] ;

function DisplayIsPrivate(node)
{
  return _("MSG_suivi_student_private") ;
}
DisplayIsPrivate.need_node = [] ;

function DisplayPreamble(node)
{
  if ( is_a_teacher )
    return '' ;
  return '<title>TOMUSS</title>' + _("MSG_suivi_student_important") ;
}
DisplayPreamble.need_node = [] ;

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
    t.push('<TR><TD>' + node.data[i][0] + '</TD><TD>' + node.data[i][1]
	   + '</TD><TD>' +  html(node.data[i][2])
	   + '</TD></TR>') ;
  
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
		    + '/feed.png" style="border:0px"></a>',
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
      if ( i_am_root )
	{
	  t.push('<td>' + (c || ('<span class="displaygrey">'
				 + node.children[ii].name))) ;
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
DisplayLinksTable.need_node = [] ;

function private_toggle()
{
  window.location = url + '/=' + ticket + '/private/'
    + (1-display_data['PrivateLife']) ;
}

function popup_private()
{
  create_popup('private_div',
	       _("LINK_suivi_student_private"),
	       _("MSG_suivi_student_private_full")
	       + '<p><button onclick="private_toggle()">'
	       + (display_data['PrivateLife']
		  ? _("MSG_suivi_student_private_public")
		  : _("MSG_suivi_student_private_private"))
		  + '</button>',
	       '', false
	      );
}

function DisplayPrivateLife(node)
{
  if ( ! is_a_teacher )
    return hidden_txt('<a href="javascript:popup_private();undefined"'
		      + (node.data ? ' class="bad"' : '') + '>'
		      + _("LINK_suivi_student_private") + '</a>',
		      _("TIP_suivi_student_private")
		      ) ;
  if ( node.data )
    return hidden_txt(_("LINK_suivi_student_private"),
		      _("MSG_suivi_student_private"), 'bad') ;
  return '' ;
}

function DisplayTT(node)
{
  return '<TABLE class="colored"><tr><th>' + _("MSG_suivi_student_tt")+'</tr>'
    + '<tr><td>' + html(node.data).replace(/\n/g,'<br>') + '</tr></table>' ;
}

function DisplayMemberOf(node)
{
  if ( ! is_a_teacher )
    return '' ;
  
  var mo = '<table class="memberof">' ;
  for(var i in node.data[0])
    mo += '<tr><td>' + node.data[0][i].replace(/,/g, '<td>') + '</tr>' ;
  mo += '</table>' ;

  var etapes = '' ;
  for(var i in node.data[1])
    etapes += ' ' + hidden_txt(node.data[1][i][0], html(node.data[1][i][1])) ;
    
  return hidden_txt(_("MSG_suivi_student_memberof"), mo) + etapes ;
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

function DisplayMoreOnSuivi(node)
{
  return node.data ;
}
