#!/usr/bin/python

f = open("LOGS/VM_usage", "r")
data = []
last = '24'
for line in f:
    line = line.strip().split(' ')
    if len(line) != 8:
        continue
    try:
        h, m, s = line[4].split(':')
        hour = int(h) + int(m)/60.
        s1 = int(line[6].split(":")[1])
        s2 = int(line[7].split(":")[1])
    except ValueError:
        continue
    if hour < last:
        data.append([])
    data[-1].append((hour, s1, s2))
    last = hour
f.close()

import matplotlib.pyplot
plt = matplotlib.pyplot
plt.xlabel("Heure")
plt.ylabel("Mem")
plt.figure()
plt.axes().set_xticks(range(24))

for day in data:
    h, x, y = zip(*day)
    plt.plot(h, x, color="red", alpha=1, linewidth=0.1)
    plt.plot(h, y, color="green", alpha=1, linewidth=0.1)

plt.savefig("xxx-vm-usage.png", dpi=300)

print "xxx-vm-usage.png computed"

