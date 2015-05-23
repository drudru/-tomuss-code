#!/bin/env python
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
    #stop_the_auto_save { float:right; font-size:70%; border:1px solid red}
    .fill_menu { margin-top: 0.3em ; margin-bottom: 0.3em ; }
    #fill_table { margin-top: 0.3em ; border-spacing: 1px }
    #fill_table TR { vertical-align: top ; }
    #fill_table TH { border: 1px solid black; }
    #fill_table TH DIV.tipped { width: 100%; display: block }
    .room_line { height: 1.1em }
    .room_cb { width: 1em }
    .room_used { width: 3em }
    .room_places { width: 15% }
    .room_name { width: 35% }
    .room_comment { width: 20% ; font-size: 50% ; border:1px solid #DDD }
    .room_comment:hover { transform: scale(2,2) ;
        background: #EEE ; border: 1px solid #888 }
    TD.fill_result { overflow: auto ; font-size: 60% ; width: 30% }
    .fill_error { color: #FFF ; background: #F00 }
    .fill_important { color: #000 ; background: #0F0 }
    .fill_warning { color: #000 ; background: orange }
    .fill_replace { color: #800 ; }
    .room_predefined INPUT { background: #FFE }
    .room_created_empty INPUT { background: #FFF }
    .room_yet_used INPUT { background: #EEF }
    .show_in_comment TR.only_value, .show_in_value TR.only_comment
        { display: none }

  .pulsing {
  animation-duration: 2s;
  animation-name: keys_pulsing;
  animation-iteration-count: infinite;
  display: inline-block ;
    }
 @keyframes keys_pulsing {
    0% { transform: scale(1,1) }
   20% { transform: scale(1.5,1.5) }
   40% { transform: scale(1,1) }
  100% { transform: scale(1,1) }
  }
    /*
 @keyframes keys_pulsing {
    0%   { transform: rotate(15deg) }
    50%  { transform: rotate(-15deg) }
    100% { transform: rotate(15deg) }
  }
    */

    """
