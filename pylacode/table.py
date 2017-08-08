# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import copy
import sys

import pylacode as pl
import pylacode.refine
import pylacode.tools

assert sys.version_info >= (2, 7)


class translation(object):
    def __init__(self, backends):
        self.table = self
        self.backends = backends
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
        payloads = pl.tools.listify(payloads)
        if reset:
            self.reset()

        self.mdata = dict(**mdata)
        self.inverse = inverse
        self.remaining_data = list(payloads)
        self.pending_backends = list(self.backends)

    def trigger(self, backend=None):
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
        except pl.refine.NoDataRefinedError:
            pass

        return False

    def next(self, retain_history=False, **mdata):
        if self.finished:
            return False

        previous_state = None
        if retain_history:
            previous_state = copy.deepcopy(self)

        backend = self.pending_backends.pop()
        self.mdata = dict(self.mdata, **mdata)
        self.active_backend = backend

        if self.execute():
            self.previous_state = previous_state
        return True

    def digest(self,
               payloads,
               inverse=False,
               retain_history=False,
               reset=True,
               **mdata):
        payloads = pl.tools.listify(payloads)
        self.prepare(payloads, inverse=inverse, reset=reset, **mdata)
        while self.iterate(retain_history=retain_history):
            pass
        return self.finish()

    def finish(self):
        if not self.finished:
            raise RuntimeError('Method finish called when not finished.')

        return self.output
