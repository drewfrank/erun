#!/usr/bin/env python2
"""
Output the list of result files matching a metadata filter.
"""

import argparse
import json
import os

import erun

def parse_args():
    parser = argparse.ArgumentParser(description='Collect the result files matching a specified filter.')
    parser.add_argument('-o', metavar='OUT_DIR', type=str, 
            help='Directory where the result files are located.')
    return parser.parse_known_args()

def main():
    """Print the files matching a specified filter to stdout."""
    args, params = parse_args()
    solo_flags, arg_flags = erun.parse_params(params)
    all = json.load(open(os.path.join(args.o, 'METADATA')))
    matches = [x for x in all if select(x, solo_flags, arg_flags)]
    print '\n'.join(os.path.join(args.o, x['outfile']) for x in matches)

def select(entry, solo_flags, arg_flags):
    """Returns true if the metadata entry matches the filter, and False otherwise."""
    if any(x.lstrip('-') not in entry['solo_flags'] for x in solo_flags):
        return False
    if any(all(v != entry['arg_flags'].get(k.lstrip('-')) for v in vs) 
            for k,vs in arg_flags.iteritems()):
        return False
    return True

if __name__ == '__main__':
    main()
