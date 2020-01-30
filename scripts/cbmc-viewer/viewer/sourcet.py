"""Gather names of source files used to buid a goto binary."""

import logging
import os
import re
import json
import platform

import locationt
import runt

################################################################

class Source:
    def __init__(self, build=None, root=None, sources=None,
                 walk=None, find=None, extensions=None, exclude=None):

        logging.debug('Source init: '
                      'build: %s, root: %s, sources: %s, walk: %s, '
                      'find: %s, extensions: %s, exclude: %s',
                      build, root, sources, walk,
                      find, extensions, exclude)

        self.root = None
        self.files = []
        self.lines_of_code = None
        self.root_files = []
        self.all_files = []

        build = os.path.abspath(build) if build else None
        root = os.path.abspath(root) if root else None
        if walk and find or not walk and not find:
            walk = platform.system() == 'Windows'
            find = not walk

        if sources:
            with open(sources) as datafile:
                data = json.load(datafile)
                self.root = data['root']
                self.all_files = data['all-files']
        elif root and build:
            self.root, self.all_files = find_sources_with_make(build, root)
        elif root and find:
            self.root = root
            self.all_files = find_sources_with_find(root)
        elif root and walk:
            self.root = root
            self.all_files = find_sources_with_walk(root)
        else:
            print("No source files found")
            logging.info("No source files found")
            return

        if exclude:
            raise UserWarning("Use of exclude currently unimplemented.")
        if extensions:
            raise UserWarning("Use of extensions currently unimplemented.")

        self.root = locationt.canonical_abspath(self.root)
        self.all_files = sorted([locationt.canonical_abspath(path, self.root)
                                 for path in self.all_files])

        self.root_files, self.files = root_source_files(
            self.all_files, self.root
        )
        self.lines_of_code = sloc(self.files, self.root)

    def dump(self):
        return json.dumps(
            {
                'root': self.root,
                'files': self.files,
                'lines-of-code': self.lines_of_code,
                'files-under-root': self.root_files,
                'all-files': self.all_files
            },
            indent=2)

################################################################

def find_sources(build=None, root=None):
    build = os.path.abspath(build) if build else None
    root = os.path.abspath(root) if root else None

    if build and root:
        _, files = find_sources_with_make(build=build, root=root)
    elif root:
        if platform.system() == 'Windows':
            # Walk is slow but windows has no find command
            files = find_sources_with_walk(root)
        else:
            files = find_sources_with_find(root)
    else:
        logging.info("Unable to find source files.")
        root = None
        files = []

    return root, files

def find_sources_with_make(build='.', root='.'):
    """Gather names of source files used to buid a goto binary."""

    # Remove build artifacts before building with preprocessor
    runt.run(['make', 'clean'], build)

    bld_commands = build_with_preprocessor(build)
    bld_files = build_files(bld_commands, build)
    bld_output = build_output(bld_files)
    all_files = build_source_files(bld_output, build)

    # Remove build artifacts after building with preprocessor
    runt.run(['make', 'clean'], build)


    return root, all_files

def find_sources_with_find(root='.'):
    """Use find to list source files in subtree rooted at root."""
    cmd = ["find", "-L", ".",
           "(", "-iname", "*.[ch]", "-or", "-iname", "*.inl", ")"]
    find = runt.run(cmd, root)
    return find.strip().splitlines()

def find_sources_with_walk(root='.'):
    """Use walk to list source files in subtree rooted at root."""
    files = []
    for path, _, filenames in os.walk(root, followlinks=True):
        names = [os.path.join(path, name) for name in filenames
                 if name.lower().endswith((".h", ".c", ".inl"))]
        files.extend(names)
    dirlen = len(root) + 1
    files = [name[dirlen:].replace(os.sep, '/') for name in files]
    return files

################################################################
# Use make to find the source files
#

def build_with_preprocessor(directory=None):
    """Build the goto binary using goto-cc as a preprocessor."""

    # Make will fail when it tries to link the preprocessed output
    # What is a system-independent way of skipping an okay link failure?
    result = runt.run(['make', 'GOTO_CC=goto-cc -E', 'goto'], directory,
                      ignored=[2])

    return [line
            for line in result.splitlines()
            if line.strip().startswith('goto-cc')]

def build_files(commands, directory=None):
    """Accumulate the names of the files containing the preprocessed output."""

    files = []
    for cmd in commands:
        match = re.search(r' -o (\S+) ', cmd)
        if match:
            name = match.group(1)
            if directory:
                name = os.path.join(directory, name)
            files.append(os.path.abspath(name))
    return files

def build_output(files):
    """Accumulate the preprocessed output."""

    output = []
    for name in files:
        try:
            with open(name) as handle:
                output.extend(handle.read().splitlines())
        except FileNotFoundError:
            # The output file for the failed linking step will be in list
            logging.debug("Can't open '%s', "
                          "probably due to the failure of the link step", name)
    return output

def build_source_files(output, directory=None):
    """Extract the source file names listed in the preprocessed output."""

    files = [line.strip().split()[2] for line in output
             if line.strip().startswith('#')]
    files = [name.strip('"') for name in files]
    files = [name for name in files
             if name not in ['<built-in>', '<command-line>']]
    if directory:
        files = [os.path.abspath(os.path.join(directory, name))
                 for name in files]
    return sorted(list(set(files)))

################################################################

def root_source_files(files, root=None):
    """Extract the source files under the root."""

    full_paths, relative_paths = list(files), list(files)
    if root:
        root = os.path.abspath(root)
        full_paths = [name for name in files if name.startswith(root)]
        relative_paths = [name[len(root):].lstrip(os.path.sep)
                          for name in full_paths]
    return sorted(list(set(full_paths))), sorted(list(set(relative_paths)))

def sloc(files, root=None):
    """Run sloc on files under the root directory."""

    command = ['sloc', '-f', 'json'] + files
    try:
        result = runt.run(command, root)
    except FileNotFoundError as error:
        logging.info("Unable to run sloc: %s", error.strerror)
        return None
    except OSError as error:
        if error.errno != 7: # Argument list too long
            raise
        print("Unable to run sloc: {}".format(error.strerror))
        logging.info("Unable to run sloc: %s", error.strerror)
        return None
    # sloc produces a great deal of useful data in addition to the summary
    return json.loads(result)["summary"]

################################################################

def merge(data_files):
    """Merge a collection of files produced by this program."""

    root = None
    all_files = []
    for data_file in data_files:
        with open(data_file) as data_json:
            data = json.load(data_json)
            data_root = os.path.abspath(data['root'])
            data_all_files = data['all-files']
            if root is None:
                root = data_root
            elif root != data_root:
                raise UserWarning('Found differing roots {} and {}'.
                                  format(root, data_root))
            all_files.extend(data_all_files)
    all_files = sorted(list(set(all_files)))
    root_files, files = root_source_files(all_files, root)
    return {'root': root,
            'files': files,
            'lines-of-code': sloc(files, root),
            'files-under-root': root_files,
            'all-files': all_files}

################################################################
