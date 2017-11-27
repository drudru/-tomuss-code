requests = "" ;
alerts = "" ;

function restore_unsaved() {}
function head_html() {}
function insert_middle() {}
function wait_scripts() {  return true ; }
function table_init() {}
function update_line_menu() {}
function update_column_menu() {}
function update_popup_on_red_line() {}
function update_vertical_scrollbar_real() {}
function update_horizontal_scrollbar() {}
function change_option() {}
function line_fill() {}
function column_update_option() {}
function append_image(td, text, force) { requests += text + "\n" ; }
function alert(x) { alerts += x + "\n" ; }

Current.prototype.jump = function() { } ;
Current.prototype.update_table_headers = function() { } ;

tests_are_fine = true ;

function check_requests(t)
{
  if ( t != requests.trim() )
  {
    console.log("ERROR requests") ;
    console.log("Expected: " + t) ;
    console.log("Computed: " + requests) ;
    tests_are_fine = false ;
  }
  requests = "" ;
}

function check_alerts(t)
{
  if ( t != alerts.trim() )
  {
    console.log("ERROR alerts") ;
    console.log("Expected: " + t) ;
    console.log("Computed: " + alerts) ;
    tests_are_fine = false ;
  }
  alerts = "" ;
}

function hide_dates(t)
{
  return t.replace(/"20[0-9]{12}"/g, '"DATE"').replace(/\n/g, "") ;
}

function check_lines(t)
{
  if ( hide_dates(lines_in_javascript()) != t )
    {
      console.log("ERROR") ;
      console.log("Expected:") ;
      console.log(t) ;
      console.log("Computed:") ;
      console.log(hide_dates(lines_in_javascript())) ;
      tests_are_fine = false ;
    }
}

function change_identity(login)
{
  my_identity = login ;
  initialise_columns() ; // To recompile filters
}

function error(v)
{
  var err = new Error();
  console.log("ERROR: " + v + '\n' + err.stack) ;
  tests_are_fine = false ;
}

initialize() ;
add_empty_column() ;

if ( i_am_the_teacher )
    error(i_am_the_teacher) ;

// Create first line and cell

add_a_new_line("lin_0") ;
cell_set_value_real("lin_0", 0, "k01") ;
check_requests('cell_change/0_0/lin_0/k01') ;
check_lines('[[C("k01","tt.master","DATE",""),C("","","",""),C("","","",""),C("","","",""),C("","","",""),C("","","","")]]')
if ( columns[0].type != 'Text' )
  error(columns[0].type) ;

// Change value

cell_set_value_real("lin_0", 0, "k02") ;
check_requests('cell_change/0_0/lin_0/k02') ;
check_lines('[[C("k02","tt.master","DATE",""),C("","","",""),C("","","",""),C("","","",""),C("","","",""),C("","","","")]]')

// Failing to change a value

change_identity("test") ;
line = lines['lin_0'] ;
cell = line[0] ;
column = columns[0] ;

if ( cell.is_mine() )
  error() ;
if ( column.cell_writable_filter(line, cell) )
  error() ;
if ( cell.changeable(line, columns[0]) === true )
  error() ;

cell_set_value_real("lin_0", 0, "k03") ;
check_lines('[[C("k02","tt.master","DATE",""),C("","","",""),C("","","",""),C("","","",""),C("","","",""),C("","","","")]]')
check_requests('') ;


// Try to change column ID

change_identity("tt.master") ;
column_attr_set(column, "title", "A") ;
check_requests('') ;
check_alerts(_("ERROR_value_not_modifiable") + '\n'
	     + _("ERROR_value_system_defined")) ;


// Create a new column

column = columns[6] ;
column_attr_set(column, "title", "A") ;
check_requests('column_attr_title/1_0/A') ;
column_attr_set(column, "cell_writable", "[A]= | @[]=test") ;
check_requests('column_attr_cell_writable/1_0/%5BA%5D=%20%7C%20@%5B%5D=test') ;
if ( column.type != 'Note' )
  error(column.type) ;

// Is the cell content writable

c = lines['lin_0'][6].changeable(lines['lin_0'], column)
if ( c !== true )
  error("Cell not changeable: " + c) ;

// Set bad value in the new column

cell_set_value_real("lin_0", 6, "x") ;

if ( lines['lin_0'][6].value !== '' )
  error("Cell changed!") ;

check_requests('') ;
check_alerts('x' + _("ALERT_bad_grade") + "[0;20]\n"
	     + "I(INJLEAVE), J(JUSLEAVE), C(CANTGRADE), W(WNGIVEN)") ;

// Set comment on the value

comment_change('lin_0', 6, "comment") ;
check_requests('comment_change/1_0/lin_0/comment') ;

// Set value in the new column

cell_set_value_real("lin_0", 6, "12.34") ;
check_requests('cell_change/1_0/lin_0/12$2E34') ;
cell_set_value_real("lin_0", 6, "13") ;
check_requests('') ; // Impossible to change

// But 'test' user can

change_identity("test") ;
cell_set_value_real("lin_0", 6, "13") ;
check_requests('cell_change/1_0/lin_0/13') ;

// Filtering columns

set_columns_filter('A') ;
if ( column_list_all() != "0,2,1,6" )
  error(column_list_all()) ;

set_columns_filter('@=*') ;
if ( column_list_all() != "0,2,1,3,4" )
  error(column_list_all()) ;

