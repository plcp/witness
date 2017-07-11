import pylacode as pl
import numpy as np
import inspect
import random
import sys

test_types = pl.logic.types
test_ops = ['__invert__']

def _similar(a, b):
    return np.allclose(a, b,
        rtol=pl.logic.eq_rtol,
        atol=pl.logic.eq_atol,
        equal_nan=pl.logic.eq_nan)

def run():
    for vtype in test_types:
        vtype(size=5)

    for vtype in test_types:
        x = vtype(size=3)
        y = vtype(x)

        assert x.value is not y.value
        for vx, vy in zip(x.value, y.value):
            assert vx is not vy

    for vtype in test_types:
        x = vtype(size=7)
        for i, name in enumerate(vtype.value_names):
            assert getattr(x, name) is x.value[i]

            n = np.ones(7)
            setattr(x, name, n)
            assert n is x.value[i]

    for vtype in test_types:
        n = [np.ones(4) for _ in range(0, len(vtype.value_names))]
        x = vtype(tuple(n))
        for a, b in zip(x.value, n):
            assert a is b

    for stype in test_types:
        x = stype.uniform(6)
        for dtype in test_types:
            n = x.cast_to(dtype)
            v = n.cast_to(stype)
            assert isinstance(v, stype) and isinstance(n, dtype)
            assert (x == v) and (x.equals(n))

    for vtype in test_types:
        x = vtype.uniform(3)
        assert (x == (~x).invert()) and (~x == ~(~x).invert())

    for op in test_ops:
        assert _check_op(op)

    return True

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
                    differ = abs(obtained[0][0] - expected[0][0])
                    rerror = (pl.logic.eq_atol
                        + pl.logic.eq_rtol * abs(expected[0][0]))
                except BaseException:
                    differ = 'Unavailable'

                raise AssertionError(error +
                    '\n\n >> Here is the failing test case:' +
                    '\n\t{}'.format(obtained) +
                    '\n\n >> Here is the expected result:' +
                    '\n\t{}'.format(expected) +
                    '\n\n >> Here is the error vs tolerance:' +
                    '\n\t{}'.format(differ) +
                    '\n\t{}'.format(rerror) +
                    '\n')
    return True

def _get_parameter_count(op):
    if sys.version_info < (3,):
        spec = inspect.getargspec(op)
        return len(spec.args) - len(spec.defaults)

    spec = inspect.signature(op).parameters
    args = [p for p in spec if spec[p].default is inspect._empty]
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
