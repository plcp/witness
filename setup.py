#!/usr/bin/env python

from distutils.core import setup

setup(
    name='witness',
    packages=['witness'],
    package_data={'witness': ['backends/*.py']},
    version='0.0.5',
    description=('Knowledge abstraction layer based on subjective logic'),
    author='plcp',
    author_email='matthieu@daumas.me',
    url='https://github.com/plcp/witness',
    download_url='https://github.com/plcp/witness/archive/0.0.5.zip',
    install_requires=['numpy'], )
