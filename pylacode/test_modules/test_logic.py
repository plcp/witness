# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
from __future__ import unicode_literals, division, with_statement

import sys
import pylacode as pl
assert sys.version_info >= (2, 7)

import numpy as np
import traceback
import warnings
import inspect
import random
import sys

test_types = pl.logic.types
test_ops = ['__invert__', 'probability', 'alpha', 'beta',
            'weight', '__iadd__', 'trust', '__imul__',
            '__idiv__', '__iand__', '__ior__']

# test near-equality with a relative/absolute tolerance
def _similar(a, b):
    return np.allclose(a, b,
        rtol=pl.logic.eq_rtol,
        atol=pl.logic.eq_atol,
        equal_nan=pl.logic.eq_nan)

# run tests
def run():
    # test basic constructor
    for vtype in test_types:
        vtype(size=5)

    # test from-instance constructor
    for vtype in test_types:
        x = vtype(size=3)
        y = vtype(x)

        assert x.value is not y.value
        for vx, vy in zip(x.value, y.value):
            assert _similar(vx, vy)
            assert vx is not vy

    # test by-name getters and setters of internal value
    for vtype in test_types:
        x = vtype(size=7)
        for i, name in enumerate(vtype.value_names):
            assert getattr(x, name) is x.value[i]

            n = np.ones(7)
            setattr(x, name, n)
            assert n is x.value[i]

    # test by-tuple constructor
    for vtype in test_types:
        n = [np.ones(4) for _ in range(0, len(vtype.value_names))]
        x = vtype(tuple(n))
        for a, b in zip(x.value, n):
            assert a is b

    # test by-value constructor
    for vtype in test_types:
        n = [np.random.rand() for _ in range(0, len(vtype.value_names))]
        x = vtype(tuple(n))
        for a, b in zip(x.value, n):
            assert len(a) == 1
            assert a[0] == b

    # test back-forth cast consistency (« AtoB(BtoA(b)) == b »)
    for stype in test_types:
        x = stype.uniform(6)
        for dtype in test_types:
            n = x.cast_to(dtype)
            v = n.cast_to(stype)
            assert isinstance(v, stype) and isinstance(n, dtype)
            assert (x == v) and (x.equals(n))

    # test double-invert consistency
    for vtype in test_types:
        x = vtype.uniform(3)
        assert (x == (~x).invert()) and (~x == ~(~x).invert())

    # test if « p(A) + p(!A) == 1 »
    for vtype in test_types:
        x = vtype.uniform(11)
        y = ~x
        assert _similar(x.p() + y.p(), np.ones_like(x.p()))

    # test if trust factor is linear uppon consensus
    for vtype in test_types:
        x = vtype.uniform(47)
        y = vtype.uniform(47)
        assert _similar(x.trust + y.trust, (x + y).trust)

    # test numerically unstable assertions
    _success = False
    failures = []
    for j in range(0, 24):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')

            try:
                _unstable_tests()
                _success = True
            except AssertionError as e:
                e.exc_info = sys.exc_info()
                failures.append(e)

                _warns = []
                for i in range(0, len(w)):
                    _wi = None
                    if sys.version_info < (3,):
                        _wi = w[i].message
                    else:
                        _wi = str(w[i])

                    if pl.error._stable_warntext in _wi:
                        _warns.append(w[i])

                if len(_warns) < 1:
                    raise AssertionError('No warning raised when '
                        + 'assertion failed: {}, {} '.format(str(w), e))
        if _success:
            break

    # raise an AssertionError if we fail to converge
    if not _success:
        for e in failures:
            traceback.print_exception(*e.exc_info)
        raise AssertionError('Numerically unstable operations failed '
            + '{} times in a row'.format(j + 1))

    # test operators equivalence between representations
    for op in test_ops:
        assert _check_op(op)

    return True

