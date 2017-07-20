# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
from __future__ import unicode_literals, division, with_statement

import sys
import pylacode as pl
assert sys.version_info >= (2, 7)

import time
import hashlib
import binascii
import warnings

_local_occuring_uid = 0

uuid_magic = '49e'
uuid_session = pl.logic.np.random.rand().hex()[4:10]
def create_uuid(source):
    global _local_occuring_uid

    src = None
    if sys.version_info < (3,):
        src = source.decode('utf8')
    else:
        src = bytes(source, 'utf8')

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

default_source = 'default_source' # no source provided
class fe:
    def __init__(self, value=None, size=None, source=default_source, **mdata):
        global _local_occuring_uid
        self.source = source

        if value is None:
            assert size is not None # if value is None, then size must be given
            self.value = pl.logic.obsl(size=size)
        else:
            self.value = value
            if size is not None:
                warnings.warn('Size given but ignored')

        self.uuid = create_uuid(source)
        self.meta = dict(**mdata)
        self.uid = _local_occuring_uid
