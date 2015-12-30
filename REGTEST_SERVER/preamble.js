window = { location: { pathname: "" } } ;
navigator = { appName: "", userAgent: "" } ;
document = {
  getElementsByTagName: function() { return [] ; },
  getElementById: function() { return document.object },
  write: function() { },
  body: { clientHeight: 1000 },
  object: {
    focus: function() { },
    style: {}
    }
}

