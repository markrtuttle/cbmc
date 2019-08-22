"""Gather names of source files used to buid a goto binary."""

import logging
import os
import subprocess
import re
import json

def run_command(command, directory=None):
    """Run a command in a directory."""

    if isinstance(command, str):
        command = command.split()
    result = subprocess.run(command, capture_output=True, text=True,
                            cwd=directory)
    return result

def build_with_preprocessor(directory=None):
    """Build the goto binary using goto-cc as a preprocessor."""

    run_command(['make', 'clean'], directory)
    result = run_command(['make', 'GOTO_CC=goto-cc -E', 'goto'], directory)
    # Make will fail when it tries to link the preprocessed output
    # What is a system-independent way of skipping an okay link failure?
    if result.returncode and result.returncode != 2:
        print(result.stdout)
        print(result.stderr)
        result.check_returncode()
    return [line for line in result.stdout.splitlines()
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
             if name not in ['<built-in>', '<command']]
    if directory:
        files = [os.path.abspath(os.path.join(directory, name))
                 for name in files]
    return sorted(list(set(files)))

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
    result = run_command(command, root)
    if result.returncode:
        print(result.stdout)
        print(result.stderr)
        result.check_returncode()
    # sloc produces a great deal of useful data in addition to the summary
    return json.loads(result.stdout)["summary"]


def source_files(build='.', root='.'):
    """Gather names of source files used to buid a goto binary."""

    build = os.path.abspath(build)
    root = os.path.abspath(root)
    bld_commands = build_with_preprocessor(build)
    bld_files = build_files(bld_commands, build)
    bld_output = build_output(bld_files)
    all_files = build_source_files(bld_output, build)
    root_files, files = root_source_files(all_files, root)
    return {'root': root,
            'files': files,
            'lines-of-code': sloc(files, root),
            'root-files': root_files,
            'all-files': all_files}

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
            'root-files': root_files,
            'all-files': all_files}
