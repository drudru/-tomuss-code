#!/usr/bin/python

"""
Parameters :
   * a plugin time file as :  LOGS/SUIVI8898/2013.times
   * a plugin name as : student
   * time precision in seconds as : 86400
"""

import sys
import time
import math

times = open(sys.argv[1])
plugin = sys.argv[2]
interval = int(sys.argv[3])

n = 0
start = None
stats = []
hours = [[] for i in range(24)]

for line in times:
    line = line[:-1].split(' ')
    if line[-1] != plugin:
        continue
    duration = float(line[1])
    t = int(line[0].split('.')[0])
    hours[ (t % 86400) // 3600 ].append(duration)
    t //= interval
    if start is None:
        start = t
    t -= start

    while t >= len(stats):
        stats.append([])
    stats[t].append(duration)

def histogram(v, minimum=0.001, maximum=5000):
    h = [0]*int(math.log(maximum) - math.log(minimum))
    for ii in v:
        h[int(math.log(ii) - math.log(minimum))] += 1
    return ' '.join('%4d' % i
                    for i in h)

for t, i in enumerate(stats):
    if not i:
        continue
    i.sort()
    print time.strftime('%Y%m%d',time.localtime((start+t)*interval)
                        ), "%5d %6.3f %6.3f %6.3f " % (
        len(i), min(i), sum(i)/len(i), max(i)), histogram(i)
        
        
for t, i in enumerate(hours):
    if not i:
        continue
    i.sort()
    print "%02d:00 %5d %6.3f %6.3f %6.3f " % (t,
        len(i), min(i), sum(i)/len(i), max(i)), histogram(i)
        
        
    
    
    
    
