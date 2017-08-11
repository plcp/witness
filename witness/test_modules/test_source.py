# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import random
import sys

import witness as wit
import witness.source

assert sys.version_info >= (2, 7)


# run tests
def run():

    # check the default source
    assert wit.source.default.name == 'default'
    assert wit.source.issource(wit.source.default)
    assert isinstance(wit.source.default, wit.source.default_source)

    # construct named sources
    x = wit.source.named_source(name='what', other_metadata='some')
    y = wit.source.named_source(
        name='whom', other_metadata='some', more='again')
    assert y.more == 'again'
    assert x.name == 'what' and y.name == 'whom'
    assert x.other_metadata == 'some' and y.other_metadata

    # test issource
    assert wit.source.issource(x) and wit.source.issource(y)
    assert not wit.source.issource(x.name) and not wit.source.issource(y.more)

    # check __str__
    assert str(x) == 'what(other_metadata=some)'
    assert str(y) == 'whom(more=again,other_metadata=some)'

    # check equality
    z = wit.source.named_source(name='what', other_metadata='some')
    assert x == z
    assert not (x == y or z == y)

    # construct merged sources
    a = wit.source.merge_source(op='concat', left=x, right=y)
    b = wit.source.merge_source(op='concat', right=x, left=x)

    # test property setter
    assert b.right == x
    b.right = y
    assert b.right == y

    # (retrieve some identical, but shuffled dicts)
    adict = a.dict()
    bdict = dict(random.sample(b.dict().items(), len(b.dict())))

    # construct pathological merged sources
    c = wit.source.merge_source(op=z, again=(b, a), nope=adict)
    e = wit.source.merge_source(op=x, again=(a, b), nope=bdict)

    # check repr & dict-ordering-sensitive determinism
    strab = ('merge<concat>(left=what(other_metadata=some),' +
             'right=whom(more=again,other_metadata=some))')
    strec = (
        'merge<what(other_metadata=some)>(again=(merge' +
        '<concat>(left=what(other_metadata=some),rig' +
        'ht=whom(more=again,other_metadata=some)),me' +
        'rge<concat>(left=what(other_metadata=some),' +
        'right=whom(more=again,other_metadata=some))' +
        '),nope={left:what(other_metadata=some),name' +
        ':merge,op:concat,right:whom(more=again,othe' + 'r_metadata=some)})')
    assert str(a) == repr(b) == strab
    assert repr(e) == str(c) == strec

    return True
