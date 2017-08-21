# -*- coding: utf-8 -*-

import unittest

import witness as wit
import witness.boil # !! wit.error.state.quiet = True !!

wit.error.state.quiet = False # (to avoid breaking other tests)

def build_weather_labels():
    w = wit.refine.label(name='weather', size=6)
    w.add(label='warm', value=[True, False])
    w.add(label='cold', value=[False, True], where=slice(0, 2))
    w.add(label='temp', where=slice(0, 2))

    w.add(label='rainy')
    w.add(label='cloudly')
    w.add(label='windy')

    w.add(label='!thunder', value=False)
    w.add(label='thunder', value=[True, None, True], where=slice(3, 6))

    w.add(label='rainstorm', where=slice(1, 4))
    w.add(label='thunderstorm', where=slice(2, 6))
    return wit.table.translation(w)


weather_labels = build_weather_labels()

# TOFIX: restructure tests code in a unittest-friendly fashion
class test_case(unittest.TestCase):

    # run tests
    def test_weather(self):
        wit.error.state.quiet = True

        o = wit.oracle.new(wit.backends.naive)
        o.add_labels(weather_labels)

        o.submit('cold')
        self.assertTrue('cold' in o.query('cold'))

        o.submit('rainy')
        self.assertTrue('rainy' in o.query('rainstorm'))
        self.assertTrue('rainstorm' not in o.query('rainstorm'))

        o.submit('cloudly')
        self.assertTrue('rainstorm' in o.query('rainstorm'))
        self.assertTrue('thunderstorm' not in o.query('rainstorm'))
        self.assertTrue('thunderstorm' not in o.query('thunderstorm'))

        o.submit('windy')
        self.assertTrue('thunderstorm' not in o.query('rainstorm'))
        self.assertTrue('thunderstorm' in o.query('thunderstorm'))

        wit.error.state.quiet = False

if __name__ == '__main__':
    unittest.main()
