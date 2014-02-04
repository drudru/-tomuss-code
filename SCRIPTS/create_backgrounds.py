#!/usr/bin/python

"""Create the translated image background for empty INPUT"""

import os
import tomuss_init
from .. import utilities

for m in ('comment.png', 'filtre.png', 'filtre2.png',
          'title.png', 'teacher.png', 'columns.png',
          'visible.png' ,'empty.png', 'rounding.png',
	  'course_dates.png', "import.png"):
    f = open("xxx.svg", "w")
    f.write('''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg>
<text
       xml:space="preserve"
       style="font-size:20px;font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;text-align:start;line-height:125%;letter-spacing:0px;word-spacing:0px;writing-mode:lr-tb;text-anchor:start;fill:#B0B0B0;fill-opacity:1;stroke:none;font-family:Arial;-inkscape-font-specification:Arial"
       x="0"
       y="0"><tspan>''' + utilities._(m) + '''</tspan></text>
</svg>
''')
    f.close()
    os.system("inkscape --export-area-drawing --export-png=FILES/%s xxx.svg"
              % m)
    
