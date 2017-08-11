# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import operator
import sys

import numpy as np
import pylacode as pl
import pylacode.error
import pylacode.fuzzy
import pylacode.source
import pylacode.tools

assert sys.version_info >= (2, 7)


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
            pl.error.warn('No inverse function provided while refining data ' +
                          'with "{}" backend (id: {}).'.format(
                          self.name, self))
            raise NoDataRefinedError()
        self._inverse(state=state, parent=self)

    def __repr__(self):
        return self.name + object.__repr__(self)


def _from_bool(value, size):
    if size is None:
        size = 1
    if value:
        return pl.logic.tbsl(pl.logic.tbsl.true(size))
    else:
        return pl.logic.tbsl(pl.logic.tbsl.false(size))


def _from_boollist(value, size):
    if size is None:
        size = len(value)
    assert len(value) == size
    _value = pl.logic.tbsl(size=size)
    for idx, _b in enumerate(value):
        _value[idx] = _from_bool(_b, 1)
    return _value


def label_castvalue(value, size):
    if value is None:
        if size is None:
            size = 1
        return pl.logic.tbsl(pl.logic.tbsl.true(size))
    elif isinstance(value, (bool, np.bool, np.bool_)):
        return _from_bool(value, size)
    elif (isinstance(value, list) and isinstance(value[0],
                                                 (bool, np.bool, np.bool_))):
        return _from_boollist(value, size)
    elif (isinstance(value, tuple) and len(value) == 3 and
          isinstance(value[0], np.ndarray)):
        if size is None:
            size = len(value[0])
        assert len(value[0]) == size
        return pl.logic.tbsl(value)
    elif pl.logic.islogic(value):
        return value.tbsl
    else:
        raise AssertionError('Unable to build a label from {}'.format(value) +
                             ' (size={})'.format(size))


class label(data):
    class item(object):
        def __init__(self, **attributes):
            for a in attributes:
                setattr(self, a, attributes[a])

    def __init__(self, name, size, source=None, **mdata):
        self.size = size
        self.name = name
        self.last = 0
        self.mdata = dict(**mdata)
        self.labels = {}

        if source is None:
            self.source = pl.source.label_source(tag=self.name)
        else:
            assert pl.source.issource(source)
            self.source = source

    def add(self,
            labels=[],
            label=None,
            value=None,
            transform_slice=None,
            inverse_op='by_trust',
            size=None):
        labels = pl.tools.listify(labels)
        if label is None:
            if len(labels) == 0:
                raise AssertionError('No label provided: {}... {}'.format(
                    dict(
                        label=label,
                        value=value,
                        size=size,
                        transform_slice=transform_slice,
                        inverse_op=inverse_op), labels))
            self.add(labels=labels[1:], **labels[0])
            return

        if transform_slice is not None:
            assert isinstance(transform_slice, slice)
            size = len(pl.logic.tbsl(size=self.size)[transform_slice])

        value = label_castvalue(value, size)
        size = len(value)

        if transform_slice is None and len(value) == self.size:
            transform_slice = slice(None)
        elif transform_slice is None:

            transform_slice = slice(self.last, self.last + size)
            self.last += size
            if self.last > self.size:
                oversized_label_collection = ('Oversized label collection: '
                    + 'need {}, only {} provided'.format(self.last, self.size))
                pl.error.warn(oversized_label_collection)
        else:
            assert size == len(pl.logic.tbsl(size=self.size)[transform_slice])

        if inverse_op == 'by_trust':
            inverse_op = lambda x, y: np.average(np.abs(x.trust - y.trust))
        elif inverse_op == 'by_truth':
            inverse_op = lambda x, y: np.average(np.abs(x.truth - y.truth))
        elif inverse_op == 'by_probability':
            inverse_op = lambda x, y: np.average(
                np.abs(x.probability - y.probability))

        self.labels[label] = self.item(
            label=label,
            value=value,
            size=size,
            transform_slice=transform_slice,
            inverse_op=inverse_op)

        if len(labels) > 0:
            self.add(labels=labels[1:], **labels[0])

    def get_label(self, label):
        if label not in self.labels:
            return None
        return self.labels[label]

    def transform_label(self, label):
        item = self.get_label(label)
        if item is None:
            return None

        _evidence = pl.fuzzy.evidence(
            size=self.size, source=self.source, origin='label', label=label)
        _evidence.value[item.transform_slice] = item.value
        return _evidence

    def transform(self, state):
        def tconv(label):
            # try with transform(label)
            payload = self.transform_label(label)

            # then, try with !transform(label) (if label startswith !)
            # then, try with !transform(!label)
            if payload is None:
                if label.startswith('!'):
                    payload = self.transform_label(label[1:])
                if payload is None:
                    payload = self.transform_label('!' + label)
                if payload is not None:
                    payload.value.invert()
            return payload

        output = pl.table.foreach(tconv, state.remaining_data)
        if len(output) < 1:
            raise NoDataRefinedError
        else:
            state.output += output

    def match_label(self, label, evidence, threshold=0.25):
        item = self.get_label(label)
        if item is None:
            return None

        payload_value = evidence.value[item.transform_slice]
        if not item.size == len(payload_value):
            return None

        if item.inverse_op(payload_value, item.value) > threshold:
            return None

        return item.label

    def inverse(self, state, threshold=0.25):
        def imatch(evidence):
            results = []
            for label in self.labels:
                v = self.match_label(label, evidence, threshold=threshold)
                if v is not None:
                    results.append(v)
            return results

        output = pl.table.foreach(imatch, state.remaining_data)
        if len(output) < 1:
            raise NoDataRefinedError()
        else:
            state.output += output
