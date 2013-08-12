/*
    TOMUSS: The Online Multi User Simple Spreadsheet
    Copyright (C) 2009-2011 Thierry EXCOFFIER, Universite Claude Bernard

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

function table_linear()
{
   window.location = url +'/='+ticket+'/'+year+'/'+semester+'/'+ue+'/=linear=';
}

// XXX: live connection does not work

function Linear()
{
  /////////////////////////////////////////////////////////////////////////////
  /////////////////////////////////////////////////////////////////////////////
  /////////////////////////////////////////////////////////////////////////////
  this.informations_cell =
    [
     new Information
     (this,
      function() {
       if ( this.L.column().real_type.cell_compute )
	 return this.L.column().type + _("MSG_tablelinear_not_modifiable") ;
       else
	 return _("MSG_tablelinear_value") ;
     },
      _("LABEL_tablelinear_value"),
      function() {
	var value = this.L.cell().value ;
	if ( value.toFixed && value !== 0 )
	  value = tofixed(value).replace(/[.]*0*$/,'') ;
	return value ;
      },
      function(value) { cell_set_value_real(this.L.line_id(),
					    this.L.data_col(),
					    value);
      },
      function() {
	if ( this.L.column().real_type.cell_compute )
	    return _("ERROR_tablelinear_value_not_modifiable") ;
	return this.L.cell().changeable(this.L.column()) ;
      },
      function() {
	var h = _(this.L.column().real_type.tip_cell) ;
	if ( this.L.column().type == 'Note' )
	    h = _("TIP_tablelinear_grade_between") + this.L.column().min
	      + _("TIP_tablelinear_and") + this.L.column().max
	      + '. ' + h ;
        return h + '.' ;
      }
      ),
     new Information
     (this,
      function() { return _("MSG_tablelinear_value_author") ; },
      _("LABEL_tablelinear_value_author"),
      function() { return this.L.cell().author ; }
      ),
     new Information
     (this,
      function () { return _("MSG_tablelinear_value_date") },
      _("LABEL_tablelinear_value_date"),
      function() { return date_full(this.L.cell().date) ; }
      ),
     new Information
     (this,
      function() { return _("MSG_tablelinear_value_comment") ; },
      _("LABEL_tablelinear_value_comment"),
      function() { return this.L.cell().comment ; },
      function(value) { comment_change(this.L.line_id(),
				       this.L.data_col(),
				       value);
      },
      function() { return table_attr.modifiable ? true :
		   _("MSG_tablelinear_table_not_modifiable") ; }
      ),
     new Information
     (this,
      function() { return _("MSG_tablelinear_registered"); },
      '',
      function() {
	var w ;
	if ( this.L.line()[5].value != 'ok' )
	    w = _("MSG_tablelinear_registered_no") ;
	else
	    w = _("MSG_tablelinear_registered_yes") ;
	w += '<br>' + student_abjs(this.L.line()[0].value) ;
	return '\001' + w.replace(/[.]<br>$/,'') ; // \001 indicate HTML code
      }
      ),
     new Information
     (this,
      function() { return _("MSG_tablelinear_rank") ; },
      _("LABEL_tablelinear_rank"),
      function() { return compute_rank(this.L.line_id(), this.L.column()).replace('&nbsp;','').replace('/', _("MSG_tablelinear_rank_on")) ; }
      ),
     new Information
     (this,
      function() { return _("MSG_tablelinear_history") },
      _("LABEL_tablelinear_history"),
      function() { return this.L.cell().history ; }
      )
     ] ;
  /////////////////////////////////////////////////////////////////////////////
  /////////////////////////////////////////////////////////////////////////////
  /////////////////////////////////////////////////////////////////////////////
  this.informations_column =
    [
     new Information
     (this,
      function() {return _("MSG_tablelinear_column_title") ; },
      _("LABEL_tablelinear_column_title"),
      function() { return this.L.column().title ; },
      function(value) {
	// this.L.column().real_type.set_title(value, this.L.column());
	column_attr_set(this.L.column(), 'title', value) ;
      },
      function() { return column_change_allowed_text(this.L.column()) ; },
      function() { return _("TIP_tablelinear_column_title") ; }
      ),
     new Information
     (this,
      function() {return _("TIP_column_attr_type") ; },
      _("LABEL_tablelinear_column_type"),
      function() { return this.L.column().type ; },
      function(value) {
	column_attr_set(this.L.column(), 'type', value) ;
	this.L.update_column() ;
      },
      function() { return column_change_allowed_text(this.L.column()) ; },
      function() { return _("TIP_tablelinear_column_type") ; }
      ),
     new Information
     (this,
      function() {return _("TIP_column_attr_weight") ; },
      _("LABEL_tablelinear_column_weight"),
      function()
      {
	var column = this.L.column() ;
	if ( column.real_type.set_weight != unmodifiable )
	  return column.real_weight ;
	else
	  return "" ;
      },
      function(value) {
	column_attr_set(this.L.column(), 'weight', value) ;
	this.L.update_column() ;
      },
      function() { return column_change_allowed_text(this.L.column()) ; },
      function() { return _("MSG_tablelinear_column_weight") ; }
      ),
     new Information
     (this,
      function() {return _("TIP_column_attr_minmax") ; },
      _("LABEL_tablelinear_column_minmax"),
      function()
      {
	var column = this.L.column() ;
	if ( column.real_type.set_test != unmodifiable )
	  return column.min + ' ' + column.max ;
	else
	  return "" ;
      },
      function(value) {
	column_attr_set(this.L.column(), 'minmax', value) ;
	this.L.update_column() ;
      },
      function() { return column_change_allowed_text(this.L.column()) ; },
      function() { return _("MSG_tablelinear_column_minmax");}
      ),
     new Information
     (this,
      function() { return _("MSG_tablelinear_column_columns") ; },
      _("LABEL_tablelinear_column_columns"),
      function()
      {
	var column = this.L.column() ;
	if ( column.average_from !== undefined )
	  return column.average_from.toString().replace(/,/g,' ') ;
	else
	    return _("ERROR_tablelinear_column_columns_na") ;
      },
      function(value) {
	column_attr_set(this.L.column(), 'columns', value) ;
	this.L.update_column() ;
      },
      function() {
	var column = this.L.column() ;
	if ( column.real_type.set_weight == unmodifiable )
	    return _("ERROR_tablelinear_column_columns_na2") + column.type ;
	return column_change_allowed_text(column) ;
      },
      function() { return _("TIP_tablelinear_column_columns") ;}
      ),
     new Information
     (this,
      function() { return _("MSG_tablelinear_column_comment") ; },
      _("LABEL_tablelinear_column_comment"),
      function() { return this.L.column().comment ; },
      function(value) {
	column_attr_set(this.L.column(), 'comment', value) ;
      },
      function() { return column_change_allowed_text(this.L.column()) ; },
      function() { return _("TIP_tablelinear_column_comment");}
      ),
     new Information
     (this,
      function() {return _("MSG_tablelinear_column_emptyis") ; },
      'ø',
      function() {return this.L.column().empty_is ; },
      function(value) {
	column_attr_set(this.L.column(), 'empty_is', value) ;
	this.L.update_column() ;
      },
      function() { return column_change_allowed_text(this.L.column()) ; },
      function() {
	var column = this.L.column() ;
	if ( column.type == 'Note' )
	    return _("TIP_tablelinear_column_emptyis_note") ;
        return _("TIP_tablelinear_column_emptyis") ;
      }
      ),
     new Information
     (this,
      function() {return _("MSG_tablelinear_column_stats"); },
      '',
      function() {
	var stats = compute_histogram(this.L.data_col()) ;
	var s ;
	if ( stats.nr )
	    s = stats.nr + ' ' + _("grades") + '. '
	      + _("Average") + ' ' + tofixed(stats.average()) + '. '
	      + _("Mediane") + ' ' + tofixed(stats.mediane()) + '. '
	      + _("Standard-deviation") + ' '
	      + tofixed(stats.standard_deviation()) + '. '
	      + _("Minimum") + ' ' + tofixed(stats.min) + '. '
	      + _("Maximum") + ' ' + tofixed(stats.max)+ '.' ;
	else
	    s = _("MSG_tablelinear_no_grade") ;
	if ( stats.nr_ppn)s+=' '+stats.nr_ppn()+' '+_("MSG_columnstats_ppn")+'.';
	if ( stats.nr_abi)s+=' '+stats.nr_abi()+' '+_("MSG_columnstats_abi")+'.';
	if ( stats.nr_abj)s+=' '+stats.nr_abj()+' '+_("MSG_columnstats_abj")+'.';
	if ( stats.nr_pre)s+=' '+stats.nr_pre()+' '+_("MSG_columnstats_pre")+'.';
	if ( stats.nr_yes)s+=' '+stats.nr_yes()+' '+_("MSG_columnstats_yes")+'.';
	if ( stats.nr_no )s+=' '+stats.nr_no() +' '+_("MSG_columnstats_no") +'.';
	if ( stats.nr_nan)
	    s += ' ' + stats.nr_nan() + ' ' + _("MSG_columnstats_empty") ;
	return s.substr(0, s.length-1) ;
	}
      ),
     new Information
     (this,
      function() { return _("MSG_tablelinear_filter")
		   + "<a href=\"" + url + '/doc_filtre.html" target="_new_">'
		   + _("MSG_tablelinear_filter_doc") + '</a>.' ; },
      _("LABEL_tablelinear_filter"),
      function() { return this.L.column().filter ; },
      function(value) {
	var column = this.L.column() ;
	column.filter = value ;
        set_filter_generic(value, column) ;
	update_filters() ;
	update_filtered_lines() ;
	this.L.lin = 0 ;
      },
      function() { return true ; },
      function() { return _("TIP_tablelinear_filter"); }
      )
     ] ;
  /////////////////////////////////////////////////////////////////////////////
  /////////////////////////////////////////////////////////////////////////////
  /////////////////////////////////////////////////////////////////////////////
  this.informations_table =
    [
     new Information
     (this,
      function() {return _("MSG_tablelinear_table_stats") ; },
      '',
      function() { return filtered_lines.length
		   + _("MSG_tablelinear_table_lines") + nr_not_empty_lines ; }
      ),
     new Information
     (this,
      function() {return _("MSG_tablelinear_table_comment");},
      _("LABEL_tablelinear_table_comment"),
      function() { return table_attr.comment ; },
      function(value) {
	table_attr_set('comment', value) ;
      },
      function() {
	if ( table_attr.modifiable && (i_am_the_teacher||teachers.length == 0))
	  return true ;
	  return _("ERROR_tablelinear_table_comment");
      },
      function() { return _("TIP_tablelinear_table_comment") ; }
      ),
     new Information
     (this,
      function() {return _("MSG_tablelinear_table_masters");},
      _("LABEL_tablelinear_table_masters"),
      function() { return teachers.toString().replace(/,/g,' ') ; },
      function(value) {
	table_attr_set('masters', value) ;
      },
      function() {
	if ( table_attr.modifiable&&(i_am_the_teacher||teachers.length == 0) )
	  return true ;
        return _("ERROR_tablelinear_table_masters");
      },
      function() { return _("TIP_tablelinear_table_masters") ; }
      )
     ] ;
  /////////////////////////////////////////////////////////////////////////////
  /////////////////////////////////////////////////////////////////////////////
  /////////////////////////////////////////////////////////////////////////////
  this.informations = this.informations_cell
  this.information = this.informations[0] ;
  this.col = 3 ;
  this.lin = 0 ;
  this.top = document.getElementById('top') ;
  this.input_edit = false ;
  this.w('<h1>' + ue + ' ' + semester + ' ' + year + '</h1>' +
         '<h2>' + table_attr.table_title + '</h2>'
	 + _("MSG_tablelinear_welcome")) ;
}


var linear_w_real_queue = [] ;

function linear_w_real()
{
  if ( L === undefined )
    return ;
  if ( linear_w_real_queue.length !== 0 )
    {
      var c = '' ;
      while(linear_w_real_queue.length !== 0)
	{
	  c += '<br>' + linear_w_real_queue.splice(0,1)[0] ;
	}
      var e = document.createElement('div') ;
      e.innerHTML = c.substr(4) ; // Remove first <br>
      L.top.appendChild(e) ;
      scrollTop(10000000) ;
    }
  if ( L.input_to_init !== undefined )
    {
      L.input_edit = true ;
      L.input.value = L.input_to_init ;
      L.input.initial_value = L.input.value ;
      L.input_to_init = undefined ;
      L.input.style.display = '' ;
      L.input.select() ;
      L.input.focus() ;
      scrollTop(10000000) ;
    }
}

if ( window.location.pathname.search('/=linear=') != -1 )
  setInterval(linear_w_real, 100) ;

function linear_w(x)
{
  linear_w_real_queue.push(x) ;
}


function column_list_all2()
{
  var t = column_list_all() ;
  t.push( add_empty_columns() ) ;
  return t ;
}

function linear_data_col() { return column_list_all2()[this.col]      ; }
function linear_line_id()  { return this.line().line_id               ; }
function linear_column()   { return columns[this.data_col()]          ; }
function linear_cell()     { return this.line()[this.data_col()]      ; }
function linear_line()
{
  // update_filtered_lines() ;
  if ( this.lin < filtered_lines.length )
    return filtered_lines[this.lin] ;
  else
    {
      if ( this.lin != filtered_lines.length )
	alert('There is a bug') ;
      add_a_new_line() ;
      return filtered_lines[this.lin] ;
    }
}

function linear_column_title()
{
  if ( this.hide_column_title )
    return '' ;
  var empty = '' ;
  if ( this.column().is_empty )
      empty = _("MSG_tablelinear_is_empty") ;
    return _("TAB_column") + ' <i>' + html(this.column().title) + '</i>'
	+ empty + ', ' ;
}

function linear_line_title()
{
  if ( this.hide_line_title )
    return '' ;
  var cls = column_list_all2() ;
  var s = '' ;
  var line = this.line() ;
  for(var data_col in cls)
    {
      data_col = cls[data_col] ;
      if ( columns[data_col].freezed == 'F' )
	s += line[data_col].value + ', ' ;
    }
  if ( s.replace(/, /g, '') === '' )
      s = _("MSG_tablelinear_enter_id") ;
  return s ;
}

function linear_update_column()
{
  var column = this.column() ;
  init_column(column) ;
  column.need_update = true ;
  update_columns() ;
}

function linear_go_right(quiet)
{
  this.hide_column_title = this.hide_line_title = this.hide_what = quiet ;
  var cls = column_list_all2() ;
  this.col++ ;
  if ( this.col >= cls.length )
    {
      this.col = cls.length - 1 ;
	this.w(_("MSG_tablelinear_nothing_right")) ;
    }
  this.hide_line_title = true ;
  this.display() ;
  return true ;
}

function linear_go_left(quiet)
{
  this.hide_column_title = this.hide_line_title = this.hide_what = quiet ;
  this.col-- ;
  this.hide_line_title = true ;
  if ( this.col < 0  )
    {
      this.col = 0 ;
	this.w(_("MSG_tablelinear_nothing_left")) ;
    }
  this.display() ;
  return true ;
}

function linear_go_down(quiet)
{
  this.hide_column_title = this.hide_line_title = this.hide_what = quiet ;
  // update_filtered_lines() ;
  this.lin++ ;
  this.hide_column_title = true ;
  if ( this.lin >= filtered_lines.length  )
    {
      this.lin = filtered_lines.length ;
      this.w(_("MSG_tablelinear_nothing_under")) ;
    }
  this.display() ;
  return true ;
}

function linear_go_up(quiet)
{
  this.hide_column_title = this.hide_line_title = this.hide_what = quiet ;
  this.lin-- ;
  this.hide_column_title = true ;
  if ( this.lin < 0 )
    {
      this.lin = 0 ;
      this.w(_("MSG_tablelinear_nothing_above")) ;
    }
  this.display() ;
  return true ;
}

function linear_change_show(quiet)
{
  var i = myindex(this.informations, this.information) ;
  if ( i != -1 )
    {
      i = (i+1) % this.informations.length ;
      this.information = this.informations[i] ;
    }

  this.hide_column_title = this.hide_line_title = true ;
  this.hide_what = quiet ;
  this.display() ;
  return true ;
}

function linear_set_show(quiet, table, n, col)
{
  var c ;

  if ( this.informations == table && n === undefined )
    {
      this.change_show() ;
      return true ;
    }
  if ( n === undefined )
    c = 0 ;
  else
    {
      c = n ;
      this.informations_save = this.informations ;
      this.information_save = this.information ;
      this.col_save = this.col ;
      if ( col !== undefined )
	{
	  var cls = column_list_all() ;
	  for(var i in cls)
	    {
	      if ( columns[cls[i]].title == col )
		{
		  this.col = i ;
		  break ;
		}
	    }
	}
    }

  this.informations = table ;
  this.information = table[c] ;

  if ( ! quiet )
    this.display() ;
  if ( n !== undefined )
    this.edit(quiet) ;
  return true ;
}

function linear_onkeypress(event)
{
  event = the_event(event) ;
  if ( event.keyCode == 13 )
    {
      stop_event(event) ;
      L.stop_edit() ;
      return false ;
    }
  if ( event.keyCode != 27 )
    return true ;
  L.w(_("MSG_tablelinear_cancel")) ;
  L.stop_edit(true) ;
  stop_event(event) ;
}

function linear_edit(quiet)
{
  var changeable = this.information.is_changeable() ;
  if ( changeable != true )
    {
      this.w(changeable) ;
      return true ;
    }
  if ( quiet != true && this.information.content )
    this.w(this.information.content());
  this.input_to_init = this.information.get_value() ;
  return true ;
}

function linear_stop_edit(abort)
{
  if ( ! this.input_edit ) // OPERA
    return ;
  if ( this.input.value != this.input.initial_value && abort === undefined )
    this.information.change(this.input.value) ;
  this.input_edit = false ;
  this.input.value = '' ;
  this.input.style.display = 'none' ;

  if ( this.informations_save !== undefined )
    {
      if ( ! abort )
	this.display() ;

      this.informations = this.informations_save ;
      this.information = this.information_save ;
      this.col = this.col_save ;
      this.informations_save = undefined ;
      this.information_save = undefined ;
      this.col_save = undefined ;

      if ( abort )
	return ;
    }
  else
    {
      if ( abort )
	return ;

      this.hide_column_title = this.hide_line_title = true ;
    }
  this.display() ;

  update_line(this.line_id(), this.data_col()) ;

  if ( this.informations == this.informations_column )
    {
      columns[this.data_col()].need_update = true ;  
      update_columns() ;
    }
}

function linear_display()
{
  this.w(this.information.value()) ;
  this.hide_column_title = false ;
  this.hide_line_title = false ;
  this.hide_what = false ;
}

function linear_tip()
{
  var r = this.information.help() ;

  if ( this.information.is_changeable
       && this.information.is_changeable() == true )
      r += _("MSG_tablelinear_enter_to_edit") ;

  this.w(r) ;
  return true ;
}

function linear_sort(dir)
{
  var sorted = false ;
  if ( this.column() != sort_columns[0] )
    {
      sort_column(undefined, this.data_col()) ;
      sorted = true ;
    }
  if ( this.column().dir != dir )
    {
      sort_column(undefined, this.data_col()) ;
      sorted = true ;
    }
  if ( ! sorted ) // force the sort (the user modified the table)
    {
      sort_column(undefined, this.data_col()) ;
      sort_column(undefined, this.data_col()) ;
    }
    var s = _("MSG_tablelinear_sort_before") + "<i>"
	+ this.column().title + "</i>" + _("MSG_tablelinear_sort_after") ;
  if ( dir == 1 )
      s += _("MSG_tablelinear_sort_up") ;
  else
      s += _("MSG_tablelinear_sort_down") ;
  this.w(s) ;
  update_filtered_lines() ;
  this.display() ;
  return true ;
}

function linear_freeze()
{
  if ( this.column().freezed )
      this.w(_("MSG_tablelinear_freezed")) ;
  else
      this.w(_("MSG_tablelinear_unfreezed")) ;
  freeze_column(this.column()) ;
  return true ;
}

function linear_hide()
{
    this.w(_("MSG_tablelinear_hide_before") + "<i>" + html(this.column().title)
	   + "</i>" + _("MSG_tablelinear_hide_after")) ;
  this.column().hidden = 1 ;
  this.display() ;
  return true ;
}

function linear_print()
{
  print_page() ;
  return true ;
}

function linear_suivi()
{
  window.open(suivi + '/ ' + this.line()[0].value) ;
}


function linear_help()
{
  this.w(_("MSG_tablelinear_doc")) ;
  return true ;
}

Linear.prototype.data_col            = linear_data_col            ;
Linear.prototype.line_id             = linear_line_id             ;
Linear.prototype.cell                = linear_cell                ;
Linear.prototype.line                = linear_line                ;
Linear.prototype.column              = linear_column              ;
Linear.prototype.update_column       = linear_update_column       ;
Linear.prototype.column_title        = linear_column_title        ;
Linear.prototype.line_title          = linear_line_title          ;
Linear.prototype.display             = linear_display             ;
Linear.prototype.edit                = linear_edit                ;
Linear.prototype.stop_edit           = linear_stop_edit           ;
Linear.prototype.onkeypress          = linear_onkeypress          ;
Linear.prototype.go_right            = linear_go_right            ;
Linear.prototype.go_left             = linear_go_left             ;
Linear.prototype.go_down             = linear_go_down             ;
Linear.prototype.go_up               = linear_go_up               ;
Linear.prototype.help                = linear_help                ;
Linear.prototype.w                   = linear_w                   ;
Linear.prototype.change_show         = linear_change_show         ;
Linear.prototype.set_show            = linear_set_show            ;
Linear.prototype.tip                 = linear_tip                 ;
Linear.prototype.sort                = linear_sort                ;
Linear.prototype.freeze              = linear_freeze              ;
Linear.prototype.hide                = linear_hide                ;
Linear.prototype.print               = linear_print               ;
Linear.prototype.suivi               = linear_suivi               ;

function Information(L, help, value_info, get_value, change_value, changeable,
		     content)
{
  this.L            = L            ;
  this.help         = help         ;
  this.value_info   = value_info   ;
  this.get_value    = get_value    ;
  this.change_value = change_value ;
  this.changeable   = changeable   ;
  this.content      = content      ;
}

function information_value()
{
  var prepend ;

  if ( this.L.hide_what || this.value_info === '' )
    prepend = '&nbsp;' ;
  else
    prepend = '<u>' + this.value_info + '</u> ' ;

  if ( this.L.informations != this.L.informations_cell )
    {
      this.L.hide_line_title = true ;
      if ( this.L.information == this.L.informations_column[0]
	   || this.L.informations == this.L.informations_table)
	this.L.hide_column_title = true ;      
    }

  var value = this.get_value() ;
  if ( value.substr !== undefined && value.substr(0,1) == '\001' )
    value = value.substr(1) ;
  else
    value = html(value) ;

  return this.L.line_title() + this.L.column_title() + prepend
    + '<b>' + value + '</b>.' ;
}

function information_change(value)
{
  this.change_value(value) ;
}

function information_is_changeable()
{
  if ( this.change_value === undefined )
      return _("MSG_tablelinear_unmodifiable") ;
  return this.changeable() ;
}

Information.prototype.value         = information_value      ;
Information.prototype.change        = information_change     ;
Information.prototype.is_changeable = information_is_changeable ;

var L ;
var key_history = '' ;

/* The problem is that the server must not answer because it is impossible */
function send_key_history()
{
  if ( key_history === '' )
    return ;

  L.w('<img src="' + url + "/=" + ticket + '/' + year + '/' + semester
      + '/' + ue + '/' + page_id + '/key_history/'
      + encode_uri(key_history) +
      '">') ;
  key_history = '' ; // Do not send history more than once
}

