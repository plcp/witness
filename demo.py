# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import witness as wit
import witness.backends
import witness.refine
import witness.error
import witness.table
import witness.oracle

wit.error.state.quiet = True

refine_weather_labels = wit.refine.label(name='weather', size=4)
refine_weather_labels.add([
        dict(label='cold'),
        dict(label='warm', value=False, transform_slice=slice(0, 1)),
        dict(label='rainy'),
        dict(label='cloudly'),
        dict(label='windy'),
        dict(label='rainstorm', transform_slice=slice(0, 3)),
    ])

weather_labels = wit.table.translation(refine_weather_labels)

o = wit.oracle.oracle(wit.backends.naive)
o.add_labels(weather_labels)

o.submit('!warm')
print(o.query('cold'))
o.submit('cloudly')
print(o.query('rainstorm'))
o.submit(['rainy', 'windy'])
print(o.query('rainstorm'))