def _unstable_tests():
    # test distributivity of discounting upon consensus
    for vtype in test_types:
        x, y, z = [vtype.uniform(601) for _ in range(0, 3)]
        assert (x * z) + (y * z) == (x + y) * z

    # test if scalar product « by n » == « x + x + … + x » (n times)
    for vtype in test_types:
        x = vtype.uniform(541)
        assert 2 * x == x + x
        assert x * 3 == x + x + x
        assert 2 * x * 2 == x + x + x + x

    # test various calculus upon product
    for vtype in test_types:
        x, y, z = [vtype.uniform(463) for _ in range(0, 3)]
        assert x / 2 == (x * 2) / 4
        assert (x * y) / y == x
        assert (((x * 2) / y) / 2) * y == x
        assert (x * y * z * z) / (y * z) == x * z
        assert _similar(x.trust * 2, (x * 2).trust)
        assert _similar(x.trust ** 3, (x * x * x).trust)
        assert _similar(x.trust * y.trust, (x * y).trust)
        assert _similar((x.trust + y.trust) * z.trust,
            (x * z + y * z).trust)

def _get_op_from_name(vtype, op_name):
    op = getattr(vtype, op_name)
    if isinstance(op, property):
        return op.fget
    return op

def _evaluate_op_with_vtype(op_name, vtype, values):
    op = _get_op_from_name(vtype, op_name)
    _values = [vtype(value) for value in values]
    return op(*_values), (op_name, vtype, values)

def _evaluate_op_forall(op_name, values):
    results = []
    reports = []
    for vtype in test_types:
        result, report = _evaluate_op_with_vtype(op_name, vtype, values)
        results.append(result)
        reports.append(report)
    return results, reports

def _check_op_forall(op_name, values):
    results = []
    reports = []
    for vtype in test_types:
        resu, repo = _evaluate_op_forall(op_name, [vtype(v) for v in values])
        results += resu
        reports += repo

    for j, result in enumerate(results):
        if isinstance(result, np.ndarray):
            checks = [_similar(result, other) for other in results]
        else:
            checks = [(result == other) for other in results]

        if isinstance(checks[0], np.ndarray):
            checks = [c.all() for c in checks]

        for i, c in enumerate(checks):
            error = None
            if not isinstance(c, (bool, np.bool_)):
                error = "Equality '==' doesn't return a proper boolean !"
            elif not c:
                error = 'Incoherent results !'

            if error is not None:
                expected = (_evaluate_op_with_vtype(*reports[j]), reports[j])
                obtained = (_evaluate_op_with_vtype(*reports[i]), reports[i])

                try:
                    obt = obtained[0][0]
                    exp = expected[0][0]
                    if exp.__class__ in test_types:
                        obt = obt.cast_to(exp.__class__).value
                        exp = exp.value

                        differ = [abs(o - e) for o, e in zip(obt, exp)]
                        rerror = [pl.logic.eq_atol + pl.logic.eq_rtol
                                    * abs(e) for e in exp]
                    else:
                        differ = abs(obt - exp)
                        rerror = pl.logic.eq_atol + pl.logic.eq_rtol * abs(exp)

                except BaseException as e:
                    differ = 'Unavailable: {}'.format(e)
                    rerror = 'Unavailable: <see above exception>'

                raise AssertionError(error +
                    '\n\n >> Here is the failing test case:' +
                    '\n\t{}'.format(str(obtained)) +
                    '\n\n >> Here is the expected result:' +
                    '\n\t{}'.format(str(expected)) +
                    '\n\n >> Here is the error vs tolerance:' +
                    '\n\t{}'.format(differ) +
                    '\n\t{}'.format(rerror) +
                    '\n')
    return True

def _get_parameter_count(op):
    if sys.version_info < (3,):
        spec = inspect.getargspec(op)
        _len = len(spec.args)
        if spec.defaults is not None:
            _len -= len(spec.defaults)
        return _len

    spec = inspect.signature(op).parameters
    args = [p for p in spec if spec[p].default is inspect._empty]
    args = [p for p in args if spec[p].kind not in {2, 4}]
    return len(args)

def _check_op(op_name):
    vtypes = list(test_types)
    random.shuffle(vtypes)

    width = random.randint(2, 10)
    for vtype in vtypes:
        op = _get_op_from_name(vtype, op_name)
        nargs = _get_parameter_count(op)
        args = [vtype.uniform(width) for _ in range(0, nargs)]
        assert _check_op_forall(op_name, args)

    return True
