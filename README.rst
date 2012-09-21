erun: A lightweight experiment runner
==================-----==============

About
-----

erun is a small collection of tools designed to simplify the task of setting up
and running computational experiments. It is implemented in Python but
completely agnostic with respect to the language and data formats used in the
experimental code -- its only requirement is a fairly general command-line interface
for running experimental trials.

Usage
-----

Using erun involves four simple steps:

1. create a wrapper.
2. generate cmds
3. run cmds.
4. collect results.

For a simple demo of how this all works together, see tests/simulate_workflow.py.

Installation
------------

python setup.py install
or
pip install -e ./
