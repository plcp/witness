# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
from __future__ import unicode_literals, division, with_statement

import sys
import pylacode as pl
assert sys.version_info >= (2, 7)

import pylacode.source
import pylacode.fuzzy
import warnings
import operator

class NoDataRefinedError(Exception):
    pass

class data(object):
    def __init__(self, name, transform, inverse=None, **mdata):
        self._transform = transform
        self._inverse = inverse
        self.mdata = dict(**mdata)
        self.name = name

    def transform(self, state):
        self._transform(state=state, parent=self)

    def inverse(self, state):
        if self._inverse is None:
            warnings.warn('No inverse function provided while refining data '
                + 'with {} backend (id: {}).'.format(self.name, self))
            raise NoDataRefinedError()
        self._inverse(state=state, parent=self)

    def __repr__(self):
        return self.name + object.__repr__(self)

class label(data):
    def __init__(self, name, size, source=None, **mdata):
        self.size = size
        self.name = name
        self.mdata = dict(**mdata)
        self.labels = {}

        if source is None:
            self.source = pl.source.label_source(tag=self.name)
        else:
            assert pl.source.issource(source)
            self.source = source

    def add(self, label, *labels):
        if isinstance(label, tuple):
            if len(label) >= 2:
                assert isinstance(label[0], type(''))
                assert pl.logic.islogic(label[1])

            if len(label) == 2:
                assert len(label[1]) == self.size
                self.labels[label[0]] = (label[1].tbsl, slice(None));
            elif len(label) == 3:
                assert isinstance(label[3], slice)
                assert len(label[1]) == len(pl.logic.tbsl(self.size)[label[3]])
                self.labels[label[0]] = (label[1].tbsl, label[3])
            else:
                raise AssertionError('Ill-formed by-tuple label')
        elif isinstance(label, type('')):
            assert(len(self.labels) < self.size)

            _value = None
            if label.startswith('!'):
                _value = pl.logic.tbsl(pl.logic.tbsl.false())
            elif label.startswith('?'):
                _value = pl.logic.tbsl(pl.logic.tbsl.uncertain())
            else:
                _value = pl.logic.tbsl(pl.logic.tbsl.true())
            _slice = slice(len(self.labels))

            self.labels[label] = (_value, _slice)
        else:
            raise AssertionError('Unable to use {} to construct a label'.format(
                label))

        for _remaining in labels:
            self.add(_remaining)

    def get_label(self, label):
        if label not in self.labels:
            return None

        _evidence = pl.fuzzy.evidence(
            size=self.size,
            source=self.source,
            origin='label',
            label=label)
        _value, _slice = self.labels[label]

        _evidence.value[_slice] = _value
        return _evidence

    def transform(self, state):
        _refined = False
        for idx, payload in state.remaining_data:
            _label = self.get_label(payload)
            if _label is None and payload[0].startswith('!'):
                _label = self.get_label(payload[1:])
                if _label is not None:
                    _label.value.invert()

            if _label is not None:
                state.ouput.append(_label)
                del state.remaining_data[idx]
                _refined = True

        if not _refined:
            raise NoDataRefinedError()

    def inverse(self, state):
       raise NoDataRefinedError() # todo
