import pylacode as pl
import numpy as np
import inspect
import random
import sys

test_types = pl.logic.types
test_ops = ['__invert__']

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

def _evaluate_op_with_vtype(op_name, vtype, values):
    op = getattr(vtype, op_name)
    _values = [vtype(value) for value in values]
    return op(*_values)

def _evaluate_op_forall(op_name, values):
    results = []
    for vtype in test_types:
        results.append(_evaluate_op_with_vtype(op_name, vtype, values))
    return results

def _check_op_forall(op_name, values):
    results = []
    for vtype in test_types:
        results += _evaluate_op_forall(op_name, [vtype(v) for v in values])

    for result in results:
        checks = [(result == other) for other in results]

        if not all([isinstance(c, bool) for c in checks]):
            raise AssertionError("op == doesn't return booleans")

        if not all(checks):
            raise AssertionError("results differ")

    return True

def _get_parameter_count(op):
    if sys.version_info < (3,):
        return len(inspect.getargspec(op).args)
    return len(inspect.signature(op).parameters)

def _check_op(op_name):
    vtypes = list(test_types)
    random.shuffle(vtypes)

    width = random.randint(2, 10)
    for vtype in vtypes:
        op = getattr(vtype, op_name)
        nargs = _get_parameter_count(op)
        args = [vtype.uniform(width) for _ in range(0, nargs)]
        assert _check_op_forall(op_name, args)

    return True
