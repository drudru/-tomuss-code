#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    Copyright (C) 2010-2011 Thierry EXCOFFIER, Universite Claude Bernard
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

import sys
import os

if not os.path.isdir('LOCAL'):
    for i in ('FILES', 'TMP', 'DB', 'TEMPLATES'):
        if not os.path.islink(i):
            sys.stderr.write('Missing link: %s in %s\n' % (i, os.getcwd()))
        elif not os.path.isdir(i):
            sys.stderr.write('Should be a directory: %s in %s\n' % (
                i, os.getcwd()))

    sys.path.insert(0,
                    os.path.sep
                    + os.path.join(*os.getcwd().split(os.path.sep)[:-1])
                    )
else:
    sys.path.insert(0, os.getcwd())


import configuration
if configuration.regtest:
    import regtestpatch
    regtestpatch.do_patch()

configuration.terminate()
sys.stderr.write('DB=%s\n' % configuration.db)

import plugins
plugins.load_types()

import document
document.table(0, 'Dossiers', 'config_table', None, None)
