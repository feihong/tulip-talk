#!/usr/bin/env python

import sys
import os
import os.path as op
import subprocess

num = sys.argv[1]
dirname = (d for d in os.listdir('demos') if d.startswith(num)).send(None)
dirname = op.join('demos', dirname)
print(dirname)

cmd = ['python', 'demo.py']
env = os.environ.copy()
env['PYTHONPATH'] = op.dirname(op.abspath(__file__))
try:
    subprocess.call(cmd, cwd=dirname, env=env)
except KeyboardInterrupt:
    pass
