/*REDEFINE
Display the UE name in the timeline
*/
function timeline_display_external_info(year, semester, code, bilan)
{
  return code ;
}

function get_day_html(y, m, d, style, content)
{
  var t = new Date(y, m-1, d),
      x = t.getDay(),
      first_weekday = (8 + x - d % 7) % 7,
      y = Math.floor((d - 1) / 7) + (x < first_weekday ? 1 : 0) ;
  if ( t.getMonth() != m - 1 )
    return ;
  return '<span class="x' + x + ' y' + y + '" style="' + style + '">'
          + content  + '</span>' ;
}

function end_year(year, month, semester, bilan, resume)
{
  var s = [] ;
  var n = 0 ;
  for(var i in resume)
    for(var j in resume[i])
    {
      var r = resume[i][j] ;
      if ( r[0] == year && r[1] == semester )
      {
        if ( n++ % 6 == 0 )
          s.push('<td><div class="calendar tables">') ;
        s.push('<div style="color:#' + value_to_color(r[5], 2) + '">') ;
        s.push(timeline_display_external_info(year, semester, i, bilan,
                                              j == resume[i].length - 1));
        s.push('<span class="stats" style="background:#'
                + value_to_color(r[5], 1.1) + '">') ;
        if ( r[2] )
          s.push(r[2] + pre.toLowerCase() + ' ') ;
        if ( r[3] )
          s.push(r[3] + abi.toLowerCase() + ' ') ;
        if ( r[4] )
          s.push(r[4] + abj.toLowerCase() + ' ') ;
        s.push('<br>') ;
        if ( r[6] )
        {
          s.push(Math.floor(r[5]*20)) ;
          s.push('/20 ') ;
          s.push(r[6] + _("MSG_columnstats_grade").toLowerCase()) ;
          s.push('</span>') ;
        }
        else
          s.push(' ') ;
        s.push('</div>') ;
      }
    }
  s.push('</tr>') ;
  return s.join('') ;
}

function init_month(year, month, grades)
{
  if ( month > 12 )
    month -= 12 ;
  var s = ['<div class="month">', year, '<br>', months_full[month-1], '</div>'] ;
  var key = year + two_digits(month) ;
  for(var day=1;  day < 99 ; day++)
  {
    if ( grades[key + two_digits(day)] )
      continue ;
    var t = get_day_html(year, month, day, '', '') ;
    if ( t === undefined )
      break ;
    s.push(t) ;
  }
  return s.join('') ;
}

var hex_letters = "0123456789ABCDEFF" ;

function value_to_color(v, darkness)
{
  var r, g, b ;
  if ( v < 0.5 )
     { r = 1 ; g = 0; b = 0 ; v = 2*v ; }
  else
     { r = 0 ; g = 1 ; b = 0 ; v = 2*(1 - v) ; }

  return  hex_letters.substr(Math.floor((v/darkness + (1-v)*r)*16), 1)
        + hex_letters.substr(Math.floor((v/darkness + (1-v)*g)*16), 1)
        + hex_letters.substr(Math.floor((v/darkness + (1-v)*b)*16), 1) ;
}

