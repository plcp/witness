# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
from __future__ import unicode_literals, division, with_statement

import sys
import pylacode as pl
assert sys.version_info >= (2, 7)

# default imports
modules = ['logic',]
def bootstrap(modules):
    for module in modules:
        __import__('pylacode.{}'.format(module))
bootstrap(modules)

# test class
class test:
    test_list = ["logic",]

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