function dispatch(x)
{
  if ( x == 'init' )
    {
      L = new Linear() ;
      L.input = document.getElementsByTagName('INPUT')[0] ;
      L.input.style.width = '100%' ;
      L.input.style.display = 'none' ;
      L.display() ;
      return ;
    }
  if ( L.input_edit )
    {
      L.onkeypress(x) ;
      return ;
    }
  if ( x.keyCode == 13 && L.input_edit === false )
    {
      // Do not take into account the 'Return' just after a 'stop_edit'
      L.input_edit = 0 ;
      return ;
    }
  L.input_edit = 0 ;

  if ( x.altKey || x.ctrlKey )
    return ;

  var k = '' ;
  if ( x.which )
    k = String.fromCharCode(x.which) ;
  else
    k = String.fromCharCode(x.keyCode) ;
  if ( k == null )
    k = '' ;
  k = k.toLowerCase() ;



  switch( x.keyCode )
    {
    case 39: k = 'R' ; break ; 
    case 37: k = 'L' ; break ; 
    case 40: k = 'D' ; break ; 
    case 38: k = 'U' ; break ; 
    case 13: k = 'C' ; break ; 
    }

  r =  k == '?'  && L.help()
    || k == 'R'  && L.go_right(x.shiftKey)
    || k == 'r'  && L.go_right(x.shiftKey)
    || k == 'L'  && L.go_left(x.shiftKey)
    || k == 'l'  && L.go_left(x.shiftKey)
    || k == 'D'  && L.go_down(x.shiftKey)
    || k == 'd'  && L.go_down(x.shiftKey)
    || k == 'U'  && L.go_up(x.shiftKey)
    || k == 'u'  && L.go_up(x.shiftKey)
    || k == 'C'  && L.edit(x.shiftKey)
    || k == 'i'  && L.change_show(x.shiftKey)
    || k == 'h'  && L.tip()
    || k == 'a'  && L.tip()
    || k == '1'  && L.set_show(false, L.informations_cell)
    || k == '2'  && L.set_show(false, L.informations_column)
    || k == '3'  && L.set_show(false, L.informations_table)
    || k == '>'  && L.sort(1)
    || k == '<'  && L.sort(-1)
    || k == '.'  && L.freeze()
    || k == 'f'  && L.set_show(x.shiftKey, L.informations_column, 8)
    || k == 'n'  && L.set_show(x.shiftKey, L.informations_column, 8, 'Nom')
    || k == 'p'  && L.set_show(x.shiftKey, L.informations_column, 8, 'Prénom')
    || k == 'x'  && L.hide()
    || k == 't'  && L.print()
    || k == 's'  && L.suivi()
    ;

  if ( x.shiftKey )
    key_history += '_' ;
  key_history += k ;

  if ( r && x.keyCode !== undefined )
    {
      stop_event(x) ;
    }
  else
    {
      L.input.value = '' ;
      if ( my_identity == 'thierry.excoffier' )
	L.w('<small><small>' + k + ':' + x.keyCode + '</small></small>') ;
    }
}

function dispatch2(x)
{
  if ( navigator.appName == 'Microsoft Internet Explorer'
       || navigator.appVersion.toString().indexOf('Chrome') != -1)
    if ( x.keyCode == 39 || x.keyCode == 37 ||
	 x.keyCode == 40 || x.keyCode == 38 )
      {
	dispatch(x) ;
      }
}
