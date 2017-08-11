# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import sys

import pylacode as pl

assert sys.version_info >= (2, 7)

# api version
api_version = (0, 0, 2)

# test class


class test:
    test_list = ['logic', 'source', 'fuzzy', 'refine', 'table']

    def __init__(self):
        self.run()

    @staticmethod
    def run():
        import pylacode.test_modules
        for t in test.test_list:
            test_name = 'test_{}'.format(t)

            __import__('pylacode.test_modules.{}'.format(test_name))
            test_module = getattr(pl.test_modules, test_name)

            assert test_module.run()