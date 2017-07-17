# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
from __future__ import unicode_literals, division, with_statement

import sys
import pylacode as pl
assert sys.version_info >= (2, 7)

import warnings
import numpy as np

# Non-informative prior weight
ebsl_prior = 2 # (ensure uniform Beta-distribution when « apriori == 0.5 »)

# Minimal uncertainty considered during discounting
min_uncertainty = 1.0 / 33. # defaulted at 33:1 to fix « inert_weight(2) == 64 »

# Belief required for full-trust during discounting
trust_threshold = 1.0 / 2.0 # defaulted at 2:1 for positive against negative

# Operator __eq__ constants
eq_rtol = 1e-5 # relative tolerance
eq_atol = 1e-8 # absolute tolerance
eq_nan = False # is NaN equal to NaN ?

class _base(object):
    '''Base class for logic types

    '''
    aliases = (
        ('__eq__', 'equals'),
        ('__invert__', 'invert'),
        ('probability', 'p'),
        ('__iadd__', 'merge_with'),
    )

    def __init__(self, other=None, size=None):
        if isinstance(other, tuple):
            if not len(other) == len(self.value_names):
                raise AssertionError(
                    'Expected a tuple of lenght {}'.format(
                    len(self.value_names)))

            s = None
            if isinstance(other[0], (float, int)):
                s = 1
            else:
                s = len(other[0])

            new_values = []
            for v in other:
                if isinstance(v, (float, int)):
                    v = np.array([float(v),])

                if not isinstance(v, np.ndarray):
                    raise AssertionError(
                        'Expecting numpy.ndarray: {} in {}'.format(
                        v, other))

                if not s == len(v):
                    raise AssertionError(
                        'Expecting uniform lenght: {}'.format(other))

                new_values.append(v)

            if size is not None:
                warnings.warn('Size given but ignored')

            self.size = s
            self.value = tuple(new_values)
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

    def __str__(self, crop_to=None):
        if crop_to is None:
            crop_to = len(self)

        values = []
        for a in self.value:
            s = ['{:0.4}'.format(float(v)) for v in a[:crop_to]]
            if len(s) != len(a):
                s.append('...')
            values.append('[' + ', '.join(s) + ']')
        s = '{}'.format(self.__class__.__name__)
        return s + '(' + ', '.join(values) + ', size={})'.format(len(self))

    def __repr__(self):
        return '{}@{}'.format(self.__str__(crop_to=1), hex(id(self)))

    def reset(self):
        raise NotImplementedError

    @staticmethod
    def uniform(size, _min=0, _max=None, prior=ebsl_prior, mu=min_uncertainty):
        raise NotImplementedError

    @staticmethod
    def inert_weight(prior=ebsl_prior, min_u=min_uncertainty):
        return prior * (1 - min_uncertainty) / min_uncertainty

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

    def __eq__(self, other, rtol=eq_rtol, atol=eq_atol, equal_nan=eq_nan):
        assert other.__class__ in types

        if not isinstance(other, self.__class__):
            other = other.cast_to(self.__class__)

        return all([
                np.allclose(a, b, rtol, atol, equal_nan)
                for a, b in zip(self.value, other.value)])

    def __invert__(self):
        raise NotImplementedError

    @property
    def probability(self):
        raise NotImplementedError

    def alpha(self, prior=ebsl_prior):
        return self.cast_to(ebsl, prior=prior).alpha(prior=prior)

    def beta(self, prior=ebsl_prior):
        return self.cast_to(ebsl, prior=prior).beta(prior=prior)

    @property
    def weight(self, prior=ebsl_prior):
        raise NotImplementedError

    def w(self, prior=ebsl_prior):
        return self.__class__.weight.fget(self, prior)

    def __iadd__(self, other, prior=ebsl_prior):
        raise NotImplementedError

    def __add__(self, other, prior=ebsl_prior):
        return self.copy().__iadd__(other, prior)

    @property
    def trust(self, prior=ebsl_prior, mu=min_uncertainty, tt=trust_threshold):
        raise NotImplementedError

    def t(self, prior=ebsl_prior, mu=min_uncertainty, tt=trust_threshold):
        return self.__class__.trust.fget(self, prior, mu, tt)

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
    def uniform(size, _min=0, _max=None, prior=ebsl_prior, mu=min_uncertainty):
        if _max is None:
            _max = 1.0 - mu
        low, high = (1. - _max, 1. - _min)

        _uncertainty = np.random.uniform(low=low, high=high, size=size)
        snd = np.random.uniform(high=(1.0 - _uncertainty), size=size)
        trd = 1.0 - snd - _uncertainty

        snd, trd = np.random.permutation((snd, trd))

        _belief = snd
        _disbelief = trd
        _apriori = np.random.uniform(size=size)

        return obsl((_belief, _disbelief, _uncertainty, _apriori))

    def cast_to(self, other, prior=ebsl_prior):
        n = _base.cast_to(self, other)
        if isinstance(n, obsl):
            pass
        elif isinstance(n, tbsl):
            _truth = self.belief - self.disbelief
            _confidence = 1.0 - self.uncertainty
            _apriori = 2 * self.apriori - 1.0

            n.value = (_truth, _confidence, _apriori)
        elif isinstance(n, ebsl):
            _positive = self.w(prior) * self.belief
            _negative = self.w(prior) * self.disbelief

            n.value = (_positive, _negative, self.apriori)
        return n

    def __invert__(self):
        return obsl(
            (self.disbelief, self.belief,
            self.uncertainty, 1.0 - self.apriori))

    @property
    def probability(self):
        return self.belief + self.apriori * self.uncertainty

    @property
    def weight(self, prior=ebsl_prior):
        return prior / self.uncertainty

    def __iadd__(self, other, prior=ebsl_prior):
        assert other.__class__ in types
        if not isinstance(other, self.__class__):
            other = other.cast_to(self.__class__)

        norm = 1.0 / (self.uncertainty + other.uncertainty
                - self.uncertainty * other.uncertainty)

        _belief = (self.belief * other.uncertainty
                + other.belief * self.uncertainty) * norm
        _disbelief = (self.disbelief * other.uncertainty
                + other.disbelief * self.uncertainty) * norm
        _uncertainty = 1 - _belief - _disbelief

        s_weight = self.w(prior) - prior
        o_weight = other.w(prior) - prior

        if (s_weight == 0).all() and (s_weight == o_weight).all():
            _apriori = (self.apriori + other.apriori) / 2.
            return obsl((_belief, _disbelief, _uncertainty, _apriori))

        _apriori = (self.apriori * s_weight + other.apriori * o_weight)
        _apriori /= s_weight + o_weight
        return obsl((_belief, _disbelief, _uncertainty, _apriori))

    @property
    def trust(self, prior=ebsl_prior, mu=min_uncertainty, tt=trust_threshold):
        iw = self.inert_weight(prior, mu)

        scale = tt * mu
        scale = (scale - tt) / (scale - mu)
        scale = iw / scale

        brate = (self.belief * scale - self.disbelief) * self.w(prior)
        arate = (self.apriori - 1. / 2.) * (self.w(prior) - prior)

        result = (brate + arate) / iw
        return result

