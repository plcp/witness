# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import sys

from witness.hell import handle_unicode, is_string

assert sys.version_info >= (2, 7)


def listify(target):
    if target is None:
        return []
    if isinstance(target, list):
        return target
    return [target]


def to_str(target, strlify_class=None.__class__):
    if is_string(target):
        return str(target)
    elif isinstance(target, dict):
        return ('{' + ','.join([
            str(k) + ':' + str(v)
            for k, v in (sorted(target.items(), key=lambda x: x[0]))
        ]) + '}')
    elif isinstance(target, tuple):
        return '(' + ','.join([str(t) for t in target]) + ')'
    elif issubclass(target.__class__, strlify_class):
        return str(target)
    elif sys.version_info < (3, ) and isinstance(target, unicode):
        return str(target)

    try:
        return target.__name__
    except AttributeError:
        return target.__class__.__name__
