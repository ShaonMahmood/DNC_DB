# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import os
import sys
import logging


PROJECT_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')
print(PROJECT_ROOT)
PACKAGE_DIR = os.path.join(PROJECT_ROOT, 'dnc_db')
print(PACKAGE_DIR)


def execfile(path, global_vars=None, local_vars=None):
    with open(path, 'r') as f:
        code = compile(f.read(), path, 'exec')
        exec(code, global_vars, local_vars)



def activate_venv():

    # VENV = os.path.join(os.path.expanduser('~'), 'virtualenvs')
    #
    # if os.path.isfile(os.path.join(VENV, 'base_env/bin/activate_this.py')):
    #     execfile(os.path.join(VENV, 'base_env/bin/activate_this.py'),
    #              dict(__file__=os.path.join(VENV, 'base_env/bin/activate_this.py')))
    try:
        import django
        sys.path.extend([PROJECT_ROOT, PACKAGE_DIR])
        print(sys.path.extend([PROJECT_ROOT, PACKAGE_DIR]))
        os.environ["DJANGO_SETTINGS_MODULE"] = "dnc_db.settings"
        django.setup()

    except ImportError as e:
        print(e)



