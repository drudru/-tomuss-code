#!/usr/bin/python3

"""
THIS CODE IS NOT WORKING.
It does 'for in' search but do not patch them

Patch sources files to change the JavaScript 'for' loop on arrays.

For each 'for' it display contextual information in order to
check if the itered set is an array or a dictionnary.

The user answer is memorized in the source code in order to run
this script many time without asking the same question to the user.

"""

import subprocess
import re

re_for = re.compile(r'^([ \t]*for *\()(var )?([^)]*) in ([^)]*)\)(.*)')

ls = subprocess.Popen(["git", '--no-pager', 'ls-files'],
                      stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE)



for filename in ls.stdout:
    filename = filename.strip()
    lines = []
    f = open(filename, "r", encoding = "utf-8")
    modified = False
    line_number = 0
    for line in f:
        line_number += 1
        lines.append(line)
        match = re_for.match(line)
        if not match:
            continue
        left, var, name, array_or_dict, right = match.groups()
        print('='*79)
        print("%s:%d %s" % (filename, line_number, line.strip()))
        print('.'*79)
        before = []
        found = False
        array_or_dict_name = re.split('[.[(]', array_or_dict)[0]
        for previous_line in lines[-1::-1]:
            before.append('        ' + previous_line)
            if previous_line.startswith('function'):
                if (re.match(r'.*\b' + array_or_dict_name + r'\b.*',
                                 previous_line)
                    ):
                    found = 'function'
                    before[-1] = before[-1].replace('        ', '@@@@@@@@', 1)
                break
            if re.match(r'.*\b'+array_or_dict_name+r'\b.*', previous_line):
                if (' var ' in previous_line
                    and re.match(r'.*(\bvar|,) ' + array_or_dict_name + r'\b.*',
                                 previous_line)
                    ):
                    before[-1] = before[-1].replace('        ', '########', 1)
                    found = 'exact'
                    break
                else:
                    if re.match('.*' + array_or_dict_name +
                                r' *= .*\.split\([^)]*\) *;.*',
                                previous_line):
                        before[-1] = before[-1].replace('        ',
                                                        '-SPLIT--', 1)
                        found = 'split'
                        break
                    if array_or_dict_name + '.push(' in previous_line:
                        before[-1] = before[-1].replace('        ',
                                                        '--PUSH--', 1)
                        found = 'push'
                        break
                        
                    before[-1] = before[-1].replace('        ', '--------', 1)
                    if previous_line != line:
                        found = 'missing'
                    
        before.reverse()
        for i in before:
            print(i, end=' ')
        print()

        if not found:
            try:
                x = subprocess.check_output(
                    ['git', '--no-pager', 'grep',
                     r'\b' + array_or_dict_name + r'\b *= ',
                     '--', '*.js'])
                print('Affectations to this array or dict name:')
                print(x)
                print()
            except:
                pass
        if found == 'function':
            print('Calls to this function:')
            name = previous_line.split('function ')[1].split('(')[0].strip()
            x = subprocess.check_output(['git', '--no-pager', 'grep', '-E',
                                         r'\b' + name + r'\(',
                                         '--', '*.js'])
            print(x)
            print()

        # POSER LA QUESTION : dict / array / latter
        print("   left:", left)
        print("   var:", var)
        print("   name:", name)
        print("   array_or_dict:", repr(array_or_dict))
        print("   right:", right)
    f.close()
