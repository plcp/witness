# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
from __future__ import unicode_literals, division, with_statement

import sys
import pylacode as pl
assert sys.version_info >= (2, 7)

class fe:
    def __init__(self, size, source=None, **metadata):
        self.source = source
        self.value = pl.logic.obsl(size=size)
        self.uuid = None
        self.meta = dict(**metadata)
        self.uid = None
