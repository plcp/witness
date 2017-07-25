# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
from __future__ import unicode_literals, division, with_statement

import sys
import pylacode as pl
assert sys.version_info >= (2, 7)

import pylacode.source
import binascii
import warnings
import operator
import hashlib
import time

_local_occuring_uid = 0

uuid_magic = '49e'
uuid_session = pl.logic.np.random.rand().hex()[4:10]
def create_uuid(source):
    global _local_occuring_uid

    src = None
    if sys.version_info < (3,):
        src = str(source).decode('utf8')
    else:
        src = bytes(str(source), 'utf8')

    s = uuid_magic
    s += '-%x%x%02x' % pl.api_version
    s += '-' + uuid_session
    s += '-{}'.format(hashlib.sha224(src).hexdigest()[-6:])
    s += '-%08x' % int(time.time())
    s += '-%08x' % _local_occuring_uid
    s += '-' + pl.logic.np.random.rand().hex()[4:10]

    src = None
    if sys.version_info < (3,):
        src = s.decode('utf8')
    else:
        src = bytes(s, 'utf8')

    s += '%08x' % (binascii.crc32(src) & 0xffffffff)
    _local_occuring_uid += 1
    return s

class evidence:
    def __init__(self,
        value=None,
        size=None,
        source=None,
        merge_operator=operator.add,
        **mdata):

        if source is None:
            source = pl.source.default
        assert issubclass(source.__class__, pl.source._base_source)

        if value is None:
            assert size is not None # if value is None, then size must be given
            self.value = pl.logic.tbsl(size=size)
        else:
            self.value = value
            if size is not None:
                warnings.warn('Size given but ignored')

        global _local_occuring_uid
        self.merge_operator = merge_operator
        self.source = source
        self.mdata = dict(**mdata)
        self.uuid = create_uuid(source)
        self.uid = _local_occuring_uid

    def __lshift__(self, other):
        assert isinstance(other, evidence)
        assert len(self.value) == len(other.value)

        value = self.merge_operator(self.value, other.value)
        source = None
        if self.source == other.source:
            source = self.source
        else:
            source = pl.source.merge_source(
                op=self.merge_operator,
                left=self.source,
                right=other.source)

        return evidence(
            value=value,
            source=source,
            merge_operator=self.merge_operator,
            **self.mdata)
