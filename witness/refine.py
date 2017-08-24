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

from __future__ import (division, unicode_literals)

import sys

import witness as wit
import witness.error

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
            wit.error.warn(
                'No inverse function provided while refining data ' +
                'with "{}" backend (id: {}).'.format(
                    self.name,
                    self))
            raise NoDataRefinedError()
        self._inverse(state=state, parent=self)

    def __repr__(self):
        return self.name + object.__repr__(self)

