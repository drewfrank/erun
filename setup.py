#!/usr/bin/env python

from distutils.core import setup

setup(
    name = 'erun',
    version = '0.1',
    description = 'A simple experiment runner.',
    long_description = open('README.rst').read() + '\n\n' + open('HISTORY.rst').read(),
    author = 'Drew Frank',
    author_email = 'drewfrank@gmail.com',
    packages = [
        'erun'
    ],
    scripts=['bin/erun', 'bin/equery']
)
