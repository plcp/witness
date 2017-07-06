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
        assert other in types

        if isinstance(self, other):
            return self.copy()

        return other(size=self.size)

    def copy(self):
        n = self.__class__(size=self.size)
        n.value = tuple([np.array(a, copy=True) for a in self.value])
        return n

    def __len__(self):
        return self.size

class obsl(_base):
    '''Opinion-Based Subjective Logic (as found in the litterature)

    '''
    def reset(self, apriori=0.5):
        _belief = np.zeros(self.size)
        _disbelief = np.zeros(self.size)
        _uncertainty = np.ones(self.size)
        _apriori = np.ones(self.size) * apriori

        self.value = (_belief, _disbelief, _uncertainty, _apriori)

    def cast_to(self, other):
        n = _base.cast_to(self, other)
        if isinstance(n, obsl):
            return n

        if isinstance(n, ebsl):
            raise NotImplementedError
        elif isinstance(n, tbsl):
            raise NotImplementedError

        return None

class tbsl(_base):
    '''Three-Value-Based Subjective Logic

    '''
    def reset(self, apriori=0.0):
        _truth = np.zeros(self.size)
        _confidence = np.zeros(self.size)
        _apriori = np.ones(self.size) * apriori

        self.value = (_truth, _confidence, _apriori)

    def cast_to(self, other):
        n = _base.cast_to(self, other)
        if isinstance(n, tbsl):
            return n

        if isinstance(n, ebsl):
            raise NotImplementedError
        elif isinstance(n, obsl):
            raise NotImplementedError

        return None

class ebsl(_base):
    '''Evidence-Based Subjective Logic

    '''
    def reset(self, apriori=0.5):
        _positive = np.zeros(self.size)
        _negative = np.zeros(self.size)
        _apriori = np.ones(self.size) * apriori

        self.value = (_positive, _negative, _apriori)

    def cast_to(self, other):
        n = _base.cast_to(self, other)
        if isinstance(n, ebsl):
            return n

        if isinstance(n, tbsl):
            raise NotImplementedError
        elif isinstance(n, obsl):
            raise NotImplementedError

        return None

types = [obsl, tbsl, ebsl]
