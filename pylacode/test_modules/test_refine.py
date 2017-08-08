# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import sys
import warnings

import pylacode as pl
import pylacode.refine

assert sys.version_info >= (2, 7)


# run tests
def run():

    # test exception
    try:
        raise pl.refine.NoDataRefinedError
        assert False
    except pl.refine.NoDataRefinedError:
        assert True

    # construct a data refining backend
    class unvalue:
        v = 0

    x = unvalue()

    def xinc(state, parent):
        x.v += state + len(parent.mdata['some']) / 100.

    rd = pl.refine.data('paul', xinc, xinc, some='thing')
    assert rd.name == 'paul'
    assert rd.mdata['some'] == 'thing'
    assert rd._transform == rd._inverse == xinc

    # check calls
    assert x.v == 0.
    rd.transform(1)
    assert x.v == 1.05

    rd.mdata['some'] = 'not'
    rd.inverse(3)
    assert x.v == 4.08

    # check warning & repr
    re = pl.refine.data('more', None, None)
    with warnings.catch_warnings(record=True) as w:
        m = ('No inverse function provided while refining ' +
             'data with more backend ' +
             '(id: more{}).'.format(object.__repr__(re)))

        try:
            re.inverse(3)
            assert False
        except pl.refine.NoDataRefinedError:
            assert True
        assert str(w[0].message) == m

    # construct a label collection
    lc = pl.refine.label('again', 13)
    assert 'again' + object.__repr__(lc) == repr(lc)
    assert repr(lc.source) == 'label<again>()'
    assert lc.size == 13

    # add various labels to the collection
    lc.add(label='false', value=False)
    lc.add([dict(label='true', value=True)])

    return True
