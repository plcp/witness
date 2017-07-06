import pylacode as pl

test_types = pl.logic.types
test_ops = []

def run():
    for vtype in test_types:
        vtype(size=5)

    return True
