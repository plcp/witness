# -*- coding: utf-8 -*-

import sys

def handle_unicode(payload):
    if sys.version_info < (3,):
        return unicode(payload)
    else:
        return payload

def is_string(payload):
    payload = handle_unicode(payload)
    if sys.version_info < (3,):
        return isinstance(payload, unicode)
    else:
        return isinstance(payload, str)
