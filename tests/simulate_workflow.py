#!/usr/bin/env python2
"""Simulate a simple workflow using erun."""

import json
import os
import shutil

import erun
import experiment

# Start with a clean environment.
shutil.rmtree('inputs', ignore_errors=True)
shutil.rmtree('results', ignore_errors=True)
shutil.rmtree('cmds', ignore_errors=True)

os.mkdir('inputs')
os.mkdir('results')
os.system('touch inputs/input1; touch inputs/input2')

# Prepare the commands to run our experiment.
os.system('erun -r ./experiment.py -o results -s range:0,10,5 --foo set:bar,baz -i inputs/* >cmds')

assert len(open('cmds').readlines()) == 12 # (3 values of s) * (2 values of foo) * (2 input files)
assert len(json.load(open('results/METADATA'))) == 12

# Run the commands, generating results.
os.system('source cmds')

assert len(os.listdir('results')) == 13 # includes the METADATA file.
