#!/usr/bin/python3
# -*- coding: utf-8

import ast
import collections
import re
import sys
import getopt

class Opt:
    def __init__(self):
        self.depth = 6
        self.stop = "User"
        self.minimum = 2
        for name, value in getopt.getopt(sys.argv[1:], "",
                                         ["depth=", "stop=", "minimum="])[0]:
            setattr(self, name.strip('-'), value)
        s = sys.argv[0]
        for name, value in self.__dict__.items():
            s += " --" + name + "=" + str(value)
        print(s)
        print("   * depth   : maximum depth of the tree")
        print("   * stop    : tree is pruned under this attribute")
        print("   * minimum : hide items if less than this value")
        print()
        
opt = Opt()

names = ['Error', 'Script', 'Line', 'URL', 'User', 'Browser', 'Agent']


def canonize(txt):
    return re.sub('=ST[-0-9a-zA-Z.]*', 'Ⓣ', txt
    ).replace(".univ-lyon1.fr","").replace("; ", ";").strip(" .")

f = open("LOGS/javascript_errors", "r", encoding = "utf-8")
lines = []
for line in f:
    try:
        lines.append([canonize(i) for i in ast.literal_eval(line)[1:]])
    except SyntaxError:
        print(line)
f.close()
lines = [line
	for line in lines
	if len(line) == len(names)
	]

browser = names.index("Browser")
for line in lines:
    line[browser] = re.sub(" *[0-9._]{3,99} *", "€", line[browser])

def remove_cols(lines, cols):
    cols = set(cols)
    return [
        tuple(v
         for (i, v) in enumerate(line)
         if i not in cols
         )
        for line in lines
        ]

def most_common_recursive(lines, cols, depth=0):
    if depth == opt.depth:
        return
    if len(lines) < opt.minimum:
        return
    nr_lines = len(lines)
    while lines:
        counters = []
        max_val = 0
        for i, col in enumerate(cols):
            counter = collections.defaultdict(int)            
            for line in lines:
                counter[line[i]] += 1
            m = max((v, k, i)
                    for k, v in counter.items()
                )
            if m > max_val:
                max_val = m

        repetition, value, column = max_val

        if repetition < nr_lines // 20 and depth != 0:
            break
        # v = str(value, "UTF-8", "replace")
        v = value
        if len(v) > 60:
            v1 = v[:len(v)//2]
            v2 = v[len(v)//2:]
        else:
            v1 = v
            v2 = ''

        print('   |'*depth + "%d*%s=%s" % (repetition, cols[column], v1))
        if v2:
            print('   |'*depth + " "*len(cols[column]+str(repetition)+"*="
                                           ) + v2)

        selected = []
        unselected = []
        for line in lines:
            if line[column] == value:
                selected.append(line)
            else:
                unselected.append(line)

        if cols[column] != opt.stop:
            most_common_recursive(remove_cols(selected, [column]),
                                  cols[:column] + cols[column+1:],
                                  depth+1
                          )
        lines = unselected
    

most_common_recursive(lines, names)
