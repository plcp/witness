# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
from __future__ import unicode_literals, division, with_statement

import sys
import pylacode as pl
assert sys.version_info >= (2, 7)

import pylacode.source
import random

# run tests
def run():

    # check the default source
    assert pl.source.default.name == 'default'
    assert pl.source.issource(pl.source.default)
    assert isinstance(pl.source.default, pl.source.default_source)

    # construct named sources
    x = pl.source.named_source(name='what', other_metadata='some')
    y = pl.source.named_source(name='whom', other_metadata='some', more='again')
    assert y.more == 'again'
    assert x.name == 'what' and y.name == 'whom'
    assert x.other_metadata == 'some' and y.other_metadata

    # test issource
    assert pl.source.issource(x) and pl.source.issource(y)
    assert not pl.source.issource(x.name) and not pl.source.issource(y.more)

    # check __str__
    assert str(x) == 'what(other_metadata=some)'
    assert str(y) == 'whom(more=again,other_metadata=some)'

    # check equality
    z = pl.source.named_source(name='what', other_metadata='some')
    assert x == z
    assert not (x == y or z == y)

    # construct merged sources
    a = pl.source.merge_source(op='concat', left=x, right=y)
    b = pl.source.merge_source(op='concat', right=x, left=x)

    # test property setter
    assert b.right == x
    b.right = y
    assert b.right == y

    # (retrieve some identical, but shuffled dicts)
    adict = a.dict()
    bdict = dict(random.sample(b.dict().items(), len(b.dict())))

    # construct pathological merged sources
    c = pl.source.merge_source(op=z, again=(b, a), nope=adict)
    e = pl.source.merge_source(op=x, again=(a, b), nope=bdict)

    # check repr & dict-ordering-sensitive determinism
    strab = (
        'merge<concat>(left=what(other_metadata=some),'
        + 'right=whom(more=again,other_metadata=some))')
    strec = (
        'merge<what(other_metadata=some)>(again=(merge'
        + '<concat>(left=what(other_metadata=some),rig'
        + 'ht=whom(more=again,other_metadata=some)),me'
        + 'rge<concat>(left=what(other_metadata=some),'
        + 'right=whom(more=again,other_metadata=some))'
        + '),nope={left:what(other_metadata=some),name'
        + ':merge,op:concat,right:whom(more=again,othe'
        + 'r_metadata=some)})')
    assert str(a) == repr(b) == strab
    assert repr(e) == str(c) == strec

    return True
