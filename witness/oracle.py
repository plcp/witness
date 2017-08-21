# -*- coding: utf-8 -*-

##
# witness
#
#  Copyright 2017 by Matthieu Daumas <matthieu@daumas.me> and other authors.
#
# This file is a part of fuddly, as part of the knowledge component.
#
#  Licensed under GNU General Public License 3.0 or later.
#  Some rights reserved. See COPYING, AUTHORS.
#
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>
##

from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import sys

import witness as wit
import witness.fuzzy
import witness.table
import witness.tools

assert sys.version_info >= (2, 7)


class backend(object):
    def __init__(self, parent):
        self.parent = parent
        self.reset()

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
        self.reset(tables=True)

    def add_tables(self, tables):
        tables = wit.tools.listify(tables)
        for table in tables:
            table.reset(oracle=True)
            table.oracle = self
            self.tables.append(table)

    def add_labels(self, labels):
        labels = wit.tools.listify(labels)
        for label in labels:
            label.reset(oracle=True)
            label.oracle = self
            self.labels.append(label)

    def reset(self, tables=False, backend=True):
        if backend:
            self.backend.reset()
        if tables:
            self.tables = []
            self.labels = []

    def digest_payloads(self, payloads, inverse=False):
        payloads = wit.tools.listify(payloads)
        _output = []
        for table in self.tables:
            _output += table.digest(payloads, inverse=inverse)
        return _output

    def digest_labels(self, labels, inverse=False):
        labels = wit.tools.listify(labels)
        _output = []
        for table in self.labels:
            _output += table.digest(labels, inverse=inverse)
        return _output

    def digest(self, various, try_data=False):
        various = wit.tools.listify(various)
        _outputs = []
        for v in various:
            if isinstance(v, wit.fuzzy.evidence):
                _outputs.append(v)
                continue

            if wit.tools.is_string(v):
                _output = self.digest_labels(v)
                if len(_output) > 0:
                    _outputs += _output
                    continue

            if try_data:
                _output = self.digest_payloads(v)
                if len(_output) > 0:
                    _outputs += _output
                    continue

        return _outputs

    def submit(self, various):
        self.backend.submit(self.digest(various))

    def submit_payloads(self, payloads):
        self.submit(self.digest_payloads(payloads))

    def submit_labels(self, labels):
        self.submit(self.digest_labels(labels))

    def learn(self, answers, history=None, try_data=False):
        answers = wit.tools.listify(answers)
        _answers = self.digest(answers, try_data=try_data)
        _history = None
        if history is not None:
            _history = self.digest(history, try_data=try_data)
        self.backend.learn(_answers, history=_history)

    def query(self, queries, inverse_answer=True, try_data=False):
        queries = wit.tools.listify(queries)
        _queries = self.digest(queries, try_data=try_data)
        _answers = self.backend.query(_queries)
        if inverse_answer:
            return self.digest_labels(_answers, inverse=True)
        else:
            return _answers


new = oracle
