#pylint: disable=missing-docstring

import json
import logging
import subprocess

import metadata
import sourcest

# Invoke ctags on a bounded number of files at a time
CTAG_FILES = 1000

################################################################

def run_cmd(cmd, cwd=None):
    if isinstance(cmd, str):
        cmd = cmd.split()

    logging.debug('command run: %s', cmd)
    # Source file written on Windows in Europe can't be read as utf-8
    result = subprocess.run(cmd, cwd=cwd, encoding='latin-1',
                            capture_output=True, text=True)
    if result.returncode:
        debug = {'command': result.args,
                 'returncode': result.returncode,
                 'stdout': result.stdout.splitlines(),
                 'stderr': result.stderr.splitlines()}
        logging.debug(json.dumps(debug, indent=2))
    result.check_returncode()

    logging.debug('command results: %s', result.stdout)
    return result.stdout.splitlines()

################################################################

def run_ctags(root, files, ctags='ctags'):
    results = []
    while files:
        names, files = files[:CTAG_FILES], files[CTAG_FILES:]
        results.extend(run_cmd([ctags, '-x'] + names, cwd=root))
    return results

################################################################

def parse_ctags_line(line):
    """Parse a line 'symbol kind line file ...' of ctags -x output."""

    logging.debug('Parsing ctags output: %s', line)

    try:
        symbol, _, linenumber, filename = line.split()[:4]
        return (symbol, filename, int(linenumber))
    except:
        # Ignore operator definitions 'operator != function line file ...'
        if line.startswith('operator'):
            return None
        logging.debug("Can't parse ctags output: %s", line)
        raise

################################################################

def parse_ctags_output(results):
    symbols = {}
    for line in results:
        result = parse_ctags_line(line)
        if result is None:
            continue
        symbol, filename, linenumber = result

        if filename.startswith('./'):
            filename = filename[2:]
        if symbols.get(symbol):
            # ctags itself emits duplication warnings on stderr
            logging.info('Duplicate symbol definition: '
                         '%s at %s %s and %s %s',
                         symbol,
                         symbols[symbol]['file'], symbols[symbol]['line'],
                         filename, linenumber)
            continue

        symbols[symbol] = {'file':filename, 'line':linenumber}
    return symbols

################################################################

def get_symbols(srcdir, srcexclude, srcfiles):
    symbols = Symbols(srcdir, srcexclude, srcfiles)
    return {'metadata': symbols.metadata,
            'symbols': symbols.symbols}

def print_symbols(srcdir, srcexclude, srcfiles):
    symbols = get_symbols(srcdir, srcexclude, srcfiles)
    print(json.dumps(symbols, indent=2))

def write_symbols(srcdir, srcexclude, srcfiles, filename='symbols.json'):
    symbols = get_symbols(srcdir, srcexclude, srcfiles)
    with open(filename, 'w') as output:
        json.dump(symbols, output, indent=2)

################################################################

class Symbols:
    # pylint: disable=too-few-public-methods

    def __init__(self, srcdir=None, srcexclude=None, srcfiles=None,
                 symfile=None):
        self.metadata = None
        self.symbols = {}

        if symfile:
            with open(symfile) as handle:
                data = json.load(handle)
                self.symbols = data['symbols']
                self.metadata = data['metadata']
                return

        if not srcdir and not srcfiles:
            raise UserWarning(
                "Symbols class requires a source root or sources object.")

        if srcfiles:
            sources = sourcest.Sources(srcdir, srcfiles=srcfiles)
        else:
            sources = sourcest.Sources(srcdir, srcexclude=srcexclude)

        ctags = run_ctags(sources.root(), sources.files())
        self.symbols = parse_ctags_output(ctags)
        self.metadata = metadata.metadata('cbmc-symbol-data', root=sources.root())

    def lookup(self, symbol):
        try:
            loc = self.symbols[symbol]
            return (loc['file'], loc['line'])
        except KeyError:
            return None
