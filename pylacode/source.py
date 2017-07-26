# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
from __future__ import unicode_literals, division, with_statement

import sys
import pylacode as pl
assert sys.version_info >= (2, 7)

import collections

class _base_source:
    name = '_base'
    prop = 'genericity'

    def __init__(self, **mdata):
        _dict = dict(**mdata)
        self._attributes = collections.OrderedDict(sorted(_dict.items()))
        if self.prop is not None and self.prop in mdata:
            self._genericity = mdata[self.prop]
            del self._attributes[self.prop]
        else:
            self._genericity = None

        if self.prop is not None:
            def _fget(self):
                return self._genericity

            if sys.version_info < (3,):
                _fget.__name__ = str(self.prop)
            else:
                _fget.__name__ = self.prop
            setattr(self.__class__, self.prop, property(_fget))

        for p in self._attributes:
            assert p[0] != '_'

            def _fget_p(self, _key=p):
                return self._attributes[_key]

            if sys.version_info < (3,):
                _fget_p.__name__ = str(p)
            else:
                _fget_p.__name__ = p
            setattr(self.__class__, p, property(_fget_p))

    def __str__(self):
        s = self.name
        if self._genericity is not None:
            if (sys.version_info < (3,)
                and isinstance(self._genericity, unicode)):
                s += '<{}>'.format(str(self._genericity))
            elif isinstance(self._genericity, str):
                s += '<{}>'.format(self._genericity)
            elif issubclass(self._genericity.__class__, _base_source):
                s += '<{}>'.format(str(self._genericity))
            else:
                try:
                    s += '<{}>'.format(self._genericity.__name__)
                except NameError:
                    s += '<{}>'.format(self._genericity.__class__.__name__)

        if len(self._attributes) < 1:
            s += '()'
        else:
            _attr = []
            for key in self._attributes:
                value = self._attributes[key]
                if sys.version_info < (3,) and isinstance(value, unicode):
                    _attr.append(key + '=' + str(value))
                elif isinstance(value, str):
                    _attr.append(key + '=' + value)
                elif issubclass(value.__class__, _base_source):
                    _attr.append(key + '=' + str(value))
                else:
                    try:
                        _attr.append(key + '=' + value.__name__)
                    except NameError:
                        _attr.append(key + '=' + value.__class__.__name__)

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
