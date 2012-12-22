#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    Copyright (C) 2010-2012 Thierry EXCOFFIER, Universite Claude Bernard
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

package_name = "TOMUSS" # Choose your package name (for absolute import)

caller_globals = sys._getframe(1).f_globals

# Only the __main__ must become a package, not the other modules.
if caller_globals["__name__"] == '__main__':
    # Search package root: its container directory does not have an __init__.py
    current_dir = __file__.split(os.path.sep)
    if len(current_dir) == 1:
        current_dir = os.getcwd().split(os.path.sep)
    else:
        # Remove filename
        current_dir.pop()
    local_name = []
    while os.path.exists(os.path.sep.join(current_dir + ['__init__.py'])):
        local_name.insert(0, current_dir.pop())
    # Import the package root (else relative imports fails)
    sys.path.insert(0, os.path.sep.join(current_dir))
    sys.modules[package_name] = __import__(local_name[0])

    # The python path can be reset to the initial value
    sys.path.pop(0)

    # The local top level directory is renamed to the desired package name.
    current_dir.append(local_name[0])
    local_name[0] = package_name

    # Set the good package name (eg. TOMUSS or TOMUSS.YYY or TOMUSS.YYY.TTT)
    __package__ = caller_globals["__package__"] = '.'.join(local_name)

    if len(local_name) != 1:
        # To fix absolute import: load the directory containing the script
        __import__('.'.join(local_name))

    # Some old table data file contains 'from data import *'
    # in place of 'from TOMUSS.data import *'
    # This link fixes the problem
    for i in ('data', 'abj', 'teacher'):
        __import__(package_name + '.' + i)
        sys.modules[i] = sys.modules[package_name + '.' + i]

    if '.' in __package__:
        # Not in a TOMUSS server but in a script in a direct subdirectory
        os.chdir(os.path.sep.join(current_dir))
        sys.stderr.write("*"*50 + '\n')
        sys.stderr.write("BEWARE The current directory is now %s\n"
                         % os.getcwd())
        sys.stderr.write("*"*50 + '\n')
        from TOMUSS import configuration
        if 'REGTEST_SERVER' in __package__:
            configuration.regtest = True
        if configuration.regtest:
            from TOMUSS import regtestpatch
            regtestpatch.do_patch()

        configuration.terminate()
        sys.stderr.write('DB=%s\n' % configuration.db)

        from TOMUSS import plugins
        plugins.load_types()

        from TOMUSS import column
        column.initialize()

        from TOMUSS import utilities
        utilities.init(launch_threads=False)

        from TOMUSS import document
        document.table(0, 'Dossiers', 'config_table', None, None)
