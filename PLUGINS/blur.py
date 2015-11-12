# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2015 Thierry EXCOFFIER, Universite Claude Bernard
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#    Contact: Thierry.EXCOFFIER@univ-lyon1.fr

import json
from .. import files
from .. import teacher
from .. import inscrits

files.append('style.css', 'blur.py', r"""

IMG.phot, IMG.big { filter: blur(6px) ; }
IMG.pic { filter: blur(12px) ; }

""")

def create_blurred():
    import random
    import os
    from .. import configuration
    from .. import document
    from .. import utilities
    from .. import tablestat
    year, semester = configuration.year_semester
    firstnames = set()
    surnames = set()
    student_ids = set()
    def canonise(txt):
        return utilities.flat(txt.lower())
    def add_login(login):
        if "." not in login:
            return
        fn, sn = login.split('.')[:2]
        firstnames.add(canonise(fn))
        if sn:
            surnames.add(canonise(sn))
    for t in tablestat.les_ues(year, semester, true_file=True):
        print(t)
        try:
            document.update_students.pop()
        except IndexError:
            pass
        if not t.official_ue:
            continue
        for master in t.masters:
            add_login(master)
        for line in t.lines.values():
            if line[0].value == '':
                continue
            if '.' in line[0].value:
                continue
            student_ids.add(inscrits.login_to_student_id(
                canonise(line[0].value)))
            firstnames.add(canonise(line[1].value))
            surnames.add(canonise(line[2].value))
            for cell in line:
                add_login(cell.author)
    for ue in teacher.all_ues().values():
        for name in ue._responsables:
            fn, sn = name.split(" ", 1)
            firstnames.add(utilities.flat(fn.lower()))
            surnames.add(utilities.flat(sn.lower()))
        for login in ue._responsables_login:
            add_login(login)

    s = ['# -*- coding: utf-8 -*-']
    for name in ('student_ids', 'firstnames', 'surnames'):
        s.append('%s = {' % name)
        all_values = tuple(locals()[name])
        firsts = all_values[:len(all_values)//2]
        lasts = all_values[len(all_values)//2:]
        # XXX Not correct algorithm if there are duplicate shortened names
        for a, b in zip(firsts, lasts) + zip(lasts, firsts):
            b = b.split('(')[0].replace('-', ' ').split(" ")
            b.sort(key=len)
            b = b[-1] # The longest name part
            s.append('"%s": "%s",' % (a, b))
        s.append("}")

    utilities.write_file(os.path.join('TMP', 'blurred.py'), '\n'.join(s))
    from ..TMP import blurred
    return blurred

try:
    from ..TMP import blurred
except ImportError:
    blurred = create_blurred()

files.append('lib.js', 'blur.py',
    "student_ids = %s ; firstnames = %s ; surnames = %s ;" % (
        json.dumps(blurred.student_ids),
        json.dumps(blurred.firstnames),
        json.dumps(blurred.surnames))
       + """
// XXX Unecessary function because in the dictionary A=>B and B=>A
function get_real_id(student_id)
{
   student_id = login_to_id(student_id) ;
   for(var i in student_ids)
       if ( student_ids[i] == student_id )
            return i ;
   return student_id ;
}
function get_real_name(name)
{
  for(var i in surnames)
     if ( surnames[i] == name )
       return i ;
  for(var i in firstnames)
     if ( firstnames[i] == name )
       return i ;
  return i ;
}
function student_picture_url_new(login)
{
   return student_picture_url_new.old(get_real_id(login)) ;
}
student_picture_url_new.old = student_picture_url ;
student_picture_url = student_picture_url_new ;

function change_abjs_new(d)
{
       for(var i in d)
          d[blur_txt(i)] = d[i] ;
       change_abjs_new.old(d) ;

       for(var i in table_attr.mails)
          table_attr.mails[blur_txt(i)] = blur_txt(table_attr.mails[i])
}
change_abjs_new.old = change_abjs ;
change_abjs = change_abjs_new ;
"""
)

files.append('utilities.js', 'blur.py', r'''

function blur_txt(orig)
{
   if ( orig === undefined || orig.toLowerCase === undefined )
      return orig ;
   if ( orig.length <= 1 )
      return orig ;
   if ( window.real_ue !== undefined )
      return orig ;
   txt = flat(orig.toLowerCase()) ;
   var t = student_ids[txt] || firstnames[txt] || surnames[txt] ;
   if ( t )
      {
      if ( orig == orig.toUpperCase() )
         return t.toUpperCase() ;
      if ( orig.substr(0,1) == orig.substr(0,1).toUpperCase() )
         return t.substr(0,1).toUpperCase() + t.substr(1) ;
      return t ;
      }
   if ( login_to_id(orig) != orig )
     {
        t = student_ids[login_to_id(orig)] ;
        if ( t )
            return the_login(t) ;
     }

   var t, d = ["_", "-", "<", "@", ".", "=", " "] ;
   orig = orig.trim() ;
   for(var i in d)
     {
       t = orig.split(d[i]) ;
       if ( t.length >= 2 )
           {
           var s = [] ;
           for(var j in t)
               if ( t[j].length > 2 )
                   s.push(blur_txt(t[j])) ;
               else
                   s.push(t[j]) ;
           return s.join(d[i]) ;
           }
    }
   return orig ;
}

function blur_history(txt)
{
   if ( txt === undefined )
      return txt ;
  txt = txt.split(/\),·/g) ;
  var s = '', j ;
  for(var i in txt)
    {
      i = txt[i] ;
      if ( i === '' )
         continue ;
      j = i.split("\n") ;
      k = j[1].split(" ") ;
      s += j[0] + "\n" + k[0] + " " + blur_txt(k[1]) + "),·" ;
    }
  return s ;
}

function blur_recursive(data)
{
   if ( !data || data.toFixed )
       return data ;
   if ( typeof data === "string" )
       return blur_txt(data) ;
   if ( data instanceof Array )
   {
      var v = [] ;
      for(var k in data)
         v.push( blur_recursive(data[k]) ) ;
      return v ;
   }
   if ( typeof data === "object")
   {
      var d = {} ;
      for(var k in data)
        d[k] = blur_recursive(data[k]) ;
      return d ;
   }
  return data ;
}

function C(value, author, date, comment, history)
{
     return new Cell(blur_txt(value), blur_txt(author), date, comment,
                     blur_history(history)) ;
}

''')

files.append('display.js', 'blur.py', """

function display_update_new(x, y)
{
  try {
    if ( ! display_update_new.done )
        all_ues = blur_recursive(all_ues) ;
    display_update_new.done = true ;
    }
   catch(e) { } ;
  return display_update_new.old(blur_recursive(x), y) ;
}
display_update_new.old = display_update ;
display_update = display_update_new ;
""")



files.append('suivi_student.js', 'blur.py', """
function DisplaySemesters_new(node)
{
   var save = display_data['Login'] ;
   var login ;
   display_data['Login'] = the_login(get_real_id(display_data['Login'])) ;
   var v = DisplaySemesters_new.old(node) ;
   display_data['Login'] = save ;
   return v ;
}
DisplaySemesters_new.old = DisplaySemesters ;
DisplaySemesters = DisplaySemesters_new ;
""")

files.append('home3.js', 'blur.py', """
function DisplayHomeLogin(node)
{
  return blur_txt(username) ;
}

function search_student_change_new(t)
{
  var x = {value: blur_txt(t.value), parentNode: t.parentNode} ;
  search_student_change_new.old(x) ;

  if ( ! full_login_list_new.cache )
     full_login_list_new_init() ;
}
search_student_change_new.old = search_student_change ;
search_student_change = search_student_change_new ;

function full_login_list_new(login, results, add)
{
   full_login_list_new.old(login, blur_recursive(results), add) ;
   ask_login_list = blur_txt(login) ;
   full_login_list.cache[ask_login_list] = full_login_list.cache[login] ;
}

function full_login_list_new_init()
{
   full_login_list_new.old = full_login_list ;
   full_login_list_new.cache = full_login_list.cache ;
   full_login_list = full_login_list_new ;
}

""")
