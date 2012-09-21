#!/usr/bin/env python2
"""A mock experiment script for testing erun."""

import argparse
import os

def parse_args():
    parser = argparse.ArgumentParser(description='A mock experiment script.')
    parser.add_argument('-s', type=int,
            help='Random seed.')
    parser.add_argument('--foo', type=str,
            help='Either bar or baz.')
    parser.add_argument('-o', type=str, 
            help='Output file name')
    parser.add_argument('file', type=str, 
            help='Input file.')
    return parser.parse_args()

def main():
    args = parse_args()
    # Write the arguments to the output file.
    open(args.o, 'w').write(str(args))

if __name__ == '__main__':
    main()
