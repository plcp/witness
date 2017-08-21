# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import sys

import witness as wit

assert sys.version_info >= (2, 7)

# api version
api_version = (0, 0, 4)


# run tests
def test():
    import unittest

    suite = unittest.TestLoader().loadTestsFromName('witness.test_modules')
    unittest.TextTestRunner(verbosity=2).run(suite)

