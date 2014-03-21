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

def histogram(v=[], minimum=0.001, maximum=5000, header=False):
    if header:
        return '         #Call MIN    MOY    MAX   ' + ''.join(
            '%6.0e' % (math.exp(ii) * minimum)
            for ii in range(int(math.log(maximum) - math.log(minimum)))
            )
    else:
        h = [0]*int(math.log(maximum) - math.log(minimum))
        for ii in v:
            h[int(math.log(ii) - math.log(minimum))] += 1
    return "%5d %6.3f %6.3f %6.3f" % (
        len(v), min(v), sum(v)/len(v), max(v)) + ''.join('%6d' % i
                    for i in h)


print histogram(header=True)
for t, i in enumerate(stats):
    if not i:
        continue
    i.sort()
    print time.strftime('%Y%m%d',time.localtime((start+t)*interval)
                        ), histogram(i)
        
        
print histogram(header=True)
for t, i in enumerate(hours):
    if not i:
        continue
    i.sort()
    print "%02d:00   " % t, histogram(i)
        
        
    
    
    
    
