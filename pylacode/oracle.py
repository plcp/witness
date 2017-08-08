# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import sys

import pylacode as pl
import pylacode.fuzzy
import pylacode.table
import pylacode.tools

assert sys.version_info >= (2, 7)


class oracle_backend(object):
    def __init__(self, parent):
        self.parent = parent

    def reset(self):
        raise NotImplementedError

    def learn(self, evidences, history=None):
        raise NotImplementedError

    def query(self, evidences):
        raise NotImplementedError

    def submit(self, evidences):
        raise NotImplementedError


class oracle(object):
    def __init__(self, backend_class, *kargs, **kwargs):
        self.backend = backend_class(parent=self, *kargs, **kwargs)
        self.backend_class = backend_class
        self.reset(backend=True)

    def add_table(self, tables):
        tables = pl.tools.listify(tables)
        for table in tables:
            table.reset(oracle=True)
            table.oracle = self
            self.tables.append(table)

    def add_label(self, labels):
        labels = pl.tools.listify(labels)
        for label in labels:
            label.reset(oracle=True)
            label.oracle = self
            self.lables.append(label)

    def reset(self, backend=False):
        if backend:
            self.backend.reset()
        self.tables = []
        self.labels = []

    def digest_data(self, payloads, inverse=False):
        payloads = pl.tools.listify(payloads)
        _output = []
        for table in self.tables:
            table.digest(payloads, inverse=inverse)
            _output += table.output
        return _output

    def digest_label(self, labels, inverse=False):
        labels = pl.tools.listify(labels)
        _output = []
        for table in self.tables:
            table.digest(labels, inverse=inverse)
            _output += table.output
        return _output

    def digest(self, various, inverse=False, try_data=False):
        various = pl.tools.listify(various)
        _outputs = []
        for v in various:
            if isinstance(v, pl.fuzzy.evidence):
                _outputs.append(v)
                continue

            if isinstance(v, type('')):
                _output = self.digest_label(v, inverse=inverse)
                if len(_output) > 0:
                    _outputs += _output
                    continue

            if try_data:
                _output = self.digest_data(v, inverse=inverse)
                if len(_output) > 0:
                    _outputs += _output
                    continue

        return _outputs

    def submit(self, various):
        self.backend.submit(self.digest(various))

    def submit_data(self, payloads):
        self.submit(self.digest_data(payloads))

    def submit_label(self, labels):
        self.submit(self.digest_label(labels))

    def learn(self, answers, history=None, try_data=False):
        answers = pl.tools.listify(answers)
        _answers = self.digest(answers, try_data=try_data)
        _history = None
        if history is not None:
            _history = self.digest(history, try_data=try_data)
        self.backend.learn(_answers, history=_history)

    def query(self, queries, inverse_answer=True, try_data=False):
        queries = pl.tools.listify(queries)
        _queries = self.digest(queries, try_data=try_data)
        _answers = self.backend.query(_queries)
        if inverse_answer:
            return self.digest(_answers, inverse=True, try_data=True)
        else:
            return _answers
