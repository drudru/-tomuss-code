/******************************************************************************
Check the 'filter' cell in the header
******************************************************************************/

/******************************************************************************   Beware : the value is [value, author, date, comment]
   The test update the information in the column object.
   It returns the new value.
******************************************************************************/

/**************** Generic filter **********************/

function compile_filter_generic_(value)
{
  var negate, val, oper, data ;
  var test, end, v, number ;

  /*
   * Negate part
   */
  value = value.replace(/ */, '') ; // Remove Spaces at the left
  if ( value.substr(0,1) == '!' )
    {
      negate = true ;
      value = value.substr(1) ;
    }
  else
    negate = false ;

  /*
   * Value part (allow white space here)
   */
  value = value.replace(/ */, '') ;
  if ( value.substr(0,1) == '#' )
    {
      val = 'value_.comment' ;
      value = value.substr(1) ;
    }
  else if ( value.substr(0,1) == '@' )
    {
      val = 'value_.author' ;
      value = value.substr(1) ;
    }
  else if ( value.substr(0,1) == ':' )
    {
      val = 'value_.history' ;
      value = value.substr(1) ;
    }
  else if ( value.substr(0,1) == '?' )
    {
      val = '(value_.date.substr(6,2)+"/"+value_.date.substr(4,2)+"/"+value_.date.substr(0,4)+"/"+value_.date.substr(8,2))' ; /* The date and hour */
      value = value.substr(1) ;
    }
  else
    val = 'value_.value' ; /* The value */

  /*
   * Operator part (do not allow white space because : '@ a' for example)
   */
  // value = value.replace(/ */, '') ;
  if ( value.substr(0,1) == '=' )
    { oper = '==' ; value = ' ' + value ; }
  else if ( value.substr(0,2) == '<=' )
    oper = '<=' ;
  else if ( value.substr(0,2) == '>=' )
    oper = '>=' ;
  else if ( value.substr(0,1) == '<' )
    oper = '<' ;
  else if ( value.substr(0,1) == '>' )
    oper = '>' ;
  else if ( value.substr(0,1) == '~' )
    oper = "~" ;
  else
    oper = "" ;
  value = value.substr(oper.length) ;

  /*
   * Constant part
   */
  // value = value.replace(/ */, '') ;
  if ( val === 'value_.value' && oper === '' )
    end = value.search(/[<>&|=!]| [<>&|=!:#?@~]| ou/) ;
  else
    end = value.search(/[ <>&|=!]/) ;
  if ( end == -1 )
    {
      data = value ;
      value = '' ;
    }
  else
    {
      data = value.substr(0, end) ;
      value = value.substr(end) ;
      value = value.replace(/ */, '') ;
    }

  /*
   * Special constant cases
   */
  if ( val === 'value_.author' && data === '' && oper === '')
    {
      data = my_identity ;
      oper = '==' ;
    }
  else if ( val === 'value_.comment' && data === '' && oper === '')
    {
      oper = '!=' ;
    }
  else if ( val.length > 20 && data === '' && oper === '')
    {
      oper = '>=' ;
      data = today.substr(6,2) + '/' + today.substr(4,2) + '/' + today.substr(0,4) ;
    }
  else if ( val == 'value_.history' && data === '' && oper === '')
    {
      oper = '!=' ;
    }

  /*
   * code generation
   */
  if ( replaceDiacritics(data) === data )
    {
      // No diacritics in data, so don't test them
      if ( value.substr(0,1) != '(' ) // Not a Date
	val = 'replaceDiacritics(' + val + '.toString())' ;
    }


  /*
   * Constant type : true: number, false:string, other: date
   */
  if ( ! isNaN(data.replace(',', '.')) )
    data = data.replace(',', '.') ;

  if ( isNaN(data) )
    {
      number = get_date(data) ;
      if ( number.reverse )
	{
	  if ( oper === '>' || oper === '>=' )
	    oper = '<' ;
	  else if ( oper === '<' || oper === '<=' )
	    oper = '>' ;
	}
    }
  else
    number = data !== '' ;


  /*
   * Create formula, depends on constant type AND operator
   */
  if ( oper === '~' || oper === '' || number === false )
    {
      dataorig = data ;
      data =  "'" + data.replace(/\\/g,"\\\\").replace(/[\']/g,"\\'").toUpperCase() + "'" ;
      number = false ;
    }

  /* Use regex to speedup process with /i option if the searched
     text does not contains dangerous symbols */

  if ( oper === '' )
    {
      if ( dataorig === '' || dataorig.search(/[^a-zA-Z0-9_-]/) != -1 )
	test = val + '.toString().toUpperCase().indexOf(' + data + ') == 0' ;
      else
	test = val + '.toString().search(/^' + dataorig + '/i) != -1' ;
    }
  else if ( oper === '~' )
    {
      if (  dataorig === '' || dataorig.search(/[^a-zA-Z0-9_-]/) != -1 )
	test = val + '.toString().toUpperCase().indexOf(' + data + ') != -1' ;
      else
	test = val + '.toString().search(/' + dataorig + '/i) != -1' ;
    }
  else
    switch(number)
      {
      case true:
	switch(oper)
	  {
	  case '<':
	  case '>':
	  case '<=':
	  case '>=':
	    test = 'a_float(' + val + ')' + oper + data ;
	    break ;
	  default:
	    test = val + oper + data ;
	    break ;
	  }
	break ;
      case false:
	test = val + '.toString().toUpperCase()' + oper + data ;
	break ;
      default:

	switch(oper)
	  {
	  case '<':
	    test = 'get_date_sup(' + val + ') < ' + number.getTime() ;
	    break ;
	  case '<=':
	    test = 'get_date_sup('+ val+ ') <= ' + number.sup.getTime() ;
	    break ;
	  case '>':
	    test = 'get_date_inf(' + val + ') > ' + number.sup.getTime() ;
	    break ;
	  case '>=':
	    test = 'get_date_inf(' + val + ') >= ' + number.getTime() ;
	    break ;
	  default:
	    break ;
	  }
      }

  if ( negate )
    test = '!(' + test + ')' ;

  if ( value !== '' )
    {
      if ( value.substr(0,1) == '&' )
	test += ' && ('
	  + compile_filter_generic_(value.substr(1)) + ')' ;
      else if ( value.substr(0,1) == '|' )
	test = '(' + test + ') || ('
	  + compile_filter_generic_(value.substr(1)) + ')' ;
      else if ( value.substr(0,2) == 'ou' )
	test = '(' + test + ') || ('
	  + compile_filter_generic_(value.substr(2)) + ')' ;
      else
	test += ' && ('
	  + compile_filter_generic_(value) + ')' ;
    }

  _d('\n' + test + '\n') ;
  return test ;
}

var tmp_index_filter = 0 ;

function compile_filter_generic_old(value)
{
  if ( value === '' || value === '~' )
    return function() { return true ; } ;
  tmp_index_filter++ ;

  return eval('function f' + tmp_index_filter + '(value_){return '
	      + compile_filter_generic_(value
					.replace(/\\\\/g, '\001')
					.replace(/\\[ ]/g, '\002')
					.replace(/\\[!]/g, '\003')
					.replace(/\\[~]/g, '\004')
					.replace(/\\[|]/g, '\005')
					.replace(/\\[=]/g, '\006')
					.replace(/\\[<]/g, '\007')
					.replace(/\\[>]/g, '\010')
					.replace(/\\[@]/g, '\011')
					.replace(/\\[:]/g, '\013')
					.replace(/\\[#]/g, '\014')
					.replace(/\\[?]/g, '\016')
				       )
	      .replace(/\001/g, '\\\\')
	      .replace(/\002/g, ' ')
	      .replace(/\003/g, '!')
	      .replace(/\004/g, '~')
	      .replace(/\005/g, '|')
	      .replace(/\006/g, '=')
	      .replace(/\007/g, '<')
	      .replace(/\010/g, '>')
	      .replace(/\011/g, '@')
	      .replace(/\013/g, ':')
	      .replace(/\014/g, '#')
	      .replace(/\016/g, '?')
	      + ';} ; f' + tmp_index_filter) ;
}


function compute_average_old(data_col, line)
{
  var column = columns[data_col] ;

  if ( column.average_columns.length === 0 )
    {
      line[data_col].set_value('') ;
      return;
    }

  var nr_abj = 0 ;
  var nr_abi = 0 ;
  var nr_ppn = 0 ;
  var value ;
  var from ;
  var values = [] ;
  for(var c in column.average_columns)
    {
      c = column.average_columns[c] ;
      value = line[c].value ;
      from = columns[c] ;
      if ( from.real_weight === 0 )
	continue ;
      if ( value === '' ) 
	       value = from.empty_is ;
      switch(value)
	{
        case '':  line[data_col].set_value(NaN) ; return ;
	case abj_short:
	case abj: nr_abj++ ; continue ;
	case ppn_short:
	case ppn: nr_ppn++ ; continue ;
	case pre_short:
	case pre: values.push([1, from]) ; break ;
	case tnr_short:
	case tnr:
	case abi_short:
	case abi: values.push([0, from]) ; nr_abi++ ; break ;
	default:  
	  value = a_float(value) ;
	  if ( isNaN(value) )
	    {
	      line[data_col].set_value(NaN) ;
	      return ;
	    }
	  if ( from.real_weight_add )
	    {
	      values.push([(value - from.min) / (from.max - from.min), from]);
	    }
	  else
	    {
	      values.push([value, from]) ;
	      if (column.mean_of || column.best_of )
		{
		  line[data_col].set_value('???') ;
		  return ;
		}
	    }
	  break ;
	}
    }
  if ( nr_abj == column.average_columns.length )
    {
      line[data_col].set_value(abj) ;
      return ;
    }
  if ( column.best_of )
    {
      if ( column.best_of > 0 )
	{
	  values.sort() ;
	  values.reverse() ;
	  if ( values.length < column.best_of )
	    {
	      line[data_col].set_value(NaN) ;
	      return ;
	    }
	  values = values.slice(0, column.best_of) ;
	}
      else
	{
	  values.sort() ;
	  if ( values.length < -column.best_of )
	    {
	      line[data_col].set_value(NaN) ;
	      return ;
	    }
	  values = values.slice(0, values.length + column.best_of) ;
	}
    }
  if ( column.mean_of )
    {
      var i = -column.mean_of ;
      values.sort() ;
      values.reverse() ;
      if( i>0 && nr_abi )
	{
	  var n = Math.min(i, nr_abi) ;
	  i -= n ;
	  if ( values.length < n )
	    {
	      line[data_col].set_value(NaN) ;
	      return ;	      
	    }
	  values = values.slice(0, values.length - n) ;
	}
      if ( i > 0 )
	{
	  if ( values.length < i )
	    {
	      line[data_col].set_value(NaN) ;
	      return ;
	    }
	  values = values.slice(0, values.length - i) ;
	}
      if ( false )
	{
	  var s = '' ;
	  for(var ii in values)
	    s += ' ' + values[ii][0] ;
	  line[data_col].set_comment(s) ;
	}
    }
 
  var weight = 0, w ;
  var sum = 0 ;
  var sum2 = 0 ;
  var nr_sum = 0 ;
  for(var c in values)
    {
      c = values[c] ;
      from = c[1] ;
      value = c[0] ;
      if ( from.real_weight_add )
	{
	  w = from.real_weight ;
	  sum += w * value ;
	  weight += w ;
	}
      else
	{
	  sum2 += from.real_weight * value ;
	  nr_sum++ ;
	}
    }

  if ( nr_abj == column.average_columns.length )
    value = abj ;
  else if ( nr_abi == column.average_columns.length )
    value = abi ;
  else if ( weight !== 0 )
    {
      if ( sum2 <= 0 && nr_abi == values.length - nr_sum )
      {
	value = abi ;
      }
      else
      {
	sum = column.min + sum * (column.max - column.min) / weight + sum2 ;
	value = Number(sum.toPrecision(6)) ;
      }
      if ( column.round_by )
	{
	  value = Math.round(value / column.round_by) * column.round_by ;
	}
    }
  else if ( nr_sum == column.average_columns.length )
    value = sum2 ;
  else
    value = ppn ;

  line[data_col].set_value(value) ;
}

function compute_max_real_old(data_col, line)
{
  var column = columns[data_col] ;
  var the_max ;

  if ( column.average_columns.length === 0 )
    {
      line[data_col].set_value('') ;
      return;
    }

  the_max = -1 ;
  for(var c in column.average_columns)
    {
      c = column.average_columns[c] ;
      value = line[c].value ;
      from = columns[c] ;
      if ( value === '' ) 
	value = from.empty_is ;
      if ( value === '' )
	continue ;
      value = a_float(value) ;
      value = (value - from.min) / from.max ;
      if ( value > the_max )
	the_max = value ;
    }

  if ( the_max >= 0 )
    line[data_col].set_value(the_max * (column.max - column.min) + column.min);
  else
    {
      // No good number
      line[data_col].set_value('') ;
    }

}

function compute_cow_old(data_col, line)
{
  var column = columns[data_col] ;

  if ( column.average_columns.length != 1 )
    return ;
  if ( line[data_col].author !== '' )
    return ;

  c = column.average_columns[0] ;

  var value = line[c].value ;

  if ( value === '' )
    value = columns[c].empty_is ;

  line[data_col].set_value(value) ;
}


function compute_diff_date_old(data_col, line)
{
  var column = columns[data_col] ;

  if ( column.average_columns.length !== 2 )
    {
      line[data_col].set_value('') ;
      return;
    }

  var div = Number(column.comment.split('/')[1]) ;
  if ( isNaN(div) )
    div = 1 ;  

  var values = [] ;
  for(var c in column.average_columns)
    {
      c = column.average_columns[c] ;
      value = line[c].value ;
      from = columns[c] ;
      if ( value === '' ) 
	value = from.empty_is ;
      values.push(get_date(value)) ;
    }
  try {
    line[data_col].set_value(
      (values[1].getTime() - values[0].getTime())/(div*1000*86400)) ;
  }
  catch(e) { line[data_col].set_value('') ; }
}

function compute_weighted_percent_(data_col, line, filter)
{
  var column = columns[data_col] ;
  if ( column.real_type.cell_compute === undefined )
  {
    if ( filter(line[data_col]) )
      return 1. ;
    else
      return 0. ;
  }
  var sum = 0, sum_weight = 0, weight ;
  for(var col in column.average_columns)
  {
    col = column.average_columns[col] ;
    
    if ( ! columns[col].real_weight_add )
      continue ;

    weight = columns[col].real_weight ;
    sum += weight * compute_weighted_percent_(col, line, filter);
    sum_weight += weight ;
  }
  if ( sum_weight == 0 )
    return 0. ;
  return sum / sum_weight ;
}

function compute_weighted_percent(data_col, line)
{
  var column = columns[data_col] ;

  if ( column.average_columns.length !== 1 )
    {
      line[data_col].set_value('') ;
      return;
    }
  var v = column.min + (column.max - column.min) *
    compute_weighted_percent_(column.average_columns[0],
			      line, column.nmbr_filter) ;

  if ( column.round_by )
    v = Math.round(v / column.round_by) * column.round_by ;

  line[data_col].set_value(v) ;
}


