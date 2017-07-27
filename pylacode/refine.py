# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
from __future__ import unicode_literals, division, with_statement

import sys
import pylacode as pl
assert sys.version_info >= (2, 7)

import warnings

class NoDataRefinedError(Exception):
    pass

class data(object):
    def __init__(self, name, transform, inverse=None, **mdata):
        self._transform = transform
        self._inverse = inverse
        self.mdata = dict(**mdata)
        self.name = name

    def transform(self, state):
        self._transform(state=state, parent=self)

    def inverse(self, state):
        if self._inverse is None:
            warnings.warn('No inverse function provided while refining data '
                + 'with {} backend (id: {}).'.format(self.name, self))
            return
        self._inverse(state=state, parent=self)

    def __repr__(self):
        return self.name + object.__repr__(self)
