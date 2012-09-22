#!/usr/bin/env python2
"""
Output the list of result files matching a metadata filter.
"""
__all__ = ['query']

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

def query(result_dir, process=None, *args, **kwargs):
    """Return a list of results (or files) matching a metadata filter.
    
    Parameters
    ----------
    result_dir : str
        Directory containing the results and metadata file.
    process : function, optional
        A function to load and process each data file.
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
            # v is a string. Pass it through the parsing function.
            kwargs[k] = erun.process_arg(v)
        elif hasattr(v, '__iter__'):
            # v is a Python list, array, etc.
            kwargs[k] = map(str, v)
        else:
            # v is probably a single, numeric value.
            kwargs[k] = [str(v)]
    all = json.load(open(os.path.join(result_dir, 'METADATA')))
    solo_flags = map(str, args)
    arg_flags = {k: v for k,v in kwargs.iteritems()}
    matches = [x for x in all if select(x, solo_flags, arg_flags)]
    df = dataframe_from_metadata(matches)
    if process:
        df['res'] = df.outfile.apply(lambda x: os.path.join(result_dir, x)).apply(process)
    return df

def dataframe_from_metadata(metadata):
    """Create a dataframe to organize metadata.
    
    Parameters
    ----------
    metadata : list of dicts
        Metadata entries for a collection of trials.

    Returns
    -------
    df : pandas.DataFrame
        A dataframe representation of the metadata. This dataframe is constructed as
        follows:
        - Create columns for cmd, each element of solo_flags, each element of arg_flags,
          infile, and outfile.
        - Columns corresponding to a solo_flag element are boolean.
        - Columns corresponding to an arg_flag pair are string valued.
    """
    import pandas as pd
    solo_cols = list(set.union(*(set(entry['solo_flags']) for entry in metadata)))
    arg_cols = list(set.union(*(set(entry['arg_flags'].keys()) for entry in metadata)))
    def mk_row(entry):
        # Create a dict corresponding to one row of the DataFrame.
        row = {col: None for col in arg_cols}
        row.update(entry['arg_flags'])
        row.update({col: (True if col in entry.solo_flags else False) for col in solo_cols})
        row.update({'cmd': entry['cmd'], 'infile': entry['infile'], 'outfile': entry['outfile']})
        return row
    return pd.DataFrame([mk_row(x) for x in metadata])

if __name__ == '__main__':
    main()
