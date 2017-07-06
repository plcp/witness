import pylacode as pl

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

    return True
