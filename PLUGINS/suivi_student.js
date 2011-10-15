/* To send the cell change and feedback */

function _cell(s, url, col_type)
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
    s.value = type_title_to_type(col_type).cell_test(s.value) ;

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

