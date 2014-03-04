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

// goto_resume()

function compute_abj_per_day(t)
{
  var tag = document.getElementById('div_abjs') ;
  var s, abjs, end ;
  var ttam = [], ttpm = []  ;
  var d = new Date() ;
  d.setTime(t) ;
  var t12 = t + 16*3600*1000 ;
  
  for(var login in the_abjs)
    {
      abjs = the_abjs[login] ;
      for(i in abjs)
	{
	  begin = parse_date(abjs[i][0]) ;
	  end = parse_date(abjs[i][1]) ;
	  if ( end < t )
	    continue ; // Before the day
	  if ( begin > t12 )
	    continue ; // After the day
	  s = '<!-- ' +  names[login]
	    + ' --><tr><td>' + login + '<th align="left">'
	    + names[login] +
	    '<td>' + abjs[i][0] + '<td>' + abjs[i][1] +
	    '<td>' + html(abjs[i][2]) + '</tr>' ;
	  if ( begin <= t )
	    ttam.push(s) ;
	  if ( end > t )
	    ttpm.push(s) ;
	}
    }
  ttam.sort() ;
  ttpm.sort() ;
  s = '<h3>' + _("MSG_abjtt_from_before") + ' ' +
      d.formate('%A %d %B %Y') + _("MSG_abjtt_from_after") + '</h3>' ;
  s += _("MSG_abjtt_begin_end") ;
  s += '<p>' + _("MSG_abjtt_morning") + '<table class="colored">' ;
  for(var i=0; i<ttam.length; i++)
    s += ttam[i] ;
  s += '</table>' ;
  s += '<p>' + _("MSG_abjtt_afternoon") + '<table class="colored">' ;
  for(var i=0; i<ttpm.length; i++)
    s += ttpm[i] ;
  s += '</table>' ;
  tag.innerHTML = s ;
}

