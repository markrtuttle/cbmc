r"""Manipulate paths and source locations.

This module encapsulates all reasoning about paths and source locations.
Paths are confusing in cbmc.  Paths may be Linux or Windows paths.  Paths may
be paths used to access the filesystem or used as links in html.
Paths may be relative or absolute.  Relative paths may be relative to
the source root or may be relative to the working directory in which
the goto binary was built.  The source root may be the root on the
machine that built the goto binary or the root on the local machine
producing the report.

A viewer location is a file, a line number, and a function name.  The
file is in a canonical form using the Linux path separator.  The file
is path relative to the source root on the local machine if possible,
and an absolute path if not.

The canonical form of a windows path "c:\users\foo" is "c:/users/foo".
On Windows, the os.path functions accept both / and \ as path
separators, but os.path.normpath and os.path.abspath return paths
using \.  Canonical paths can be used both to access the file system
and also links in html.

The most important source of path information is the source location
embedded in the output of cbmc.  A source location consists of a file,
function, line number, and working directory.  The file may be
absolute or relative to the working directory.  The working directory
is generally the current working directory of the build process that
built the goto binary.  The json and xml output of cbmc includes the
working directory in source locations, but the textual output usually
omits it.  The working directory must be given explicitly when working
with textual output.
"""

import os
import re
import logging

################################################################
# Canonical path manipulation

def canonical(path):
    """Return path in canonical form."""

    if path is None:
        return None
    return os.path.normpath(path).replace(os.sep, '/')

def canonical_abspath(path):
    """Return absolute path in canonical form."""

    if path is None:
        return None
    return canonical(os.path.abspath(path))

def canonical_join(*paths):
    """Join paths in canonical form."""

    if not paths:
        return None
    return canonical(os.path.join(*paths))

def canonical_abspath_join(*paths):
    """Join paths and return absolute path in canonical form."""

    paths = [path for path in paths if path is not None]
    if not paths:
        return None

    return canonical(os.path.abspath(os.path.join(*paths)))

def canonical_relpath(path, start):
    """Return relative path from start directory in canonical form."""

    path = canonical(path)
    start = canonical(start)

    if path is None:
        return None
    if start is None:
        return path
    return canonical(os.path.relpath(path, start))

def canonical_childpath(child, ancestor):
    """Return relative path from ancestor directory in canonical form."""

    child = canonical(child)
    ancestor = canonical(ancestor)

    if child is None:
        return None
    if ancestor is None:
        return child

    path = canonical_relpath(child, ancestor)
    if path.startswith('..'):  # child not a descendant of ancestor
        return child
    return path

################################################################
# Source locations

def make_srcloc(filename, function, line, wkdir):
    """Create a srcloc understood by this module."""

    return {'file': filename,
            'function': function,
            'line': int(line),
            'working-directory': wkdir}

################################################################
# CBMC path to built in function FOO ends in <built-in-FOO>

def builtin_name(path):
    """Extract file name from path to a built in function."""

    if path is None:
        return None

    name = os.path.basename(path)
    if name.startswith('<') and name.endswith('>'):
        return name

    return None

################################################################
# A location is a file and line number, and optionally a function name.
#

class Location:
    """Manipulation cbmc source locations and viewer locations.

    A cbmc source location is a file, a line number, a function name,
    and a working directory (some components may be missing).  The
    file may be an absolute path or it may be relative to the working
    directory.  The file is usually a path in the style of the
    operating system on which the goto-binary was built (usually
    Windows or Linux).  The working directory is usually the current
    working directory of the process that built the goto binary.

    A viewer location is a file, a line number, and a function name
    (some components may be missing).  The file is a canonical path
    relative to the root of the source tree.

    Components may be missing.  For example, there is no function
    named in a cbmc source location for a built-in function: the file
    name includes the function name.
    """

    def __init__(self, srcdir, blddir=None, wkdir=None):
        """Initialize with source, build, and working directories."""

        self.srcdir = canonical_abspath(srcdir)
        self.blddir = canonical_abspath(blddir) or self.srcdir
        self.wkdir = canonical_abspath(wkdir)

    def blddir_path_from_wkdir_path(self, path, wkdir=None):
        """A path relative to blddir from a path relative to wkdir.

        Take a path that is absolute or relative to wkdir and
        transform it into a path that is absolute or relative to bldir
        (and hence relative to srcdir) if the path falls under blddir.
        Use the location's wkdir as the default unless a different
        wkdir is specified as an argument.
        """

        if path is None:
            return None

        wkdir_path = canonical_abspath_join(wkdir, self.wkdir, path)
        return canonical_childpath(wkdir_path, self.blddir)

    def parse_srcloc(self, sloc, asdict=False):
        """Extract a viewer location from a cbmc source location."""

        logging.debug("srcloc: sloc=%s asdict=%s", sloc, asdict)

        if sloc is None:
            return None

        filename = sloc.get('file')
        function = sloc.get('function')
        line = sloc.get('line')
        directory = sloc.get('working-directory')

        line = int(line) if line is not None else None
        path = (builtin_name(filename) or
                self.blddir_path_from_wkdir_path(filename, wkdir=directory))

        if asdict:
            return {'file': path, 'function': function, 'line': line}
        return path, function, line

    def parse_text_srcloc(self, sloc, asdict=False):
        """Extract a viewer location from a cbmc text source location."""

        match = re.search('file (.+) function (.+) line ([0-9]+)', sloc)
        if match:
            path, func, line = match.groups()[:3]
            return self.parse_srcloc(make_srcloc(path, func, line, self.wkdir),
                                     asdict)

        match = re.search('file (.+) line ([0-9]+) function (.+)', sloc)
        if match:
            path, line, func = match.groups()[:3]
            return self.parse_srcloc(make_srcloc(path, func, line, self.wkdir),
                                     asdict)

        # Some models of intrinsic functions omit file and line
        match = re.search('function (.+)', sloc)
        if match:
            path, func, line = '<intrinsic>', match.groups(0), 0
            return self.parse_srcloc(make_srcloc(path, func, line, self.wkdir),
                                     asdict)

            logging.debug("No source location found in %s", sloc)
            return None

    def parse_json_srcloc(self, sloc, asdict=False):
        """Extract a viewer location from a cbmc json source location."""

        return self.parse_srcloc(
            make_srcloc(
                sloc.get('file'),
                sloc.get('function'),
                sloc.get('line'),
                sloc.get('workingDirectory')
            ),
            asdict
        )

    def parse_xml_srcloc(self, sloc, asdict=False):
        """Extract a viewer location from a cbmc xml source location."""

        return self.parse_srcloc(
            make_srcloc(
                sloc.get('file'),
                sloc.get('function'),
                sloc.get('line'),
                sloc.get('working-directory')
            ),
            asdict
        )

################################################################
