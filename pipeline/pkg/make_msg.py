import sys
sys.path.insert(0, '/home/claude/pkg')
from texts import message
from notes import N, NUM
s = sys.argv[1]
m = message(s, NUM[s], N[s])
open(f'/home/claude/pkg/msg_{s}.txt', 'w').write(m)
print(len(m))
