var preferences = {"language":"fr"} ;
var my_identity = "" ;
var upload_max = 100000;
display_data["Preferences"] = {} ;
display_data["Grades"] = [[]] ;
var the_body ;

function init_data()
{
  lib_init() ;
  the_body = document.getElementsByTagName("BODY")[0] ;
  the_body.className = "themeG" ;
  for(var i in columns)
  {
    columns[i].columns = '' ;
    columns[i] = Col(columns[i]) ;
    columns[i].dir = 1 ;
  }
  var tmp_lines = [] ;
  for(var i in lines)
  {
    for(var j in lines[i] )
    {
      var cell = lines[i][j] ;
      lines[i][j] = C(cell[0], cell[1], cell[2], cell[3]) ;
      lines[i][j].key(columns[j].empty_is) ;
    }
    lines[i].line_id = i ;
    tmp_lines.push(lines[i]) ;
  }
  lines = tmp_lines ;
  for(var data_col in columns)
  {
    init_column(columns[data_col]) ;
    columns[data_col].data_col = data_col ;
  }
  var h = (window.location.hash + "sort=").split("sort=")[1] + ",,,," ;
  h = h.split(',') ;
  for(var i = 0 ; i < 3 && i < columns.length ; i++)
  {
    var dir = h[i] ;
    var c = columns[dir.substr(1)] ;
    if ( c === undefined )
      c = columns[i] ;
    if ( dir.substr(0, 1) == '-' )
      c.dir = -1 ;
    else
      c.dir = 1 ;
    sort_columns[i] = c ;
  }
}

function sort_this_column(i)
{
  if ( sort_columns[0].data_col == i )
    sort_columns[0].dir *= -1 ;
  else
  {
    sort_columns.splice(0, 0, columns[i]) ;
    sort_columns.splice(sort_columns.length-1, 1) ;
  }
  fill_data() ;
  var s = [] ;
  for(var i in sort_columns)
    s.push((sort_columns[i].dir > 0 ? '+' : '-') + sort_columns[i].data_col) ;
  window.location.hash = "sort=" + s.join(",") ;
}

function fill_data()
{
  lines.sort(sort_lines23) ;
  var s = [] ;
  s.push('<table class="colored">') ;
  s.push("<tr>") ;
  var cols = column_list_all() ;
  for(var c in cols)
  {
    c = cols[c] ;
    var title = html(columns[c].title) ;
    if ( columns[c].comment )
      title = hidden_txt(title, html(columns[c].comment)) ;
    if ( columns[c] === sort_columns[0] )
      if ( columns[c].dir == 1 )
        title = "▲ " + title ;
    else
      title = "▼ " + title ;
    if ( columns[c] === sort_columns[1] )
      if ( columns[c].dir == 1 )
        title = "△ " + title ;
    else
      title = "▽ " + title ;
    s.push('<th onclick="sort_this_column(' + c + ')">'
           + title + '</th>'
          ) ;
  }
  s.push('</tr>') ;
  DisplayGrades.ue = table_attr ;
  DisplayGrades.table_attr = DisplayGrades.ue ;
  for(var i in lines)
  {
    if ( line_empty(lines[i]) )
      continue ;
    s.push("<tr>") ;
    DisplayGrades.ue.line_real = lines[i] ;
    DisplayGrades.ue.line_id = lines[i].line_id ;
    for(var c in cols)
    {
      c = cols[c] ;
      DisplayGrades.column = columns[c] ;
      DisplayGrades.cell = lines[i][c] ;
      DisplayGrades.value = lines[i][c].value ;
      // DisplayGrades.cellstats = table_attr.stats[columns[c].the_id] || {} ;
      DisplayGrades.cellstats = {} ;
      cs = get_cell_class_and_style() ;
      var text = DisplayGrades.column.real_type.formatte_suivi() ;
      if ( DisplayGrades.cell.comment !== "")
	text = hidden_txt(text, html(DisplayGrades.cell.comment)) ;
      s.push('<td class="' + cs[0] + '" style="' + cs[1] + '">'
             + text + '</td>') ;
    }
    s.push('</tr>') ;
  }
  s.push("<table>") ;
  document.getElementById("content").innerHTML = s.join('') ;
}
init_data() ;
fill_data() ;
