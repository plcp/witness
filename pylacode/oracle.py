# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
from __future__ import unicode_literals, division, with_statement

import sys
import pylacode as pl
assert sys.version_info >= (2, 7)

import pylacode.table
import pylacode.fuzzy

class oracle_backend(object):
    def __init__(self, parent):
        self.parent = parent
    def reset(self):
        raise NotImplementedError
    def learn(self, *evidences, history=None):
        raise NotImplementedError
    def query(self, *evidences):
        raise NotImplementedError
    def submit(self, *evidences):
        raise NotImplementedError

class oracle(object):
    def __init__(self, backend_class, *kargs, **kwargs):
        self.backend = backend(parent=self, *kargs, **kwargs)
        self.backend_class = backend
        self.reset(backend=True)

    def add_table(self, table):
        self.tables.append(table)

    def add_label(self, label):
        self.lables.append(label)

    def reset(self, backend=False):
        if backend:
            self.backend.reset()
        self.tables = []
        self.labels = []

    def digest_data(self, *payloads, inverse=False):
        _output = []
        for table in self.tables:
            table.digest(*payloads, inverse=inverse)
            _output += table.output
        return _output

   def digest_label(self, *labels, inverse=False):
        _output = []
        for table in self.tables:
            table.digest(*labels, inverse=inverse)
            _output += table.output
        return _output

    def digest(self, *various, inverse=False, try_data=False):
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

    def submit(self, *various):
        self.backend.submit(*self.digest(*various))

    def submit_data(self, *payloads):
        self.submit(*self.digest_data(*payloads))

    def submit_label(self, *labels):
        self.submit(*self.digest_label(*labels))

    def learn(self, *answers, history=None, try_data=False):
        _answers = self.digest(*answers, try_data=try_data)
        _history = None
        if history is not None:
            _history = self.digest(*history, try_data=try_data)
        self.backend.learn(*_answers, history=_history)

    def query(self, *queries, inverse_answer=True, try_data=False):
        _queries = self.digest(*queries, try_data=try_data)
        _answers = self.backend.query(*_queries)
        if inverse_answer:
            return self.digest(*_answers, inverse=True, try_data=True)
        else:
            return _answers
