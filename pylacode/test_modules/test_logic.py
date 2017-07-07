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

    for op in test_ops:
        assert _check_op(op)

    return True
