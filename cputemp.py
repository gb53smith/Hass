#!/usr/bin/python3.6
from subprocess import Popen, PIPE
p = Popen(['/opt/vc/bin/vcgencmd', 'measure_temp'], stdout=PIPE)
s = str(p.communicate())
x = s.split('=')
y = x[1].split('\'')
temp = y[0]
print(temp)
