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

import copy
import sys

import witness as wit
import witness.refine
import witness.tools

assert sys.version_info >= (2, 7)


def foreach(f, target):
    results = []
    for idx, e in zip(range(len(target) - 1, -1, -1), reversed(target)):
        result = wit.tools.listify(f(e))
        if len(result) > 0:
            del target[idx]
            results += result
    return results


class translation(object):
    def __init__(self, backends):
        self.table = self
        self.backends = wit.tools.listify(backends)
        self.reset(oracle=True)

    def reset(self, oracle=False):
        self.mdata = {}
        self.output = []
        self.inverse = False
        self.backtrace = []
        self.active_backend = None
        self.previous_state = None
        self.remaining_data = []
        self.pending_output = []
        self.pending_backends = []

        if oracle:
            self.oracle = None

    @property
    def finished(self):
        return len(self.pending_backends) < 1

    def prepare(self, payloads, inverse=False, reset=True, **mdata):
        payloads = wit.tools.listify(payloads)
        if reset:
            self.reset()

        self.mdata = dict(**mdata)
        self.inverse = inverse
        self.remaining_data = list(payloads)
        self.pending_backends = list(self.backends)

    def apply(self, backend=None):
        if backend is None:
            backend = self.active_backend
            if self.active_backend is None:
                return False
        try:
            if not self.inverse:
                backend.transform(self)
            else:
                backend.inverse(self)

            self.backtrace.append(backend)
            return True
        except wit.refine.NoDataRefinedError:
            pass

        return False

    def iterate(self, retain_history=False, **mdata):
        if self.finished:
            return False

        previous_state = None
        if retain_history:
            previous_state = copy.deepcopy(self)

        backend = self.pending_backends.pop()
        self.mdata = dict(self.mdata, **mdata)
        self.active_backend = backend

        if self.apply():
            self.previous_state = previous_state
        return True

    def digest(self,
               payloads,
               inverse=False,
               retain_history=False,
               reset=True,
               **mdata):
        payloads = wit.tools.listify(payloads)
        self.prepare(payloads, inverse=inverse, reset=reset, **mdata)
        while self.iterate(retain_history=retain_history):
            pass
        return self.finish()

    def finish(self):
        if not self.finished:
            raise RuntimeError('Method finish called when not finished.')

        return self.output
