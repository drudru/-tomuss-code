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

from column import TableAttr

class TableStatistics(TableAttr):
    name = "statistics"
    gui_display = "GUI_button"
    need_authorization = 0
    action = "display_statistics"
    css = '''

TD { overflow: hidden ; }
    
.s_td {
position: relative ;
padding-top: 0.6em ;
padding-bottom: 0.6em ;
padding-left: 0.2em ;
padding-right: 0.2em ;
min-height: 1em ;
position: relative;
left: 0;
right: 0;
}


.s_center {
left:0 ;
right:0 ;
top: .5em ;
bottom: 0 ;
position: absolute ;
text-align: center ;
white-space: nowrap ;
}
    
.s_mediane {
font-size: 60% ;
vertical-align: middle ;
}

.s_minimum {position: absolute;left:0  ;bottom: 0;font-size:60%;z-index:1;}
.s_maximum {position: absolute;left:0  ;top: 0   ;font-size:60%;z-index:1;}
.s_stddev  {position: absolute;right:0 ;bottom: 0;font-size:60%;z-index:1;}
.s_nr      {position: absolute;right:0 ;top: 0   ;font-size:60%;z-index:1;}


TH DIV.s_td { min-width: 7em ; min-height: 1.7em ; font-size: 80% }

TD DIV.s_td:hover { background: #FFA ; }

DIV.stat_enum { font-size: 60% ; }

SPAN.s_histogram {
position: absolute ;
bottom: 0 ;
left: 25% ;
font-size:60%;
}

DIV.s_histogram {
position: absolute ;
left: 50% ;
right: 0 ;
bottom: 0 ;
height: 1em ;
z-index: 0;
}

DIV.s_histogram DIV {
position: absolute ;
bottom: 0;
width: 2px ;
font-size:0px; /* For IE */
}

.s_stat_red { background: #FAA }
.s_stat_green { background: #AFA }



/* Kludge to make the SVG object clickable */
DIV.s_graph { position: relative; }
DIV.s_graph DIV.s_clickable {
position: absolute;
left:0;
top:0;
right:0;
bottom:0;
}


DIV.s_stat_tip, DIV.s_stat_tip TABLE TD { font-size: 70% }

DIV.s_stat_tip TABLE TR { vertical-align: top ; }

.s_stat_tip { margin: 0px ; }

/* =================== ZOOMED TIP ========================== */

DIV.s_zoomed_histogram {
position: relative ;
width: 100% ;
height: 8em ;
width: 40em;
margin: 1em ;
}

.s_enumeration { border-left: 4px solid #888 }

DIV.s_zoomed_histogram DIV {
position: absolute ;
bottom: 0;
width: 2em ;
vertical-align: bottom;
border: 1px solid #888 ;
}

DIV.s_zoomed_histogram DIV SPAN {
position: absolute ;
bottom: 0px ;
text-align: center ;
width: 100% ;
}

DIV.s_zoomed_histogram DIV DIV {
position: absolute ;
font-size: 80% ;
bottom: -1.4em ;
text-align: center;
border: 0px ;
}

DIV.s_zoomed_histogram_note DIV DIV {
left: -1em ;
}

DIV.s_zoomed_histogram_enum DIV DIV {
width: 100%;
}


'''
