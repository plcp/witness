# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
from __future__ import unicode_literals, division, with_statement

import sys
import pylacode as pl
assert sys.version_info >= (2, 7)

import collections

def _to_string(target):
    if isinstance(target, str):
        return target
    elif isinstance(target, dict):
        return ('{'
            + ','.join([str(k)+':'+str(v) for k, v in (
                    sorted(target.items(), key=lambda x: x[0]))
            ]) + '}')
    elif isinstance(target, tuple):
        return '(' + ','.join([str(t) for t in target]) + ')'
    elif issubclass(target.__class__, _base_source):
        return str(target)
    elif sys.version_info < (3,) and isinstance(target, unicode):
        return str(target)

    try:
        return target.__name__
    except AttributeError:
        return target.__class__.__name__

class _base_source:
    name = '_base'
    prop = 'genericity'

    def __init__(self, **mdata):
        _dict = dict(**mdata)
        self._attributes = collections.OrderedDict(
            sorted(_dict.items(), key=lambda x: x[0]))
        if self.prop is not None and self.prop in mdata:
            self._genericity = mdata[self.prop]
            del self._attributes[self.prop]
        else:
            self._genericity = None

        if self.prop is not None:
            def _fget(self):
                return self._genericity
            def _fset(self, value):
                self._genericity = value
            setattr(self.__class__, self.prop, property(_fget, _fset))

        for p in self._attributes:
            assert p[0] != '_'

            def _fget_p(self, _key=p):
                return self._attributes[_key]
            def _fset_p(self, value, _key=p):
                self._attributes[_key] = value

            setattr(self.__class__, p, property(_fget_p, _fset_p))

    def __str__(self):
        s = self.name
        if self._genericity is not None:
            s += '<{}>'.format(_to_string(self._genericity))

        if len(self._attributes) < 1:
            s += '()'
        else:
            _attr = []
            for key in self._attributes:
                value = self._attributes[key]
                _attr.append(key + '=' + _to_string(value))
            s += '({})'.format(','.join(_attr))
        return s

    def __repr__(self):
        _dict = {str('name'): str(self.name)}
        if self._genericity is not None:
            _dict[str(self.prop)] = self._genericity
        for k, v in self._attributes.items():
            _dict[str(k)] = v

        return str(_dict)

    def __eq__(self, other):
        return str(self) == str(other)

class default_source(_base_source):
    name = 'default'
    prop = None
default = default_source()

class named_source(_base_source):
    prop = None
    def __init__(self, name, **mdata):
        _base_source.__init__(self, **mdata)
        self.name = name

class merge_source(_base_source):
    name = 'merge'
    prop = 'op'
