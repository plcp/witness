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
        if isinstance(other, tuple):
            if not len(other) == len(self.value_names):
                raise AssertionError(
                    'Expected a tuple of lenght {}'.format(
                    len(self.value_names)))

            s = len(other[0])
            for v in other:
                if not isinstance(v, np.ndarray):
                    raise AssertionError(
                        'Expecting numpy.ndarray: {} in {}'.format(
                        v, other))

                if not s == len(v):
                    raise AssertionError(
                        'Expecting uniform lenght: {}'.format(other))

            if size is not None:
                warnings.warn('Size given but ignored')

            self.size = len(other[0])
            self.value = other
        elif other is not None:
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

    @staticmethod
    def uniform(size):
        raise NotImplementedError

    def cast_to(self, other):
        assert other in types

        if isinstance(self, other):
            return self.copy()

        return other(size=self.size)

    def copy(self):
        n = tuple([np.array(a, copy=True) for a in self.value])
        return self.__class__(n)

    def __len__(self):
        return self.size

    def __eq__(self, other, rtol=1e-05, atol=1e-08, equal_nan=False):
        assert isinstance(other, self.__class__)

        return all([
                np.allclose(a, b, rtol, atol, equal_nan)
                for a, b in zip(self.value, other.value)])
    equals = __eq__

class obsl(_base):
    '''Opinion-Based Subjective Logic (as found in the litterature)

    '''
    value_names = ['belief', 'disbelief', 'uncertainty', 'apriori']

    def reset(self, apriori=0.5):
        _belief = np.zeros(self.size)
        _disbelief = np.zeros(self.size)
        _uncertainty = np.ones(self.size)
        _apriori = np.ones(self.size) * apriori

        self.value = (_belief, _disbelief, _uncertainty, _apriori)

    @staticmethod
    def uniform(size):
        _uncertainty = np.random.uniform(size=size)
        snd = np.random.uniform(high=(1.0 - _uncertainty), size=size)
        trd = 1.0 - snd - _uncertainty

        snd, trd = np.random.permutation((snd, trd))

        _belief = snd
        _disbelief = trd
        _apriori = np.random.uniform(size=size)

        return obsl((_belief, _disbelief, _uncertainty, _apriori))

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
    value_names = ['truth', 'confidence', 'apriori']

    @staticmethod
    def uniform(size):
        _confi = np.random.uniform(size=size)
        _truth = np.random.uniform(low=-_confi, high=_confi, size=size)
        _apriori = np.random.uniform(low=-1.0, high=1.0, size=size)

        return tbsl((_truth, _confi, _apriori))

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
    value_names = ['positive', 'negative', 'apriori']

    def reset(self, apriori=0.5):
        _positive = np.zeros(self.size)
        _negative = np.zeros(self.size)
        _apriori = np.ones(self.size) * apriori

        self.value = (_positive, _negative, _apriori)

    @staticmethod
    def uniform(size, _min=0, _max=1e2):
        _positive = np.random.randint(_min, _max, size=size)
        _negative = np.random.randint(_min, _max, size=size)
        _apriori = np.random.uniform(size=size)

        return ebsl((_positive, _negative, _apriori))

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
for vtype in types:
    for i, name in enumerate(vtype.value_names):
        def _fget(self, idx=i):
            return self.value[idx]

        def _fset(self, array, idx=i):
            assert isinstance(array, np.ndarray)
            assert len(self) == len(array)

            self.value = (tuple()
                + self.value[:idx]
                + (array,)
                + self.value[idx + 1:])

        _fget.__name__ = '_fget_{}'.format(name)
        _fset.__name__ = '_fset_{}'.format(name)
        setattr(vtype, name, property(_fget, _fset))
