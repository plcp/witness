# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import sys
import traceback
import warnings

import numpy as np
import pylacode as pl

assert sys.version_info >= (2, 7)

# Stable Residual (used when numeric instability can't be avoided)
_stable_residual = 1e-12

# Warnings text
_stable_warntext = ('Numerically unstable calculus suppressed ' +
                    '(obtained values may not be meaningful).')
_unrecov_failure = (
    'Unrecoverable failure during numerical instability ' + 'handling ' +
    '(likely to be caused by NaN values, see `pylacode.error.state`).')

last_warning = None


class _state:
    inverse_suppress = True
    inverse_inf = True
    inverse_nan = True
    quiet = False


state = _state()


def warn(text):
    global last_warning
    last_warning = text
    warnings.warn(text, RuntimeWarning, 2)


def _try_inverse_details(vector):
    _vector = None
    if issubclass(vector.dtype.type, np.float):
        _vector = vector.copy()
    else:
        _vector = vector.astype(np.float64)

    if state.inverse_nan:
        _nans = np.isnan(_vector)
        _vector[_nans] = _stable_residual

    _invalids = (np.abs(_vector) < _stable_residual)
    if any(_invalids):
        _vector[_invalids] = _stable_residual

    result = 1.0 / _vector
    if state.inverse_nan:
        result[_nans] = vector[_nans]

    if state.inverse_inf:
        result[_invalids] = (np.sign(_vector[_invalids]) * float('inf'))
    return result


def try_inverse(vector):
    assert isinstance(vector, np.ndarray)
    global last_warning, state
    last_warning = None

    try:
        with np.errstate(divide='raise', invalid='raise'):
            return 1.0 / vector
    except FloatingPointError as e:
        if not state.inverse_suppress:
            raise e
        elif not state.quiet:
            warn(_stable_warntext)

        try:
            with np.errstate(divide='raise', invalid='raise'):
                return _try_inverse_details(vector)
        except FloatingPointError as f:
            if not state.quiet:
                traceback.print_exc()
                warn(_unrecov_failure)

        raise e  # Unable to recover from/suppress numerical instability
    assert False  # Unreachable
