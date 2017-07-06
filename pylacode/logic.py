# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
from __future__ import unicode_literals, division, with_statement

import sys
assert sys.version_info >= (2, 7)

import warnings
import numpy as np

class _base:
    '''Base class for logic types

    '''

    def __init__(self, other=None, size=None):
        if other is not None:
            assert other.__class__ in types
            if size is not None:
                warnings.warn('Size given but ignored')

            self.size = len(other)
            self.value = other.cast_to(self.__class__).value
        else:
            assert size is not None
            assert isinstance(size, int) and size > 0

            self.size = size
            self.reset()

    def reset(self):
        raise NotImplementedError

    def cast_to(self, other):
        raise NotImplementedError

class obsl(_base):
    '''Opinion-Based Subjective Logic (as found in the litterature)

    '''
    def reset(self, apriori=0.5):
        _belief = np.zeros(self.size)
        _disbelief = np.zeros(self.size)
        _uncertainty = np.ones(self.size)
        _apriori = np.ones(self.size) * apriori

        self.value = (_belief, _disbelief, _uncertainty, _apriori)

class tbsl(_base):
    '''Three-Value-Based Subjective Logic

    '''
    def reset(self, apriori=0.0):
        _truth = np.zeros(self.size)
        _confidence = np.zeros(self.size)
        _apriori = np.ones(self.size) * apriori

        self.value = (_truth, _confidence, _apriori)

class ebsl(_base):
    '''Evidence-Based Subjective Logic

    '''
    def reset(self, apriori=0.5):
        _positive = np.zeros(self.size)
        _negative = np.zeros(self.size)
        _apriori = np.ones(self.size) * apriori

        self.value = (_positive, _negative, _apriori)

types = [obsl, tbsl, ebsl]
