#!/bin/env python3
# -*- coding: utf-8 -*-
#    TOMUSS: The Online Multi User Simple Spreadsheet
#    Copyright (C) 2011 Thierry EXCOFFIER, Universite Claude Bernard
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
#    Contact: Thierry.EXCOFFIER@bat710.univ-lyon1.fr

from ..column import ColumnAttr

class ColumnFill(ColumnAttr):
    name = "fill"
    gui_display = "GUI_a"
    need_authorization = 0
    action = "fill_column"
    default_value = 1
    check_and_set = 'function() { return 1; }'
    css = """
    #popup DIV.fill_column_div { border: 4px solid red ; overflow:scroll ;
                          left: 5%; right: 5%; bottom: 5% ; top: 5%}
    #stop_the_auto_save { font-size:70%; border:1px solid red}
    .fill_menu {
    line-height: 1.7em ;
    width: 18em; /* copy/paste */
    }
    .fill_column_right { height: 0px }
    #fill_table { margin-top: 0.3em ; border-spacing: 0px }
    #fill_table TR { vertical-align: top ; }
    #fill_table TH {
    padding: 1px ;
    border-left: 1px solid black;
    border-top: 1px solid black;
    }
    #fill_table TH DIV.tipped { width: 100%; display: block }
    .room_cb, .room_used { border-bottom: 1px solid #CCC }
    .room_line { height: 1.1em }
    .room_cb { width: 1em }
    .room_used { width: 3em }
    .room_places { width: 30% }
    .room_name { width: 70% }
    .room_comment {
         width: 15em ;
         position: absolute ;
         left: 40% ;
         margin-top: 1.4em ;
         border:1px solid #888 ;
         display: none ;
         background: rgba(255,255,255,0.9) ;
         z-index: 1000 ;
    }
    #popup DIV.fill_column_div INPUT { padding-left: 2px }
    TABLE.simulation { border: 1px solid black }
    TD.old_value { text-align: right }
    TD.old_value, TD.new_value { white-space: pre; width: 50% }
    .room_name:hover .room_comment {
         display: inline-block ;
        }
    BODY.tomuss TABLE TD.fill_result {
        overflow: visible ;
        width: 18em; /* copy/paste */
        line-height: 1em ;
        padding-left: 0.2em ;
    }
    DIV.fill_important, DIV.fill_warning, DIV.fill_error, DIV.fill_replace {
    margin-bottom: 0.5em ;
    border: 1px solid black ;
    }
    .fill_result H3 { margin-bottom: 0.4em ; font-size: 100% }
    .fill_result #stop_the_auto_save { margin-bottom: 1em }
    .fill_error { background: #F88; }
    .fill_important { color: #000 ; background: #8F8 }
    .fill_warning { background: orange ; }
    .fill_replace { background: #F8F ; }
    .room_enumeration INPUT { background: #EFF }
    .room_predefined INPUT { background: #FFE }
    .room_created_empty INPUT { background: #FFF }
    .room_yet_used INPUT { background: #EEF }
    .show_in_comment TR.only_value, .show_in_value TR.only_comment
        { display: none }
    .fill_result BUTTON { width: 100% ; }

  .pulsing {
  /* display: inline-block ; */
  animation-duration: 2s;
  animation-name: keys_pulsing;
  animation-iteration-count: infinite;
  -webkit-animation-duration: 2s;
  -webkit-animation-name: keys_pulsing;
  -webkit-animation-iteration-count: infinite;
    }
 @keyframes keys_pulsing {
    0% { background: #EEE }
    50% { background: #BBB }
    100% { background: #EEE }
  }
 @-webkit-keyframes keys_pulsing {
    0% { background: #EEE }
    50% { background: #BBB }
    100% { background: #EEE }
  }

    """