function abj_per_day()
{
  var w = window_open() ;
  w.document.open('text/html') ;

  var p = html_begin_head(true) ;


  var title = _("TITLE_abjtt") + ' ' + ue + ' ' + semester + ' ' + year ;

  p +='<script src="_FILES_/abj.js" onload="this.onloadDone=true;"></script>'+
    '<title>' + title + '</title>' +
    '<body>' +
    '<h1>' + title + '</h1>' +
    '<script>var the_abjs = {};\n' +
    'function virtual_init() {\n' +
    'if ( ! wait_scripts("virtual_init()") ) return ;\n' +
    'lib_init() ; }\n' +
    'virtual_init() ;\n' ;

  var s = '', t, end, names='' ;
  var days = [] ;
  var bug = '' ;
  for(var i in the_student_abjs)
    {
      s += "the_abjs[" + js(i) + "] = [" ;
      if ( lines[login_to_line_id(i)] === undefined )
	  {
	      bug += 'BUG : ' + login_to_line_id(i) + ' unfound\n' ;
	      continue ;
	  }
      names += ',' + js(i) + ':'
	+ js(lines[login_to_line_id(i)][2].value
	     + ' ' + lines[login_to_line_id(i)][1].value) ;
      i = the_student_abjs[i] ;
      var t = '' ;
      for(var j in i[0])
	{
	  j = i[0][j] ;
	  t += ',[' + js(j[0]) + ',' + js(j[1]) + ',' + js(j[2]) + ']' ;
	  end = parse_date(j[1].replace(ampms[0],ampms[1])).getTime() ;
	  for(var d=parse_date(j[0].replace(ampms[1],ampms[0]));
	      d.getTime() < end;
	      d.setTime(d.getTime() + 86400*1000)
	      )
	    {
	      if ( d.getHours() == 23 )
		d.setHours(24) ;
	      else if ( d.getHours() == 1 )
		d.setHours(0) ;
	      days[d.getFullYear()+'/'+d.getMonth()+'/'+d.getDate()] = d.getTime() ;
	    }
	      
	}
      s += (t+' ').substr(1) + '] ;\n' ;
    }
  if ( bug )
      alert(bug) ;
  p += s + '\n' +
    'var names = {' + (names+' ').substr(1) + '};</script>' ;
  
  var mm, first, start, stop, yy, nr, table_abjs = '' ;

  var i = myindex(semesters, semester) ;
  yy = year ;
  if ( i != -1 )
    { start = semesters_months[i][0] ; stop = semesters_months[i][1] ; }
  else
    { start = 1 ; stop = 12 ; }

  nr = 0 ;
  start-- ;
  stop-- ;
  for(var m=start; m<=stop; m++)
    {
      first = true ;
      mm = m % 12 ;
      if ( mm == 0 )
	  yy++ ;
      for(var d=1; d<32; d++)
	{
	  if ( first )
	    {
	      first = false ;
	      table_abjs  += '<tr><th>' + months[mm] ;
	      for(var i=1;i<d;i++)
		table_abjs  += '<td>&nbsp;' ;
	    }
	  if ( days[yy + '/' + mm + '/' + d] )
	    {
	      table_abjs  += '<td><a onclick="javascript:compute_abj_per_day('
		+ days[yy + '/' + mm + '/' + d] + ');">' + d + '</a>' ;
	      nr++ ;
	    }
	  else
	    {
	      table_abjs  += '<td><span style="color:#DDD">' + d ;
	    }
	}
	
      if ( ! first )
	{
	  table_abjs  += '</tr>\n' ;
	}
    }

  if ( nr )
      p += '<h2>' + _("TITLE_abjtt_abj") + '</h2>\n'
	  + '<p>' + _("MSG_abjtt_choose_day")
	  + '<table class="colored abj_table">' + table_abjs + '</table>'
	  + _("MSG_abjtt_explanation_before") + ' <b>'
	  + nr + "</b> " + _("MSG_abjtt_explanation_after") + "<br>"
	  + _("MSG_abjtt_more_before") + ' '
	  + '<a href="' + url + '/=' + ticket + '/' + year + '/' + semester
	  + '/' + ue + '/resume">' + _("MSG_abjtt_more_link") + '</a> '
	  + _("MSG_abjtt_more_after") + '<br>' ;
  else
      p += "<h2>" + _("TITLE_abjtt_no_abj") + "</h2>" ;


  var tt = [], tt2 = [], data, line, student, da ;
  for(var login in the_student_abjs)
    {
      data = the_student_abjs[login] ;
      if ( data[1].length == 0 && data[2] == '' )
	continue ;
	
      line = lines[login_to_line_id(login)] ;
      student = login ;
      if ( line )
	student = html(line[2].value) + ' ' + html(line[1].value)
	  + '<br>' + login ;
      
      if ( data[2] ) // Tiers-temps
	tt.push('<tr><td>' + student
		+ '<td>' + html(data[2]).replace(/\n/g,'<br>') + '</tr>') ;

      for(da in data[1])
	if ( data[1][da][0].substr(0,ue.length) == ue )
	  tt2.push('<tr><td>' + student + '<td>À partir du '
		   + data[1][da][1] + '<br>'
		 + data[1][da][2] + '</tr>') ;

    }
  tt.sort() ;
  tt2.sort() ;

  if ( tt.length == 0 )
      tt = '<h2>' + _("TITLE_abjtt_no_tt") + '</h2>' ;
  else
      tt = '<h2>' + _("TITLE_abjtt_tt") + '</h2>'
	  + '<table class="colored abj_table_tt">' + tt.join('\n') +'</table>';

  if ( tt2.length == 0 )
      tt2 = '<h2>' + _("TITLE_abjtt_no_da") + '</h2>' ;
  else
      tt2 = '<h2>' + _("TITLE_abjtt_da") + '</h2>'
	  + '<table class="colored abj_table_da">'+tt2.join('\n') + '</table>';


  p += '<div id="div_abjs"></div>' + tt + tt2 + '</html></body>' ;
  w.document.write(p) ;
  w.document.close() ;
}
