
# erun: A lightweight experiment runner

## About

**erun** is a small collection of tools designed to simplify the task of setting up and running computational experiments. It is implemented in Python but supports experimental code and data in arbitrary languages and formats -- its only requirement is a fairly general command-line interface for running experimental trials.

## Usage

Using erun involves four simple steps:

1.  Create an experiment script that conforms to the erun command-line interface. In this example, the script is called experiment.py:
    
    ```sh
    ./experiment.py -h
    ```
    
        usage: experiment.py [-h] [-s S] [--foo FOO] [-o O] file
        
        A mock experiment script.
        
        positional arguments:
          file        Input file.
        
        optional arguments:
          -h, --help  show this help message and exit
          -s S        Random seed.
          --foo FOO   Either bar or baz.
          -o O        Output file name
    
    The arguments `-s` and `--foo` are parameters to be varied over the course of different trials. The arguments `-o` and `file` implement the erun command line interface.

2.  Call the erun executable to generate the experiment's commands and associated metadata. For example, the following call:
    
    ```sh
    erun -r ./experiment.py -o results -s range:0,10,5 --foo set:bar,baz -i inputs/input1 inputs/input2 >cmds
    ```
    
    will generate the command lines to run 12 experiments (3 values of `-s`, 2 values of `--foo`, and 2 input files) and write them to `cmds`.
    
    ```sh
    head cmds
    ```
    
        ./experiment.py  -s 0 --foo bar -o results/8532fb26 inputs/input1
        ./experiment.py  -s 0 --foo bar -o results/38d06d92 inputs/input2
        ./experiment.py  -s 0 --foo baz -o results/7cbc7805 inputs/input1
        ./experiment.py  -s 0 --foo baz -o results/6055ff6a inputs/input2
        ./experiment.py  -s 5 --foo bar -o results/cfe097e4 inputs/input1
        ./experiment.py  -s 5 --foo bar -o results/b2642081 inputs/input2
        ./experiment.py  -s 5 --foo baz -o results/97a7bb3b inputs/input1
        ./experiment.py  -s 5 --foo baz -o results/ae5573d8 inputs/input2
        ./experiment.py  -s 10 --foo bar -o results/fe80f688 inputs/input1
        ./experiment.py  -s 10 --foo bar -o results/b65cb717 inputs/input2

3.  Run the commands generated in step 2, either locally via bash or remotely using something like GNU parallel.
    
    ```sh
    bash cmds
    ```
    
    At this point, the results are stored in individual files in the specified output directory (`results/` in this case), and `results/METADATA` contains the mapping from filenames to parameter settings:
    
    ```sh
    ls -x results
    ```
    
    <pre class="example">
    38d06d92  6055ff6a  67a41f56  7cbc7805  8532fb26  97a7bb3b  ae5573d8  b2642081
    b65cb717  bacc9b0e  cfe097e4  fe80f688  METADATA
    </pre>

4.  Use one of the language-specific query modules to collect a subset of the results. The Python version works as follows:
    
    ```python
    import erun; import numpy as np
    df = erun.query('results', process=np.loadtxt, s=[0,10], foo='baz')
    print df[:10]
    ```
    
    <pre class="example">
                   cmd  foo         infile   outfile   s  res
    0  ./experiment.py  baz  inputs/input1  7cbc7805   0    2
    1  ./experiment.py  baz  inputs/input2  6055ff6a   0    2
    2  ./experiment.py  baz  inputs/input1  bacc9b0e  10    7
    3  ./experiment.py  baz  inputs/input2  67a41f56  10    7
    </pre>
    
    Here, `df` is a [Pandas](<http://pandas.pydata.org>) DataFrame object containing the results and metadata for the trials specified by the parameters to `erun.query`.

## Command-line interface

```sh
erun -h
```

    usage: erun [-h] -r MAIN_SCRIPT -o OUT_DIR [-FLAG FLAG] [-SHORT_OPT ARG]
                [--LONG_OPT ARG] -i FILE [FILE ...]
    
    Prepare a set of commands to run a single experiment.
    
    optional arguments:
      -h, --help          show this help message and exit
      -r MAIN_SCRIPT      The experiment script for running a single trial.
      -o OUT_DIR          Directory for the result files.
      -FLAG FLAG          Simple flag to be passed through to the experiment
                          script. Multiple such flags are allowed.
      -SHORT_OPT ARG      Short option with argument to be passed through to the
                          experiment script. Multiple such options are allowed.
      --LONG_OPT ARG      Long option with argument to be passed through to the
                          experiment script. Multiple such options are allowed.
      -i FILE [FILE ...]  Input files to process.
    
    Specifying argument combinations for the experiment script
    ----------------------------------------------------------
    Of the options listed above, "-r", "-o", "-h", and "-i" are given
    special treatment by the erun executable. All other options
    specified when calling erun are treated as options of the experiment
    script and determine the set of commands generated by erun.
    
    For example:
      erun -r ./trial -o results -i input.txt -x 1 --foo bar
    produces a single command as output:
      ./trial -o results/<OUTFILE> -x 1 --foo bar input.txt
    where OUTFILE is a randomly generated filename for the results.
    
    To ease the task of specifying many argument combinations, erun
    has syntax for several "special" argument types:
    
      - set:<value>[,<value>]*
        A set of values.
    
      - range:<start>,<stop>[,<step>]
        A range of values from <start> to <stop>, in increments of
        <step> (with a default step size of 1). A range is inclusive
        unless it does not divide evenly into increments of <step>,
        in which case <stop> is excluded. Note that, for example,
        set:2,4,6,8 is equivalent to range:2,8,2. Non-integer values
        are also supported.
    
    Each option with a special argument value actually refers to a
    set of concrete values. erun interprets these by generating
    one command line (trial) for each element in the Cartesian product
    of these sets. For example, the following invocations:
      erun -r ./trial -o results -i input.txt \
              -x range:1,2 -y --foo set:bar,baz
    will generate four commands:
      ./trial -o results/[OUTFILE] -x 1 -y --foo bar input.txt
      ./trial -o results/[OUTFILE] -x 1 -y --foo baz input.txt
      ./trial -o results/[OUTFILE] -x 2 -y --foo bar input.txt
      ./trial -o results/[OUTFILE] -x 2 -y --foo baz input.txt
    Note that since the option "-y" does not have a special
    value it is included unaltered in every command.
    
    Spaces around punctuation are not allowed in any of the special
    arguments.
    
    Experiment script command line interface
    ----------------------------------------
    erun makes a few assumptions about the command-line interface of the
    experiment script:
     - It must accept its output file name via "-o FILE".
     - It must accept its input file as its sole positional argument.
     - If it parses long options, it must accept the format "--long ARG"
       rather than (or in addition to) "--long=ARG".
     - All options must begin with "-" or "--".
     - It should not accept multiple forms of the same option, e.g.
       "-d" and "--dims" having the same behavior. If erun is called
       multiple times using different forms of the same option,
       subsequent queries may not return all relevant results.

## Language-specific query modules

### Python

## Installation

`python setup.py install`
