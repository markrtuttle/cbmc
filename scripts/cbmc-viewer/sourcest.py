"""Source files used to build a goto binary."""

import os
import json
import platform

import make_sources

def get_sources_from_json(srcfiles):
    """Generate the list of source files by reading json file generated by source-files."""

    with open(srcfiles) as handle:
        data = json.load(handle)
    return os.path.abspath(data['root']), sorted(data['files'])

class Sources:
    """Source files used to build a goto binary."""

    def __init__(self, srcdir, srcfiles=None, srcexclude=None):
        self.srcroot = None
        self.srcfiles = []

        if srcfiles:
            self.srcroot, self.srcfiles = get_sources_from_json(srcfiles)
        else:
            self.srcroot = os.path.abspath(srcdir)
            if platform.system() == 'Windows':
                # Windows does not have the faster find command
                self.srcfiles = make_sources.sources_found_using_walk(self.srcroot,
                                                                      srcexclude)['files']
            else:
                self.srcfiles = make_sources.sources_found_using_find(self.srcroot,
                                                                      srcexclude)['files']
            # Consider writing results to sources.json for logging, etc.

    def files(self):
        """List of source files."""
        return self.srcfiles

    def root(self):
        """Root of source directory."""
        return self.srcroot
