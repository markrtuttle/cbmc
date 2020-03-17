r"""Manipulate paths and source locations in canonical form.

Define a canonical form for paths that uses the Linux path separator.

The canonical form of a windows path "c:\users\foo" is "c:/users/foo".
On Windows, the os.path functions accept both / and \ as path separators,
but os.path.normpath and os.path.abspath return paths using \.
"""

import os
import re
import logging

################################################################

def builtin_name(path):
    if path is None:
        return None

    name = os.path.basename(path)
    if name.startswith('<') and name.endswith('>'):
        return name

    return None

def canonical_path(path):
    """Return path in canonical form."""
    logging.debug("canonical_path: path=%s", path)

    if path is None:
        return None
    return os.path.normpath(path).replace(os.sep, '/')

def native_path(path):
    """Return path in normal form for the native operating system."""
    logging.debug("native_path: path=%s", path)

    if path is None:
        return None
    return os.path.normpath(path)

def canonical_abspath(path, wkdir=None):
    """Return path as absolute path in canonical form.

    If the working directory wkdir is given, path may be relative to wkdir
    (which may in turn be relative to the current working directory).
    """

    if path is None:
        return None
    return canonical_path(
        os.path.abspath(os.path.join(wkdir, path) if wkdir else path)
    )

def canonical_relpath(path, wkdir=None, root=None):
    """Return path as relative path in canonical form relative to root.

    Return path if path is not under root.
    """

    path = canonical_abspath(path, wkdir)
    root = canonical_abspath(root)

    if path and root and path.startswith(root+'/'):
        return canonical_path(path[len(root)+1:] or '.')
    return canonical_path(path)

################################################################

def make_srcloc(filename, function, line, wkdir):
    """Create a srcloc understood by this module."""

    return {'file': filename,
            'function': function,
            'line': int(line),
            'working-directory': wkdir}

def parse_srcloc(sloc, root=None, asdict=False):
    """Extract filename, function, and line from a source location.

    Filename will be in canonical form.  It will be an absolute path,
    or a path relative to root if path is under root.

    Function may be None if there is no function named in the source
    location.  For example, there is no function named in a source
    location for a built-in function: the file name is the function
    name.
    """
    logging.debug("srcloc: sloc=%s root=%s asdict=%s", sloc, root, asdict)

    if sloc is None:
        return None

    filename = sloc.get('file')
    function = sloc.get('function')
    line = sloc.get('line')
    directory = sloc.get('working-directory')

    line = int(line) if line is not None else None
    path = (builtin_name(filename) or
            canonical_relpath(filename, wkdir=directory, root=root))

    if asdict:
        return {'file': path, 'function': function, 'line': line}
    return path, function, line

def parse_text_srcloc(sloc, root=None, asdict=False, wkdir=None):
    match = re.search('file (.+) function (.+) line ([0-9]+)', sloc)
    if match:
        path, func, line = match.groups()[:3]
        return parse_srcloc(make_srcloc(path, func, line, wkdir), root, asdict)

    match = re.search('file (.+) line ([0-9]+) function (.+)', sloc)
    if match:
        path, line, func = match.groups()[:3]
        return parse_srcloc(make_srcloc(path, func, line, wkdir), root, asdict)

    # Some models of intrinsic functions omit file and line
    match = re.search('function (.+)', sloc)
    if match:
        path, func, line = '<intrinsic>', match.groups(0), 0
        return parse_srcloc(make_srcloc(path, func, line, wkdir), root, asdict)

    logging.debug("No source location found in %s", sloc)
    return None

def parse_json_srcloc(sloc, root=None, asdict=False):
    # json output omits source locations in traces
    if sloc is None:
        logging.info("Found null srcloc in json output from cbmc")
        sloc = {'file': os.path.join(root, 'MISSING'),
                'function': 'MISSING',
                'line': 0,
                'workingDirectory': root}

    return parse_srcloc(
        make_srcloc(
            sloc.get('file'),
            sloc.get('function'),
            sloc.get('line'),
            sloc.get('workingDirectory')
        ),
        root,
        asdict
    )

def parse_xml_srcloc(sloc, root=None, asdict=False):
    # json output omits source locations in traces, maybe xml does, too
    if None in (sloc,
                sloc.get('file'),
                sloc.get('function'),
                sloc.get('line'),
                sloc.get('working-directory')):
        logging.info("Found null srcloc in xml output from cbmc")
        sloc = {'file': os.path.join(root, 'MISSING'),
                'function': 'MISSING',
                'line': 0,
                'workingDirectory': root}

    return parse_srcloc(
        make_srcloc(
            sloc.get('file'),
            sloc.get('function'),
            sloc.get('line'),
            sloc.get('working-directory')
        ),
        root,
        asdict
    )

################################################################
