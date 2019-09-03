#!/usr/bin/python python3

# Use emacs python mode
# -*- mode: python-mode -*-

"""Compute lines of code for a proof."""

import argparse
import re
import subprocess
import logging
import os
import json

import make_sources

################################################################

def create_parser():
    """Build the command line parser."""

    parser = argparse.ArgumentParser(
        description='Compute the lines of code in a goto binary.')

    parser.add_argument(
        '--blddir',
        metavar='BLD',
        required=True,
        help="""
        The build directory.  The command "make goto" in this directory
        produces the goto binary.
	"""
    )
    parser.add_argument(
        '--srcdir',
        metavar='SRC',
        required=True,
        help="""
        The root of the source tree.  The root is typically the root
        of the respository, and the build directory is typically
        contained in this source tree.
	"""
    )
    parser.add_argument(
        '--cbmcdir',
        metavar='STR',
        required=True,
        help="""
        A string in an absolute path --- typically cbmc/proofs or
        .cbmc-batch/jobs --- indicating that the path lies within the
        directory containing all code written for cbmc proof work.
        This is used to identify the code used to build the proof
        harness.
	"""
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Debugging output'
    )
    return parser

################################################################

def run(cmd, cwd=None):
    """Run command."""
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if result.returncode:
        print("Failed to run command", cmd)
        logging.info("Command failed: %s", ' '.join(result.args))
        logging.debug("stdout is")
        logging.debug(result.stdout)
        logging.debug("stderr is")
        logging.debug(result.stderr)
        result.check_returncode()
    logging.info("Command succeeded: %s", ' '.join(result.args))
    logging.debug("stdout is")
    logging.debug(result.stdout)
    return result.stdout

################################################################
# Get the lines of code in each function of a goto binary.

def expand_pathname(name, builddir=None, workingdir=None):
    """Expand a source location filename to an absolute path."""

    paths = [path for path in [builddir, workingdir, name] if path]
    return os.path.abspath(os.path.join(*paths))

def internal_file(name):
    return name.startswith('<') and name.endswith('>')

def show_goto_functions(goto):
    """Get program listing of goto binary."""

    # Use textual output since xml and json output does not reliably
    # attach source locations to lines.
    cmd = ['goto-instrument', '--show-goto-functions', goto]
    return run(cmd).splitlines()

def lines_of_goto_functions(results, builddir=None, workingdir=None):
    """Get lines of code given in the listing of a goto binary."""

    loc = []
    regexp = r'// \d+ file (.*) line (\d+) function (.*)'
    for entry in results:
        match = re.search(regexp, entry)
        if not match:
            continue
        name = match.group(1)
        line = match.group(2)
        func = match.group(3)
        if internal_file(name):
            continue
        loc.append((expand_pathname(name, builddir, workingdir),
                    int(line),
                    func))
    loc = sorted(list(set(loc)))

    lines = {}
    for name, line, func in loc:
        lines[func] = lines.get(func) or []
        lines[func].append((name, line))

    return lines

################################################################
# Get the list of reachable functions in a goto binary.

def reachable_functions(goto, builddir=None):
    """Get reachable functions in a goto binary."""

    cmd = ['goto-analyzer', '--reachable-functions', '--json', '-', goto]
    results = run(cmd)
    # Skip 6 lines of output before the json
    results = '\n'.join(results.splitlines()[6:])

    functions = []
    for entry in json.loads(results):
        name = entry['file name']
        func = entry['function']
        if internal_file(os.path.basename(name)):
            continue
        size = int(entry['last line']) - int(entry['first line'])
        functions.append((func, expand_pathname(name, builddir), size))
    return sorted(functions)

################################################################
# Get the number of lines of each reachable function in a goto binary.

def count_lines(linesofcode, reachablefunctions, cbmcdir=None):
    """Count the lines of code in the reachable functions."""

    if cbmcdir:
        cbmcdir = os.path.normpath(cbmcdir).strip(os.sep)

    total_loc = 0
    total_size = 0
    for func, path, size in reachablefunctions:
        if cbmcdir and not cbmcdir in path:
            continue
        number = len(linesofcode[func])
        total_loc += number
        total_size += size
        logging.info('Line count: %s', (func, number))
    logging.info('Total line count: %s', total_loc)
    return total_loc, total_size

################################################################
# Build the goto binary and return its name.

def clean_goto(directory):
    cmd = ['make', 'clean']
    run(cmd, directory)

def make_goto(directory):
    cmd = ['make', 'goto']
    run(cmd, directory)

def most_recent_goto(directory):
    logging.debug('Most recent goto binary directory: %s', directory)
    cwd = os.getcwd()
    try:
        os.chdir(directory)
        gotos = [path for path in os.listdir('.')
                 if os.path.isfile(path) and path.endswith('.goto')]
        logging.debug('Most recent goto binary gotos: %s', gotos)
        most_recent = max(gotos, key=os.path.getmtime)
        logging.debug('Most recent goto binary: %s', most_recent)
    finally:
        os.chdir(cwd)
    return most_recent

def goto_harness(directory):
    logging.info('Making goto harness: directory: %s', directory)
    clean_goto(directory)
    make_goto(directory)
    harness = most_recent_goto(directory)
    logging.info('Making goto harness: result: %s', harness)
    return harness

################################################################

def proof_name(goto):
    name = os.path.basename(goto)
    suffix = '_harness.goto'
    if name.endswith(suffix):
        name = name[len(suffix):]
    return name

################################################################

def cbmc_lines_of_code(blddir, cbmcdir=None):
    goto = goto_harness(blddir)
    goto_path = os.path.join(blddir, goto)

    pgm = show_goto_functions(goto_path)
    loc = lines_of_goto_functions(pgm, builddir=blddir)
    reachable = reachable_functions(goto_path, builddir=blddir)
    total_loc, total_size = count_lines(loc, reachable)
    harness_total_loc, harness_total_size = count_lines(loc, reachable, cbmcdir=cbmcdir)

    logging.debug('Lines of code:')
    logging.debug(loc)
    logging.debug('Reachable functions:')
    logging.debug(reachable)

    report = {
        'property': proof_name(goto_path)[:-len('.goto')],
        'lines': total_loc,
        'harness-lines': harness_total_loc,
        'size': total_size,
        'harness-size': harness_total_size
        }

    return report

def sloc_lines_of_code(blddir, srcdir, proofdir=None):
    loc = make_sources.sources_found_using_make(blddir, srcdir, proofdir)
    report = {
        'sloc-lines': loc['lines-of-code']['source'],
        'sloc-harness-lines': loc['proof-lines-of-code']['source']
        }
    return report


################################################################

def main():
    args = create_parser().parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    loc = cbmc_lines_of_code(args.blddir, 'cbmc/proof')
    sloc = sloc_lines_of_code(args.blddir, args.srcdir, 'cbmc/proof')
    loc['sloc-lines'] = sloc['sloc-lines']
    loc['sloc-harness-lines'] = sloc['sloc-harness-lines']
    print(json.dumps(loc))

if __name__ == '__main__':
    main()

################################################################
