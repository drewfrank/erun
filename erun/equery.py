#!/usr/bin/env python2
"""
Output the results matching a metadata filter.
"""
__all__ = ['query']

import argparse
import json
import os
from cStringIO import StringIO
import subprocess
import textwrap

import erun

def parse_args():
    parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description='Collect the result files matching a specified filter.',
            epilog=textwrap.dedent("""
            equery collects the set of result files matching the provided options and
            prints them, along with their metadata, as a tab-delimited table to stdout.

            The command line interface for equery mirrors that of erun except that no input
            file is needed. See `erun -h` for an explanation of the special argument types
            accepted. When multiple values for a single option are specified (using e.g.
            set: notation), equery includes result files generated with any of the specified
            values.

            It may occasionally be useful to call equery from the command line, but its
            primary purpose is to simplify the development of the language-specific
            query functions. See e.g. the query() function in equery.py for the Python
            version, which calls equery in a subprocess and then parses the output.
            """))
    parser.add_argument('-o', metavar='OUT_DIR', type=str, 
            help='Directory where the result files are located.')
    parser.add_argument('-FLAG',
            help='Simple flag to be passed through to the experiment script. Multiple such flags are allowed.')
    parser.add_argument('-SHORT_OPT', metavar='ARG', type=str, 
            help='Short option with argument to be passed through to the experiment script. Multiple such options are allowed.')
    parser.add_argument('--LONG_OPT', metavar='ARG', type=str, 
            help='Long option with argument to be passed through to the experiment script. Multiple such options are allowed.')
    return parser.parse_known_args()

def main():
    """Print the files and metadata matching a specified filter to stdout."""
    args, params = parse_args()
    solo_flags, arg_flags = erun.parse_params(params)
    all = json.load(open(os.path.join(args.o, 'METADATA')))
    matches = [x for x in all if select(x, solo_flags, arg_flags)]
    # Don't use Pandas to implement this since it's not a dependency.
    solo_cols = list(set.union(*(set(entry['solo_flags']) for entry in matches)))
    arg_cols = list(set.union(*(set(entry['arg_flags'].keys()) for entry in matches)))
    all_cols = ['cmd'] + solo_cols + arg_cols + ['infile', 'outfile']
    def mk_row(entry):
        # Create a dict corresponding to one row of the output.
        row = {col: None for col in arg_cols + solo_cols}
        row.update(entry['arg_flags'])
        row.update({col: (True if col in entry.solo_flags else False) for col in solo_cols})
        row.update({'cmd': entry['cmd'], 'infile': entry['infile'], 
            'outfile': os.path.join(args.o, entry['outfile'])})
        return row
    print '\t'.join(all_cols)
    for x in matches:
        row = mk_row(x)
        print '\t'.join(row[key] for key in all_cols)

def select(entry, solo_flags, arg_flags):
    """Returns true if the metadata entry matches the filter, and False otherwise."""
    if any(x.lstrip('-') not in entry['solo_flags'] for x in solo_flags):
        return False
    if any(all(v != entry['arg_flags'].get(k.lstrip('-')) for v in vs) 
            for k,vs in arg_flags.iteritems()):
        return False
    return True

def query(result_dir, process=None, *args, **kwargs):
    """Return the results matching a metadata filter.
    
    Parameters
    ----------
    result_dir : str
        Directory containing the results and metadata file.
    process : function, optional
        A function to load and process each data file. If provided, this
        function will be called once for each result file (given the
        path to the file as input), and its return value placed into
        the `res` column of the returned DataFrame.
    *args : str, optional
        Flags to use as a filter, e.g. "-x".
    **kwargs : optional
        Flag/argument pairs to use as a filter, e.g. "foo='bar'".
        The same special value types (set, range, etc.) as used with the
        command-line erun program are accepted here.

    Returns
    -------
    results : list
        If the `process` argument was passed, return a list of the values
        returned by the provided function. Otherwise, just return a list
        of file names.
    """
    import pandas as pd
    # Get the keyword argument values into the expected format (lists of strings).
    for k,v in kwargs.iteritems():
        if isinstance(v, basestring):
            # v is a concrete string value or a special value. Leave it alone.
            pass
        elif hasattr(v, '__iter__'):
            # v is a Python list, array, etc. Convert to "set:" notation.
            kwargs[k] = 'set:' + ','.join(map(str, v))
        else:
            # v is probably a single, numeric value.
            kwargs[k] = str(v)
    # Build the command line and call equery. Note that equery strips all leading
    # dashes from all of the options, so it's okay if there are too many / not enough.
    cmd = ' '.join(['equery -o', result_dir, ' '.join('-%s' % flag for flag in args),
        ' '.join('-%s %s' % (k, v) for k,v in kwargs.iteritems())])
    df = pd.read_csv(StringIO(subprocess.check_output(cmd.split())), sep='\t')
    if process:
        df['res'] = df.outfile.apply(process)
    return df

if __name__ == '__main__':
    main()
