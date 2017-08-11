# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import sys
import warnings

import numpy as np
import witness as wit
import witness.logic
import witness.table
import witness.error
import witness.fuzzy
import witness.refine

assert sys.version_info >= (2, 7)

# test near-equality with a relative/absolute tolerance
def _eq(a, b):
    return np.allclose(
        a,
        b,
        rtol=wit.logic.eq_rtol,
        atol=wit.logic.eq_atol,
        equal_nan=wit.logic.eq_nan)

# run tests
def run():

    # first, create a label refining backend
    labels = wit.refine.label('main', 5)
    labels.add([
        dict(label='first'),
        dict(label='second'),
        dict(label='third'),
        dict(label='fourth'),
        dict(label='fifth'),
        dict(label='even', where=slice(1, None, 2)),
        dict(label='odd', where=slice(0, None, 2)),
        dict(label='even_only', value=[False, True, False, True, False]),
        dict(label='odd_only', value=[True, False, True, False, True]),
        dict(label='!prime', value=[True, False, False, True, False]),
    ])

    # then, create a translation table using our label refining label backend
    table = wit.table.translation(labels)

    # translate semantic textual labels in abstract representation
    assert _eq(table.digest('first')[0].value.trust, [2, 0, 0, 0, 0])
    assert _eq(table.digest('second')[0].value.trust, [0, 2, 0, 0, 0])
    assert _eq(table.digest('third')[0].value.trust, [0, 0, 2, 0, 0])
    assert _eq(table.digest('fourth')[0].value.trust, [0, 0, 0, 2, 0])
    assert _eq(table.digest('fifth')[0].value.trust, [0, 0, 0, 0, 2])
    assert _eq(table.digest('even')[0].value.trust, [0, 2, 0, 2, 0])
    assert _eq(table.digest('odd')[0].value.trust, [2, 0, 2, 0, 2])
    assert _eq(table.digest('even_only')[0].value.trust, [-1, 2, -1, 2, -1])
    assert _eq(table.digest('odd_only')[0].value.trust, [2, -1, 2, -1, 2])
    assert _eq(table.digest('prime')[0].value.trust, [-1, 2, 2, -1, 2])
    assert _eq(table.digest('!prime')[0].value.trust, [2, -1, -1, 2, -1])
    assert _eq(table.digest('!!prime')[0].value.trust, [-1, 2, 2, -1, 2])

    results = table.digest(['first', 'third', 'fifth'])
    assert _eq(results[2].value.trust, [2, 0, 0, 0, 0])
    assert _eq(results[1].value.trust, [0, 0, 2, 0, 0])
    assert _eq(results[0].value.trust, [0, 0, 0, 0, 2])

    wit.error.state.quiet = True
    v = wit.fuzzy.squash(results)
    assert _eq(v.value.trust, [2, 0, 2, 0, 2])

    inversed = table.digest(v, inverse=True)
    assert 'first' in inversed
    assert 'third' in inversed
    assert 'fifth' in inversed
    assert 'odd' in inversed
    assert len(inversed) == 4

    v = wit.fuzzy.squash(v, table.digest('even_only'))
    inversed = table.digest(v, inverse=True)
    assert 'second' in inversed
    assert 'fourth' in inversed
    assert 'even' in inversed
    assert len(inversed) == 3

    return True