set_columns_filter('@=@[]') ;
if ( column_list_all() != "0,2,1" )
  error(column_list_all()) ;

set_columns_filter('') ;
if ( column_list_all() != "0,2,1,3,4,6" )
  error(column_list_all()) ;

// Full filter

full_filter_change({value:"@"}) ;
if ( column_list_all() != "0,2,1,6" )
  error(column_list_all()) ;
update_filtered_lines() ;
if ( filtered_lines.length != 1 )
  error(filtered_lines.length) ;

full_filter_change({value:"not"}) ;
if ( column_list_all() != "0,2,1" )
  error(column_list_all()) ;
update_filtered_lines() ;
if ( filtered_lines.length != 0 )
  error(column_list_all()) ;

full_filter_change({value:""}) ;
if ( column_list_all() != "0,2,1,3,4,6" )
  error(column_list_all()) ;
update_filtered_lines() ;
if ( filtered_lines.length != 1 )
  error(filtered_lines.length) ;

// line filter

line_filter_change_value = {value: "no"} ;
line_filter_change_real() ;
update_filtered_lines() ;
if ( filtered_lines.length != 0 )
  error(filtered_lines.length) ;

line_filter_change_value = {value: "no | k"} ;
line_filter_change_real() ;
update_filtered_lines() ;
if ( filtered_lines.length != 1 )
  error(filtered_lines.length) ;

line_filter_change_value = {value: "k @=tt.master ?<0.001j"} ;
line_filter_change_real() ;
update_filtered_lines() ;
if ( filtered_lines.length != 1 )
  error(filtered_lines.length) ;

line_filter_change_value = {
  value: "=13 >=13 >12 <=13 <14 @=test @[ID]=tt.master @[A]=test !@[ID]=@[A] ?<0.001j :~12.34 :[A]~12.34 :[A]12.3 #=comment #~com #[A]=comment #[A]~com"} ;
line_filter_change_real() ;
update_filtered_lines() ;
if ( filtered_lines.length != 1 )
  error(filtered_lines.length) ;

// Create an average

add_empty_column() ;
column = columns[7] ;
column_attr_set(column, "title", "Average") ;
column_attr_set(column, "type", "Moy") ;
column_attr_set(column, "columns", "A") ;
column_attr_set(column, "minmax", "[0;40]") ;
if ( column.type != 'Moy' )
  error(column.type) ;
if ( column_list_all() != "0,2,1,3,4,6,7" )
  error(column_list_all()) ;
update_line("lin_0", 7) ;

if ( 26 - lines["lin_0"][7].value > 1e-9 )
  error(lines["lin_0"][7].value) ;
if ( lines["lin_0"][7].author != "*" )
  error(lines["lin_0"][7].author) ;

check_requests('column_attr_title/1_1/Average\n'
	       + 'column_attr_columns/1_1/A\n'
	       + 'column_attr_minmax/1_1/%5B0;40%5D') ;

// Modify an average

cell_set_value_real("lin_0", 7, "12") ;

check_alerts("") ; // No alert because it is impossible
if ( 26 - lines["lin_0"][7].value > 1e-9 )
  error(lines["lin_0"][7].value) ;

check_requests('') ;

// Create a COW

add_empty_column() ;
column = columns[8] ;
column_attr_set(column, "title", "Cow") ;
column_attr_set(column, "type", "COW") ;
column_attr_set(column, "columns", "Average") ;
if ( column.type != 'COW' )
  error(column.type) ;
if ( column_list_all() != "0,2,1,3,4,6,7,8" )
  error(column_list_all()) ;
update_line("lin_0", 8) ;

if ( 26 - lines["lin_0"][8].value > 1e-9 )
  error(lines["lin_0"][8].value) ;
if ( lines["lin_0"][8].author != "?" )
  error(lines["lin_0"][8].author) ;

check_requests('column_attr_title/1_2/Cow\n'
	       + 'column_attr_columns/1_2/Average') ;

// Change value

cell_set_value_real("lin_0", 6, "3") ;
update_line("lin_0", 6) ;

if ( 6 - lines["lin_0"][8].value > 1e-9 )
  error(lines["lin_0"][8].value) ;

check_requests('cell_change/1_0/lin_0/3') ;

// I set myself as table master

table_attr_set("masters", "test") ;
check_requests('table_attr_masters/test') ;

// Change COW

cell_set_value_real("lin_0", 8, "5") ;
if ( lines["lin_0"][8].value != "5" )
  error(lines["lin_0"][8].value) ;
if ( lines["lin_0"][8].author != "test" )
  error(lines["lin_0"][8].author) ;

check_requests('cell_change/1_2/lin_0/5') ;
check_alerts("") ;


// Create a Nmbr without columns.
// Do it like it was a page loading and not user creation

columns.push(Col({"the_id": "Nmbr", "title": "Nmbr", "type": "Nmbr"})) ;
column = columns[9] ;
init_column(column) ;
column_attr_set(column, "title", "Nmbr") ;
column_attr_set(column, "type", "Nmbr") ;
column_attr_set(column, "columns", "") ;
check_requests('') ;
check_alerts("") ;

if ( column.max != 1 || column.minmax != "[0;1]" )
  error(column.minmax) ;

column_attr_set(column, "columns", "Average Cow", "interactif") ;
if ( column.max != 2 || column.minmax != "[0;2]" )
  error(column.minmax) ;



// All is done

if ( tests_are_fine )
  console.log("tests are fine") ;