function timeline(txt, bilan, resume, student_id, fn_sn_mail)
{
  lib_init() ;
  var date_y_s_grade, year, month, day, y, m, d, v, t, g, s = [
  '<body class="themeG">',
  '<style>',
  'TD { vertical-align: top }',
  'TABLE.colored { background: #F8F8F8; border: 0px }',
  'TABLE.colored TD { border: 0px }',
  'TABLE.colored TH, DIV.calendar { border: 1px solid #888 }',
  'TH DIV { overflow: hidden ; }',
  'DIV.calendar, TH DIV { width: ' + (7*timeline.size) + 'px ;',
  '                 position: relative; overflow: hidden }',
  'DIV.calendar:hover, TH DIV:hover { overflow: visible ; }',
  'SPAN { width:  ' + (timeline.size - 2*timeline.border) + 'px ;',
  '       height: ' + (timeline.size - 2*timeline.border) + 'px ;',
  '       position: absolute; font-size: 20% ;',
  '       background: #FFF ;',
  '       line-height: 0.85em ;',
  '       border: ' + timeline.border + 'px solid #EEE }',
  'DIV.calendar.tables { width: auto }',
  '.tables { font-size: 66% ; ',
  '          white-space: nowrap;',
  '          }',
  '.tables DIV { height: 1em ; }',
  '.tables SPAN { width:  ' + timeline.size*1.5 + 'px ;',
  '       height: auto ; text-align: center; vertical-align: top ; color: #000;',
  '       display: inline-block; position: relative; margin-top: 0.3em;',
  '       border: 0px; font-size: 3px; line-height: 1.25em; }',
  '.tables SPAN.stats { text-align: left ; width: auto; }',
  'DIV.calendar { height: ' + 6*timeline.size + 'px; background: #FFF ; ',
  '         transition: transform 0.2s; }',
  'TD { overflow: visible }',
  'TD:hover DIV.calendar { transform: scale(3,3) ; z-index: 1;',
  '               transition: transform 3s }',
  'SPAN:hover { transform:scale(2.5,2.5); z-index:2; transition:transform 3s }',
  '.x0 { left: 0px ; border: ' + timeline.border + 'px solid #CCC }',
  '.x1 { left: ' + 1*timeline.size + 'px }',
  '.x2 { left: ' + 2*timeline.size + 'px }',
  '.x3 { left: ' + 3*timeline.size + 'px }',
  '.x4 { left: ' + 4*timeline.size + 'px }',
  '.x5 { left: ' + 5*timeline.size + 'px }',
  '.x6 { left: ' + 6*timeline.size
                 + 'px ; border:' + timeline.border + 'px solid #CCC }',
  '.month { left: ' + 7*timeline.size
         + 'px; position: absolute; pointer-events: none; font-size: 60% }',
  '.y0 { top: 0px }',
  '.y1 { top: ' + 1*timeline.size + 'px }',
  '.y2 { top: ' + 2*timeline.size + 'px }',
  '.y3 { top: ' + 3*timeline.size + 'px }',
  '.y4 { top: ' + 4*timeline.size + 'px }',
  '.y5 { top: ' + 5*timeline.size + 'px }',
  '</style>',
  '<h1>', student_id, ' ', title_case(fn_sn_mail[0]), ' ', fn_sn_mail[1],
  ' <small>', fn_sn_mail[2], '</small></h1>',
  _("MSG_timeline"),
  '<p><br><table class="colored">',
  ] ;
  txt = txt.split(/\n/) ;
  var grades = {}, ordered = [] ;
  for(var i in txt)
  {
    date_y_s_grade = txt[i].split(' ') ;
    t = date_y_s_grade[0] ;
    if ( grades[t] === undefined )
    {
      grades[t] = [[], []] ;
      ordered.push(t) ;
    }
    v = date_y_s_grade[3] ;
    if ( isNaN(v) )
      grades[t][0].push(v) ;
    else
      grades[t][1].push(v) ;
  }
  var semester_start, semester_stop, semester, univ_year ;
  function is_in_semester(month)
  {
    return month >= semester_start && month <= semester_stop
           || semester_stop > 12 && month <= semester_stop - 12 ;
  }
  function update_semester_span(year, m)
  {
    for(var i in semesters_months)
    {
      semester_start = semesters_months[i][0] ;
      semester_stop = semesters_months[i][1] ;
      semester = semesters[i] ;
      univ_year = Number(year) + semesters_year[i] ;
      if ( is_in_semester(m) )
          return ;
    }
    alert("bug update_semester_span " + m) ;
  }
  function add_months()
  {
    while( month < m || month > m && month - 12 <  m )
    {
      s.push('<td><div class="calendar">') ;
      month++ ;
      s.push(init_month(y, month, grades)) ;
    }
  }

  for(var i in ordered)
  {
    i = ordered[i] ;
    y = i.substr(0, 4) ;
    m = i.substr(4, 2) ;
    d = i.substr(6, 2) ;
    v = grades[i] ;
    if ( ! is_in_semester(m) )
    {
      if ( univ_year !== undefined )
      {
        // Terminate the previous line
        while( month < semester_stop )
        {
          s.push('<td><div class="calendar">') ;
          month++ ;
          s.push(init_month(year, month, grades)) ;
        }
        s.push(end_year(year, month, semester, bilan, resume)) ;
      }
      update_semester_span(y, m) ;

      s.push('<tr><th><div>' + univ_year + '<br>' + semester + '</div>') ;
      month = semester_start-1 ;
      year = Number(y) ; // The real year
    }
    add_months() ;
    t = '' ;
    if ( v[1].length != 0 )
    {
       g = 0 ;
       for(var j in v[1])
       {
           g += Number(v[1][j]) ;
           t += Math.floor(v[1][j]*20) + '<br>' ;
       }
       g = 'background:#' + value_to_color(g / v[1].length, 1.2) + ';' ;
    }
    else
        g = '' ;
    if ( v[0].length != 0 )
    {
      g += 'border:' + timeline.border + 'px solid #'
           + ( v[0].indexOf(abi) != -1 ? "F" : "0")
           + ( v[0].indexOf(pre) != -1 ? "F" : "0")
           + ( v[0].indexOf(abj) != -1 ? "F" : "0") ;
    }
    s.push(get_day_html(y, m, d, g, t)) ;
  }
  if ( univ_year !== undefined )
  {
    m = semester_stop ;
    add_months() ;
    s.push(end_year(year, month, semester, bilan, resume)) ;
  }
  s.push('</table>') ;
  document.write(s.join('\n')) ;
}

timeline.border = 1 ;
timeline.size = 8 ;

