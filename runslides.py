#!/usr/bin/env python

import os
import os.path as op
import subprocess

cmd = ['python', 'runserver.py']
env = os.environ.copy()
env['PYTHONPATH'] = op.dirname(op.abspath(__file__))
try:
	subprocess.call(cmd, cwd='slides', env=env)
except KeyboardInterrupt:
	pass
