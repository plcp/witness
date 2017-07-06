# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
from __future__ import unicode_literals, division, with_statement

import sys
assert sys.version_info >= (2, 7)

import warnings

class _base:
    '''Base class for logic types

    '''

    def __init__(self, value=None, size=None):
        if value is not None:
            assert value in types
            self.size = len(value)

            if size is not None:
                warnings.warn('Size given but ignored')

        else:
            assert size is not None
            self.size = size

class obsl(_base):
    '''Opinion-Based Subjective Logic (as found in the litterature)

    '''
    def __init__(self, value=None, size=None):
        _base.__init__(self, value, size)
        pass

class tbsl(_base):
    '''Three-Value-Based Subjective Logic

    '''
    def __init__(self, value=None, size=None):
        _base.__init__(self, value, size)
        pass

class ebsl(_base):
    '''Evidence-Based Subjective Logic

    '''
    def __init__(self, value=None, size=None):
        _base.__init__(self, value, size)
        pass

types = [obsl, tbsl, ebsl]
