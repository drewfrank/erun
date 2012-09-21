#!/usr/bin/env python2
"""
Output a batch of commands corresponding to a single experiment and store metadata.

This utility makes a number of assumptions to simplify its implementation.
Specifically, in order for it to work properly the base command must satisfy
the following requirements:

    - Accept only one positional argument (the path to the input file).
    - Do not support multiple options with the same functionality (i.e. do not
      make both --dims and -d mean the same thing). This would cause problems
      when querying the metadata file using equery.
    - All options must begin with '-' or '--'.

To sweep over a range of values for a parameter the following syntax is supported:

    set:FOO,BAR,BAZ : A set of possible values.
    range:start,stop : A range of integer values from start to stop, inclusive.
        e.g. range:2,4 == set:2,3,4
    range:start,stop,step : A range of values from start to stop in increments
        of step.

Spaces before or after punctuation are NOT permitted. Any values specified without
one of these constructs will be automatically converted to a set with a single value,
and one command will be generated for each element in the cross-product of the
domains.
"""
import argparse
import itertools
import json
import md5
import os

FP_PREC = 1e-8 # Numbers that differ by less than this quantity are assumed equal.

def parse_args():
    parser = argparse.ArgumentParser(description='Prepare a set of commands to run a single experiment.')
    parser.add_argument('-r', metavar='MAIN_SCRIPT', type=str,
            help='The base command for running a single trial.')
    parser.add_argument('-o', metavar='OUT_DIR', type=str, 
            help='Directory for the result files.')
    parser.add_argument('-i', metavar='FILE', nargs='+', type=str, 
            help='Input files to process.')
    return parser.parse_known_args()

def main():
    args, params = parse_args()
    solo_flags, arg_flags = parse_params(params)
    base_cmd = ' '.join([args.r, ' '.join(solo_flags)])
    for vals in itertools.product(*arg_flags.values()):
        arg_pairs = zip(arg_flags.keys(), vals)
        arg_str = ' '.join(map(' '.join, arg_pairs))
        for file in args.i:
            outfile = os.path.join(args.o, outfile_name(base_cmd + arg_str + file))
            cmd = ' '.join([base_cmd, arg_str, '-o', outfile, file])
            store_metadata(open(os.path.join(args.o, 'METADATA'), 'a'),
                    args.r, solo_flags, arg_pairs, file, outfile, cmd)
            print cmd

def process_arg(x):
    """Process an argument and create a list of possible values."""
    if x.lower().startswith('set:'):
        return x[x.find(':')+1:].split(',')
    elif x.lower().startswith('range:'):
        sss = x[x.find(':')+1:].split(',')
        if len(sss) == 2:
            start, stop = map(float, sss[:2])
            step = 1
        if len(sss) == 3:
            start, stop, step = map(float, sss)
        return [str(intify(x)) for x in frange(start, stop, step)]
    else:
        return [x]

def parse_params(params):
    """Manually parse arguments that argparse doesn't know about."""
    def isoption(x):
        return x.startswith('-')
    solo_flags = []
    arg_flags = dict()
    i = 0
    while i < len(params):
        if not isoption(params[i]):
            raise ValueError('"' + params[i] + '" does not look like an option.')
        if i == len(params) - 1 or isoption(params[i+1]):
            solo_flags.append(params[i])
            i += 1
            continue
        else:
            arg_flags[params[i]] = process_arg(params[i+1])
            i += 2
            continue
    return solo_flags, arg_flags

def store_metadata(fh, cmd, solo_flags, arg_flags, infile, outfile, full_cmd):
    """Write the metadata corresponding to a single run to a file."""
    json.dump({
        'outfile': os.path.split(outfile)[-1],
        'cmd': cmd,
        'infile': infile,
        'solo_flags': solo_flags,
        'arg_flags': {k.lstrip('-'):v for k, v in arg_flags},
        'full_cmd': full_cmd
    }, fh, indent=2)

def outfile_name(cmd):
    """Generate an output filename by hashing the (partial) command line."""
    return md5.md5(cmd).hexdigest()[:8]

def frange(start, stop, step=1):
    """Like xrange, but inclusive and handles floats."""
    while start < stop:
        yield start
        start += step
    # Simple hack to handle floating point precision issues nicely,
    # most of the time :).
    if almost_equal(start, stop):
        yield start

def almost_equal(x, y):
    """Check if two numbers are equal up to FP_PREC."""
    return abs(x-y) < FP_PREC

def intify(x):
    """Return the nearest integer if it's almost equal to x."""
    return int(x) if almost_equal(x, round(x)) else x

if __name__ == '__main__':
    main()
