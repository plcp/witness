import pylacode as pl
import numpy as np

test_types = pl.logic.types
test_ops = []

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