class tbsl(_base):
    '''Three-Value-Based Subjective Logic

    '''
    value_names = ['truth', 'confidence', 'apriori']

    @staticmethod
    def uniform(size, _min=0, _max=None, prior=ebsl_prior, mu=min_uncertainty):
        if _max is None:
            _max = 1.0 - mu

        _confi = np.random.uniform(low=_min, high=_max, size=size)
        _truth = np.random.uniform(low=-_confi, high=_confi, size=size)
        _apriori = np.random.uniform(low=-1.0, high=1.0, size=size)

        return tbsl((_truth, _confi, _apriori))

    def reset(self, apriori=0.0):
        _truth = np.zeros(self.size)
        _confidence = np.zeros(self.size)
        _apriori = np.ones(self.size) * apriori

        self.value = (_truth, _confidence, _apriori)

    def cast_to(self, other, prior=ebsl_prior):
        n = _base.cast_to(self, other)
        if isinstance(n, tbsl):
            pass
        elif isinstance(n, ebsl):
            _positive = (1.0 + self.truth) * self.w(prior)
            _negative = (1.0 - self.truth) * self.w(prior)
            _apriori = 1.0 + self.apriori

            half = 1.0 / 2.0
            _apriori *= half
            _positive = (_positive - prior) * half
            _negative = (_negative - prior) * half

            n.value = (_positive, _negative, _apriori)
        elif isinstance(n, obsl):
            _belief = self.confidence + self.truth
            _disbelief = self.confidence - self.truth
            _uncertainty = 1.0 - self.confidence
            _apriori = 1.0 + self.apriori

            half = 1.0 / 2.0
            _belief *= half
            _apriori *= half
            _disbelief *= half

            n.value = (_belief, _disbelief, _uncertainty, _apriori)
        return n

    def __invert__(self):
        return tbsl((-self.truth, self.confidence, -self.apriori))

    @property
    def probability(self):
        return (1.0 + self.truth + self.apriori
            - self.apriori * self.confidence) / 2.0

    @property
    def weight(self, prior=ebsl_prior):
        return prior / (1.0 - self.confidence)

    def __iadd__(self, other, prior=ebsl_prior):
        n = self.cast_to(ebsl)
        n += other
        return n.cast_to(tbsl)

    @property
    def trust(self, prior=ebsl_prior, mu=min_uncertainty, tt=trust_threshold):
        iw = self.inert_weight(prior, mu)

        scale = tt * mu
        scale = (scale - tt) / (scale - mu)
        scale = iw / scale

        brate = ((1. + self.truth) * scale + self.truth - 1.) * self.w(prior)
        arate = self.apriori * (self.w(prior) - prior) / 2.

        brate -= prior * (scale - 1.)
        brate /= 2.0

        result = (brate + arate) / iw
        return result

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
    def uniform(size, _min=0, _max=None, prior=ebsl_prior, mu=min_uncertainty):
        if _max is None:
            _max = _base.inert_weight(prior, mu) / 2.0

        _positive = np.random.randint(_min, _max, size=size)
        _negative = np.random.randint(_min, _max, size=size)
        _apriori = np.random.uniform(size=size)

        return ebsl((_positive, _negative, _apriori))

    def cast_to(self, other, prior=ebsl_prior):
        n = _base.cast_to(self, other)
        if isinstance(n, ebsl):
            pass
        if isinstance(n, tbsl):
            norm = 1.0 / self.w(prior)
            _truth = (self.positive - self.negative) * norm
            _confidence = 1.0 - prior * norm
            _apriori = 2 * self.apriori - 1

            n.value = (_truth, _confidence, _apriori)
        elif isinstance(n, obsl):
            norm = 1.0 / self.w(prior)
            _belief = self.positive * norm
            _disbelief = self.negative * norm
            _uncertainty = prior * norm

            n.value = (_belief, _disbelief, _uncertainty, self.apriori)
        return n

    def __invert__(self):
        return ebsl((self.negative, self.positive, 1.0 - self.apriori))

    @property
    def probability(self, prior=ebsl_prior):
        return (self.positive + self.apriori * prior
            ) / (self.positive + self.negative + prior)

    def alpha(self, prior=ebsl_prior):
        return self.positive + prior * self.apriori

    def beta(self, prior=ebsl_prior):
        return self.negative + prior * (1.0 - self.apriori)

    @property
    def weight(self, prior=ebsl_prior):
        return self.negative + self.positive + prior

    def __iadd__(self, other, prior=ebsl_prior):
        assert other.__class__ in types
        if not isinstance(other, self.__class__):
            other = other.cast_to(self.__class__)

        _positive = self.positive + other.positive
        _negative = self.negative + other.negative

        s_weight = self.w(prior) - prior
        o_weight = other.w(prior) - prior

        if (s_weight == 0).all() and (s_weight == o_weight).all():
            _apriori = (self.apriori + other.apriori) / 2.
            return ebsl((_positive, _negative, _apriori))

        _apriori = (self.apriori * s_weight + other.apriori * o_weight)
        _apriori /= s_weight + o_weight
        return ebsl((_positive, _negative, _apriori))

    @property
    def trust(self, prior=ebsl_prior, mu=min_uncertainty, tt=trust_threshold):
        iw = self.inert_weight(prior, mu)

        scale = tt * mu
        scale = (scale - tt) / (scale - mu)
        scale = iw / scale

        brate = self.positive * scale - self.negative
        arate = (self.apriori - 1. / 2.) * (self.w(prior) - prior)

        result = (brate + arate) / iw
        return result

types = [obsl, tbsl, ebsl]
for vtype in types:
    for dtype in types:
        def _fcast(self, target=dtype):
            return self.cast_to(target)

        if sys.version_info < (3,):
            _fcast.__name__ = str('_cast_to_{}'.format(dtype.__name__))
        else:
            _fcast.__name__ = '_cast_to_{}'.format(dtype.__name__)
        setattr(vtype, dtype.__name__, property(_fcast))

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

        if sys.version_info < (3,):
            _fget.__name__ = str('_fget_{}'.format(name))
            _fset.__name__ = str('_fset_{}'.format(name))
        else:
            _fget.__name__ = '_fget_{}'.format(name)
            _fset.__name__ = '_fset_{}'.format(name)
        setattr(vtype, name, property(_fget, _fset))

for name, alias in _base.aliases:
    for vtype in types:
        op = getattr(vtype, name)
        setattr(vtype, alias, op)
