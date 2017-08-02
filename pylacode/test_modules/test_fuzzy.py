# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import binascii
import hashlib
import operator
import random
import sys
import time

import pylacode as pl
import pylacode.fuzzy
import pylacode.logic
import pylacode.source

assert sys.version_info >= (2, 7)


# run tests
def run():

    # save the « local uid »
    local_uid = int(pl.fuzzy._local_occuring_uid)

    # check the consistency of each uuid field (see below)
    fake_source = pl.source.named_source(random.uniform(0, 1).hex())
    uuid_tcheck = pl.fuzzy.create_uuid(fake_source)

    # check if the « local uid » was increased
    assert local_uid + 1 == pl.fuzzy._local_occuring_uid

    # check if the uuid's first field is magic
    assert uuid_tcheck.startswith(pl.fuzzy.uuid_magic)
    uuid_ncheck = uuid_tcheck[len(pl.fuzzy.uuid_magic) + 1:]

    # check if the uuid's second field is the correct api version
    assert uuid_ncheck.startswith('%x%x%02x' % pl.api_version)
    uuid_ncheck = uuid_ncheck[5:]

    # check if the uuid's third field is equal to the « session » token
    assert uuid_ncheck.startswith(pl.fuzzy.uuid_session)
    uuid_ncheck = uuid_ncheck[len(pl.fuzzy.uuid_session) + 1:]

    # check if the uuid's fourth field is equal to current « local uid »
    assert int(uuid_ncheck[:8], 16) == local_uid
    uuid_ncheck = uuid_ncheck[9:]

    # check if the uuid's fifth field is equal to hashed source
    h = fake_source.name + '()'
    if sys.version_info < (3, ):
        h = hashlib.sha224(h).hexdigest()[-6:]
    else:
        h = hashlib.sha224(bytes(h, 'utf8')).hexdigest()[-6:]

    assert uuid_ncheck.startswith(h)
    uuid_ncheck = uuid_ncheck[len(h) + 1:]

    # check if the uuid's penultimate field is near the current timestamp
    stamp = int(uuid_ncheck[:8], 16)
    assert abs(stamp - time.time()) < 1
    uuid_ncheck = uuid_ncheck[9:]

    # check if the uuid's ultimate field is finished by a correct crc32
    crc = uuid_tcheck[:-8]
    if sys.version_info < (3, ):
        crc = (binascii.crc32(crc) & 0xffffffff)
    else:
        crc = (binascii.crc32(bytes(crc, 'utf8')) & 0xffffffff)
    assert int(uuid_ncheck[6:], 16) == crc

    # test by-size evidence constructor & metadata storage
    e = pl.fuzzy.evidence(size=37, some_meta='data')
    assert isinstance(e.value, pl.logic.tbsl)
    assert pl.logic.obsl(size=37) == e.value
    assert e.mdata['some_meta'] == 'data'

    # test by-value evidence constructor
    x = pl.fuzzy.evidence(value=pl.logic.ebsl.uniform(37))
    y = pl.fuzzy.evidence(value=pl.logic.obsl.uniform(37))
    assert x.size == y.size == e.size == len(x.value + y.value + e.value)

    # test value type coherence
    assert x.value.__class__ == y.value.__class__ == e.value.__class__

    # test if the (u)uids are ordered
    assert y.uid == x.uid + 1 == e.uid + 2 == local_uid + 4
    assert y.uid > x.uid > e.uid > local_uid
    assert y.uuid > x.uuid > e.uuid

    # test source conservation while uniform merge
    assert (x << y).source == x.source == y.source

    # test source mixing while merging
    x.source = fake_source
    assert str(
        (x << y).source) == 'merge<add>(left={}(),right=default())'.format(
            fake_source.name)

    # test source mixing with another operator
    y.merge_operator = operator.mul
    assert str(
        (y << x).source) == 'merge<mul>(left=default(),right={}())'.format(
            fake_source.name)

    # test results obtained while merging
    assert (x << y).value == (x.value + y.value)
    assert (y << x).value == (y.value * x.value)

    return True
