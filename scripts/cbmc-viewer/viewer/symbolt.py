#pylint: disable=missing-docstring

import os
import json
import logging
import subprocess

import locationt

class Symbol:
    def __init__(self, symbols=None, root=None, files=None):
        if symbols:
            with open(symbols) as symbols_file:
                self.symbols = json.load(symbols_file)
            return

        if have_ctags():
            symbols = ctags_symbols(run_ctags(root, files))
        elif have_etags():
            symbols = etags_symbols(run_etags(root, files))
        else:
            print("Can't find ctags or etags, skipping symbols.")
            logging.info("Can't find ctags or etags, skipping symbols.")
            symbols = []

        self.symbols = {}
        for symbol, filename, linenumber in symbols:
            if symbol in self.symbols:
                logging.info("Found duplication definition: %s, %s, %s",
                             symbol, filename, linenumber)
                continue
            self.symbols[symbol] = locationt.parse_srcloc(
                locationt.make_srcloc(filename, None, linenumber, root),
                root=root,
                asdict=True
            )

    def lookup(self, symbol):
        return self.symbols.get(symbol)

    def dump(self):
        return json.dumps(self.symbols, indent=2)

################################################################

def run(cmd, verbose=False, cwd=None):
    if isinstance(cmd, str):
        cmd = cmd.split()
    if verbose:
        print('Running: {}'.format(' '.join(cmd)))

    result = subprocess.run(cmd,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            universal_newlines=True, cwd=cwd)
    if result.returncode:
        debug = {'command': result.args,
                 'returncode': result.returncode,
                 'stdout': result.stdout.split('\n'),
                 'stderr': result.stderr.split('\n')}
        logging.info(json.dumps(debug, indent=2))
    result.check_returncode()

    return result.stdout

################################################################
# Parse a ctags file
#

EXUBERANT = 'exuberant'
CTAGS = 'ctags'

def have_ctags():
    try:
        help_banner = run([CTAGS, '--help']).splitlines()[0].lower().split()
        return all(string in help_banner for string in [EXUBERANT, CTAGS])
    except FileNotFoundError:
        return False

def run_ctags(root, files):
    if not files:
        return ''

    output = ''
    while files:
        paths = files[:100]
        files = files[100:]
        output += run([CTAGS, '-x'] + paths, cwd=root)
    return output

def ctags_symbols(ctags_data):
    """Return the symbol definitions appears in a ctags file.

    Each line names a symbol, a symbol kind, a line number, and a file
    name.  The values are space-separated.
    """

    definitions = []
    for line in [line.strip() for line in ctags_data.splitlines()]:
        if not line:
            continue

        # assume filenames do not contain whitespace
        symbol, _, linenumber, filename = line.split()[:4]
        if filename.startswith('./'):
            filename = filename[2:]
        definitions.append([symbol, filename, linenumber])

    return sorted(definitions)

################################################################
# Parse an etags file
#
# The etags format is described at https://en.wikipedia.org/wiki/Ctags#Etags_2

ETAGS = 'etags'
TAGS = 'TAGS' + '-' + str(os.getpid())

def have_etags():
    try:
        help_banner = run([ETAGS, '--help']).splitlines()[0].lower().split()
        return ETAGS in help_banner
    except FileNotFoundError:
        return False

def run_etags(root, files):
    if not files:
        return ''

    try:
        os.remove(TAGS)
    except FileNotFoundError:
        pass # file did not exist

    while files:
        paths = files[:100]
        files = files[100:]
        run([ETAGS, '-o', TAGS, '--append'] + paths, cwd=root)

    with open(os.path.join(root, TAGS)) as etags_file:
        etags_data = etags_file.read()
    os.remove(os.path.join(root, TAGS))
    return etags_data

def etags_symbols(etags_data):
    """Return the symbol definitions appearing in an etags file.

    Scan etags_data, the contents of an etags file, and return the
    list of symbol definitions in the file as a list of tuples of the
    form [symbol, filename, linenumber].
    """

    # Each section begins with a line containing just "\f"
    sections = etags_data.split("\f\n")[1:]
    return sorted([definition
                   for section in sections
                   for definition in etags_section_definitions(section)])

def etags_section_definitions(section):
    """Return the symbol definitions in a section of an etags file.

    A section consists of a sequence of lines: a header containing a
    file name, and a sequence of definitions containing symbols and
    line numbers.
    """

    lines = section.splitlines()
    filename = etags_section_filename(lines[0])
    return [[symbol, filename, num]
            for symbol, num in [etags_symbol_definition(line)
                                for line in lines[1:]]]

def etags_section_filename(header):
    """Return the file name in the section header.

    A section header is a filename and a section length separated by a
    comma.
    """
    return header.split(',')[0]

def etags_symbol_definition(definition):
    """Return the symbol and line number in a symbol definition.

    A symbol definition is the symbol definition, '\x7f', the symbol
    name, '\x01, the line number, ',', and the offset within the file.
    The symbol name is omitted if it can be easily located in the
    symbol definition.
    """
    tag_def, tag_name_line_offset = definition.split('\x7f')
    tag_name_line, _ = tag_name_line_offset.split(',')
    tag_name, tag_line = ([None] + tag_name_line.split('\x01'))[-2:]

    if tag_name is None:
        tag_name = tag_def.split()[-1].lstrip('(')

    return tag_name, int(tag_line)

################################################################

def main():
    import sourcet
    sources = sourcet.Source(
        build='/Users/mrtuttle/freertos/tools/cbmc/proofs/HTTP/IotHttpsClient_AddHeader',
        root='/Users/mrtuttle/freertos/tools/cbmc/proofs')

    symbols = Symbol(root=sources.root, files=sources.files)
    print(symbols.dump())
