#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

__version__ = "0.1.0"

#try:
#from . import radiative_transfer as rt
#except:
#    print("Problem with rt, will not work")
from . import photospheres
from .session import Session
